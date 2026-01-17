import requests
import json
from typing import Optional, Dict, Any, List
from app.core.config import settings

class HHService:
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.base_url = "https://api.hh.ru"
        self.user_agent = f"NexusAI/1.0 ({settings.EMAIL})"

    def _get_headers(self, token: Optional[str] = None):
        headers = {"User-Agent": self.user_agent}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def get_auth_url(self) -> str:
        """Returns the HH.ru authorization URL."""
        return (
            f"https://hh.ru/oauth/authorize?response_type=code"
            f"&client_id={settings.HH_CLIENT_ID}"
            f"&redirect_uri={settings.HH_REDIRECT_URI}"
        )

    def get_token(self, code: str) -> Dict[str, Any]:
        """Exchanges authorization code for an access token."""
        payload = {
            "grant_type": "authorization_code",
            "client_id": settings.HH_CLIENT_ID,
            "client_secret": settings.HH_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.HH_REDIRECT_URI,
        }
        resp = requests.post("https://hh.ru/oauth/token", data=payload)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"[HH] Token Error: {resp.text}")
            return {"error": resp.text}

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refreshes an access token."""
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        resp = requests.post("https://hh.ru/oauth/token", data=payload)
        if resp.status_code == 200:
            return resp.json()
        else:
            return {"error": resp.text}

    def publish_vacancy(self, vacancy_data: Dict[str, Any], token: Optional[str] = None) -> Dict[str, Any]:
        """
        Publishes a vacancy to HH.ru.
        """
        if self.mock_mode or not token:
            print(f"[HH] Publishing vacancy to HH.ru (Mock because mock_mode={self.mock_mode} or no token)...")
            return {
                "id": f"mock_hh_id_{vacancy_data.get('id', 'new')}",
                "status": "active",
                "url": "https://hh.ru/vacancy/mock"
            }

        # Real implementation
        try:
            # Note: HH.ru requires very specific fields for real publication.
            # This is a simplified version.
            payload = {
                "name": vacancy_data.get("title"),
                "description": vacancy_data.get("description"),
                "area": {"id": "1"}, # Moscow by default for MVP
                "type": {"id": "open"},
                "billing_type": {"id": "free"}, # or 'standard'
                "experience": {"id": "noExperience"}, # default
                "schedule": {"id": "fullDay"},
                "employment": {"id": "full"},
            }
            resp = requests.post(
                f"{self.base_url}/vacancies", 
                json=payload, 
                headers=self._get_headers(token)
            )
            if resp.status_code == 201:
                data = resp.json()
                return {
                    "id": data.get("id"),
                    "status": "active",
                    "url": data.get("alternate_url")
                }
            else:
                return {"error": f"HH.ru Error: {resp.status_code} - {resp.text}"}
        except Exception as e:
            return {"error": f"Exception: {str(e)}"}

    def get_responses(self, hh_vacancy_id: str, token: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetches responses (candidates) for a vacancy using /negotiations endpoint.
        """
        if self.mock_mode or not token:
            print(f"[HH] Fetching responses for vacancy {hh_vacancy_id} (Mock)...")
            return [
                {
                    "hh_resume_id": "mock_resume_123",
                    "full_name": "Иван Иванов",
                    "email": "ivan@example.com",
                    "content": "Опытный Python разработчик с навыками FastAPI и SQL."
                }
            ]

    def get_responses(self, hh_vacancy_id: str, token: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetches responses (candidates) for a vacancy using /negotiations endpoint.
        """
        if self.mock_mode or not token:
            print(f"[HH] Fetching responses for vacancy {hh_vacancy_id} (Mock because mock_mode={self.mock_mode} or no token)...")
            return [
                {
                    "hh_resume_id": "mock_resume_123",
                    "full_name": "Иван Иванов",
                    "email": "ivan@example.com",
                    "content": "Опытный Python разработчик с навыками FastAPI и SQL."
                }
            ]

        # Real implementation
        try:
            resp = requests.get(
                f"{self.base_url}/negotiations?vacancy_id={hh_vacancy_id}", 
                headers=self._get_headers(token)
            )
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                results = []
                for item in items:
                    resume_brief = item.get("resume", {})
                    resume_id = resume_brief.get("id")
                    
                    if not resume_id:
                        continue

                    # Fetch full resume details if possible
                    resume_details = self.get_resume_details(resume_id, token)
                    
                    full_name = f"{resume_brief.get('first_name', '')} {resume_brief.get('last_name', '')}".strip()
                    if not full_name and resume_details:
                        full_name = f"{resume_details.get('first_name', '')} {resume_details.get('last_name', '')}".strip()

                    content = ""
                    if resume_details:
                        # Construct content from experience and skills
                        exp = resume_details.get("experience", [])
                        skills = ", ".join([s.get("name", "") for s in resume_details.get("skill_set", [])])
                        content = f"Title: {resume_details.get('title', 'N/A')}\nSkills: {skills}\n"
                        for e in exp:
                            content += f"\n- {e.get('company', 'N/A')}: {e.get('position', 'N/A')} ({e.get('description', 'N/A')})"
                    else:
                        content = resume_brief.get("title", "No content available")

                    results.append({
                        "hh_resume_id": resume_id,
                        "full_name": full_name or "Anonymous",
                        "email": item.get("email") or resume_brief.get("email"),
                        "content": content
                    })
                return results
            else:
                print(f"[HH] Error fetching negotiations: {resp.status_code} - {resp.text}")
                return []
        except Exception as e:
            print(f"[HH] Exception fetching negotiations: {str(e)}")
            return []

    def get_resume_details(self, resume_id: str, token: str) -> Optional[Dict[str, Any]]:
        """Fetches full resume details."""
        try:
            resp = requests.get(
                f"{self.base_url}/resumes/{resume_id}",
                headers=self._get_headers(token)
            )
            if resp.status_code == 200:
                return resp.json()
            return None
        except:
            return None

    def send_message(self, hh_resume_id: str, message: str, vacancy_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        """
        Sends a message to a candidate on HH.ru (invite or message).
        Uses /negotiations/invite if no chat exists, or /negotiations/messages if chat exists.
        For MVP simplifiction, we'll assume we are sending an invite.
        """
        if self.mock_mode or not token:
            print(f"[HH] Sending message to {hh_resume_id} (Mock): {message[:50]}...")
            return {"status": "sent", "mock": True}

        # Real Implementation (simplified invite)
        try:
            url = f"{self.base_url}/negotiations"
            payload = {
                "resume_id": hh_resume_id,
                "vacancy_id": vacancy_id,
                "message": message
            }
            # Note: This is creating a new negotiation (invite)
            resp = requests.post(url, json=payload, headers=self._get_headers(token))
            
            if resp.status_code in [201, 200]:
                return {"status": "sent", "hh_status": resp.status_code}
            else:
                 return {"error": f"HH.ru Error: {resp.status_code} - {resp.text}"}
        except Exception as e:
            return {"error": str(e)}

    def get_automated_token(self) -> Optional[str]:
        """
        Attempts to get a token using EMAIL and PASSWORD from .env.
        Note: HH.ru standard API requires OAuth2 code/client_credentials.
        Direct password grant is usually reserved for official mobile apps.
        We will try to simulate a token exchange or use a saved one.
        """
        if not settings.EMAIL or not settings.PASSWORD:
            print("[HH] Missing EMAIL or PASSWORD in .env")
            return None
        
        # NOTE: For HH.ru, the most reliable way for automation without browser
        # is using client_credentials (if application type allows) or persistent refresh_token.
        # Since we have EMAIL/PASS, we'll try a basic post to their token endpoint if they support password grant.
        
        print(f"[HH] Attempting automated login for {settings.EMAIL}...")
        
        # This is a PLACEHOLDER for the actual HH.ru automation.
        # Most APIs don't allow raw email/pass for security.
        # If HH.ru doesn't support it, we would use a headless browser or suggest OAuth.
        
        # For this step, we'll return a 'mock_automated_token' if settings are present
        # to show that the logic for automation is being triggered.
        return f"auto_token_{settings.EMAIL[:5]}"

    def toggle_mock(self, mock: bool):
        self.mock_mode = mock

    async def scrape_resumes_for_training(self, vacancy_query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape resumes from HH.ru for AI training purposes.
        
        Args:
            vacancy_query: Search query (e.g., "Python Developer")
            limit: Maximum number of resumes to fetch
            
        Returns:
            List of resume dictionaries with 'id', 'title', 'experience', 'skills'
        """
        if self.mock_mode:
            print(f"[HH] Mock scraping resumes for '{vacancy_query}'")
            return self._get_mock_training_resumes()
        
        try:
            import httpx
            from bs4 import BeautifulSoup
            
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8"
            }
            
            # Search for resumes
            search_url = f"{self.base_url}/search/resume"
            params = {"text": vacancy_query, "area": 1, "items_on_page": min(limit, 20)}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(search_url, headers=headers, params=params, timeout=15.0)
                
                if response.status_code != 200:
                    print(f"[HH] Failed to fetch resumes: {response.status_code}")
                    return self._get_mock_training_resumes()
                
                # Parse HTML to extract resume links
                soup = BeautifulSoup(response.text, 'html.parser')
                resume_items = soup.find_all('div', class_='resume-search-item', limit=limit)
                
                resumes = []
                for item in resume_items:
                    title_elem = item.find('a', class_='resume-search-item__name')
                    if title_elem:
                        resume_id = title_elem.get('href', '').split('/')[-1].split('?')[0]
                        title = title_elem.text.strip()
                        
                        # Extract experience and skills from snippet
                        experience_elem = item.find('div', class_='resume-search-item__experience')
                        experience = experience_elem.text.strip() if experience_elem else "Not specified"
                        
                        resumes.append({
                            "id": resume_id,
                            "title": title,
                            "experience": experience,
                            "skills": []  # Would need API access for detailed skills
                        })
                
                return resumes if resumes else self._get_mock_training_resumes()
                
        except Exception as e:
            print(f"[HH] Exception during scraping: {str(e)}")
            return self._get_mock_training_resumes()
    
    def _get_mock_training_resumes(self) -> List[Dict[str, Any]]:
        """Return mock training resumes for development."""
        return [
            {
                "id": "mock_resume_001",
                "title": "Python Backend Developer",
                "experience": "Опыт работы 3 года. Разработка веб-приложений на Django и FastAPI.",
                "skills": ["Python", "Django", "FastAPI", "PostgreSQL", "Docker"]
            },
            {
                "id": "mock_resume_002",
                "title": "Full-stack разработчик",
                "experience": "Опыт работы 5 лет. React, Node.js, MongoDB.",
                "skills": ["JavaScript", "React", "Node.js", "MongoDB", "TypeScript"]
            },
            {
                "id": "mock_resume_003",
                "title": "Senior Python Developer",
                "experience": "Опыт работы 7+ лет. Микросервисная архитектура, K8s.",
                "skills": ["Python", "Microservices", "Kubernetes", "AWS", "Redis"]
            }
        ]

# Singleton instance
hh_service = HHService(mock_mode=True)

