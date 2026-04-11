import os
import re
import json
from collections import defaultdict

def generate_category_heatmap():
    category_counts = defaultdict(int)
    category_to_files = defaultdict(list)
    special_entries = []
    
    files = [f for f in os.listdir('.') if f.endswith('.html') and f != 'index.html']
    
    for filename in files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = re.search(r'<div class="category">(.*?)</div>', content)
            if match:
                keywords = [k.strip().upper() for k in match.group(1).split(',')]
                for kw in keywords:
                    category_counts[kw] += 1
                    category_to_files[kw].append(filename)
            else:
                special_entries.append(filename)
        except:
            pass

    # CSS for Category Cloud
    category_css = """
    .category-cloud {
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        justify-content: center;
        margin-top: 4rem;
        padding: 0 1rem;
    }
    .category-item {
        transition: all 0.4s ease;
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
        color: var(--text-color);
        opacity: 0.6;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .category-item:hover {
        color: var(--accent-color);
        opacity: 1;
        transform: scale(1.1);
    }
    .entry-list {
        display: none;
        margin-top: 1rem;
        padding-left: 1rem;
        border-left: 1px solid var(--accent-color);
        width: 100%;
        text-align: left;
    }
    .category-wrapper {
        text-align: center;
        margin-bottom: 1rem;
    }
    .category-wrapper.active .entry-list {
        display: block;
    }
    .category-wrapper.active .category-item {
        color: var(--accent-color);
        opacity: 1;
    }
    """

    with open('style.css', 'a') as s:
        s.write(category_css)

    # Generate HTML
    html_parts = []
    html_parts.append('<div class="category-cloud">')
    
    # Sort categories by frequency or name
    sorted_categories = sorted(category_counts.keys())
    
    max_count = max(category_counts.values()) if category_counts else 1
    
    for cat in sorted_categories:
        count = category_counts[cat]
        # Calculate size based on frequency
        # Range from 0.7rem to 1.8rem
        size = 0.7 + (count / max_count) * 1.1
        opacity = 0.4 + (count / max_count) * 0.6
        
        html_parts.append(f'<div class="category-wrapper" id="wrap-{cat.replace(" ", "-")}">')
        html_parts.append(f'<a href="javascript:void(0)" class="category-item" onclick="toggleCategory(\'{cat.replace(" ", "-")}\')" style="font-size: {size:.2f}rem; opacity: {opacity:.2f}">{cat}</a>')
        
        html_parts.append('<div class="entry-list"><ul>')
        # Sort files in category descending (newest first based on JYYYYMMDD)
        for f in sorted(category_to_files[cat], reverse=True):
            title = f.replace('.html', '').upper()
            html_parts.append(f'<li><a href="{f}">{title}</a></li>')
        html_parts.append('</ul></div></div>')
        
    html_parts.append('</div>')

    # JavaScript for toggling
    js_toggle = """
function toggleCategory(catId) {
    const wrappers = document.querySelectorAll('.category-wrapper');
    const target = document.getElementById('wrap-' + catId);
    
    const isActive = target.classList.contains('active');
    
    wrappers.forEach(w => w.classList.remove('active'));
    
    if (!isActive) {
        target.classList.add('active');
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}
    """
    with open('script.js', 'a') as js:
        js.write(js_toggle)

    # Update index.html
    with open('index.html', 'r') as f:
        content = f.read()

    new_nav = f"""
            <nav>
                <div style="text-align: center;">
                    <a href="javascript:void(0)" onclick="goToRandomEntry()" style="letter-spacing: 5px;">A TOSS OF THE DICE</a>
                </div>
                {"".join(html_parts)}
            </nav>
    """
    
    pattern = re.compile(r'<nav>.*?</nav>', re.DOTALL)
    updated_content = pattern.sub(new_nav, content)
    
    with open('index.html', 'w') as f:
        f.write(updated_content)

if __name__ == "__main__":
    generate_category_heatmap()
