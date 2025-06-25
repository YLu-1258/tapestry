
import os
import argparse
import random
import json
import time
from datetime import datetime
from mistralai import Mistral

# Initialize Mistral client
api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise EnvironmentError("Please set the MISTRAL_API_KEY environment variable.")
client = Mistral(api_key=api_key)
model = "mistral-large-latest"

TAG_POOL = [
    "python", "ai", "obsidian", "algorithms", "physics",
    "demo", "vault", "note", "example", "tutorial",
    "math", "c++", "javascript", "web", "data",
    "machine-learning", "deep-learning", "nlp", "mlops",
    "project", "research", "python", "rust", "brainstorm"
]

CACHE_SUBFOLDERS = ["projects", "journal", "ideas"]


def generate_ai_note(tags: list) -> dict:
    """
    Use Mistral to generate a title and a short paragraph based on the given tags.
    Returns a dict with 'title' and 'content'.
    Handles rate limit errors by waiting 60 seconds and retrying.
    """
    prompt = (
        f"Generate a JSON object with keys 'title' and 'content'. "
        f"The title should be a concise heading for an Obsidian note covering these tags: {', '.join(tags)}. "
        f"The content should be a short paragraph (1-2 sentences) relevant to those tags."
    )

    while True:
        try:
            response = client.chat.complete(
                model=model,
                messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant that generates concise and relevant notes for Obsidian vaults. It is imperative and very important that you return a JSON object formatted with a 'title' and 'content' key. The content should be a short paragraph (1-2 sentences) relevant to the tags provided. Do not include any additional text or explanations outside of the JSON object. Do not include code block formattings either, I don't want any backticks, just raw, unfiltered, json.",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
                ]
            )
            text = response.choices[0].message.content.strip()
            break

        except Exception as e:
            err = str(e).lower()
            if "rate limit" in err or "too many requests" in err:
                print("🔄 Rate limit hit – sleeping for 60s before retrying...", file=sys.stderr)
                time.sleep(60)
            else:
                # Non-rate-limit errors bubble up
                raise
            
    print("Mistral output: ", text)

    try:
        if not text.startswith("{"):
            text = text[text.find("{"):]
        data = json.loads(text)
    except Exception:
        data = {
            "title": " / ".join(tags).title(),
            "content": f"An overview note covering: {', '.join(tags)}."
        }
    return data

def create_note(path: str, tags: list):
    date_str = datetime.now().isoformat()
    ai_note = generate_ai_note(tags)
    title = ai_note.get("title", "Untitled")
    content = ai_note.get("content", "")

    # Write markdown with YAML front-matter and generated content
    with open(path, "w", encoding="utf8") as f:
        f.write("---\n")
        f.write(f"title: '{title}'\n")
        f.write(f"date: {date_str}\n")
        f.write("tags:\n")
        for tag in tags:
            f.write(f"  - {tag}\n")
        f.write("---\n\n")

        # Write content
        f.write(f"{content}\n")


def generate_vault(vault_dir: str, num_notes: int, max_tags: int):
    os.makedirs(vault_dir, exist_ok=True)

    for sub in CACHE_SUBFOLDERS:
        os.makedirs(os.path.join(vault_dir, sub), exist_ok=True)

    for i in range(1, num_notes + 1):
        # Randomly pick a location: root or one of the subfolders
        folder = random.choice([vault_dir] + [os.path.join(vault_dir, s) for s in CACHE_SUBFOLDERS])
        filename = f"note_{i}.md"
        path = os.path.join(folder, filename)

        # Generate title and random tags
        num_tags = random.randint(1, max_tags)
        tags = random.sample(TAG_POOL, num_tags)
        create_note(path, tags)

    print(f"Generated {num_notes} notes (across {len(CACHE_SUBFOLDERS)+1} folders) in '{vault_dir}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a test Obsidian vault with sample markdown notes."
    )
    parser.add_argument(
        "--vault", default="./test_vault", help="Path to create the vault folder"
    )
    parser.add_argument(
        "--notes", type=int, default=10, help="Number of markdown notes to generate"
    )
    parser.add_argument(
        "--max-tags", type=int, default=3, help="Maximum tags per note"
    )
    args = parser.parse_args()

    generate_vault(args.vault, args.notes, args.max_tags)
