/* Standalone matrix visualizations, embedded into 10_matrices.ipynb. */
(function (global) {
  'use strict';
  const C = {blue:'#6ab0f3', green:'#5fd08a', gold:'#e0b25a', rose:'#e0757f', violet:'#bd9ce8', ink:'#e6e9ec', soft:'#a7b0ba', grid:'#293440', bg:'#111820'};
  const fmt = x => Math.abs(x) < 1e-10 ? '0' : String(Number(Number(x).toFixed(2)));
  const clamp = (x, lo, hi) => Math.max(lo, Math.min(hi, x));
  const vector = x => '(' + x.map(fmt).join('; ') + ')';
  const shape = A => [A.length, A[0].length];
  const dot = (a, b) => { if (a.length !== b.length) throw new Error('Vector dimensions do not agree'); return a.reduce((s, x, i) => s + x*b[i], 0); };
  const transpose = A => A[0].map((_, j) => A.map(row => row[j]));
  function mul(A, B) {
    if (A[0].length !== B.length) throw new Error('Matrix dimensions do not agree');
    const cols = transpose(B);
    return A.map(row => cols.map(col => dot(row, col)));
  }
  const matvec = (A, x) => A.map(row => dot(row, x));
  const add = (A, B) => A.map((row, i) => row.map((v, j) => v + B[i][j]));
  const sub = (A, B) => A.map((row, i) => row.map((v, j) => v - B[i][j]));
  const scale = (A, k) => A.map(row => row.map(v => k*v));
  const signed = x => x < 0 ? '(' + fmt(x) + ')' : fmt(x);
  const dotRule = (a,b) => a.map((x,k) => `${signed(x)} · ${signed(b[k])}`).join(' + ');
  function node(tag, attrs = {}, value) {
    const e = document.createElement(tag);
    for (const [k,v] of Object.entries(attrs)) e.setAttribute(k,String(v));
    if (value !== undefined) e.textContent = value;
    return e;
  }
  function svgNode(tag, attrs = {}, value) {
    const e = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [k,v] of Object.entries(attrs)) e.setAttribute(k,String(v));
    if (value !== undefined) e.textContent = value;
    return e;
  }
  function svgText(svg, x, y, value, color = C.soft, anchor = 'middle', size = 12) {
    svg.appendChild(svgNode('text', {x,y,fill:color,'text-anchor':anchor,'font-size':size,'font-family':'system-ui,sans-serif'}, value));
  }
  function style(root) {
    root.classList.add('m10');
    root.appendChild(node('style', {}, `
      .m10 .m10-controls{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin:12px 0}
      .m10 .m10-control{display:flex;flex-direction:column;gap:5px;color:${C.ink};font-size:14px;min-width:150px}
      .m10 [hidden]{display:none!important}
      .m10 select,.m10 button{font:inherit;background:#18232f;color:${C.ink};border:1px solid #405164;border-radius:6px;padding:7px 10px;cursor:pointer}
      .m10 button:focus-visible,.m10 select:focus-visible,.m10 input:focus-visible{outline:3px solid ${C.gold};outline-offset:3px}
      .m10 button[aria-pressed=true]{background:#24435f;border-color:${C.blue};color:white}
      .m10 input[type=range]{width:150px;accent-color:${C.blue}}
      .m10 .m10-plots{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,270px),1fr));gap:10px}
      .m10 .m10-plot{min-width:0;background:#0f151d;border:1px solid ${C.grid};border-radius:8px}
      .m10 .m10-plot svg{width:100%;height:auto;display:block}
      .m10 .m10-matrices{display:flex;align-items:center;flex-wrap:wrap;gap:18px;margin:16px 0;overflow-x:auto}
      .m10 .m10-matrix{display:inline-flex;flex-direction:column;gap:7px;text-align:center;align-self:center}
      .m10 .m10-matrix>span{font-size:14px;color:${C.soft}}
      .m10 .m10-matrix table{border-collapse:separate;border-spacing:3px;border-left:2px solid ${C.soft};border-right:2px solid ${C.soft};border-radius:5px}
      .m10 .m10-matrix td{min-width:34px;padding:7px 9px;color:${C.ink};text-align:center;border-radius:4px;background:transparent;font-variant-numeric:tabular-nums}
      .m10 .m10-matrix td.m10-selected{background:#23455b;color:${C.blue}}
      .m10 .m10-matrix td.m10-column{background:#3f3550;color:${C.violet}}
      .m10 .m10-matrix td.m10-result{background:#284a37;color:${C.green}}
      .m10 .m10-matrix td:has(button){padding:0}
      .m10 .m10-matrix button{width:100%;padding:7px 9px;border-color:transparent;background:transparent}
      .m10 .m10-matrix td.m10-result button{color:${C.green};border-color:${C.green}}
      .m10 .m10-rows{display:flex;flex-wrap:wrap;gap:7px;align-items:flex-start;margin-bottom:10px}
      .m10 .m10-note{font-size:14px;line-height:1.55;color:${C.soft};margin:8px 0}
      .m10 .m10-eq{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;white-space:normal;line-height:1.7;color:${C.ink};overflow-wrap:anywhere}
      .m10 [data-readout]{line-height:1.65;overflow-wrap:anywhere}
      .m10 .m10-warning{color:${C.gold};padding:14px;border:1px solid #79633a;border-radius:7px}
      .m10 .m10-heading{font-size:15px;color:${C.ink};padding:12px 14px 0;font-weight:600}
      .m10 .m10-small{font-size:13px;color:${C.soft}}
    `));
  }
  function output(root, html) { root.querySelector('[data-readout]').innerHTML = html; }
  function controls(stage) { const d=node('div', {class:'m10-controls'}); stage.appendChild(d); return d; }
  function dropdown(container, label, key, options, value, onChange) {
    const wrap=node('label',{class:'m10-control'}), caption=node('span',{},label), select=node('select',{'data-control':key});
    for(const [v,t] of options) select.appendChild(node('option',{value:v},t));
    select.value=String(value); select.addEventListener('change',()=>onChange(select.value));
    wrap.append(caption,select); container.appendChild(wrap); return select;
  }
  function slider(container,label,key,value,min,max,step,onInput) {
    const wrap=node('label',{class:'m10-control'}),caption=node('span'), range=node('input',{type:'range','data-control':key,min,max,step,value});
    function sync(v) { range.value=String(v); caption.textContent=label+' = '+fmt(v); range.setAttribute('aria-valuetext',label+' = '+fmt(v)); }
    range.addEventListener('input',()=>{sync(Number(range.value));onInput(Number(range.value));});
    sync(value); wrap.append(caption,range);container.appendChild(wrap);return {range,sync,wrap};
  }
  function button(container,label,key,fn) { const b=node('button',{type:'button','data-action':key},label);b.addEventListener('click',fn);container.appendChild(b);return b; }
  function matrix(container,A,label,opts={}) {
    const wrap=node('div',{class:'m10-matrix'}),title=node('span',{},label+' · '+shape(A).join(' × ')),table=node('table',{'aria-label':label});
    A.forEach((row,i)=>{
      const tr=node('tr');
      row.forEach((v,j)=>{
        const selected=opts.cell&&opts.cell[0]===i&&opts.cell[1]===j;
        const td=node('td',{class:selected?'m10-result':opts.row===i?'m10-selected':opts.col===j?'m10-column':''});
        if(opts.click) { const b=node('button',{type:'button','data-cell':i+','+j,'aria-label':label+', строка '+(i+1)+', столбец '+(j+1)+': '+fmt(v),'aria-pressed':String(!!selected)},fmt(v));b.addEventListener('click',()=>{opts.click(i,j);const next=container.querySelector('[data-cell="'+i+','+j+'"]');if(next)next.focus({preventScroll:true});});td.appendChild(b); }
        else td.textContent=fmt(v);
        tr.appendChild(td);
      });table.appendChild(tr);
    });wrap.append(title,table);container.appendChild(wrap);return wrap;
  }
  function plots(stage,titles) {
    const row=node('div',{class:'m10-plots'});stage.appendChild(row);
    return titles.map(title=>{const d=node('div',{class:'m10-plot'}),s=svgNode('svg');d.append(node('div',{class:'m10-heading'},title),s);row.appendChild(d);return s;});
  }
  function line(svg,x1,y1,x2,y2,color,width=1,extra={}) {svg.appendChild(svgNode('line',{x1,y1,x2,y2,stroke:color,'stroke-width':width,...extra}));}
  function plane(svg,title,limit=8) {
    svg.replaceChildren();svg.setAttribute('viewBox','0 0 420 420');svg.setAttribute('role','img');svg.setAttribute('aria-label',title);svg.appendChild(svgNode('title',{},title));
    const L=42,R=400,T=28,B=386,u=(R-L)/(2*limit),sx=x=>L+(x+limit)*u,sy=y=>B-(y+limit)*u;
    // The drawing area is a square: one unit has equal x/y pixel lengths.
    const id='m10-clip-'+(global.__matrixLesson10ClipCounter=(global.__matrixLesson10ClipCounter||0)+1),defs=svgNode('defs'),clip=svgNode('clipPath',{id});clip.appendChild(svgNode('rect',{x:L,y:T,width:R-L,height:B-T}));defs.appendChild(clip);svg.appendChild(defs);
    for(let x=-limit;x<=limit;x++)line(svg,sx(x),T,sx(x),B,C.grid,1,{'stroke-opacity':.7});
    for(let y=-limit;y<=limit;y++)line(svg,L,sy(y),R,sy(y),C.grid,1,{'stroke-opacity':.7});
    line(svg,L,sy(0),R,sy(0),C.soft,1.2);line(svg,sx(0),T,sx(0),B,C.soft,1.2);
    const tick=limit>4?2:1;
    for(let k=-limit;k<=limit;k+=tick) { if(k!==0){svgText(svg,sx(k),sy(0)+16,fmt(k),C.soft,'middle',10);svgText(svg,sx(0)-8,sy(k)+4,fmt(k),C.soft,'end',10);} }
    svgText(svg,R-3,sy(0)-9,'x₁',C.ink,'end');svgText(svg,sx(0)+10,T+10,'x₂',C.ink,'start');
    const layer=svgNode('g',{'clip-path':'url(#'+id+')'});svg.appendChild(layer);
    return {svg,layer,L,R,T,B,u,sx,sy,limit,labelBoxes:[]};
  }
  function arrow(p,end,color,label,start=[0,0],dashed=false) {
    const x1=p.sx(start[0]),y1=p.sy(start[1]),x2=p.sx(end[0]),y2=p.sy(end[1]);
    line(p.layer,x1,y1,x2,y2,color,2.6,dashed?{'stroke-dasharray':'5 4'}:{});
    const dx=x2-x1,dy=y2-y1,length=Math.hypot(dx,dy);
    if(length>1) {
      const ux=dx/length,uy=dy/length,head=Math.min(9,length*.35),w=head*.48;
      p.layer.appendChild(svgNode('polygon',{points:`${x2},${y2} ${x2-head*ux+w*uy},${y2-head*uy-w*ux} ${x2-head*ux-w*uy},${y2-head*uy+w*ux}`,fill:color}));
    } else p.layer.appendChild(svgNode('circle',{cx:x2,cy:y2,r:3,fill:color}));
    if(label) {
      const width=label.length*8+6,height=17;
      const candidates=[[x2+9,y2-12],[x2+9,y2+23],[x2-width-9,y2-12],[x2-width-9,y2+23],[x2+9,y2-32]];
      let choice;
      for(const [cx,cy] of candidates) {
        const lx=clamp(cx,p.L+3,p.R-width-3),ly=clamp(cy,p.T+height,p.B-3),box={x:lx,y:ly-height,w:width,h:height};
        choice=box;
        if(!p.labelBoxes.some(b=>box.x<b.x+b.w&&box.x+box.w>b.x&&box.y<b.y+b.h&&box.y+box.h>b.y))break;
      }
      p.labelBoxes.push(choice);
      const textAttrs={x:choice.x,y:choice.y+height,'font-size':13,'font-family':'system-ui,sans-serif'};
      p.layer.appendChild(svgNode('text',{...textAttrs,fill:C.bg,stroke:C.bg,'stroke-width':3,'stroke-linejoin':'round','aria-hidden':'true'},label));
      p.layer.appendChild(svgNode('text',{...textAttrs,fill:color},label));
    }
  }
  function polygon(p,points,color,opacity=.12) {p.layer.appendChild(svgNode('polygon',{points:points.map(x=>p.sx(x[0])+','+p.sy(x[1])).join(' '),fill:color,'fill-opacity':opacity,stroke:color,'stroke-width':1.4}));}
  const cloud=[[-1.5,-1],[0,-1],[1,.2],[.4,1.7],[-1.5,1]];
  function points(p,values,color) {polygon(p,values,color,.1);for(const v of values)p.layer.appendChild(svgNode('circle',{cx:p.sx(v[0]),cy:p.sy(v[1]),r:3.5,fill:color}));}
  function transformedGrid(p,A) {
    for(let t=-3;t<=3;t++) {
      const a=matvec(A,[t,-3]),b=matvec(A,[t,3]),c=matvec(A,[-3,t]),d=matvec(A,[3,t]);
      line(p.layer,p.sx(a[0]),p.sy(a[1]),p.sx(b[0]),p.sy(b[1]),C.violet,1,{'stroke-opacity':.3});
      line(p.layer,p.sx(c[0]),p.sy(c[1]),p.sx(d[0]),p.sy(d[1]),C.violet,1,{'stroke-opacity':.3});
    }
  }

  function dataWidget(root,data) {
    const stage=root.querySelector('[data-stage]'),X=data.X,labels=data.labels||['Признак 1','Признак 2'];let selected=0;
    const row=node('div',{class:'m10-rows'}),mats=node('div',{class:'m10-matrices'});stage.append(row,mats);
    const [svg]=plots(stage,['Наблюдение в таблице и точка на плоскости']);
    X.forEach((_,i)=>button(row,'Строка '+(i+1),'row-'+i,()=>{selected=i;render();}));
    function render() {
      row.querySelectorAll('button').forEach((b,i)=>b.setAttribute('aria-pressed',String(i===selected)));
      mats.replaceChildren();matrix(mats,X,'X',{row:selected,click:i=>{selected=i;render();}});
      svg.replaceChildren();svg.setAttribute('viewBox','0 0 640 410');svg.setAttribute('role','img');svg.setAttribute('aria-label','Каждой строке матрицы соответствует точка: '+labels.join(', '));
      const xs=X.map(x=>x[0]),ys=X.map(x=>x[1]),xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...ys),ymax=Math.max(...ys),dx=Math.max(1,xmax-xmin),dy=Math.max(1,ymax-ymin);
      const xlo=xmin-.15*dx,xhi=xmax+.15*dx,ylo=ymin-.15*dy,yhi=ymax+.15*dy,L=75,R=610,T=28,B=340;
      const sx=x=>L+(x-xlo)/(xhi-xlo)*(R-L),sy=y=>B-(y-ylo)/(yhi-ylo)*(B-T);
      for(let k=0;k<=4;k++) { const x=xlo+(xhi-xlo)*k/4,y=ylo+(yhi-ylo)*k/4;line(svg,sx(x),T,sx(x),B,C.grid);line(svg,L,sy(y),R,sy(y),C.grid);svgText(svg,sx(x),B+23,fmt(x));svgText(svg,L-10,sy(y)+4,fmt(y),C.soft,'end'); }
      svgText(svg,(L+R)/2,394,labels[0],C.ink);svgText(svg,L,T-9,labels[1],C.ink,'start');
      X.forEach((v,i)=>{svg.appendChild(svgNode('circle',{cx:sx(v[0]),cy:sy(v[1]),r:i===selected?8:5,fill:i===selected?C.gold:C.blue,'fill-opacity':i===selected?1:.65}));svgText(svg,sx(v[0])+10,sy(v[1])-11,String(i+1),i===selected?C.gold:C.soft,'start');});
      output(root,`<b>Матрица X: ${X.length} строк × ${X[0].length} столбца.</b><br>Строка ${selected+1}: ${vector(X[selected])}. Это одно наблюдение и одна точка на графике.<br>В NumPy та же строка: <code>X[${selected}]</code>. Нумерация в формулах начинается с 1, в NumPy — с 0.`);
      Object.assign(root.dataset,{selected,nRows:X.length,nCols:X[0].length});
    }render();
  }
  function operations(root) {
    const stage=root.querySelector('[data-stage]'),A=[[1,2,3],[4,5,6]],B=[[6,5,4],[3,2,1]];let mode='add',k=2,ij=[0,1];
    const ctrl=controls(stage),mats=node('div',{class:'m10-matrices'});stage.appendChild(mats);
    dropdown(ctrl,'Операция','operation',[['add','A + B'],['sub','A − B'],['scalar','Умножение на число k'],['transpose','Aᵀ — транспонирование']],mode,v=>{mode=v;render();});
    const ks=slider(ctrl,'Множитель k (для каждого элемента A)','scalar',k,-2,3,.5,v=>{k=v;render();});
    const scalarNote=node('p',{class:'m10-note','data-scalar-note':''},'k — обычное число, или скалярный коэффициент. Ползунок выбирает это число: каждый элемент матрицы A умножается на одно и то же k.');
    stage.appendChild(scalarNote);
    stage.appendChild(node('p',{class:'m10-note'},'Нажмите на элемент A: проследите, какой элемент результата с ним связан.'));
    function render() {
      const D=mode==='add'?add(A,B):mode==='sub'?sub(A,B):mode==='scalar'?scale(A,k):transpose(A),outCell=mode==='transpose'?[ij[1],ij[0]]:ij;
      ks.wrap.hidden=mode!=='scalar';ks.range.disabled=mode!=='scalar';scalarNote.hidden=mode!=='scalar';mats.replaceChildren();matrix(mats,A,'A',{cell:ij,click:(i,j)=>{ij=[i,j];render();}});
      if(mode==='add'||mode==='sub'){mats.appendChild(node('span',{},mode==='add'?'+':'−'));matrix(mats,B,'B',{cell:ij});}
      if(mode==='scalar')mats.appendChild(node('span',{},'× '+fmt(k)));
      mats.appendChild(node('span',{},'→'));matrix(mats,D,mode==='transpose'?'Aᵀ':'Результат',{cell:outCell});
      const i=ij[0],j=ij[1],v=A[i][j];
      const rule=mode==='add'?`${v} + ${B[i][j]} = ${D[i][j]}`:mode==='sub'?`${v} − ${B[i][j]} = ${D[i][j]}`:mode==='scalar'?`${fmt(k)} · ${v} = ${fmt(D[i][j])}`:`a${i+1}${j+1} = ${v} → элемент (${j+1}, ${i+1}) в Aᵀ`;
      const code=mode==='add'?'A + B':mode==='sub'?'A - B':mode==='scalar'?'k * A':'A.T';
      const scalarCase=k===0?'При k = 0 все элементы результата равны нулю.':k===1?'При k = 1 матрица не меняется.':k===-1?'При k = −1 каждый элемент меняет знак.':'';
      output(root,mode==='scalar'
        ? `<b>Множитель k = ${fmt(k)}. ${rule}.</b><br>В строке ${i+1}, столбце ${j+1} число ${v} превратилось в ${fmt(D[i][j])}. Остальные элементы умножаются на то же число ${fmt(k)}.<br>${scalarCase?scalarCase+'<br>':''}NumPy: <code>${code}</code>.`
        : `<b>${rule}</b><br>${mode==='transpose'?'Строки становятся столбцами. Размер 2 × 3 превращается в 3 × 2.':'Складываем или вычитаем элементы на одинаковых местах. Размеры A и B должны совпадать.'}<br>NumPy: <code>${code}</code>.`);
      Object.assign(root.dataset,{operation:mode,scalar:k,row:i,col:j,result:JSON.stringify(D)});
    }render();
  }
  function transform(root) {
    const stage=root.querySelector('[data-stage]');let A=[[2,1],[0,1]],x=[1,2],dragColumn=null,dragLimit=null,lastPlane;
    const presets={identity:[[1,0],[0,1]],stretch:[[2,0],[0,1]],rotation:[[0,-1],[1,0]],reflection:[[-1,0],[0,1]],shear:[[1,1],[0,1]],custom:null};
    const first=controls(stage);
    const select=dropdown(first,'Пример','preset',[['custom','Своя матрица'],['identity','Без изменений'],['stretch','Растяжение по горизонтали'],['rotation','Поворот на 90°'],['reflection','Отражение относительно x₂'],['shear','Скос по горизонтали']], 'custom',key=>{if(presets[key])A=presets[key].map(row=>[...row]);sync();render();});
    const ac=controls(stage),sliders=[];
    for(let i=0;i<2;i++)for(let j=0;j<2;j++)sliders.push(slider(ac,'a'+(i+1)+(j+1),'a'+i+j,A[i][j],-2,2,.25,v=>{A[i][j]=v;select.value='custom';render();}));
    const xc=controls(stage);slider(xc,'x₁','x0',x[0],-2,2,.25,v=>{x[0]=v;render();});slider(xc,'x₂','x1',x[1],-2,2,.25,v=>{x[1]=v;render();});
    const mats=node('div',{class:'m10-matrices'});stage.appendChild(mats);
    const [before,after]=plots(stage,['Исходные векторы и точки','Результат умножения на A']);
    after.style.touchAction='none';
    stage.appendChild(node('p',{class:'m10-note'},'Синяя и зелёная стрелки — два единичных вектора и их образы. Золотая — x и Ax. Можно перетаскивать круглые концы синей и зелёной стрелок справа; ползунки делают то же самое. Серые оси и сетка остаются на месте; фиолетовая сетка преобразована матрицей. Масштаб подбирается автоматически и всегда одинаков на обоих графиках.'));
    function sync(){sliders.forEach((s,k)=>s.sync(A[Math.floor(k/2)][k%2]));}
    function render(){
      const y=matvec(A,x),cols=transpose(A),square=[[0,0],[1,0],[1,1],[0,1]],part1=cols[0].map(v=>v*x[0]);
      const visible=[x,y,part1,...cols,...cloud,...square,...cloud.map(v=>matvec(A,v)),...square.map(v=>matvec(A,v))];
      const autoLimit=Math.max(3,Math.ceil(Math.max(...visible.flat().map(Math.abs))+.75));
      const limit=dragColumn===null?autoLimit:dragLimit;
      const p=plane(before,'Исходная плоскость, одинаковый масштаб по обеим осям',limit),q=plane(after,'Преобразованная плоскость: два столбца A и вектор Ax',limit);lastPlane=q;
      polygon(p,[[0,0],[1,0],[1,1],[0,1]],C.blue,.13);points(p,cloud,C.soft);arrow(p,[1,0],C.blue,'e₁');arrow(p,[0,1],C.green,'e₂');arrow(p,x,C.gold,'x');
      transformedGrid(q,A);polygon(q,[[0,0],[1,0],[1,1],[0,1]].map(v=>matvec(A,v)),C.blue,.14);points(q,cloud.map(v=>matvec(A,v)),C.soft);
      arrow(q,part1,C.blue,'', [0,0],true);arrow(q,y,C.green,'',part1,true);
      arrow(q,cols[0],C.blue,'Ae₁');arrow(q,cols[1],C.green,'Ae₂');arrow(q,y,C.gold,'Ax');
      cols.forEach((v,j)=>q.layer.appendChild(svgNode('circle',{cx:q.sx(v[0]),cy:q.sy(v[1]),r:6,fill:j?C.green:C.blue,stroke:C.bg,'stroke-width':2,'data-column':j,style:'cursor:grab'})));
      mats.replaceChildren();matrix(mats,A,'A');mats.appendChild(node('span',{},'×'));matrix(mats,x.map(v=>[v]),'x');mats.appendChild(node('span',{},'='));matrix(mats,y.map(v=>[v]),'Ax');
      output(root,`<b>Столбцы A показывают, куда переходят e₁ = (1; 0) и e₂ = (0; 1).</b><br><span style="color:${C.blue}">Ae₁ = ${vector(cols[0])}</span>; <span style="color:${C.green}">Ae₂ = ${vector(cols[1])}</span>.<br>Линейная комбинация: Ax = ${signed(x[0])} · ${vector(cols[0])} + ${signed(x[1])} · ${vector(cols[1])} = <b>${vector(y)}</b>.<br>Координаты x — коэффициенты перед столбцами A. NumPy: <code>A @ x</code>.`);
      Object.assign(root.dataset,{matrix:JSON.stringify(A),vector:JSON.stringify(x),result:JSON.stringify(y),limit});
    }
    // Pointer capture stays on the SVG, which survives every redraw.
    after.addEventListener('pointerdown',e=>{const raw=e.target.getAttribute('data-column');if(raw===null)return;dragColumn=Number(raw);dragLimit=lastPlane.limit;after.setPointerCapture(e.pointerId);e.preventDefault();});
    after.addEventListener('pointermove',e=>{
      if(dragColumn===null)return;const rect=after.getBoundingClientRect(),s=Math.min(rect.width/420,rect.height/420),ox=(rect.width-420*s)/2,oy=(rect.height-420*s)/2;
      const px=(e.clientX-rect.left-ox)/s,py=(e.clientY-rect.top-oy)/s;
      A[0][dragColumn]=Math.round(clamp((px-lastPlane.L)/lastPlane.u-lastPlane.limit,-2,2)*4)/4;
      A[1][dragColumn]=Math.round(clamp((lastPlane.B-py)/lastPlane.u-lastPlane.limit,-2,2)*4)/4;
      select.value='custom';sync();render();
    });
    const release=e=>{if(dragColumn===null)return;dragColumn=null;dragLimit=null;if(after.hasPointerCapture&&after.hasPointerCapture(e.pointerId))after.releasePointerCapture(e.pointerId);render();};
    after.addEventListener('pointerup',release);after.addEventListener('pointercancel',release);render();
  }
  function multiply(root) {
    const stage=root.querySelector('[data-stage]');let preset='rect',cell=[0,0];
    const cases={rect:{A:[[1,2,0],[-1,3,1]],B:[[2,1],[0,4],[3,-2]]},square:{A:[[2,1],[0,1]],B:[[1,-1],[2,0]]},bad:{A:[[1,2,3],[4,5,6]],B:[[1,2],[3,4]]}};
    const ctrl=controls(stage),mats=node('div',{class:'m10-matrices'});stage.appendChild(mats);
    dropdown(ctrl,'Пример','example',[['rect','2 × 3 на 3 × 2'],['square','2 × 2 на 2 × 2'],['bad','Несогласованные размеры']],preset,v=>{preset=v;cell=[0,0];render();});
    stage.appendChild(node('p',{class:'m10-note'},'Нажмите на элемент результата: подсветятся нужная строка A и нужный столбец B.'));
    function render(){
      const {A,B}=cases[preset],compatible=A[0].length===B.length;mats.replaceChildren();
      matrix(mats,A,'A',compatible?{row:cell[0]}:{});mats.appendChild(node('span',{},'×'));matrix(mats,B,'B',compatible?{col:cell[1]}:{});mats.appendChild(node('span',{},'='));
      if(!compatible){mats.appendChild(node('div',{class:'m10-warning'},'Произведение не определено: 3 ≠ 2.'));output(root,'<b>(2 × 3) · (2 × 2): внутренние размеры 3 и 2 не совпадают.</b><br>В строке A три числа, а в столбце B два. Скалярное произведение этих векторов не определено. NumPy для <code>A @ B</code> сообщит об ошибке размеров.');Object.assign(root.dataset,{compatible:'false',result:''});return;}
      const D=mul(A,B),i=cell[0],j=cell[1],col=B.map(row=>row[j]);matrix(mats,D,'AB',{cell,click:(r,c)=>{cell=[r,c];render();}});
      output(root,`<b>Элемент (${i+1}, ${j+1}): строка ${i+1} из A · столбец ${j+1} из B.</b><br><span class="m10-eq">${A[i].map((v,k)=>`<span style="color:${C.blue}">${signed(v)}</span> · <span style="color:${C.violet}">${signed(col[k])}</span>`).join(' + ')} = <b style="color:${C.green}">${fmt(D[i][j])}</b></span><br>(${shape(A).join(' × ')}) · (${shape(B).join(' × ')}) → ${shape(D).join(' × ')}. Внутренние размеры совпали; внешние дают размер результата.<br>NumPy: <code>A @ B</code> или <code>np.dot(A, B)</code> для двух двумерных массивов.`);
      Object.assign(root.dataset,{compatible:'true',row:i,col:j,result:JSON.stringify(D)});
    }render();
  }
  function composition(root) {
    const stage=root.querySelector('[data-stage]'),S=[[2,0],[0,1]],R=[[0,-1],[1,0]],x=[1,0];let order='RS',step=2;
    const ctrl=controls(stage),mats=node('div',{class:'m10-matrices'});stage.appendChild(mats);
    dropdown(ctrl,'Порядок действий','order',[['RS','Сначала S, затем R: R @ S'],['SR','Сначала R, затем S: S @ R']],order,v=>{order=v;render();});
    const steps=slider(ctrl,'Шаг','step',step,0,2,1,v=>{step=v;render();});
    const btns=controls(stage);for(let k=0;k<=2;k++)button(btns,['Исходные','После первого действия','После двух действий'][k],'step-'+k,()=>{step=k;steps.sync(k);render();});
    const [left,right]=plots(stage,['Два действия по очереди','Одно умножение на произведение']);
    stage.appendChild(node('p',{class:'m10-note'},'S растягивает по горизонтали в 2 раза; R поворачивает на 90° против часовой стрелки. В обоих графиках масштабы осей одинаковы.'));
    function render(){
      const first=order==='RS'?S:R,second=order==='RS'?R:S,firstName=order==='RS'?'S':'R',secondName=order==='RS'?'R':'S',P=mul(second,first),middle=matvec(first,x),end=matvec(P,x),M=step===0?[[1,0],[0,1]]:step===1?first:P;
      const p=plane(left,'Последовательные преобразования',5),q=plane(right,'Умножение на произведение двух матриц',5);
      points(p,cloud,C.soft);points(q,cloud,C.soft);
      if(step>0)points(p,cloud.map(v=>matvec(M,v)),step===1?C.blue:C.gold);
      points(q,cloud.map(v=>matvec(P,v)),C.gold);
      arrow(p,x,C.soft,'x');if(step>=1)arrow(p,middle,C.blue,firstName+'x');if(step===2)arrow(p,end,C.gold,secondName+firstName+'x');arrow(q,end,C.gold,secondName+firstName+'x');
      mats.replaceChildren();matrix(mats,second,secondName);mats.appendChild(node('span',{},'×'));matrix(mats,first,firstName);mats.appendChild(node('span',{},'='));matrix(mats,P,secondName+firstName);
      btns.querySelectorAll('button').forEach((b,k)=>b.setAttribute('aria-pressed',String(k===step)));
      output(root,`<b>Сначала действует правая матрица: ${firstName}, затем ${secondName}.</b><br>x = ${vector(x)} → ${firstName}x = ${vector(middle)} → ${secondName}(${firstName}x) = ${vector(end)}.<br>Произведение ${secondName}${firstName} даёт тот же итог за одно умножение: (${secondName}${firstName})x = ${vector(end)}.<br>Слева показан шаг ${step}; справа — итог обоих действий. NumPy: <code>${secondName} @ (${firstName} @ x)</code> и <code>(${secondName} @ ${firstName}) @ x</code>.`);
      Object.assign(root.dataset,{order,step,result:JSON.stringify(P),endpoint:JSON.stringify(end)});
    }render();
  }
  const widgets={data:dataWidget,operations,transform,multiply,composition};
  global.MatricesLesson10={
    mount:(root,kind,data={})=>{if(!root||!widgets[kind])throw new Error('Unknown widget: '+kind);if(!root.querySelector('[data-stage]')||!root.querySelector('[data-readout]'))throw new Error('Widget requires data-stage and data-readout');root.querySelector('[data-stage]').replaceChildren();style(root);widgets[kind](root,data);},
    math:{dot,transpose,mul,matvec,add,sub,scale}
  };
})(typeof window!=='undefined'?window:globalThis);
