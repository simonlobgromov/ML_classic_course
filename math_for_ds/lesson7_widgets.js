/* Standalone SVG simulations, embedded into 07_stat_sampling_clt.ipynb. */
(function (global) {
  'use strict';
  const C = { blue:'#6ab0f3', green:'#5fd08a', gold:'#e0b25a', rose:'#e0757f', ink:'#e6e9ec', soft:'#a7b0ba', grid:'#293440' };
  const fmt = (x, d=2) => Number(x).toFixed(d).replace(/\.?0+$/, '') || '0';
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
  function frame(svg,xrange,yrange,xlabel,ylabel,title,showYTicks=true){
    svg.replaceChildren();svg.setAttribute('viewBox','0 0 640 360');svg.setAttribute('role','img');svg.setAttribute('aria-label',`${title}. ${xlabel}; ${ylabel}`);
    svg.appendChild(el('title',{},title));
    const [lo,hi]=xrange,[bottom,top]=yrange,L=68,R=614,T=54,B=301;
    const sx=x=>L+(x-lo)/(hi-lo)*(R-L),sy=y=>B-(y-bottom)/(top-bottom)*(B-T);
    text(svg,L,22,title,C.ink,'start',14);text(svg,L,42,ylabel,C.soft,'start',11);
    if(showYTicks)for(let i=0;i<=4;i++){const y=bottom+(top-bottom)*i/4;svg.appendChild(el('line',{x1:L,x2:R,y1:sy(y),y2:sy(y),stroke:C.grid}));text(svg,L-8,sy(y)+4,fmt(y,3),C.soft,'end',11);}
    for(let i=0;i<=5;i++){const x=lo+(hi-lo)*i/5;svg.appendChild(el('line',{x1:sx(x),x2:sx(x),y1:T,y2:B,stroke:C.grid,'stroke-opacity':.5}));text(svg,sx(x),B+19,fmt(x),C.soft,'middle',11);}
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

  function sampling(root){
    const pop=sample(rng(101),200).sort((a,b)=>a-b),mu=mean(pop);let seed=11;
    function render(){
      const n=num(root,'n'),biased=value(root,'selection')==='low',r=rng(seed),pool=biased?pop.slice(0,150):pop;
      const indices=Array.from({length:n},()=>Math.floor(r()*pool.length)),a=indices.map(i=>pool[i]),selected=new Set(indices);
      const p=frame(chart(root,'population'),[0,200],[0,Math.ceil(Math.max(...pop)/10)*10],'Номер доставки (от быстрых к медленным)','Время доставки, мин','Все 200 вымышленных доставок');
      pop.forEach((x,i)=>dot(p,i+1,x,selected.has(i)?C.green:C.soft,selected.has(i)?4:2));hline(p,mu,C.gold);
      const q=hist(chart(root,'sample'),a,[0,Math.ceil(Math.max(...pop)/10)*10],'Время доставки, мин',`Выбрали ${n} записей`,C.blue);
      vline(q,mu,`Все доставки: ${fmt(mu)} мин`,C.gold);vline(q,mean(a),`Выборка: ${fmt(mean(a))} мин`,C.green,1);
      output(root,`<b>Среднее всех доставок: ${fmt(mu)} мин. Ответ по выборке: ${fmt(mean(a))} мин.</b><br>Жёлтая линия — известное среднее; зелёные точки — выбранные записи. Выбрали ${n} раз, разных записей ${selected.size}: повторения допустимы.<br>${biased?'Мы исключили 50 самых долгих доставок. Даже большая выборка из оставшихся записей не исправляет этот отбор.':'При новом отборе меняется состав выборки, поэтому её среднее может стать другим.'}`);
      Object.assign(root.dataset,{populationMean:mu,sampleMean:mean(a),n,poolMean:mean(pool)});
    }
    button(root,'new',()=>{seed++;render();});bind(root,render);
  }

  function means(root){
    let seed=21,history=[],last=[];
    function drawMore(B){const r=rng(seed++),n=num(root,'n');for(let i=0;i<B;i++){last=sample(r,n);history.push(mean(last));}if(history.length>5000)history=history.slice(-5000);render();}
    function render(){
      if(!history.length)return;
      const n=num(root,'n'),p=hist(chart(root,'observations'),last,[10,Math.max(110,...last)],'Время одной доставки, мин','Последняя выборка: отдельные доставки');
      vline(p,30,'μ = 30',C.gold);vline(p,mean(last),'Среднее этой выборки',C.green,1);
      const q=hist(chart(root,'means'),history,[5,100],'Среднее одной выборки, мин','Ответы по разным выборкам',C.green);
      vline(q,30,'μ = 30',C.gold);
      output(root,`<b>В каждой выборке ${n} доставок. Справа собрано ${history.length} средних.</b><br>Ответ последней выборки: ${fmt(mean(last))} мин. Истинное среднее источника: 30 мин.<br>Слева число — время одной доставки. Справа число — среднее целой выборки. Новое повторение добавляет справа один ответ. Смена размера выборки очищает историю; храним до 5000 ответов.`);
      Object.assign(root.dataset,{n,B:history.length,meanOfMeans:mean(history)});
    }
    button(root,'one',()=>drawMore(1));button(root,'many',()=>drawMore(200));
    bind(root,()=>{history=[];drawMore(1);});
  }

  function precision(root){
    let seed=31;
    function render(){
      const n=num(root,'n'),sigma=num(root,'sigma'),B=num(root,'B'),mu=30,r=rng(seed),out=batch(r,n,B,'skew',mu,sigma),se=sigma/Math.sqrt(n);
      const p=hist(chart(root,'spread'),out.means,[0,mu+2*sigma],'Среднее одной выборки, мин','Как разбросаны средние',C.green);
      vline(p,mu,'μ = 30',C.gold);
      const curve=frame(chart(root,'law'),[1,400],[0,Math.max(sigma,1)],'Доставок в одной выборке n','Стандартная ошибка, мин','Как SE зависит от размера выборки');
      line(curve,Array.from({length:400},(_,i)=>[i+1,sigma/Math.sqrt(i+1)]),C.gold);dot(curve,n,se,C.green,6);
      output(root,`<b>SD отдельных доставок: ${fmt(sigma)} мин. SE среднего по ${n} доставкам: ${fmt(se,2)} мин.</b><br>Проверка опытом: разброс ${B} полученных средних ≈ ${fmt(sd(out.means,1),2)} мин.<br>Справа зелёная точка показывает выбранный размер выборки. Больше доставок в каждой выборке — меньше SE. Больше повторений B — подробнее изображение того же распределения.`);
      Object.assign(root.dataset,{se,empiricalSE:sd(out.means,1),n,B});
    }
    button(root,'new',()=>{seed++;render();});bind(root,render);
  }

  function convergence(root){
    let seed=41;
    function render(){
      const n=num(root,'n'),biased=value(root,'selection')==='biased';
      const paths=Array.from({length:4},(_,path)=>{const r=rng(seed+path*10007);let total=0;return Array.from({length:n},(_,i)=>{total+=sample(r,1,'skew',biased?20:30,biased?10:20)[0];return[i+1,total/(i+1)];});});
      const p=frame(chart(root,'paths'),[1,Math.max(n,2)],[0,Math.max(100,...paths.flat().map(a=>a[1]))*1.03],'Сколько доставок накопили','Среднее по накопленным доставкам, мин','Четыре набора данных: следим за средним');
      paths.forEach((a,i)=>line(p,a,[C.blue,C.green,C.rose,C.soft][i]));hline(p,30,C.gold);
      output(root,`<b>Последние средние: ${paths.map(a=>fmt(a.at(-1)[1])).join('; ')} мин.</b><br>Жёлтая линия — нужное нам среднее 30 мин. ${biased?'Но данные сейчас приходят от другой службы, со средним 20 мин. Большой объём уточняет ответ про неё, а не про нашу службу.':'В среднем ответ становится устойчивее, хотя на отдельных шагах может отдаляться от 30.'}`);
      root.dataset.target=30;root.dataset.sourceMean=biased?20:30;
    }
    button(root,'new',()=>{seed++;render();});bind(root,render);
  }

  function clt(root){
    let seed=51;
    function render(){
      const n=num(root,'n'),B=num(root,'B'),kind=value(root,'shape'),standardized=value(root,'scale')==='z',delivery=kind==='skew';
      const mu=delivery?30:0,sigma=delivery?20:1,r=rng(seed),raw=sample(r,6000,kind,mu,sigma);
      const means=batch(r,n,B,kind,mu,sigma).means,se=sigma/Math.sqrt(n),z=means.map(x=>(x-mu)/se);
      const source=hist(chart(root,'source'),raw,delivery?[0,170]:kind==='rare'?[-4,12]:[-4,4],delivery?'Время одной доставки, мин':'Значение показателя, условные единицы',delivery?'Отдельные доставки — длинный правый хвост':'Отдельные наблюдения',C.blue);
      vline(source,mu,`Среднее ${mu}`,C.green);
      const domain=standardized?[-5,7]:[delivery?Math.max(0,mu-5*se):mu-5*se,mu+7*se];
      const q=hist(chart(root,'standardized'),standardized?z:means,domain,standardized?'Отклонение среднего в единицах SE':delivery?'Среднее одной выборки, мин':'Среднее одной выборки, условные единицы',standardized?'Средние после перехода в z-шкалу':'Средние по выборкам и нормальная кривая',C.green,{mu:standardized?0:mu,sd:standardized?1:se});
      vline(q,standardized?0:mu,standardized?'Центр 0':`Центр ${mu}`,C.gold);
      output(root,`<b>В каждой выборке ${n} наблюдений. SE среднего = ${fmt(se,3)}${delivery?' мин':''}. Повторений: ${B}.</b><br>${standardized?'Справа из каждого среднего вычли истинный центр и поделили на SE. Жёлтая кривая — стандартная нормаль.':'Справа обычные средние. Жёлтая кривая имеет тот же истинный центр и разброс SE. Масштаб правой оси меняется с n: читайте числа на ней.'}<br>${kind==='normal'?'Нормальный источник даёт нормальные средние при любом n.':kind==='rare'?'Редкие большие значения могут замедлять приближение к нормальной форме. Проверяйте его, а не полагайтесь на правило «30 достаточно».':'При увеличении n гистограмма средних приближается по форме к нормальной кривой. Левое распределение при этом сохраняется.'}<br>Если часть значений не помещается в окно графика, их количество подписано.`);
      Object.assign(root.dataset,{n,B,zMean:mean(z),zSD:sd(z,1),se,center:mu,scale:standardized?'z':'raw'});
    }
    button(root,'new',()=>{seed++;render();});bind(root,render);
  }

  function proportion(root){
    let seed=61;
    function render(){
      const n=num(root,'n'),p=num(root,'p'),r=rng(seed),rates=Array.from({length:2000},()=>{let count=0;for(let i=0;i<n;i++)count+=r()<p;return count/n;});
      const se=Math.sqrt(p*(1-p)/n),plot=hist(chart(root,'rates'),rates,[-.01,1.01],'Доля единиц в одной выборке','Доля — среднее нулей и единиц',C.green);
      vline(plot,p,`Истинная p = ${fmt(p)}`,C.gold);
      output(root,`<b>SE доли: ${fmt(100*se)} процентных пункта.</b><br>Собрали 2000 выборок по ${n} наблюдений. В ${fmt(100*rates.filter(x=>x===0).length/rates.length)}% выборок не было ни одного успеха, хотя вероятность успеха равна ${fmt(100*p)}%.<br>Доля может быть нулевой в одной выборке, даже если событие возможно. При редких успехах форма распределения долей может быть далеко от нормальной.`);
      Object.assign(root.dataset,{se,empiricalSE:sd(rates,1),p,n});
    }
    button(root,'new',()=>{seed++;render();});bind(root,render);
  }

  function dependence(root){
    let seed=71;
    function render(){
      const days=num(root,'days'),m=num(root,'m'),tau=num(root,'tau'),sigma=4,n=days*m,r=rng(seed),means=[],points=[];
      for(let b=0;b<1500;b++){let total=0;for(let d=0;d<days;d++){const shift=tau*normal(r);for(let j=0;j<m;j++){const x=30+shift+sigma*normal(r);total+=x;if(b===0)points.push([d+1,x]);}}means.push(total/n);}
      const trueSE=Math.sqrt(tau*tau/days+sigma*sigma/n),naive=Math.sqrt(tau*tau+sigma*sigma)/Math.sqrt(n);
      const p=frame(chart(root,'groups'),[.5,days+.5],bounds(points.map(x=>x[1]),.15),'Номер независимой группы','Показатель, усл. ед.','Общий сдвиг внутри каждой группы');
      points.forEach(([d,x],i)=>dot(p,d+((i%m)/Math.max(m-1,1)-.5)*.55,x,d%2?C.blue:C.green,2.5));hline(p,30,C.gold);
      const q=hist(chart(root,'groupmeans'),means,[30-5*trueSE,30+5*trueSE],'Общее среднее, усл. ед.','Распределение средних с зависимостью',C.green,{mu:30,sd:trueSE});vline(q,30,'μ = 30',C.gold);
      output(root,`<b>${days} групп по ${m} измерений: всего ${n} строк.</b><br>Правильная SE: ${fmt(trueSE,2)}. Если забыть о связи внутри группы: ${fmt(naive,2)}. Проверка по 1500 опытам: ${fmt(sd(means,1),2)}.<br>Измерения одной группы сдвигаются вместе. Новые независимые группы дают информацию, которую не заменяют дополнительные строки в прежних группах. При нулевом общем сдвиге две SE совпадают.`);
      Object.assign(root.dataset,{trueSE,naiveSE:naive,empiricalSE:sd(means,1),n});
    }
    button(root,'new',()=>{seed++;render();});bind(root,render);
  }

  function medicine(root){
    let seed=81;
    function render(){
      const n=num(root,'n'),delta=num(root,'delta'),noise=num(root,'noise'),background=num(root,'background'),r=rng(seed);
      // Independent synthetic patients, allocated at random to equal-size groups.
      const patients=Array.from({length:2*n},()=>background+noise*normal(r));
      for(let i=patients.length-1;i>0;i--){const j=Math.floor(r()*(i+1));[patients[i],patients[j]]=[patients[j],patients[i]];}
      const control=patients.slice(0,n),treated=patients.slice(n).map(x=>x+delta),observed=mean(treated)-mean(control),se=noise*Math.sqrt(2/n);
      const domain=bounds([...control,...treated]),p=frame(chart(root,'patients'),domain,[0,3],'Улучшение: до − после, баллы','Группа (каждая точка — пациент)','Один случайно распределённый эксперимент',false);
      control.forEach((x,i)=>dot(p,x,.7+(i%9)*.045,C.blue));treated.forEach((x,i)=>dot(p,x,1.85+(i%9)*.045,C.green));
      text(p.svg,p.L+8,p.sy(1.25),'Контроль',C.blue,'start');text(p.svg,p.L+8,p.sy(2.4),'Препарат',C.green,'start');
      vline(p,mean(control),`Контроль: ${fmt(mean(control))}`,C.blue);vline(p,mean(treated),`Препарат: ${fmt(mean(treated))}`,C.green,1);
      const nullDiffs=Array.from({length:3000},()=>se*normal(r)),span=Math.max(4.5*se,Math.abs(observed)*1.2,Math.abs(delta)*1.2,1);
      const q=hist(chart(root,'null'),nullDiffs,[-span,span],'Среднее препарата − среднее контроля, баллы','Какие разности бывают без действия препарата',C.soft,{mu:0,sd:se});
      vline(q,0,'Нет эффекта',C.gold);vline(q,observed,`Наблюдали ${fmt(observed)}`,C.rose,1);
      output(root,`<b>Среднее улучшение: препарат ${fmt(mean(treated))}, контроль ${fmt(mean(control))} балла. Разность: ${fmt(observed)}.</b><br>Заданное действие препарата: ${fmt(delta)} балла. Это известная нам настройка симуляции; в настоящем исследовании её не знают.<br>Справа 3000 разностей, возможных без действия препарата. Розовая линия — результат текущего опыта. Насколько далеко она от обычных разностей? Формальное правило ответа разберём на следующем занятии.`);
      Object.assign(root.dataset,{delta,observed,se,background,n});
    }
    button(root,'new',()=>{seed++;render();});bind(root,render);
  }

  const widgets={sampling,means,precision,convergence,clt,proportion,dependence,medicine};
  global.SamplingLesson7={mount:(root,kind)=>{if(!root||!widgets[kind])throw new Error('Unknown widget: '+kind);widgets[kind](root);},math:{rng,normal,draw,sample,batch,mean,sd,pdf}};
})(typeof window!=='undefined'?window:globalThis);
