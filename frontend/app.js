// State & App Data
let eventsData = [];
let modelsData = [];
let agentsData = [];
let currentOrgName = "Hackathon Demo Org";
let currentUserName = "Demo Visitor";
let currentUserSession = null;

// Initialize Supabase Auth Client
let supabaseClient = null;
if (typeof supabase !== 'undefined' && APP_CONFIG.SUPABASE_URL && APP_CONFIG.SUPABASE_ANON_KEY) {
    supabaseClient = supabase.createClient(APP_CONFIG.SUPABASE_URL, APP_CONFIG.SUPABASE_ANON_KEY);
}

// Global API Fetch Wrapper with Authorization Header
async function fetchWithAuth(url, options = {}) {
    options.headers = options.headers || {};
    
    // Attach Session Token if available
    const savedToken = localStorage.getItem('governance_auth_token');
    if (savedToken) {
        options.headers['Authorization'] = `Bearer ${savedToken}`;
    } else if (supabaseClient) {
        const { data: { session } } = await supabaseClient.auth.getSession();
        if (session && session.access_token) {
            options.headers['Authorization'] = `Bearer ${session.access_token}`;
        }
    }

    const response = await fetch(url, options);
    return response;
}

// Module Explanations
const helpTexts = {
    recorder: {
        title: "Governance Event Recorder Overview",
        content: `
            <p><strong>Purpose:</strong> Captures every model substitution as an immutable governance record.</p>
            <div class="explanation-box margin-top">
                <h4>Recorded Event Attributes:</h4>
                <ul style="margin-left: 1.25rem; margin-top: 0.5rem; line-height: 1.6;">
                    <li><strong>Requested Model:</strong> Target model selected by caller application</li>
                    <li><strong>Actual Model Used:</strong> Final model routed by LLM Gateway</li>
                    <li><strong>Substitution Reason:</strong> Cost optimization, Provider unavailability, or Fallback policy</li>
                    <li><strong>Risk Assessment:</strong> Capability drop calculation based on context window delta</li>
                    <li><strong>Compliance Flag:</strong> Whitelist violation detection against agent policy</li>
                </ul>
            </div>
        `
    },
    risk: {
        title: "Substitution Risk Assessor Overview",
        content: `
            <p><strong>Purpose:</strong> Calculates material capability downgrades when model routing decisions switch models.</p>
            <div class="explanation-box margin-top">
                <h4>Context Window Reduction Thresholds:</h4>
                <ul style="margin-left: 1.25rem; margin-top: 0.5rem; line-height: 1.6;">
                    <li><strong class="badge risk-low">Low Risk:</strong> &le; 25% Context Capacity Reduction</li>
                    <li><strong class="badge risk-medium">Medium Risk:</strong> 25.1% - 50% Context Capacity Reduction</li>
                    <li><strong class="badge risk-high">High Risk:</strong> 50.1% - 75% Context Capacity Reduction</li>
                    <li><strong class="badge risk-critical">Critical Risk:</strong> &gt; 75% Context Capacity Reduction</li>
                </ul>
            </div>
        `
    },
    compliance: {
        title: "Compliance Flag Engine Overview",
        content: `
            <p><strong>Purpose:</strong> Enforces model whitelists mapped to specific AI Agents.</p>
            <div class="explanation-box margin-top">
                <h4>Policy Enforcement Logic:</h4>
                <p class="margin-top">Every incoming substitution event is matched against the agent's pre-approved model list. If the routed model is not whitelisted, the event is automatically flagged with a compliance violation.</p>
            </div>
        `
    },
    audit: {
        title: "Retroactive Compliance Audit Overview",
        content: `
            <p><strong>Purpose:</strong> Scans historical substitution logs to produce compliance & capability exposure audits.</p>
            <div class="explanation-box margin-top">
                <h4>Audit Metrics Computed:</h4>
                <ul style="margin-left: 1.25rem; margin-top: 0.5rem; line-height: 1.6;">
                    <li>Total Substitution Events Analyzed</li>
                    <li>Unapproved Model Routing Count & Flag Rate %</li>
                    <li>High / Critical Risk Exposure Ratio %</li>
                </ul>
            </div>
        `
    },
    models: {
        title: "Model Capability Profiles Overview",
        content: `
            <p><strong>Purpose:</strong> Global reference directory holding context window specifications across top AI model providers.</p>
        `
    }
};

// DOM Initialization
document.addEventListener('DOMContentLoaded', () => {
    initAuthLanding();
    initTabNavigation();
    initFilterListeners();
    initModalListeners();
    initApiKeyListeners();
    initSimulator();
    initAuditButton();
    
    // Initial Auth Session Check
    checkAuthSession();
});

function initApiKeyListeners() {
    const copyBtn = document.getElementById('btn-copy-api-key');
    const regenBtn = document.getElementById('btn-regen-api-key');

    copyBtn?.addEventListener('click', async () => {
        const cachedKey = localStorage.getItem('governance_active_api_key');
        const textToCopy = cachedKey || document.getElementById('api-key-text')?.innerText || '';
        try {
            await navigator.clipboard.writeText(textToCopy);
            copyBtn.innerText = 'Copied!';
            setTimeout(() => { copyBtn.innerText = 'Copy Key'; }, 2000);
        } catch (e) {
            alert('API Key: ' + textToCopy);
        }
    });

    regenBtn?.addEventListener('click', async () => {
        if (!confirm('Are you sure you want to regenerate your API key? Any SDK using the old key will stop sending events.')) return;
        try {
            const res = await fetchWithAuth(`${APP_CONFIG.RENDER_API_BASE}/auth/api-key/regenerate`, { method: 'POST' });
            if (res.ok) {
                const data = await res.json();
                if (data.api_key) {
                    localStorage.setItem('governance_active_api_key', data.api_key);
                    document.getElementById('api-key-text').innerText = data.api_key;
                    document.getElementById('api-key-full-secret').innerText = data.api_key;
                    document.getElementById('api-key-new-alert').style.display = 'block';
                    try { await navigator.clipboard.writeText(data.api_key); } catch(e){}
                    fetchUserApiKey();
                }
            } else {
                alert('Failed to regenerate API key.');
            }
        } catch (err) {
            alert('Regenerate Error: ' + err.message);
        }
    });
}

// Supabase & Backend Auth Session Check
async function checkAuthSession() {
    const savedUser = localStorage.getItem('governance_user_profile');
    if (savedUser) {
        try {
            const userObj = JSON.parse(savedUser);
            showDashboardView(userObj);
            return;
        } catch(e) {}
    }

    if (supabaseClient) {
        const { data: { session } } = await supabaseClient.auth.getSession();
        if (session && session.user) {
            showDashboardView({
                full_name: session.user.user_metadata?.full_name || session.user.email.split('@')[0],
                organization_name: `${session.user.user_metadata?.full_name || 'User'}'s Workspace`
            });
            return;
        }
    }

    showAuthLandingView();
}

function showAuthLandingView() {
    document.getElementById('auth-view').style.display = 'flex';
    document.getElementById('dashboard-view').style.display = 'none';
}

function showDashboardView(userObj = null) {
    document.getElementById('auth-view').style.display = 'none';
    document.getElementById('dashboard-view').style.display = 'block';

    if (userObj) {
        currentUserName = userObj.full_name || "Account User";
        document.getElementById('header-user-name').innerText = currentUserName;
    } else {
        document.getElementById('header-user-name').innerText = "Demo Visitor";
    }

    loadAllData();
}

function initAuthLanding() {
    const toggleLogin = document.getElementById('toggle-login-mode');
    const toggleSignup = document.getElementById('toggle-signup-mode');
    const loginForm = document.getElementById('auth-login-form');
    const signupForm = document.getElementById('auth-signup-form');

    // Switch between Sign In and Create Account
    toggleLogin?.addEventListener('click', () => {
        toggleLogin.classList.add('active');
        toggleSignup.classList.remove('active');
        loginForm.style.display = 'block';
        signupForm.style.display = 'none';
    });

    toggleSignup?.addEventListener('click', () => {
        toggleSignup.classList.add('active');
        toggleLogin.classList.remove('active');
        signupForm.style.display = 'block';
        loginForm.style.display = 'none';
    });

    // Sign In Submit
    loginForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('auth-login-email').value;
        const password = document.getElementById('auth-login-password').value;
        const errDiv = document.getElementById('auth-login-error');

        errDiv.style.display = 'none';

        // 1. Try Direct Backend Auth
        try {
            const res = await fetch(`${APP_CONFIG.RENDER_API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (res.ok) {
                const data = await res.json();
                localStorage.setItem('governance_auth_token', data.access_token);
                localStorage.setItem('governance_user_profile', JSON.stringify(data.user));
                if (data.api_key && data.api_key !== 'null') {
                    localStorage.setItem('governance_active_api_key', data.api_key);
                }
                showDashboardView(data.user);
                return;
            }
        } catch (e) {}

        // 2. Try Supabase Auth
        if (supabaseClient) {
            const { data, error } = await supabaseClient.auth.signInWithPassword({ email, password });
            if (error) {
                errDiv.innerText = error.message;
                errDiv.style.display = 'block';
            } else {
                const userObj = {
                    full_name: data.session.user.user_metadata?.full_name || email.split('@')[0]
                };
                localStorage.setItem('governance_user_profile', JSON.stringify(userObj));
                showDashboardView(userObj);
            }
        } else {
            errDiv.innerText = "Invalid credentials. Please check your email and password or create an account.";
            errDiv.style.display = 'block';
        }
    });

    // Create Account Submit
    signupForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fullName = document.getElementById('auth-signup-name').value;
        const email = document.getElementById('auth-signup-email').value;
        const password = document.getElementById('auth-signup-password').value;
        const errDiv = document.getElementById('auth-signup-error');

        errDiv.style.display = 'none';

        // 1. Try Direct Backend Signup (Guarantees instant save in database)
        try {
            const res = await fetch(`${APP_CONFIG.RENDER_API_BASE}/auth/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ full_name: fullName, email, password })
            });

            if (res.ok) {
                const data = await res.json();
                localStorage.setItem('governance_auth_token', `user_token_${data.user.id}`);
                localStorage.setItem('governance_user_profile', JSON.stringify(data.user));
                if (data.api_key && data.api_key !== 'null') {
                    localStorage.setItem('governance_active_api_key', data.api_key);
                }
                showDashboardView(data.user);
                return;
            } else {
                const errJson = await res.json();
                if (errJson.detail) {
                    errDiv.innerText = errJson.detail;
                    errDiv.style.display = 'block';
                    return;
                }
            }
        } catch (e) {}

        // 2. Fallback to Supabase Auth Signup
        if (supabaseClient) {
            const { data, error } = await supabaseClient.auth.signUp({
                email,
                password,
                options: { data: { full_name: fullName } }
            });

            if (error) {
                errDiv.innerText = error.message;
                errDiv.style.display = 'block';
            } else {
                const userObj = { full_name: fullName };
                localStorage.setItem('governance_user_profile', JSON.stringify(userObj));
                showDashboardView(userObj);
            }
        }
    });

    // Public Guest Demo Mode
    document.getElementById('btn-guest-demo')?.addEventListener('click', () => {
        localStorage.removeItem('governance_auth_token');
        localStorage.removeItem('governance_user_profile');
        localStorage.removeItem('governance_active_api_key');
        showDashboardView();
    });

    // Logout
    document.getElementById('btn-logout')?.addEventListener('click', async () => {
        localStorage.removeItem('governance_auth_token');
        localStorage.removeItem('governance_user_profile');
        localStorage.removeItem('governance_active_api_key');
        if (supabaseClient) {
            await supabaseClient.auth.signOut();
        }
        showAuthLandingView();
    });
}

// Fetch & Load All Data
async function loadAllData() {
    await fetchUserProfile();
    await fetchUserApiKey();
    await Promise.all([
        fetchEvents(),
        fetchModels(),
        fetchAgents()
    ]);
}

async function fetchUserProfile() {
    try {
        const res = await fetchWithAuth(`${APP_CONFIG.RENDER_API_BASE}/auth/me`);
        if (res.ok) {
            const profile = await res.json();
            if (profile.full_name) {
                document.getElementById('header-user-name').innerText = profile.full_name;
            }
        }
    } catch (e) {
        console.warn("User profile fetch error:", e);
    }
}

async function fetchUserApiKey() {
    try {
        const cachedKey = localStorage.getItem('governance_active_api_key');
        const res = await fetchWithAuth(`${APP_CONFIG.RENDER_API_BASE}/auth/api-key`);
        if (res.ok) {
            const data = await res.json();
            const keyText = cachedKey || (data.key_prefix ? `${data.key_prefix}••••••••••••` : 'usr_live_demo_key');
            
            const keyTextElem = document.getElementById('api-key-text');
            if (keyTextElem) keyTextElem.innerText = keyText;

            const step3Box = document.getElementById('step3-config-box');
            if (step3Box) {
                step3Box.innerText = `TRACKER_URL="https://model-substitution-governance-event.onrender.com"\nAPI_KEY="${cachedKey || (data.key_prefix ? data.key_prefix + '...' : 'usr_live_your_api_key_here')}"`;
            }
        }
    } catch (e) {
        console.warn("API Key fetch error:", e);
    }
}

async function fetchEvents() {
    try {
        const res = await fetchWithAuth(`${APP_CONFIG.RENDER_API_BASE}/events?limit=500`);
        if (!res.ok) throw new Error('API Error');
        eventsData = await res.json();

        updateHealthStatus(true, true);
        renderEventsTable();
        renderRiskTable();
        updateKPIs();
        populateAgentFilter();
    } catch (err) {
        console.error("Fetch Events Error:", err);
        updateHealthStatus(false, false);
    }
}

async function fetchModels() {
    try {
        const res = await fetch(`${APP_CONFIG.RENDER_API_BASE}/models`);
        if (!res.ok) throw new Error('API Error');
        modelsData = await res.json();
        renderModelsTable();
    } catch (err) {
        console.error("Fetch Models Error:", err);
    }
}

async function fetchAgents() {
    try {
        const res = await fetchWithAuth(`${APP_CONFIG.RENDER_API_BASE}/agents`);
        if (!res.ok) throw new Error('API Error');
        agentsData = await res.json();
        renderComplianceTable();
    } catch (err) {
        console.error("Fetch Agents Error:", err);
    }
}

function updateHealthStatus(backendOk, dbOk) {
    const dotBackend = document.getElementById('dot-backend');
    const textBackend = document.getElementById('text-backend');

    if (backendOk) {
        dotBackend.className = 'status-dot green';
        textBackend.innerText = 'Online';
    } else {
        dotBackend.className = 'status-dot red';
        textBackend.innerText = 'Offline';
    }
}

function updateKPIs() {
    const total = eventsData.length;
    const highRisk = eventsData.filter(e => e.risk_level === 'High' || e.risk_level === 'Critical').length;
    const violations = eventsData.filter(e => e.compliance_flagged).length;

    document.getElementById('kpi-total').innerText = total;
    document.getElementById('kpi-high-risk').innerText = highRisk;
    document.getElementById('kpi-violations').innerText = violations;
    if (modelsData.length > 0) {
        document.getElementById('kpi-models-count').innerText = modelsData.length;
    }
}

function populateAgentFilter() {
    const select = document.getElementById('filter-agent');
    if (!select) return;
    const currentVal = select.value;
    const uniqueAgents = [...new Set(eventsData.map(e => e.agent_id))];

    select.innerHTML = '<option value="">All Agents</option>';
    uniqueAgents.forEach(agent => {
        const opt = document.createElement('option');
        opt.value = agent;
        opt.innerText = agent;
        select.appendChild(opt);
    });
    select.value = currentVal;
}

// Render Event Recorder Table
function renderEventsTable() {
    const tbody = document.getElementById('events-tbody');
    if (!tbody) return;

    const agentFilter = document.getElementById('filter-agent')?.value;
    const reasonFilter = document.getElementById('filter-reason')?.value;
    const riskFilter = document.getElementById('filter-risk')?.value;
    const complianceFilter = document.getElementById('filter-compliance')?.value;

    let filtered = eventsData.filter(e => {
        if (agentFilter && e.agent_id !== agentFilter) return false;
        if (reasonFilter && e.reason !== reasonFilter) return false;
        if (riskFilter && e.risk_level !== riskFilter) return false;
        if (complianceFilter === 'true' && !e.compliance_flagged) return false;
        if (complianceFilter === 'false' && e.compliance_flagged) return false;
        return true;
    });

    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center">No governance events match filters.</td></tr>';
        return;
    }

    tbody.innerHTML = filtered.map(e => `
        <tr>
            <td class="font-mono text-sm">${new Date(e.timestamp).toLocaleString()}</td>
            <td><strong>${e.agent_id}</strong></td>
            <td><span class="model-tag requested">${e.requested_model}</span></td>
            <td><span class="model-tag actual">${e.actual_model}</span></td>
            <td><span class="badge reason-${e.reason.toLowerCase()}">${e.reason.toUpperCase()}</span></td>
            <td><span class="badge risk-${e.risk_level.toLowerCase()}">${e.risk_level.toUpperCase()}</span></td>
            <td>
                ${e.compliance_flagged 
                    ? '<span class="badge status-flagged">VIOLATION FLAGGED</span>' 
                    : '<span class="badge status-approved">COMPLIANT</span>'}
            </td>
            <td>
                <button class="btn btn-secondary text-sm" onclick="inspectEvent('${e.id}')">Inspect</button>
            </td>
        </tr>
    `).join('');
}

// Render Risk Assessor Table
function renderRiskTable() {
    const tbody = document.getElementById('risk-tbody');
    if (!tbody) return;

    if (eventsData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No capability risk assessments found.</td></tr>';
        return;
    }

    tbody.innerHTML = eventsData.map(e => `
        <tr>
            <td><strong>${e.agent_id}</strong></td>
            <td><span class="model-tag requested">${e.requested_model}</span></td>
            <td><span class="model-tag actual">${e.actual_model}</span></td>
            <td class="font-mono"><strong>${e.context_downgrade_pct}%</strong></td>
            <td><span class="badge risk-${e.risk_level.toLowerCase()}">${e.risk_level.toUpperCase()}</span></td>
            <td class="text-sm color-muted">${e.risk_reason}</td>
        </tr>
    `).join('');
}

// Render Compliance Whitelist Table
function renderComplianceTable() {
    const tbody = document.getElementById('compliance-tbody');
    if (!tbody) return;

    if (agentsData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center">No agent compliance policies found.</td></tr>';
        return;
    }

    tbody.innerHTML = agentsData.map(a => `
        <tr>
            <td><strong>${a.agent_id}</strong></td>
            <td>${a.agent_name}</td>
            <td>
                ${a.approved_models.map(m => `<span class="model-tag approved">${m}</span>`).join(' ')}
            </td>
            <td><span class="badge status-approved">WHITELIST ACTIVE</span></td>
        </tr>
    `).join('');
}

// Render Model Profiles Table
function renderModelsTable() {
    const tbody = document.getElementById('models-tbody');
    if (!tbody) return;

    const query = document.getElementById('search-models')?.value?.toLowerCase() || '';
    let filtered = modelsData.filter(m => m.model_name.toLowerCase().includes(query));

    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="text-center">No model profiles match search.</td></tr>';
        return;
    }

    tbody.innerHTML = filtered.map(m => `
        <tr>
            <td><strong>${m.model_name}</strong></td>
            <td class="font-mono">${m.context_window.toLocaleString()} tokens</td>
            <td><span class="badge status-approved">VERIFIED PROFILE</span></td>
        </tr>
    `).join('');
}

// Event Inspector Modal
window.inspectEvent = function(eventId) {
    const event = eventsData.find(e => e.id === eventId);
    if (!event) return;

    const modalContent = document.getElementById('modal-content');
    modalContent.innerHTML = `
        <div class="detail-row"><strong>Event ID:</strong> <span class="font-mono">${event.id}</span></div>
        <div class="detail-row"><strong>Timestamp:</strong> ${new Date(event.timestamp).toLocaleString()}</div>
        <div class="detail-row"><strong>Agent ID:</strong> ${event.agent_id}</div>
        <div class="detail-row"><strong>Session ID:</strong> <span class="font-mono">${event.session_id}</span></div>
        <hr class="divider">
        <div class="detail-row"><strong>Requested Model:</strong> <span class="model-tag requested">${event.requested_model}</span></div>
        <div class="detail-row"><strong>Actual Model Used:</strong> <span class="model-tag actual">${event.actual_model}</span></div>
        <div class="detail-row"><strong>Substitution Reason:</strong> <span class="badge reason-${event.reason.toLowerCase()}">${event.reason.toUpperCase()}</span></div>
        <hr class="divider">
        <div class="detail-row"><strong>Capability Risk Level:</strong> <span class="badge risk-${event.risk_level.toLowerCase()}">${event.risk_level.toUpperCase()}</span></div>
        <div class="detail-row"><strong>Context Reduction:</strong> ${event.context_downgrade_pct}%</div>
        <div class="explanation-box">${event.risk_reason}</div>
        <hr class="divider">
        <div class="detail-row"><strong>Compliance Status:</strong> 
            ${event.compliance_flagged 
                ? '<span class="badge status-flagged">VIOLATION FLAGGED</span>' 
                : '<span class="badge status-approved">COMPLIANT</span>'}
        </div>
        ${event.compliance_reason ? `<div class="explanation-box text-danger">${event.compliance_reason}</div>` : ''}
    `;

    document.getElementById('event-modal').classList.add('active');
};

// Retroactive Audit Trigger
function initAuditButton() {
    document.getElementById('btn-run-audit')?.addEventListener('click', async () => {
        const container = document.getElementById('audit-results-container');
        container.innerHTML = '<p>Running retroactive compliance audit across historical substitution logs...</p>';

        try {
            const res = await fetchWithAuth(`${APP_CONFIG.RENDER_API_BASE}/compliance/audit`);
            if (!res.ok) throw new Error("Audit failed");
            const audit = await res.json();

            container.innerHTML = `
                <div class="kpi-grid margin-top" style="grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));">
                    <div class="kpi-card">
                        <div class="kpi-title">ANALYZED EVENTS</div>
                        <div class="kpi-value">${audit.total_events_analyzed}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">UNAPPROVED REQUESTS</div>
                        <div class="kpi-value text-danger">${audit.total_unapproved_requests}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">FLAG RATE %</div>
                        <div class="kpi-value text-danger">${audit.compliance_flag_rate_pct}%</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">HIGH RISK EXPOSURE</div>
                        <div class="kpi-value">${audit.high_risk_exposure_pct}%</div>
                    </div>
                </div>

                <div class="margin-top">
                    <h4>Audit Log Details (Flagged Substitutions)</h4>
                    ${audit.unapproved_events.length === 0 ? '<p class="text-success margin-top">✔ Zero compliance violations found in historical logs.</p>' : `
                        <div class="table-container margin-top">
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>Timestamp</th>
                                        <th>Agent ID</th>
                                        <th>Requested</th>
                                        <th>Actual Used</th>
                                        <th>Compliance Audit Violation Reason</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${audit.unapproved_events.map(u => `
                                        <tr>
                                            <td class="font-mono text-sm">${new Date(u.timestamp).toLocaleString()}</td>
                                            <td><strong>${u.agent_id}</strong></td>
                                            <td><span class="model-tag requested">${u.requested_model}</span></td>
                                            <td><span class="model-tag actual">${u.actual_model}</span></td>
                                            <td class="text-danger text-sm">${u.compliance_reason}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    `}
                </div>
            `;
        } catch (err) {
            container.innerHTML = `<p class="text-danger">Audit Error: ${err.message}</p>`;
        }
    });
}

// Navigation & Modals
function initTabNavigation() {
    const buttons = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');
    const kpiGrid = document.querySelector('.kpi-grid');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            buttons.forEach(b => b.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const targetId = btn.getAttribute('data-tab');
            document.getElementById(targetId)?.classList.add('active');

            if (kpiGrid) {
                kpiGrid.style.display = (targetId === 'tab-integration') ? 'none' : 'grid';
            }
        });
    });

    document.getElementById('btn-goto-integration')?.addEventListener('click', () => {
        document.querySelector('.tab-btn[data-tab="tab-integration"]')?.click();
    });
}

function initFilterListeners() {
    ['filter-agent', 'filter-reason', 'filter-risk', 'filter-compliance'].forEach(id => {
        document.getElementById(id)?.addEventListener('change', renderEventsTable);
    });
    document.getElementById('search-models')?.addEventListener('input', renderModelsTable);
    document.getElementById('btn-refresh')?.addEventListener('click', loadAllData);
}

function initModalListeners() {
    document.getElementById('modal-close-btn')?.addEventListener('click', () => {
        document.getElementById('event-modal').classList.remove('active');
    });

    document.getElementById('btn-open-arch')?.addEventListener('click', () => {
        document.getElementById('arch-modal').classList.add('active');
    });
    document.getElementById('arch-close-btn')?.addEventListener('click', () => {
        document.getElementById('arch-modal').classList.remove('active');
    });

    document.querySelectorAll('.help-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const helpKey = btn.getAttribute('data-help');
            if (helpTexts[helpKey]) {
                document.getElementById('help-modal-title').innerText = helpTexts[helpKey].title;
                document.getElementById('help-modal-content').innerHTML = helpTexts[helpKey].content;
                document.getElementById('help-modal').classList.add('active');
            }
        });
    });

    document.getElementById('help-close-btn')?.addEventListener('click', () => {
        document.getElementById('help-modal').classList.remove('active');
    });
}

// Live Gateway Traffic Simulator
function initSimulator() {
    const runSim = async () => {
        const sampleEvents = [
            { requested_model: "GPT-5", actual_model: "GPT-4o Mini", reason: "cost", agent_id: "HR-Agent", session_id: "sess-sim-" + Math.floor(Math.random()*1000) },
            { requested_model: "Claude 3.5 Sonnet", actual_model: "Claude 3 Haiku", reason: "availability", agent_id: "Finance-Bot", session_id: "sess-sim-" + Math.floor(Math.random()*1000) },
            { requested_model: "Gemini 1.5 Pro", actual_model: "Gemini 1.5 Flash", reason: "cost", agent_id: "Support-Router", session_id: "sess-sim-" + Math.floor(Math.random()*1000) }
        ];

        const payload = sampleEvents[Math.floor(Math.random() * sampleEvents.length)];

        try {
            const res = await fetchWithAuth(`${APP_CONFIG.RENDER_API_BASE}/events`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                alert(`Simulated Substitution Event Sent!\nRequested: ${payload.requested_model} → Actual: ${payload.actual_model}`);
                loadAllData();
            }
        } catch (e) {
            alert("Simulation failed: " + e.message);
        }
    };

    document.getElementById('btn-open-sim')?.addEventListener('click', runSim);
    document.getElementById('btn-run-sim-step')?.addEventListener('click', runSim);
}
