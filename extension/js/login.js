import { apiHelper } from "./api.js";

document.getElementById("loginForm").addEventListener("submit", (e) => {
  e.preventDefault();
  // Terus ke questionnaire
  window.location.href = "questionnaire.html";
});
