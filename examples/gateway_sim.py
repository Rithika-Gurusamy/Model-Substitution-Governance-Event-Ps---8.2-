import time
import uuid
import sys
import os

# Allow importing local interceptor module directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from interceptor import GovernanceInterceptor

def run_gateway_simulation(tracker_url="http://localhost:8000"):
    print("=" * 70)
    print("🚀 STARTING LLM GATEWAY MODEL SUBSTITUTION SIMULATOR")
    print("=" * 70)
    
    interceptor = GovernanceInterceptor(tracker_url=tracker_url, fail_silently=True)
    
    scenarios = [
        {
            "name": "Scenario 1: Cost-Based Model Downgrade",
            "agent_id": "Finance-Bot",
            "requested_model": "gpt-4",
            "actual_model": "gpt-4o-mini",
            "reason": "cost",
            "session_id": f"sess_{uuid.uuid4().hex[:8]}",
            "desc": "Gateway routed request to cheaper model because high token usage exceeded cost budget."
        },
        {
            "name": "Scenario 2: Availability / Outage Fallback",
            "agent_id": "Support-Agent",
            "requested_model": "claude-3-5-sonnet",
            "actual_model": "gemini-1-5-flash",
            "reason": "availability",
            "session_id": f"sess_{uuid.uuid4().hex[:8]}",
            "desc": "Primary provider returned HTTP 503 Outage. Gateway automatically switched to secondary provider."
        },
        {
            "name": "Scenario 3: Policy-Based Routing to Unapproved Model",
            "agent_id": "HR-Policy-Bot",
            "requested_model": "gpt-4",
            "actual_model": "llama-3-70b",
            "reason": "policy",
            "session_id": f"sess_{uuid.uuid4().hex[:8]}",
            "desc": "Data residency policy restricted cloud LLM usage. Gateway rerouted to local Llama model (Unapproved model)."
        },
        {
            "name": "Scenario 4: Direct Match (No Substitution)",
            "agent_id": "Code-Assistant",
            "requested_model": "gpt-4o",
            "actual_model": "gpt-4o",
            "reason": "normal",
            "session_id": f"sess_{uuid.uuid4().hex[:8]}",
            "desc": "Gateway served request using exact model requested."
        }
    ]

    for i, s in enumerate(scenarios, 1):
        print(f"\n----------------------------------------------------------------------")
        print(f"📌 [{i}/4] {s['name']}")
        print(f"   Description: {s['desc']}")
        print(f"   Agent ID   : {s['agent_id']}")
        print(f"   Requested  : {s['requested_model']}")
        print(f"   Actual Used: {s['actual_model']}")
        print(f"   Reason     : {s['reason']}")
        
        result = interceptor.intercept_substitution(
            requested_model=s["requested_model"],
            actual_model=s["actual_model"],
            reason=s["reason"],
            agent_id=s["agent_id"],
            session_id=s["session_id"]
        )

        if result.get("substituted"):
            if result.get("recorded"):
                evt = result.get("event", {})
                print(f"   ✅ GOVERNANCE EVENT RECORDED!")
                print(f"      Event ID         : {evt.get('id')}")
                print(f"      Risk Level       : {evt.get('risk_level')}")
                print(f"      Risk Reason      : {evt.get('risk_reason')}")
                print(f"      Compliance Flag : {evt.get('compliance_flagged')} ({evt.get('compliance_reason')})")
            else:
                print(f"   ⚠️  SUBSTITUTION DETECTED BUT TRACKER UNREACHABLE (Logged locally)")
                print(f"      Error: {result.get('error')}")
        else:
            print(f"   ℹ️  NO SUBSTITUTION DETECTED (Requested model matches actual model)")

        time.sleep(0.5)

    print("\n" + "=" * 70)
    print("✅ SIMULATION COMPLETE. Check Governance Dashboard for results!")
    print("=" * 70)

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    run_gateway_simulation(url)
