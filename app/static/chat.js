const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const userIdInput = document.getElementById("userId");
const messages = document.getElementById("messages");
const sendButton = document.getElementById("sendButton");
const connectionStatus = document.getElementById("connectionStatus");
const quickActionButtons = document.querySelectorAll(".quick-action");
const pdfUploadForm = document.getElementById("pdfUploadForm");
const pdfFileInput = document.getElementById("pdfFile");
const uploadPdfButton = document.getElementById("uploadPdfButton");
const pdfStatus = document.getElementById("pdfStatus");

let requestInProgress = false;
const maxPdfSize = 10 * 1024 * 1024;


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
    pdfFileInput.disabled = isLoading;
    uploadPdfButton.disabled = isLoading;

    if (isLoading) {
        connectionStatus.textContent = "Thinking...";
        connectionStatus.className = "status loading";
    } else {
        connectionStatus.textContent = "Ready";
        connectionStatus.className = "status";
        messageInput.focus();
    }
}


async function uploadPdf(file) {
    const userId = userIdInput.value.trim();

    if (!userId) {
        addMessage(
            "assistant",
            "Please enter a demo user ID before uploading a PDF.",
            true
        );
        return;
    }

    if (file.size > maxPdfSize) {
        addMessage("assistant", "PDF files must be 10 MB or smaller.", true);
        return;
    }

    setLoading(true);
    pdfStatus.textContent = "Uploading...";

    try {
        const formData = new FormData();
        formData.append("user_id", userId);
        formData.append("pdf_file", file);

        const response = await fetch("/documents/pdf", {
            method: "POST",
            body: formData
        });
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || `The server returned status ${response.status}.`);
        }

        pdfStatus.textContent = `${data.filename} ready`;
        addMessage(
            "assistant",
            `${data.filename} is ready to search. Ask me a question about it.`
        );
    } catch (error) {
        console.error(error);
        pdfStatus.textContent = "Upload failed";
        addMessage("assistant", error.message, true);
    } finally {
        setLoading(false);
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


pdfUploadForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const file = pdfFileInput.files[0];

    if (file && !requestInProgress) {
        uploadPdf(file);
    }
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