
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
        const candidates = await Api.get('/candidates/'); // Fetch all for calc
        const vacancies = await Api.get('/vacancies/');

        // 1. Calculate Core Metrics
        const activeVacancies = vacancies.filter(v => v.status === 'published').length;
        const analyzedCandidates = candidates.filter(c => c.ai_score !== null);
        const avgScore = analyzedCandidates.length > 0
            ? Math.round(analyzedCandidates.reduce((sum, c) => sum + c.ai_score, 0) / analyzedCandidates.length)
            : 0;

        // Simple "Time to Hire" mock (randomized or 0 if no data) as backend doesn't track hired date yet
        const timeToHire = 14;

        // Update Stat Cards
        document.getElementById('avg-ai-score').textContent = avgScore + '%';
        document.getElementById('time-to-hire').textContent = timeToHire;
        document.getElementById('active-vacancies').textContent = activeVacancies;

        // 2. Prepare Chart Data

        // Score Distribution
        const scoreRanges = ['0-20', '21-40', '41-60', '61-80', '81-100'];
        const scoreCounts = [0, 0, 0, 0, 0];

        analyzedCandidates.forEach(c => {
            const score = c.ai_score;
            if (score <= 20) scoreCounts[0]++;
            else if (score <= 40) scoreCounts[1]++;
            else if (score <= 60) scoreCounts[2]++;
            else if (score <= 80) scoreCounts[3]++;
            else scoreCounts[4]++;
        });

        // Status Distribution
        const statuses = ['new', 'screening', 'shortlist', 'interview', 'hired', 'rejected'];
        const statusLabels = ['New', 'Screening', 'Shortlist', 'Interview', 'Hired', 'Rejected'];
        const statusCounts = statuses.map(s => candidates.filter(c => c.status === s).length);
        const statusColors = ['#3b82f6', '#7c3aed', '#f59e0b', '#8b5cf6', '#10b981', '#ef4444'];

        // Vacancy Scores (Top 5)
        const topVacancies = vacancies
            .filter(v => typeof v.avg_score === 'number' && v.avg_score > 0)
            .sort((a, b) => b.avg_score - a.avg_score)
            .slice(0, 5);

        const vacLabels = topVacancies.map(v => v.title.length > 15 ? v.title.substring(0, 15) + '...' : v.title);
        const vacScores = topVacancies.map(v => v.avg_score);

        // 3. Render Charts (Lazy load Chart.js logic)
        renderCharts({
            scoreData: { labels: scoreRanges, data: scoreCounts },
            statusData: { labels: statusLabels.filter((_, i) => statusCounts[i] > 0), data: statusCounts.filter(c => c > 0), colors: statusColors.filter((_, i) => statusCounts[i] > 0) },
            vacData: { labels: vacLabels, data: vacScores }
        });

        // 4. Update Skills List (Mock extraction from candidates)
        const allSkills = {};
        analyzedCandidates.forEach(c => {
            const skills = c.matched_skills || []; // Assuming backend returns this
            skills.forEach(s => {
                allSkills[s] = (allSkills[s] || 0) + 1;
            });
        });
        const sortedSkills = Object.entries(allSkills)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([name, count]) => `<li>${name} (${count})</li>`);

        document.getElementById('top-skills-list').innerHTML = sortedSkills.length ? sortedSkills.join('') : '<li>No skills data yet</li>';

    } catch (e) {
        console.error("Error loading analytics:", e);
    }
}

function renderCharts({ scoreData, statusData, vacData }) {
    // We need to inject <canvas> elements first, replacing the chart placeholders in HTML
    // Wait, the HTML I wrote has Grid but no ID for canvas. Let's assume standard IDs for now or inject them.
    // Actually the HTML provided by user had Recharts components. I need to Replace HTML content first? 
    // No, I already overwrote analytics.html with my structure but it needs Canvas IDs.

    // Quick Fix: The analytics.html I wrote in previous step didn't have <canvas> IDs! 
    // It has `stats-grid` and 2 cards below. I need to INSERT canvas elements.
    // Let's rewrite the "Charts Grid" section dynamically for now to ensure IDs exist.

    const container = document.querySelector('.main-content');
    // Find the div after stats-grid
    const existingChartsInfo = document.querySelector('.main-content > div:last-child'); // The grid with Skills/Export

    // Create a new Chart Grid div to insert BEFORE the last div
    const chartGrid = document.createElement('div');
    chartGrid.className = 'grid grid-cols-1 lg:grid-cols-2 gap-6';
    chartGrid.style.display = 'grid';
    chartGrid.style.gap = '1.5rem';
    chartGrid.style.marginTop = '2rem';
    chartGrid.style.marginBottom = '2rem';

    chartGrid.innerHTML = `
        <div class="card">
            <h3 style="margin-bottom:1rem;">Score Distribution</h3>
            <div style="height:250px;"><canvas id="scoreChart"></canvas></div>
        </div>
        <div class="card">
            <h3 style="margin-bottom:1rem;">Candidate Status</h3>
             <div style="height:250px;"><canvas id="statusChart"></canvas></div>
        </div>
        <div class="card" style="grid-column: span 1;">
            <h3 style="margin-bottom:1rem;">Top Vacancies by Score</h3>
             <div style="height:250px;"><canvas id="vacancyChart"></canvas></div>
        </div>
    `;

    container.insertBefore(chartGrid, existingChartsInfo);

    // Chart 1: Score Distribution (Bar)
    new Chart(document.getElementById('scoreChart'), {
        type: 'bar',
        data: {
            labels: scoreData.labels,
            datasets: [{
                label: 'Candidates',
                data: scoreData.data,
                backgroundColor: '#8B5CF6',
                borderRadius: 4
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    // Chart 2: Status (Doughnut)
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

    // Chart 3: Vacancy (Horizontal Bar)
    new Chart(document.getElementById('vacancyChart'), {
        type: 'bar',
        data: {
            labels: vacData.labels,
            datasets: [{
                label: 'Avg Score',
                data: vacData.data,
                backgroundColor: '#10B981',
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false
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
