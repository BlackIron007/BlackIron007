import requests
import json
import os
import base64
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = "BlackIron007"

INPUT = "data/repos.json"
OUTPUT = "data/repo_domains.json"

MODEL = "meta-llama/llama-3.3-70b-instruct"

def clean_llm_output(text):
    """Removes common conversational prefixes from the LLM output."""
    if not isinstance(text, str):
        return text

    prefixes_to_remove = [
        "based on the repository data, the main technologies, frameworks, and concepts are",
        "the main technologies, frameworks, and concepts are",
        "here is a list of the main technologies, frameworks, and concepts",
        "here are the main technologies, frameworks, and concepts",
        "main technologies, frameworks, and concepts",
    ]
    
    normalized_text = text.strip().lower()
    
    for prefix in prefixes_to_remove:
        if normalized_text.startswith(prefix):
            prefix_end_index = len(prefix)
            return text[prefix_end_index:].lstrip(":\n ").strip()
            
    return text.strip()

def truncate_text(text, max_chars):
    """Truncates text to a maximum character count, adding an ellipsis if truncated."""
    if text and len(text) > max_chars:
        return text[:max_chars] + "\n... (content truncated)"
    return text

def get_github_file_content(repo_name, file_path):
    """Fetches the content of a file from a GitHub repository."""
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/contents/{file_path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()
        try:
            content = base64.b64decode(data['content']).decode('utf-8')
            return content
        except UnicodeDecodeError:
            print(f"Warning: Could not decode {file_path} in {repo_name} as UTF-8. Skipping file.")
            return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code != 404:
            print(f"HTTP error fetching {file_path} for {repo_name}: {e}")
        return None

def get_github_tree(repo_name, branch):
    """Fetches the recursive file tree for a given branch."""
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/git/trees/{branch}?recursive=1"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()
        file_paths = [item['path'] for item in data.get('tree', []) if item['type'] == 'blob']
        tree_string = "\n".join(file_paths)
        if data.get('truncated'):
            tree_string += "\n... (file list is truncated)"
        return tree_string
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error fetching tree for {repo_name}: {e}")
        return None

def get_dependency_files_content(repo_name):
    """Fetches and concatenates content of common dependency files."""
    COMMON_DEPS = [
        "requirements.txt", "Pipfile", "pyproject.toml",
        "package.json", "yarn.lock", "pnpm-lock.yaml",
        "pom.xml", "build.gradle", "settings.gradle",
        "Gemfile", "Gemfile.lock",
        "Cargo.toml", "Cargo.lock",
        "go.mod", "go.sum",
        "composer.json", "composer.lock",
        "Dockerfile"
    ]
    content_parts = []
    for file_path in COMMON_DEPS:
        file_content = get_github_file_content(repo_name, file_path)
        if file_content:
            content_parts.append(f"--- {file_path} ---\n{file_content.strip()}")
    
    return "\n\n".join(content_parts) if content_parts else "N/A"

def classify(repo, context):

    prompt = f"""
Analyze the following GitHub repository data to identify its key technologies, libraries, and concepts.

**Analysis Priority:**
1. README content (Primary signal)
2. Project Structure (file names)
3. Dependency files
4. Repository description

**Repository Name:** {repo['name']}
**Primary Language:** {repo['language']}

**Repository Data:**
---
**README.md:**
{context.get('readme', 'N/A')}
---
**Project Structure (File List):**
{context.get('tree', 'N/A')}
---
**Dependency Files:**
{context.get('dependencies', 'N/A')}
---
**Description:**
{context.get('description', 'N/A')}
---

Your task is to generate a comma-separated list of the main technologies, frameworks, and concepts.

**Output format requirements:**
- A single line of text.
- Items are separated by commas.
- DO NOT include any introductory phrases, explanations, or markdown formatting.

Example: FastAPI, Docker, PyTorch, Computer Vision, LLM
"""

    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL,
            "messages":[{"role":"user","content":prompt}]
        }
    )

    try:
        r.raise_for_status() 
        response_json = r.json()

        if "choices" in response_json and response_json.get("choices"):
            return response_json["choices"][0]["message"]["content"].strip()
        else:
            print(f"Error: Unexpected API response structure for {repo['name']}:")
            print(response_json)
            return "Error: Invalid API response"
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error classifying {repo['name']}: {e}")
        print("API Response Text:", r.text)
        return "Error: API request failed"
    except json.JSONDecodeError:
        print(f"JSON Decode Error for {repo['name']}. Response was not valid JSON.")
        print("API Response Text:", r.text)
        return "Error: Invalid JSON response"

def main():

    with open(INPUT) as f:
        repos = json.load(f)

    results = {}

    MAX_README_CHARS = 24000
    MAX_TREE_CHARS = 8000
    MAX_DEPS_CHARS = 24000

    for repo in repos:

        readme_content = get_github_file_content(repo["name"], "README.md")
        tree_content = get_github_tree(repo["name"], repo.get("default_branch", "main"))
        deps_content = get_dependency_files_content(repo["name"])

        context = {
            "description": repo.get("description"),
            "readme": truncate_text(readme_content, MAX_README_CHARS),
            "tree": truncate_text(tree_content, MAX_TREE_CHARS),
            "dependencies": truncate_text(deps_content, MAX_DEPS_CHARS)
        }

        domain_tags = classify(repo, context)

        cleaned_tags = clean_llm_output(domain_tags)

        print(repo["name"], "→", cleaned_tags)

        results[repo["name"]] = cleaned_tags

    with open(OUTPUT, "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()