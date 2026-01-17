
// Map React action colors/icons handling to Vanilla
const actionConfig = {
    vacancy_created: { label: 'Vacancy Created', colorClass: 'bg-blue-50 text-blue-700 border-blue-200', icon: 'M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' },
    vacancy_published: { label: 'Vacancy Published', colorClass: 'bg-emerald-50 text-emerald-700 border-emerald-200', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
    candidate_added: { label: 'Candidate Added', colorClass: 'bg-purple-50 text-purple-700 border-purple-200', icon: 'M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z' },
    candidate_analyzed: { label: 'AI Analysis', colorClass: 'bg-amber-50 text-amber-700 border-amber-200', icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
    status_changed: { label: 'Status Changed', colorClass: 'bg-indigo-50 text-indigo-700 border-indigo-200', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
    resume_uploaded: { label: 'Resume Uploaded', colorClass: 'bg-violet-50 text-violet-700 border-violet-200', icon: 'M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12' },
    default: { label: 'Activity', colorClass: 'bg-slate-50 text-slate-700 border-slate-200', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' }
};

let allActivities = [];
let currentFilter = 'all';
let searchQuery = '';

document.addEventListener('DOMContentLoaded', async () => {
    // Check auth
    if (!Api.getToken()) {
        window.location.href = 'login.html';
        return;
    }

    // Load activities
    await loadActivities();

    // Setup Search
    document.getElementById('searchInput').addEventListener('input', (e) => {
        searchQuery = e.target.value.toLowerCase();
        renderTimeline();
    });
});

async function loadActivities() {
    try {
        const response = await Api.get('/activities/'); // Ensure trailing slash if needed by FastAPI logic, or not
        allActivities = response;
        renderTimeline();
    } catch (error) {
        console.error('Failed to load activities:', error);
        document.getElementById('activity-timeline').innerHTML = '<p class="text-center text-red-500">Failed to load history.</p>';
    }
}

function filterActivities(type, btnElement) {
    currentFilter = type;

    // Update UI
    document.querySelectorAll('.filter-group button').forEach(btn => {
        btn.classList.remove('bg-slate-900', 'text-white');
        btn.classList.add('bg-white', 'text-slate-600');
    });
    if (btnElement) {
        btnElement.classList.remove('bg-white', 'text-slate-600');
        btnElement.classList.add('bg-slate-900', 'text-white');
    }

    renderTimeline();
}

function renderTimeline() {
    const container = document.getElementById('activity-timeline');
    const emptyState = document.getElementById('empty-state');

    // Filter
    const filtered = allActivities.filter(act => {
        const matchesSearch = (act.description || '').toLowerCase().includes(searchQuery) ||
            (act.entity_name || '').toLowerCase().includes(searchQuery);
        const matchesType = currentFilter === 'all' || act.action_type === currentFilter;
        return matchesSearch && matchesType;
    });

    if (filtered.length === 0) {
        container.innerHTML = '';
        emptyState.classList.remove('hidden');
        return;
    }

    emptyState.classList.add('hidden');

    // Group by Date
    const groups = {};
    filtered.forEach(act => {
        const dateKey = moment(act.created_date).format('YYYY-MM-DD');
        if (!groups[dateKey]) groups[dateKey] = [];
        groups[dateKey].push(act);
    });

    // Generate HTML
    let html = '';
    const sortedDates = Object.keys(groups).sort().reverse(); // Newest first

    sortedDates.forEach(date => {
        const acts = groups[date];
        const dateLabel = moment(date).calendar(null, {
            sameDay: '[Today]',
            lastDay: '[Yesterday]',
            lastWeek: 'dddd',
            sameElse: 'D MMMM YYYY'
        });

        html += `
            <div>
                <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:1rem;">
                    <h3 style="font-size:0.875rem; font-weight:600; color:#64748B; margin:0;">${dateLabel}</h3>
                    <div style="flex:1; height:1px; background:#E2E8F0;"></div>
                </div>
                <div class="space-y-3">
                    ${acts.map(act => renderActivityItem(act)).join('')}
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function renderActivityItem(act) {
    const config = actionConfig[act.action_type] || actionConfig.default;
    const time = moment(act.created_date).format('HH:mm');

    // Parse classes into inline styles for Vanilla JS simplicity (mocking new Tailwind classes)
    // Actually we have main.css so we can use classes if they exist, or inline styles for specific colors not in main.css
    // Let's use the colors defined in config roughly mapped to styles

    // Quick mapping for background/text colors based on the React props
    let bgStyle = '';
    let textStyle = '';
    let borderStyle = '';

    if (config.colorClass.includes('blue')) { bgStyle = '#EFF6FF'; textStyle = '#1D4ED8'; borderStyle = '#BFDBFE'; }
    else if (config.colorClass.includes('emerald') || config.colorClass.includes('green')) { bgStyle = '#ECFDF5'; textStyle = '#047857'; borderStyle = '#A7F3D0'; }
    else if (config.colorClass.includes('purple') || config.colorClass.includes('violet')) { bgStyle = '#F5F3FF'; textStyle = '#5B21B6'; borderStyle = '#DDD6FE'; }
    else if (config.colorClass.includes('amber') || config.colorClass.includes('orange')) { bgStyle = '#FFFBEB'; textStyle = '#B45309'; borderStyle = '#FDE68A'; }
    else { bgStyle = '#F8FAFC'; textStyle = '#334155'; borderStyle = '#E2E8F0'; }

    return `
        <div class="card" style="padding:1rem; border:1px solid #F1F5F9; transition:all 0.2s;" onmouseover="this.style.borderColor='${borderStyle}'" onmouseout="this.style.borderColor='#F1F5F9'">
            <div style="display:flex; align-items:flex-start; gap:1rem;">
                <div style="width:40px; height:40px; border-radius:0.75rem; display:flex; align-items:center; justify-content:center; background:${bgStyle}; color:${textStyle}; flex-shrink:0;">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="20" height="20"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${config.icon}" /></svg>
                </div>
                <div style="flex:1;">
                    <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.25rem;">
                        <span class="badge" style="background:${bgStyle}; color:${textStyle}; font-size:0.75rem;">${config.label}</span>
                        <span style="font-size:0.75rem; color:#94A3B8;">${time}</span>
                    </div>
                    <p style="margin:0; font-weight:500; color:#0F172A;">${act.description}</p>
                    ${act.entity_name ? `
                        <div style="font-size:0.875rem; margin-top:0.25rem; display:flex; align-items:center; gap:0.5rem;">
                            <span style="color:#64748B;">${act.entity_name}</span>
                            ${act.entity_id ? `
                                <a href="${act.entity_type === 'Vacancy' ? 'vacancy-view.html?id=' + act.entity_id : 'candidate-view.html?id=' + act.entity_id}" style="color:#7C3AED; text-decoration:none; display:flex; align-items:center; font-size:0.75rem; font-weight:500;">
                                    Open
                                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" width="12" height="12" style="margin-left:2px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                                </a>
                            `: ''}
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}
