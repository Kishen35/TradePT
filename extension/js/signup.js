import { apiHelper } from "./api.js";

document.getElementById("signupForm").addEventListener("submit", async (e) => {
  // prevent page reload (default form submission behavior)
  e.preventDefault();

  // form elements extraction
  const formData = new FormData(e.target);
  const name = formData.get("name");
  const email = formData.get("email");
  const password = formData.get("password");
  const confirm_password = formData.get("confirm_password");
  const experience_level = formData.get("experience_level");
  const risk_tolerance = formData.get("risk_tolerance");
  const trading_duration = formData.get("trading_duration");
  const capital_allocation = formData.get("capital_allocation");
  const asset_preference = formData.get("asset_preference");

  if (password !== confirm_password) {
    alert("Password does not match!");
    return;
  }

  try {
    const result = await apiHelper.register({
      name,
      email,
      password,
      experience_level,
      risk_tolerance,
      trading_duration,
      capital_allocation,
      asset_preference,
    });

    // Store session and redirect to style profiling — pass session via URL param
    localStorage.setItem("user_session", JSON.stringify(result));
    chrome.storage.local.set({ user_session: result });
    alert("Signup successful! Let's choose your trading style.");
    const encoded = btoa(encodeURIComponent(JSON.stringify(result)));
    chrome.tabs.create({ url: `http://localhost:8000/style-profiling?session=${encoded}` });
  } catch (error) {
    console.error("Signup failed:", error);
    alert("Signup failed: " + error.message);
  }
});
