import { apiHelper } from "./api.js";

document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(e.target);
  const email = formData.get("email");
  const password = formData.get("password");

  try {
    const result = await apiHelper.login({
      email,
      password,
    });

    chrome.runtime.sendMessage(
      {
        type: "user_session_data",
        payload: result,
      },
      () => {
        console.log("Login result:", result);
        localStorage.setItem("user_session", JSON.stringify(result));
        alert("Login successful!");
        location.href = "./main.html";
      },
    );
  } catch (error) {
    console.error("Login failed:", error);
    alert("Login failed: " + error.message);
  }
});


// import { apiHelper } from "./api.js";

// document.getElementById("loginForm").addEventListener("submit", async (e) => {
//   e.preventDefault();

//   const formData = new FormData(e.target);
//   const email = formData.get("email");
//   const password = formData.get("password");

//   try {
//     const result = await apiHelper.login({
//       email,
//       password,
//     });

//     chrome.runtime.sendMessage(
//       {
//         type: "user_session_data",
//         payload: result,
//       },
//       () => {
//         console.log("Login result:", result);
//         localStorage.setItem("user_session", JSON.stringify(result));
//         // Also store in chrome.storage.local for content script access on any domain
//         chrome.storage.local.set({ user_session: result });
//         alert("Login successful!");

//         // Route based on trader_type — pass session via URL param
//         const encoded = btoa(encodeURIComponent(JSON.stringify(result)));
//         if (!result.trader_type) {
//           chrome.tabs.create({ url: `http://localhost:8000/style-profiling?session=${encoded}` });
//         } else {
//           chrome.tabs.create({ url: `http://localhost:8000/static/trading_edu.html?session=${encoded}` });
//         }
//       },
//     );
//   } catch (error) {
//     console.error("Login failed:", error);
//     alert("Login failed: " + error.message);
//   }
// });
