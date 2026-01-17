
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const analytics = await Api.get("/analytics/");

        // Load Subscription Status
        try {
            const status = await Api.get('/candidates/subscription/status');
            const widget = document.getElementById('subscription-status-widget');
            if (widget) {
                widget.style.display = 'block';
                document.getElementById('widget-tier-name').innerText = status.tier_name;

                const badge = document.getElementById('widget-status-badge');
                if (status.is_expired) {
                    badge.innerText = 'Истек';
                    badge.className = 'badge bg-red';
                } else if (status.is_trial) {
                    badge.innerText = 'Пробный';
                    badge.className = 'badge bg-blue';
                } else {
                    badge.innerText = 'Активен';
                    badge.className = 'badge bg-green';
                }

                if (status.is_trial) {
                    document.getElementById('widget-days-left').innerText = `Осталось дней: ${status.days_left}`;
                } else {
                    document.getElementById('widget-days-left').innerText = 'Бессрочная подписка';
                }

                const used = status.used;
                const limit = status.limit;
                const percent = Math.min(100, (used / limit) * 100);

                document.getElementById('widget-usage-text').innerText = `${used} / ${limit}`;
                const progressBar = document.getElementById('widget-progress-bar');
                progressBar.style.width = `${percent}%`;

                // Color logic
                const remaining = 100 - percent;
                if (remaining > 50) {
                    progressBar.style.backgroundColor = '#10B981'; // Green
                } else if (remaining > 20) {
                    progressBar.style.backgroundColor = '#F59E0B'; // Yellow
                } else {
                    progressBar.style.backgroundColor = '#EF4444'; // Red
                }
            }
        } catch (subErr) {
            console.error("Failed to load subscription status in widget", subErr);
        }

        document.getElementById("stat-active-vacancies").textContent = analytics.active_vacancies;
        document.getElementById("stat-total-candidates").textContent = analytics.total_candidates;
        // avg-score is not in the stats but we can add it or ignore if not present
        if (document.getElementById("avg-score")) {
            document.getElementById("avg-score").textContent = analytics.avg_ai_score;
        }

        const vacancies = await Api.get("/vacancies/");
        const tbody = document.getElementById("vacancies-table-body");
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
