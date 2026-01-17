
document.addEventListener("DOMContentLoaded", () => {
    // Create Vacancy logic
    const createForm = document.getElementById("createVacancyForm");
    if (createForm) {
        // Init first weight row
        addWeightRow();

        createForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            // Collect weights
            const weights = {};
            document.querySelectorAll(".weight-row").forEach(row => {
                const skill = row.querySelector(".weight-skill").value.trim();
                const value = row.querySelector(".weight-value").value;
                if (skill) {
                    weights[skill] = parseFloat(value);
                }
            });

            const data = {
                title: document.getElementById("title").value,
                description: document.getElementById("description").value,
                experience_level: document.getElementById("experience_level").value,
                salary_range: document.getElementById("salary_range").value,
                required_skills: document.getElementById("required_skills").value,
                skill_weights: JSON.stringify(weights)
            };

            try {
                // Post the vacancy
                const vacancy = await Api.post("/vacancies/", data);

                // Immediately trigger demo publication
                await Api.post(`/vacancies/${vacancy.id}/publish-demo`);

                window.location.href = "dashboard.html";
            } catch (err) {
                alert("Ошибка создания вакансии: " + err.message);
            }
        });
    }

    // View Vacancy logic
    const vacancyView = document.getElementById("vacancy-view-container");
    if (vacancyView) {
        const urlParams = new URLSearchParams(window.location.search);
        const id = urlParams.get("id");
        if (id) {
            loadVacancy(id);
        }
    }
});

async function loadVacancy(id) {
    try {
        const vacancy = await Api.get(`/vacancies/${id}`);
        document.getElementById("vacancy-title").textContent = vacancy.title;
        document.getElementById("vacancy-meta").textContent = `${vacancy.experience_level} • ${vacancy.salary_range}`;
        document.getElementById("vacancy-description").textContent = vacancy.description;

        // Load candidates
        loadCandidates(id);

        // Setup Add Candidate button link
        document.getElementById("add-candidate-btn").href = `candidates.html?vacancy_id=${id}`;

    } catch (err) {
        console.error(err);
        alert("Failed to load vacancy");
    }
}

async function loadCandidates(vacancyId) {
    // This function will be shared or called here
    // For MVP simplicity, implementing here or in candidates.js
    // Assuming simple separation: vacancies.js handles Vacancy View Page which has a list of candidates

    try {
        const candidates = await Api.get(`/candidates/?vacancy_id=${vacancyId}`);
        const tbody = document.querySelector("#candidates-table tbody");
        tbody.innerHTML = "";

        // Sort by score (Ranking)
        candidates.sort((a, b) => (b.score || 0) - (a.score || 0));

        candidates.forEach((c, index) => {
            const tr = document.createElement("tr");
            let scoreClass = "status-new"; // neutral
            const scoreVal = (c.score || 0) * 100;
            if (scoreVal >= 80) scoreClass = "status-shortlist";
            else if (scoreVal < 50) scoreClass = "status-rejected";

            // Determine Medal/Rank icon
            let rankIcon = index + 1;
            if (index === 0) rankIcon = '🥇';
            else if (index === 1) rankIcon = '🥈';
            else if (index === 2) rankIcon = '🥉';

            tr.innerHTML = `
                <td style="font-weight:bold;">${rankIcon}</td>
                <td>${c.filename.replace(/\.txt|\.pdf/g, '')}</td>
                <td>
                    <span class="tag ${scoreClass}">${scoreVal.toFixed(0)}%</span>
                </td>
                <td>${c.status}</td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="viewChatHistory(${c.id})" style="width: auto; padding: 0.4rem 0.8rem;">💬 Чат</button>
                </td>
                <td>
                    <a href="candidate-view.html?id=${c.id}"><button class="btn btn-sm" style="width: auto; padding: 0.4rem 0.8rem;">Отчет</button></a>
                </td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error("Error loading candidates", err);
    }
}

async function viewChatHistory(candidateId) {
    const modal = document.getElementById('chatModal');
    const content = document.getElementById('modal-chat-content');
    modal.classList.remove('hidden');
    content.innerHTML = '<div style="text-align:center;">Загрузка диалога...</div>';

    try {
        const messages = await Api.get(`/chat/${candidateId}`);
        if (!messages || messages.length === 0) {
            content.innerHTML = '<div style="text-align:center; color:#94A3B8;">Диалогов пока нет.</div>';
            return;
        }

        content.innerHTML = `<div class="chat-grid" style="padding:0;">${messages.map(msg => `
            <div class="chat-card ${msg.role}" style="margin-bottom:0.5rem; width: 100%; box-sizing: border-box;">
                <div class="chat-card-header">${msg.role === 'user' ? '👤 Кандидат' : '🤖 HR AI'}</div>
                <div class="chat-card-body">${msg.content}</div>
            </div>
        `).join('')}</div>`;
        content.scrollTop = content.scrollHeight;
    } catch (e) {
        content.innerHTML = '<div style="text-align:center; color:red;">Ошибка загрузки.</div>';
    }
}

function closeChatModal() {
    document.getElementById('chatModal').classList.add('hidden');
}

function addWeightRow() {
    const list = document.getElementById('weights-list');
    if (!list) return;

    const row = document.createElement('div');
    row.className = 'weight-row';
    row.style = 'display:flex; gap:0.5rem; align-items:center;';
    row.innerHTML = `
        <input type="text" class="weight-skill" placeholder="Навык (напр. Python)" style="flex:2;">
        <input type="number" class="weight-value" value="1.0" step="0.1" min="0.1" style="flex:1;">
        <button type="button" class="btn btn-sm" style="background:#FEE2E2; color:#991B1B; width:auto; padding: 0.5rem;" onclick="this.parentElement.remove()">×</button>
    `;
    list.appendChild(row);
}
