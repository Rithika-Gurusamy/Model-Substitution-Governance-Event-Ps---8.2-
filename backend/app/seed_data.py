import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from backend.app.models.models import UserProfile, ModelProfile, Agent, ApprovedModel, GovernanceEvent, ApiKey
from backend.app.auth import DEFAULT_DEMO_USER_PROFILE_ID, generate_api_key_for_user

SEED_MODELS = [
    # OpenAI Series
    {"model_name": "GPT-5", "context_window": 1000000},
    {"model_name": "GPT-5 Mini", "context_window": 1000000},
    {"model_name": "GPT-5 Nano", "context_window": 1000000},
    {"model_name": "GPT-4.1", "context_window": 1000000},
    {"model_name": "GPT-4o", "context_window": 128000},
    {"model_name": "GPT-4o Mini", "context_window": 128000},
    {"model_name": "GPT-4 Turbo", "context_window": 128000},
    {"model_name": "GPT-4", "context_window": 128000},
    {"model_name": "GPT-3.5 Turbo", "context_window": 16000},

    # Anthropic Claude Series
    {"model_name": "Claude Opus 4", "context_window": 200000},
    {"model_name": "Claude Sonnet 4", "context_window": 200000},
    {"model_name": "Claude Haiku 4", "context_window": 200000},
    {"model_name": "Claude Opus 3", "context_window": 200000},
    {"model_name": "Claude Sonnet 3.7", "context_window": 200000},
    {"model_name": "Claude Haiku 3.5", "context_window": 200000},

    # Google Gemini Series
    {"model_name": "Gemini 2.5 Pro", "context_window": 1048576},
    {"model_name": "Gemini 2.5 Flash", "context_window": 1048576},
    {"model_name": "Gemini 2.5 Flash Lite", "context_window": 1048576},
    {"model_name": "Gemini 1.5 Pro", "context_window": 2000000},
    {"model_name": "Gemini 1.5 Flash", "context_window": 1000000},

    # Meta Llama Series
    {"model_name": "Llama 4 Scout", "context_window": 10000000},
    {"model_name": "Llama 4 Maverick", "context_window": 1000000},
    {"model_name": "Llama 3.3 70B", "context_window": 128000},
    {"model_name": "Llama 3.1 405B", "context_window": 128000},
    {"model_name": "Llama 3.1 70B", "context_window": 128000},
    {"model_name": "Llama 3.1 8B", "context_window": 128000},

    # DeepSeek Series
    {"model_name": "DeepSeek V3", "context_window": 128000},
    {"model_name": "DeepSeek R1", "context_window": 128000},
    {"model_name": "DeepSeek Chat", "context_window": 128000},

    # Alibaba Qwen Series
    {"model_name": "Qwen 3 235B", "context_window": 262144},
    {"model_name": "Qwen 2.5 Max", "context_window": 131072},
    {"model_name": "Qwen 2.5 72B", "context_window": 131072},
    {"model_name": "Qwen 2.5 32B", "context_window": 131072},

    # Mistral AI Series
    {"model_name": "Mistral Large", "context_window": 128000},
    {"model_name": "Mistral Medium", "context_window": 128000},
    {"model_name": "Mistral Small", "context_window": 128000},
    {"model_name": "Mixtral 8x22B", "context_window": 65536},
    {"model_name": "Mixtral 8x7B", "context_window": 32768},

    # Cohere Series
    {"model_name": "Cohere Command A", "context_window": 256000},
    {"model_name": "Cohere Command R+", "context_window": 128000},
    {"model_name": "Cohere Command R", "context_window": 128000},
    {"model_name": "Command R7B", "context_window": 128000},

    # xAI Grok Series
    {"model_name": "Grok 4", "context_window": 2000000},
    {"model_name": "Grok 3", "context_window": 128000},

    # Microsoft Phi Series
    {"model_name": "Phi-4", "context_window": 16000},
    {"model_name": "Phi-3 Medium", "context_window": 128000},

    # Google Gemma Series
    {"model_name": "Gemma 3 27B", "context_window": 128000},
    {"model_name": "Gemma 3 12B", "context_window": 128000},
    {"model_name": "Gemma 2 27B", "context_window": 8192},

    # 01.AI Yi Series
    {"model_name": "Yi Large", "context_window": 200000},
]

SEED_AGENTS = [
    {
        "agent_id": "HR-Agent",
        "agent_name": "Human Resources Resume Screening Agent",
        "description": "Processes candidate resumes and PII data; restricted to enterprise tier models.",
        "approved_models": ["GPT-4", "GPT-4o", "GPT-5", "Claude Sonnet 3.7", "Claude Opus 3"]
    },
    {
        "agent_id": "Finance-Bot",
        "agent_name": "Financial Compliance & Risk Assessor",
        "description": "Performs financial regulatory analysis; requires strict high-context governance models.",
        "approved_models": ["GPT-4", "GPT-4.1", "Claude Opus 4", "Gemini 1.5 Pro", "Gemini 2.5 Pro"]
    },
    {
        "agent_id": "Support-Router",
        "agent_name": "Customer Care Support Router",
        "description": "Handles general customer care inquiries.",
        "approved_models": ["GPT-4o Mini", "GPT-3.5 Turbo", "Claude Haiku 3.5", "Gemini 1.5 Flash", "Llama 3.1 8B"]
    }
]

def seed_database(db: Session):
    # Seed Default Demo UserProfile
    demo_user = db.query(UserProfile).filter(UserProfile.id == DEFAULT_DEMO_USER_PROFILE_ID).first()
    if not demo_user:
        demo_user = UserProfile(
            id=DEFAULT_DEMO_USER_PROFILE_ID,
            auth_user_id="demo_visitor",
            full_name="Demo Visitor",
            role="Demo Visitor"
        )
        db.add(demo_user)
        db.commit()
        # Seed API key for Demo User
        generate_api_key_for_user(DEFAULT_DEMO_USER_PROFILE_ID, db)

    # Seed Models (Global)
    for model_data in SEED_MODELS:
        existing = db.query(ModelProfile).filter(ModelProfile.model_name == model_data["model_name"]).first()
        if not existing:
            db.add(ModelProfile(
                model_name=model_data["model_name"],
                context_window=model_data["context_window"]
            ))
    db.commit()

    # Seed Agents & Approved Models for Default Demo User
    for agent_data in SEED_AGENTS:
        try:
            existing_agent = db.query(Agent).filter(
                Agent.agent_id == agent_data["agent_id"],
                Agent.user_profile_id == DEFAULT_DEMO_USER_PROFILE_ID
            ).first()
            if not existing_agent:
                agent_obj = Agent(
                    agent_id=agent_data["agent_id"],
                    agent_name=agent_data["agent_name"],
                    description=agent_data["description"],
                    user_profile_id=DEFAULT_DEMO_USER_PROFILE_ID
                )
                db.add(agent_obj)
                db.commit()
                db.refresh(agent_obj)

                for m_name in agent_data["approved_models"]:
                    db.add(ApprovedModel(agent_db_id=agent_obj.id, model_name=m_name))
                db.commit()
        except Exception as e:
            db.rollback()
            print(f"Notice: Agent seed skipped for {agent_data['agent_id']}: {e}")

    # Pre-seed initial demonstration events attached to Default Demo User
    existing_events_count = db.query(GovernanceEvent).filter(GovernanceEvent.user_profile_id == DEFAULT_DEMO_USER_PROFILE_ID).count()
    if existing_events_count == 0:
        now = datetime.now(timezone.utc)
        sample_events = [
            {
                "requested_model": "GPT-5",
                "actual_model": "GPT-4o Mini",
                "reason": "cost",
                "agent_id": "HR-Agent",
                "session_id": "sess-hr-8812",
                "risk_level": "Critical",
                "risk_reason": "CRITICAL RISK: Severe material capability downgrade (87.2% drop in context capacity: 1,000,000 → 128,000 tokens). Risk of prompt truncation or severe context loss.",
                "context_downgrade_pct": 87.2,
                "compliance_flagged": True,
                "compliance_reason": "COMPLIANCE VIOLATION: Substituted model 'GPT-4o Mini' is not in approved list for agent 'HR-Agent' (GPT-4, GPT-4o, GPT-5, Claude Sonnet 3.7, Claude Opus 3).",
                "timestamp": now - timedelta(minutes=45)
            },
            {
                "requested_model": "Claude Opus 4",
                "actual_model": "Gemini 1.5 Flash",
                "reason": "availability",
                "agent_id": "Finance-Bot",
                "session_id": "sess-fin-9941",
                "risk_level": "Low",
                "risk_reason": "LOW RISK: Context window capacity maintained or increased (200,000 → 1,000,000 tokens).",
                "context_downgrade_pct": 0.0,
                "compliance_flagged": True,
                "compliance_reason": "COMPLIANCE VIOLATION: Substituted model 'Gemini 1.5 Flash' is not in approved list for agent 'Finance-Bot' (GPT-4, GPT-4.1, Claude Opus 4, Gemini 1.5 Pro, Gemini 2.5 Pro).",
                "timestamp": now - timedelta(minutes=30)
            },
            {
                "requested_model": "GPT-4",
                "actual_model": "Llama 3.1 8B",
                "reason": "policy",
                "agent_id": "Support-Router",
                "session_id": "sess-sup-1042",
                "risk_level": "Low",
                "risk_reason": "LOW RISK: Context window capacity maintained or increased (128,000 → 128,000 tokens).",
                "context_downgrade_pct": 0.0,
                "compliance_flagged": False,
                "compliance_reason": None,
                "timestamp": now - timedelta(minutes=15)
            },
            {
                "requested_model": "Claude Opus 4",
                "actual_model": "Gemini 1.5 Pro",
                "reason": "availability",
                "agent_id": "Finance-Bot",
                "session_id": "sess-fin-9950",
                "risk_level": "Low",
                "risk_reason": "LOW RISK: Context window capacity maintained or increased (200,000 → 2,000,000 tokens).",
                "context_downgrade_pct": 0.0,
                "compliance_flagged": False,
                "compliance_reason": None,
                "timestamp": now - timedelta(minutes=5)
            }
        ]
        for se in sample_events:
            event_obj = GovernanceEvent(
                id=str(uuid.uuid4()),
                requested_model=se["requested_model"],
                actual_model=se["actual_model"],
                reason=se["reason"],
                agent_id=se["agent_id"],
                session_id=se["session_id"],
                risk_level=se["risk_level"],
                risk_reason=se["risk_reason"],
                context_downgrade_pct=se["context_downgrade_pct"],
                compliance_flagged=se["compliance_flagged"],
                compliance_reason=se["compliance_reason"],
                user_profile_id=DEFAULT_DEMO_USER_PROFILE_ID,
                timestamp=se["timestamp"]
            )
            db.add(event_obj)
        db.commit()
