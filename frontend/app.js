document.addEventListener('DOMContentLoaded', () => {
    // Dynamic API Base URL setup: Use live Render URL when hosted on Vercel or external domain
    let API_BASE = '/api/v1';
    if (window.location.hostname.includes('vercel.app') || window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        API_BASE = 'https://model-substitution-governance-event.onrender.com/api/v1';
    }

    // State Variables
    let eventsData = [];
    let modelsData = [];
    let agentsData = [];

    // DOM Elements
    const eventsTbody = document.getElementById('events-tbody');
    const modelsTbody = document.getElementById('models-tbody');
    const agentsTbody = document.getElementById('agents-tbody');
    const auditContainer = document.getElementById('audit-results-container');
    const apiStatus = document.getElementById('api-status');

    const kpiTotal = document.getElementById('kpi-total');
    const kpiHighRisk = document.getElementById('kpi-high-risk');
    const kpiViolations = document.getElementById('kpi-violations');
    const kpiModelsCount = document.getElementById('kpi-models-count');

    const filterAgent = document.getElementById('filter-agent');
    const filterReason = document.getElementById('filter-reason');
    const filterRisk = document.getElementById('filter-risk');
    const filterCompliance = document.getElementById('filter-compliance');
    const searchModels = document.getElementById('search-models');

    const btnRefresh = document.getElementById('btn-refresh');
    const btnOpenSim = document.getElementById('btn-open-sim');
    const btnRunAudit = document.getElementById('btn-run-audit');

    const eventModal = document.getElementById('event-modal');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const modalContent = document.getElementById('modal-content');

    // Tab Navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(btn.dataset.tab).classList.add('active');
        });
    });

    // Modal Close handlers
    modalCloseBtn.addEventListener('click', () => eventModal.classList.remove('active'));
    eventModal.addEventListener('click', (e) => {
        if (e.target === eventModal) eventModal.classList.remove('active');
    });

    // Refresh Data
    btnRefresh.addEventListener('click', loadAllData);
    btnOpenSim.addEventListener('click', async () => {
        btnOpenSim.innerText = '⚡ Simulating...';
        try {
            // Trigger sample substitutions via API calls
            const testPayloads = [
                { requested_model: "GPT-5", actual_model: "GPT-4o Mini", reason: "cost", agent_id: "HR-Agent", session_id: "sim-" + Math.floor(Math.random() * 10000) },
                { requested_model: "Claude Opus 4", actual_model: "Gemini 1.5 Flash", reason: "availability", agent_id: "Finance-Bot", session_id: "sim-" + Math.floor(Math.random() * 10000) },
                { requested_model: "GPT-5", actual_model: "GPT-3.5 Turbo", reason: "cost", agent_id: "HR-Agent", session_id: "sim-" + Math.floor(Math.random() * 10000) },
                { requested_model: "Claude Opus 4", actual_model: "Gemini 1.5 Pro", reason: "availability", agent_id: "Finance-Bot", session_id: "sim-" + Math.floor(Math.random() * 10000) }
            ];

            for (const p of testPayloads) {
                await fetch(`${API_BASE}/events`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(p)
                });
            }
            await loadAllData();
        } catch (e) {
            console.error('Simulator error:', e);
        } finally {
            btnOpenSim.innerText = '⚡ Gateway Simulator';
        }
    });

    // Run Retroactive Audit Button
    btnRunAudit.addEventListener('click', loadAuditReport);

    // Filter Listeners
    [filterAgent, filterReason, filterRisk, filterCompliance].forEach(elem => {
        elem.addEventListener('change', renderEventsTable);
    });

    if (searchModels) {
        searchModels.addEventListener('input', renderModelsTable);
    }

    // Initial Load
    loadAllData();

    async function loadAllData() {
        await Promise.all([
            fetchEvents(),
            fetchModels(),
            fetchAgents()
        ]);
        updateKPIs();
        renderEventsTable();
        renderModelsTable();
        renderAgentsTable();
        populateAgentFilter();
    }

    async function fetchEvents() {
        try {
            const res = await fetch(`${API_BASE}/events?limit=200`);
            if (res.ok) {
                eventsData = await res.json();
                if (apiStatus) apiStatus.innerHTML = '<span class="status-dot green"></span> Live API Connected';
            } else {
                if (apiStatus) apiStatus.innerHTML = '<span class="status-dot red"></span> API Disconnected';
            }
        } catch (err) {
            console.error('Error fetching events:', err);
            if (apiStatus) apiStatus.innerHTML = '<span class="status-dot red"></span> API Offline';
        }
    }

    async function fetchModels() {
        try {
            const res = await fetch(`${API_BASE}/models`);
            if (res.ok) {
                modelsData = await res.json();
            }
        } catch (err) {
            console.error('Error fetching models:', err);
        }
    }

    async function fetchAgents() {
        try {
            const res = await fetch(`${API_BASE}/agents`);
            if (res.ok) {
                agentsData = await res.json();
            }
        } catch (err) {
            console.error('Error fetching agents:', err);
        }
    }

    function updateKPIs() {
        kpiTotal.innerText = eventsData.length;
        const highRiskCount = eventsData.filter(e => e.risk_level === 'High' || e.risk_level === 'Critical').length;
        kpiHighRisk.innerText = highRiskCount;
        const violationsCount = eventsData.filter(e => e.compliance_flagged).length;
        kpiViolations.innerText = violationsCount;
        kpiModelsCount.innerText = modelsData.length > 0 ? modelsData.length : '50+';
    }

    function populateAgentFilter() {
        const currentSelected = filterAgent.value;
        filterAgent.innerHTML = '<option value="">All Agents</option>';
        const agentIds = [...new Set(eventsData.map(e => e.agent_id))];
        agentIds.forEach(id => {
            const opt = document.createElement('option');
            opt.value = id;
            opt.innerText = id;
            if (id === currentSelected) opt.selected = true;
            filterAgent.appendChild(opt);
        });
    }

    function renderEventsTable() {
        const agent = filterAgent.value;
        const reason = filterReason.value.toLowerCase();
        const risk = filterRisk.value;
        const compliance = filterCompliance.value;

        const filtered = eventsData.filter(e => {
            if (agent && e.agent_id !== agent) return false;
            if (reason && e.reason.toLowerCase() !== reason) return false;
            if (risk && e.risk_level !== risk) return false;
            if (compliance === 'true' && !e.compliance_flagged) return false;
            if (compliance === 'false' && e.compliance_flagged) return false;
            return true;
        });

        if (filtered.length === 0) {
            eventsTbody.innerHTML = `<tr><td colspan="8" class="text-center">No governance events match the selected filters. Click "⚡ Gateway Simulator" to generate sample live events.</td></tr>`;
            return;
        }

        eventsTbody.innerHTML = filtered.map(e => {
            const dateStr = new Date(e.timestamp).toLocaleString();
            const riskBadgeClass = `badge risk-${e.risk_level.toLowerCase()}`;
            const compBadgeClass = e.compliance_flagged ? 'badge status-flagged' : 'badge status-approved';
            const compText = e.compliance_flagged ? '⛔ Violation Flagged' : '✅ Compliant';

            return `
                <tr>
                    <td class="font-mono text-sm">${dateStr}</td>
                    <td><strong>${escapeHtml(e.agent_id)}</strong></td>
                    <td><span class="model-tag requested">${escapeHtml(e.requested_model)}</span></td>
                    <td><span class="model-tag actual">${escapeHtml(e.actual_model)}</span></td>
                    <td><span class="badge reason-${e.reason.toLowerCase()}">${escapeHtml(e.reason.toUpperCase())}</span></td>
                    <td><span class="${riskBadgeClass}">${escapeHtml(e.risk_level)}</span></td>
                    <td><span class="${compBadgeClass}">${compText}</span></td>
                    <td>
                        <button class="btn btn-secondary text-sm" onclick="window.inspectEvent('${e.id}')">Inspect</button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    function renderModelsTable() {
        const query = (searchModels ? searchModels.value : '').toLowerCase();
        const filtered = modelsData.filter(m => m.model_name.toLowerCase().includes(query));

        if (filtered.length === 0) {
            modelsTbody.innerHTML = `<tr><td colspan="3" class="text-center">No model profiles found.</td></tr>`;
            return;
        }

        modelsTbody.innerHTML = filtered.map(m => `
            <tr>
                <td><strong>${escapeHtml(m.model_name)}</strong></td>
                <td><span class="font-mono">${m.context_window.toLocaleString()} tokens</span></td>
                <td><span class="badge status-approved">Context Profile Verified</span></td>
            </tr>
        `).join('');
    }

    function renderAgentsTable() {
        if (agentsData.length === 0) {
            agentsTbody.innerHTML = `<tr><td colspan="4" class="text-center">No agent policies configured.</td></tr>`;
            return;
        }

        agentsTbody.innerHTML = agentsData.map(a => `
            <tr>
                <td><strong>${escapeHtml(a.agent_id)}</strong></td>
                <td>${escapeHtml(a.agent_name)}</td>
                <td>${escapeHtml(a.description || 'N/A')}</td>
                <td>
                    ${a.approved_models.map(m => `<span class="model-tag approved">${escapeHtml(m)}</span>`).join(' ')}
                </td>
            </tr>
        `).join('');
    }

    async function loadAuditReport() {
        auditContainer.innerHTML = '<p class="subtitle">Computing retroactive audit across historical records...</p>';
        try {
            const res = await fetch(`${API_BASE}/compliance/audit`);
            if (res.ok) {
                const data = await res.json();
                auditContainer.innerHTML = `
                    <div class="kpi-grid">
                        <div class="kpi-card">
                            <div class="kpi-title">EVENTS ANALYZED</div>
                            <div class="kpi-value">${data.total_events_analyzed}</div>
                        </div>
                        <div class="kpi-card danger">
                            <div class="kpi-title">UNAPPROVED REQUESTS</div>
                            <div class="kpi-value">${data.total_unapproved_requests}</div>
                            <div class="kpi-sub">${data.compliance_flag_rate_pct}% Violation Rate</div>
                        </div>
                        <div class="kpi-card warning">
                            <div class="kpi-title">HIGH RISK EXPOSURE</div>
                            <div class="kpi-value">${data.high_risk_substitutions}</div>
                            <div class="kpi-sub">${data.high_risk_exposure_pct}% Exposure Ratio</div>
                        </div>
                    </div>
                    ${data.unapproved_events.length > 0 ? `
                        <h3 class="margin-top">Flagged Compliance Violation Events</h3>
                        <div class="table-container">
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>Agent ID</th>
                                        <th>Requested</th>
                                        <th>Actual Used</th>
                                        <th>Compliance Reason</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${data.unapproved_events.map(ev => `
                                        <tr>
                                            <td><strong>${escapeHtml(ev.agent_id)}</strong></td>
                                            <td>${escapeHtml(ev.requested_model)}</td>
                                            <td>${escapeHtml(ev.actual_model)}</td>
                                            <td class="text-danger">${escapeHtml(ev.compliance_reason)}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    ` : '<p class="subtitle text-success">No compliance violations detected in recent event logs.</p>'}
                `;
            }
        } catch (e) {
            console.error('Audit report error:', e);
            auditContainer.innerHTML = '<p class="subtitle text-danger">Failed to generate audit report.</p>';
        }
    }

    // Modal Inspection Helper
    window.inspectEvent = function(eventId) {
        const ev = eventsData.find(e => e.id === eventId);
        if (!ev) return;

        modalContent.innerHTML = `
            <div class="detail-row"><strong>Event ID:</strong> <span class="font-mono">${ev.id}</span></div>
            <div class="detail-row"><strong>Timestamp:</strong> ${new Date(ev.timestamp).toLocaleString()}</div>
            <div class="detail-row"><strong>Agent ID:</strong> ${escapeHtml(ev.agent_id)}</div>
            <div class="detail-row"><strong>Session ID:</strong> <span class="font-mono">${escapeHtml(ev.session_id)}</span></div>
            <hr class="divider"/>
            <div class="detail-row"><strong>Requested Model:</strong> <span class="model-tag requested">${escapeHtml(ev.requested_model)}</span></div>
            <div class="detail-row"><strong>Actual Model Used:</strong> <span class="model-tag actual">${escapeHtml(ev.actual_model)}</span></div>
            <div class="detail-row"><strong>Substitution Reason:</strong> <span class="badge reason-${ev.reason.toLowerCase()}">${escapeHtml(ev.reason.toUpperCase())}</span></div>
            <hr class="divider"/>
            <div class="detail-row"><strong>Risk Assessment Level:</strong> <span class="badge risk-${ev.risk_level.toLowerCase()}">${escapeHtml(ev.risk_level)}</span></div>
            <div class="detail-row"><strong>Context Capacity Downgrade:</strong> ${ev.context_downgrade_pct}% reduction</div>
            <div class="detail-row"><strong>Risk Analysis Details:</strong> ${escapeHtml(ev.risk_reason)}</div>
            <hr class="divider"/>
            <div class="detail-row"><strong>Compliance Status:</strong> ${ev.compliance_flagged ? '<span class="badge status-flagged">⛔ VIOLATION FLAGGED</span>' : '<span class="badge status-approved">✅ COMPLIANT</span>'}</div>
            ${ev.compliance_reason ? `<div class="detail-row text-danger"><strong>Violation Reason:</strong> ${escapeHtml(ev.compliance_reason)}</div>` : ''}
        `;
        eventModal.classList.add('active');
    };

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }
});
