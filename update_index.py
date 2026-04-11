import json
import os
from collections import defaultdict

# Load the previously processed mappings (from previous batches and the new script)
# For the newly generated ones
try:
    with open('category_mapping.json', 'r') as f:
        new_mappings = json.load(f)
except FileNotFoundError:
    new_mappings = {}

# Assume we have a complete list of entries and we want to categorize them
with open('entries.json', 'r') as f:
    all_entries = json.load(f)

# Build a mapping from reading the files directly, since the LLM script might not have everything
# or we just read the DOM of the files that are already processed
categorized_entries = defaultdict(list)
uncategorized = []

for entry in all_entries:
    try:
        with open(entry, 'r', encoding='utf-8') as f:
            content = f.read()
            
        import re
        match = re.search(r'<div class="category">(.*?)</div>', content)
        if match:
            keywords = match.group(1).split(',')
            # Just take the first keyword for grouping to keep it simple
            primary_keyword = keywords[0].strip().upper()
            categorized_entries[primary_keyword].append(entry)
        else:
            uncategorized.append(entry)
    except Exception as e:
        print(f"Error reading {entry}: {e}")

# Build the new index.html content
html_start = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Journal of Disquiet</title>
    <link rel="stylesheet" href="style.css">
    <script src="script.js"></script>
</head>
<body>
    <div id="container">
        <header>
            <h1>JOURNAL OF DISQUIET</h1>
        </header>

        <main>
            <nav>
                <ul>
                    <li><a href="javascript:void(0)" onclick="goToRandomEntry()">A TOSS OF THE DICE</a></li>
                </ul>
                <hr style="border-color: #333; margin: 2rem 0;">
"""

html_end = """
            </nav>
        </main>

        <footer>
            <p>&copy; 2026. THE PAGES REMAIN UNTURNED.</p>
        </footer>
    </div>
</body>
</html>
"""

category_blocks = []
for category in sorted(categorized_entries.keys()):
    block = f"                <h3 style='color: var(--accent-color); font-size: 0.9rem; margin-top: 2rem;'>{category}</h3>\n                <ul>\n"
    for entry in sorted(categorized_entries[category], reverse=True):
        title = entry.replace('.html', '').upper()
        block += f"                    <li><a href=\"{entry}\">{title}</a></li>\n"
    block += "                </ul>\n"
    category_blocks.append(block)

if uncategorized:
    block = f"                <h3 style='color: var(--accent-color); font-size: 0.9rem; margin-top: 2rem;'>THE VOID (UNPROCESSED)</h3>\n                <ul>\n"
    for entry in sorted(uncategorized, reverse=True):
        title = entry.replace('.html', '').upper()
        block += f"                    <li><a href=\"{entry}\">{title}</a></li>\n"
    block += "                </ul>\n"
    category_blocks.append(block)

final_html = html_start + "".join(category_blocks) + html_end

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print(f"Updated index.html. {len(categorized_entries)} categories found.")
