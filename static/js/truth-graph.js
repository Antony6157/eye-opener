(() => {
  const NODE_LABELS = {
    claim: "Claim",
    preprocessor: "Preprocessor",
    surgeon: "Surgeon",
    diver: "Diver",
    skeptic: "Skeptic",
    scorer: "Scorer",
    architect: "Architect (Orchestrator)",
    error: "Error Handler",
  };

  const NODE_IDS = [
    "claim",
    "preprocessor",
    "surgeon",
    "diver",
    "skeptic",
    "scorer",
    "architect",
    "error",
  ];

  const WORKERS = ["preprocessor", "surgeon", "diver", "skeptic", "scorer"];
  const LINKS = [
    { source: "claim", target: "architect" },
    { source: "architect", target: "preprocessor" },
    { source: "architect", target: "surgeon" },
    { source: "architect", target: "diver" },
    { source: "architect", target: "skeptic" },
    { source: "architect", target: "scorer" },
    { source: "architect", target: "error" },
  ];

  const styleId = "truth-graph-inline-style";

  let d3ref = null;
  let svg = null;
  let linkSel = null;
  let nodeSel = null;
  let labelSel = null;
  let container = null;
  let nodes = [];
  let activeNodeId = null;
  let dashOffset = 0;
  let frameHandle = null;

  window.truthGraph = window.truthGraph || {};
  window.truthGraph.activateNode = activateNode;

  initWhenReady();

  function initWhenReady() {
    const ready = () => {
      const hasD3 = typeof window.d3 !== "undefined";
      const hasContainer = !!document.querySelector("#graph-container");
      return hasD3 && hasContainer;
    };

    if (ready()) {
      init();
      return;
    }

    const attemptsMax = 120;
    let attempts = 0;
    const interval = setInterval(() => {
      attempts += 1;
      if (ready()) {
        clearInterval(interval);
        init();
      } else if (attempts >= attemptsMax) {
        clearInterval(interval);
      }
    }, 250);
  }

  function init() {
    d3ref = window.d3;
    container = document.querySelector("#graph-container");
    if (!d3ref || !container) {
      return;
    }

    injectStyle();
    buildData();
    render();
    startAnimationLoop();

    const resizeObserver = new ResizeObserver(() => {
      render();
    });
    resizeObserver.observe(container);

    activateNode("claim");
  }

  function injectStyle() {
    if (document.getElementById(styleId)) {
      return;
    }

    const style = document.createElement("style");
    style.id = styleId;
    style.textContent = `
      #graph-container svg {
        width: 100%;
        height: 100%;
        display: block;
      }

      .tg-link {
        stroke: rgba(20, 34, 38, 0.34);
        stroke-width: 2;
        fill: none;
        stroke-linecap: round;
        stroke-dasharray: 8 6;
      }

      .tg-link.active {
        stroke: rgba(0, 142, 125, 0.95);
        stroke-width: 3.2;
        filter: drop-shadow(0 0 6px rgba(0, 142, 125, 0.65));
      }

      .tg-node circle {
        fill: #fff;
        stroke: rgba(24, 34, 40, 0.4);
        stroke-width: 2;
      }

      .tg-node.node-claim circle {
        fill: #f9fcff;
      }

      .tg-node.node-architect circle {
        fill: #f5f3ff;
      }

      .tg-node.node-error circle {
        fill: #fff0f0;
        stroke: rgba(158, 30, 30, 0.75);
      }

      .tg-node text {
        font: 600 12px "Space Grotesk", "Segoe UI", sans-serif;
        fill: #1f2a2f;
        text-anchor: middle;
        dominant-baseline: middle;
        pointer-events: none;
      }

      .tg-node.node-error text {
        fill: #9e1e1e;
      }

      .tg-node {
        transition: transform 220ms ease;
      }

      .tg-node.active {
        filter: drop-shadow(0 0 10px rgba(0, 142, 125, 0.4));
      }

      .tg-node.node-error {
        opacity: 0;
        transition: opacity 240ms ease, transform 220ms ease;
      }

      .tg-node.node-error.show {
        opacity: 1;
        filter: drop-shadow(0 0 9px rgba(170, 46, 46, 0.5));
      }

      .tg-node.node-error.active circle {
        fill: #ffdede;
        stroke: rgba(170, 46, 46, 1);
      }

      .tg-node.node-error.active text {
        fill: #7e1111;
      }
    `;
    document.head.appendChild(style);
  }

  function buildData() {
    nodes = NODE_IDS.map((id) => ({ id }));
  }

  function render() {
    if (!container || !d3ref) {
      return;
    }

    const width = Math.max(container.clientWidth, 320);
    const height = Math.max(container.clientHeight, 280);

    d3ref.select(container).selectAll("*").remove();
    svg = d3ref
      .select(container)
      .append("svg")
      .attr("viewBox", `0 0 ${width} ${height}`)
      .attr("aria-label", "Truth workflow graph");

    const pos = getPositions(width, height);

    linkSel = svg
      .append("g")
      .attr("class", "tg-links")
      .selectAll("line")
      .data(LINKS)
      .enter()
      .append("line")
      .attr("class", "tg-link")
      .attr("x1", (d) => pos[d.source].x)
      .attr("y1", (d) => pos[d.source].y)
      .attr("x2", (d) => pos[d.target].x)
      .attr("y2", (d) => pos[d.target].y);

    const nodeG = svg
      .append("g")
      .attr("class", "tg-nodes")
      .selectAll("g")
      .data(nodes)
      .enter()
      .append("g")
      .attr("class", (d) => `tg-node node-${d.id}`)
      .attr("transform", (d) => `translate(${pos[d.id].x}, ${pos[d.id].y}) scale(1)`);

    nodeG
      .append("circle")
      .attr("r", (d) => (d.id === "claim" ? 36 : d.id === "architect" ? 28 : d.id === "error" ? 24 : 22));

    labelSel = nodeG
      .append("text")
      .text((d) => NODE_LABELS[d.id] || d.id)
      .attr("dy", "0.1em");

    nodeSel = nodeG;
    updateVisualState();
  }

  function getPositions(width, height) {
    const cx = width * 0.5;
    const cy = height * 0.5;
    const workerRadius = Math.min(width, height) * 0.34;

    const workerPos = {};
    WORKERS.forEach((id, idx) => {
      const angle = (-Math.PI / 2) + (idx * (2 * Math.PI)) / WORKERS.length;
      workerPos[id] = {
        x: cx + Math.cos(angle) * workerRadius,
        y: cy + Math.sin(angle) * workerRadius,
      };
    });

    return {
      claim: { x: cx, y: cy },
      architect: { x: cx, y: cy - workerRadius * 0.55 },
      preprocessor: workerPos.preprocessor,
      surgeon: workerPos.surgeon,
      diver: workerPos.diver,
      skeptic: workerPos.skeptic,
      scorer: workerPos.scorer,
      error: { x: cx + workerRadius * 0.95, y: cy - workerRadius * 0.72 },
    };
  }

  function activateNode(nodeId) {
    if (!NODE_IDS.includes(nodeId)) {
      return;
    }
    activeNodeId = nodeId;
    updateVisualState();
  }

  function updateVisualState() {
    if (!nodeSel || !linkSel) {
      return;
    }

    nodeSel
      .classed("active", (d) => d.id === activeNodeId)
      .classed("show", (d) => d.id === "error" && activeNodeId === "error")
      .attr("transform", function (d) {
        const t = d3ref.select(this).attr("transform");
        const match = /translate\(([^)]+)\)/.exec(t || "");
        const translate = match ? match[0] : "translate(0, 0)";
        const scale = d.id === activeNodeId ? 1.35 : 1;
        return `${translate} scale(${scale})`;
      });

    linkSel
      .classed("active", (d) => d.source === activeNodeId || d.target === activeNodeId)
      .attr("stroke-dashoffset", (d) => ((d.source === activeNodeId || d.target === activeNodeId) ? dashOffset : 0));
  }

  function startAnimationLoop() {
    if (frameHandle) {
      cancelAnimationFrame(frameHandle);
    }

    const tick = () => {
      dashOffset -= 0.75;
      if (linkSel) {
        linkSel
          .filter((d) => d.source === activeNodeId || d.target === activeNodeId)
          .attr("stroke-dashoffset", dashOffset);
      }
      frameHandle = requestAnimationFrame(tick);
    };

    frameHandle = requestAnimationFrame(tick);
  }
})();
