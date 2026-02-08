document.addEventListener("DOMContentLoaded", async () => {
  chrome.tabs.query(
    {
      active: true,
      currentWindow: true,
    },
    (tabs) => {
      const tab = tabs[0];
      if (tab && tab.url) {
        const isAtDeriv = tab.url.includes("app.deriv.com");
        const userSession = localStorage.getItem("user_session");
        if (isAtDeriv) {
          if (userSession) location.href = "./views/main.html";
          else location.href = "./views/login.html";
        }
      }
    },
  );
});
