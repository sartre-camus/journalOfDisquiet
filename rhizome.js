
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
    