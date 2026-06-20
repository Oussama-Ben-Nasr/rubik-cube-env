import * as THREE from "three";
import { TrackballControls } from "https://unpkg.com/three@0.179.1/examples/jsm/controls/TrackballControls.js";
import { initMoveHistory, syncHistoryDisplay, initSolver } from '/static/solver.js?v13';

const SIDEBAR_W = 220;
const INDEX_COLORS = [
    0xffffff, // 0  U  white
    0x00cc44, // 1  F  green
    0xffdd00, // 2  D  yellow
    0xff8800, // 3  L  orange
    0x1144ff, // 4  B  blue
    0xee1111, // 5  R  red
];

const DARK_BG = 0x0d1117;
const LIGHT_BG = 0xf0ece4;

let currentLeaderboardFilter = 'all';

const CUBIE_BODY_COLOR = 0x111111;
const STICKER_OFFSET = 0.501;
const STICKER_SIZE = 0.85;
const ANIM_DURATION_MS = 280;
const loadingOverlay =
    document.getElementById("loading-overlay");

// Action → { axis, layerValue, direction, angleDelta }
// axis: 0=X,1=Y,2=Z   layerValue: which slice (-1|0|1)
// angleDelta: full rotation in radians (±π/2)
const ACTION_META = [
    { axis: 1, layer: 1, angle: Math.PI / 2 },  //  0  U
    { axis: 1, layer: 1, angle: -Math.PI / 2 },  //  1  U'
    { axis: 1, layer: -1, angle: -Math.PI / 2 },  //  2  D
    { axis: 1, layer: -1, angle: Math.PI / 2 },  //  3  D'
    { axis: 2, layer: 1, angle: Math.PI / 2 },  //  4  F
    { axis: 2, layer: 1, angle: -Math.PI / 2 },  //  5  F'
    { axis: 2, layer: -1, angle: -Math.PI / 2 },  //  6  B
    { axis: 2, layer: -1, angle: Math.PI / 2 },  //  7  B'
    { axis: 0, layer: -1, angle: -Math.PI / 2 },  //  8  L
    { axis: 0, layer: -1, angle: Math.PI / 2 },  //  9  L'
    { axis: 0, layer: 1, angle: Math.PI / 2 },  // 10  R
    { axis: 0, layer: 1, angle: -Math.PI / 2 },  // 11  R'
];

const AXES = [
    new THREE.Vector3(1, 0, 0),
    new THREE.Vector3(0, 1, 0),
    new THREE.Vector3(0, 0, 1),
];
const INITIAL_CAMERA_POSITION = new THREE.Vector3(6, 6, 6);
const INITIAL_TARGET = new THREE.Vector3(0, 0, 0);


let scene, camera, renderer, controls;
let cubieGroup = new THREE.Group();
let animating = false;
document.body.classList.remove("animating");
let nickname = localStorage.getItem("rubiks_nickname") || "";
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

const FACE_TO_MOVE = {
    U: [0, 1],   // U, U'
    D: [2, 3],   // D, D'
    F: [4, 5],   // F, F'
    B: [6, 7],   // B, B'
    L: [8, 9],   // L, L'
    R: [10, 11], // R, R'
};
const moveHistory = [];
const redoHistory = [];
const snapshots = [];
let currentSnapshotId = null;
let isCompeting = false;

window.setCompeting = (val) => {
    isCompeting = val;
    document.body.classList.toggle("competing", val);
 
    // Snapshot buttons
    const snapshotBtn = document.getElementById("snapshot-btn");
    const createBtn   = document.getElementById("snapshot-create-btn");
    if (snapshotBtn) { snapshotBtn.disabled = val; snapshotBtn.title = val ? "Disabled during compete" : "Snapshots"; }
    if (createBtn)   { createBtn.disabled   = val; }
 
    // Action buttons — solve/undo/redo locked during compete; reset always allowed
    ["solve-btn", "btn-undo", "btn-redo"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.disabled = val;
    });
};

const INVERSE_MOVE = {
    0: 1, 1: 0,
    2: 3, 3: 2,
    4: 5, 5: 4,
    6: 7, 7: 6,
    8: 9, 9: 8,
    10: 11, 11: 10,
};

init();
initMoveHistory(moveHistory);
initSolver();
initSnapshotUI();

const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'light') {
    document.body.classList.add('light');
    scene.background = new THREE.Color(0xe8e8e8);
    document.getElementById('theme-toggle').textContent = '🌙 dark';
}
await loadAndRender();
function askNickname() {
    return new Promise((resolve) => {
        const modal = document.getElementById('nickname-modal');
        const input = document.getElementById('nickname-input');
        const ok = document.getElementById('nickname-ok');
        const cancel = document.getElementById('nickname-cancel');

        input.value = '';
        modal.style.display = 'flex';
        setTimeout(() => input.focus(), 50);

        const finish = (val) => {
            modal.style.display = 'none';
            ok.removeEventListener('click', onOk);
            cancel.removeEventListener('click', onCancel);
            input.removeEventListener('keydown', onKey);
            resolve(val);
        };
        const onOk = () => finish(input.value.trim() || 'Anonymous');
        const onCancel = () => finish(null);
        const onKey = (e) => { if (e.key === 'Enter') onOk(); if (e.key === 'Escape') onCancel(); };

        ok.addEventListener('click', onOk);
        cancel.addEventListener('click', onCancel);
        input.addEventListener('keydown', onKey);
    });
}
function showNicknameTag(name) {
    let tag = document.getElementById('nickname-tag');
    if (!tag) {
        tag = document.createElement('div');
        tag.id = 'nickname-tag';
        document.body.appendChild(tag);
    }
    tag.textContent = name;
}

function getWinMessage(timeSeconds, moves) {
    const mins = String(Math.floor(timeSeconds / 60)).padStart(2, '0');
    const secs = String(timeSeconds % 60).padStart(2, '0');
    return `${mins}:${secs} · ${moves} moves\nSaved to leaderboard`;
}

if (!nickname) {
    nickname = await askNickname();;
    localStorage.setItem(
        "rubiks_nickname",
        nickname
    );
}
if (nickname) showNicknameTag(nickname);

window.move = async (actionId) => {
    if (animating) return;

    const meta = ACTION_META[actionId];
    if (!meta) return;

    animating = true;
    document.body.classList.add("animating");

    await animateLayer(meta);

    await fetch(`/move/${actionId}`, { method: "POST" });

    const state = await fetch("/cube").then(r => r.json());
    const status = await fetch("/status").then(r => r.json());

    if (status.is_competing && status.solved) {
        const solveMs =
            new Date(status.solve_time) -
            new Date(status.start_time);
        lastSolve = {
            nickname,
            solveMs,
            moves: status.real_moves_count,
        };
        document.getElementById("btn-share").disabled = false;
        document.getElementById("share-menu").disabled = false;

        await fetch("/solve", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                nickname,
                solve_time_ms: solveMs,
                moves: status.real_moves_count,
            }),
        });
        await refreshLeaderboard();

        clearInterval(timerInterval);
        const modal = document.getElementById('win-modal');
        document.getElementById('win-message').textContent =
            getWinMessage(Math.round(solveMs / 1000), status.real_moves_count);
        document.getElementById('btn-share').disabled = false;
        modal.classList.add('visible');
        const winOk = document.getElementById('win-ok');
        const closeWin = () => { modal.classList.remove('visible'); winOk.removeEventListener('click', closeWin); };
        winOk.addEventListener('click', closeWin);
        await fetch("finished", { method: "POST" });
    }
    renderCube(state);

    animating = false;
    document.body.classList.remove("animating");
};

window.reset = async () => {
    if (animating) return;
    await fetch(`/reset`, { method: "POST" });
    const state = await fetch("/cube").then(r => r.json());
    renderCube(state);
    const status = await fetch("/status").then(r => r.json());
    if (!status.is_competing) {
        document.getElementById('timer-display').textContent = `--:--:--`;
        if (timerInterval) clearInterval(timerInterval);
    }
    await animateCameraReset();
    moveHistory.length = 0;
    redoHistory.length = 0;
    syncHistoryDisplay(moveHistory);
};


window.addEventListener('resize', () => {
    renderer.setSize(window.innerWidth - SIDEBAR_W, window.innerHeight);
    camera.aspect = (window.innerWidth - SIDEBAR_W) / window.innerHeight;
    camera.updateProjectionMatrix();
});
function init() {
    scene = new THREE.Scene();
    const savedTheme = localStorage.getItem('theme');
    scene.background = new THREE.Color(savedTheme === 'light' ? LIGHT_BG : DARK_BG);

    camera = new THREE.PerspectiveCamera(60, (window.innerWidth - SIDEBAR_W) / window.innerHeight, 0.1, 1000);
    camera.position.copy(INITIAL_CAMERA_POSITION);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth - SIDEBAR_W, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    controls = new TrackballControls(
        camera,
        renderer.domElement
    );
    controls.rotateSpeed = 5;
    controls.zoomSpeed = 2;
    controls.panSpeed = 1;


    scene.add(new THREE.AmbientLight(0xffffff, 0.9));
    const dir = new THREE.DirectionalLight(0xffffff, 1.2);
    dir.position.set(5, 10, 5);
    scene.add(dir);

    scene.add(cubieGroup);
    renderer.domElement.addEventListener(
        "contextmenu",
        (e) => e.preventDefault()
    );

    renderer.domElement.addEventListener(
        "pointerdown",
        onCubePointerDown
    );

    window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    renderLoop();
}
function getMouseNDC(event) {
    const rect = renderer.domElement.getBoundingClientRect();
    return {
        x: ((event.clientX - rect.left) / rect.width) * 2 - 1,
        y: -((event.clientY - rect.top) / rect.height) * 2 + 1,
    };
}
async function onCubePointerDown(event) {
    if (animating) return;

    const ndc = getMouseNDC(event);
    mouse.x = ndc.x;
    mouse.y = ndc.y;

    raycaster.setFromCamera(mouse, camera);

    const intersections = raycaster.intersectObjects(
        cubieGroup.children,
        true
    );

    if (!intersections.length) return;

    const hit = intersections[0].object;

    const faceName = hit.userData.faceName;

    if (!faceName) return;

    const isRightClick = event.button === 2;

    const moveId =
        FACE_TO_MOVE[faceName][isRightClick ? 1 : 0];

    await window.doMove(moveId);
}

function renderLoop() {
    requestAnimationFrame(renderLoop);
    controls.update();
    renderer.render(scene, camera);
}


function clearScene() {
    scene.remove(cubieGroup);
    cubieGroup = new THREE.Group();
    scene.add(cubieGroup);
}

function createBody() {
    const geo = new THREE.BoxGeometry(0.95, 0.95, 0.95);
    const mat = new THREE.MeshStandardMaterial({ color: CUBIE_BODY_COLOR, roughness: 0.8 });
    return new THREE.Mesh(geo, mat);
}

function createSticker(color, position, rotation, faceName) {
    const geo = new THREE.PlaneGeometry(STICKER_SIZE, STICKER_SIZE);
    const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.5, metalness: 0.1 });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.copy(position);
    mesh.rotation.set(rotation.x, rotation.y, rotation.z);
    mesh.userData.faceName = faceName;

    if (faceName) {
        const label = createFaceLabel(faceName);

        mesh.userData.label = label;
    }

    return mesh;
}

function createFaceLabel(text) {
    const canvas = document.createElement("canvas");
    canvas.width = 128;
    canvas.height = 128;

    const ctx = canvas.getContext("2d");

    ctx.fillStyle = "black";
    ctx.font = "bold 96px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(text, 64, 64);

    const texture = new THREE.CanvasTexture(canvas);

    return new THREE.Mesh(
        new THREE.PlaneGeometry(0.45, 0.45),
        new THREE.MeshBasicMaterial({
            map: texture,
            transparent: true,
        })
    );
}

function createCubie({ x, y, z, colors }) {
    const group = new THREE.Group();
    group.position.set(x, y, z);

    group.add(createBody());

    const o = STICKER_OFFSET;
    const FACE_DEFS = [
        { face: "U", pos: new THREE.Vector3(0, o, 0), rot: new THREE.Euler(-Math.PI / 2, 0, 0) },
        { face: "D", pos: new THREE.Vector3(0, -o, 0), rot: new THREE.Euler(Math.PI / 2, 0, 0) },
        { face: "F", pos: new THREE.Vector3(0, 0, o), rot: new THREE.Euler(0, 0, 0) },
        { face: "B", pos: new THREE.Vector3(0, 0, -o), rot: new THREE.Euler(0, Math.PI, 0) },
        { face: "L", pos: new THREE.Vector3(-o, 0, 0), rot: new THREE.Euler(0, -Math.PI / 2, 0) },
        { face: "R", pos: new THREE.Vector3(o, 0, 0), rot: new THREE.Euler(0, Math.PI / 2, 0) },
    ];

    for (const { face, pos, rot } of FACE_DEFS) {
        if (colors[face] !== undefined) {
            group.add(
                createSticker(
                    INDEX_COLORS[colors[face]],
                    pos,
                    rot,
                    face
                )
            );
        }
    }

    const isCenter =
        Math.abs(x) + Math.abs(y) + Math.abs(z) === 1;

    if (isCenter) {
        for (const child of group.children) {
            if (
                child.userData?.faceName &&
                child.userData?.label
            ) {
                const label = child.userData.label;

                label.position.set(0, 0, 0.01);
                label.rotation.set(0, 0, 0);

                child.add(label);
            }
        }
    }

    return group;
}

function renderCube(state) {
    clearScene();
    for (const cubie of state) {
        cubieGroup.add(createCubie(cubie));
    }
}


function animateLayer(meta) {
    return new Promise(resolve => {
        const axisVec = AXES[meta.axis];
        const axisKey = ["x", "y", "z"][meta.axis];

        const layerMeshes = cubieGroup.children.filter(child => {
            return Math.round(child.position[axisKey]) === meta.layer;
        });

        const pivot = new THREE.Group();
        scene.add(pivot);
        for (const mesh of layerMeshes) {
            cubieGroup.remove(mesh);
            pivot.add(mesh);
        }

        const startTime = performance.now();
        const totalAngle = meta.angle;

        function tick() {
            const elapsed = performance.now() - startTime;
            const t = Math.min(elapsed / ANIM_DURATION_MS, 1);
            const eased = easeInOut(t);

            const currentAngle = totalAngle * eased;
            pivot.setRotationFromAxisAngle(axisVec, currentAngle);

            if (t < 1) {
                requestAnimationFrame(tick);
            } else {
                pivot.updateMatrixWorld();
                for (const mesh of [...pivot.children]) {
                    pivot.remove(mesh);
                    mesh.applyMatrix4(pivot.matrix);
                    cubieGroup.add(mesh);
                }
                scene.remove(pivot);
                resolve();
            }
        }

        requestAnimationFrame(tick);
    });
}

function easeInOut(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}


async function loadAndRender() {
    const state = await fetch("/cube").then(r => r.json());
    renderCube(state);
    updateUndoRedoButtons();
    await refreshLeaderboard();
    requestAnimationFrame(() => {
        loadingOverlay?.classList.add("hidden");
    });
}

let _count = 0;
const countEl = document.getElementById('count');

window.incrementCount = () => { countEl.textContent = ++_count; };
window.resetCount = () => { _count = 0; countEl.textContent = 0; };

window.doScramble = async () => {
    if (document.body.classList.contains('animating')) return;
    if (!nickname) {
        nickname = await askNickname();;
        localStorage.setItem(
            "rubiks_nickname",
            nickname
        );
    }
    if (!nickname) return;
    showNicknameTag(nickname);
    await fetch(`/scramble`, { method: "POST" });
    const state = await fetch("/cube").then(r => r.json());
    renderCube(state);
    moveHistory.length = 0;
    redoHistory.length = 0;
    document.getElementById("btn-share").disabled = true;
    document.getElementById("share-menu").disabled = true;
    updateUndoRedoButtons();
    startCompetitionTimer();
    window.resetCount();
    syncHistoryDisplay(moveHistory);
};

window.doMove = async (a) => {
    await window.move(a);

    moveHistory.push(a);
    redoHistory.length = 0;

    window.incrementCount();
    updateUndoRedoButtons();
    syncHistoryDisplay(moveHistory);
};
window.doReset = async () => {
    await window.reset();
    document.getElementById("btn-share").disabled = true;
    document.getElementById("share-menu").disabled = true;

    moveHistory.length = 0;
    redoHistory.length = 0;

    window.resetCount();
    updateUndoRedoButtons();
};


function updateUndoRedoButtons() {
    const undoBtn = document.getElementById("undo-btn");
    const redoBtn = document.getElementById("redo-btn");

    if (undoBtn) undoBtn.disabled = moveHistory.length === 0;
    if (redoBtn) redoBtn.disabled = redoHistory.length === 0;
}

window.doUndo = async () => {
    if (animating) return;
    if (moveHistory.length === 0) return;

    const move = moveHistory.pop();
    const inverse = INVERSE_MOVE[move];

    redoHistory.push(move);

    await window.move(inverse);

    if (_count > 0) {
        _count--;
        countEl.textContent = _count;
    }

    updateUndoRedoButtons();
    syncHistoryDisplay(moveHistory);
};

window.doRedo = async () => {
    if (animating) return;
    if (redoHistory.length === 0) return;

    const move = redoHistory.pop();

    moveHistory.push(move);

    await window.move(move);

    window.incrementCount();
    updateUndoRedoButtons();
    syncHistoryDisplay(moveHistory);
};

function animateCameraReset() {
    return new Promise(resolve => {
        const startPos = camera.position.clone();
        const startTarget = controls.target.clone();
        const startQuaternion = camera.quaternion.clone();

        camera.position.copy(INITIAL_CAMERA_POSITION);
        camera.up.set(0, 1, 0); 
        camera.lookAt(INITIAL_TARGET);
        const endQuaternion = camera.quaternion.clone();

        camera.position.copy(startPos);
        camera.quaternion.copy(startQuaternion);

        const duration = 500;
        const startTime = performance.now();

        controls.enabled = false; 

        function tick() {
            const elapsed = performance.now() - startTime;
            const t = Math.min(elapsed / duration, 1);
            const eased = easeInOut(t);

            controls.target.lerpVectors(startTarget, INITIAL_TARGET, eased);
            camera.position.lerpVectors(startPos, INITIAL_CAMERA_POSITION, eased);
            camera.quaternion.slerpQuaternions(startQuaternion, endQuaternion, eased);

            camera.up.set(0, 1, 0); 
            controls.update();

            if (t < 1) {
                requestAnimationFrame(tick);
            } else {
                camera.position.copy(INITIAL_CAMERA_POSITION);
                camera.quaternion.copy(endQuaternion);
                camera.up.set(0, 1, 0);
                controls.target.copy(INITIAL_TARGET);
                controls.update();
                
                controls.enabled = true;
                resolve();
            }
        }

        requestAnimationFrame(tick);
    });
}


let timerInterval = null;
let startTime = null;
let lastSolve = null;

async function startCompetitionTimer() {

    if (timerInterval) clearInterval(timerInterval);

    startTime = Date.now();


    timerInterval = setInterval(() => {
        const elapsedMs = Date.now() - startTime;

        const totalSecs = Math.floor(elapsedMs / 1000);
        const hrs = String(Math.floor(totalSecs / 3600)).padStart(2, '0');
        const mins = String(Math.floor((totalSecs % 3600) / 60)).padStart(2, '0');
        const secs = String(totalSecs % 60).padStart(2, '0');

        document.getElementById('timer-display').textContent = `${hrs}:${mins}:${secs}`;
    }, 1000);
}

async function refreshLeaderboard() {
    const rows = await fetch(`/leaderboard?period=${currentLeaderboardFilter}`)
        .then(r => r.json());

    const el = document.getElementById("leaderboard");

    if (!rows.length) {
        el.innerHTML = "";
        return;
    }

    el.innerHTML =
        `<div class="leaderboard-title">TOP TIMES</div>` +
        rows
            .slice(0, 5)
            .map((r, i) => {
                const secs = Math.floor(
                    r.solve_time_ms / 1000
                );

                return `
                    <div class="leaderboard-row">
                        ${i + 1}. ${r.nickname} - ${secs}s · ${r.moves}m
                    </div>
                `;
            })
            .join("");
}
window.shareResult = () => {
    const menu = document.getElementById("share-menu");

    menu.hidden = !menu.hidden;
};

window.shareTo = (platform) => {
    if (!lastSolve) return;

    const secs = Math.round(
        lastSolve.solveMs / 1000
    );

    const text = encodeURIComponent(
        `🧩 ${lastSolve.nickname} solved the Rubik's Cube in ${secs}s using ${lastSolve.moves} moves. Can you beat me?`
    );

    const url = "https://rubik-cube-service.onrender.com"

    let shareUrl = "";

    switch (platform) {
        case "x":
            shareUrl =
                `https://twitter.com/intent/tweet?text=${text}&url=${url}`;
            break;

        case "linkedin":
            shareUrl =
                `https://www.linkedin.com/sharing/share-offsite/?url=${url}`;
            break;

        case "whatsapp":
            shareUrl =
                `https://wa.me/?text=${text}%20${url}`;
            break;

        case "telegram":
            shareUrl =
                `https://t.me/share/url?url=${url}&text=${text}`;
            break;
    }

    if (shareUrl) {
        window.open(
            shareUrl,
            "_blank",
            "noopener,noreferrer"
        );
    }

    document.getElementById("share-menu").hidden = true;
};

// ---------------------------------------------------------------------------
// Keyboard shortcuts
// U/D/F/B/L/R = normal move, Shift+key = prime (inverse)
// ---------------------------------------------------------------------------
const KEY_TO_MOVE = {
    'u': 0, 'U': 1,
    'd': 2, 'D': 3,
    'f': 4, 'F': 5,
    'b': 6, 'B': 7,
    'l': 8, 'L': 9,
    'r': 10, 'R': 11,
};

document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT') return;
    if (animating) return;
    if (document.getElementById('solve-btn').disabled) return;

    const key = e.shiftKey
        ? e.key.toUpperCase()   // Shift+U → 'U' → prime
        : e.key.toLowerCase();  // u → normal

    const moveId = KEY_TO_MOVE[key];
    if (moveId === undefined) return;

    e.preventDefault();
    window.doMove(moveId);
});

window.toggleTheme = () => {
    const isLight = document.body.classList.toggle('light');
    scene.background = new THREE.Color(isLight ? LIGHT_BG : DARK_BG);
    document.getElementById('theme-toggle').textContent =
        isLight ? '🌙' : '☀️';
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
};




window.setLeaderboardFilter = (period) => {
    currentLeaderboardFilter = period;

    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('filter-btn--active');
    });
    document.getElementById(
        period === 'today' ? 'filter-today' : 'filter-all'
    ).classList.add('filter-btn--active');

    refreshLeaderboard();
};

window.resetCameraView = async () => {
    await animateCameraReset();
};

window.createSnapshot = async () => {
    if (isCompeting) return; 
    const id = crypto.randomUUID();
    const createdAt = new Date();
    const label = `Snap ${snapshots.length + 1} — ${_fmtTime(createdAt)}`;

    const res = await fetch("/snapshot/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ snapshot_id: id }),
    });

    if (!res.ok) {
        console.error("Failed to save snapshot", await res.text());
        return;
    }

    snapshots.push({ id, label, createdAt });
    renderSnapshotTree();
};

async function restoreSnapshot(id) {
    if (animating || isCompeting) return;

    const res = await fetch("/snapshot/load", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ snapshot_id: id }),
    });

    if (!res.ok) {
        console.error("Failed to load snapshot", await res.text());
        return;
    }

    const state = await fetch("/cube").then(r => r.json());
    renderCube(state);

    document.querySelectorAll(".snapshot-node").forEach(n => {
        n.classList.toggle("snapshot-node--active", n.dataset.id === id);
    });
}

function renderSnapshotTree() {
    const container = document.getElementById("snapshot-tree");
    let list = container.querySelector(".snapshot-list");
    if (!list) {
        list = document.createElement("div");
        list.className = "snapshot-list";
        container.appendChild(list);
    }

    list.innerHTML = "";

    if (snapshots.length === 0) {
        list.innerHTML = `<p class="snapshot-empty">No snapshots yet.</p>`;
        return;
    }

    [...snapshots].reverse().forEach(snap => {
        const node = document.createElement("div");
        node.className = "snapshot-node";
        node.dataset.id = snap.id;
        node.title = snap.label;
        node.onclick = () => restoreSnapshot(snap.id);

        const dot = document.createElement("span");
        dot.className = "snapshot-dot";

        const lbl = document.createElement("span");
        lbl.className = "snapshot-label";
        lbl.textContent = snap.label;

        node.appendChild(dot);
        node.appendChild(lbl);
        list.appendChild(node);
    });
}

function initSnapshotUI() {
    const btn   = document.getElementById("snapshot-btn");
    const tree  = document.getElementById("snapshot-tree");
    const panel = document.getElementById("floating-side-panel");
    if (!btn || !tree || !panel) return;
 
    btn.onclick = () => {
        const opening = tree.hidden;
        tree.hidden   = !opening;
        panel.classList.toggle("expanded", opening);
    };
}


function _fmtTime(date) {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}