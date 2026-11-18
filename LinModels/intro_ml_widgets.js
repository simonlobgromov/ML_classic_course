/* Standalone visual exercises for the introductory machine-learning lesson. */
(function (global) {
  'use strict';
  const C = {blue:'#6ab0f3',green:'#5fd08a',gold:'#e0b25a',rose:'#e0757f',violet:'#bd9ce8',ink:'#e6e9ec',soft:'#a7b0ba',grid:'#293440',bg:'#111820'};
  const fmt = (value, digits = 2) => {
    if (!Number.isFinite(value)) return '—';
    const x = Math.abs(value) < 1e-10 ? 0 : value;
    return x.toLocaleString('ru-RU', {maximumFractionDigits:digits});
  };
  const mean = values => values.reduce((sum, value) => sum + value, 0) / values.length;
  function losses(actual, predicted) {
    if (!actual.length || actual.length !== predicted.length) throw new Error('Paired values are required');
    const errors = actual.map((y, i) => y - predicted[i]);
    const squared = errors.map(e => e * e), absolute = errors.map(Math.abs);
    const mse = mean(squared);
    return {errors,squared,absolute,mse,mae:mean(absolute),rmse:Math.sqrt(mse)};
  }
  const key = (n, sigma, rep) => [n,sigma,rep].join('|');
  const finiteArray = a => Array.isArray(a) && a.length > 0 && a.every(Number.isFinite);
  function node(tag, attrs = {}, value) {
    const element = document.createElement(tag);
    Object.entries(attrs).forEach(([name, val]) => element.setAttribute(name, String(val)));
    if (value !== undefined) element.textContent = value;
    return element;
  }
  function svgNode(tag, attrs = {}, value) {
    const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
    Object.entries(attrs).forEach(([name, val]) => element.setAttribute(name, String(val)));
    if (value !== undefined) element.textContent = value;
    return element;
  }
  function text(svg, x, y, value, color = C.soft, anchor = 'middle', size = 18) {
    svg.appendChild(svgNode('text', {x,y,fill:color,'text-anchor':anchor,'font-family':'system-ui,sans-serif','font-size':size}, value));
  }
  function line(svg, x1, y1, x2, y2, color, width = 1, attrs = {}) {
    svg.appendChild(svgNode('line', {x1,y1,x2,y2,stroke:color,'stroke-width':width,...attrs}));
  }
  function styles(root) {
    root.classList.add('iml');
    const old = root.querySelector('[data-intro-ml-style]');
    if (old) old.remove();
    root.appendChild(node('style', {'data-intro-ml-style':''}, `
      .iml [hidden]{display:none!important}
      .iml .iml-controls{display:flex;flex-wrap:wrap;align-items:flex-end;gap:12px 18px;margin:14px 0}
      .iml .iml-control{display:flex;flex-direction:column;gap:7px;min-width:165px;font:14px/1.45 system-ui,sans-serif;color:${C.ink}}
      .iml .iml-controls label{cursor:pointer}
      .iml .iml-check{display:flex;align-items:center;gap:9px;font:14px/1.5 system-ui,sans-serif;color:${C.ink};min-height:40px}
      .iml input[type=checkbox]{width:19px;height:19px;accent-color:${C.green}}
      .iml input[type=range]{width:210px;max-width:100%;accent-color:${C.blue};min-height:30px}
      .iml select,.iml button{font:14px/1.4 system-ui,sans-serif;background:#18232f;color:${C.ink};border:1px solid #405164;border-radius:8px;padding:10px 13px;min-height:42px;cursor:pointer}
      .iml button:focus-visible,.iml select:focus-visible,.iml input:focus-visible{outline:3px solid ${C.gold};outline-offset:3px}
      .iml button[aria-pressed=true]{background:#25445e;border-color:${C.blue};color:white}
      .iml button:disabled,.iml select:disabled{opacity:.45;cursor:default}
      .iml .iml-primary{border-color:${C.green};background:#1c3c2b;color:#d1f4dc}
      .iml .iml-layout{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(280px,1fr);gap:14px;margin:14px 0}
      .iml .iml-chart{min-width:0;overflow-x:auto;background:#0f151d;border:1px solid ${C.grid};border-radius:12px}
      .iml .iml-chart svg{display:block;width:100%;height:auto;min-width:360px}
      .iml .iml-bars svg{min-width:280px}
      .iml .iml-heading{padding:15px 17px 0;font:600 15px/1.5 system-ui,sans-serif;color:${C.ink}}
      .iml .iml-single{max-width:820px;margin:14px auto}
      .iml .iml-legend{display:flex;flex-wrap:wrap;gap:8px 20px;font:14px/1.5 system-ui,sans-serif;margin:12px 0}
      .iml .iml-note{font:14px/1.6 system-ui,sans-serif;color:${C.soft};margin:10px 0}
      .iml .iml-status{border-left:3px solid ${C.blue};padding:10px 13px;margin:12px 0;background:#172330;color:${C.ink};font:14px/1.65 system-ui,sans-serif}
      .iml .iml-status[data-locked=true]{border-color:${C.violet};background:#242032}
      .iml .iml-table-wrap{overflow-x:auto;margin:16px 0}
      .iml table{border-collapse:collapse;min-width:620px;width:100%;font:14px/1.5 system-ui,sans-serif;font-variant-numeric:tabular-nums;color:${C.ink}}
      .iml th,.iml td{padding:10px 12px;text-align:center;border-bottom:1px solid ${C.grid}}
      .iml th{font-weight:500;color:${C.soft}}
      .iml .iml-selected{background:#29291f}
      .iml .iml-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:16px 0}
      .iml .iml-metric{border:1px solid ${C.grid};border-radius:10px;padding:14px;background:#121c27;font:14px/1.5 system-ui,sans-serif}
      .iml .iml-metric strong{display:block;font-size:26px;color:${C.gold};font-variant-numeric:tabular-nums;margin:5px 0}
      .iml .iml-metric span{color:${C.soft}}
      .iml [data-readout]{font:15px/1.75 system-ui,sans-serif;overflow-wrap:anywhere}
      @media(max-width:760px){.iml .iml-layout{grid-template-columns:1fr}.iml .iml-bars svg{max-height:360px}.iml .iml-metrics{grid-template-columns:1fr}.iml .iml-metric strong{display:inline-block;margin:0 10px}}
    `));
  }
  function controls(stage) { const wrap = node('div', {class:'iml-controls'}); stage.appendChild(wrap); return wrap; }
  function slider(parent, title, name, value, min, max, step, callback, suffix = '') {
    const wrap = node('label', {class:'iml-control'}), caption = node('span');
    const input = node('input', {type:'range','data-control':name,min,max,step,value});
    function sync(v) { input.value = String(v); caption.textContent = title + ': ' + fmt(v) + suffix; input.setAttribute('aria-valuetext', fmt(v) + suffix); }
    input.addEventListener('input', () => {sync(Number(input.value));callback(Number(input.value));});
    sync(value);wrap.append(caption,input);parent.appendChild(wrap);return {input,sync};
  }
  function checkbox(parent, title, name, checked, callback) {
    const wrap=node('label',{class:'iml-check'}),input=node('input',{type:'checkbox','data-control':name});
    input.checked=checked;input.addEventListener('change',()=>callback(input.checked));wrap.append(input,node('span',{},title));parent.appendChild(wrap);return input;
  }
  function dropdown(parent,title,name,values,value,callback,format = fmt) {
    const wrap=node('label',{class:'iml-control'}),select=node('select',{'data-control':name});
    values.forEach(v=>select.appendChild(node('option',{value:v},format(v))));select.value=String(value);
    select.addEventListener('change',()=>callback(Number(select.value)));wrap.append(node('span',{},title),select);parent.appendChild(wrap);return select;
  }
  function button(parent,title,name,callback,primary=false) {
    const b=node('button',{type:'button','data-action':name,class:primary?'iml-primary':''},title);b.addEventListener('click',callback);parent.appendChild(b);return b;
  }
  function chart(parent,title,extra='') {
    const panel=node('div',{class:'iml-chart '+extra}),svg=svgNode('svg');
    panel.append(node('div',{class:'iml-heading'},title),svg);parent.appendChild(panel);return svg;
  }
  function legend(parent,entries) {
    const wrap=node('div',{class:'iml-legend'});entries.forEach(([value,color])=>wrap.appendChild(node('span',{style:'color:'+color},value)));parent.appendChild(wrap);return wrap;
  }
  function output(root,value) {root.querySelector('[data-readout]').innerHTML=value;}
  function range(values,padding=.1) {
    const lo=Math.min(...values),hi=Math.max(...values),span=hi-lo||Math.max(1,Math.abs(lo)*.1);
    return [lo-padding*span,hi+padding*span];
  }
  function ticks(lo,hi) {
    const raw=(hi-lo)/4,power=10**Math.floor(Math.log10(raw)),ratio=raw/power;
    const step=(ratio<=1?1:ratio<=2?2:ratio<=2.5?2.5:ratio<=5?5:10)*power,values=[];
    for(let v=Math.ceil(lo/step)*step;v<=hi+step*1e-8;v+=step)values.push(v);
    return values;
  }
  function frame(svg,title,xrange,yrange,xlabel='Расстояние, км',ylabel='Время, мин') {
    svg.replaceChildren();svg.setAttribute('viewBox','0 0 520 400');svg.setAttribute('role','img');svg.setAttribute('aria-label',title);svg.appendChild(svgNode('title',{},title));
    const L=68,R=496,T=40,B=330,sx=x=>L+(x-xrange[0])/(xrange[1]-xrange[0])*(R-L),sy=y=>B-(y-yrange[0])/(yrange[1]-yrange[0])*(B-T);
    ticks(...xrange).forEach(x=>{line(svg,sx(x),T,sx(x),B,C.grid);text(svg,sx(x),B+25,fmt(x),C.soft);});
    ticks(...yrange).forEach(y=>{line(svg,L,sy(y),R,sy(y),C.grid);text(svg,L-9,sy(y)+6,fmt(y),C.soft,'end');});
    line(svg,L,B,R,B,C.soft);line(svg,L,T,L,B,C.soft);text(svg,(L+R)/2,385,xlabel,C.ink);text(svg,L,25,ylabel,C.ink,'start');
    const id='intro-ml-clip-'+(global.__introMLClipCounter=(global.__introMLClipCounter||0)+1),defs=svgNode('defs'),clip=svgNode('clipPath',{id});
    clip.appendChild(svgNode('rect',{x:L,y:T,width:R-L,height:B-T}));defs.appendChild(clip);svg.appendChild(defs);
    const layer=svgNode('g',{'clip-path':'url(#'+id+')'});svg.appendChild(layer);return {svg,layer,L,R,T,B,sx,sy,xrange,yrange};
  }
  function curve(p,x,y,color,width=2.5,dashed=false) {
    const pairs=x.map((v,i)=>[v,y[i]]).sort((a,b)=>a[0]-b[0]);
    p.layer.appendChild(svgNode('polyline',{points:pairs.map(([a,b])=>p.sx(a)+','+p.sy(b)).join(' '),fill:'none',stroke:color,'stroke-width':width,'stroke-dasharray':dashed?'7 5':'none','stroke-linejoin':'round'}));
  }
  function point(p,x,y,color,kind='circle',size=4.5) {
    const a=p.sx(x),b=p.sy(y);
    if(kind==='diamond')p.layer.appendChild(svgNode('polygon',{points:`${a},${b-size} ${a+size},${b} ${a},${b+size} ${a-size},${b}`,fill:color,'fill-opacity':.8,stroke:C.bg,'stroke-width':.8}));
    else if(kind==='hollow')p.layer.appendChild(svgNode('circle',{cx:a,cy:b,r:size,fill:'none',stroke:color,'stroke-width':1.8}));
    else p.layer.appendChild(svgNode('circle',{cx:a,cy:b,r:size,fill:color,'fill-opacity':.8,stroke:C.bg,'stroke-width':.8}));
  }
  function points(p,xy,color,kind='circle') {xy.x.forEach((x,i)=>point(p,x,xy.y[i],color,kind,kind==='diamond'?4.4:4));}
  function signal(root,data) {
    if(!data||![data.x,data.truth,data.noise].every(finiteArray)||data.x.length!==data.truth.length||data.x.length!==data.noise.length)throw new Error('Signal requires equal-length x, truth and noise arrays');
    const stage=root.querySelector('[data-stage]');let sigma=3,showTruth=false;
    const ctrl=controls(stage);slider(ctrl,'Разброс шума σ','noise',sigma,0,8,.25,v=>{sigma=v;render();},' мин');
    checkbox(ctrl,'Показать заданную зависимость','truth',showTruth,v=>{showTruth=v;render();});
    const svg=chart(stage,'Одно расстояние — разные времена доставки','iml-single');
    const symbols=legend(stage,[['● Наблюдаемое время',C.blue],['— Заданная зависимость (по переключателю)',C.gold]]);
    symbols.setAttribute('aria-label','Обозначения на графике');
    stage.appendChild(node('p',{class:'iml-note'},'По горизонтали — расстояние доставки в километрах; по вертикали — время в минутах. При движении ползунка меняется только величина тех же случайных отклонений.'));
    const xr=range(data.x,.04),allY=data.truth.flatMap((v,i)=>[v,v+8*data.noise[i]]),yr=range(allY,.08);
    function render() {
      const y=data.truth.map((v,i)=>v+sigma*data.noise[i]);
      const p=frame(svg,'Синтетические времена доставки и заданная зависимость',xr,yr);
      if(showTruth)curve(p,data.x,data.truth,C.gold,3);
      points(p,{x:data.x,y},C.blue);
      output(root,`<b>Шум σ = ${fmt(sigma)} мин.</b> ${sigma===0?'Все наблюдения лежат на заданной зависимости.':'Наблюдаемое время отличается от заданной зависимости: к нему добавлен шум.'}<br>${showTruth?'Золотая линия известна нам, потому что мы сами создали эти данные.':'Пока видны только наблюдения. Включите линию, чтобы сравнить их с зависимостью, заданной в симуляции.'}<br>Остаточный разброс здесь относится к прогнозу по одному доступному признаку — расстоянию.`);
      Object.assign(root.dataset,{noise:String(sigma),truthVisible:String(showTruth),observed:JSON.stringify(y)});
    }render();
  }
  function mseBars(svg,model,revealed) {
    svg.replaceChildren();svg.setAttribute('viewBox','0 0 360 440');svg.setAttribute('role','img');svg.setAttribute('aria-label','По вертикали — выборка; по горизонтали — MSE в минутах в квадрате');
    svg.appendChild(svgNode('title',{},'MSE: средняя квадратичная ошибка, минуты в квадрате'));
    text(svg,24,36,'Выборка',C.ink,'start',19);text(svg,24,64,'Меньше MSE — лучше',C.soft,'start',16);
    const rows=[['Train',model.train_mse,C.blue,'Обучение'],['Validation',model.validation_mse,C.green,'Выбор модели'],['Test',revealed?model.test_mse:null,C.violet,'Финальная проверка']];
    const max=Math.max(1,...rows.map(r=>r[1]===null?0:r[1]));
    rows.forEach(([label,value,color,purpose],i)=>{
      const y=105+i*96;text(svg,24,y,label,color,'start',19);text(svg,336,y,value===null?'закрыт':fmt(value),value===null?C.soft:C.ink,'end',19);
      svg.appendChild(svgNode('rect',{x:24,y:y+13,width:312,height:18,rx:5,fill:'#25313e'}));
      if(value!==null)svg.appendChild(svgNode('rect',{x:24,y:y+13,width:Math.max(0,value/max*312),height:18,rx:5,fill:color,'fill-opacity':.8}));
      text(svg,24,y+54,purpose,C.soft,'start',16);
    });
    line(svg,24,377,336,377,C.soft);
    [0,.5,1].forEach(fraction=>{
      const x=24+312*fraction,value=max*fraction;
      line(svg,x,377,x,383,C.soft);
      text(svg,x,403,value>=1e5?value.toExponential(1):fmt(value),C.soft,fraction===0?'start':fraction===1?'end':'middle',15);
    });
    text(svg,180,431,'MSE, мин²',C.ink,'middle',18);
  }
  function complexity(root,data) {
    if(!data||!Array.isArray(data.cases)||!data.cases.length)throw new Error('Complexity requires precomputed cases');
    const lookup=new Map(data.cases.map(c=>[key(c.n,c.sigma,c.rep),c]));
    const ns=[...new Set(data.cases.map(c=>c.n))].sort((a,b)=>a-b),sigmas=[...new Set(data.cases.map(c=>c.sigma))].sort((a,b)=>a-b),reps=[...new Set(data.cases.map(c=>c.rep))].sort((a,b)=>a-b);
    let n=ns.includes(40)?40:ns[0],sigma=sigmas.includes(4)?4:sigmas[0],rep=reps.includes(0)?0:reps[0],degree=3,revealed=false,showTruth=false,showValidation=false;
    const usedReps=new Set(),stage=root.querySelector('[data-stage]');
    const ctrl=controls(stage),selection=[];
    const nSelect=dropdown(ctrl,'Объектов в train','n',ns,n,v=>{if(!revealed){n=v;render();}},v=>fmt(v)+' доставок');selection.push(nSelect);
    const sSelect=dropdown(ctrl,'Разброс шума σ','noise',sigmas,sigma,v=>{if(!revealed){sigma=v;render();}},v=>fmt(v)+' мин');selection.push(sSelect);
    const sampleButton=button(ctrl,'Другая выборка','sample',()=>{if(!revealed){advanceRep();render();}});selection.push(sampleButton);
    const degreeRow=controls(stage);degreeRow.setAttribute('role','group');degreeRow.setAttribute('aria-label','Степень полинома — гибкость кривой');
    degreeRow.appendChild(node('span',{class:'iml-note'},'Гибкость модели:'));
    const degreeButtons=[1,3,12].map(d=>button(degreeRow,({1:'Степень 1 · прямая',3:'Степень 3',12:'Степень 12'})[d],'degree-'+d,()=>{if(!revealed){degree=d;render();}}));selection.push(...degreeButtons);
    const visibility=controls(stage);
    checkbox(visibility,'Показать validation на графике','validation',showValidation,v=>{showValidation=v;render();});
    checkbox(visibility,'Показать заданную зависимость','truth',showTruth,v=>{showTruth=v;render();});
    const status=node('div',{class:'iml-status','data-state-notice':'','aria-live':'polite'});stage.appendChild(status);
    const layout=node('div',{class:'iml-layout'});stage.appendChild(layout);
    const svg=chart(layout,'Наблюдения и прогноз модели'),bars=chart(layout,'Ошибка на разных данных','iml-bars');
    legend(stage,[['● Train',C.blue],['○ Validation (по переключателю)',C.green],['◆ Test (после открытия)',C.violet],['— Модель',C.rose],['┄ Заданная зависимость',C.gold]]);
    const clipping=node('p',{class:'iml-note','data-clipping-note':''});stage.appendChild(clipping);
    const actions=controls(stage);
    const revealButton=button(actions,'Зафиксировать выбор и открыть test','reveal',()=>{if(!revealed){revealed=true;usedReps.add(rep);render();}},true);
    const resetButton=button(actions,'Начать новый независимый повтор','reset',()=>{
      const available=reps.filter(r=>!usedReps.has(r));if(!revealed||!available.length)return;
      rep=available[0];revealed=false;render();
    });
    stage.appendChild(node('p',{class:'iml-note'},'Модель обучена только на train. Ошибку validation можно использовать для выбора гибкости. После открытия test менять модель в этом повторе нельзя. Новые выборки — независимые учебные повторы одной и той же задачи.'));
    function advanceRep() {
      const available=reps.filter(r=>!usedReps.has(r));const index=available.indexOf(rep);rep=available[(index+1)%available.length];
    }
    function render() {
      const c=lookup.get(key(n,sigma,rep));if(!c)throw new Error('Missing combination of sample size, noise and repetition');
      const model=c.models.find(m=>m.degree===degree);if(!model)throw new Error('Missing polynomial degree');
      selection.forEach(e=>{e.disabled=revealed;});
      if(!revealed)sampleButton.disabled=reps.filter(r=>!usedReps.has(r)).length<2;
      nSelect.value=String(n);sSelect.value=String(sigma);
      degreeButtons.forEach((b,i)=>b.setAttribute('aria-pressed',String([1,3,12][i]===degree)));
      revealButton.disabled=revealed;resetButton.hidden=!revealed;resetButton.disabled=usedReps.size>=reps.length;
      resetButton.textContent=usedReps.size>=reps.length?'Все учебные повторы использованы':'Начать новый независимый повтор';
      status.setAttribute('data-locked',String(revealed));
      status.textContent=revealed?`Выбор зафиксирован: степень ${degree}, ${n} объектов, шум ${fmt(sigma)} мин. Test открыт только для этой модели. ${usedReps.size>=reps.length?'Все '+reps.length+' независимых повтора уже использованы.':'Для нового выбора перейдите к следующему независимому повтору.'}`:`Повтор ${reps.indexOf(rep)+1} из ${reps.length}. Выбирайте модель по train и validation. Test пока закрыт.`;
      // Hidden test observations never influence the axes used during model selection.
      const xr=range([...c.grid,...c.train.x,...c.validation.x],.025),yr=range([...c.truth,...c.train.y,...c.validation.y],.12);
      const p=frame(svg,`Прогноз полинома степени ${degree}, ${n} обучающих наблюдений`,xr,yr);
      if(showTruth)curve(p,c.grid,c.truth,C.gold,2.4,true);
      curve(p,c.grid,model.prediction,C.rose,2.8);
      if(showValidation)points(p,c.validation,C.green,'hollow');
      if(revealed)points(p,c.test,C.violet,'diamond');
      points(p,c.train,C.blue);
      const outside=model.prediction.some(v=>v<yr[0]||v>yr[1]);
      const hiddenTest=revealed&&c.test.y.some((v,i)=>v<yr[0]||v>yr[1]||c.test.x[i]<xr[0]||c.test.x[i]>xr[1]);
      clipping.hidden=!outside&&!hiddenTest;
      clipping.textContent=(outside?'Часть кривой модели выходит за границы графика. Шкала сохранена, чтобы наблюдения оставались видны. ':'')+(hiddenTest?'Некоторые тестовые точки за пределами шкалы. Все они учтены в MSE.':'');
      mseBars(bars,model,revealed);
      output(root,`<b>Степень ${degree}; train: ${n} доставок; шум: ${fmt(sigma)} мин.</b><br>MSE на train = ${fmt(model.train_mse)} мин²; на validation = ${fmt(model.validation_mse)} мин².${revealed?'<br><b>MSE на test = '+fmt(model.test_mse)+' мин².</b> Это проверка уже выбранной модели.':'<br>Сравните, как изменение гибкости влияет на обе видимые ошибки. Меньшая ошибка на train сама по себе не означает лучший прогноз новых наблюдений.'}<br>${showTruth?'Заданная зависимость — подсказка только для этой симуляции. На реальных данных её обычно не видно.':''}`);
      Object.assign(root.dataset,{n:String(n),noise:String(sigma),rep:String(rep),degree:String(degree),testRevealed:String(revealed),trainMse:String(model.train_mse),validationMse:String(model.validation_mse),truthVisible:String(showTruth),validationVisible:String(showValidation),usedReps:JSON.stringify([...usedReps])});
      if(revealed)root.dataset.testMse=String(model.test_mse);else delete root.dataset.testMse;
    }render();
  }
  function loss(root) {
    const stage=root.querySelector('[data-stage]'),actual=[10,20,30];let third=40;
    const ctrl=controls(stage);slider(ctrl,'Прогноз для доставки 3','prediction',third,20,60,1,v=>{third=v;render();},' мин');
    stage.appendChild(node('p',{class:'iml-note'},'Фактические времена трёх доставок — 10, 20 и 30 минут. Первые два прогноза фиксированы: 12 и 18 минут. Ползунок меняет только третий прогноз.'));
    const svg=chart(stage,'От фактического времени к прогнозу','iml-single');
    legend(stage,[['● Фактическое время y',C.blue],['◆ Прогноз ŷ',C.gold],['Стрелка: факт → прогноз',C.rose]]);
    const tableWrap=node('div',{class:'iml-table-wrap'});stage.appendChild(tableWrap);
    const cards=node('div',{class:'iml-metrics'});stage.appendChild(cards);
    function render() {
      const predicted=[12,18,third],s=losses(actual,predicted);
      const p=frame(svg,'Фактические времена и прогнозы трёх доставок',[.5,3.5],[0,65],'Номер доставки','Время, мин');
      actual.forEach((y,i)=>{
        const x=p.sx(i+1),a=p.sy(y),b=p.sy(predicted[i]),length=Math.abs(b-a),direction=Math.sign(b-a),head=Math.min(8,length*.4);
        line(p.layer,x,a,x,b,C.rose,2.5);
        if(length>1)p.layer.appendChild(svgNode('polygon',{points:`${x},${b} ${x-4},${b-direction*head} ${x+4},${b-direction*head}`,fill:C.rose}));
        point(p,i+1,y,C.blue,'circle',6);point(p,i+1,predicted[i],C.gold,'diamond',6);
      });
      tableWrap.replaceChildren();const table=node('table',{'aria-label':'Ошибки трёх прогнозов и их квадраты'}),head=node('tr');
      ['Доставка','Факт y, мин','Прогноз ŷ, мин','Ошибка y − ŷ, мин','Квадрат ошибки, мин²','Модуль ошибки, мин'].forEach(title=>head.appendChild(node('th',{scope:'col'},title)));table.appendChild(head);
      actual.forEach((y,i)=>{
        const tr=node('tr',{class:i===2?'iml-selected':''});[i+1,y,predicted[i],s.errors[i],s.squared[i],s.absolute[i]].forEach((v,j)=>tr.appendChild(node(j===0?'th':'td',j===0?{scope:'row'}:{},fmt(v))));table.appendChild(tr);
      });tableWrap.appendChild(table);
      cards.replaceChildren();
      [['MSE',s.mse,'мин²','Среднее квадратов ошибок'],['MAE',s.mae,'мин','Среднее модулей ошибок'],['RMSE',s.rmse,'мин','Корень из MSE']].forEach(([name,value,unit,description])=>{
        const card=node('div',{class:'iml-metric'});card.append(node('b',{},name),node('strong',{},fmt(value)+' '+unit),node('span',{},description));cards.appendChild(card);
      });
      output(root,`<b>Ошибка третьего прогноза: 30 − ${fmt(third)} = ${fmt(s.errors[2])} мин.</b><br>MSE = (4 + 4 + ${fmt(s.squared[2])}) / 3 = ${fmt(s.mse)} мин².<br>MAE = (2 + 2 + ${fmt(s.absolute[2])}) / 3 = ${fmt(s.mae)} мин.<br>RMSE — квадратный корень из MSE: ${fmt(s.rmse)} мин.<br>${third===30?'Третий прогноз точен, но общая ошибка не нулевая: первые два прогноза отличаются от факта на 2 минуты.':'Чем больше модуль ошибки третьего прогноза, тем больше его квадрат. Поэтому одна большая ошибка особенно заметна в MSE.'}`);
      Object.assign(root.dataset,{prediction:String(third),mse:String(s.mse),mae:String(s.mae),rmse:String(s.rmse),errors:JSON.stringify(s.errors)});
    }render();
  }
  function mount(root,kind,data) {
    if(!root||!root.querySelector('[data-stage]')||!root.querySelector('[data-readout]'))throw new Error('IntroML requires a stage and readout');
    root.querySelector('[data-stage]').replaceChildren();root.querySelector('[data-readout]').replaceChildren();
    ['noise','truthVisible','observed','n','rep','degree','testRevealed','trainMse','validationMse','validationVisible','usedReps','testMse','prediction','mse','mae','rmse','errors','introWidget'].forEach(name=>{delete root.dataset[name];});
    styles(root);const widgets={signal,complexity,loss};if(!widgets[kind])throw new Error('Unknown IntroML widget: '+kind);
    widgets[kind](root,data);root.dataset.introWidget=kind;
  }
  global.IntroML={mount,math:{losses,mean}};
})(typeof window!=='undefined'?window:globalThis);
