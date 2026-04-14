import os
import re
import json
from collections import defaultdict
from datetime import datetime

def generate_heatmap():
    # Group entries by year and date
    # Format: entries[year][date] = filename
    entries = defaultdict(dict)
    special_entries = []
    
    files = [f for f in os.listdir('.') if f.endswith('.html') and f != 'index.html']
    
    for f in files:
        # Match JYYYYMMDD.html
        match = re.match(r'J(\d{4})(\d{2})(\d{2})\.html', f)
        if match:
            year, month, day = match.groups()
            date_str = f"{year}-{month}-{day}"
            entries[year][date_str] = f
        else:
            special_entries.append(f)

    # Update index.html
    html_parts = []
    html_parts.append('<div class="heatmap-container">')
    
    for year in sorted(entries.keys(), reverse=True):
        html_parts.append(f'<div class="year-block"><div class="year-title">{year}</div><div class="grid">')
        
        # Simple grid: 365/366 days
        # To keep it simple and compact, we'll just render the active days
        # Real GitHub heatmaps are complex (aligned by day of week).
        # Here we'll do a simple "Disquiet Pulse" - a sequence of dots for the year.
        
        for month in range(1, 13):
            for day in range(1, 32):
                date_str = f"{year}-{month:02d}-{day:02d}"
                if date_str in entries[year]:
                    filename = entries[year][date_str]
                    html_parts.append(f'<a href="{filename}" class="day active"><span class="tooltip">{date_str}</span></a>')
                else:
                    # We only show a faint dot for inactive days to keep it tight
                    # Or skip them to save space. Let's show them for the "pulse" look.
                    pass
        
        html_parts.append('</div></div>')
    
    html_parts.append('</div>')
    
    # Add Special entries
    html_parts.append('<div class="special-links">')
    for f in special_entries:
        title = f.replace('.html', '').upper()
        html_parts.append(f'<a href="{f}">{title}</a>')
    html_parts.append('</div>')

    # Update index.html
    with open('index.html', 'r') as f:
        content = f.read()

    # Replace the navigation content with the heatmap
    new_nav = f"""
            <nav>
                <ul>
                    <li><a href="javascript:void(0)" onclick="goToRandomEntry()">A TOSS OF THE DICE</a></li>
                </ul>
                <hr style="border-color: #333; margin: 2rem 0;">
                {"".join(html_parts)}
            </nav>
    """
    
    # Use regex to find <nav>...</nav> and replace it
    pattern = re.compile(r'<nav>.*?</nav>', re.DOTALL)
    updated_content = pattern.sub(new_nav, content)
    
    with open('index.html', 'w') as f:
        f.write(updated_content)

if __name__ == "__main__":
    generate_heatmap()
