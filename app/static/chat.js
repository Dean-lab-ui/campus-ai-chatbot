const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const userIdInput = document.getElementById("userId");
const messages = document.getElementById("messages");
const sendButton = document.getElementById("sendButton");
const connectionStatus = document.getElementById("connectionStatus");
const quickActionButtons = document.querySelectorAll(".quick-action");

let requestInProgress = false;


function addFormattedText(element, text) {
    const sections = text.split(/(\*\*.*?\*\*)/g);

    for (const section of sections) {
        if (section.startsWith("**") && section.endsWith("**")) {
            const strong = document.createElement("strong");
            strong.textContent = section.slice(2, -2);
            element.appendChild(strong);
        } else {
            element.appendChild(document.createTextNode(section));
        }
    }
}


function addMessage(role, text, isError = false) {
    const message = document.createElement("div");
    const label = document.createElement("div");
    const bubble = document.createElement("div");

    message.classList.add("message");

    if (role === "user") {
        message.classList.add("user-message");
        label.textContent = "You";
    } else {
        message.classList.add("assistant-message");
        label.textContent = "Campus Assistant";
    }

    if (isError) {
        message.classList.add("error-message");
    }

    label.classList.add("message-label");
    bubble.classList.add("message-bubble");

    addFormattedText(bubble, text);

    message.appendChild(label);
    message.appendChild(bubble);
    messages.appendChild(message);

    messages.scrollTop = messages.scrollHeight;
}


function setLoading(isLoading) {
    requestInProgress = isLoading;

    sendButton.disabled = isLoading;
    messageInput.disabled = isLoading;
    userIdInput.disabled = isLoading;

    quickActionButtons.forEach((button) => {
        button.disabled = isLoading;
    });

    if (isLoading) {
        connectionStatus.textContent = "Thinking...";
        connectionStatus.className = "status loading";
    } else {
        connectionStatus.textContent = "Ready";
        connectionStatus.className = "status";
        messageInput.focus();
    }
}


function resizeMessageInput() {
    messageInput.style.height = "auto";
    messageInput.style.height =
        `${Math.min(messageInput.scrollHeight, 130)}px`;
}


async function sendMessage(messageText) {
    const message = messageText.trim();
    const userId = userIdInput.value.trim();

    if (!message || requestInProgress) {
        return;
    }

    if (!userId) {
        addMessage(
            "assistant",
            "Please enter a demo user ID before sending a message.",
            true
        );

        return;
    }

    addMessage("user", message);

    messageInput.value = "";
    resizeMessageInput();
    setLoading(true);

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_id: userId,
                message: message
            })
        });

        if (!response.ok) {
            throw new Error(`The server returned status ${response.status}.`);
        }

        const data = await response.json();

        addMessage(
            "assistant",
            data.response || "The assistant returned an empty response."
        );
    } catch (error) {
        console.error(error);

        connectionStatus.textContent = "Error";
        connectionStatus.className = "status error";

        addMessage(
            "assistant",
            "I could not reach the chatbot. Check that the FastAPI server is running and try again.",
            true
        );
    } finally {
        setLoading(false);
    }
}


chatForm.addEventListener("submit", (event) => {
    event.preventDefault();
    sendMessage(messageInput.value);
});


messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        chatForm.requestSubmit();
    }
});


messageInput.addEventListener("input", resizeMessageInput);


quickActionButtons.forEach((button) => {
    button.addEventListener("click", () => {
        sendMessage(button.dataset.message);
    });
});


messageInput.focus();