// Centralized Frontend Configuration Module for GitHub Release Distribution
const APP_CONFIG = {
    // Repository & Version Metadata
    REPO_URL: 'https://github.com/Rithika-Gurusamy/Model-Substitution-Governance-Event-Ps---8.2-',
    SDK_VERSION: 'v1.0.0',
    
    // GitHub Release Download CDN URLs
    SDK_DOWNLOAD_URL: 'https://github.com/Rithika-Gurusamy/Model-Substitution-Governance-Event-Ps---8.2-/releases/download/v1.0.0/governance-interceptor-v1.0.0.zip',
    SAMPLE_GW_DOWNLOAD_URL: 'https://github.com/Rithika-Gurusamy/Model-Substitution-Governance-Event-Ps---8.2-/releases/download/v1.0.0/sample-gateway-v1.0.0.zip',
    
    // Backend API & Swagger Docs URLs
    API_DOCS_URL: 'https://model-substitution-governance-event.onrender.com/docs',
    RENDER_API_BASE: 'https://model-substitution-governance-event.onrender.com/api/v1'
};

if (typeof module !== 'undefined' && module.exports) {
    module.exports = APP_CONFIG;
}
