/* Shared helpers for the interactive SVG widgets (linear-algebra track).
   Same base as DT/theory/assets/common.js, plus vector helpers: arrows,
   pointer→SVG coordinate conversion and drag. Russian UI strings live in pages. */

const NS = "http://www.w3.org/2000/svg";

// Linear scale factory: maps a data domain onto a pixel range.
// Call scale(range, domain) to get the inverse (pixel -> data).
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

// Draw axes + light grid into a group. cfg: {x:scaleX, y:scaleY, x0,x1,y0,y1, xticks, yticks}
function drawFrame(g, cfg) {
  const { x, y, x0, x1, y0, y1, xticks = [], yticks = [] } = cfg;
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

// ---- vector-specific helpers ------------------------------------------------

const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

// An arrow (shaft + head) from (x1,y1) to (x2,y2) in PIXEL coords. Returns a <g>.
function arrow(x1, y1, x2, y2, opt = {}) {
  const g = el("g");
  const color = opt.color || "#2f6f4f";
  const w = opt.width || 2.6;
  const dash = opt.dash || null;
  const line = { x1, y1, x2, y2, stroke: color, "stroke-width": w, "stroke-linecap": "round" };
  if (dash) line["stroke-dasharray"] = dash;
  g.appendChild(el("line", line));
  const len = Math.hypot(x2 - x1, y2 - y1);
  if (len > 4) {                       // only draw a head if the arrow is visible
    const ang = Math.atan2(y2 - y1, x2 - x1), hl = opt.head || 12, ha = 0.42;
    const p1x = x2 - hl * Math.cos(ang - ha), p1y = y2 - hl * Math.sin(ang - ha);
    const p2x = x2 - hl * Math.cos(ang + ha), p2y = y2 - hl * Math.sin(ang + ha);
    g.appendChild(el("polygon", { points: `${x2},${y2} ${p1x},${p1y} ${p2x},${p2y}`, fill: color }));
  }
  return g;
}

// Pointer (mouse/touch) event -> SVG user coordinates.
function svgPoint(svg, evt) {
  const pt = svg.createSVGPoint();
  const src = evt.touches && evt.touches.length ? evt.touches[0] : evt;
  pt.x = src.clientX; pt.y = src.clientY;
  return pt.matrixTransform(svg.getScreenCTM().inverse());
}

// Make an element draggable. `cb` receives the SVG-space point on every move.
function onDrag(svg, handle, cb) {
  let on = false;
  const start = e => { on = true; e.preventDefault(); };
  const move = e => { if (!on) return; e.preventDefault(); cb(svgPoint(svg, e)); };
  const stop = () => { on = false; };
  handle.style.cursor = "grab";
  handle.addEventListener("mousedown", start);
  handle.addEventListener("touchstart", start, { passive: false });
  window.addEventListener("mousemove", move);
  window.addEventListener("touchmove", move, { passive: false });
  window.addEventListener("mouseup", stop);
  window.addEventListener("touchend", stop);
}
