const loginForm = document.getElementById("login-form");
const loginError = document.getElementById("login-error");
const loginButton = loginForm.querySelector(
    'button[type="submit"]'
);


loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    loginError.textContent = "";
    loginButton.disabled = true;

    const username = document
        .getElementById("username")
        .value
        .trim();

    const password = document
        .getElementById("password")
        .value;

    try {
        const response = await fetch(
            `${window.BACKEND_URL}/api/login`,
            {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username,
                    password
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Login failed."
            );
        }

        window.location.href = "/chat";

    } catch (error) {
        loginError.textContent = error.message;

    } finally {
        loginButton.disabled = false;
    }
});