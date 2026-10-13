import re
from datetime import datetime, timedelta
import openai
from app.core.config import settings

def parse_task_heuristics(text: str) -> dict:
    result = {
        "title": text,
        "description": "",
        "priority": "MEDIUM",
        "dueDate": None,
        "estimatedMinutes": None
    }
    
    lower_text = text.lower()
    if any(w in lower_text for w in ["urgent", "asap", "critical"]):
        result["priority"] = "URGENT"
    elif any(w in lower_text for w in ["high priority", "important", "must do"]):
        result["priority"] = "HIGH"
    elif any(w in lower_text for w in ["low priority", "trivial", "minor"]):
        result["priority"] = "LOW"
        
    duration_match = re.search(r'(\d+)\s*(m|min|minutes|h|hr|hours)', lower_text)
    if duration_match:
        val = int(duration_match.group(1))
        unit = duration_match.group(2)
        if unit.startswith('h'):
            result["estimatedMinutes"] = val * 60
        else:
            result["estimatedMinutes"] = val
            
    now = datetime.now()
    if "today" in lower_text:
        result["dueDate"] = now.replace(hour=23, minute=59, second=59)
    elif "tomorrow" in lower_text:
        result["dueDate"] = (now + timedelta(days=1)).replace(hour=23, minute=59, second=59)
    elif "next week" in lower_text:
        result["dueDate"] = (now + timedelta(weeks=1)).replace(hour=23, minute=59, second=59)
        
    clean_title = text
    clean_title = re.sub(r'(?i)\b(urgent|asap|critical|today|tomorrow|next week)\b', '', clean_title)
    clean_title = re.sub(r'\d+\s*(m|min|minutes|h|hr|hours)', '', clean_title)
    clean_title = re.sub(r'\s+', ' ', clean_title).strip()
    if clean_title:
        result["title"] = clean_title
        
    return result

async def parse_task_ai(text: str) -> dict:
    if not settings.OPENAI_API_KEY:
        return parse_task_heuristics(text)
        
    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = f"""
        You are an AI Task Parsing Engine. Parse the following sentence and extract task metadata:
        Sentence: "{text}"
        
        Extract the following fields in JSON format:
        - title: clear, concise summary of the task
        - description: extra context
        - priority: "LOW", "MEDIUM", "HIGH", or "URGENT"
        - estimatedMinutes: integer or null
        - dueDate: date-time string in ISO 8601 format (YYYY-MM-DDTHH:MM:SS) or null
        
        Provide only valid raw JSON.
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        import json
        parsed = json.loads(response.choices[0].message.content)
        if "dueDate" in parsed and parsed["dueDate"]:
            parsed["dueDate"] = datetime.fromisoformat(parsed["dueDate"])
        return parsed
    except Exception as e:
        print(f"Error parsing task with AI: {e}")
        return parse_task_heuristics(text)
