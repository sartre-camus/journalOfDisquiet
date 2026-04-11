import os
import json
import time
from bs4 import BeautifulSoup
import google.generativeai as genai

# Setup Gemini API (Make sure you set the GEMINI_API_KEY environment variable)
# export GEMINI_API_KEY="your_api_key_here"
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY environment variable not set.")
    exit(1)

genai.configure(api_key=api_key)
# Using gemini-1.5-flash for speed and cost efficiency
model = genai.GenerativeModel('gemini-1.5-flash')

# Load the list of entries
with open('entries.json', 'r') as f:
    all_entries = json.load(f)

# Determine which files need processing (skip the first 180 that were already done)
# We can check if a file already has the new template by looking for '<div class="category">'
files_to_process = []
for entry in all_entries:
    try:
        with open(entry, 'r', encoding='utf-8') as f:
            content = f.read()
            if '<div class="category">' not in content:
                files_to_process.append(entry)
    except FileNotFoundError:
        pass

print(f"Found {len(files_to_process)} files to process.")

def process_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract existing content. We'll try to find the main text block.
    # Older org-mode exports usually have a div with id="content"
    content_div = soup.find('div', id='content')
    if content_div:
        # Extract all paragraphs and verses
        paragraphs = content_div.find_all(['p', 'div'])
        raw_text = "\n\n".join([p.get_text() for p in paragraphs if p.name == 'p' or 'verse' in p.get('class', [])])
    else:
        # Fallback to body text
        raw_text = soup.body.get_text() if soup.body else ""

    if not raw_text.strip():
        print(f"Skipping {filename}: No content found.")
        return None

    # Construct the prompt for the LLM
    prompt = f"""
You are a noir-style editor for a "Journal of Disquiet".
Task 1: Read the following journal entry and fictionalize any real-world references (names, people, locations, events, specific modern technologies) to be evocative, slightly cryptic, and noir-ish (e.g., "India" -> "The Dusty South", "Company" -> "The Syndicate", "John" -> "The Passenger", "iPhone" -> "The Device").
Task 2: Assign 1 to 2 single-word keywords that capture the theme of the entry (e.g., Loneliness, Memory, Nature, Chaos, Mystery).
Task 3: Output the result strictly in this JSON format:
{{
  "keywords": "Keyword1, Keyword2",
  "fictionalized_html": "<p>Fictionalized paragraph 1...</p><p>Fictionalized paragraph 2...</p>"
}}

Important: Only output valid JSON. Do not use markdown code blocks like ```json.
Keep the HTML formatting simple, mostly <p> tags.

Entry Text:
{raw_text}
"""

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        # Clean up potential markdown formatting
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        result = json.loads(response_text)
        keywords = result.get('keywords', 'Mystery')
        fictionalized_content = result.get('fictionalized_html', f'<p>{raw_text}</p>')
        
        # Construct the new HTML
        title = filename.replace('.html', '').upper()
        new_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Journal of Disquiet</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div id="container">
        <header>
            <h1><a href="index.html">JOURNAL OF DISQUIET</a></h1>
        </header>

        <main>
            <h2 class="title">{title}</h2>
            <div class="category">{keywords}</div>
            {fictionalized_content}
        </main>

        <footer>
            <p>BACK TO THE <a href="index.html">VOID</a>. OR SEEK <a href="javascript:void(0)" onclick="goToRandomEntry()">RANDOM</a>.</p>
        </footer>
    </div>
    <script src="script.js"></script>
</body>
</html>"""

        # Write the new HTML back to the file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_html)
            
        print(f"Processed {filename} -> Keywords: {keywords}")
        return {filename: keywords}

    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return None

# Process files with a delay to avoid rate limits
category_mapping = {}
for filename in files_to_process:
    result = process_file(filename)
    if result:
        category_mapping.update(result)
    time.sleep(4)  # ~15 RPM limit safety

# Save the category mapping for updating the index later
with open('category_mapping.json', 'w') as f:
    json.dump(category_mapping, f, indent=2)

print("Batch processing complete!")
