const DB_BASE = location.pathname.includes('/src/') ? '../db/' : 'db/';
const INDEX_URL = DB_BASE + 'index.json';

const state = {
  nodes: {},
  roots: [],
  filtered: null,
};

function buildTree(nodes) {
  const childrenMap = {};
  Object.keys(nodes).forEach((url) => (childrenMap[url] = []));
  Object.entries(nodes).forEach(([url, n]) => {
    (n.children || []).forEach((c) => {
      if (childrenMap[c]) childrenMap[c].push(url);
    });
  });

  const hasParent = new Set(Object.values(nodes).flatMap((n) => n.children || []));
  const roots = Object.keys(nodes).filter((u) => !hasParent.has(u));
  state.roots = roots;
}

function createNodeEntry(url, node, depth = 0) {
  const item = document.createElement('div');
  item.className = 'pl-' + Math.min(depth * 4, 64) + ' py-1';

  const btn = document.createElement('button');
  btn.className = 'text-left w-full hover:bg-gray-100 rounded px-2 py-1';
  btn.textContent = node.title || url;
  btn.onclick = () => openPreview(url, node);
  item.appendChild(btn);

  const kids = node.children || [];
  if (kids.length) {
    const container = document.createElement('div');
    kids.forEach((childUrl) => {
      const child = state.nodes[childUrl];
      if (child) container.appendChild(createNodeEntry(childUrl, child, depth + 1));
    });
    item.appendChild(container);
  }

  return item;
}

function renderTree(filter = '') {
  const tree = document.getElementById('treeContainer');
  tree.innerHTML = '';
  const match = (t) => (filter ? (t || '').toLowerCase().includes(filter.toLowerCase()) : true);

  const addSubtree = (url, node) => {
    if (match(node.title) || (node.children || []).some((c) => match(state.nodes[c]?.title))) {
      tree.appendChild(createNodeEntry(url, node, 0));
    }
  };

  state.roots.forEach((u) => {
    const n = state.nodes[u];
    if (n) addSubtree(u, n);
  });
}

function openPreview(url, node) {
  const iframe = document.getElementById('preview');
  iframe.src = DB_BASE + (node.local_path || '');
  const bc = document.getElementById('breadcrumb');
  bc.textContent = node.title ? node.title + ' — ' + url : url;
}

async function init() {
  try {
    const res = await fetch(INDEX_URL);
    if (!res.ok) throw new Error('index.json yüklenemedi: ' + res.status);
    const data = await res.json();
    state.nodes = data.nodes || {};
    buildTree(state.nodes);
    renderTree('');
  } catch (err) {
    console.error(err);
    const tree = document.getElementById('treeContainer');
    tree.innerHTML = '<div class="text-red-600 text-sm">Veri yüklenemedi: ' + String(err) + '</div>';
  }
}

document.getElementById('searchInput').addEventListener('input', (e) => {
  renderTree(e.target.value);
});

init();


