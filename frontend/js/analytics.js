
document.addEventListener('DOMContentLoaded', async () => {
    // Check auth
    if (!Api.getToken()) {
        window.location.href = 'login.html';
        return;
    }

    await loadAnalytics();
});

async function loadAnalytics() {
    try {
        // Fetch analytics from backend which now returns advanced metrics
        const data = await Api.get('/analytics/');

        // Update KPI Cards
        document.getElementById('avg-ai-score').textContent = data.avg_ai_score + '%';
        document.getElementById('active-vacancies').textContent = data.active_vacancies;

        // New Metrics
        if (data.metrics) {
            document.getElementById('time-to-hire').textContent = data.metrics.time_to_hire + ' days';
        }

        // 2. Prepare Chart Data from Backend Response

        // Score Distribution (We can keep this calculated frontend or assume backend might send it later. 
        // For now, let's keep the frontend calc if backend doesn't send specific distro, 
        // but wait, backend currently sends: active_vacancies, total, avg, status_breakdown, sources, top_skills, metrics.
        // It does NOT send score_distribution list yet. So we might need to fetch candidates if we want that detail,
        // OR we can rely on what we have.
        // To be safe and efficient, let's use the status_breakdown from backend directly.

        const statusData = {
            labels: Object.keys(data.status_breakdown).map(s => s.charAt(0).toUpperCase() + s.slice(1)),
            data: Object.values(data.status_breakdown),
            colors: ['#3b82f6', '#7c3aed', '#f59e0b', '#8b5cf6', '#10b981', '#ef4444']
        };

        // Funnel Data (from metrics)
        const funnel = data.metrics.funnel_conversion;
        const funnelData = {
            labels: ['New -> Screened', 'Screened -> Interview', 'Interview -> Offer'],
            data: [funnel.new_to_screened, funnel.screened_to_interview, funnel.interview_to_offer]
        };

        // 3. Render Charts
        renderCharts({
            statusData: statusData,
            funnelData: funnelData
        });

        // 4. Update Skills List
        if (data.top_skills && data.top_skills.length) {
            const skillsHtml = data.top_skills.map(s => `<li>${s}</li>`).join('');
            document.getElementById('top-skills-list').innerHTML = skillsHtml;
        }

    } catch (e) {
        console.error("Error loading analytics:", e);
    }
}

function renderCharts({ statusData, funnelData }) {
    const container = document.querySelector('.main-content');

    // Remove existing chart grid if present to avoid duplicates during reload
    const existingGrid = document.getElementById('chart-grid-dynamic');
    if (existingGrid) existingGrid.remove();

    const chartGrid = document.createElement('div');
    chartGrid.id = 'chart-grid-dynamic';
    chartGrid.className = 'grid grid-cols-1 lg:grid-cols-2 gap-6';
    chartGrid.style.display = 'grid';
    chartGrid.style.gap = '1.5rem';
    chartGrid.style.marginTop = '2rem';
    chartGrid.style.marginBottom = '2rem';

    chartGrid.innerHTML = `
            <div class="card">
                <h3 style="margin-bottom:1rem;">Candidate Status</h3>
                <div style="height:250px;"><canvas id="statusChart"></canvas></div>
            </div>
            <div class="card">
                <h3 style="margin-bottom:1rem;">Hiring Funnel Conversion (%)</h3>
                 <div style="height:250px;"><canvas id="funnelChart"></canvas></div>
            </div>
        `;

    // Insert before the last div (usually lists)
    const lastDiv = document.querySelector('.main-content > div:last-child');
    container.insertBefore(chartGrid, lastDiv);

    // Chart 1: Status (Doughnut)
    new Chart(document.getElementById('statusChart'), {
        type: 'doughnut',
        data: {
            labels: statusData.labels,
            datasets: [{
                data: statusData.data,
                backgroundColor: statusData.colors,
                borderWidth: 0
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    // Chart 2: Funnel (Bar or Line)
    new Chart(document.getElementById('funnelChart'), {
        type: 'bar',
        data: {
            labels: funnelData.labels,
            datasets: [{
                label: 'Conversion Rate %',
                data: funnelData.data,
                backgroundColor: '#10B981',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, max: 100 }
            }
        }
    });
}

function exportData() {
    // Basic CSV export
    Api.get('/candidates/').then(data => {
        const headers = ['ID', 'Name', 'Email', 'Status', 'AI Score'];
        const rows = data.map(c => [c.id, c.full_name, c.email, c.status, c.ai_score].join(','));
        const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows].join('\n');
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "candidates_export.csv");
        document.body.appendChild(link);
        link.click();
    });
}
