const BASE_URL = "http://127.0.0.1:8000";

// --- Multi-Sheet File Ingestion Handler ---
document.getElementById('uploadBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('excelFile');
    const mappingInput = document.getElementById('mappings');
    const logOutput = document.getElementById('logOutput');

    if (!fileInput.files || fileInput.files.length === 0) {
        logOutput.innerText = "❌ Please select an Excel workbook first.";
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);
    formData.append("sheet_mappings", mappingInput.value.trim());

    logOutput.innerText = "⏳ Uploading workbook and executing type cleansing updates...";

    try {
        const response = await fetch(`${BASE_URL}/api/upload-excel`, {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            let summary = `✅ ${data.message}\n\n`;
            data.details.forEach(item => {
                summary += `📁 Sheet '${item.sheet}' ➔ Table '${item.target_table}' (${item.rows} rows imported)\n`;
            });
            logOutput.innerText = summary;
        } else {
            const errData = await response.json();
            logOutput.innerText = `❌ Server Error: ${errData.detail || 'Processing failed'}`;
        }
    } catch (error) {
        logOutput.innerText = `⚠️ Connection failed: ${error.message}`;
    }
});

// --- Chat Execution Handler ---
async function sendMessage() {
    const userInput = document.getElementById('userInput');
    const chatFeed = document.getElementById('chatFeed');
    const queryText = userInput.value.trim();

    if (!queryText) return;

    // Append User Message to UI
    appendMessage(queryText, 'user');
    userInput.value = "";

    // Append Placeholder AI Response element while loading
    const aiMessageDiv = appendMessage("⚡ AI is generating SQL and analyzing...", 'assistant');

    try {
        const response = await fetch(`${BASE_URL}/api/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question: queryText })
        });

        if (response.ok) {
            const data = await response.json();
            // Clean up answer and apply the engine metric tag
            aiMessageDiv.innerHTML = `${data.answer}<span class="engine-tag">⚡ Engine: ${data.mode}</span>`;
        } else {
            const errData = await response.json();
            aiMessageDiv.innerText = `❌ Backend Error: ${errData.detail || 'Unknown error'}`;
        }
    } catch (error) {
        aiMessageDiv.innerText = `⚠️ Connection Error: ${error.message}`;
    }

    // Scroll feed to bottom
    chatFeed.scrollTop = chatFeed.scrollHeight;
}

// Helper to push text blocks cleanly onto feed
function appendMessage(text, sender) {
    const chatFeed = document.getElementById('chatFeed');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    msgDiv.innerText = text;
    chatFeed.appendChild(msgDiv);
    chatFeed.scrollTop = chatFeed.scrollHeight;
    return msgDiv;
}