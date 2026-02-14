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
          if (userSession) {
            // Check if user has chosen a trader type
            try {
              const session = JSON.parse(userSession);
              if (!session.trader_type) {
                // No trader type yet — open style profiling in new tab with session
                const encoded = btoa(encodeURIComponent(userSession));
                chrome.tabs.create({ url: `http://localhost:8000/style-profiling?session=${encoded}` });
              } else {
                // Has trader type — go to main extension view
                location.href = "./views/main.html";
              }
            } catch {
              location.href = "./views/main.html";
            }
          } else {
            location.href = "./views/login.html";
          }
        }
      }
    },
  );
});
