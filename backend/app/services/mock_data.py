import random

NAMES = [
    "Александр Иванов", "Мария Смирнова", "Дмитрий Кузнецов", "Анна Попова",
    "Сергей Васильев", "Елена Соколова", "Андрей Михайлов", "Ольга Новикова",
    "Игорь Фёдоров", "Татьяна Морозова", "Никита Волков", "Юлия Алексеева",
    "Артем Лебедев", "Наталья Семенова", "Виктор Степанов", "Екатерина Павлова",
    "Максим Козлов", "Светлана Макарова", "Денис Орлов", "Ирина Никитина"
]

SKILLS_BY_CATEGORY = {
    "Backend": ["Python", "Django", "FastAPI", "PostgreSQL", "Redis", "Docker", "Kubernetes", "gRPC", "RabbitMQ"],
    "Frontend": ["JavaScript", "TypeScript", "React", "Vue.js", "Next.js", "Tailwind CSS", "Redux", "Webpack"],
    "Data Science": ["Pandas", "NumPy", "Scikit-Learn", "TensorFlow", "PyTorch", "SQL", "Spark", "MLOps"],
    "DevOps": ["Terraform", "Ansible", "CI/CD", "AWS", "GCP", "Azure", "Linux", "Prometheus", "Grafana"]
}

EXPERIENCE_TEMPLATES = [
    "Более {years} лет опыта в разработке. Работал над высоконагруженными системами и микросервисной архитектурой.",
    "Специализируюсь на {category} разработке. Имею опыт работы с {skills}.",
    "Занимаюсь проектированием и реализацией сложных бизнес-решений. Глубокое понимание {skills}.",
    "В поисках новых вызовов в области {category}. Уверенно владею {skills}.",
    "Имею опыт руководства командой разработчиков (Lead). Эксперт в {skills}."
]

def generate_mock_resume(vacancy_title: str, required_skills: str) -> str:
    category = "Backend"
    if "Front" in vacancy_title or "React" in vacancy_title:
        category = "Frontend"
    elif "Data" in vacancy_title or "ML" in vacancy_title:
        category = "Data Science"
    elif "DevOps" in vacancy_title or "Ops" in vacancy_title:
        category = "DevOps"

    years = random.randint(2, 10)
    skills = random.sample(SKILLS_BY_CATEGORY.get(category, SKILLS_BY_CATEGORY["Backend"]), k=4)
    
    # Add some required skills from vacancy
    if required_skills:
        req_list = [s.strip() for s in required_skills.split(",")]
        skills.extend(random.sample(req_list, k=min(2, len(req_list))))
    
    skills_str = ", ".join(list(set(skills)))
    template = random.choice(EXPERIENCE_TEMPLATES)
    
    content = template.format(years=years, category=category, skills=skills_str)
    return content

def get_random_name() -> str:
    return random.choice(NAMES)
