/* Standalone SVG simulations, embedded into 08_stat_ci_bootstrap.ipynb. */
(function (global) {
  'use strict';
  const C = { blue:'#6ab0f3', green:'#5fd08a', gold:'#e0b25a', rose:'#e0757f', ink:'#e6e9ec', soft:'#a7b0ba', grid:'#293440' };
  const fmt = (x, d=2) => (d ? Number(x).toFixed(d).replace(/\.?0+$/, '') : String(Math.round(x))) || '0';
  const mean = a => a.reduce((s,x)=>s+x,0)/a.length;
  const sd = (a, ddof=0) => { const m=mean(a); return Math.sqrt(a.reduce((s,x)=>s+(x-m)**2,0)/(a.length-ddof)); };
  const pdf = x => Math.exp(-x*x/2)/Math.sqrt(2*Math.PI);
  function rng(seed) { return () => { seed|=0; seed=seed+0x6D2B79F5|0; let t=Math.imul(seed^seed>>>15,1|seed); t=t+Math.imul(t^t>>>7,61|t)^t; return ((t^t>>>14)>>>0)/4294967296; }; }
  function normal(r) { return Math.sqrt(-2*Math.log(Math.max(r(),1e-12)))*Math.cos(2*Math.PI*r()); }
  function draw(r, kind='skew') {
    if (kind==='normal') return normal(r);
    if (kind==='uniform') return Math.sqrt(3)*(2*r()-1);
    if (kind==='rare') { const y=r()<.01 ? 10+normal(r) : normal(r); return (y-.1)/Math.sqrt(1.99); }
    return -Math.log(Math.max(r(),1e-12))-1;
  }
  const sample = (r,n,kind='skew',mu=30,sigma=20) => Array.from({length:n},()=>mu+sigma*draw(r,kind));
  function batch(r,n,B,kind='skew',mu=30,sigma=20) {
    const means=[], spreads=[];
    for(let b=0;b<B;b++){ const a=sample(r,n,kind,mu,sigma); means.push(mean(a)); spreads.push(n>1?sd(a,1):NaN); }
    return {means,spreads};
  }
  function el(tag, attrs={}, content='') { const e=document.createElementNS('http://www.w3.org/2000/svg',tag); for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v)); if(content!=='')e.textContent=content; return e; }
  function text(svg,x,y,t,color=C.soft,anchor='middle',size=12){svg.appendChild(el('text',{x,y,fill:color,'text-anchor':anchor,'font-family':'system-ui,sans-serif','font-size':size},t));}
  function frame(svg,xrange,yrange,xlabel,ylabel,title,showYTicks=true,xTicks=null,yTicks=null){
    svg.replaceChildren();svg.setAttribute('viewBox','0 0 640 360');svg.setAttribute('role','img');svg.setAttribute('aria-label',`${title}. ${xlabel}; ${ylabel}`);
    svg.appendChild(el('title',{},title));
    const [lo,hi]=xrange,[bottom,top]=yrange,L=68,R=614,T=54,B=301;
    const sx=x=>L+(x-lo)/(hi-lo)*(R-L),sy=y=>B-(y-bottom)/(top-bottom)*(B-T);
    text(svg,L,22,title,C.ink,'start',14);text(svg,L,42,ylabel,C.soft,'start',11);
    if(showYTicks)for(const y of (yTicks||Array.from({length:5},(_,i)=>bottom+(top-bottom)*i/4))){svg.appendChild(el('line',{x1:L,x2:R,y1:sy(y),y2:sy(y),stroke:C.grid}));text(svg,L-8,sy(y)+4,fmt(y,3),C.soft,'end',11);}
    for(const x of (xTicks||Array.from({length:6},(_,i)=>lo+(hi-lo)*i/5))){svg.appendChild(el('line',{x1:sx(x),x2:sx(x),y1:T,y2:B,stroke:C.grid,'stroke-opacity':.5}));text(svg,sx(x),B+19,fmt(x),C.soft,'middle',11);}
    text(svg,(L+R)/2,345,xlabel,C.ink,'middle',12);return {svg,lo,hi,bottom,top,L,R,T,B,sx,sy};
  }
  function line(p,coords,color=C.blue,width=2){p.svg.appendChild(el('path',{d:coords.map(([x,y],i)=>`${i?'L':'M'} ${p.sx(x)} ${p.sy(y)}`).join(' '),fill:'none',stroke:color,'stroke-width':width}));}
  function vline(p,x,label,color=C.gold,row=0){if(x<p.lo||x>p.hi)return;p.svg.appendChild(el('line',{x1:p.sx(x),x2:p.sx(x),y1:p.T,y2:p.B,stroke:color,'stroke-dasharray':'5 4','stroke-width':2}));text(p.svg,Math.max(p.L+55,Math.min(p.R-55,p.sx(x))),p.T+15+row*18,label,color);}
  function hline(p,y,color=C.green){line(p,[[p.lo,y],[p.hi,y]],color);}
  function dot(p,x,y,color=C.blue,r=3){p.svg.appendChild(el('circle',{cx:p.sx(x),cy:p.sy(y),r,fill:color}));}
  function bounds(a,pad=.08){const lo=Math.min(...a),hi=Math.max(...a),span=Math.max(hi-lo,1);return[lo-pad*span,hi+pad*span];}
  function hist(svg,data,domain,xlabel,title,color=C.blue,normalCurve=null){
    const [lo,hi]=domain,m=32,w=(hi-lo)/m,counts=Array(m).fill(0);let outside=0;
    for(const x of data){if(x<lo||x>hi){outside++;continue;} counts[Math.min(m-1,Math.floor((x-lo)/w))]++;}
    const heights=counts.map(c=>c/(data.length*w));
    const ymax=Math.max(...heights,normalCurve?pdf(0)/normalCurve.sd:0,1e-6)*1.2;
    const p=frame(svg,domain,[0,ymax],xlabel,'Плотность (1 / единица горизонтальной оси)',title);
    counts.forEach((c,i)=>p.svg.appendChild(el('rect',{x:p.sx(lo+i*w)+.3,y:p.sy(heights[i]),width:Math.max(0,p.sx(lo+(i+1)*w)-p.sx(lo+i*w)-.6),height:p.B-p.sy(heights[i]),fill:color,'fill-opacity':.6})));
    if(normalCurve)line(p,Array.from({length:301},(_,i)=>{const x=lo+(hi-lo)*i/300;return[x,pdf((x-normalCurve.mu)/normalCurve.sd)/normalCurve.sd];}),C.gold,2.5);
    if(outside)text(svg,p.R,p.T+14,`За окном: ${outside} из ${data.length}`,C.rose,'end',11);
    return p;
  }
  const value=(root,k)=>root.querySelector(`[data-control="${k}"]`).value;
  const num=(root,k)=>Number(value(root,k));
  const chart=(root,k)=>root.querySelector(`[data-chart="${k}"]`);
  const output=(root,s)=>{root.querySelector('[data-readout]').innerHTML=s;};
  function sync(root){root.querySelectorAll('input[type=range][data-control]').forEach(e=>{const o=root.querySelector(`[data-value="${e.dataset.control}"]`);if(o)o.textContent=fmt(e.value);});}
  function bind(root,render){root.querySelectorAll('[data-control]').forEach(e=>e.addEventListener('input',()=>{sync(root);render();}));sync(root);render();}
  function button(root,k,fn){root.querySelector(`[data-action="${k}"]`).addEventListener('click',fn);}

  // Acklam's inverse-normal approximation; confidence controls use only 0.8..0.99.
  function ppf(p) {
    if (!(p > 0 && p < 1)) throw new Error('Probability must be between 0 and 1');
    const a=[-39.6968302866538,220.946098424521,-275.928510446969,138.357751867269,-30.6647980661472,2.50662827745924];
    const b=[-54.4760987982241,161.585836858041,-155.698979859887,66.8013118877197,-13.2806815528857];
    const c=[-.00778489400243029,-.322396458041136,-2.40075827716184,-2.54973253934373,4.37466414146497,2.93816398269878];
    const d=[.00778469570904146,.32246712907004,2.445134137143,3.75440866190742];
    if(p<.02425){const q=Math.sqrt(-2*Math.log(p));return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);}
    if(p>1-.02425)return -ppf(1-p);
    const q=p-.5,r=q*q;return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q/(((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1);
  }
  function quantile(a,q){const s=[...a].sort((x,y)=>x-y),t=(s.length-1)*q,i=Math.floor(t);return s[i]+(s[Math.min(i+1,s.length-1)]-s[i])*(t-i);}
  const statistic=(a,kind='mean')=>kind==='median'?quantile(a,.5):mean(a);
  function resample(r,a){return Array.from({length:a.length},()=>a[Math.floor(r()*a.length)]);}
  function boot(r,a,B,kind='mean'){
    const out=[];
    for(let b=0;b<B;b++){
      if(kind==='mean'){let total=0;for(let i=0;i<a.length;i++)total+=a[Math.floor(r()*a.length)];out.push(total/a.length);}
      else out.push(statistic(resample(r,a),kind));
    }
    return out;
  }
  function interval(a,level=.95){const tail=(1-level)/2;return [quantile(a,tail),quantile(a,1-tail)];}
  const covers=(ci,mu)=>ci[0]<=mu && mu<=ci[1];
  function bandRect(p,low,high,color=C.green){
    const left=Math.max(p.lo,low),right=Math.min(p.hi,high);
    if(right>left)p.svg.appendChild(el('rect',{x:p.sx(left),y:p.T,width:p.sx(right)-p.sx(left),height:p.B-p.T,fill:color,'fill-opacity':.12}));
  }
  function area(p,mu,se,lo,hi){
    const pts=[[lo,0],...Array.from({length:151},(_,i)=>{const x=lo+(hi-lo)*i/150;return[x,pdf((x-mu)/se)/se];}),[hi,0]];
    p.svg.appendChild(el('path',{d:pts.map(([x,y],i)=>`${i?'L':'M'} ${p.sx(x)} ${p.sy(y)}`).join(' ')+' Z',fill:C.gold,'fill-opacity':.25}));
  }
  function segment(p,lo,hi,y,color=C.green,point=null){
    line(p,[[lo,y],[hi,y]],color,5);
    for(const x of [lo,hi])p.svg.appendChild(el('line',{x1:p.sx(x),x2:p.sx(x),y1:p.sy(y)-7,y2:p.sy(y)+7,stroke:color,'stroke-width':2}));
    if(point!==null){dot(p,point,y,'#0e1319',6);dot(p,point,y,color,4);}
  }
  function forest(svg,means,intervals,truth,title,domain=null){
    const k=Math.min(means.length,40),shown=intervals.slice(0,k);
    const p=frame(svg,domain||bounds([truth,...shown.flat()]),[0,k+5],'Значение среднего','Номер исследования (первые '+k+')',title,true,null,[1,10,20,30,40].filter(x=>x<=k));
    for(let i=0;i<k;i++){
      const ci=shown[i],color=covers(ci,truth)?C.green:C.rose,y=i+1;
      line(p,[[ci[0],y],[ci[1],y]],color,2);dot(p,means[i],y,color,2.5);
    }
    vline(p,truth,'Истинное среднее',C.gold);
    return p;
  }
  function singleInterval(svg,estimate,ci,truth,title,domain=null){
    const p=frame(svg,domain||bounds([estimate,...ci,...(truth===null?[]:[truth])],.25),[0,1],'Время, мин','Точка — оценка; отрезок — интервал',title,false);
    const color=truth!==null&&!covers(ci,truth)?C.rose:C.green;
    segment(p,ci[0],ci[1],.45,color,estimate);
    text(svg,p.sx(ci[0]),p.sy(.45)+27,fmt(ci[0]),color);
    text(svg,p.sx(ci[1]),p.sy(.45)+27,fmt(ci[1]),color);
    text(svg,p.sx(estimate),p.sy(.45)-22,'Оценка '+fmt(estimate),color);
    if(truth!==null)vline(p,truth,'Истинное: '+fmt(truth),C.gold);
    return p;
  }
  function sampling(root){
    let seed=101,history=[],last=[];
    function add(B){const r=rng(seed++),n=num(root,'n');for(let i=0;i<B;i++){last=sample(r,n);history.push(mean(last));}history=history.slice(-3000);render();}
    function render(){
      const p=hist(chart(root,'data'),last,bounds(last),'Время отдельной доставки, мин','Одна выборка доставок');
      vline(p,30,'Истинное среднее: 30',C.gold);vline(p,mean(last),'Среднее выборки: '+fmt(mean(last)),C.green,1);
      const q=hist(chart(root,'means'),history,bounds([20,40,...history]),'Среднее целой выборки, мин','Ответы по новым выборкам',C.green);
      vline(q,30,'Истинное среднее: 30',C.gold);
      output(root,`<b>В выборке ${last.length} доставок; среднее ${fmt(mean(last))} мин. Получено ${history.length} выборок.</b><br>Слева одно число — отдельная доставка; справа одно число — среднее целой выборки. Все выборки получаем заново из одного и того же генератора. Истинное среднее остаётся 30 минут.`);
      Object.assign(root.dataset,{n:last.length,B:history.length,estimate:mean(last)});
    }
    button(root,'one',()=>add(1));button(root,'many',()=>add(200));bind(root,()=>{history=[];add(1);});
  }
  function samplingBand(root){
    let seed=201;
    function render(){
      const n=num(root,'n'),level=num(root,'level'),se=20/Math.sqrt(n),z=ppf((1+level)/2),h=z*se;
      const means=batch(rng(seed),n,3000).means,domain=bounds([30-4*se,30+4*se,...means]);
      const p=hist(chart(root,'band'),means,domain,'Среднее выборки, мин','Где оказываются выборочные средние',C.blue,{mu:30,sd:se});
      area(p,30,se,30-h,30+h);vline(p,30,'μ = 30',C.gold);
      vline(p,30-h,fmt(30-h),C.green,1);vline(p,30+h,fmt(30+h),C.green,1);
      const hit=means.filter(x=>Math.abs(x-30)<=h).length;
      output(root,`<b>Границы: ${fmt(30-h)}–${fmt(30+h)} мин. SE = ${fmt(se)} мин.</b><br>Золотая кривая — нормальное приближение; под ней закрашено ${fmt(level*100)}%. По 3000 настоящим выборкам из генератора внутрь попало ${fmt(100*hit/3000)}% средних.<br>Для асимметричных доставок это приближение. При малом n форма гистограммы может заметно отличаться от кривой. Квантиль стандартной нормали: ${fmt(z,3)}.`);
      Object.assign(root.dataset,{n,level,se,h,coverage:hit/3000});
    }
    button(root,'new',()=>{seed++;render();});bind(root,render);
  }
  function inversion(root){
    let seed=301;
    function render(){
      const n=num(root,'n'),level=num(root,'level'),x=num(root,'estimate'),h=ppf((1+level)/2)*20/Math.sqrt(n),hit=Math.abs(x-30)<=h;
      const domain=bounds([30-h,30+h,x-h,x+h],.14),color=hit?C.green:C.rose;
      const p=frame(chart(root,'fixed'),domain,[0,1],'Среднее, мин','Фиксированный отрезок вокруг μ','1. Где может оказаться среднее выборки?',false);
      segment(p,30-h,30+h,.45,C.gold,30);dot(p,x,.45,color,7);
      text(p.svg,p.sx(30),p.sy(.45)-35,'μ = 30',C.gold);
      text(p.svg,p.sx(x),p.sy(.45)+34,'Среднее выборки: '+fmt(x),color);
      const q=frame(chart(root,'moving'),domain,[0,1],'Среднее, мин','Случайный отрезок вокруг среднего выборки','2. Накрыл ли интервал истинное среднее?',false);
      segment(q,x-h,x+h,.45,color,x);vline(q,30,'μ = 30',C.gold);
      text(q.svg,q.sx(x),q.sy(.45)+34,'Среднее выборки: '+fmt(x),color);
      output(root,`<b>${hit?'Попадание в обоих случаях':'Промах в обоих случаях'}.</b> Расстояние от выборочного среднего до 30: ${fmt(Math.abs(x-30))} мин; половина ширины h = ${fmt(h)} мин.<br>Слева точка ${fmt(x)} ${hit?'внутри':'вне'} фиксированного отрезка. Справа число 30 ${hit?'внутри':'вне'} интервала [${fmt(x-h)}; ${fmt(x+h)}].<br>Оси одинаковы. Двигайте среднее выборки: граница попадания меняется одновременно на двух графиках. На первом графике случайна точка, на втором — границы интервала.`);
      Object.assign(root.dataset,{n,level,estimate:x,h,fixedHit:hit,intervalHit:covers([x-h,x+h],30)});
    }
    button(root,'new',()=>{
      const control=root.querySelector('[data-control="estimate"]'),x=mean(sample(rng(seed++),num(root,'n')));
      control.min=Math.min(+control.min,Math.floor(x));control.max=Math.max(+control.max,Math.ceil(x));control.value=x.toFixed(1);sync(root);render();
    });bind(root,render);
  }
  function coverage(root){
    let seed=401;
    function render(){
      const n=num(root,'n'),M=num(root,'M'),level=num(root,'level'),shape=value(root,'shape'),h=ppf((1+level)/2)*20/Math.sqrt(n);
      const means=batch(rng(seed),n,M,shape).means,cis=means.map(x=>[x-h,x+h]),hit=cis.filter(ci=>covers(ci,30)).length;
      forest(chart(root,'forest'),means,cis,30,'Каждая строка — новое исследование');
      output(root,`<b>Накрыли истинное среднее: ${hit} из ${M} (${fmt(100*hit/M)}%). Заданный уровень: ${fmt(100*level)}%.</b><br>На графике первые ${Math.min(40,M)} исследований, счётчик учитывает все ${M}. Зелёный отрезок накрыл 30, розовый — не накрыл; точка — среднее соответствующей выборки. Ширина каждого интервала ${fmt(2*h)}.<br>${shape==='normal'?'Для независимых нормальных наблюдений с известной σ метод имеет заданное покрытие. Частота в конечной серии всё равно колеблется. Нормальная модель здесь — условный показатель, не реальные времена доставок.':'Доставки асимметричны: используем ЦПТ и проверяем приближение. Малое n и конечное число исследований дают отличия от заданного уровня.'}<br>Изменение уровня доверия сохраняет те же выборки: виден эффект одной лишь ширины интервалов.`);
      Object.assign(root.dataset,{n,M,level,coverage:hit/M,width:2*h,shape});
    }
    button(root,'new',()=>{seed++;render();});bind(root,render);
  }
  const palette=['#6ab0f3','#5fd08a','#e0b25a','#e0757f','#bd9ce8','#73d1d1','#c8b365','#df9dc7','#89ad7a','#dcaa80','#8bace0','#baaa92'];
  function cards(svg,indices,data,counts,title){
    svg.replaceChildren();svg.setAttribute('viewBox','0 0 640 360');svg.setAttribute('role','img');svg.setAttribute('aria-label',title);svg.appendChild(el('title',{},title));
    text(svg,24,26,title,C.ink,'start',15);
    indices.forEach((idx,i)=>{
      const x=22+(i%4)*154,y=48+Math.floor(i/4)*96,col=palette[idx%palette.length];
      svg.appendChild(el('rect',{x,y,width:140,height:82,rx:9,fill:col,'fill-opacity':.1,stroke:col,'stroke-opacity':.7}));
      text(svg,x+12,y+20,'№ '+(idx+1),col,'start',12);
      text(svg,x+70,y+45,fmt(data[idx],1)+' мин',C.ink,'middle',18);
      text(svg,x+70,y+67,counts?'Выбран '+counts[idx]+' раз':'Позиция '+(i+1),C.soft,'middle',11);
    });
  }
  function resampling(root){
    let seed=501,data=sample(rng(seed),12),r=rng(701),history=[],last=[];
    function add(B){
      const replace=value(root,'replace')==='yes';
      for(let b=0;b<B;b++){
        last=Array.from({length:12},(_,i)=>i);
        if(replace)last=last.map(()=>Math.floor(r()*12));
        else for(let i=11;i>0;i--){const j=Math.floor(r()*(i+1));[last[i],last[j]]=[last[j],last[i]];}
        history.push(mean(last.map(i=>data[i])));
      }
      history=history.slice(-5000);render();
    }
    function render(){
      const counts=Array(12).fill(0);last.forEach(i=>counts[i]++);
      cards(chart(root,'original'),Array.from({length:12},(_,i)=>i),data,counts,'Исходные 12 наблюдений');
      cards(chart(root,'resample'),last,data,null,'Последняя повторная выборка: 12 записей');
      const p=hist(chart(root,'bootmeans'),history,bounds([mean(data)-8,mean(data)+8,...history]),'Среднее повторной выборки, мин','Средние из одной исходной выборки',C.green);
      vline(p,mean(data),'Исходное среднее: '+fmt(mean(data)),C.gold);
      output(root,`<b>Повторений: ${history.length}. Разных исходных записей в последней выборке: ${new Set(last).size} из 12.</b><br>Исходное среднее: ${fmt(mean(data))}; последнее повторное: ${fmt(mean(last.map(i=>data[i])))} мин.<br>${value(root,'replace')==='yes'?'Одинаковые номера и цвета обозначают одну исходную запись. Некоторые записи повторяются; размер каждой выборки остаётся 12. Это обычный бутстрап.':'Без возвращения мы взяли все 12 записей в другом порядке. Среднее осталось прежним. Это сравнение показывает, зачем бутстрапу возвращение.'}<br>Новые реальные наблюдения здесь не появляются.`);
      Object.assign(root.dataset,{B:history.length,n:12,unique:new Set(last).size,spread:history.length>1?sd(history,1):0,estimate:mean(data)});
    }
    button(root,'one',()=>add(1));button(root,'many',()=>add(200));
    button(root,'source',()=>{data=sample(rng(++seed),12);history=[];r=rng(seed+200);add(1);});
    bind(root,()=>{history=[];r=rng(seed+200);add(1);});
  }
  function bootstrap(root){
    let seed=601,bootSeed=801;
    function render(){
      const n=num(root,'n'),B=num(root,'B'),kind=value(root,'stat'),level=num(root,'level'),show=value(root,'truth')==='show';
      const data=sample(rng(seed),n),estimate=statistic(data,kind),truth=kind==='mean'?30:10+20*Math.log(2);
      const reps=boot(rng(bootSeed),data,B,kind),ci=interval(reps,level),se=sd(reps,1),name=kind==='mean'?'Среднее':'Медиана';
      const p=hist(chart(root,'data'),data,bounds(data),'Время отдельной доставки, мин','Исходная выборка: '+n+' доставок');
      vline(p,estimate,name+' выборки: '+fmt(estimate),C.green);
      const q=hist(chart(root,'distribution'),reps,bounds([...reps,estimate,...(show?[truth]:[])]),name+' повторной выборки, мин','Бутстрап-распределение: '+B+' повторений',C.green);
      bandRect(q,...ci);vline(q,estimate,'Исходная оценка',C.green);
      if(show)vline(q,truth,'Истинное значение',C.gold,1);
      singleInterval(chart(root,'interval'),estimate,ci,show?truth:null,'Интервал по квантилям бутстрап-распределения');
      output(root,`<b>${name}: ${fmt(estimate)} мин. Интервал: [${fmt(ci[0])}; ${fmt(ci[1])}] мин. Бутстрап-SE: ${fmt(se)} мин.</b><br>n = ${n} исходных наблюдений; B = ${B} повторных выборок. Зелёная полоса на гистограмме — центральные ${fmt(level*100)}% бутстрап-значений, отрезок внизу — их границы на исходной шкале.<br>${show?`Для проверки открыто истинное значение: ${fmt(truth)} мин. Этот интервал его ${covers(ci,truth)?'накрыл':'не накрыл'}.`:'Истинное значение скрыто: при расчёте интервала мы его не использовали.'}<br>Кнопка «Повторить бутстрап» сохраняет исходные данные; кнопка «Новая исходная выборка» собирает новые доставки. Увеличение B уточняет вычисление, но не увеличивает n. ${kind==='median'?'Для медианы не используем формулу SE среднего.':'Для среднего оценка s / √n по этой выборке: '+fmt(sd(data,1)/Math.sqrt(n))+' мин.'}`);
      Object.assign(root.dataset,{n,B,estimate,truth,lower:ci[0],upper:ci[1],se,analyticSE:sd(data,1)/Math.sqrt(n),kind});
    }
    button(root,'source',()=>{seed++;render();});button(root,'repeat',()=>{bootSeed++;render();});bind(root,render);
  }
  function bootcoverage(root){
    let seed=901;
    function render(){
      const n=num(root,'n'),M=num(root,'M'),B=500,r=rng(seed),rboot=rng(seed+10000),means=[],cis=[],known=[],h=ppf(.975)*20/Math.sqrt(n);
      for(let i=0;i<M;i++){const data=sample(r,n),m=mean(data);means.push(m);cis.push(interval(boot(rboot,data,B)));known.push([m-h,m+h]);}
      const domain=bounds([30,...cis.slice(0,40).flat(),...known.slice(0,40).flat()]);
      forest(chart(root,'known'),means,known,30,'Нормальный интервал: σ известна',domain);
      forest(chart(root,'bootstrap'),means,cis,30,'Бутстрап: интервал по квантилям',domain);
      const hit=cis.filter(ci=>covers(ci,30)).length,hitKnown=known.filter(ci=>covers(ci,30)).length;
      output(root,`<b>Из ${M} новых исследований: формула накрыла 30 в ${hitKnown} (${fmt(100*hitKnown/M)}%); бутстрап — в ${hit} (${fmt(100*hit/M)}%).</b><br>Обе панели используют одни и те же исходные выборки. На каждой показаны первые ${Math.min(40,M)} исследований. Внутри каждого исследования B = ${B} бутстрап-повторений по n = ${n} доставок.<br>Только метод слева получает истинную σ = 20. Справа используются одни наблюдения. Это сравнение условий, а не соревнование равноправных методов.<br>Для асимметричного источника и небольших выборок квантильный интервал может накрывать истину реже заявленных 95%. Частоты в конечной серии и сами оценки квантилей тоже случайно колеблются.`);
      Object.assign(root.dataset,{n,M,B,coverage:hit/M,knownCoverage:hitKnown/M});
    }
    button(root,'new',()=>{seed++;render();});bind(root,render);
  }
  function model(root){
    let seed=1101;
    function render(){
      const data=sample(rng(seed),60),kind=value(root,'kind'),r=rng(seed+1000),m=mean(data),s=sd(data),B=1000;
      const draws=kind==='empirical'?Array.from({length:3000},()=>data[Math.floor(r()*data.length)]):Array.from({length:3000},()=>m+s*normal(r));
      const domain=bounds([...data,...draws]);
      const p=hist(chart(root,'observed'),data,domain,'Время, мин','Данные: 60 доставок');vline(p,m,'Выборочное среднее',C.green);
      const q=hist(chart(root,'generated'),draws,domain,'Сгенерированное время, мин',kind==='empirical'?'Повторные значения из наблюдений':'Значения из подобранной нормальной модели');vline(q,m,'Среднее исходных данных',C.green);
      const reps=kind==='empirical'?boot(rng(seed+2000),data,B):batch(rng(seed+2000),data.length,B,'normal',m,s).means;
      const t=hist(chart(root,'statistics'),reps,bounds(reps),'Среднее повторной выборки, мин','В обоих случаях пересчитываем среднее',C.green);vline(t,m,'Исходное среднее',C.gold);
      output(root,`<b>${kind==='empirical'?'Непараметрический':'Параметрический'} бутстрап.</b> Справа вверху 3000 отдельных сгенерированных значений; внизу ${B} средних выборок по 60 значений.<br>${kind==='empirical'?'Каждое значение справа уже встречалось в исходных данных. Мы используем эмпирическое распределение.':'Мы предположили нормальное распределение и оценили его центр и разброс по данным. Возможны новые значения. Отрицательных времён сгенерировано: '+draws.filter(x=>x<0).length+'. Для доставок это показывает возможную проблему выбранной модели; параметрический бутстрап наследует её предположения.'}<br>Схему выбирают по устройству задачи и обоснованности модели, а не по тому, какой интервал оказался уже.`);
      Object.assign(root.dataset,{kind,n:60,negative:draws.filter(x=>x<0).length,estimate:m,se:sd(reps,1)});
    }
    button(root,'new',()=>{seed++;render();});bind(root,render);
  }
  function clusters(root){
    let seed=1201;
    function render(){
      const D=num(root,'groups'),m=8,tau=num(root,'tau'),r=rng(seed),groups=[];
      for(let d=0;d<D;d++){const shift=tau*normal(r);groups.push(Array.from({length:m},()=>30+shift+2*normal(r)));}
      const flat=groups.flat(),groupMeans=groups.map(mean),rows=boot(rng(seed+1000),flat,2000),whole=boot(rng(seed+2000),groupMeans,2000);
      const ticks=Array.from({length:Math.min(6,D)},(_,i)=>Math.round(1+i*(D-1)/(Math.min(6,D)-1)));
      const p=frame(chart(root,'groups'),[.5,D+.5],bounds(flat),'Номер дня','Условный показатель','Внутри дня есть общий случайный сдвиг',true,ticks);
      groups.forEach((g,i)=>g.forEach((x,j)=>dot(p,i+1+(j-3.5)*.07,x,palette[i%12],3)));hline(p,mean(flat),C.gold);
      const domain=bounds([...rows,...whole]);
      const q=hist(chart(root,'rows'),rows,domain,'Общее среднее, усл. ед.','Бутстрап отдельных строк',C.blue);vline(q,mean(flat),'Исходное среднее',C.gold);
      const t=hist(chart(root,'whole'),whole,domain,'Общее среднее, усл. ед.','Бутстрап целых дней',C.green);vline(t,mean(flat),'Исходное среднее',C.gold);
      output(root,`<b>${D} независимых дней по ${m} записей.</b> SE при пересэмплировании строк: ${fmt(sd(rows,1))}; при пересэмплировании дней: ${fmt(sd(whole,1))}.<br>В каждом повторении справа выбираем с возвращением ${D} дней и берём все 8 записей каждого выбранного дня. Повторившийся день повторяется целиком.<br>При заметном общем сдвиге перемешивание отдельных строк разрушает зависимость и обычно занижает неопределённость. Здесь дни независимы и одинакового размера; для последовательных зависимых дней нужна другая схема. Небольшое число дней ограничивает надёжность и кластерного бутстрапа.<br>Это синтетический пример устройства данных, а не расчёт по реальным автобусам.`);
      Object.assign(root.dataset,{groups:D,n:D*m,rowSE:sd(rows,1),clusterSE:sd(whole,1)});
    }
    button(root,'new',()=>{seed++;render();});bind(root,render);
  }
  const widgets={sampling,band:samplingBand,inversion,coverage,resampling,bootstrap,bootcoverage,model,clusters};
  global.InferenceLesson8={mount:(root,kind)=>{if(!root||!widgets[kind])throw new Error('Unknown widget: '+kind);widgets[kind](root);},math:{rng,normal,sample,batch,mean,sd,ppf,quantile,resample,boot,interval,covers}};
})(typeof window!=='undefined'?window:globalThis);
