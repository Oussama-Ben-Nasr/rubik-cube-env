import * as THREE from "three";
import { OrbitControls } from "https://unpkg.com/three@0.179.1/examples/jsm/controls/OrbitControls.js";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Scene globals
// ---------------------------------------------------------------------------

let scene, camera, renderer, controls;
let cubieGroup = new THREE.Group();
let animating = false;
    document.body.classList.remove("animating");           // block input during animation

// ---------------------------------------------------------------------------
// Bootstrap
// ---------------------------------------------------------------------------

init();
await loadAndRender();

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
    renderCube(state);

    animating = false;
    document.body.classList.remove("animating");
};

window.reset = async () => {
    if (animating) return;
    await fetch(`/reset`, { method: "POST" });
    const state = await fetch("/cube").then(r => r.json());
    renderCube(state);
};

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------

function init() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x111111);

    camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(6, 6, 6);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    scene.add(new THREE.AmbientLight(0xffffff, 0.9));
    const dir = new THREE.DirectionalLight(0xffffff, 1.2);
    dir.position.set(5, 10, 5);
    scene.add(dir);

    scene.add(cubieGroup);

    window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    renderLoop();
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
function createSticker(color, position, rotation) {
    const geo = new THREE.PlaneGeometry(STICKER_SIZE, STICKER_SIZE);
    const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.5, metalness: 0.1 });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.copy(position);
    mesh.rotation.set(rotation.x, rotation.y, rotation.z);
    return mesh;
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
            group.add(createSticker(INDEX_COLORS[colors[face]], pos, rot));
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
    window.resetCount();
};

window.doMove  = (a) => { window.move(a); window.incrementCount(); };
window.doReset = () => { window.reset(); window.resetCount(); };