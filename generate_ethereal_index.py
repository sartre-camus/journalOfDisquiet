import os
import re
import random
from collections import defaultdict

def generate_ethereal_index():
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
                    category_to_files[kw].append(filename)
            else:
                special_entries.append(filename)
        except:
            pass

    # CSS for Ethereal Cloud
    ethereal_css = """
    .ethereal-cloud {
        display: flex;
        flex-wrap: wrap;
        gap: 2rem;
        justify-content: center;
        align-items: center;
        margin-top: 6rem;
        padding: 0 2rem;
        perspective: 1000px;
    }
    .memory-fragment {
        transition: all 1s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        text-decoration: none;
        display: inline-block;
        color: var(--text-color);
        text-transform: uppercase;
        letter-spacing: 4px;
        position: relative;
        filter: blur(1px);
    }
    .memory-fragment:hover {
        color: var(--accent-color);
        filter: blur(0px);
        transform: translateZ(20px) scale(1.1);
        opacity: 1 !important;
    }
    .fragment-list {
        display: none;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(13, 13, 13, 0.95);
        padding: 3rem;
        border: 1px solid #222;
        max-height: 70vh;
        overflow-y: auto;
        z-index: 1000;
        width: 80%;
        max-width: 500px;
        box-shadow: 0 0 100px rgba(0,0,0,1);
    }
    .fragment-list ul {
        list-style: none;
        padding: 0;
    }
    .fragment-list li {
        margin-bottom: 1rem;
        border-bottom: 1px solid #1a1a1a;
        padding-bottom: 0.5rem;
    }
    .fragment-list a {
        font-size: 0.8rem;
        color: var(--text-color);
    }
    .overlay {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        z-index: 999;
        backdrop-filter: blur(5px);
    }
    .close-overlay {
        position: absolute;
        top: 1rem;
        right: 1rem;
        color: var(--accent-color);
        cursor: pointer;
        font-size: 1.5rem;
    }
    """

    with open('style.css', 'a') as s:
        s.write(ethereal_css)

    # Generate HTML
    html_parts = []
    html_parts.append('<div class="ethereal-cloud">')
    
    categories = list(category_to_files.keys())
    random.shuffle(categories) # Break the order
    
    for cat in categories:
        # Random vividness (opacity and size)
        # Some memories are sharp, some are fading
        vividness = random.uniform(0.1, 0.9)
        size = random.uniform(0.6, 1.6)
        blur = (1.0 - vividness) * 3
        
        html_parts.append(f'<div class="fragment-wrapper">')
        html_parts.append(f'<a href="javascript:void(0)" class="memory-fragment" onclick="openMemory(\'{cat.replace(" ", "-")}\')" style="font-size: {size:.2f}rem; opacity: {vividness:.2f}; filter: blur({blur:.1f}px)">{cat}</a>')
        
        html_parts.append(f'<div class="fragment-list" id="mem-{cat.replace(" ", "-")}">')
        html_parts.append(f'<span class="close-overlay" onclick="closeMemory()">&times;</span>')
        html_parts.append(f'<h3 class="title" style="font-size: 1rem; margin-bottom: 2rem;">RECALLING: {cat}</h3><ul>')
        
        # Shuffle entries within category - time is an illusion
        entries_in_cat = category_to_files[cat]
        random.shuffle(entries_in_cat)
        
        for f in entries_in_cat:
            # We don't use the date-based title, just a generic "DISPATCH" or "FRAGMENT"
            # or we keep the filename but strip the 'J' and '.html'
            title = f.replace('.html', '').replace('J', 'FRAGMENT ')
            if 'absurdity' in f or 'pain' in f:
                title = f.replace('.html', '').upper()
            html_parts.append(f'<li><a href="{f}">{title}</a></li>')
        html_parts.append('</ul></div></div>')
        
    html_parts.append('</div>')
    html_parts.append('<div class="overlay" id="memory-overlay" onclick="closeMemory()"></div>')

    # JavaScript for Modal logic
    js_ethereal = """
function openMemory(catId) {
    document.getElementById('memory-overlay').style.display = 'block';
    document.getElementById('mem-' + catId).style.display = 'block';
}

function closeMemory() {
    document.getElementById('memory-overlay').style.display = 'none';
    document.querySelectorAll('.fragment-list').forEach(l => l.style.display = 'none');
}
    """
    with open('script.js', 'a') as js:
        js.write(js_ethereal)

    # Update index.html
    with open('index.html', 'r') as f:
        content = f.read()

    new_nav = f"""
            <nav>
                <div style="text-align: center; margin-bottom: 2rem;">
                    <a href="javascript:void(0)" onclick="goToRandomEntry()" style="letter-spacing: 8px; font-size: 0.8rem; opacity: 0.5;">A TOSS OF THE DICE</a>
                </div>
                {"".join(html_parts)}
            </nav>
    """
    
    pattern = re.compile(r'<nav>.*?</nav>', re.DOTALL)
    updated_content = pattern.sub(new_nav, content)
    
    with open('index.html', 'w') as f:
        f.write(updated_content)

if __name__ == "__main__":
    generate_ethereal_index()
