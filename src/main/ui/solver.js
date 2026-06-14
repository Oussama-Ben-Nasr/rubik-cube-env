const SOLVE_STEP_DELAY_MS = 400;

let isSolving = false;


function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function setControlsLocked(locked) {
  const controls = document.querySelectorAll(
    '#btn-pair, #btn-scramble, #btn-reset, #btn-undo, #btn-redo'
  );
  controls.forEach(el => {
    el.disabled = locked;
    el.style.opacity = locked ? '0.4' : '1';
  });

  const solveBtn = document.getElementById('solve-btn');
  if (solveBtn) {
    solveBtn.disabled = locked;
    solveBtn.textContent = locked ? 'Solving…' : '✨ Solve';
  }
}

async function animateSolve() {

  if (isSolving) return;

  isSolving = true;
  setControlsLocked(true);

  try {
    const status = await fetch("/status").then(r => r.json());
    if (status.is_competing) {
      alert("Cannot use auto solver while competing!");
      isSolving = false;
      setControlsLocked(false);
      return;
    }
    const adminPassword = "my-suppa-duppa-password#aA";

    const res = await fetch("/solution", {
      method: "POST",
      headers: {
        "X-Admin-Password": adminPassword
      }
    });

    if (!res.ok) {

      const text = await res.text();

      throw new Error(
        `Solver request failed (${res.status}): ${text}`
      );
    }

    const data = await res.json();

    console.log("Solver response:", data);

    const moveIds = [];

    for (const step of (data.actions_to_be_executed || [])) {

      const match = step.match(
        /Apply action:\s*(\d+)/
      );

      if (match) {
        moveIds.push(
          parseInt(match[1], 10)
        );
      }
    }

    if (moveIds.length === 0) {

      if (data.status === "solved") {
        alert("Puzzle is already solved!");
        return;
      }

      throw new Error(
        "Solver returned no executable actions."
      );
    }

    console.log(
      `Solver returned ${moveIds.length} moves`,
      moveIds
    );


    for (const moveId of moveIds) {

      await doMove(moveId);



      await sleep(
        SOLVE_STEP_DELAY_MS
      );
    }

    console.log("Solve complete!");

  } catch (err) {

    console.error(
      "Solve animation error:",
      err
    );

    alert(
      `Solver error: ${err.message}`
    );

  } finally {

    isSolving = false;
    setControlsLocked(false);

  }
}
export function initSolver() {
  const solveBtn = document.getElementById('solve-btn');
  if (solveBtn) {
    solveBtn.addEventListener('click', animateSolve);
  } else {
    console.warn('initSolver: no element with id="solve-btn" found.');
  }
}

const MOVE_ID_TO_NOTATION = {
  0: 'U', 1: "U'",
  2: 'D', 3: "D'",
  4: 'F', 5: "F'",
  6: 'B', 7: "B'",
  8: 'L', 9: "L'",
  10: 'R', 11: "R'",
};

export function syncHistoryDisplay(moves) {
  localStorage.setItem(
    "moveHistory",
    JSON.stringify(moves)
  );
  const container = document.getElementById('move-history-list');
  const countEl = document.getElementById('move-history-count');

  if (countEl) countEl.textContent = moves.length;
  if (!container) return;

  if (moves.length === 0) {
    container.innerHTML = '<span class="history-badge history-badge--empty">No moves yet</span>';
    return;
  }

  container.innerHTML = moves.map((moveId, i) => {
    const notation = MOVE_ID_TO_NOTATION[moveId] ?? `#${moveId}`;
    if (isSolving)
      return `<span class="history-badge history-badge--solver" title="Move ${i + 1}">${notation}</span>`;
    return `<span class="history-badge history-badge--manual" title="Move ${i + 1}">${notation}</span>`;
  }).join('');

  container.scrollLeft = container.scrollWidth;
  console.log("history sync");
}

export function initMoveHistory(moveHistory) {
  const saved =
    JSON.parse(
      localStorage.getItem("moveHistory") || "[]"
    );

  moveHistory.push(...saved);
  syncHistoryDisplay(moveHistory);
}