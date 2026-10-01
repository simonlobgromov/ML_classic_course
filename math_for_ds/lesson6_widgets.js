/* Self-contained SVG widgets embedded by build_lesson6.py. No network or Python callbacks. */
(function (global) {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const C = { blue: "#6ab0f3", green: "#5fd08a", gold: "#e0b25a", rose: "#e0757f", ink: "#e6e9ec", soft: "#a7b0ba", grid: "#293440" };
  const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
  const pdf = z => Math.exp(-z * z / 2) / Math.sqrt(2 * Math.PI);
  // erfc approximation: absolute error below 1.5e-7; direct tail evaluation avoids cancellation.
  function erfc(x) {
    const t = 1 / (1 + 0.5 * Math.abs(x));
    const value = t * Math.exp(-x * x - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));
    return x >= 0 ? value : 2 - value;
  }
  const sf = z => z === 0 ? 0.5 : clamp(0.5 * erfc(z / Math.SQRT2), 0, 1);
  const cdf = z => sf(-z);
  function interval(a, b) {
    if (a >= b) return 0;
    return clamp(a >= 0 ? sf(a) - sf(b) : cdf(b) - cdf(a), 0, 1);
  }
  const fmt = (v, digits = 3) => Math.abs(v) > 0 && Math.abs(v) < Math.pow(10, -digits) ? v.toExponential(2) : v.toFixed(digits).replace(/\.?0+$/, "").replace(/^-0$/, "0");
  const pct = p => (100 * p).toFixed(p < 0.001 && p > 0 ? 5 : 2) + "%";
  function rng(seed) {
    return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  }
  function gaussian(random) {
    return Math.sqrt(-2 * Math.log(Math.max(random(), 1e-12))) * Math.cos(2 * Math.PI * random());
  }
  const mean = a => a.reduce((s, x) => s + x, 0) / a.length;
  const std = a => { const m = mean(a); return Math.sqrt(mean(a.map(x => (x - m) ** 2))); };
  function node(tag, attrs = {}, text = "") {
    const e = document.createElementNS(NS, tag);
    Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, String(v)));
    if (text !== "") e.textContent = text;
    return e;
  }
  function text(svg, x, y, value, color = C.soft, anchor = "middle", size = 12) {
    svg.appendChild(node("text", { x, y, fill: color, "text-anchor": anchor, "font-family": "system-ui,sans-serif", "font-size": size }, value));
  }
  function frame(svg, domain, ymax, xlabel, ylabel, title, xticks = null) {
    svg.replaceChildren();
    svg.setAttribute("viewBox", "0 0 620 350");
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", title + ". " + xlabel + "; " + ylabel);
    svg.appendChild(node("title", {}, title));
    const [lo, hi] = domain, L = 68, R = 600, T = 49, B = 291;
    const sx = x => L + (x - lo) / (hi - lo) * (R - L);
    const sy = y => B - y / ymax * (B - T);
    text(svg, L, 22, title, C.ink, "start", 14);
    text(svg, L, 40, ylabel, C.soft, "start", 11);
    for (let i = 0; i <= 4; i++) {
      const value = ymax * i / 4, yy = sy(value);
      svg.appendChild(node("line", { x1: L, x2: R, y1: yy, y2: yy, stroke: C.grid }));
      text(svg, L - 9, yy + 4, fmt(value, 3), C.soft, "end", 11);
    }
    for (const value of xticks || Array.from({ length: 7 }, (_, i) => lo + (hi - lo) * i / 6)) {
      const xx = sx(value);
      svg.appendChild(node("line", { x1: xx, x2: xx, y1: T, y2: B, stroke: C.grid, "stroke-opacity": 0.5 }));
      text(svg, xx, B + 19, fmt(value, 2), C.soft, "middle", 11);
    }
    text(svg, (L + R) / 2, 338, xlabel, C.ink, "middle", 12);
    return { svg, lo, hi, ymax, L, R, T, B, sx, sy };
  }
  function curve(p, f, color = C.blue, width = 2.5) {
    let d = "";
    for (let i = 0; i <= 400; i++) { const x = p.lo + (p.hi - p.lo) * i / 400; d += (i ? " L " : "M ") + p.sx(x) + " " + p.sy(f(x)); }
    p.svg.appendChild(node("path", { d, fill: "none", stroke: color, "stroke-width": width }));
  }
  function shade(p, f, a, b, color = C.green) {
    a = clamp(a, p.lo, p.hi); b = clamp(b, p.lo, p.hi);
    if (a >= b) return;
    let d = `M ${p.sx(a)} ${p.B}`;
    for (let i = 0; i <= 180; i++) { const x = a + (b - a) * i / 180; d += ` L ${p.sx(x)} ${p.sy(f(x))}`; }
    d += ` L ${p.sx(b)} ${p.B} Z`;
    p.svg.appendChild(node("path", { d, fill: color, "fill-opacity": 0.3, "data-shading": "probability" }));
  }
  function marker(p, x, label, color = C.gold, row = 0) {
    if (x < p.lo || x > p.hi) return;
    p.svg.appendChild(node("line", { x1: p.sx(x), x2: p.sx(x), y1: p.T, y2: p.B, stroke: color, "stroke-width": 1.6, "stroke-dasharray": "5 4" }));
    text(p.svg, clamp(p.sx(x), p.L + 48, p.R - 48), p.T + 15 + 17 * row, label, color, "middle", 12);
  }
  function range(root, key) { return Number(root.querySelector(`[data-control="${key}"]`).value); }
  function value(root, key) { return root.querySelector(`[data-control="${key}"]`).value; }
  const chart = (root, key) => root.querySelector(`[data-chart="${key}"]`);
  function output(root, html) { root.querySelector("[data-readout]").innerHTML = html; }
  function syncLabels(root) {
    root.querySelectorAll("input[type=range][data-control]").forEach(input => {
      const label = root.querySelector(`[data-value="${input.dataset.control}"]`);
      if (label) label.textContent = fmt(Number(input.value), 3);
    });
  }
  function listen(root, render) {
    root.querySelectorAll("[data-control]").forEach(input => input.addEventListener("input", () => { syncLabels(root); render(); }));
    syncLabels(root); render();
  }
  function ordered(root, ka, kb) {
    const a = range(root, ka), b = range(root, kb);
    return [Math.min(a, b), Math.max(a, b)];
  }

  function histogram(root) {
    let seed = 71, data = [];
    const generate = () => { const random = rng(seed); data = Array.from({ length: 2000 }, () => 170 + 10 * gaussian(random)); };
    generate();
    function render() {
      const n = range(root, "n"), width = range(root, "width"), mode = value(root, "mode");
      const sample = data.slice(0, n), lo = Math.floor(Math.min(130, ...sample) / width) * width;
      const hi = Math.ceil(Math.max(210, ...sample) / width) * width + width;
      const bins = Array.from({ length: Math.round((hi - lo) / width) }, () => 0);
      sample.forEach(x => bins[Math.min(bins.length - 1, Math.floor((x - lo) / width))]++);
      const j = clamp(Math.floor((range(root, "bin") - lo) / width), 0, bins.length - 1);
      const heights = bins.map(count => mode === "count" ? count : mode === "share" ? count / n : count / (n * width));
      const yLabel = mode === "count" ? "Количество, человек" : mode === "share" ? "Доля наблюдений в бине" : "Плотность, 1/см";
      const p = frame(chart(root, "hist"), [lo, hi], Math.max(...heights, mode === "density" ? pdf(0) / 10 : 0) * 1.17, "Рост x, см", yLabel, "Одна выборка — три нормировки");
      heights.forEach((h, i) => {
        const rect = node("rect", { x: p.sx(lo + i * width) + 0.7, y: p.sy(h), width: (p.R - p.L) / bins.length - 1.4, height: p.B - p.sy(h), fill: i === j ? C.green : C.blue, "fill-opacity": i === j ? 0.85 : 0.45, tabindex: 0, role: "button", "aria-label": `Бин от ${lo + i * width} до ${lo + (i + 1) * width}: ${bins[i]} человек` });
        const pick = () => { root.querySelector('[data-control="bin"]').value = lo + (i + 0.5) * width; syncLabels(root); render(); };
        rect.addEventListener("click", pick);
        rect.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); } });
        p.svg.appendChild(rect);
      });
      if (mode === "density") curve(p, x => pdf((x - 170) / 10) / 10, C.gold);
      const a = lo + j * width, b = a + width, share = bins[j] / n;
      root.dataset.selectedCount = bins[j]; root.dataset.sampleSize = n;
      output(root, `<b>Выбранный бин: [${fmt(a)}; ${fmt(b)}) см.</b> В нём ${bins[j]} из ${n} человек: доля ${pct(share)}.<br>Высота = ${fmt(heights[j], 5)}${mode === "density" ? " 1/см" : ""}; ширина = ${width} см; площадь = ${fmt(heights[j] * width, 5)}.<br>${mode === "density" ? `<b>Площадь выбранного столбика = доля ${pct(share)}. Сумма площадей всех столбиков = 1.</b><br>Жёлтая кривая — известная модель генерации; её вероятность этого интервала = ${pct(interval((a - 170) / 10, (b - 170) / 10))}.` : "Площадь здесь не равна доле: для такого чтения выберите «плотность»."}`);
    }
    root.querySelector('[data-action="resample"]').addEventListener("click", () => { seed++; generate(); render(); });
    listen(root, render);
  }

  function discrete(root) {
    function render() {
      const p = range(root, "p"), selected = range(root, "selected");
      const g = frame(chart(root, "pmf"), [-0.5, 1.5], 1.1, "Возможное значение x", "Вероятность P(X = x)", "Бернулли: вероятность отдельного значения");
      [1 - p, p].forEach((prob, i) => {
        const color = i === selected ? C.green : C.blue;
        g.svg.appendChild(node("line", { x1: g.sx(i), x2: g.sx(i), y1: g.B, y2: g.sy(prob), stroke: color, "stroke-width": 5 }));
        g.svg.appendChild(node("circle", { cx: g.sx(i), cy: g.sy(prob), r: 7, fill: color }));
        text(g.svg, g.sx(i), g.sy(prob) - 12, pct(prob), color);
      });
      output(root, `Выбрано x = ${selected}. <b>P(X = ${selected}) = ${pct(selected ? p : 1 - p)}.</b><br>Это график вероятностей двух отдельных значений. Сумма вероятностей: (1 − p) + p = 1. Ширина нарисованной линии не участвует в расчёте.`);
    }
    listen(root, render);
  }

  function density(root) {
    function render() {
      const center = range(root, "center"), width = range(root, "width"), meters = value(root, "unit") === "m", factor = meters ? 100 : 1;
      const mu = 170 / factor, sd = 10 / factor, a = (center - width / 2) / factor, b = (center + width / 2) / factor, x = center / factor;
      const f = t => pdf((t - mu) / sd) / sd, unit = meters ? "м" : "см";
      const p = frame(chart(root, "density"), [130 / factor, 210 / factor], pdf(0) / sd * 1.2, `Рост x, ${unit}`, `Плотность, 1/${unit}`, "Высота и площадь — разные величины");
      shade(p, f, a, b);
      p.svg.appendChild(node("rect", { x: p.sx(a), y: p.sy(f(x)), width: p.sx(b) - p.sx(a), height: p.B - p.sy(f(x)), fill: "none", stroke: C.gold, "stroke-width": 2, "stroke-dasharray": "5 3" }));
      curve(p, f); marker(p, x, `x = ${fmt(x)}`);
      const probability = interval((center - width / 2 - 170) / 10, (center + width / 2 - 170) / 10);
      output(root, `<b>Площадь интервала = ${pct(probability)}.</b> Высота в центре f(x) = ${fmt(f(x), 5)} 1/${unit}.<br>Ширина Δ = ${fmt(width / factor, 4)} ${unit}. Жёлтый прямоугольник: f(x) · Δ = ${fmt(f(x) * width / factor, 6)} ≈ ${pct(f(x) * width / factor)}.<br>${width === 0 ? "<b>Ширина 0 → площадь 0 → P(X = x) = 0, хотя высота кривой может быть положительной.</b>" : "Зелёная площадь — вероятность; прямоугольник — приближение, которое улучшается при уменьшении интервала."}<br>${meters ? "После перехода в метры плотность в центре может быть выше 1. Вероятность того же события не изменилась." : "Переключите сантиметры на метры: меняются числа на осях и высота, но вероятность сохраняется."}`);
      root.dataset.probability = probability;
    }
    listen(root, render);
  }

  function rectangles(root) {
    function render() {
      const [a, b] = ordered(root, "a", "b"), n = range(root, "n"), width = (b - a) / n;
      const p = frame(chart(root, "rectangles"), [-4, 4], 0.48, "Значение x", "Плотность f(x)", "Интеграл как сумма площадей прямоугольников");
      shade(p, pdf, a, b);
      let sum = 0;
      for (let i = 0; i < n; i++) {
        const left = a + i * width, h = pdf(left + width / 2); sum += h * width;
        p.svg.appendChild(node("rect", { x: p.sx(left), y: p.sy(h), width: p.sx(left + width) - p.sx(left), height: p.B - p.sy(h), fill: C.gold, "fill-opacity": 0.13, stroke: C.gold, "stroke-width": 0.8 }));
      }
      curve(p, pdf); marker(p, a, `a = ${fmt(a)}`, C.green); marker(p, b, `b = ${fmt(b)}`, C.gold, 1);
      const exact = interval(a, b);
      output(root, `Границы: a = ${fmt(a)}, b = ${fmt(b)}. Прямоугольников m = ${n}; ширина Δ = ${fmt(width, 5)}.<br>Сумма площадей Σ f(tᵢ)Δ ≈ <b>${fmt(sum, 6)}</b>. Вероятность по модели ≈ <b>${fmt(exact, 6)} (${pct(exact)})</b>.<br>Абсолютное расхождение ≈ ${fmt(Math.abs(sum - exact), 7)}. Больше прямоугольников обычно даёт более точное приближение; равные границы дают нулевую площадь.`);
      root.dataset.approximation = sum; root.dataset.probability = exact;
    }
    listen(root, render);
  }

  function cumulative(root) {
    function render() {
      const x = range(root, "x"), probability = cdf(x), slope = pdf(x);
      const p = frame(chart(root, "pdf"), [-4, 4], 0.48, "Порог x", "PDF: плотность f(x)", "PDF: вероятность показана площадью");
      shade(p, pdf, -Infinity, x); curve(p, pdf); marker(p, x, `x = ${fmt(x)}`);
      p.svg.appendChild(node("circle", { cx: p.sx(x), cy: p.sy(slope), r: 6, fill: C.rose }));
      const q = frame(chart(root, "cdf"), [-4, 4], 1.06, "Тот же порог x", "CDF: накопленная вероятность F(x)", "CDF: вероятность показана высотой");
      curve(q, cdf, C.green); marker(q, x, `x = ${fmt(x)}`);
      q.svg.appendChild(node("line", { x1: q.L, x2: q.sx(x), y1: q.sy(probability), y2: q.sy(probability), stroke: C.gold, "stroke-dasharray": "5 4" }));
      // Keep the local tangent inside the probability chart without changing its slope.
      const tangentLeft = Math.max(q.lo, x - 0.65, x - probability / slope);
      const tangentRight = Math.min(q.hi, x + 0.65, x + (1 - probability) / slope);
      q.svg.appendChild(node("line", { x1: q.sx(tangentLeft), x2: q.sx(tangentRight), y1: q.sy(probability + slope * (tangentLeft - x)), y2: q.sy(probability + slope * (tangentRight - x)), stroke: C.rose, "stroke-width": 3, "data-tangent": "cdf" }));
      q.svg.appendChild(node("circle", { cx: q.sx(x), cy: q.sy(probability), r: 6, fill: C.gold }));
      output(root, `<b>CDF: F(${fmt(x)}) = P(X ≤ ${fmt(x)}) ≈ ${fmt(probability, 6)} = ${pct(probability)}.</b><br>PDF: f(${fmt(x)}) ≈ ${fmt(slope, 6)}. <b>Производная CDF: F′(${fmt(x)}) = f(${fmt(x)}).</b><br>Розовая касательная на CDF имеет наклон ${fmt(slope, 6)}; это высота розовой точки на PDF. Наклон сравнивается в единицах осей, а не в пикселях.<br>Справа от порога: 1 − F(x) ≈ ${pct(sf(x))}. Передвиньте порог вправо: накопленная вероятность не уменьшается.`);
      root.dataset.probability = probability; root.dataset.density = slope;
    }
    listen(root, render);
  }

  function standardized(root) {
    let previousLock = "x";
    function render() {
      const mu = range(root, "mu"), sigma = range(root, "sigma"), mode = value(root, "event"), lock = value(root, "lock");
      const inputA = root.querySelector('[data-control="a"]'), inputB = root.querySelector('[data-control="b"]');
      if (lock !== previousLock) {
        const oldA = Number(inputA.value), oldB = Number(inputB.value);
        inputA.min = inputB.min = lock === "z" ? -4 : 80;
        inputA.max = inputB.max = lock === "z" ? 4 : 260;
        inputA.step = inputB.step = lock === "z" ? 0.05 : 0.5;
        inputA.value = lock === "z" ? clamp((oldA - mu) / sigma, -4, 4) : mu + sigma * oldA;
        inputB.value = lock === "z" ? clamp((oldB - mu) / sigma, -4, 4) : mu + sigma * oldB;
        previousLock = lock;
      }
      syncLabels(root);
      const [low, high] = ordered(root, "a", "b");
      // For one-sided events the first handle is the threshold; the second is disabled.
      const twoBounds = mode === "interval" || mode === "outside";
      inputB.disabled = !twoBounds;
      const vA = twoBounds ? low : Number(inputA.value), vB = twoBounds ? high : Number(inputA.value);
      const a = lock === "z" ? mu + sigma * vA : vA, b = lock === "z" ? mu + sigma * vB : vB;
      const za = (a - mu) / sigma, zb = (b - mu) / sigma;
      root.querySelector('[data-bound-label="a"]').textContent = lock === "z" ? "Граница A в z" : "Граница A, см";
      root.querySelector('[data-bound-label="b"]').textContent = lock === "z" ? "Граница B в z" : "Граница B, см";
      const zlo = Math.min(-4, za - 0.35, zb - 0.35), zhi = Math.max(4, za + 0.35, zb + 0.35);
      const f = x => pdf((x - mu) / sigma) / sigma;
      const px = frame(chart(root, "raw"), [mu + sigma * zlo, mu + sigma * zhi], pdf(0) / sigma * 1.2, "Рост x, см", "Плотность fₓ(x), 1/см", `Исходная шкала: μ = ${fmt(mu)}, σ = ${fmt(sigma)}`);
      const pz = frame(chart(root, "standard"), [zlo, zhi], 0.48, "z = (x − μ) / σ", "Плотность φ(z)", "Стандартная нормаль: среднее 0, σ = 1");
      let parts, probability, event;
      if (mode === "left") { parts = [[-Infinity, za]]; probability = cdf(za); event = `X ≤ ${fmt(a)} ↔ Z ≤ ${fmt(za)}`; }
      else if (mode === "right") { parts = [[za, Infinity]]; probability = sf(za); event = `X ≥ ${fmt(a)} ↔ Z ≥ ${fmt(za)}`; }
      else if (mode === "outside") { parts = [[-Infinity, za], [zb, Infinity]]; probability = cdf(za) + sf(zb); event = `X вне [${fmt(a)}; ${fmt(b)}] ↔ Z вне [${fmt(za)}; ${fmt(zb)}]`; }
      else { parts = [[za, zb]]; probability = interval(za, zb); event = `${fmt(a)} ≤ X ≤ ${fmt(b)} ↔ ${fmt(za)} ≤ Z ≤ ${fmt(zb)}`; }
      for (const [lo, hi] of parts) { shade(pz, pdf, lo, hi); shade(px, f, mu + sigma * lo, mu + sigma * hi); }
      curve(px, f); curve(pz, pdf);
      marker(px, a, `a = ${fmt(a)}`); marker(pz, za, `zₐ = ${fmt(za)}`);
      if (twoBounds) { marker(px, b, `b = ${fmt(b)}`, C.green, 1); marker(pz, zb, `zᵦ = ${fmt(zb)}`, C.green, 1); }
      output(root, `<b>${event}.</b><br>zₐ = (${fmt(a)} − ${fmt(mu)}) / ${fmt(sigma)} = ${fmt(za, 4)}${twoBounds ? `; zᵦ = (${fmt(b)} − ${fmt(mu)}) / ${fmt(sigma)} = ${fmt(zb, 4)}` : ""}.<br><b>Вероятность на обоих графиках: ${fmt(probability, 7)} = ${pct(probability)}.</b><br>${lock === "z" ? "Границы закреплены в z: при изменении μ и σ исходные пороги перемещаются, вероятность сохраняется." : "Границы закреплены в сантиметрах: при изменении μ и σ меняются z-оценки и вероятность события."}`);
      root.dataset.probability = probability; root.dataset.za = za; root.dataset.zb = zb;
    }
    root.querySelectorAll("[data-preset]").forEach(button => button.addEventListener("click", () => {
      root.querySelector('[data-control="lock"]').value = "x";
      root.querySelector('[data-control="mu"]').value = 170;
      root.querySelector('[data-control="sigma"]').value = 10;
      render();
      const preset = button.dataset.preset;
      root.querySelector('[data-control="event"]').value = preset === "tail" ? "right" : "interval";
      root.querySelector('[data-control="a"]').value = preset === "tail" ? 190 : 175;
      root.querySelector('[data-control="b"]').value = preset === "tail" ? 200 : 185;
      render();
    }));
    listen(root, render);
  }

  function sigmas(root) {
    function render() {
      const k = range(root, "k"), event = value(root, "event"), p = frame(chart(root, "sigmas"), [-4.5, 4.5], 0.48, "Стандартизированный рост z = (x − 170) / 10", "Плотность φ(z)", "Какая область отвечает на наш вопрос?");
      const one = sf(k), both = 2 * one, inside = interval(-k, k);
      const low = 170 - 10 * k, high = 170 + 10 * k;
      const probability = event === "inside" ? inside : event === "outside" ? both : one;
      const question = event === "inside" ? `Рост от ${fmt(low)} до ${fmt(high)} см?` : event === "outside" ? `Рост ниже ${fmt(low)} или выше ${fmt(high)} см?` : `Рост от ${fmt(high)} см?`;
      const eventText = event === "inside" ? `${fmt(low)} ≤ X ≤ ${fmt(high)} ↔ −${fmt(k)} ≤ Z ≤ ${fmt(k)}` : event === "outside" ? `X < ${fmt(low)} или X > ${fmt(high)} ↔ |Z| > ${fmt(k)}` : `X ≥ ${fmt(high)} ↔ Z ≥ ${fmt(k)}`;
      if (event === "inside") shade(p, pdf, -k, k);
      else { shade(p, pdf, k, Infinity, C.rose); if (event === "outside") shade(p, pdf, -Infinity, -k, C.rose); }
      curve(p, pdf);
      if (event !== "right") marker(p, -k, `z = ${fmt(-k)}; ${fmt(low)} см`, C.gold);
      marker(p, k, `z = ${fmt(k)}; ${fmt(high)} см`, C.gold, event === "right" ? 0 : 1);
      output(root, `<b>Вопрос: ${question}</b><br>Событие: ${eventText}. X — рост в см, Z — рост в стандартной шкале.<br><b>Площадь закрашенной области ≈ ${fmt(probability, 7)} = ${pct(probability)}.</b><br>Границы: 170 ± 10 · k см, где k = ${fmt(k)} — расстояние от среднего в стандартных отклонениях. Для одного правого хвоста нужна только верхняя граница.<br>При этом k: середина ${pct(inside)}, оба хвоста ${pct(both)}, один правый хвост ${pct(one)}. Выбирайте вероятность по формулировке вопроса.`);
      root.dataset.inside = inside; root.dataset.bothTails = both; root.dataset.rightTail = one;
      root.dataset.probability = probability;
    }
    root.querySelectorAll("[data-k]").forEach(b => b.addEventListener("click", () => { root.querySelector('[data-control="k"]').value = b.dataset.k; syncLabels(root); render(); }));
    listen(root, render);
  }

  function simulation(root) {
    let seed = 129, normal = [], mixture = [];
    let scenario = "", lastSeed = null, repetition = 0, history = [];
    let axisScenario = "", historyYmax = 0;
    function generate() {
      const random = rng(seed);
      normal = Array.from({ length: 10000 }, () => 170 + 10 * gaussian(random));
      mixture = Array.from({ length: 10000 }, () => 170 + (random() < 0.5 ? -8 : 8) + 6 * gaussian(random));
    }
    generate();
    function render() {
      const n = range(root, "n"), threshold = range(root, "threshold"), isMixture = value(root, "model") === "mixture";
      const sample = (isMixture ? mixture : normal).slice(0, n), count = sample.filter(x => x >= threshold).length;
      const known = isMixture ? 0.5 * sf((threshold - 162) / 6) + 0.5 * sf((threshold - 178) / 6) : sf((threshold - 170) / 10);
      const assumed = sf((threshold - 170) / 10), theoretical = x => isMixture ? (pdf((x - 162) / 6) + pdf((x - 178) / 6)) / 12 : pdf((x - 170) / 10) / 10;
      // Only compare samples generated under the same conditions. A redraw must
      // not masquerade as a new experiment; a resample click advances the seed.
      const nextScenario = `${n}:${threshold}:${isMixture}`;
      if (nextScenario !== scenario) { scenario = nextScenario; history = []; repetition = 0; lastSeed = null; }
      if (seed !== lastSeed) {
        history.push({ index: ++repetition, fraction: count / n });
        history = history.slice(-20); lastSeed = seed;
      }
      const lo = Math.floor(Math.min(125, ...sample) / 2) * 2, hi = Math.ceil(Math.max(215, ...sample) / 2) * 2 + 2;
      const bins = Array.from({ length: Math.round((hi - lo) / 2) }, () => 0);
      sample.forEach(x => bins[Math.min(bins.length - 1, Math.floor((x - lo) / 2))]++);
      const p = frame(chart(root, "sim"), [lo, hi], Math.max(...bins.map(c => c / (n * 2)), 0.05) * 1.16, "Значение x, см", "Плотность, 1/см", "Выборка и вероятностная модель");
      bins.forEach((c, i) => p.svg.appendChild(node("rect", { x: p.sx(lo + i * 2) + 0.4, y: p.sy(c / (n * 2)), width: p.sx(lo + (i + 1) * 2) - p.sx(lo + i * 2) - 0.8, height: p.B - p.sy(c / (n * 2)), fill: C.soft, "fill-opacity": 0.32 })));
      shade(p, theoretical, threshold, Infinity); curve(p, theoretical, C.green);
      if (isMixture) curve(p, x => pdf((x - 170) / 10) / 10, C.gold);
      marker(p, threshold, `Порог = ${fmt(threshold)}`);

      const first = history[0].index, last = Math.max(first + 19, repetition);
      // Retain the vertical scale when changing n, so a tighter cluster is
      // visible rather than immediately stretched back to the chart's height.
      const nextAxisScenario = `${threshold}:${isMixture}`;
      if (nextAxisScenario !== axisScenario) {
        axisScenario = nextAxisScenario;
        historyYmax = Math.min(100, Math.max(5, 200 * Math.max(known, assumed)));
      }
      historyYmax = Math.min(100, Math.max(historyYmax, ...history.map(h => 118 * h.fraction)));
      const ticks = Array.from({ length: 5 }, (_, i) => first + Math.round(19 * i / 4));
      const q = frame(chart(root, "repeats"), [first - 0.5, last + 0.5], historyYmax, "Номер новой выборки (последние 20)", "Доля / вероятность, %", "Одна точка — результат одной выборки", ticks);
      const probabilityLine = (probability, color, label) => {
        q.svg.appendChild(node("line", { x1: q.L, x2: q.R, y1: q.sy(100 * probability), y2: q.sy(100 * probability), stroke: color, "stroke-width": 2, "stroke-dasharray": "6 4", "data-probability": label }));
      };
      probabilityLine(known, C.green, "generator");
      if (isMixture && Math.abs(known - assumed) > 1e-12) probabilityLine(assumed, C.gold, "normal");
      history.forEach((h, i) => {
        const dot = node("circle", { cx: q.sx(h.index), cy: q.sy(100 * h.fraction), r: i === history.length - 1 ? 6 : 4, fill: C.blue, stroke: C.ink, "stroke-width": i === history.length - 1 ? 1.5 : 0, "data-repetition": h.index });
        dot.appendChild(node("title", {}, `Выборка ${h.index}: ${pct(h.fraction)} значений от ${fmt(threshold)} см`));
        q.svg.appendChild(dot);
      });
      const modelText = isMixture ? `<span style="color:${C.gold}">Нормальная модель</span>: вероятность ${pct(assumed)}; ожидаемое количество ${fmt(n * assumed, 2)}.<br><span style="color:${C.green}">Генератор смеси</span>: вероятность ${pct(known)}; ожидаемое количество ${fmt(n * known, 2)}.` : `<span style="color:${C.green}">Нормальная модель = закон генератора</span>: вероятность <b>${pct(assumed)}</b>; ожидаемое количество <b>${fmt(n * assumed, 2)}</b>.`;
      output(root, `<b>Событие: рост от ${fmt(threshold)} см. В каждой выборке ${n} наблюдений.</b><br>${modelText}<br><span style="color:${C.blue}">Последняя выборка № ${repetition}</span>: количество <b>${count}</b>; доля <b>${count}/${n} = ${pct(count / n)}</b>.<br>Справа показано ${history.length} из ${repetition} повторений. Линии — вероятности, точки — наблюдаемые доли. При смене условий история начинается заново. При смене n масштаб вертикальной оси сохраняется и расширяется, только если новая точка не помещается.<br>${isMixture ? (Math.abs(known - assumed) < 1e-12 ? "При этом пороге вероятности совпадают, зелёная линия общая для обеих моделей. Их плотности всё равно различаются." : "Точки из смеси колеблются вокруг зелёной вероятности. Большее n снижает случайный разброс долей, но не сближает две модельные вероятности.") : "Новая выборка может дать другое количество и другую долю. Вероятность и ожидаемое количество остаются прежними. При сравнении размеров выборок смотрите на числа вертикальной оси."}`);
      root.dataset.empirical = count / n; root.dataset.probability = known; root.dataset.assumed = assumed;
      root.dataset.expectedCount = n * assumed; root.dataset.observedCount = count;
      root.dataset.repetitions = repetition; root.dataset.historyLength = history.length;
    }
    root.querySelector('[data-action="resample"]').addEventListener("click", () => { seed++; generate(); render(); });
    listen(root, render);
  }

  const widgets = { histogram, discrete, density, rectangles, cumulative, standardized, sigmas, simulation };
  global.DistributionLesson6 = { mount: (root, kind) => { if (!root || !widgets[kind]) throw new Error("Unknown lesson widget: " + kind); widgets[kind](root); }, math: { pdf, cdf, sf, interval, rng, gaussian } };
})(typeof window !== "undefined" ? window : globalThis);
