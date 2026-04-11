import os
import json
import time
import google.generativeai as genai

# Setup Gemini API - export GEMINI_API_KEY="your_api_key_here"
# Run this script to process the remaining handwritten images automatically.
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Please set the GEMINI_API_KEY environment variable.")
    exit(1)

genai.configure(api_key=api_key)

generation_config = {
  "temperature": 0.3,
  "response_mime_type": "application/json",
}

system_instruction = """
You are an expert archivist transcribing handwritten journal entries for a noir, dystopian-styled 'Journal of Disquiet'.
Extract the text accurately. If there are dates, format them.
CRITICAL: Fictionalize all references to real names, persons, locations, companies, and specific events so they do not point to anything in reality. (e.g. 'G' becomes 'V', 'Linode' becomes 'Aether Servers', real cities become dystopian sectors).
Output a JSON array of entries. Each entry must have:
- "date": string, YYYYMMDD format (infer from text if possible, e.g., '19 June 2024' -> '20240619').
- "title": string, e.g., "JUNE 19, 2024".
- "categories": string, 2 comma-separated thematic categories (e.g., "LETHARGY, DETACHMENT").
- "paragraphs": array of strings, the fictionalized text broken into paragraphs.
"""

model = genai.GenerativeModel(
    model_name="models/gemini-flash-latest",
    generation_config=generation_config,
    system_instruction=system_instruction
)

handwritten_dir = "handwritten"
processed_log = "processed_handwritten.json"

if os.path.exists(processed_log):
    with open(processed_log, 'r') as f:
        processed_files = json.load(f)
else:
    processed_files = []

# Exclude the ones I just processed manually
to_ignore = ['20250414_094506.jpg', '20250414_094525.jpg', '20250414_094536.jpg', '20250414_094552.jpg', '20250414_094614.jpg']
for f_ignore in to_ignore:
    if f_ignore not in processed_files:
        processed_files.append(f_ignore)

files_to_process = [f for f in os.listdir(handwritten_dir) if f.endswith(('.jpg', '.pdf')) and f not in processed_files]

def create_html(date_str, title, category, paragraphs):
    filename = f"J{date_str}_handwritten.html"
    # Ensure unique filename
    counter = 1
    base_filename = filename
    while os.path.exists(base_filename):
        base_filename = f"J{date_str}_handwritten_{counter}.html"
        counter += 1
    
    html_content = f"""<!DOCTYPE html>
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
            <div class="category">{category}</div>
"""
    for p in paragraphs:
        html_content += f"            <p>{p}</p>\n"
        
    html_content += """        </main>

        <footer>
            <p>BACK TO THE <a href="index.html">VOID</a>. OR SEEK <a href="javascript:void(0)" onclick="goToRandomEntry()">RANDOM</a>.</p>
        </footer>
    </div>
    <script src="script.js"></script>
</body>
</html>"""
    
    with open(base_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return base_filename

print(f"Found {len(files_to_process)} handwritten files to process.")

new_html_files = []

for idx, file_name in enumerate(files_to_process):
    file_path = os.path.join(handwritten_dir, file_name)
    print(f"Processing {file_name} ({idx+1}/{len(files_to_process)})...")
    
    try:
        sample_file = genai.upload_file(path=file_path)
        response = model.generate_content([sample_file, "Extract, fictionalize, and categorize the journal entries in this document."])
        entries = json.loads(response.text)
        
        for entry in entries:
            html_file = create_html(entry['date'], entry['title'], entry['categories'], entry['paragraphs'])
            new_html_files.append(html_file)
            print(f"  Created {html_file}")
            
        processed_files.append(file_name)
        with open(processed_log, 'w') as f:
            json.dump(processed_files, f, indent=2)
            
        # Optional: delete the file from genai to free space
        genai.delete_file(sample_file.name)
        
        time.sleep(5) # rate limit
        
    except Exception as e:
        print(f"Error processing {file_name}: {e}")

if new_html_files:
    # Update entries.json and final_entries.json
    for json_file in ['entries.json', 'final_entries.json']:
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                data = json.load(f)
            data.extend(new_html_files)
            data = sorted(list(set(data))) # Deduplicate and sort
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=2)
                
    # Update index
    os.system("python3 generate_rhizome_index.py")
    print(f"Successfully added {len(new_html_files)} new entries and updated the index.")
