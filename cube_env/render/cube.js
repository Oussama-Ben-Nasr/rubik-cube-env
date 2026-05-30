import * as THREE from "three";
// FIX: use the same unpkg base as the importmap so module resolution is consistent
import { OrbitControls } from "https://unpkg.com/three@0.179.1/examples/jsm/controls/OrbitControls.js";

// Map face index (as stored in Python) → hex color
// 0=U white, 1=F green, 2=D yellow, 3=L orange, 4=B blue, 5=R red
const INDEX_COLORS = [
    0xffffff, // 0  U
    0x00ff00, // 1  F
    0xffff00, // 2  D
    0xffa500, // 3  L
    0x0000ff, // 4  B
    0xff0000, // 5  R
];

let scene, camera, renderer, controls;
let cubieGroup = new THREE.Group();

init();
await loadAndRender();

window.move = async (a) => {
    await fetch(`/move/${a}`, { method: "POST" });
    await loadAndRender();
};

window.reset = async () => {
    await fetch(`/reset`, { method: "POST" });
    await loadAndRender();
};

function init() {

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x111111);

    camera = new THREE.PerspectiveCamera(
        60,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );

    camera.position.set(6, 6, 6);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    controls = new OrbitControls(camera, renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 1.2));

    const light = new THREE.DirectionalLight(0xffffff, 1.5);
    light.position.set(5, 10, 5);
    scene.add(light);

    scene.add(cubieGroup);

    window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    animate();
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

async function loadAndRender() {
    const state = await fetch("/cube").then(r => r.json());
    renderCube(state);
}

function clearScene() {
    scene.remove(cubieGroup);
    cubieGroup = new THREE.Group();
    scene.add(cubieGroup);
}

function createSticker(color, position, rotation) {

    const geo = new THREE.PlaneGeometry(0.9, 0.9);
    const mat = new THREE.MeshBasicMaterial({
        color,
        side: THREE.DoubleSide
    });

    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.copy(position);
    mesh.rotation.set(rotation.x, rotation.y, rotation.z);

    return mesh;
}

function createCubie(cubie) {

    const { x, y, z, colors } = cubie;

    const group = new THREE.Group();
    group.position.set(x, y, z);

    const offset = 0.5;

    // FIX: resolve the actual sticker color from the face's color index in state.
    // Previously the code always used the face's default color (e.g. FACE_COLORS.U
    // was always white), ignoring what color the state said was there after moves.
    const resolve = (faceColorIndex) => INDEX_COLORS[faceColorIndex];

    if (colors.U !== undefined) {
        group.add(createSticker(
            resolve(colors.U),
            new THREE.Vector3(0, offset, 0),
            new THREE.Euler(-Math.PI / 2, 0, 0)
        ));
    }

    if (colors.D !== undefined) {
        group.add(createSticker(
            resolve(colors.D),
            new THREE.Vector3(0, -offset, 0),
            new THREE.Euler(Math.PI / 2, 0, 0)
        ));
    }

    if (colors.F !== undefined) {
        group.add(createSticker(
            resolve(colors.F),
            new THREE.Vector3(0, 0, offset),
            new THREE.Euler(0, 0, 0)
        ));
    }

    if (colors.B !== undefined) {
        group.add(createSticker(
            resolve(colors.B),
            new THREE.Vector3(0, 0, -offset),
            new THREE.Euler(0, Math.PI, 0)
        ));
    }

    if (colors.L !== undefined) {
        group.add(createSticker(
            resolve(colors.L),
            new THREE.Vector3(-offset, 0, 0),
            new THREE.Euler(0, -Math.PI / 2, 0)
        ));
    }

    if (colors.R !== undefined) {
        group.add(createSticker(
            resolve(colors.R),
            new THREE.Vector3(offset, 0, 0),
            new THREE.Euler(0, Math.PI / 2, 0)
        ));
    }

    return group;
}

function renderCube(state) {
    clearScene();   // FIX: was named 'clear()' — shadowed the built-in window.clear

    for (const cubie of state) {
        const mesh = createCubie(cubie);
        cubieGroup.add(mesh);
    }
}