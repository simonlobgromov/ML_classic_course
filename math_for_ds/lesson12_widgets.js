/* Standalone systems and inverse visualizations, embedded into lesson 12. */
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
    root.classList.add('s12');
    root.appendChild(node('style', {}, `
      .s12 .s12-controls{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin:12px 0}
      .s12 .s12-control{display:flex;flex-direction:column;gap:5px;color:${C.ink};font-size:14px;min-width:170px}
      .s12 [hidden]{display:none!important}
      .s12 select,.s12 button{font:inherit;background:#18232f;color:${C.ink};border:1px solid #405164;border-radius:6px;padding:7px 10px;cursor:pointer}
      .s12 button:focus-visible,.s12 select:focus-visible,.s12 input:focus-visible{outline:3px solid ${C.gold};outline-offset:3px}
      .s12 button[aria-pressed=true]{background:#24435f;border-color:${C.blue};color:white}
      .s12 input[type=range]{width:170px;accent-color:${C.blue}}
      .s12 input[type=checkbox]{accent-color:${C.blue};width:18px;height:18px}
      .s12 .s12-check{display:flex;align-items:center;gap:7px;color:${C.ink};font-size:14px}
      .s12 .s12-plots{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:10px}
      .s12 .s12-plot{min-width:0;background:#0f151d;border:1px solid ${C.grid};border-radius:8px}
      .s12 .s12-plot svg{width:100%;height:auto;display:block;max-height:520px}
      .s12 .s12-table-wrap{overflow-x:auto;margin:14px 0}
      .s12 table{border-collapse:collapse;color:${C.ink};font-size:14px;font-variant-numeric:tabular-nums;width:100%}
      .s12 th,.s12 td{padding:9px 12px;text-align:center;border-bottom:1px solid ${C.grid}}
      .s12 th{font-weight:500;color:${C.soft}}
      .s12 .s12-selected{background:#203343;color:${C.blue}}
      .s12 .s12-modified{color:${C.gold};font-weight:700}
      .s12 .s12-note{font-size:14px;line-height:1.6;color:${C.soft};margin:9px 0}
      .s12 .s12-heading{font-size:15px;color:${C.ink};padding:12px 14px 0;font-weight:600}
      .s12 .s12-equation{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;color:${C.ink};line-height:1.7;overflow-wrap:anywhere}
      .s12 [data-readout]{line-height:1.7;overflow-wrap:anywhere}
      .s12 .s12-matrix{display:inline-grid;grid-template-columns:repeat(2,minmax(35px,auto));border-left:2px solid #a7b0ba;border-right:2px solid #a7b0ba;padding:3px 7px;gap:2px 12px;vertical-align:middle;text-align:center;font-variant-numeric:tabular-nums}
      .s12 .s12-formulas{display:flex;align-items:center;flex-wrap:wrap;gap:12px 24px;margin:14px 0}
      .s12 .s12-legend{display:flex;flex-wrap:wrap;gap:7px 18px;font-size:14px;margin:10px 0}
    `));
  }
  function controls(stage) { const el = node('div', {class:'s12-controls'}); stage.appendChild(el); return el; }
  function slider(container, label, key, value, min, max, step, onInput) {
    const wrap = node('label', {class:'s12-control'}), caption = node('span');
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
    const row = node('div', {class:'s12-plots'}); stage.appendChild(row);
    return titles.map(title => {
      const panel = node('div', {class:'s12-plot'}), svg = svgNode('svg');
      panel.append(node('div', {class:'s12-heading'}, title), svg); row.appendChild(panel); return svg;
    });
  }
  function output(root, text) { root.querySelector('[data-readout]').innerHTML = text; }
  function plane(svg, title, limit = 5, labels = ['x₁','x₂'], center = [0,0]) {
    svg.replaceChildren(); svg.setAttribute('viewBox', '0 0 420 420'); svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', title); svg.appendChild(svgNode('title', {}, title));
    const L = 42, R = 400, T = 28, B = 386, u = (R - L) / (2 * limit);
    const xmin=center[0]-limit,xmax=center[0]+limit,ymin=center[1]-limit,ymax=center[1]+limit;
    const sx = x => L + (x - xmin) * u, sy = y => B - (y - ymin) * u;
    const id = 'systems12-clip-' + (global.__systemsLesson12ClipCounter = (global.__systemsLesson12ClipCounter || 0) + 1);
    const defs = svgNode('defs'), clip = svgNode('clipPath', {id});
    clip.appendChild(svgNode('rect', {x:L,y:T,width:R-L,height:B-T})); defs.appendChild(clip); svg.appendChild(defs);
    const step = limit > 6 ? 2 : 1;
    for (let i = Math.ceil(xmin / step) * step; i <= xmax; i += step) {
      line(svg, sx(i), T, sx(i), B, C.grid, 1, {'stroke-opacity':.7});
      if(i!==0)svgText(svg,sx(i),sy(0)+16,fmt(i),C.soft,'middle',10);
    }
    for (let i = Math.ceil(ymin / step) * step; i <= ymax; i += step) {
      line(svg,L,sy(i),R,sy(i),C.grid,1,{'stroke-opacity':.7});
      if(i!==0)svgText(svg,sx(0)-8,sy(i)+4,fmt(i),C.soft,'end',10);
    }
    line(svg, L, sy(0), R, sy(0), C.soft, 1.2); line(svg, sx(0), T, sx(0), B, C.soft, 1.2);
    svgText(svg, R - 3, sy(0) - 9, labels[0], C.ink, 'end'); svgText(svg, sx(0) + 10, T + 10, labels[1], C.ink, 'start');
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
    const d = node('div', {class:'s12-legend'});
    entries.forEach(([text,color]) => d.appendChild(node('span', {style:'color:'+color}, text)));
    stage.appendChild(d);
  }
  const inversePresets = {
    rotation:[[0,-1],[1,0]], stretch:[[2,0],[0,.5]],
    shear:[[1,1],[0,1]], singular:[[1,1],[2,2]]
  };
  const determinant = A => A[0][0]*A[1][1]-A[0][1]*A[1][0];
  function inverse(A) {
    const d=determinant(A);
    return d===0?null:[[A[1][1]/d,-A[0][1]/d],[-A[1][0]/d,A[0][0]/d]];
  }
  function systemResult(independent, b2) {
    const A=independent?[[1,1],[1,2]]:[[1,1],[2,2]], b=[3,b2];
    const kind=independent?'unique':b2===6?'infinite':'none';
    return {A,b,kind,rank:independent?2:1,solution:independent?[6-b2,b2-3]:null};
  }
  function matrixHTML(A) {
    return '<span class="s12-matrix" aria-label="Матрица: '+A.map(r=>r.map(fmt).join(', ')).join('; ')+'">'+A.flat().map(x=>'<span>'+fmt(x)+'</span>').join('')+'</span>';
  }
  function point(p, v, color, text, radius=5) {
    p.layer.appendChild(svgNode('circle',{cx:p.sx(v[0]),cy:p.sy(v[1]),r:radius,fill:color,stroke:C.bg,'stroke-width':1.5}));
    if(text)label(p,v,text,color);
  }
  function drawEquation(p, coefficients, b, color, dashed=false, width=2.6) {
    // Clip a complete line through the plotting viewport rather than just a finite sample.
    const L=(p.R-p.L)/(2*p.u), [a,c]=coefficients;
    if(c!==0)line(p.layer,p.sx(-L),p.sy((b+a*L)/c),p.sx(L),p.sy((b-a*L)/c),color,width,dashed?{'stroke-dasharray':'6 5'}:{});
    else if(a!==0)line(p.layer,p.sx(b/a),p.T,p.sx(b/a),p.B,color,width,dashed?{'stroke-dasharray':'6 5'}:{});
  }
  function systemsWidget(root) {
    const stage=root.querySelector('[data-stage]');let independent=true,b2=4;
    const presets=controls(stage);
    const bs=slider(controls(stage),'Правая часть второго уравнения b₂','b2',b2,0,8,.5,v=>{b2=v;render();});
    [['unique','Одно решение',true,4],['infinite','Бесконечно много',false,6],['none','Нет решений',false,8]].forEach(([key,title,ind,val])=>button(presets,title,key,()=>{independent=ind;b2=val;bs.sync(b2);render();}));
    const formulas=node('div',{class:'s12-formulas'});stage.appendChild(formulas);
    const [left,right]=plots(stage,['Ищем общую точку двух прямых','Можно ли получить вектор b из столбцов A?']);
    legend(stage,[['Первое уравнение / столбец a₁',C.blue],['Второе уравнение / столбец a₂',C.green],['Решение x / цель b',C.gold]]);
    stage.appendChild(node('p',{class:'s12-note'},'Слева координаты точки — неизвестные x₁ и x₂. Справа координаты — результат y = Ax. Серые точки справа показывают только комбинации с коэффициентами от −2 до 2. Два графика имеют разные пределы; внутри каждого масштаб по осям одинаков.'));
    function render() {
      const res=systemResult(independent,b2),{A,b,kind,solution}=res;
      formulas.innerHTML='<span>A = '+matrixHTML(A)+'</span><span>b = '+vector(b)+'</span>';
      const bound=solution?Math.max(5,...solution.map(v=>Math.ceil(Math.abs(v)+1))):5;
      const p=plane(left,'Две прямые: '+(kind==='unique'?'одно решение':kind==='infinite'?'бесконечно много решений':'решений нет'),bound);
      drawEquation(p,A[0],b[0],C.blue,false,4);drawEquation(p,A[1],b[1],C.green,kind==='infinite',2.6);
      if(solution)point(p,solution,C.gold,'x = '+vector(solution),6);
      if(kind==='infinite') {point(p,[1,2],C.gold,'например, (1; 2)');point(p,[3,0],C.gold,'(3; 0)');}
      const q=plane(right,'Столбцы матрицы и целевой вектор b',10,['y₁','y₂']);
      if(!independent)drawEquation(q,[-2,1],0,C.violet,false,2);
      for(let i=-8;i<=8;i++)for(let j=-8;j<=8;j++) {
        const v=matvec(A,[i/4,j/4]);
        q.layer.appendChild(svgNode('circle',{cx:q.sx(v[0]),cy:q.sy(v[1]),r:1.8,fill:C.soft,'fill-opacity':.45}));
      }
      arrow(q,[A[0][0],A[1][0]],C.blue,'a₁',[0,0],false,4.5);
      arrow(q,[A[0][1],A[1][1]],C.green,'a₂',[0,0],!independent,2.5);
      arrow(q,b,C.gold,'b');point(q,b,C.gold,'',5);
      const equations=independent?'x₁ + x₂ = 3; &nbsp; x₁ + 2x₂ = '+fmt(b2):'x₁ + x₂ = 3; &nbsp; 2x₁ + 2x₂ = '+fmt(b2);
      let conclusion;
      if(kind==='unique')conclusion='<b>Одно решение: x = '+vector(solution)+'.</b> Прямые пересекаются. Столбцы A независимы: любой вектор b можно получить ровно одной комбинацией.';
      else if(kind==='infinite')conclusion='<b>Бесконечно много решений.</b> Второе уравнение — первое, умноженное на 2. Прямые совпадают. Все решения: x₁ = 3 − t, x₂ = t, где t — любое действительное число. Вектор b лежит на прямой доступных результатов.';
      else conclusion='<b>Решений нет.</b> Из первого уравнения следует 2x₁ + 2x₂ = 6, а второе требует '+fmt(b2)+'. Прямые параллельны и не совпадают. Вектор b не лежит на прямой доступных результатов.';
      output(root,'<span class="s12-equation">'+equations+'</span><br>'+conclusion+'<br>Ранг A = '+res.rank+'. '+(!independent?'Попробуйте b₂ = 6, затем другое значение. Матрица A остаётся той же; меняется существование решения.':'Ползунок меняет b₂: единственное решение сохраняется, а его координаты меняются.'));
      presets.querySelectorAll('button').forEach(btn=>btn.setAttribute('aria-pressed',String(btn.getAttribute('data-action')===(independent?'unique':kind))));
      Object.assign(root.dataset,{mode:kind,b2,independent:String(independent),rank:res.rank,matrix:JSON.stringify(A),target:JSON.stringify(b),solution:JSON.stringify(solution)});
    }
    render();
  }
  function inverseWidget(root) {
    const stage=root.querySelector('[data-stage]');let mode='rotation',x1=1,x2=1;
    const presetRow=controls(stage);
    [['rotation','Поворот на 90°'],['stretch','Растяжение и сжатие'],['shear','Наклон фигуры'],['singular','Сжатие в прямую']].forEach(([key,title])=>button(presetRow,title,key,()=>{mode=key;render();}));
    const ctrl=controls(stage);
    slider(ctrl,'Первая координата входа x₁','x1',x1,-2,2,.25,v=>{x1=v;render();});
    slider(ctrl,'Вторая координата входа x₂','x2',x2,-2,2,.25,v=>{x2=v;render();});
    const formulas=node('div',{class:'s12-formulas'});stage.appendChild(formulas);
    const [before,after,restored]=plots(stage,['Вход x','Результат y = Ax','Возвращаемся к входу']);
    legend(stage,[['Фигура и её образ',C.blue],['Выбранная точка',C.gold]]);
    stage.appendChild(node('p',{class:'s12-note'},'У каждой вершины фигуры свои координаты. К каждой точке применяется одна и та же матрица. Масштаб и пределы всех координатных графиков одинаковы. Ползунки двигают золотую точку.'));
    const shape=[[-1,-.7],[.4,-1],[1,.1],[.3,1.5],[-.8,1]];
    function render() {
      const A=inversePresets[mode], inv=inverse(A),x=[x1,x2],y=matvec(A,x),back=inv?matvec(inv,y):null;
      const transformed=shape.map(v=>matvec(A,v));
      const bound=Math.ceil(Math.max(3,...transformed.flat().map(v=>Math.abs(v)+1),...y.map(v=>Math.abs(v)+1)));
      const p=plane(before,'Исходные точки',bound),q=plane(after,'Точки после умножения на A',bound,['y₁','y₂']);
      polygon(p,shape,C.blue,.2);polygon(q,transformed,C.blue,.2);
      arrow(p,x,C.gold,'x');point(p,x,C.gold,'');arrow(q,y,C.gold,'y');point(q,y,C.gold,'');
      formulas.innerHTML='<span>A = '+matrixHTML(A)+'</span><span>'+(inv?'A⁻¹ = '+matrixHTML(inv):'Обратной матрицы A⁻¹ нет')+'</span>';
      if(inv) {
        const r=plane(restored,'Точки после умножения на обратную матрицу',bound);
        polygon(r,transformed.map(v=>matvec(inv,v)),C.blue,.2);arrow(r,back,C.gold,'A⁻¹y = x');point(r,back,C.gold,'');
        output(root,'<b>Матрица обратима: ранг A = 2.</b><br>x = '+vector(x)+' → Ax = '+vector(y)+' → A⁻¹(Ax) = '+vector(back)+'.<br>Исходная фигура и выбранная точка восстановлены. Обратная матрица отменяет действие A для любого входа.');
      } else {
        restored.replaceChildren();restored.setAttribute('viewBox','0 0 420 420');restored.setAttribute('role','img');restored.setAttribute('aria-label','Обратной матрицы нет: два разных входа дают одинаковый результат');
        restored.appendChild(svgNode('title',{},'Однозначное восстановление невозможно'));
        svgText(restored,210,115,'Восстановить однозначно',C.rose,'middle',17);
        svgText(restored,210,143,'нельзя',C.rose,'middle',17);
        svgText(restored,210,206,'(1; 0) → (1; 2)',C.blue,'middle',18);
        svgText(restored,210,240,'(0; 1) → (1; 2)',C.green,'middle',18);
        svgText(restored,210,298,'Два входа — один результат.',C.soft,'middle',14);
        svgText(restored,210,322,'Какой вход вернуть?',C.soft,'middle',14);
        output(root,'<b>Матрица вырожденная и необратимая: ранг A = 1.</b><br>x = '+vector(x)+' → Ax = '+vector(y)+'.<br>Разные входы (1; 0) и (0; 1) дают один результат (1; 2). По этому результату нельзя узнать, какой из них был на входе. Обратная матрица для такого преобразования не существует.');
      }
      presetRow.querySelectorAll('button').forEach(btn=>btn.setAttribute('aria-pressed',String(btn.getAttribute('data-action')===mode)));
      Object.assign(root.dataset,{mode,rank:inv?2:1,invertible:String(!!inv),matrix:JSON.stringify(A),inverse:JSON.stringify(inv),input:JSON.stringify(x),output:JSON.stringify(y),restored:JSON.stringify(back)});
    }
    render();
  }
  function determinantWidget(root) {
    const stage=root.querySelector('[data-stage]');let s=1,t=1;
    const ctrl=controls(stage);
    const ss=slider(ctrl,'Горизонтальная координата a₂: s','s',s,-2,2,.25,v=>{s=v;render();});
    const ts=slider(ctrl,'Вертикальная координата a₂: t','t',t,-2,2,.25,v=>{t=v;render();});
    const presets=controls(stage);
    [['unit','Площадь 1',1,1],['double','Площадь 2',1,2],['negative','Смена ориентации',1,-1],['zero','Площадь 0',1,0]].forEach(([key,title,newS,newT])=>button(presets,title,key,()=>{s=newS;t=newT;ss.sync(s);ts.sync(t);render();}));
    const formula=node('div',{class:'s12-formulas'});stage.appendChild(formula);
    const [before,after]=plots(stage,['Единичный квадрат: площадь 1','Образ квадрата: параллелограмм']);
    legend(stage,[['Первый столбец a₁',C.blue],['Второй столбец a₂',C.green],['Порядок обхода вершин',C.gold]]);
    stage.appendChild(node('p',{class:'s12-note'},'Золотые стрелки обходят вершины в одном и том же порядке до и после преобразования. Если направление обхода меняется, меняется ориентация. Пределы и масштаб двух графиков одинаковы.'));
    const square=[[0,0],[1,0],[1,1],[0,1]];
    function render() {
      const A=[[1,s],[0,t]],area=Math.abs(t),det=determinant(A),transformed=square.map(v=>matvec(A,v));
      formula.innerHTML='<span>A = '+matrixHTML(A)+'</span><span>det(A) = 1 · '+fmt(t)+' − '+fmt(s)+' · 0 = '+fmt(det)+'</span>';
      const points=[...square,...transformed],xs=points.map(v=>v[0]),ys=points.map(v=>v[1]);
      const xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...ys),ymax=Math.max(...ys);
      const center=[(xmin+xmax)/2,(ymin+ymax)/2],bound=Math.max(xmax-xmin,ymax-ymin)/2+.65;
      const p=plane(before,'Единичный квадрат с обходом против часовой стрелки',bound,['x₁','x₂'],center),q=plane(after,'Образ единичного квадрата, площадь '+fmt(area),bound,['y₁','y₂'],center);
      polygon(p,square,C.violet,.2);polygon(q,transformed,C.violet,.2);
      const walk=(plane,vertices)=>vertices.forEach((v,i)=>{
        const next=vertices[(i+1)%vertices.length],start=v.map((c,j)=>c+.3*(next[j]-c)),end=v.map((c,j)=>c+.7*(next[j]-c));
        arrow(plane,end,C.gold,'',start,false,2);
      });
      walk(p,square);walk(q,transformed);
      arrow(p,[1,0],C.blue,'e₁');arrow(p,[0,1],C.green,'e₂');
      arrow(q,[1,0],C.blue,'a₁',[0,0],false,3.2);arrow(q,[s,t],C.green,'a₂',[0,0],t===0,2.4);
      const orientation=t>0?'Ориентация сохранена: обход остаётся против часовой стрелки.':t<0?'Ориентация изменилась: обход стал по часовой стрелке.':'Квадрат схлопнулся в отрезок. Два независимых направления не сохранились.';
      output(root,'<b>Определитель det(A) = '+fmt(det)+'. Площадь образа = |det(A)| = '+fmt(area)+'.</b><br>'+orientation+'<br>'+ (t===0?'Ранг A = 1: матрица вырожденная, обратной матрицы нет.':'Ранг A = 2: матрица невырожденная, обратная существует.')+'<br>Параметр s сдвигает конец второго столбца по горизонтали, но не меняет площадь. Параметр t задаёт его вертикальную координату; |t| — высота параллелограмма при основании 1.');
      presets.querySelectorAll('button').forEach(btn=>{
        const selected=s===1&&(btn.getAttribute('data-action')===(t===1?'unit':t===2?'double':t===-1?'negative':t===0?'zero':''));
        btn.setAttribute('aria-pressed',String(selected));
      });
      Object.assign(root.dataset,{s,t,det,area,rank:t===0?1:2,invertible:String(t!==0),matrix:JSON.stringify(A),polygon:JSON.stringify(transformed)});
    }
    render();
  }
  function mount(root,kind) {
    if(!root||!root.querySelector('[data-stage]')||!root.querySelector('[data-readout]'))throw new Error('Systems widget requires a stage and a readout');
    const widgets={systems:systemsWidget,inverse:inverseWidget,determinant:determinantWidget};
    if(!widgets[kind])throw new Error('Unknown systems widget: '+kind);
    style(root);widgets[kind](root);root.dataset.widget=kind;
  }
  global.SystemsLesson12={mount,math:{dot,matvec,combination,rank,determinant,inverse,systemResult,inversePresets}};
})(typeof window!=='undefined'?window:globalThis);
