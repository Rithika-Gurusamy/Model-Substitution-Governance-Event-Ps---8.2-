import os
import sys
import time
import uuid

# Add interceptor directory to sys.path if governance_interceptor is not installed globally
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "interceptor")))

from governance_interceptor import GovernanceInterceptor

def main():
    print("=" * 70)
    print("⚡ LLM Gateway Substitution Simulator (Governance Interceptor Integration)")
    print("=" * 70)
    print("Connecting to Governance Tracker at: http://localhost:8000/api/v1/events\n")

    interceptor = GovernanceInterceptor(tracker_url="http://localhost:8000")

    # Substitution Scenarios
    scenarios = [
        {
            "name": "Scenario 1: Cost-Based Substitution (High Risk + Compliance Violation)",
            "agent_id": "HR-Agent",
            "requested_model": "GPT-5",
            "actual_model": "GPT-4o Mini",
            "reason": "cost"
        },
        {
            "name": "Scenario 2: Availability/Outage Fallback (High Risk)",
            "agent_id": "Finance-Bot",
            "requested_model": "Claude Opus 4",
            "actual_model": "Gemini 1.5 Flash",
            "reason": "availability"
        },
        {
            "name": "Scenario 3: Governance Policy Enforced Substitution (Low Risk)",
            "agent_id": "Support-Router",
            "requested_model": "GPT-4",
            "actual_model": "Llama 3.1 8B",
            "reason": "policy"
        },
        {
            "name": "Scenario 4: Approved Substitution (Low Risk + Compliant)",
            "agent_id": "Finance-Bot",
            "requested_model": "Claude Opus 4",
            "actual_model": "Gemini 1.5 Pro",
            "reason": "availability"
        }
    ]

    for idx, sc in enumerate(scenarios, 1):
        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        print(f"[{idx}] Triggering {sc['name']}...")
        print(f"    Agent ID: {sc['agent_id']} | Session: {session_id}")
        print(f"    Routing Decision: Requested '{sc['requested_model']}' → Substituted to '{sc['actual_model']}' (Reason: {sc['reason']})")

        was_substituted, event = interceptor.intercept(
            requested_model=sc["requested_model"],
            actual_model=sc["actual_model"],
            reason=sc["reason"],
            agent_id=sc["agent_id"],
            session_id=session_id
        )

        if event:
            print(f"    🛡️ Recorded Event ID: {event['id']}")
            print(f"    ⚠️ Capability Risk Level: {event['risk_level']}")
            print(f"    📝 Risk Reason: {event['risk_reason']}")
            print(f"    🚨 Compliance Flagged: {event['compliance_flagged']}")
            if event['compliance_flagged']:
                print(f"    ⛔ Violation Reason: {event['compliance_reason']}")
        print("-" * 70)
        time.sleep(1)

    print("\n✅ Simulation complete! Check http://localhost:8000 to view events live on the Enterprise Dashboard.")

if __name__ == "__main__":
    main()
