const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatContainer = document.getElementById('chat-container');
const submitBtn = document.getElementById('submit-btn');

// --- Feature: Auto-fill Sample Buttons ---
document.querySelectorAll('.sample-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        // Strip the icon text out
        userInput.value = e.currentTarget.innerText.trim();
        userInput.focus();
    });
});

// --- Feature: Create Chat Bubbles ---
function appendMessage(role, text, mode = null) {
    const isUser = role === 'user';
    const wrapper = document.createElement('div');
    wrapper.className = `flex ${isUser ? 'justify-end' : 'justify-start'} mb-6 opacity-0 translate-y-4`;
    wrapper.style.transition = 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)';
    
    // Avatar Column (Only for AI)
    let avatarHtml = '';
    if (!isUser) {
        avatarHtml = `
            <div class="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center mr-3 shrink-0 mt-1 shadow-sm">
                <i class="fa-solid fa-robot text-brand-400 text-sm"></i>
            </div>
        `;
    }

    // Message Bubble
    const bubble = document.createElement('div');
    if (isUser) {
        bubble.className = 'bg-brand-600 text-white font-medium rounded-2xl rounded-tr-none p-4 max-w-2xl text-sm shadow-md';
        bubble.innerText = text; // Raw text for user input
    } else {
        bubble.className = 'bg-dark-900 border border-slate-800 text-slate-200 rounded-2xl rounded-tl-none p-5 max-w-3xl text-sm shadow-md markdown-body w-full';
        
        // Use marked.js to parse the Markdown into HTML!
        // This makes tables, code blocks, and bold text look amazing.
        bubble.innerHTML = marked.parse(text); 
        
        // Add Engine Target Tag
        if (mode) {
            const metaTag = document.createElement('div');
            metaTag.className = 'text-[10px] font-mono text-brand-400/60 mt-4 pt-3 border-t border-slate-800/60 flex items-center gap-1.5';
            metaTag.innerHTML = `<i class="fa-solid fa-microchip"></i> Engine: ${mode}`;
            bubble.appendChild(metaTag);
        }
    }
    
    // Assemble and append
    if (!isUser) wrapper.innerHTML += avatarHtml;
    wrapper.appendChild(bubble);
    chatContainer.appendChild(wrapper);
    
    // Trigger entrance animation
    requestAnimationFrame(() => {
        wrapper.classList.remove('opacity-0', 'translate-y-4');
    });

    // Scroll to the newest message smoothly
    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: 'smooth'
    });
    
    return wrapper;
}

// --- Feature: Elegant Loading State ---
function showLoading() {
    return appendMessage('assistant', `
        <div class="flex items-center gap-3 text-slate-400 font-mono text-xs py-1">
            <i class="fa-solid fa-circle-notch fa-spin text-brand-400 text-base"></i>
            <span>Analyzing database schema and querying SQLite...</span>
        </div>
    `);
}

// --- Main Form Submission ---
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const question = userInput.value.trim();
    if (!question) return;

    // 1. Show User Input
    appendMessage('user', question);
    userInput.value = '';
    
    // 2. Lock UI
    submitBtn.disabled = true;
    const loadingBubble = showLoading();

    try {
        // 3. Post to local FastAPI server
        const response = await fetch('http://127.0.0.1:8000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });

        const data = await response.json();
        loadingBubble.remove(); 

        if (response.ok) {
            // Success: Render parsed markdown response
            appendMessage('assistant', data.answer, data.mode);
        } else {
            // Server error handler
            appendMessage('assistant', `**Server Error:** \`${data.detail || 'Failed to process request'}\``);
        }
        
    } catch (error) {
        loadingBubble.remove();
        appendMessage('assistant', `**Connection Error:** Could not reach the API. Is your FastAPI server running on \`port 8000\`?`);
        console.error("Fetch Error:", error);
    } finally {
        // Unlock UI
        submitBtn.disabled = false;
        userInput.focus();
    }
});