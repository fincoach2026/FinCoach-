/*
 * scene.js — the Three.js side of the Life Simulator.
 *
 * Beginner note on how this file is organized:
 *   1. SET UP THE 3D SCENE   - creates a basic world (camera, lights,
 *      ground, and a placeholder avatar box). We'll swap the box for
 *      a real Kenney/Mixamo character model once assets are added —
 *      everything else stays the same.
 *   2. TALK TO DJANGO        - fetches the next scenario as JSON and
 *      shows it in the overlay card; sends the user's choice back.
 *   3. WIRE THEM TOGETHER    - when a scenario loads, we could move the
 *      avatar toward the matching location (left as a TODO once we
 *      have real scene locations mapped out).
 */

// ---------------------------------------------------------------------
// 1. SET UP THE 3D SCENE
// ---------------------------------------------------------------------

const container = document.getElementById("sim-canvas-container");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xe8f7f0); // soft brand-tinted sky

const camera = new THREE.PerspectiveCamera(
    50,
    container.clientWidth / container.clientHeight,
    0.1,
    1000
);
camera.position.set(0, 3, 6);
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(container.clientWidth, container.clientHeight);
container.appendChild(renderer.domElement);

// Basic lighting so we can actually see the 3D shapes.
const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
scene.add(ambientLight);
const sunLight = new THREE.DirectionalLight(0xffffff, 0.8);
sunLight.position.set(5, 10, 5);
scene.add(sunLight);

// Ground plane, tinted with our brand accent color.
const groundGeometry = new THREE.PlaneGeometry(40, 40);
const groundMaterial = new THREE.MeshStandardMaterial({ color: 0x9fc35c });
const ground = new THREE.Mesh(groundGeometry, groundMaterial);
ground.rotation.x = -Math.PI / 2;
scene.add(ground);

// TEMPORARY avatar placeholder: a simple box standing on the ground.
// This gets replaced with a real character model (Mixamo/Kenney,
// loaded via GLTFLoader) once assets are added to
// static/simulator/models/.
const avatarGeometry = new THREE.BoxGeometry(0.8, 1.6, 0.5);
const avatarMaterial = new THREE.MeshStandardMaterial({ color: 0x21815f });
const avatar = new THREE.Mesh(avatarGeometry, avatarMaterial);
avatar.position.y = 0.8; // lift so it stands on the ground, not inside it
scene.add(avatar);

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();

// Keep the 3D scene sized correctly if the browser window changes size.
window.addEventListener("resize", () => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
});

// ---------------------------------------------------------------------
// 2. TALK TO DJANGO
// ---------------------------------------------------------------------

const overlay = document.getElementById("scenario-overlay");
const loadingMessage = document.getElementById("loading-message");
const titleEl = document.getElementById("scenario-title");
const descriptionEl = document.getElementById("scenario-description");
const choicesEl = document.getElementById("choice-buttons");

// Reads the CSRF token Django sets as a cookie, required on any POST
// request so Django knows the request is legitimately from our own page.
function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : "";
}

async function loadNextScenario() {
    loadingMessage.style.display = "block";
    overlay.style.display = "none";

    const response = await fetch("/simulator/api/current-scenario/");
    const data = await response.json();

    loadingMessage.style.display = "none";

    if (data.done) {
        // No more scenarios — send the user to the results page.
        window.location.href = "/simulator/results/";
        return;
    }

    showScenario(data);
}

function showScenario(scenario) {
    titleEl.textContent = scenario.title;
    descriptionEl.textContent = scenario.description;

    // Clear old choice buttons before adding the new ones.
    choicesEl.innerHTML = "";

    scenario.choices.forEach((choice) => {
        const button = document.createElement("button");
        button.className = "fc-button";
        button.textContent = choice.label;
        button.addEventListener("click", () => submitChoice(choice.id));
        choicesEl.appendChild(button);
    });

    overlay.style.display = "block";

    // TODO once real locations/models exist: move the avatar toward
    // the spot matching scenario.location_tag here.
}

async function submitChoice(choiceId) {
    const response = await fetch("/simulator/api/submit-choice/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({ choice_id: choiceId }),
    });
    const result = await response.json();

    // Simple feedback for now: a temporary alert. We'll replace this
    // with a nicer in-scene popup once the UI design is finalized.
    if (result.feedback) {
        alert(result.feedback);
    }

    loadNextScenario();
}

// ---------------------------------------------------------------------
// 3. KICK THINGS OFF
// ---------------------------------------------------------------------
loadNextScenario();
