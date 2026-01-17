
// Helper to get ID from URL
const urlParams = new URLSearchParams(window.location.search);
const candidateId = urlParams.get('id');

document.addEventListener('DOMContentLoaded', async () => {
    // Only require ID on the view page
    if (window.location.pathname.includes('candidate-view.html')) {
        if (!candidateId) {
            alert('No candidate ID provided');
            window.location.href = 'candidates.html';
            return;
        }
        await loadCandidateDetails();
        await loadChatHistory();
    } else {
        // We are on candidates.html (Add Candidate page)
        await loadVacancies();
    }
});

async function loadVacancies() {
    try {
        const vacancies = await Api.get('/vacancies/');
        const select = document.getElementById('vacancy_id');
        if (!select) return;

        select.innerHTML = vacancies.map(v => `<option value="${v.id}">${v.title}</option>`).join('');
    } catch (e) {
        console.error("Failed to load vacancies", e);
    }
}


async function loadCandidateDetails() {
    try {
        const candidate = await Api.get(`/candidates/${candidateId}`);

        // Update basic info
        const nameEl = document.getElementById('candidate-name');
        if (nameEl) nameEl.textContent = candidate.filename.replace(/\.[^/.]+$/, "").replace(/_/g, " ");

        const summaryEl = document.getElementById('summary-text');
        if (summaryEl) summaryEl.textContent = candidate.summary || "No summary available. Run AI analysis to generate one.";

        const recEl = document.getElementById('recommendation-text');
        if (recEl) recEl.textContent = candidate.recommendation || "Pending review.";

        const scoreEl = document.getElementById('score-circle');
        if (scoreEl) scoreEl.textContent = candidate.score ? (candidate.score * 100).toFixed(0) + "%" : "-%";

        // Populate skills match
        const skillsContainer = document.getElementById('skills-list');
        if (skillsContainer && candidate.skills_match) {
            skillsContainer.innerHTML = candidate.skills_match.map(skill =>
                `<span class="tag tag-success" style="margin-right:0.5rem; margin-bottom:0.5rem; display:inline-block;">${skill}</span>`
            ).join('');
            if (candidate.missing_skills && candidate.missing_skills.length > 0) {
                skillsContainer.innerHTML += candidate.missing_skills.map(skill =>
                    `<span class="tag tag-rejected" style="margin-right:0.5rem; margin-bottom:0.5rem; display:inline-block;">${skill}</span>`
                ).join('');
            }
        }

        // Add Analyze button to header actions if it exists
        const container = document.getElementById('candidate-view-container');
        if (!document.getElementById('analyzeBtn')) {
            const btn = document.createElement('button');
            btn.id = 'analyzeBtn';
            btn.className = 'btn btn-primary';
            btn.style.marginTop = '1rem';
            btn.innerHTML = '<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="16" height="16" style="margin-right:0.5rem; vertical-align:middle;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg> AI Analyze';
            btn.onclick = runAnalysis;

            // Insert before the chat section or in a dedicated actions area
            const chatSection = document.querySelector('.card');
            if (chatSection) {
                chatSection.parentNode.insertBefore(btn, chatSection);
            } else {
                container.appendChild(btn);
            }
        }
    } catch (e) {
        console.error("Error loading candidate details:", e);
        const nameEl = document.getElementById('candidate-name');
        if (nameEl) nameEl.textContent = "Ошибка загрузки кандидата";
    }
}

async function runAnalysis() {
    const btn = document.getElementById('analyzeBtn');
    if (btn) { btn.disabled = true; btn.textContent = 'Analyzing...'; }

    try {
        const result = await Api.post(`/candidates/${candidateId}/analyze`);
        if (window.UI) UI.notify('Анализ завершен!', 'success');
        location.reload();
    } catch (e) {
        if (window.UI) UI.notify('Ошибка анализа: ' + e.message, 'error');
        console.error(e);
        if (btn) { btn.disabled = false; btn.textContent = 'AI Analyze'; }
    }
}

// Chat Logic
async function loadChatHistory() {
    try {
        const messages = await Api.get(`/chat/${candidateId}`);
        const chatContainer = document.getElementById('chat-messages');
        if (!messages.length) {
            // Trigger first AI message (Interview start)
            await Api.post('/chat/', {
                candidate_id: candidateId,
                role: 'assistant',
                content: 'AI_START'
            });
            // Reload after start
            await loadChatHistory();
            return;
        }

        chatContainer.innerHTML = ''; // Clear default
        messages.forEach(msg => {
            appendMessage(msg.role, msg.content);
        });
        chatContainer.scrollTop = chatContainer.scrollHeight;
    } catch (e) {
        console.error("Chat error", e);
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const content = input.value.trim();
    if (!content) return;

    // Optimistic UI
    appendMessage('user', content);
    input.value = '';

    try {
        await Api.post('/chat/', {
            candidate_id: candidateId,
            role: 'user',
            content: content
        });

        // Show typing indicator
        const chatContainer = document.getElementById('chat-messages');
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.style.padding = '0.5rem';
        typingDiv.style.fontStyle = 'italic';
        typingDiv.style.color = '#94A3B8';
        typingDiv.textContent = 'AI печатает...';
        chatContainer.appendChild(typingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        // Wait a moment and fetch new messages (AI should have responded)
        setTimeout(async () => {
            const messages = await Api.get(`/chat/${candidateId}`);
            const typingIndicator = document.getElementById('typing-indicator');
            if (typingIndicator) typingIndicator.remove();

            // Find and append only the new AI message
            const lastMessage = messages[messages.length - 1];
            if (lastMessage && lastMessage.role === 'assistant') {
                // Check if it's not already displayed
                const existingMessages = chatContainer.querySelectorAll('div[data-role="assistant"]');
                const alreadyDisplayed = Array.from(existingMessages).some(
                    el => el.textContent.includes(lastMessage.content.substring(0, 50))
                );

                if (!alreadyDisplayed) {
                    appendMessage('assistant', lastMessage.content);
                }
            }
        }, 2000); // 2 second delay for AI to respond

    } catch (e) {
        alert('Failed to send message');
        console.error(e);
    }
}

function appendMessage(role, content) {
    const container = document.getElementById('chat-messages');
    if (container) {
        container.classList.add('chat-grid');
        container.style.height = 'auto';
        container.style.maxHeight = '600px';
        container.style.background = '#F1F5F9';
    }

    const card = document.createElement('div');
    card.className = `chat-card ${role}`;
    card.setAttribute('data-role', role);

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    card.innerHTML = `
        <div class="chat-card-header">
            <span>${role === 'user' ? '👤 Кандидат' : '🤖 HR AI'}</span>
        </div>
        <div class="chat-card-body">${content.replace(/\n/g, '<br>')}</div>
        <div class="chat-card-time">${time}</div>
    `;
    container.appendChild(card);
    container.scrollTop = container.scrollHeight;
}

// Outreach Logic
async function generateOutreach() {
    const btn = document.getElementById('btn-gen-outreach');
    const resultDiv = document.getElementById('outreach-result');
    const textarea = document.getElementById('outreach-message');

    if (btn) { btn.disabled = true; btn.textContent = 'Generating...'; }

    try {
        const data = await Api.post(`/candidates/${candidateId}/generate_outreach`);
        textarea.value = data.message;
        resultDiv.style.display = 'block';
        if (btn) { btn.textContent = '🔄 Regenerate'; btn.disabled = false; }
    } catch (e) {
        console.error("Outreach generation error", e);
        alert("Failed to generate message");
        if (btn) { btn.disabled = false; btn.textContent = '✍️ Написать письмо'; }
    }
}

async function sendOutreach() {
    const btn = document.getElementById('btn-send-outreach');
    const textarea = document.getElementById('outreach-message');
    const message = textarea.value.trim();

    if (!message) return;

    if (btn) { btn.disabled = true; btn.textContent = 'Sending...'; }

    try {
        const result = await Api.post(`/candidates/${candidateId}/send_outreach`, { message });

        if (result.error) {
            alert("Ошибка отправки сообщения: " + result.error);
        } else {
            alert(result.mock ? "Message simulated (Mock Mode)!" : "Message sent successfully!");
            document.getElementById('outreach-result').style.display = 'none';
        }
    } catch (e) {
        console.error("Outreach send error", e);
        alert("Failed to send message");
    } finally {
        if (btn) { btn.disabled = false; btn.textContent = '🚀 Отправить'; }
    }
}

// Upload Handling
const uploadForm = document.getElementById('uploadCandidateForm');
if (uploadForm) {
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const vacancyId = document.getElementById('vacancy_id').value;
        const fileInput = document.getElementById('resume_file');
        const spinner = document.getElementById('loading-spinner');

        if (!fileInput.files.length) {
            alert('Please select a file');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        try {
            if (spinner) spinner.style.display = 'block';
            const candidate = await Api.upload(`/candidates/upload?vacancy_id=${vacancyId}`, formData);
            alert('Candidate uploaded successfully!');
            window.location.href = `candidate-view.html?id=${candidate.id}`;
        } catch (err) {
            alert('Upload failed: ' + err.message);
        } finally {
            if (spinner) spinner.style.display = 'none';
        }
    });
}


async function sendHRChatMessage() {
    const input = document.getElementById('hrChatInput');
    const content = input.value.trim();
    if (!content) return;

    // Optimistic UI
    appendHRMessage('user', content);
    input.value = '';

    const container = document.getElementById('hr-chat-messages');

    // Typing indicator
    const typingDiv = document.createElement('div');
    typingDiv.id = 'hr-typing';
    typingDiv.style.padding = '0.5rem';
    typingDiv.style.fontStyle = 'italic';
    typingDiv.style.color = '#94A3B8';
    typingDiv.textContent = 'AI анализирует...';
    container.appendChild(typingDiv);
    container.scrollTop = container.scrollHeight;

    try {
        const responseText = await Api.post('/chat/hr_ask', {
            candidate_id: candidateId,
            question: content
        });

        // Remove typing indicator
        if (document.getElementById('hr-typing')) document.getElementById('hr-typing').remove();

        appendHRMessage('ai', responseText);

    } catch (e) {
        if (document.getElementById('hr-typing')) document.getElementById('hr-typing').remove();
        console.error("HR Chat error", e);
        appendHRMessage('ai', "Ошибка: Не удалось получить ответ от AI.");
    }
}

function appendHRMessage(role, content) {
    const container = document.getElementById('hr-chat-messages');
    // Clear default msg if exists
    if (container.innerText.includes('Спросите, например')) container.innerHTML = '';

    const div = document.createElement('div');
    const isUser = role === 'user';

    div.style.display = 'flex';
    div.style.justifyContent = isUser ? 'flex-end' : 'flex-start';

    div.innerHTML = `
        <div style="
            max-width: 80%;
            padding: 0.75rem 1rem;
            border-radius: 1rem;
            border-top-${isUser ? 'right' : 'left'}-radius: 0;
            background: ${isUser ? 'var(--primary-color)' : 'white'};
            color: ${isUser ? 'black' : '#1E293B'};
            border: ${isUser ? 'none' : '1px solid #E2E8F0'};
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        ">
            <p style="margin:0; font-size:0.95rem;">${content.replace(/\n/g, '<br>')}</p>
        </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}
