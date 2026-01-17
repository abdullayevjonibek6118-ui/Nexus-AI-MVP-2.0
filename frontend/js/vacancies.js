
document.addEventListener("DOMContentLoaded", () => {
    // Create Vacancy logic
    const createForm = document.getElementById("createVacancyForm");
    if (createForm) {
        createForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const data = {
                title: document.getElementById("title").value,
                description: document.getElementById("description").value,
                experience_level: document.getElementById("experience_level").value,
                salary_range: document.getElementById("salary_range").value,
                required_skills: document.getElementById("required_skills").value
            };

            try {
                await Api.post("/vacancies/", data);
                window.location.href = "dashboard.html";
            } catch (err) {
                alert("Error creating vacancy: " + err.message);
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

        candidates.forEach(c => {
            const tr = document.createElement("tr");
            let scoreClass = "status-new"; // neutral
            if (c.score >= 0.8) scoreClass = "status-shortlist";
            else if (c.score > 0 && c.score < 0.5) scoreClass = "status-rejected";

            tr.innerHTML = `
                <td>${c.filename}</td>
                <td>
                    <span class="tag ${scoreClass}">${(c.score * 100).toFixed(0)}%</span>
                </td>
                <td>${c.status}</td>
                <td>
                    <a href="candidate-view.html?id=${c.id}"><button style="width: auto; padding: 0.25rem 0.5rem; font-size: 0.8rem;">View Report</button></a>
                </td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error("Error loading candidates", err);
    }
}
