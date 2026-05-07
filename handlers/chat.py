import httpx, json, re, logging
from config import settings

logger = logging.getLogger(__name__)

async def analyze_project_plan(message: str) -> dict:
    system_prompt = """You are a senior software architect. Create a detailed project plan in JSON format only.
{
    "project_type": "...",
    "description": "...",
    "tech_stack": [...],
    "files": [
        {"name": "main.py", "description": "...", "language": "python", "purpose": "main", "priority": "high"}
    ],
    "total_files": 0,
    "estimated_time": "...",
    "dependencies": [...],
    "ready_to_generate": true
}"""
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                settings.DEEPSEEK_API_URL,
                headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                         "Content-Type": "application/json"},
                json={
                    "model": settings.DEEPSEEK_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 4000
                }
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # fallback plan
                return {
                    "project_type": "project", "description": message,
                    "files": [
                        {"name": "app.py", "description": "Main file", "language": "python", "purpose": "main", "priority": "high"},
                        {"name": "README.md", "description": "Documentation", "language": "markdown", "purpose": "docs", "priority": "medium"}
                    ],
                    "total_files": 2, "estimated_time": "1 min",
                    "dependencies": [], "ready_to_generate": True
                }
    except Exception as e:
        logger.error(f"Plan analysis failed: {e}")
        raise

async def generate_file_code(filename: str, description: str, project_context: str) -> str:
    ext = filename.split('.')[-1] if '.' in filename else ''
    lang_map = {'py': 'Python', 'js': 'JavaScript', 'html': 'HTML', 'css': 'CSS', 'md': 'Markdown'}
    language = lang_map.get(ext.lower(), 'code')

    system_prompt = f"""Write complete, production-ready {language} code for the file '{filename}'.
Project context: {project_context}
File description: {description}
Return ONLY the code inside a markdown code block (```{ext} ... ```)."""
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                settings.DEEPSEEK_API_URL,
                headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                         "Content-Type": "application/json"},
                json={
                    "model": settings.DEEPSEEK_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Generate {filename}"}
                    ],
                    "temperature": 0.5,
                    "max_tokens": 8000
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Code generation failed for {filename}: {e}")
        raise

def extract_code_from_response(response: str) -> str:
    matches = re.findall(r'```(?:\w+)?\s*\n(.*?)\n```', response, re.DOTALL)
    if matches:
        return max(matches, key=len).strip()
    return response.strip()