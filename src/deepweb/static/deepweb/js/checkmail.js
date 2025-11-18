"use strict";
document.addEventListener("DOMContentLoaded", () => {
  const emailInput = document.querySelector("#id_email");

  if (!emailInput) return;

  let feedback = document.createElement("div");
  feedback.id = "email-feedback";
  feedback.style.marginTop = "5px";
  emailInput.insertAdjacentElement("afterend", feedback);

  let timeout = null;

  emailInput.addEventListener("input", () => {
    clearTimeout(timeout);

    const email = emailInput.value;

    timeout = setTimeout(async () => {
      if (email.length < 3) {
        feedback.textContent = "";
        return;
      }

      try {
        const response = await fetch("/check-email/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: JSON.stringify({ email: email }),
        });

        const data = await response.json();

        if (data.exists) {
          feedback.textContent =
            "Cet email est déjà utilisé par un autre utilisateur ";
          feedback.style.color = "red";
        } else {
          feedback.textContent = "Email disponible";
          feedback.style.color = "green";
        }
      } catch (error) {
        console.error("Erreur AJAX :", error);
        feedback.textContent = "";
      }
    }, 400);
  });
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
