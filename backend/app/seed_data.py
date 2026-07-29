from sqlalchemy.orm import Session
from backend.app.models.models import ModelProfile, Agent, ApprovedModel

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
    # Seed Models
    for model_data in SEED_MODELS:
        existing = db.query(ModelProfile).filter(ModelProfile.model_name == model_data["model_name"]).first()
        if not existing:
            db.add(ModelProfile(
                model_name=model_data["model_name"],
                context_window=model_data["context_window"]
            ))
    db.commit()

    # Seed Agents & Approved Models
    for agent_data in SEED_AGENTS:
        existing_agent = db.query(Agent).filter(Agent.agent_id == agent_data["agent_id"]).first()
        if not existing_agent:
            agent_obj = Agent(
                agent_id=agent_data["agent_id"],
                agent_name=agent_data["agent_name"],
                description=agent_data["description"]
            )
            db.add(agent_obj)
            db.commit()
            db.refresh(agent_obj)

            for m_name in agent_data["approved_models"]:
                db.add(ApprovedModel(agent_db_id=agent_obj.id, model_name=m_name))
            db.commit()
