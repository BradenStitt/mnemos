chrome.action.onClicked.addListener((tab) => {
  // Always open the sidebar since no authentication is needed
  chrome.tabs.sendMessage(tab.id, { action: "toggleSidebar" });
});

// Initial setting when extension is installed or updated
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.sync.set({ memory_enabled: true }, function() {
    console.log('Memory enabled set to true on install/update');
  });
});

// Keep the existing message listener for opening dashboard
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "openDashboard") {
    chrome.tabs.create({ url: request.url });
  }
});