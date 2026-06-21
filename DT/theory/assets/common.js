/* Shared helpers for the interactive SVG widgets.
   Loaded by every chapter page. Russian UI strings live in the pages. */

const NS = "http://www.w3.org/2000/svg";

// Linear scale factory: maps a data domain onto a pixel range.
function scale(domain, range) {
  const [d0, d1] = domain, [r0, r1] = range;
  return v => r0 + (v - d0) * (r1 - r0) / (d1 - d0);
}

// Create an SVG element with attributes.
function el(tag, attrs = {}) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  return e;
}

// Build a polyline "points" string from arrays of pixel coords.
function pathFrom(xs, ys) {
  let s = "";
  for (let i = 0; i < xs.length; i++) {
    s += (i === 0 ? "M" : "L") + xs[i].toFixed(2) + " " + ys[i].toFixed(2);
  }
  return s;
}

// Draw axes + light grid into a group. cfg: {x:scaleX, y:scaleY, x0,x1,y0,y1, w,h, pad, xticks, yticks}
function drawFrame(g, cfg) {
  const { x, y, x0, x1, y0, y1, xticks = [], yticks = [] } = cfg;
  // grid
  for (const tx of xticks) {
    g.appendChild(el("line", { x1: x(tx), y1: y(y0), x2: x(tx), y2: y(y1), class: "gridline" }));
    const t = el("text", { x: x(tx), y: y(y0) + 16, class: "tick-label", "text-anchor": "middle" });
    t.textContent = tx;
    g.appendChild(t);
  }
  for (const ty of yticks) {
    g.appendChild(el("line", { x1: x(x0), y1: y(ty), x2: x(x1), y2: y(ty), class: "gridline" }));
    const t = el("text", { x: x(x0) - 8, y: y(ty) + 4, class: "tick-label", "text-anchor": "end" });
    t.textContent = ty;
    g.appendChild(t);
  }
  // axes (x at y=0 if in range else bottom, y at x=0 if in range else left)
  const ax = (y0 <= 0 && y1 >= 0) ? 0 : y0;
  const ay = (x0 <= 0 && x1 >= 0) ? 0 : x0;
  g.appendChild(el("line", { x1: x(x0), y1: y(ax), x2: x(x1), y2: y(ax), class: "axis" }));
  g.appendChild(el("line", { x1: x(ay), y1: y(y0), x2: x(ay), y2: y(y1), class: "axis" }));
}

// Deterministic pseudo-random generator (so demos are reproducible).
function mulberry32(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Standard-normal sample via Box–Muller, fed by a uniform rng.
function gauss(rng) {
  let u = 0, v = 0;
  while (u === 0) u = rng();
  while (v === 0) v = rng();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}
