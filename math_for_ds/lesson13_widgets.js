/* Standalone covariance and correlation visualizations, embedded into lesson 13. */
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
    root.classList.add('c13');
    root.appendChild(node('style', {}, `
      .c13 .c13-controls{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin:12px 0}
      .c13 .c13-control{display:flex;flex-direction:column;gap:5px;color:${C.ink};font-size:14px;min-width:170px}
      .c13 [hidden]{display:none!important}
      .c13 select,.c13 button{font:inherit;background:#18232f;color:${C.ink};border:1px solid #405164;border-radius:6px;padding:7px 10px;cursor:pointer}
      .c13 button:focus-visible,.c13 select:focus-visible,.c13 input:focus-visible{outline:3px solid ${C.gold};outline-offset:3px}
      .c13 button[aria-pressed=true]{background:#24435f;border-color:${C.blue};color:white}
      .c13 input[type=range]{width:170px;accent-color:${C.blue}}
      .c13 input[type=checkbox]{accent-color:${C.blue};width:18px;height:18px}
      .c13 .c13-check{display:flex;align-items:center;gap:7px;color:${C.ink};font-size:14px}
      .c13 .c13-plots{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:10px}
      .c13 .c13-plot{min-width:0;background:#0f151d;border:1px solid ${C.grid};border-radius:8px}
      .c13 .c13-plot svg{width:100%;height:auto;display:block;max-height:520px}
      .c13 .c13-highlight{background:#2a3543}
      .c13 .c13-table-wrap{overflow-x:auto;margin:14px 0}
      .c13 table{border-collapse:collapse;color:${C.ink};font-size:14px;font-variant-numeric:tabular-nums;width:100%}
      .c13 th,.c13 td{padding:9px 12px;text-align:center;border-bottom:1px solid ${C.grid}}
      .c13 th{font-weight:500;color:${C.soft}}
      .c13 .c13-selected{background:#203343;color:${C.blue}}
      .c13 .c13-modified{color:${C.gold};font-weight:700}
      .c13 .c13-note{font-size:14px;line-height:1.6;color:${C.soft};margin:9px 0}
      .c13 .c13-heading{font-size:15px;color:${C.ink};padding:12px 14px 0;font-weight:600}
      .c13 .c13-equation{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;color:${C.ink};line-height:1.7;overflow-wrap:anywhere}
      .c13 [data-readout]{line-height:1.7;overflow-wrap:anywhere}
      .c13 .c13-matrix{display:inline-grid;grid-template-columns:repeat(2,minmax(35px,auto));border-left:2px solid #a7b0ba;border-right:2px solid #a7b0ba;padding:3px 7px;gap:2px 12px;vertical-align:middle;text-align:center;font-variant-numeric:tabular-nums}
      .c13 .c13-formulas{display:flex;align-items:center;flex-wrap:wrap;gap:12px 24px;margin:14px 0}
      .c13 .c13-legend{display:flex;flex-wrap:wrap;gap:7px 18px;font-size:14px;margin:10px 0}
    `));
  }
  function controls(stage) { const el = node('div', {class:'c13-controls'}); stage.appendChild(el); return el; }
  function slider(container, label, key, value, min, max, step, onInput) {
    const wrap = node('label', {class:'c13-control'}), caption = node('span');
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
    const row = node('div', {class:'c13-plots'}); stage.appendChild(row);
    return titles.map(title => {
      const panel = node('div', {class:'c13-plot'}), svg = svgNode('svg');
      panel.append(node('div', {class:'c13-heading'}, title), svg); row.appendChild(panel); return svg;
    });
  }
  function output(root, text) { root.querySelector('[data-readout]').innerHTML = text; }
  function plane(svg, title, limit = 5, labels = ['x₁','x₂'], center = [0,0]) {
    svg.replaceChildren(); svg.setAttribute('viewBox', '0 0 420 420'); svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', title); svg.appendChild(svgNode('title', {}, title));
    const L = 42, R = 400, T = 28, B = 386, u = (R - L) / (2 * limit);
    const xmin=center[0]-limit,xmax=center[0]+limit,ymin=center[1]-limit,ymax=center[1]+limit;
    const sx = x => L + (x - xmin) * u, sy = y => B - (y - ymin) * u;
    const id = 'correlation13-clip-' + (global.__correlationLesson13ClipCounter = (global.__correlationLesson13ClipCounter || 0) + 1);
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
    const d = node('div', {class:'c13-legend'});
    entries.forEach(([text,color]) => d.appendChild(node('span', {style:'color:'+color}, text)));
    stage.appendChild(d);
  }
  function mean(a) {return a.reduce((s,v)=>s+v,0)/a.length;}
  function centered(a) {const m=mean(a);return a.map(v=>v-m);}
  function sampleStats(x,y) {
    if(x.length!==y.length||x.length<2)throw new Error('At least two paired observations are required');
    const mx=mean(x),my=mean(y),dx=x.map(v=>v-mx),dy=y.map(v=>v-my),n=x.length;
    const xx=dot(dx,dx),yy=dot(dy,dy),xy=dot(dx,dy),sx=Math.sqrt(xx/(n-1)),sy=Math.sqrt(yy/(n-1));
    return {n,mx,my,dx,dy,products:dx.map((v,i)=>v*dy[i]),cov:xy/(n-1),sx,sy,r:xx===0||yy===0?null:clamp(xy/Math.sqrt(xx*yy),-1,1)};
  }
  function averageRanks(a) {
    const pairs=a.map((v,i)=>({v,i})).sort((p,q)=>p.v-q.v),ranks=Array(a.length);
    for(let i=0;i<pairs.length;){let j=i+1;while(j<pairs.length&&pairs[j].v===pairs[i].v)j++;const r=(i+1+j)/2;for(let k=i;k<j;k++)ranks[pairs[k].i]=r;i=j;}
    return ranks;
  }
  function spearman(x,y) {return sampleStats(averageRanks(x),averageRanks(y)).r;}
  function fixedNoise(n,seed=130013) {
    let state=seed>>>0;const uniform=()=>{state=(1664525*state+1013904223)>>>0;return (state+.5)/4294967296;};
    const a=Array.from({length:n},()=>Math.sqrt(-2*Math.log(uniform()))*Math.cos(2*Math.PI*uniform()));
    const c=centered(a),sd=Math.sqrt(dot(c,c)/(n-1));return c.map(v=>v/sd);
  }
  const apartmentAreas=[30,40,50,60,70];
  const apartmentPrices={positive:[2.8,3.5,4.4,4.8,6],negative:[6,4.8,4.4,3.5,2.8],mixed:[4,6,3,6,4]};
  const feetPerSquareMetre=10.7639104167;
  const pearsonX=Array.from({length:31},(_,i)=>(i-15)/5),pearsonNoise=fixedNoise(31);
  function pearsonData(slope,noise,offset) {return {x:pearsonX.slice(),y:pearsonX.map((x,i)=>slope*x+noise*pearsonNoise[i]+offset)};}
  function transformData(kind,noise=0) {
    const x=Array.from({length:41},(_,i)=>(i-20)*(kind==='sine'?Math.PI/20:.1));
    const f=kind==='cubic'?v=>v**3:kind==='quadratic'?v=>v**2:kind==='sine'?Math.sin:null;
    if(!f)throw new Error('Unknown transformation');
    const z=x.map(f),e=fixedNoise(x.length,130131),y=z.map((v,i)=>v+noise*e[i]);return {x,z,y};
  }
  function number(x) {return x===null?'не определён':String(Number(x.toFixed(3)));}
  function axisRange(values,pad=.12) {
    const lo=Math.min(...values),hi=Math.max(...values),span=hi-lo||Math.max(1,Math.abs(lo)*.2);
    return [lo-pad*span,hi+pad*span];
  }
  function ticks(lo,hi) {
    const raw=(hi-lo)/5,power=10**Math.floor(Math.log10(raw)),ratio=raw/power;
    const step=(ratio<=1?1:ratio<=2?2:ratio<=5?5:10)*power,out=[];
    for(let v=Math.ceil(lo/step)*step;v<=hi+step*1e-8;v+=step)out.push(v);
    return out;
  }
  function scatterFrame(svg,title,xrange,yrange,xlabel,ylabel) {
    svg.replaceChildren();svg.setAttribute('viewBox','0 0 480 420');svg.setAttribute('role','img');svg.setAttribute('aria-label',title);svg.appendChild(svgNode('title',{},title));
    const L=62,R=456,T=36,B=358,sx=x=>L+(x-xrange[0])/(xrange[1]-xrange[0])*(R-L),sy=y=>B-(y-yrange[0])/(yrange[1]-yrange[0])*(B-T);
    ticks(...xrange).forEach(x=>{line(svg,sx(x),T,sx(x),B,C.grid);svgText(svg,sx(x),B+20,fmt(x),C.soft,'middle',11);});
    ticks(...yrange).forEach(y=>{line(svg,L,sy(y),R,sy(y),C.grid);svgText(svg,L-9,sy(y)+4,fmt(y),C.soft,'end',11);});
    line(svg,L,B,R,B,C.soft);line(svg,L,T,L,B,C.soft);
    svgText(svg,(L+R)/2,405,xlabel,C.ink,'middle',13);svgText(svg,L,T-14,ylabel,C.ink,'start',13);
    const id='correlation13-clip-'+(global.__correlationLesson13ClipCounter=(global.__correlationLesson13ClipCounter||0)+1),defs=svgNode('defs'),clip=svgNode('clipPath',{id});
    clip.appendChild(svgNode('rect',{x:L,y:T,width:R-L,height:B-T}));defs.appendChild(clip);svg.appendChild(defs);
    const layer=svgNode('g',{'clip-path':'url(#'+id+')'});svg.appendChild(layer);
    return {svg,layer,L,R,T,B,sx,sy,labelBoxes:[]};
  }
  function dots(p,x,y,color=C.blue,radius=4) {
    x.forEach((v,i)=>p.layer.appendChild(svgNode('circle',{cx:p.sx(v),cy:p.sy(y[i]),r:radius,fill:color,'fill-opacity':.85,stroke:C.bg,'stroke-width':1})));
  }
  function curve(p,x,y,color=C.soft) {p.layer.appendChild(svgNode('polyline',{points:x.map((v,i)=>p.sx(v)+','+p.sy(y[i])).join(' '),fill:'none',stroke:color,'stroke-width':1.7,'stroke-dasharray':'5 4'}));}
  function covarianceWidget(root) {
    const stage=root.querySelector('[data-stage]');let pattern='positive',unit='metres',selected=0;
    const patterns=controls(stage),units=controls(stage),selection=controls(stage);
    [['positive','Цена обычно растёт'],['negative','Цена обычно падает'],['mixed','Смешанная картина']].forEach(([k,t])=>button(patterns,t,k,()=>{pattern=k;render();}));
    [['metres','Площадь в м²'],['feet','Та же площадь в ft²']].forEach(([k,t])=>button(units,t,k,()=>{unit=k;render();}));
    for(let i=0;i<5;i++)button(selection,'Квартира '+(i+1),'point-'+i,()=>{selected=i;render();});
    const [svg]=plots(stage,['Отклонения считаются от двух средних']);
    legend(stage,[['Положительное произведение отклонений',C.green],['Отрицательное произведение',C.rose],['Нулевое произведение',C.soft]]);
    const tableWrap=node('div',{class:'c13-table-wrap'});stage.appendChild(tableWrap);
    stage.appendChild(node('p',{class:'c13-note'},'Синтетические данные: это пять условных квартир. 1 м² ≈ 10,764 ft²; ft² — квадратный фут. Пунктирные линии показывают средние. Цвет точки определяется знаком произведения её отклонений. Выделенный прямоугольник помогает увидеть эти два отклонения.'));
    function render() {
      const factor=unit==='feet'?feetPerSquareMetre:1,x=apartmentAreas.map(v=>v*factor),y=apartmentPrices[pattern],s=sampleStats(x,y),xu=unit==='feet'?'ft²':'м²';
      const p=scatterFrame(svg,'Площадь и цена пяти квартир',axisRange(x,.18),[2.2,6.7],'Площадь, '+xu,'Цена, млн сом');
      const xi=x[selected],yi=y[selected],color=s.products[selected]>0?C.green:s.products[selected]<0?C.rose:C.soft;
      p.layer.appendChild(svgNode('rect',{x:Math.min(p.sx(s.mx),p.sx(xi)),y:Math.min(p.sy(s.my),p.sy(yi)),width:Math.abs(p.sx(xi)-p.sx(s.mx)),height:Math.abs(p.sy(yi)-p.sy(s.my)),fill:color,'fill-opacity':.14,stroke:color,'stroke-dasharray':'3 3'}));
      line(p.layer,p.sx(s.mx),p.T,p.sx(s.mx),p.B,C.gold,1.5,{'stroke-dasharray':'6 5'});line(p.layer,p.L,p.sy(s.my),p.R,p.sy(s.my),C.gold,1.5,{'stroke-dasharray':'6 5'});
      x.forEach((v,i)=>{const c=s.products[i]>0?C.green:s.products[i]<0?C.rose:C.soft;p.layer.appendChild(svgNode('circle',{cx:p.sx(v),cy:p.sy(y[i]),r:i===selected?7:5,fill:c,stroke:i===selected?C.ink:C.bg,'stroke-width':i===selected?2:1}));label(p,[v,y[i]],String(i+1),c);});
      label(p,[s.mx,s.my],'средние',C.gold);
      tableWrap.replaceChildren();const table=node('table',{'aria-label':'Отклонения площади и цены от средних'}),head=node('tr');
      ['Квартира','x, '+xu,'y, млн сом','x − x̄','y − ȳ','(x − x̄)(y − ȳ)'].forEach(t=>head.appendChild(node('th',{scope:'col'},t)));table.appendChild(head);
      x.forEach((v,i)=>{const tr=node('tr',{class:i===selected?'c13-highlight':''});[i+1,v,y[i],s.dx[i],s.dy[i],s.products[i]].forEach((v,j)=>tr.appendChild(node(j===0?'th':'td',j===0?{scope:'row'}:{},fmt(v))));table.appendChild(tr);});tableWrap.appendChild(table);
      const sign=s.products[selected]>0?'одинаковые знаки отклонений':s.products[selected]<0?'разные знаки отклонений':'хотя бы одно отклонение равно нулю';
      output(root,'<b>Квартира '+(selected+1)+': '+sign+'.</b><br>Отклонение площади: '+fmt(s.dx[selected])+' '+xu+'; отклонение цены: '+fmt(s.dy[selected])+' млн сом.<br>Их произведение: '+fmt(s.products[selected])+' '+xu+' · млн сом.<br><b>Выборочная ковариация = сумма произведений / (5 − 1) = '+fmt(s.cov)+' '+xu+' · млн сом.</b><br>Средние: x̄ = '+fmt(s.mx)+' '+xu+', ȳ = '+fmt(s.my)+' млн сом.<br>Перевод площади в другую единицу меняет ковариацию и её единицу измерения. Сами квартиры и их цены остаются прежними.');
      [patterns,units,selection].forEach((row,j)=>row.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.getAttribute('data-action')===(j===0?pattern:j===1?unit:'point-'+selected)))));
      Object.assign(root.dataset,{pattern,unit,selected,cov:s.cov,r:s.r,mx:s.mx,my:s.my,products:JSON.stringify(s.products)});
    }
    render();
  }
  function pearsonWidget(root) {
    const stage=root.querySelector('[data-stage]');let slope=1,noise=1,offset=0;
    const ctrl=controls(stage);
    const bs=slider(ctrl,'Наклон прямой β','slope',slope,-2,2,.1,v=>{slope=v;render();});
    const ns=slider(ctrl,'Сила шума σ','noise',noise,0,3,.25,v=>{noise=v;render();});
    const cs=slider(ctrl,'Сдвиг по вертикали c','offset',offset,-3,3,.5,v=>{offset=v;render();});
    const presets=controls(stage);
    button(presets,'Прямая без шума','perfect',()=>{slope=1;noise=0;offset=0;bs.sync(slope);ns.sync(noise);cs.sync(offset);render();});
    button(presets,'Все y одинаковы','constant',()=>{slope=0;noise=0;offset=1;bs.sync(slope);ns.sync(noise);cs.sync(offset);render();});
    const [svg]=plots(stage,['Как меняется линейная связь?']);
    stage.appendChild(node('p',{class:'c13-note'},'Синтетические точки: y = βx + c + σ·ε. Здесь ε — заранее сгенерированный шум; его значения закреплены и имеют выборочное стандартное отклонение 1. Пунктир — прямая без шума y = βx + c. При движении ползунков новые случайные значения не создаются.'));
    function render() {
      const {x,y}=pearsonData(slope,noise,offset),s=sampleStats(x,y),base=x.map(v=>slope*v+offset);
      const p=scatterFrame(svg,'Облако точек при заданных наклоне и шуме',[-3.5,3.5],axisRange([...y,...base],.15),'Признак x','Признак y');
      curve(p,x,base,C.gold);dots(p,x,y);
      const meaning=s.r===null?'Стандартное отклонение y равно нулю. В формуле r получилось бы деление на ноль: корреляция не определена.':Math.abs(s.r)>.999999?'Все точки лежат на одной негоризонтальной прямой. Модуль r равен 1.':'r описывает направление и тесноту линейной связи в этом облаке точек.';
      output(root,'<b>Коэффициент Пирсона r = '+number(s.r)+'.</b><br>Выборочная ковариация = '+fmt(s.cov)+'; sₓ = '+fmt(s.sx)+'; sᵧ = '+fmt(s.sy)+'.<br>'+(s.r===null?'': 'r = ковариация / (sₓ · sᵧ) = '+fmt(s.cov)+' / ('+fmt(s.sx)+' · '+fmt(s.sy)+') ≈ '+number(s.r)+'.<br>')+meaning+'<br>Прибавление c ко всем y меняет их среднее, но не ковариацию, стандартное отклонение и r. Числа на экране округлены.');
      Object.assign(root.dataset,{slope,noise,offset,cov:s.cov,sx:s.sx,sy:s.sy,r:JSON.stringify(s.r),x:JSON.stringify(x),y:JSON.stringify(y)});
    }
    render();
  }
  function geometryWidget(root) {
    const stage=root.querySelector('[data-stage]');let angle=45;
    const ctrl=controls(stage),as=slider(ctrl,'Угол θ между векторами, градусы','angle',angle,0,180,5,v=>{angle=v;render();});
    const presets=controls(stage);
    [[0,'Одинаковое направление'],[90,'Прямой угол'],[180,'Противоположные направления']].forEach(([a,t])=>button(presets,t,'angle-'+a,()=>{angle=a;as.sync(a);render();}));
    const [svg]=plots(stage,['Корреляция — косинус угла после центрирования']);
    legend(stage,[['u: нормированный центрированный x',C.blue],['v: нормированный центрированный y',C.green],['Проекция v на u',C.gold]]);
    stage.appendChild(node('p',{class:'c13-note'},'Это схема в плоскости двух векторов, а не диаграмма двух наблюдений. В данных x и y могут содержать много значений. Сначала из каждого столбца вычитают его среднее, затем делят полученный вектор на его длину. На схеме сохраняются длины полученных векторов и угол между ними; её оси — вспомогательные.'));
    function render() {
      const theta=angle*Math.PI/180,r=Math.cos(theta),v=[r,Math.sin(theta)],p=plane(svg,'Единичные векторы и угол '+angle+' градусов',1.45,['',''],[0,.3]);
      p.layer.appendChild(svgNode('circle',{cx:p.sx(0),cy:p.sy(0),r:p.u,fill:'none',stroke:C.grid,'stroke-width':1.5}));
      const arc=Array.from({length:Math.max(2,Math.ceil(angle/3)+1)},(_,i)=>{const a=theta*i/Math.max(1,Math.ceil(angle/3));return [p.sx(.35*Math.cos(a)),p.sy(.35*Math.sin(a))];});
      p.layer.appendChild(svgNode('polyline',{points:arc.map(v=>v.join(',')).join(' '),fill:'none',stroke:C.violet,'stroke-width':2}));
      line(p.layer,p.sx(v[0]),p.sy(v[1]),p.sx(v[0]),p.sy(0),C.gold,1.7,{'stroke-dasharray':'5 4'});
      arrow(p,[1,0],C.blue,'u',[0,0],false,4);arrow(p,v,C.green,'v',[0,0],angle===0,2.6);
      arrow(p,[r,0],C.gold,'',[0,0],true,2.2);label(p,[.52*Math.cos(theta/2),.52*Math.sin(theta/2)],angle+'°',C.violet);
      output(root,'<b>r = cos θ = cos '+angle+'° ≈ '+number(r)+'.</b><br>Оба вектора имеют длину 1. Их скалярное произведение равно r.<br>Для рисунка выбраны координаты u = (1; 0), v = ('+fmt(v[0])+'; '+fmt(v[1])+'). Они показывают угол, а не исходные значения признаков.<br>'+(angle<90?'Острый угол (или 0°): r положителен.':angle===90?'Прямой угол: r = 0. Это отсутствие линейной корреляции, а не доказательство независимости.':'Тупой угол (или 180°): r отрицателен.')+'<br>Если исходный столбец постоянный, его центрированный вектор нулевой. Нормировать его и определить такой угол нельзя.');
      Object.assign(root.dataset,{angle,r:Math.abs(r)<1e-12?0:r,vector:JSON.stringify(v)});
    }
    render();
  }
  function transformWidget(root) {
    const stage=root.querySelector('[data-stage]');let kind='cubic',noise=0;
    const presets=controls(stage);
    [['cubic','Куб: y = x³ + шум'],['quadratic','Квадрат: y = x² + шум'],['sine','Синус: y = sin(x) + шум']].forEach(([k,t])=>button(presets,t,k,()=>{kind=k;render();}));
    slider(controls(stage),'Сила шума σ','noise',noise,0,3,.25,v=>{noise=v;render();});
    const [raw,transformed]=plots(stage,['Исходный признак x','Новый признак z = f(x)']);
    stage.appendChild(node('p',{class:'c13-note'},'На обоих графиках одни и те же объекты и значения y. Меняется только горизонтальная координата: x заменяем на f(x). Пунктир показывает зависимость без шума. Для синуса x задан в радианах от −π до π. Шум фиксирован; ползунок меняет его силу.'));
    function render() {
      const {x,z,y}=transformData(kind,noise),rawStats=sampleStats(x,y),newStats=sampleStats(z,y),rho=spearman(x,y),f=kind==='cubic'?'x³':kind==='quadratic'?'x²':'sin(x)';
      const yrange=axisRange([...y,...z],.13);
      const p=scatterFrame(raw,'Исходная нелинейная связь',axisRange(x,.1),yrange,kind==='sine'?'x, радианы':'x','y');
      curve(p,x,z,C.gold);dots(p,x,y);
      const q=scatterFrame(transformed,'Связь после преобразования признака',axisRange(z,.1),yrange,'z = '+f,'y');
      const zs=[Math.min(...z),Math.max(...z)];curve(q,zs,zs,C.gold);dots(q,z,y,C.green);
      const note=kind==='cubic'?'Куб строго возрастает: без шума порядок x и y совпадает, поэтому ρ = 1. При этом зависимость искривлена и r не равен 1.':kind==='quadratic'?'Для симметричных x без шума r = 0 и ρ = 0, хотя y полностью определяется через x². Ранговая корреляция тоже не обнаруживает любую нелинейную связь.':'Синус на всём показанном интервале не возрастает и не убывает постоянно. Ни r, ни ρ не описывают полностью форму этой связи.';
      output(root,'<b>Исходные x и y: Пирсон r = '+number(rawStats.r)+'; Спирмен ρ = '+number(rho)+'.</b><br><b>Новый признак z = '+f+': Пирсон между z и y равен '+number(newStats.r)+'.</b><br>'+note+'<br>ρ — корреляция Пирсона между рангами исходных x и y; одинаковым значениям присваивается средний ранг. При σ = 0 после выбранного преобразования получаем прямую y = z. Здесь формула связи известна заранее: это учебный пример выбора признака.');
      presets.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.getAttribute('data-action')===kind)));
      Object.assign(root.dataset,{mode:kind,noise,r:rawStats.r,rho,transformedR:newStats.r,x:JSON.stringify(x),y:JSON.stringify(y),z:JSON.stringify(z)});
    }
    render();
  }
  function mount(root,kind,data=null) {
    if(!root||!root.querySelector('[data-stage]')||!root.querySelector('[data-readout]'))throw new Error('Correlation widget requires a stage and readout');
    const widgets={covariance:covarianceWidget,pearson:pearsonWidget,geometry:geometryWidget,transform:transformWidget};
    if(!widgets[kind])throw new Error('Unknown correlation widget: '+kind);
    style(root);widgets[kind](root,data);root.dataset.widget=kind;
  }
  global.CorrelationLesson13={mount,math:{mean,centered,dot,sampleStats,averageRanks,spearman,fixedNoise,pearsonData,transformData,apartmentAreas,apartmentPrices,feetPerSquareMetre}};
})(typeof window!=='undefined'?window:globalThis);
