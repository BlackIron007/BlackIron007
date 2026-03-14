import json
import requests
import os
from dotenv import load_dotenv
from repo_change_detector import repos_changed

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

INPUT = "data/repo_domains.json"
OUTPUT = "data/repo_clusters.json"

MODEL = "meta-llama/llama-3.3-70b-instruct"

def clean_llm_json_output(text):
    """Removes markdown code fences from LLM's JSON output."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    
    if text.endswith("```"):
        text = text[:-3]
        
    return text.strip()

def cluster_repositories(repo_data):

    prompt = f"""
    You are analyzing technologies used in software repositories.

    Each repository has a list of technologies.

    Your task:
    Cluster the repositories into exactly 6 high-level TECHNICAL domains.

    Important rules:

    1. Use only the technologies list to determine domains.
    2. Ignore repository names completely.
    3. Domains must represent technical skill areas, not application domains.

    Examples of good domains:
    Artificial Intelligence
    Machine Learning
    Backend Systems
    Full Stack Development
    DevOps / Automation
    Computer Vision
    Developer Tools

    Examples of bad domains:
    Social Media
    Blog Platform
    E-commerce
    Attendance System

    Return JSON in this format:

    {{
    "domains": ["Domain1","Domain2","Domain3","Domain4","Domain5","Domain6"],
    "mapping": {{
    "repo_name": "Domain"
    }}
    }}

    Repositories and technologies:

    {json.dumps(repo_data, indent=2)}
    """

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages":[{"role":"user","content":prompt}],
                "response_format": { "type": "json_object" }
            }
        )
        r.raise_for_status()
        response_json = r.json()

        if "choices" in response_json and response_json.get("choices"):
            raw_text = response_json["choices"][0]["message"]["content"]
            cleaned_text = clean_llm_json_output(raw_text)
            return json.loads(cleaned_text)
        else:
            print("Error: Unexpected API response structure:")
            print(response_json)
            return None

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error during clustering: {e}")
        print("API Response Text:", r.text)
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON from LLM content: {e}")
        try:
            print("LLM Output:", r.json()["choices"][0]["message"]["content"])
        except Exception:
            print("Could not extract LLM output from response.")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error parsing API response structure: {e}")
        print("API Response JSON:", r.json())
        return None

def main():

    if not repos_changed():
        print("No repo changes detected - skipping clustering")
        return

    with open(INPUT) as f:
        repo_data = json.load(f)

    result = cluster_repositories(repo_data)

    if result:
        with open(OUTPUT,"w") as f:
            json.dump(result,f,indent=2)
        print("Domain clusters generated")
    else:
        print("Clustering failed. No output file generated.")

if __name__ == "__main__":
    main()