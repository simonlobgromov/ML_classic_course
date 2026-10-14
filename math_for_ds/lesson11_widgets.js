/* Standalone rank visualizations, embedded into 11_linear_dependence_rank.ipynb. */
(function (global) {
  'use strict';
  const C = {blue:'#6ab0f3', green:'#5fd08a', gold:'#e0b25a', rose:'#e0757f', violet:'#bd9ce8', ink:'#e6e9ec', soft:'#a7b0ba', grid:'#293440', bg:'#111820'};
  const fmt = x => Math.abs(x) < 1e-10 ? '0' : String(Number(Number(x).toFixed(2)));
  const vector = x => '(' + x.map(fmt).join('; ') + ')';
  const clamp = (x, lo, hi) => Math.max(lo, Math.min(hi, x));
  const dot = (a, b) => {
    if (a.length !== b.length) throw new Error('Vector dimensions do not agree');
    return a.reduce((sum, value, i) => sum + value * b[i], 0);
  };
  const matvec = (A, x) => A.map(row => dot(row, x));
  const combination = (a, b, lambda, mu) => a.map((x, i) => lambda * x + mu * b[i]);
  // Only small, well-separated teaching examples use this elimination helper.
  function rank(A, tolerance = 1e-10) {
    if (!A.length || !A[0].length) return 0;
    const work = A.map(row => [...row]), rows = work.length, cols = work[0].length;
    let r = 0;
    for (let j = 0; j < cols && r < rows; j++) {
      let pivot = r;
      for (let i = r + 1; i < rows; i++) if (Math.abs(work[i][j]) > Math.abs(work[pivot][j])) pivot = i;
      if (Math.abs(work[pivot][j]) <= tolerance) continue;
      [work[r], work[pivot]] = [work[pivot], work[r]];
      const value = work[r][j];
      for (let k = j; k < cols; k++) work[r][k] /= value;
      for (let i = r + 1; i < rows; i++) {
        const factor = work[i][j];
        for (let k = j; k < cols; k++) work[i][k] -= factor * work[r][k];
      }
      r++;
    }
    return r;
  }
  const orders = delta => [[1,2,3 + delta],[2,1,3],[1,3,4],[3,2,5]];
  const selectedColumns = (A, selected) => A.map(row => selected.map(j => row[j]));
  const presets = {identity:[[1,0],[0,1]], rank1:[[1,1],[2,2]], zero:[[0,0],[0,0]]};
  const volumes = [1, 1.5, 2, 2.5];
  function weightResult(t) {
    const w = [300 - 1000 * t, t];
    const parts = volumes.map(v => [v * w[0], 1000 * v * w[1]]);
    return {weights:w, parts, total:parts.map(row => row[0] + row[1])};
  }
  function node(tag, attrs = {}, value) {
    const e = document.createElement(tag);
    for (const [key, val] of Object.entries(attrs)) e.setAttribute(key, String(val));
    if (value !== undefined) e.textContent = value;
    return e;
  }
  function svgNode(tag, attrs = {}, value) {
    const e = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [key, val] of Object.entries(attrs)) e.setAttribute(key, String(val));
    if (value !== undefined) e.textContent = value;
    return e;
  }
  function svgText(svg, x, y, value, color = C.soft, anchor = 'middle', size = 12) {
    svg.appendChild(svgNode('text', {x,y,fill:color,'text-anchor':anchor,'font-size':size,'font-family':'system-ui,sans-serif'}, value));
  }
  function line(svg, x1, y1, x2, y2, color, width = 1, attrs = {}) {
    svg.appendChild(svgNode('line', {x1,y1,x2,y2,stroke:color,'stroke-width':width,...attrs}));
  }
  function style(root) {
    root.classList.add('r11');
    root.appendChild(node('style', {}, `
      .r11 .r11-controls{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin:12px 0}
      .r11 .r11-control{display:flex;flex-direction:column;gap:5px;color:${C.ink};font-size:14px;min-width:170px}
      .r11 [hidden]{display:none!important}
      .r11 select,.r11 button{font:inherit;background:#18232f;color:${C.ink};border:1px solid #405164;border-radius:6px;padding:7px 10px;cursor:pointer}
      .r11 button:focus-visible,.r11 select:focus-visible,.r11 input:focus-visible{outline:3px solid ${C.gold};outline-offset:3px}
      .r11 button[aria-pressed=true]{background:#24435f;border-color:${C.blue};color:white}
      .r11 input[type=range]{width:170px;accent-color:${C.blue}}
      .r11 input[type=checkbox]{accent-color:${C.blue};width:18px;height:18px}
      .r11 .r11-check{display:flex;align-items:center;gap:7px;color:${C.ink};font-size:14px}
      .r11 .r11-plots{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:10px}
      .r11 .r11-plot{min-width:0;background:#0f151d;border:1px solid ${C.grid};border-radius:8px}
      .r11 .r11-plot svg{width:100%;height:auto;display:block;max-height:520px}
      .r11 .r11-table-wrap{overflow-x:auto;margin:14px 0}
      .r11 table{border-collapse:collapse;color:${C.ink};font-size:14px;font-variant-numeric:tabular-nums;width:100%}
      .r11 th,.r11 td{padding:9px 12px;text-align:center;border-bottom:1px solid ${C.grid}}
      .r11 th{font-weight:500;color:${C.soft}}
      .r11 .r11-selected{background:#203343;color:${C.blue}}
      .r11 .r11-modified{color:${C.gold};font-weight:700}
      .r11 .r11-note{font-size:14px;line-height:1.6;color:${C.soft};margin:9px 0}
      .r11 .r11-heading{font-size:15px;color:${C.ink};padding:12px 14px 0;font-weight:600}
      .r11 .r11-equation{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;color:${C.ink};line-height:1.7;overflow-wrap:anywhere}
      .r11 [data-readout]{line-height:1.7;overflow-wrap:anywhere}
      .r11 .r11-legend{display:flex;flex-wrap:wrap;gap:7px 18px;font-size:14px;margin:10px 0}
    `));
  }
  function controls(stage) { const el = node('div', {class:'r11-controls'}); stage.appendChild(el); return el; }
  function slider(container, label, key, value, min, max, step, onInput) {
    const wrap = node('label', {class:'r11-control'}), caption = node('span');
    const input = node('input', {type:'range','data-control':key,min,max,step,value});
    function sync(next) {
      input.value = String(next); caption.textContent = label + ' = ' + fmt(next);
      input.setAttribute('aria-valuetext', label + ' = ' + fmt(next));
    }
    input.addEventListener('input', () => {sync(Number(input.value)); onInput(Number(input.value));});
    sync(value); wrap.append(caption, input); container.appendChild(wrap); return {input, sync};
  }
  function button(container, label, key, callback) {
    const b = node('button', {type:'button','data-action':key}, label);
    b.addEventListener('click', callback); container.appendChild(b); return b;
  }
  function plots(stage, titles) {
    const row = node('div', {class:'r11-plots'}); stage.appendChild(row);
    return titles.map(title => {
      const panel = node('div', {class:'r11-plot'}), svg = svgNode('svg');
      panel.append(node('div', {class:'r11-heading'}, title), svg); row.appendChild(panel); return svg;
    });
  }
  function output(root, text) { root.querySelector('[data-readout]').innerHTML = text; }
  function plane(svg, title, limit = 5) {
    svg.replaceChildren(); svg.setAttribute('viewBox', '0 0 420 420'); svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', title); svg.appendChild(svgNode('title', {}, title));
    const L = 42, R = 400, T = 28, B = 386, u = (R - L) / (2 * limit);
    const sx = x => L + (x + limit) * u, sy = y => B - (y + limit) * u;
    const id = 'rank11-clip-' + (global.__rankLesson11ClipCounter = (global.__rankLesson11ClipCounter || 0) + 1);
    const defs = svgNode('defs'), clip = svgNode('clipPath', {id});
    clip.appendChild(svgNode('rect', {x:L,y:T,width:R-L,height:B-T})); defs.appendChild(clip); svg.appendChild(defs);
    for (let i = -limit; i <= limit; i++) {
      line(svg, sx(i), T, sx(i), B, C.grid, 1, {'stroke-opacity':.7});
      line(svg, L, sy(i), R, sy(i), C.grid, 1, {'stroke-opacity':.7});
    }
    line(svg, L, sy(0), R, sy(0), C.soft, 1.2); line(svg, sx(0), T, sx(0), B, C.soft, 1.2);
    for (let i = -limit; i <= limit; i++) if (i !== 0) {
      svgText(svg, sx(i), sy(0) + 16, fmt(i), C.soft, 'middle', 10);
      svgText(svg, sx(0) - 8, sy(i) + 4, fmt(i), C.soft, 'end', 10);
    }
    svgText(svg, R - 3, sy(0) - 9, 'x₁', C.ink, 'end'); svgText(svg, sx(0) + 10, T + 10, 'x₂', C.ink, 'start');
    const layer = svgNode('g', {'clip-path':'url(#' + id + ')'}); svg.appendChild(layer);
    return {svg,layer,L,R,T,B,u,sx,sy,labelBoxes:[]};
  }
  function label(p, end, text, color) {
    const x = p.sx(end[0]), y = p.sy(end[1]), width = text.length * 8 + 6, height = 17;
    const candidates = [[x+9,y-12],[x+9,y+23],[x-width-9,y-12],[x-width-9,y+23],[x+9,y-34]];
    let choice;
    for (const [cx,cy] of candidates) {
      const lx = clamp(cx, p.L+3, p.R-width-3), ly = clamp(cy, p.T+height, p.B-3);
      choice = {x:lx,y:ly-height,w:width,h:height};
      if (!p.labelBoxes.some(b => choice.x < b.x+b.w && choice.x+choice.w > b.x && choice.y < b.y+b.h && choice.y+choice.h > b.y)) break;
    }
    p.labelBoxes.push(choice);
    const attrs = {x:choice.x,y:choice.y+height,'font-size':13,'font-family':'system-ui,sans-serif'};
    p.layer.appendChild(svgNode('text', {...attrs,fill:C.bg,stroke:C.bg,'stroke-width':3,'stroke-linejoin':'round','aria-hidden':'true'}, text));
    p.layer.appendChild(svgNode('text', {...attrs,fill:color}, text));
  }
  function arrow(p, end, color, text, start = [0,0], dashed = false, width = 2.6) {
    const x1 = p.sx(start[0]), y1 = p.sy(start[1]), x2 = p.sx(end[0]), y2 = p.sy(end[1]);
    line(p.layer, x1, y1, x2, y2, color, width, dashed ? {'stroke-dasharray':'5 4'} : {});
    const dx = x2-x1, dy = y2-y1, length = Math.hypot(dx,dy);
    if (length > 1) {
      const ux = dx/length, uy = dy/length, h = Math.min(9,length*.35), w = h*.48;
      p.layer.appendChild(svgNode('polygon', {points:`${x2},${y2} ${x2-h*ux+w*uy},${y2-h*uy-w*ux} ${x2-h*ux-w*uy},${y2-h*uy+w*ux}`,fill:color}));
    } else p.layer.appendChild(svgNode('circle', {cx:x2,cy:y2,r:3,fill:color}));
    if (text) label(p, end, text, color);
  }
  function polygon(p, points, color, opacity = .15) {
    p.layer.appendChild(svgNode('polygon', {points:points.map(v=>p.sx(v[0])+','+p.sy(v[1])).join(' '),fill:color,'fill-opacity':opacity,stroke:color,'stroke-width':1.6}));
    points.forEach(v => p.layer.appendChild(svgNode('circle', {cx:p.sx(v[0]),cy:p.sy(v[1]),r:3.5,fill:color})));
  }
  function legend(stage, entries) {
    const d = node('div', {class:'r11-legend'});
    entries.forEach(([text,color]) => d.appendChild(node('span', {style:'color:'+color}, text)));
    stage.appendChild(d);
  }
  function spanWidget(root) {
    const stage = root.querySelector('[data-stage]'); let t = 1, lambda = 1, mu = 1;
    const ctrl = controls(stage);
    const ts = slider(ctrl, 'Вторая координата b: t', 't', t, -2, 2, .25, value => {t=value;render();});
    slider(ctrl, 'Коэффициент λ перед a', 'lambda', lambda, -2, 2, .25, value => {lambda=value;render();});
    slider(ctrl, 'Коэффициент μ перед b', 'mu', mu, -2, 2, .25, value => {mu=value;render();});
    const row = controls(stage);
    button(row, 'Одно направление: t = 0', 'dependent', () => {t=0;ts.sync(t);render();});
    button(row, 'Два направления: t = 1', 'independent', () => {t=1;ts.sync(t);render();});
    const [svg] = plots(stage, ['Какие точки дают линейные комбинации?']);
    legend(stage, [['a — синий',C.blue],['b — зелёный',C.green],['λa + μb — золотой',C.gold],['(0; 1) — фиолетовая цель',C.violet]]);
    stage.appendChild(node('p', {class:'r11-note'}, 'Серые точки — комбинации для коэффициентов от −2 до 2 с шагом 0,25. Ползунки показывают лишь часть комбинаций: математически коэффициенты могут быть любыми действительными числами.'));
    function render() {
      const a=[1,0], b=[1,t], result=combination(a,b,lambda,mu), dependent=t===0;
      const p=plane(svg, 'Линейные комбинации двух векторов, одинаковый масштаб осей', 5);
      for (let i=-8;i<=8;i++) for (let j=-8;j<=8;j++) {
        const v=combination(a,b,i/4,j/4);
        p.layer.appendChild(svgNode('circle',{cx:p.sx(v[0]),cy:p.sy(v[1]),r:1.8,fill:C.soft,'fill-opacity':.4}));
      }
      p.layer.appendChild(svgNode('circle',{cx:p.sx(0),cy:p.sy(1),r:5,fill:'none',stroke:C.violet,'stroke-width':2}));
      label(p,[0,1],'цель',C.violet);
      arrow(p,[lambda,0],C.blue,'',[0,0],true,1.7); arrow(p,result,C.green,'',[lambda,0],true,1.7);
      arrow(p,a,C.blue,'a',[0,0],false,4); arrow(p,b,C.green,'b',[0,0],dependent);
      arrow(p,result,C.gold,'λa + μb');
      const target = dependent ? 'Точку (0; 1) получить нельзя: вторая координата любой комбинации равна 0.'
        : `Точку (0; 1) можно получить: λ = −1/t ≈ ${fmt(-1/t)}, μ = 1/t ≈ ${fmt(1/t)}.${Math.abs(1/t)>2?' Эти коэффициенты находятся за пределами ползунков.':''}`;
      output(root, `<b>${dependent?'Линейно зависимые векторы: доступно одно направление.':'Линейно независимые векторы: доступны два направления.'}</b><br>a = ${vector(a)}, b = ${vector(b)}.<br><span class="r11-equation">${fmt(lambda)} · ${vector(a)} + ${fmt(mu)} · ${vector(b)} = ${vector(result)}</span><br>${target}<br>Если разрешить любые коэффициенты, получим ${dependent?'всю горизонтальную прямую':'всю плоскость'}.`);
      Object.assign(root.dataset,{t,lambda,mu,rank:dependent?1:2,result:JSON.stringify(result),targetReachable:String(!dependent)});
      row.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.getAttribute('data-action')===(t===0?'dependent':t===1?'independent':''))));
    }
    render();
  }
  function columnsWidget(root) {
    const stage=root.querySelector('[data-stage]'), names=['Утро','Вечер','Весь день']; let delta=0, selected=[true,true,true];
    const ctrl=controls(stage);
    names.forEach((name,j)=>{
      const wrap=node('label',{class:'r11-check'}), input=node('input',{type:'checkbox','data-control':'column-'+j}); input.checked=true;
      input.addEventListener('change',()=>{selected[j]=input.checked;render();}); wrap.append(input,node('span',{},name));ctrl.appendChild(wrap);
    });
    slider(ctrl,'Поправка δ к «Весь день» в день 1','delta',delta,-2,2,1,v=>{delta=v;render();});
    stage.appendChild(node('p',{class:'r11-note'},'Отметьте столбцы, которые хотите оставить в матрице. Поправка меняет только одно число — проверим, сохранится ли зависимость. При ненулевой поправке «Весь день» уже не равно сумме двух смен: это изменённые данные для эксперимента.'));
    const tableWrap=node('div',{class:'r11-table-wrap'});stage.appendChild(tableWrap);
    function render() {
      const X=orders(delta), indices=[0,1,2].filter(j=>selected[j]), active=selectedColumns(X,indices), r=rank(active);
      tableWrap.replaceChildren();const table=node('table',{'aria-label':'Количество заказов по дням'}),head=node('tr');head.appendChild(node('th',{scope:'col'},'День'));
      names.forEach((name,j)=>head.appendChild(node('th',{scope:'col',class:selected[j]?'r11-selected':''},name)));table.appendChild(head);
      X.forEach((row,i)=>{const tr=node('tr');tr.appendChild(node('th',{scope:'row'},String(i+1)));row.forEach((value,j)=>tr.appendChild(node('td',{class:(selected[j]?'r11-selected ':'')+(i===0&&j===2&&delta!==0?'r11-modified':'')},fmt(value))));table.appendChild(tr);});tableWrap.appendChild(table);
      const relation=delta===0?'В полной таблице «Весь день» = «Утро» + «Вечер». Третий столбец восстанавливается по первым двум.':'В полной таблице равенство «Весь день» = «Утро» + «Вечер» нарушено. Теперь три столбца линейно независимы.';
      const chosen=indices.length?indices.map(j=>'«'+names[j]+'»').join(', '):'ни одного';
      output(root,`<b>Оставлено столбцов: ${indices.length}. Ранг выбранной матрицы: ${r}.</b><br>Выбраны: ${chosen}.<br>${relation}<br>Ранг не превышает ни число строк (4), ни число выбранных столбцов (${indices.length}).${indices.length===0?' У матрицы без столбцов ранг 0.':''}<br>NumPy: <code>np.linalg.matrix_rank(X[:, выбранные_столбцы])</code> для непустого выбора.`);
      Object.assign(root.dataset,{delta,rank:r,selected:JSON.stringify(indices),matrix:JSON.stringify(X),nRows:4,nCols:indices.length});
    }
    render();
  }
  function collapseWidget(root) {
    const stage=root.querySelector('[data-stage]');let mode='identity';
    const ctrl=controls(stage);
    [['identity','Плоскость → плоскость'],['rank1','Плоскость → прямая'],['zero','Плоскость → точка']].forEach(([key,title])=>button(ctrl,title,key,()=>{mode=key;render();}));
    const formula=node('p',{class:'r11-equation'});stage.appendChild(formula);
    const [before,after]=plots(stage,['До умножения на A','После умножения на A']);
    legend(stage,[['u = (1; 0) и Au — синие',C.blue],['v = (0; 1) и Av — зелёные',C.green],['Фигура из нескольких точек — золотая',C.gold]]);
    stage.appendChild(node('p',{class:'r11-note'},'Оси и масштаб на двух графиках одинаковы. Фиолетовые линии — конечный фрагмент исходной сетки и его образ. Синяя и зелёная стрелки справа — столбцы матрицы A.'));
    const shape=[[-1,-.7],[.4,-1],[1,.1],[.3,1.5],[-.8,1]];
    function render() {
      const A=presets[mode], r=rank(A), u=[1,0],v=[0,1],au=matvec(A,u),av=matvec(A,v);
      formula.textContent='A = ['+A.map(row=>row.map(fmt).join('  ')).join(';  ')+']';
      const p=plane(before,'Исходная плоскость с двумя различными векторами',4),q=plane(after,'Образ плоскости при матрице ранга '+r,4);
      for(let k=-2;k<=2;k++) {
        const t=k/2,segments=[[[t,-1],[t,1]],[[-1,t],[1,t]]];
        segments.forEach(([a,b])=>{
          line(p.layer,p.sx(a[0]),p.sy(a[1]),p.sx(b[0]),p.sy(b[1]),C.violet,1.4,{'stroke-opacity':.6});
          const aa=matvec(A,a),bb=matvec(A,b);line(q.layer,q.sx(aa[0]),q.sy(aa[1]),q.sx(bb[0]),q.sy(bb[1]),C.violet,1.4,{'stroke-opacity':.6});
        });
      }
      polygon(p,shape,C.gold);polygon(q,shape.map(x=>matvec(A,x)),C.gold);
      arrow(p,u,C.blue,'u');arrow(p,v,C.green,'v');arrow(q,au,C.blue,'Au',[0,0],false,4.5);arrow(q,av,C.green,'Av',[0,0],mode!=='identity');
      if(mode!=='identity') {
        q.layer.appendChild(svgNode('circle',{cx:q.sx(au[0]),cy:q.sy(au[1]),r:6,fill:'none',stroke:C.blue,'stroke-width':2}));
        q.layer.appendChild(svgNode('circle',{cx:q.sx(av[0]),cy:q.sy(av[1]),r:3,fill:C.green}));
      }
      const singular=r<2;
      const meaning=r===2?'Два независимых направления сохраняются. Векторы u и v после преобразования различаются.':r===1?'Все результаты лежат на одной прямой. Разные входы u и v дают один и тот же результат.':'Любой вход превращается в нулевой вектор. Все результаты совпадают.';
      output(root,`<b>Ранг A = ${r}. Матрица ${singular?'вырожденная':'невырожденная'}.</b><br>Au = ${vector(au)}, Av = ${vector(av)}.<br>${meaning}<br>${singular?'По результату уже нельзя однозначно узнать исходный вектор: часть информации потеряна.':'В этом примере A — единичная матрица: каждый вектор остаётся на месте.'}<br>Для квадратной матрицы 2 × 2 вырожденность означает ранг меньше 2.`);
      ctrl.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.getAttribute('data-action')===mode)));
      Object.assign(root.dataset,{mode,rank:r,singular:String(singular),matrix:JSON.stringify(A),au:JSON.stringify(au),av:JSON.stringify(av)});
    }
    render();
  }
  function weightsWidget(root) {
    const stage=root.querySelector('[data-stage]');let t=0;
    const ctrl=controls(stage);
    slider(ctrl,'Вес за миллилитр t','t',t,-.3,.6,.05,v=>{t=v;render();});
    const weightText=node('p',{class:'r11-equation'});stage.appendChild(weightText);
    const [svg]=plots(stage,['Два слагаемых меняются, их сумма остаётся прежней']);
    legend(stage,[['Вклад столбца «литры»',C.blue],['Вклад столбца «миллилитры»',C.green],['Сумма — вклад объёма в цену',C.gold]]);
    stage.appendChild(node('p',{class:'r11-note'},'Все суммы — в тысячах сомов. Это условный вклад только объёма двигателя, а не полная цена автомобиля. Отрицательное слагаемое допустимо: здесь мы изучаем арифметику заданных весов.'));
    const tableWrap=node('div',{class:'r11-table-wrap'});stage.appendChild(tableWrap);
    function render() {
      const result=weightResult(t),w=result.weights;
      weightText.textContent='Вес за литр: '+fmt(w[0])+' тыс. сом/л; вес за миллилитр: '+fmt(w[1])+' тыс. сом/мл.';
      svg.replaceChildren();svg.setAttribute('viewBox','0 0 680 410');svg.setAttribute('role','img');svg.setAttribute('aria-label','Вклады двух зависимых признаков и их неизменная сумма');
      svg.appendChild(svgNode('title',{},'Вклады литров и миллилитров, тысячи сомов'));
      const L=76,R=645,T=40,B=345,lo=-1000,hi=1750,sx=x=>L+(x-.75)/2*(R-L),sy=y=>B-(y-lo)/(hi-lo)*(B-T);
      for(let y=lo;y<=hi;y+=250){line(svg,L,sy(y),R,sy(y),C.grid);svgText(svg,L-9,sy(y)+4,fmt(y),C.soft,'end',11);}
      line(svg,L,sy(0),R,sy(0),C.soft,1.2);line(svg,L,T,L,B,C.soft,1.2);
      volumes.forEach(v=>svgText(svg,sx(v),B+23,fmt(v),C.soft));
      svgText(svg,(L+R)/2,393,'Объём двигателя, л',C.ink);svgText(svg,L,T-17,'Вклад в цену, тыс. сом',C.ink,'start');
      const series=[result.parts.map(p=>p[0]),result.parts.map(p=>p[1]),result.total];
      series.forEach((values,j)=>{
        const color=[C.blue,C.green,C.gold][j];
        svg.appendChild(svgNode('polyline',{points:values.map((y,i)=>sx(volumes[i])+','+sy(y)).join(' '),fill:'none',stroke:color,'stroke-width':j===2?3:2,'stroke-dasharray':j===1?'6 4':'none'}));
        values.forEach((y,i)=>svg.appendChild(svgNode('circle',{cx:sx(volumes[i]),cy:sy(y),r:j===2?5:3.5,fill:color})));
      });
      tableWrap.replaceChildren();const table=node('table',{'aria-label':'Признаки, вклады и сумма'}),head=node('tr');
      ['Литры','Миллилитры','Вклад литров','Вклад миллилитров','Сумма, тыс. сом'].forEach(title=>head.appendChild(node('th',{scope:'col'},title)));table.appendChild(head);
      volumes.forEach((v,i)=>{const tr=node('tr');[v,1000*v,...result.parts[i],result.total[i]].forEach((value,j)=>tr.appendChild(node('td',{style:j===4?'color:'+C.gold:''},fmt(value))));table.appendChild(tr);});tableWrap.appendChild(table);
      output(root,`<b>Разные веса — одинаковые результаты для всех четырёх автомобилей.</b><br>Миллилитры = 1000 · литры, поэтому столбцы линейно зависимы. Ранг этой матрицы признаков равен 1.<br>Ползунок выбирает вес t за миллилитр. Вес за литр автоматически становится 300 − 1000 · t: изменение одного вклада компенсируется другим.<br>Например, для объёма 2 л: ${fmt(result.parts[2][0])} + (${fmt(result.parts[2][1])}) = <b>${fmt(result.total[2])} тыс. сом</b>.<br>Одни и те же результаты не позволяют однозначно определить оба веса.`);
      Object.assign(root.dataset,{t,rank:1,weights:JSON.stringify(w),predictions:JSON.stringify(result.total),parts:JSON.stringify(result.parts)});
    }
    render();
  }
  function mount(root, kind) {
    if (!root || !root.querySelector('[data-stage]') || !root.querySelector('[data-readout]')) throw new Error('Rank widget requires a stage and a readout');
    style(root);
    const widgets={span:spanWidget,columns:columnsWidget,collapse:collapseWidget,weights:weightsWidget};
    if (!widgets[kind]) throw new Error('Unknown rank widget: '+kind);
    widgets[kind](root);
    root.dataset.widget=kind;
  }
  global.RankLesson11={mount,math:{dot,matvec,combination,rank,orders,selectedColumns,weightResult,presets,volumes}};
})(typeof window !== 'undefined' ? window : globalThis);
