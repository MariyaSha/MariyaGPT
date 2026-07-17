const registerForm = document.getElementById(
    "register-form"
);

const registerError = document.getElementById(
    "register-error"
);

const registerButton = registerForm.querySelector(
    'button[type="submit"]'
);


registerForm.addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();

        registerError.textContent = "";

        const username = document
            .getElementById("username")
            .value
            .trim();

        const email = document
            .getElementById("email")
            .value
            .trim();

        const password = document
            .getElementById("password")
            .value;

        const confirmPassword = document
            .getElementById("confirm-password")
            .value;

        if (password !== confirmPassword) {
            registerError.textContent =
                "Passwords do not match.";

            return;
        }

        registerButton.disabled = true;

        try {
            const response = await fetch(
                `${window.BACKEND_URL}/api/register`,
                {
                    method: "POST",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        username,
                        email,
                        password,
                        confirm_password: confirmPassword
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail || "Registration failed."
                );
            }

            window.location.href = "/chat";

        } catch (error) {
            registerError.textContent = error.message;

        } finally {
            registerButton.disabled = false;
        }
    }
);