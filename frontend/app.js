// Model Substitution Governance Tracker - Enterprise Dashboard JS

const API_BASE = window.location.origin;

let allEvents = [];
let allAgents = [];
let allModels = [];

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initEventListeners();
    loadDashboardData();
});

function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
            
            btn.classList.add("active");
            const target = btn.getAttribute("data-tab");
            document.getElementById(target).classList.add("active");

            if (target === "tab-audit") loadAuditSummary();
            if (target === "tab-agents") loadAgentPolicies();
            if (target === "tab-models") loadModelProfiles();
        });
    });
}

function initEventListeners() {
    document.getElementById("btn-refresh").addEventListener("click", loadDashboardData);
    
    // Filters
    document.getElementById("filter-agent").addEventListener("change", applyFilters);
    document.getElementById("filter-reason").addEventListener("change", applyFilters);
    document.getElementById("filter-risk").addEventListener("change", applyFilters);
    document.getElementById("filter-flagged").addEventListener("change", applyFilters);
    document.getElementById("filter-search").addEventListener("input", applyFilters);

    // Modals
    document.getElementById("modal-close").addEventListener("click", () => {
        document.getElementById("event-modal").classList.remove("active");
    });
    document.getElementById("sim-close").addEventListener("click", () => {
        document.getElementById("sim-modal").classList.remove("active");
    });
    document.getElementById("btn-open-sim").addEventListener("click", () => {
        document.getElementById("sim-modal").classList.add("active");
    });
}

async function loadDashboardData() {
    try {
        const [eventsRes, agentsRes] = await Promise.all([
            fetch(`${API_BASE}/events?limit=200`),
            fetch(`${API_BASE}/agents`)
        ]);

        if (eventsRes.ok) {
            allEvents = await eventsRes.json();
            updateKPIs(allEvents);
            applyFilters();
        }

        if (agentsRes.ok) {
            allAgents = await agentsRes.json();
            populateAgentFilter(allAgents);
        }

        document.getElementById("api-status").innerHTML = `<span class="status-dot green"></span> API Connected`;
    } catch (err) {
        console.error("Error loading dashboard data:", err);
        document.getElementById("api-status").innerHTML = `<span class="status-dot red"></span> Disconnected`;
    }
}

function updateKPIs(events) {
    const total = events.length;
    const violations = events.filter(e => e.compliance_flagged).length;
    const highRisk = events.filter(e => e.risk_level === "High" || e.risk_level === "Critical").length;
    const uniqueAgents = new Set(events.map(e => e.agent_id)).size;

    document.getElementById("kpi-total").innerText = total;
    document.getElementById("kpi-violations").innerText = violations;
    const rate = total > 0 ? ((violations / total) * 100).toFixed(1) : "0";
    document.getElementById("kpi-violation-rate").innerText = `${rate}% Exposure Rate`;
    
    document.getElementById("kpi-high-risk").innerText = highRisk;
    document.getElementById("kpi-agents").innerText = uniqueAgents;
}

function populateAgentFilter(agents) {
    const select = document.getElementById("filter-agent");
    const current = select.value;
    select.innerHTML = `<option value="">All Agents</option>`;
    agents.forEach(a => {
        const opt = document.createElement("option");
        opt.value = a.agent_id;
        opt.textContent = a.agent_name || a.agent_id;
        select.appendChild(opt);
    });
    select.value = current;
}

function applyFilters() {
    const agent = document.getElementById("filter-agent").value;
    const reason = document.getElementById("filter-reason").value;
    const risk = document.getElementById("filter-risk").value;
    const flaggedOnly = document.getElementById("filter-flagged").checked;
    const search = document.getElementById("filter-search").value.toLowerCase().trim();

    let filtered = allEvents.filter(e => {
        if (agent && e.agent_id !== agent) return false;
        if (reason && e.reason !== reason) return false;
        if (risk && e.risk_level !== risk) return false;
        if (flaggedOnly && !e.compliance_flagged) return false;
        if (search) {
            const haystack = `${e.requested_model} ${e.actual_model} ${e.agent_id} ${e.session_id}`.toLowerCase();
            if (!haystack.includes(search)) return false;
        }
        return true;
    });

    renderEventsTable(filtered);
}

function renderEventsTable(events) {
    const tbody = document.getElementById("events-tbody");
    if (events.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 2rem; color: #9ca3af;">No governance events match criteria.</td></tr>`;
        return;
    }

    tbody.innerHTML = events.map(e => {
        const timeStr = new Date(e.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const complianceBadge = e.compliance_flagged 
            ? `<span class="badge badge-violation">⚠️ VIOLATION</span>`
            : `<span class="badge badge-compliant">✓ COMPLIANT</span>`;

        return `
            <tr>
                <td style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted);">${timeStr}</td>
                <td><strong>${e.agent_id}</strong></td>
                <td style="font-family: var(--font-mono); font-size: 0.75rem;">${e.session_id}</td>
                <td class="model-flow">
                    <span class="model-req">${e.requested_model}</span> ➔ <span class="model-act">${e.actual_model}</span>
                </td>
                <td><span class="badge badge-reason">${e.reason.toUpperCase()}</span></td>
                <td><span class="badge badge-risk-${e.risk_level}">${e.risk_level}</span></td>
                <td>${complianceBadge}</td>
                <td>
                    <button class="btn btn-secondary" style="padding: 0.25rem 0.6rem; font-size: 0.75rem;" onclick="openEventDetail('${e.id}')">Inspect</button>
                </td>
            </tr>
        `;
    }).join("");
}

window.openEventDetail = function(eventId) {
    const event = allEvents.find(e => e.id === eventId);
    if (!event) return;

    const modalBody = document.getElementById("modal-body");
    modalBody.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 1rem;">
            <div style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 8px;">
                <h4 style="color: var(--primary); margin-bottom: 0.4rem;">Substitution Overview</h4>
                <p><strong>Agent ID:</strong> ${event.agent_id}</p>
                <p><strong>Session ID:</strong> ${event.session_id}</p>
                <p><strong>Timestamp:</strong> ${new Date(event.timestamp).toLocaleString()}</p>
                <p><strong>Trigger Reason:</strong> ${event.reason.toUpperCase()}</p>
            </div>

            <div style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 8px;">
                <h4 style="color: var(--warning); margin-bottom: 0.4rem;">Capability Risk Assessment</h4>
                <p><strong>Risk Level:</strong> <span class="badge badge-risk-${event.risk_level}">${event.risk_level}</span></p>
                <p><strong>Context Window Drop:</strong> ${event.context_downgrade_pct}%</p>
                <p><strong>Guardrail Level Drop:</strong> ${event.guardrail_downgrade ? 'YES ⚠️' : 'NO ✓'}</p>
                <p><strong>Bias Score Delta:</strong> ${event.bias_delta > 0 ? '+' : ''}${event.bias_delta}</p>
                <p style="margin-top: 0.4rem; color: var(--text-muted);"><em>${event.risk_reason || 'N/A'}</em></p>
            </div>

            <div style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 8px;">
                <h4 style="color: ${event.compliance_flagged ? 'var(--danger)' : 'var(--success)'}; margin-bottom: 0.4rem;">Compliance Audit</h4>
                <p><strong>Status:</strong> ${event.compliance_flagged ? 'VIOLATION FLAGGED 🚨' : 'APPROVED MODEL ✓'}</p>
                <p style="color: var(--text-muted);"><em>${event.compliance_reason || 'Substituted model is compliant.'}</em></p>
            </div>
        </div>
    `;

    document.getElementById("event-modal").classList.add("active");
};

async function loadAuditSummary() {
    try {
        const res = await fetch(`${API_BASE}/compliance/audit`);
        if (res.ok) {
            const data = await res.json();
            document.getElementById("audit-total").innerText = data.total_events;
            document.getElementById("audit-unapproved").innerText = data.unapproved_substitutions;
            document.getElementById("audit-rate").innerText = `${data.compliance_violation_rate}%`;
            document.getElementById("audit-high").innerText = data.high_risk_substitutions + data.critical_risk_substitutions;

            const tagContainer = document.getElementById("audit-agents-list");
            if (data.affected_agents.length > 0) {
                tagContainer.innerHTML = data.affected_agents.map(a => `<span class="badge badge-violation">${a}</span>`).join(" ");
            } else {
                tagContainer.innerHTML = `<span class="badge badge-compliant">No Agent Policy Violations</span>`;
            }
        }
    } catch (e) {
        console.error("Audit load error:", e);
    }
}

async function loadAgentPolicies() {
    try {
        const res = await fetch(`${API_BASE}/agents`);
        if (res.ok) {
            const agents = await res.json();
            const container = document.getElementById("agents-cards-container");
            container.innerHTML = agents.map(a => `
                <div class="kpi-card" style="margin-bottom: 1rem;">
                    <h3>🤖 ${a.agent_id}</h3>
                    <p style="color: var(--text-muted); font-size: 0.85rem; margin: 0.3rem 0;">${a.agent_name}</p>
                    <div style="margin-top: 0.6rem;">
                        <strong>Approved Whitelist Models:</strong>
                        <div style="display: flex; gap: 0.4rem; flex-wrap: wrap; margin-top: 0.4rem;">
                            ${a.approved_models.map(m => `<span class="badge badge-compliant">${m}</span>`).join("")}
                        </div>
                    </div>
                </div>
            `).join("");
        }
    } catch (e) {
        console.error("Agent policies load error:", e);
    }
}

async function loadModelProfiles() {
    try {
        const res = await fetch(`${API_BASE}/models`);
        if (res.ok) {
            const models = await res.json();
            const tbody = document.getElementById("models-tbody");
            tbody.innerHTML = models.map(m => `
                <tr>
                    <td><strong>${m.model_name}</strong></td>
                    <td style="font-family: var(--font-mono);">${m.context_window.toLocaleString()} tokens</td>
                    <td><span class="badge badge-reason">${m.guardrail_level}</span></td>
                    <td style="font-family: var(--font-mono);">${m.bias_score}</td>
                    <td style="color: var(--text-muted);">${m.description || '-'}</td>
                </tr>
            `).join("");
        }
    } catch (e) {
        console.error("Models load error:", e);
    }
}

window.triggerSimScenario = async function(type) {
    const box = document.getElementById("sim-result");
    box.classList.remove("hidden");
    box.innerText = "Triggering substitution event...";

    let payload = {};
    const sess = "sess_" + Math.random().toString(36).substring(2, 8);

    if (type === 'cost') {
        payload = {
            requested_model: "gpt-4",
            actual_model: "gpt-4o-mini",
            reason: "cost",
            agent_id: "Finance-Bot",
            session_id: sess
        };
    } else if (type === 'availability') {
        payload = {
            requested_model: "claude-3-5-sonnet",
            actual_model: "gemini-1-5-flash",
            reason: "availability",
            agent_id: "Support-Agent",
            session_id: sess
        };
    } else if (type === 'policy') {
        payload = {
            requested_model: "gpt-4",
            actual_model: "llama-3-70b",
            reason: "policy",
            agent_id: "HR-Policy-Bot",
            session_id: sess
        };
    }

    try {
        const res = await fetch(`${API_BASE}/events`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            const data = await res.json();
            box.innerText = `✅ SUBSTITUTION EVENT RECORDED!\n` +
                `Event ID: ${data.id}\n` +
                `Risk Level: ${data.risk_level}\n` +
                `Compliance Flagged: ${data.compliance_flagged} (${data.compliance_reason || 'Compliant'})`;
            
            // Reload table
            loadDashboardData();
        } else {
            box.innerText = `❌ Error recording event: HTTP ${res.status}`;
        }
    } catch (e) {
        box.innerText = `❌ Error: ${e.message}`;
    }
};
