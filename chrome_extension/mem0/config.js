// Configuration for the Memory Service Extension
const CONFIG = {
  // Base URL for your memory service
  SERVICE_BASE_URL: 'http://localhost:8000',
  
  // API endpoints
  ENDPOINTS: {
    SEARCH: '/api/cascading-retrieval',
    STORE: '/api/store-memory',
    DOCS: '/api/docs'
  },
  
  // UI Configuration
  UI: {
    BUTTON_COLOR: '#34a853',
    BUTTON_HOVER_COLOR: '#2d8f47',
    MODAL_BACKGROUND: '#2d2e30',
    TEXT_COLOR: '#e8eaed'
  },
  
  // Feature flags
  FEATURES: {
    AUTO_STORE_MESSAGES: true,
    SHOW_NOTIFICATION_DOT: true,
    ENABLE_KEYBOARD_SHORTCUT: true
  }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CONFIG;
} else {
  window.MEMORY_SERVICE_CONFIG = CONFIG;
} 