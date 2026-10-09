/* Standalone SVG simulations, embedded into 09_stat_hypotheses.ipynb. */
(function (global) {
  'use strict';
  const C = { blue:'#6ab0f3', green:'#5fd08a', gold:'#e0b25a', rose:'#e0757f', violet:'#bd9ce8', ink:'#e6e9ec', soft:'#a7b0ba', grid:'#293440' };
  const fmt = (x, d=2) => d ? (Number(x).toFixed(d).replace(/\.?0+$/, '') || '0') : String(Math.round(x));
  const mean = a => a.reduce((s,x)=>s+x,0)/a.length;
  function rng(seed) { return () => { seed|=0; seed=seed+0x6D2B79F5|0; let t=Math.imul(seed^seed>>>15,1|seed); t=t+Math.imul(t^t>>>7,61|t)^t; return ((t^t>>>14)>>>0)/4294967296; }; }
  function quantile(sorted,q) { const t=(sorted.length-1)*q,i=Math.floor(t); return sorted[i]+(sorted[Math.min(i+1,sorted.length-1)]-sorted[i])*(t-i); }
  function interval(values) { const sorted=[...values].sort((a,b)=>a-b); return [quantile(sorted,.025),quantile(sorted,.975)]; }
  function extreme(x,observed) { return Math.abs(x)>=Math.abs(observed)-100*Number.EPSILON*Math.max(1,Math.abs(observed)); }
  function permutationP(values,observed) { return (1+values.filter(x=>extreme(x,observed)).length)/(values.length+1); }
  function permutations(a,b,repeats,r) {
    const pooled=Float64Array.from([...a,...b]),work=new Float64Array(pooled.length),total=pooled.reduce((s,x)=>s+x,0),out=[];
    // A partial Fisher-Yates shuffle selects one uniformly random group A.
    for(let k=0;k<repeats;k++) {
      work.set(pooled); let sumA=0;
      for(let i=0;i<a.length;i++) {
        const j=i+Math.floor(r()*(pooled.length-i)),picked=work[j];
        work[j]=work[i]; work[i]=picked; sumA+=picked;
      }
      out.push((total-sumA)/b.length-sumA/a.length);
    }
    return out;
  }
  function bootstrap(a,b,repeats,r) {
    const out=[];
    for(let k=0;k<repeats;k++) {
      let sumA=0,sumB=0;
      for(let i=0;i<a.length;i++)sumA+=a[Math.floor(r()*a.length)];
      for(let i=0;i<b.length;i++)sumB+=b[Math.floor(r()*b.length)];
      out.push(sumB/b.length-sumA/a.length);
    }
    return out;
  }
  function deliveries(r,n) { return Array.from({length:n},()=>10-20*Math.log(Math.max(r(),1e-12))); }
  function nullStudies(start,count) {
    const values=[];
    for(let j=start;j<start+count;j++) {
      const r=rng(930000+3*j),a=deliveries(r,50),b=deliveries(r,50);
      values.push(permutationP(permutations(a,b,999,rng(1000000+j)),mean(b)-mean(a)));
    }
    return values;
  }
  function decisionResult(a,b) {
    const observed=mean(b)-mean(a),permuted=permutations(a,b,9999,rng(9102));
    return {observed,p:permutationP(permuted,observed),ci:interval(bootstrap(a,b,9999,rng(9104)))};
  }

  function el(tag,attrs={},content='') { const e=document.createElementNS('http://www.w3.org/2000/svg',tag); for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v)); if(content!=='')e.textContent=content; return e; }
  function text(svg,x,y,t,color=C.soft,anchor='middle',size=12) { svg.appendChild(el('text',{x,y,fill:color,'text-anchor':anchor,'font-family':'system-ui,sans-serif','font-size':size},t)); }
  function frame(svg,domain,yrange,xlabel,ylabel,title,yTicks=true) {
    svg.replaceChildren(); svg.setAttribute('viewBox','0 0 640 360'); svg.setAttribute('role','img'); svg.setAttribute('aria-label',`${title}. ${xlabel}; ${ylabel}`); svg.appendChild(el('title',{},title));
    const [lo,hi]=domain,[bottom,top]=yrange,L=65,R=615,T=62,B=299;
    const sx=x=>L+(x-lo)/(hi-lo)*(R-L),sy=y=>B-(y-bottom)/(top-bottom)*(B-T);
    text(svg,L,23,title,C.ink,'start',14); text(svg,L,43,ylabel,C.soft,'start',11);
    if(yTicks)for(let i=0;i<=4;i++) { const y=bottom+(top-bottom)*i/4; svg.appendChild(el('line',{x1:L,x2:R,y1:sy(y),y2:sy(y),stroke:C.grid})); text(svg,L-8,sy(y)+4,fmt(y,top>10?0:2),C.soft,'end',11); }
    for(let i=0;i<=5;i++) { const x=lo+(hi-lo)*i/5; svg.appendChild(el('line',{x1:sx(x),x2:sx(x),y1:T,y2:B,stroke:C.grid,'stroke-opacity':.5})); text(svg,sx(x),B+21,fmt(x),C.soft,'middle',11); }
    text(svg,(L+R)/2,346,xlabel,C.ink,'middle',12);
    return {svg,lo,hi,L,R,T,B,sx,sy};
  }
  function vline(p,x,label,color=C.gold,row=0) {
    p.svg.appendChild(el('line',{x1:p.sx(x),x2:p.sx(x),y1:p.T,y2:p.B,stroke:color,'stroke-dasharray':'5 4','stroke-width':2}));
    text(p.svg,Math.max(p.L+65,Math.min(p.R-65,p.sx(x))),p.T+15+row*19,label,color);
  }
  function shade(p,low,high,color=C.gold) { if(high>low)p.svg.appendChild(el('rect',{x:p.sx(low),y:p.T,width:p.sx(high)-p.sx(low),height:p.B-p.T,fill:color,'fill-opacity':.11})); }
  function bounds(a,pad=.13) { const lo=Math.min(...a),hi=Math.max(...a),width=Math.max(hi-lo,1); return [lo-pad*width,hi+pad*width]; }
  const chart=(root,key)=>root.querySelector(`[data-chart="${key}"]`);
  const output=(root,s)=>{root.querySelector('[data-readout]').innerHTML=s;};
  const control=(root,key)=>Number(root.querySelector(`[data-control="${key}"]`).value);
  function button(root,key,fn) { root.querySelector(`[data-action="${key}"]`).addEventListener('click',fn); }
  function busy(root,value) { root.dataset.busy=String(value); root.setAttribute('aria-busy',String(value)); root.querySelectorAll('button,select').forEach(e=>{e.disabled=value;}); }
  function schedule(root,fn) {
    busy(root,true);
    root.lesson9Ready=new Promise(resolve=>setTimeout(resolve,20)).then(fn).catch(error=>{
      output(root,'Не удалось завершить расчёт. Перезапустите ячейку интерактива.'); throw error;
    }).finally(()=>busy(root,false));
    return root.lesson9Ready;
  }

  function permutationChart(svg,values,observed) {
    const limit=values.reduce((m,x)=>Math.max(m,Math.abs(x)*1.04),Math.max(1,Math.abs(observed)*1.23));
    const m=42,lo=-limit,hi=limit,width=(hi-lo)/m,counts=Array(m).fill(0),tails=Array(m).fill(0);
    for(const x of values) { const i=Math.min(m-1,Math.max(0,Math.floor((x-lo)/width))); counts[i]++; if(extreme(x,observed))tails[i]++; }
    const p=frame(svg,[lo,hi],[0,Math.max(1,...counts)*1.2],'Разница средних B − A, мин','Число перестановок','Как выглядят различия после перемешивания');
    shade(p,lo,-Math.abs(observed)); shade(p,Math.abs(observed),hi);
    counts.forEach((count,i)=>{
      const x=p.sx(lo+i*width)+.5,w=p.sx(lo+(i+1)*width)-p.sx(lo+i*width)-1;
      p.svg.appendChild(el('rect',{x,y:p.sy(count),width:w,height:p.B-p.sy(count),fill:C.blue,'fill-opacity':.7}));
      if(tails[i])p.svg.appendChild(el('rect',{x,y:p.sy(tails[i]),width:w,height:p.B-p.sy(tails[i]),fill:C.gold}));
    });
    vline(p,observed,'Наблюдаемая: '+fmt(observed),C.violet);
    if(Math.abs(observed)>1e-12)vline(p,-observed,'Так же далеко от 0',C.gold,1);
    if(!values.length)text(svg,(p.L+p.R)/2,192,'Нажмите «Одна перестановка»',C.ink,'middle',14);
    else for(const x of values.filter(x=>extreme(x,observed)))p.svg.appendChild(el('line',{x1:p.sx(x),x2:p.sx(x),y1:p.B-5,y2:p.B-13,stroke:C.gold,'stroke-width':2}));
  }
  function permutation(root,data) {
    const a=data.a,b=data.b,observed=mean(b)-mean(a); let values=[],r=rng(9201);
    function render() {
      permutationChart(chart(root,'permutations'),values,observed);
      const k=values.filter(x=>extreme(x,observed)).length;
      output(root,`<b>Наблюдаемая разница: ${fmt(observed)} мин. Перестановок: ${values.length}.</b><br>`+
        (values.length?`Не менее далёких от нуля: ${k}. Оценка p-value = (${k} + 1) / (${values.length} + 1) = <b>${fmt(permutationP(values,observed),4)}</b>.<br>`:'Пока перестановок нет, p-value не оцениваем.<br>')+
        'Оранжевые области — различия не менее сильные, чем наблюдаемое, в обе стороны. В каждой перестановке меняются только метки A и B: времена и размеры групп остаются прежними.'+
        (values.length&&values.length<1000?'<br>Одного или нескольких повторений недостаточно для устойчивой оценки p-value.':''));
      Object.assign(root.dataset,{repeats:values.length,extreme:k,observed,p:values.length?permutationP(values,observed):''});
    }
    function add(count) { schedule(root,()=>{values.push(...permutations(a,b,count,r)); render();}); }
    button(root,'one',()=>add(1)); button(root,'many',()=>add(999));
    button(root,'reset',()=>{values=[];r=rng(9201);render();}); render();
  }
  function nullChart(svg,values) {
    const p=frame(svg,[0,Math.max(100,values.length)+1],[0,1],'Номер независимого исследования','Полученный p-value','Что происходит, когда различий в действительности нет');
    p.svg.appendChild(el('rect',{x:p.L,y:p.sy(.05),width:p.R-p.L,height:p.B-p.sy(.05),fill:C.gold,'fill-opacity':.14}));
    p.svg.appendChild(el('line',{x1:p.L,x2:p.R,y1:p.sy(.05),y2:p.sy(.05),stroke:C.gold,'stroke-dasharray':'5 4','stroke-width':2}));
    text(svg,p.R-5,p.sy(.05)-9,'α = 0,05',C.gold,'end',12);
    values.forEach((v,i)=>p.svg.appendChild(el('circle',{cx:p.sx(i+1),cy:p.sy(v),r:values.length>500?2:3,fill:v<=.05?C.gold:C.blue,'fill-opacity':.83})));
  }
  function nullWidget(root,data) {
    const initial=[...data.initial]; let values=[...initial];
    function render() {
      nullChart(chart(root,'null'),values); const rejected=values.filter(x=>x<=.05).length;
      output(root,`<b>Верная H₀ отклонена в ${rejected} из ${values.length} исследований (${fmt(100*rejected/values.length,1)}%).</b><br>`+
        'Здесь способы A и B имеют одинаковое распределение времени. Каждая точка — новый набор из 50 доставок A и 50 доставок B и отдельный тест с 999 перестановками.<br>'+
        'Оранжевые точки — ошибки первого рода при α = 0,05. Их доля в конечной серии не обязана равняться ровно 5%.');
      Object.assign(root.dataset,{experiments:values.length,rejected,rate:rejected/values.length});
    }
    button(root,'many',()=>schedule(root,()=>{values.push(...nullStudies(values.length,100));render();}));
    button(root,'reset',()=>{values=[...initial];render();}); render();
  }
  function intervalChart(svg,result) {
    const {observed,ci}=result,p=frame(svg,bounds([...ci,observed,-5,0],.2),[0,1],'Разница средних B − A, мин','Точка — оценка; отрезок — 95%-й бутстрап-интервал','Насколько большой может быть разница?',false);
    shade(p,p.lo,-5,C.green); vline(p,-5,'Выигрыш 5 минут',C.gold); vline(p,0,'Нет разницы',C.soft,1);
    const y=p.sy(.4); p.svg.appendChild(el('line',{x1:p.sx(ci[0]),x2:p.sx(ci[1]),y1:y,y2:y,stroke:C.green,'stroke-width':5}));
    for(const x of ci)p.svg.appendChild(el('line',{x1:p.sx(x),x2:p.sx(x),y1:y-9,y2:y+9,stroke:C.green,'stroke-width':2}));
    p.svg.appendChild(el('circle',{cx:p.sx(observed),cy:y,r:6,fill:C.green,stroke:'#0e1319','stroke-width':2}));
    text(svg,p.sx(observed),y-25,'Оценка: '+fmt(observed),C.ink);
    text(svg,p.sx(ci[0]),y+29,fmt(ci[0]),C.green); text(svg,p.sx(ci[1]),y+29,fmt(ci[1]),C.green);
  }
  function decision(root,data) {
    const cache=new Map();
    function render() {
      const n=control(root,'n'),gain=control(root,'gain'),key=`${n}:${gain}`;
      output(root,'Считаем 9999 перестановок и 9999 бутстрап-повторений…');
      return schedule(root,()=>{
        if(!cache.has(key))cache.set(key,decisionResult(data.a.slice(0,n),data.b.slice(0,n).map(x=>x-gain)));
        const result=cache.get(key),{observed,p,ci}=result; intervalChart(chart(root,'interval'),result);
        const significance=p<=.05?'Различие статистически значимо: H₀ отклоняем.':'H₀ не отклоняем: статистически значимого различия не обнаружили.';
        const zero=ci[1]<0?'Весь интервал ниже 0: он указывает на ускорение.':ci[0]>0?'Весь интервал выше 0: он указывает на замедление.':'Интервал включает 0: он допускает отсутствие разницы.';
        const business=ci[1]<=-5?'Весь интервал не выше −5 мин: данные поддерживают выигрыш не менее 5 минут.':ci[0]>-5?'Весь интервал выше −5 мин: он не поддерживает выигрыш в 5 минут.':'Интервал пересекает −5 мин: точности пока не хватает для вывода о выигрыше не менее 5 минут.';
        output(root,`<b>По ${n} доставок в группе. Разница: ${fmt(observed)} мин; p-value ≈ ${fmt(p,4)}.</b><br>`+
          `${significance}<br>95%-й интервал: [${fmt(ci[0])}; ${fmt(ci[1])}] мин. ${zero}<br>${business}<br>`+
          `В симуляции истинный выигрыш известен: ${gain} мин. В реальном исследовании мы его не знаем. Изменение размера выборки берёт больше или меньше наблюдений из того же набора.`);
        Object.assign(root.dataset,{n,gain,observed,p,ciLow:ci[0],ciHigh:ci[1]});
      });
    }
    root.querySelectorAll('[data-control]').forEach(e=>e.addEventListener('change',render)); render();
  }
  const widgets={permutation,null:nullWidget,decision};
  global.InferenceLesson9={
    mount:(root,kind,data)=>{if(!root||!widgets[kind])throw new Error('Unknown widget: '+kind);widgets[kind](root,data);},
    math:{rng,mean,quantile,interval,extreme,permutationP,permutations,bootstrap,deliveries,nullStudies,decisionResult}
  };
})(typeof window!=='undefined'?window:globalThis);
