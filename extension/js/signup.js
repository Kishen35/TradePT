document.getElementById("signupForm").addEventListener("submit", (e) => {
  e.preventDefault();
  if (
    document.getElementById("p1").value !== document.getElementById("p2").value
  ) {
    alert("Password tak sama!");
    return;
  }
  window.location.href = "questionnaire.html";
});
