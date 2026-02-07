document.addEventListener("DOMContentLoaded", async () => {
  chrome.tabs.query(
    {
      active: true,
      currentWindow: true,
    },
    (tabs) => {
      const tab = tabs[0];
      if (tab) {
        const isAtDeriv = tab.url.includes("app.deriv.com");
        if (isAtDeriv) {
          location.href = "./views/login.html";
        }
      }
    },
  );
});
