import * as THREE from "three";
import { OrbitControls } from "https://unpkg.com/three@0.179.1/examples/jsm/controls/OrbitControls.js";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const SIDEBAR_W = 220;
const INDEX_COLORS = [
    0xffffff, // 0  U  white
    0x00cc44, // 1  F  green
    0xffdd00, // 2  D  yellow
    0xff8800, // 3  L  orange
    0x1144ff, // 4  B  blue
    0xee1111, // 5  R  red
];

const CUBIE_BODY_COLOR = 0x111111;   // near-black base
const STICKER_OFFSET   = 0.501;     // just above the face surface
const STICKER_SIZE     = 0.85;
const ANIM_DURATION_MS = 280;
const loadingOverlay =
    document.getElementById("loading-overlay");

// Action → { axis, layerValue, direction, angleDelta }
// axis: 0=X,1=Y,2=Z   layerValue: which slice (-1|0|1)
// angleDelta: full rotation in radians (±π/2)
const ACTION_META = [
    { axis: 1, layer:  1, angle:  Math.PI / 2 },  //  0  U
    { axis: 1, layer:  1, angle: -Math.PI / 2 },  //  1  U'
    { axis: 1, layer: -1, angle: -Math.PI / 2 },  //  2  D
    { axis: 1, layer: -1, angle:  Math.PI / 2 },  //  3  D'
    { axis: 2, layer:  1, angle:  Math.PI / 2 },  //  4  F
    { axis: 2, layer:  1, angle: -Math.PI / 2 },  //  5  F'
    { axis: 2, layer: -1, angle: -Math.PI / 2 },  //  6  B
    { axis: 2, layer: -1, angle:  Math.PI / 2 },  //  7  B'
    { axis: 0, layer: -1, angle: -Math.PI / 2 },  //  8  L
    { axis: 0, layer: -1, angle:  Math.PI / 2 },  //  9  L'
    { axis: 0, layer:  1, angle:  Math.PI / 2 },  // 10  R
    { axis: 0, layer:  1, angle: -Math.PI / 2 },  // 11  R'
];

const AXES = [
    new THREE.Vector3(1, 0, 0),
    new THREE.Vector3(0, 1, 0),
    new THREE.Vector3(0, 0, 1),
];
const INITIAL_CAMERA_POSITION = new THREE.Vector3(6, 6, 6);
const INITIAL_TARGET = new THREE.Vector3(0, 0, 0);

// ---------------------------------------------------------------------------
// Scene globals
// ---------------------------------------------------------------------------

let scene, camera, renderer, controls;
let cubieGroup = new THREE.Group();
let animating = false;
    document.body.classList.remove("animating");           // block input during animation
let nickname =
    localStorage.getItem("rubiks_nickname") || "";
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

const INVERSE_MOVE = {
    0: 1,  1: 0,
    2: 3,  3: 2,
    4: 5,  5: 4,
    6: 7,  7: 6,
    8: 9,  9: 8,
    10: 11, 11: 10,
};

// ---------------------------------------------------------------------------
// Bootstrap
// ---------------------------------------------------------------------------

init();
await loadAndRender();
if (!nickname) {
    nickname = prompt("Nickname for leaderboard?") || "anonymous";
    localStorage.setItem(
        "rubiks_nickname",
        nickname
    );
}
// ---------------------------------------------------------------------------
// Public API (called from HTML buttons)
// ---------------------------------------------------------------------------

window.move = async (actionId) => {
    if (animating) return;

    const meta = ACTION_META[actionId];
    if (!meta) return;

    animating = true;
    document.body.classList.add("animating");

    // 1. Animate the layer visually
    await animateLayer(meta);

    // 2. Commit the move on the server
    await fetch(`/move/${actionId}`, { method: "POST" });

    // 3. Rebuild from ground-truth state
    const state = await fetch("/cube").then(r => r.json());
    const status = await fetch("/status").then(r => r.json());
    
    if (status.is_competing && status.solved) {
        console.log(status.solve_time, status.real_moves_count );
        const solveMs =
        new Date(status.solve_time) -
        new Date(status.start_time);
        
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
    
    alert(
        `Solved in ${Math.round(solveMs / 1000)}s using ${status.real_moves_count} moves`
    );
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
};

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------

window.addEventListener('resize', () => {
    renderer.setSize(window.innerWidth - SIDEBAR_W, window.innerHeight);
    camera.aspect = (window.innerWidth - SIDEBAR_W) / window.innerHeight;
    camera.updateProjectionMatrix();
});
function init() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x111111);

    camera = new THREE.PerspectiveCamera(60, (window.innerWidth - SIDEBAR_W) / window.innerHeight, 0.1, 1000);
    camera.position.copy(INITIAL_CAMERA_POSITION);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth - SIDEBAR_W, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

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

// ---------------------------------------------------------------------------
// Cube building
// ---------------------------------------------------------------------------

function clearScene() {
    scene.remove(cubieGroup);
    cubieGroup = new THREE.Group();
    scene.add(cubieGroup);
}

/** Dark box body for a single cubie */
function createBody() {
    const geo = new THREE.BoxGeometry(0.95, 0.95, 0.95);
    const mat = new THREE.MeshStandardMaterial({ color: CUBIE_BODY_COLOR, roughness: 0.8 });
    return new THREE.Mesh(geo, mat);
}

/** Colored sticker plane sitting on one face */
function createSticker(color, position, rotation, faceName) {
    const geo = new THREE.PlaneGeometry(STICKER_SIZE, STICKER_SIZE);
    const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.5, metalness: 0.1 });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.copy(position);
    mesh.rotation.set(rotation.x, rotation.y, rotation.z);
    mesh.userData.faceName = faceName;

// Add label only for center stickers
if (faceName) {
    const label = createFaceLabel(faceName);

    // Only center stickers will actually use it
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

    // Dark body
    group.add(createBody());

    const o = STICKER_OFFSET;
    const FACE_DEFS = [
        { face: "U", pos: new THREE.Vector3(0,  o, 0), rot: new THREE.Euler(-Math.PI/2, 0, 0) },
        { face: "D", pos: new THREE.Vector3(0, -o, 0), rot: new THREE.Euler( Math.PI/2, 0, 0) },
        { face: "F", pos: new THREE.Vector3(0, 0,  o), rot: new THREE.Euler(0, 0, 0) },
        { face: "B", pos: new THREE.Vector3(0, 0, -o), rot: new THREE.Euler(0, Math.PI, 0) },
        { face: "L", pos: new THREE.Vector3(-o, 0, 0), rot: new THREE.Euler(0, -Math.PI/2, 0) },
        { face: "R", pos: new THREE.Vector3( o, 0, 0), rot: new THREE.Euler(0,  Math.PI/2, 0) },
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

// ---------------------------------------------------------------------------
// Layer animation
// ---------------------------------------------------------------------------

/**
 * Smoothly rotate the cubies in `meta.layer` along `meta.axis` by `meta.angle`.
 * Uses an eased tween over ANIM_DURATION_MS ms.
 */
function animateLayer(meta) {
    return new Promise(resolve => {
        const axisVec  = AXES[meta.axis];
        const axisKey  = ["x", "y", "z"][meta.axis];

        // Collect cubies in this layer
        const layerMeshes = cubieGroup.children.filter(child => {
            return Math.round(child.position[axisKey]) === meta.layer;
        });

        // Reparent them under a temporary pivot group
        const pivot = new THREE.Group();
        scene.add(pivot);
        for (const mesh of layerMeshes) {
            // Convert world position → pivot-local (pivot is at origin so it's a no-op,
            // but keeping it explicit for correctness)
            cubieGroup.remove(mesh);
            pivot.add(mesh);
        }

        const startTime = performance.now();
        const totalAngle = meta.angle;

        function tick() {
            const elapsed = performance.now() - startTime;
            const t = Math.min(elapsed / ANIM_DURATION_MS, 1);
            const eased = easeInOut(t);

            // Set absolute rotation on the pivot each frame
            const currentAngle = totalAngle * eased;
            pivot.setRotationFromAxisAngle(axisVec, currentAngle);

            if (t < 1) {
                requestAnimationFrame(tick);
            } else {
                // Re-attach cubies back to the main group.
                // The server will supply the true final state immediately after,
                // so we just need to avoid a visual pop until that fetch resolves.
                pivot.updateMatrixWorld();
                for (const mesh of [...pivot.children]) {
                    pivot.remove(mesh);
                    // Apply pivot's rotation into the mesh world transform
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

/** Smooth ease-in-out (cubic) */
function easeInOut(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

// ---------------------------------------------------------------------------
// Load initial state
// ---------------------------------------------------------------------------

async function loadAndRender() {
    const state = await fetch("/cube").then(r => r.json());
    renderCube(state);
    updateUndoRedoButtons();
    await refreshLeaderboard();
    requestAnimationFrame(() => {
        loadingOverlay?.classList.add("hidden");
    });
}


// Move counter (read by cube.js via window.incrementCount / window.resetCount)
let _count = 0;
const countEl = document.getElementById('count');

window.incrementCount = () => { countEl.textContent = ++_count; };
window.resetCount     = () => { _count = 0; countEl.textContent = 0; };

// Scramble: 20 random moves
window.doScramble = async () => {
    if (document.body.classList.contains('animating')) return;
    // for (let i = 0; i < 20; i++) {
    //     await window.move(Math.floor(Math.random() * 12));
    // }
    await fetch(`/scramble`, { method: "POST" });
    const state = await fetch("/cube").then(r => r.json());
    renderCube(state);
    moveHistory.length = 0;
    redoHistory.length = 0;
    updateUndoRedoButtons();
    startCompetitionTimer();
    window.resetCount();
};

window.doMove = async (a) => {
    await window.move(a);

    moveHistory.push(a);
    redoHistory.length = 0;

    window.incrementCount();
    updateUndoRedoButtons();
};
window.doReset = async () => {
    await window.reset();

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
};

window.doRedo = async () => {
    if (animating) return;
    if (redoHistory.length === 0) return;

    const move = redoHistory.pop();

    moveHistory.push(move);

    await window.move(move);

    window.incrementCount();
    updateUndoRedoButtons();
};

function animateCameraReset() {
    return new Promise(resolve => {
        const startPos = camera.position.clone();
        const startTarget = controls.target.clone();

        const duration = 500;
        const startTime = performance.now();

        function tick() {
            const elapsed = performance.now() - startTime;
            const t = Math.min(elapsed / duration, 1);
            const eased = easeInOut(t);

            camera.position.lerpVectors(
                startPos,
                INITIAL_CAMERA_POSITION,
                eased
            );

            controls.target.lerpVectors(
                startTarget,
                INITIAL_TARGET,
                eased
            );

            controls.update();

            if (t < 1) {
                requestAnimationFrame(tick);
            } else {
                resolve();
            }
        }

        requestAnimationFrame(tick);
    });
}

let timerInterval = null;
let startTime = null;

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
    const rows = await fetch("/leaderboard")
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
                console.log(r);

                return `
                    <div class="leaderboard-row">
                        ${i + 1}. ${r.nickname} - ${secs}s · ${r.moves}m
                    </div>
                `;
            })
            .join("");
}