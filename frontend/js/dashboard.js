
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const analytics = await Api.get("/analytics/");

        document.getElementById("active-vacancies").textContent = analytics.active_vacancies;
        document.getElementById("total-candidates").textContent = analytics.total_candidates;
        document.getElementById("avg-score").textContent = analytics.avg_ai_score;

        const vacancies = await Api.get("/vacancies/");
        const tbody = document.querySelector("#vacancies-table tbody");
        tbody.innerHTML = "";

        if (vacancies.length === 0) {
            tbody.innerHTML = "<tr><td colspan='5' style='text-align:center'>No vacancies found. Create one!</td></tr>";
        } else {
            vacancies.forEach(v => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>
                        <a href="vacancy-view.html?id=${v.id}" style="font-weight:600; text-decoration:none; color:var(--text-color);">
                            ${v.title}
                        </a>
                    </td>
                    <td>${v.experience_level || '-'}</td>
                    <td>${v.salary_range || '-'}</td>
                    <td>-</td> 
                    <td>
                        <a href="vacancy-view.html?id=${v.id}"><button style="width: auto; padding: 0.25rem 0.5rem; font-size: 0.8rem;">View</button></a>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

    } catch (err) {
        console.error("Dashboard error:", err);
    }
});
