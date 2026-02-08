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
