// Background script to handle API requests and bypass CORS
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  // AI api request
  if (request.action === "apiRequest") {
    // Make the API request from background script (no CORS restrictions)
    fetch(request.url, {
      method: request.method || "GET",
      headers: request.headers || {},
      body: request.body ? JSON.stringify(request.body) : undefined,
    })
      .then((response) => response.json())
      .then((data) => {
        sendResponse({ success: true, data: data });
      })
      .catch((error) => {
        console.error("Background API request failed:", error);
        sendResponse({ success: false, error: error.message });
      });

    // Return true to indicate we'll send response asynchronously
    return true;
  }

  if (request.type === "user_session_data") {
    // Relay user session data to content script
    console.log(
      "Received user session data in background script:",
      request.payload,
    );
    chrome.tabs.query({ active: true, currentWindow: true }, ([tab]) => {
      if (!tab?.id) return;
      chrome.tabs.sendMessage(tab.id, request);
    });

    sendResponse();
    return true;
  }
});

console.log("PocketPT Background Script Loaded");
