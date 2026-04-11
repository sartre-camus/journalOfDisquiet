import os
import re
import random
import json
from collections import defaultdict

def generate_rhizome_index():
    category_to_files = defaultdict(list)
    file_to_categories = defaultdict(list)
    
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
                    file_to_categories[filename].append(kw)
        except:
            pass

    # Build connections: categories that share at least one file
    connections = []
    categories = list(category_to_files.keys())
    for i in range(len(categories)):
        for j in range(i + 1, len(categories)):
            shared = set(category_to_files[categories[i]]) & set(category_to_files[categories[j]])
            if shared:
                connections.append((categories[i], categories[j]))

    # CSS for the Rhizome
    rhizome_css = """
    body {
        overflow: hidden; /* Constellation is the whole view */
    }
    #rhizome-canvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;
        background: #0d0d0d;
    }
    .constellation-container {
        position: relative;
        width: 100vw;
        height: 100vh;
        perspective: 1200px;
    }
    .thought-node {
        position: absolute;
        cursor: pointer;
        text-transform: uppercase;
        letter-spacing: 5px;
        color: var(--text-color);
        transition: color 0.5s, transform 0.5s, filter 0.5s;
        white-space: nowrap;
        user-select: none;
        font-family: var(--font-mono);
    }
    .thought-node:hover {
        color: var(--accent-color);
        filter: blur(0px) !important;
        opacity: 1 !important;
        z-index: 100;
    }
    .node-label {
        pointer-events: none;
    }
    #ui-layer {
        position: fixed;
        bottom: 2rem;
        width: 100%;
        text-align: center;
        pointer-events: none;
    }
    #ui-layer a {
        pointer-events: auto;
        opacity: 0.3;
        font-size: 0.7rem;
        letter-spacing: 10px;
    }
    """

    with open('style.css', 'a') as s:
        s.write(rhizome_css)

    # Prepare data for JS
    # We'll pass the categories and their connections to a JS engine that handles the drift and lines
    nodes = []
    for cat in categories:
        nodes.append({
            "id": cat,
            "weight": len(category_to_files[cat]),
            "files": category_to_files[cat]
        })

    # Update index.html to be a clean slate for the rhizome
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Journal of Disquiet</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <canvas id="rhizome-canvas"></canvas>
    <div class="constellation-container" id="constellation"></div>
    
    <div id="ui-layer">
        <a href="javascript:void(0)" onclick="goToRandomEntry()">A TOSS OF THE DICE</a>
    </div>

    <script>
        const nodesData = {json.dumps(nodes)};
        const connectionsData = {json.dumps(connections)};
    </script>
    <script src="script.js"></script>
    <script src="rhizome.js"></script>
</body>
</html>"""

    with open('index.html', 'w') as f:
        f.write(index_html)

    # Create the JS engine for the Rhizome
    rhizome_js = """
const constellation = document.getElementById('constellation');
const canvas = document.getElementById('rhizome-canvas');
const ctx = canvas.getContext('2d');

let width, height;
let nodes = [];

function init() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;

    nodes = nodesData.map(data => ({
        ...data,
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.2,
        vy: (Math.random() - 0.5) * 0.2,
        vividness: 0.1 + Math.random() * 0.8,
        size: 0.6 + (data.weight / 10) + Math.random() * 0.5,
        el: null
    }));

    nodes.forEach(node => {
        const div = document.createElement('div');
        div.className = 'thought-node';
        div.innerText = node.id;
        div.style.fontSize = node.size + 'rem';
        div.style.opacity = node.vividness;
        div.style.filter = `blur(${(1 - node.vividness) * 4}px)`;
        
        div.onclick = () => {
            const randomFile = node.files[Math.floor(Math.random() * node.files.length)];
            window.location.href = randomFile;
        };

        constellation.appendChild(div);
        node.el = div;
    });
}

function update() {
    ctx.clearRect(0, 0, width, height);
    ctx.strokeStyle = 'rgba(178, 34, 34, 0.15)'; // Faint Ribbon Red
    ctx.lineWidth = 0.5;

    // Draw connections
    connectionsData.forEach(conn => {
        const n1 = nodes.find(n => n.id === conn[0]);
        const n2 = nodes.find(n => n.id === conn[1]);
        if (n1 && n2) {
            ctx.beginPath();
            ctx.moveTo(n1.x, n1.y);
            ctx.lineTo(n2.x, n2.y);
            ctx.stroke();
        }
    });

    // Move nodes
    nodes.forEach(node => {
        node.x += node.vx;
        node.y += node.vy;

        // Bounce off edges
        if (node.x < 0 || node.x > width) node.vx *= -1;
        if (node.y < 0 || node.y > height) node.vy *= -1;

        node.el.style.left = node.x + 'px';
        node.el.style.top = node.y + 'px';
        node.el.style.transform = `translate(-50%, -50%)`;
    });

    requestAnimationFrame(update);
}

window.addEventListener('resize', () => {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
});

init();
update();
    """
    with open('rhizome.js', 'w') as f:
        f.write(rhizome_js)

if __name__ == "__main__":
    generate_rhizome_index()
