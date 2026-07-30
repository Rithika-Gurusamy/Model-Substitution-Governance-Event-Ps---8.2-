// Centralized Frontend Configuration Module for Multi-Tenant SaaS & Releases
const APP_CONFIG = {
    // Repository & Version Metadata
    REPO_URL: 'https://github.com/Rithika-Gurusamy/Model-Substitution-Governance-Event-Ps---8.2-',
    SDK_VERSION: 'v1.0.0',
    
    // GitHub Release Download CDN URLs
    SDK_DOWNLOAD_URL: 'https://github.com/Rithika-Gurusamy/Model-Substitution-Governance-Event-Ps---8.2-/releases/download/v1.0.0/governance-interceptor-v1.0.0.zip',
    SAMPLE_GW_DOWNLOAD_URL: 'https://github.com/Rithika-Gurusamy/Model-Substitution-Governance-Event-Ps---8.2-/releases/download/v1.0.0/sample-gateway-v1.0.0.zip',
    
    // Backend API & Swagger Docs URLs
    API_DOCS_URL: 'https://model-substitution-governance-event.onrender.com/docs',
    RENDER_API_BASE: 'https://model-substitution-governance-event.onrender.com/api/v1',

    // Supabase Authentication Configuration
    SUPABASE_URL: 'https://fzluhjcenawlekrqdlxb.supabase.co',
    SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ6bHVoamNlbmF3bGVrcnFkbHhiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODUzNTEwMTAsImV4cCI6MjEwMDkyNzAxMH0.TVumRBiAFlF-x4YOs8jyaAQXOg8Y616HUcK3SY9tYYo'
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = APP_CONFIG;
}
