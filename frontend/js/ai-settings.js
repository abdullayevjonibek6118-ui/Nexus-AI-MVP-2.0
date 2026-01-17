// AI Settings Page JavaScript

document.addEventListener('DOMContentLoaded', async () => {
    await loadAISettings();

    // Temperature slider update
    const tempSlider = document.getElementById('temperature');
    const tempValue = document.getElementById('temp-value');

    tempSlider.addEventListener('input', (e) => {
        tempValue.textContent = e.target.value;
    });

    // Form submission
    document.getElementById('aiSettingsForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await saveAISettings();
    });
});

async function loadAISettings() {
    try {
        const settings = await Api.get('/ai-settings/');

        if (settings) {
            document.getElementById('ai_role').value = settings.ai_role;
            document.getElementById('system_prompt').value = settings.system_prompt;
            document.getElementById('model_name').value = settings.model_name;
            document.getElementById('temperature').value = settings.temperature;
            document.getElementById('temp-value').textContent = settings.temperature;
        }
    } catch (error) {
        console.error('Error loading AI settings:', error);
        // Use defaults if no settings exist yet
    }
}

async function saveAISettings() {
    const settings = {
        ai_role: document.getElementById('ai_role').value,
        system_prompt: document.getElementById('system_prompt').value,
        model_name: document.getElementById('model_name').value,
        temperature: parseFloat(document.getElementById('temperature').value)
    };

    try {
        await Api.post('/ai-settings/', settings);
        alert('Настройки ИИ успешно сохранены!');
    } catch (error) {
        console.error('Error saving AI settings:', error);
        alert('Ошибка при сохранении настроек');
    }
}

function resetToDefaults() {
    if (confirm('Сбросить все настройки к значениям по умолчанию?')) {
        document.getElementById('ai_role').value = 'Эксперт по подбору персонала';
        document.getElementById('system_prompt').value = `Вы - опытный HR-специалист с глубокими знаниями в области подбора персонала. 
Ваша задача - объективно оценивать кандидатов на соответствие требованиям вакансии и предоставлять практические рекомендации.`;
        document.getElementById('model_name').value = 'x-ai/grok-4.1-fast';
        document.getElementById('temperature').value = '0.7';
        document.getElementById('temp-value').textContent = '0.7';
    }
}
