// DOM Elements
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatContainer = document.getElementById('chat-container');
const submitBtn = document.getElementById('submit-btn');

// --- Helper: Auto-fill Sample Questions ---
document.querySelectorAll('.sample-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        userInput.value = e.target.innerText;
        userInput.focus();
    });
});

// --- Helper: Add Message to UI ---
function appendMessage(role, text, mode = null) {
    const isUser = role === 'user';
    const wrapper = document.createElement('div');
    wrapper.className = `flex ${isUser ? 'justify-end' : 'justify-start'} opacity-0 translate-y-4 animate-fade-in`;
    
    // Smooth animation styles
    wrapper.style.transition = 'all 0.3s ease-out';
    
    const bubble = document.createElement('div');
    
    // Different styling for User vs Assistant
    if (isUser) {
        bubble.className = 'bg-emerald-600 text-white font-medium rounded-2xl rounded-tr-none p-4 max-w-2xl text-sm shadow-md';
        bubble.innerText = text;
    } else {
        bubble.className = 'bg-gray-900 border border-gray-800 text-gray-200 rounded-2xl rounded-tl-none p-5 max-w-2xl text-sm shadow-md whitespace-pre-wrap leading-relaxed';
        bubble.innerHTML = text; // Using innerHTML in case we want to render tables later
        
        // Add Engine Mode tag if provided by backend
        if (mode) {
            const metaTag = document.createElement('div');
            metaTag.className = 'text-[10px] font-mono text-amber-500 mt-3 pt-3 border-t border-gray-800/60 uppercase tracking-wider';
            metaTag.innerText = `Engine: ${mode}`;
            bubble.appendChild(metaTag);
        }
    }
    
    wrapper.appendChild(bubble);
    chatContainer.appendChild(wrapper);
    
    // Trigger animation frame
    requestAnimationFrame(() => {
        wrapper.classList.remove('opacity-0', 'translate-y-4');
    });

    // Auto-scroll to bottom
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    
    return wrapper;
}

// --- Helper: Loading Indicator ---
function showLoading() {
    return appendMessage('assistant', `
        <div class="flex items-center gap-3 text-gray-400 font-mono text-xs">
            <svg class="animate-spin h-4 w-4 text-emerald-400" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Querying Database...
        </div>
    `);
}

// --- Main Chat Submission Logic ---
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const question = userInput.value.trim();
    if (!question) return;

    // 1. Display User Message
    appendMessage('user', question);
    userInput.value = '';
    
    // 2. Disable input & show loading state
    submitBtn.disabled = true;
    submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
    const loadingBubble = showLoading();

    try {
        // 3. Send to FastAPI Backend
        // Notice we are sending { "question": ... } to match our Pydantic Schema!
        const response = await fetch('http://127.0.0.1:8000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });

        const data = await response.json();
        
        // Remove loading spinner
        loadingBubble.remove(); 

        if (response.ok) {
            // 4. Display AI Response
            appendMessage('assistant', data.answer, data.mode);
        } else {
            // Display Server Error
            appendMessage('assistant', `❌ Server Error: ${data.detail || 'Failed to process request'}`);
        }
        
    } catch (error) {
        loadingBubble.remove();
        appendMessage('assistant', `🔌 Connection failed. Is your FastAPI server running on port 8000?`);
        console.error("Fetch Error:", error);
    } finally {
        // Re-enable input
        submitBtn.disabled = false;
        submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        userInput.focus();
    }
});
