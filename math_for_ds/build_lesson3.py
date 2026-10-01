# -*- coding: utf-8 -*-
"""Builds the Colab notebook «Статистика S1 — Генеральная совокупность и выборка».
Theory prose is Russian (academic); code and exercises are English.
Run:  ./venv/bin/python math_for_ds/build_lesson3.py
Out:  math_for_ds/03_stat_intro.ipynb
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from theme import SETUP, META

cells = []
def md(src):   cells.append(new_markdown_cell(src))
def code(src): cells.append(new_code_cell(src))

# ============================================================================
# 0. Заголовок
# ============================================================================
md(r"""# Статистика для Data Science
## Занятие S1 — Генеральная совокупность и выборка

Мы начинаем статистический трек. Первый и главный вопрос: **о чём вообще говорят числа
в таблице?** Любой признак — это лишь горстка измерений, доступных нам, тогда как интересует
нас, как правило, гораздо более широкий круг объектов. Различение этих двух вещей —
**генеральной совокупности** и **выборки** — лежит в основании всей статистики, поэтому с него
и начнём. Пока никакой вероятности не потребуется: работаем с теми данными, что есть.

Датасет-пример прежний — `Davis` (вес и рост 200 человек).
""")

# ============================================================================
# 1. Данные + оформление
# ============================================================================
code(r"""import numpy as np
import pandas as pd
from datasets import load_dataset

dataset = load_dataset('aiacademy-kg/davis_dataset', split='train')
df = dataset.to_pandas()""")

code(r"""df.head()""")

code(SETUP)

# ============================================================================
# 2. ТЕОРИЯ S1 — определения + большая визуализация (jointplot)
# ============================================================================
code(r'''#@title Теория S1 — Совокупность, выборка, смещение { display-mode: "form" }
import json
rng = np.random.default_rng(7)
N = 1200
cov = [[1.0, 0.55], [0.55, 1.0]]
pop = rng.multivariate_normal([0.0, 0.0], cov, size=N)
POP = json.dumps([[round(float(x), 3), round(float(y), 3)] for x, y in pop])
cx, cy = pop.mean(axis=0)

body = r"""
<h2>1. Генеральная совокупность и выборка</h2>

<div class="box def"><div class="t">Определения</div>
<ul>
<li><b>Генеральная совокупность</b> <span class="en">(population)</span> — всё множество объектов,
о которых мы хотим сделать вывод (например, все взрослые люди страны). Её числовые характеристики
называют <b>истинными</b> или <b>параметрами</b> <span class="en">(parameters)</span>; истинное
среднее обозначают греческой буквой $\mu$.</li>
<li><b>Выборка</b> <span class="en">(sample)</span> — конечное подмножество совокупности, которое
реально измерено. Число наблюдений в ней — <b>объём выборки</b> <span class="en">(sample size)</span>
$n$. Величины, посчитанные по выборке, называют <b>оценками</b> <span class="en">(estimates)</span>;
выборочное среднее обозначают $\bar x$.</li>
</ul>
Всю совокупность измерить обычно невозможно, поэтому о параметре $\mu$ судят по оценке $\bar x$.
Вопрос лишь в том, <em>насколько</em> оценка близка к истине.</div>

<p>Ответ зависит от двух свойств выборки — репрезентативности и наличия смещения.</p>
<ul>
<li><b>Репрезентативность</b> <span class="en">(representativeness)</span>. Выборка репрезентативна,
если её строение повторяет строение совокупности. Тогда оценки близки к параметрам, и с ростом $n$
выборочный центроид $\bar x$ приближается к истинному $\mu$.</li>
<li><b>Случайная выборка</b> <span class="en">(random sample)</span>. Простейший способ добиться
репрезентативности — отбирать наблюдения случайно и независимо, чтобы у каждого объекта
совокупности были равные шансы попасть в выборку.</li>
<li><b>Смещение</b> <span class="en">(bias)</span>. Систематическая ошибка отбора, при которой одни объекты
совокупности попадают в выборку чаще других. Смещение <em>не устраняется</em> увеличением
объёма: сколь угодно большая, но искажённо собранная выборка даёт оценку, не сходящуюся к $\mu$.</li>
</ul>
<p>Ниже — интерактив: слева вся совокупность, справа выборка из неё. Меняйте объём $n$ и
включайте смещение, следя за жёлтым центроидом $\bar x$ относительно белого $\mu$.</p>
"""

figure = r"""
<div class="widget"><div class="widget-title">Совокупность и выборка: центроид как оценка</div>
<div class="widget-sub">Слева — вся совокупность (синие точки), справа — выборка из неё (зелёные).
По краям — гистограммы каждого признака. Белый крест — истинный центроид $\mu$, жёлтый — центроид
выборки $\bar x$. Двигайте объём $n$; включите «смещённую выборку» и проследите за расстоянием
$\lvert\bar x-\mu\rvert$.</div>
<svg viewBox="0 0 600 300" id="svg-samp"></svg>
<div class="controls">
<div class="control"><label>объём выборки $n$ =</label>
<input type="range" id="samp-n" min="100" max="1000" step="100" value="300"><span class="val" id="samp-n-val">300</span></div>
<div class="control"><label><input type="checkbox" id="samp-bias"> смещённая выборка (только левая часть)</label></div>
</div>
<div class="readout" id="samp-ro"></div>
<div class="box warn" style="margin-top:12px"><div class="t">Какое смещение здесь моделируется</div>
При включённом флажке в выборку попадают только наблюдения, у которых признак $X$ меньше среднего
по совокупности (левая половина облака). Такой отбор систематически занижает оценку по $X$, а из-за
положительной корреляции признаков смещается и оценка по $Y$: жёлтый центроид уходит влево-вниз и
не возвращается к $\mu$ при росте $n$.</div>
</div>
"""

after = r"""
<div class="box take"><div class="t">Что показывает эта картинка</div>
При <b>случайной</b> выборке жёлтый центроид $\bar x$ дрожит вокруг белого $\mu$ и с ростом $n$
подбирается к нему всё ближе — это будущий <b>закон больших чисел</b>. При <b>смещённой</b>
выборке жёлтый центроид уезжает в сторону и там и остаётся, сколько ни увеличивай $n$: это и есть
разница между <em>случайной погрешностью</em> (лечится объёмом) и <em>систематическим смещением</em>
(объёмом не лечится).</div>

<p>Практический вывод для машинного обучения: качество модели ограничено прежде всего тем, <b>как
собраны данные</b>. Если обучающая выборка собрана смещённо, модель воспроизведёт это смещение —
и увеличение объёма данных проблему не решит.</p>
"""

script = r"""
(function(){
 const svg=document.getElementById("svg-samp"); if(!svg) return;
 const POP=__POP__, CX=__CX__, CY=__CY__;
 const nS=document.getElementById("samp-n"), nV=document.getElementById("samp-n-val");
 const biasCb=document.getElementById("samp-bias"), ro=document.getElementById("samp-ro");
 const DMIN=-3.6, DMAX=3.6, NB=18, Ssq=210, HH=42, TY=70, LX=40, RX=330;
 function cross(g,px,py,c){
  g.appendChild(el("line",{x1:px-7,y1:py,x2:px+7,y2:py,stroke:"#0b0f14","stroke-width":4.5,"stroke-linecap":"round"}));
  g.appendChild(el("line",{x1:px,y1:py-7,x2:px,y2:py+7,stroke:"#0b0f14","stroke-width":4.5,"stroke-linecap":"round"}));
  g.appendChild(el("line",{x1:px-7,y1:py,x2:px+7,y2:py,stroke:c,"stroke-width":2.5,"stroke-linecap":"round"}));
  g.appendChild(el("line",{x1:px,y1:py-7,x2:px,y2:py+7,stroke:c,"stroke-width":2.5,"stroke-linecap":"round"}));
  g.appendChild(el("circle",{cx:px,cy:py,r:3,fill:c,stroke:"#0b0f14","stroke-width":1}));
 }
 function centroid(a){let sx=0,sy=0;for(const p of a){sx+=p[0];sy+=p[1];}const k=a.length||1;return [sx/k,sy/k];}
 function panel(g,ox,pts,ptc,ptop,histc,cents,title){
  const sx=v=>ox+(clamp(v,DMIN,DMAX)-DMIN)/(DMAX-DMIN)*Ssq;
  const sy=v=>TY+Ssq-(clamp(v,DMIN,DMAX)-DMIN)/(DMAX-DMIN)*Ssq;
  g.appendChild(el("rect",{x:ox,y:TY,width:Ssq,height:Ssq,fill:"#0b0f14",stroke:"#2a313b","stroke-width":1}));
  for(let t=-3;t<=3;t++){ const ax=(t===0), col=ax?"#46505c":"#19212c", wd=ax?1.3:1;
   g.appendChild(el("line",{x1:sx(t),y1:TY,x2:sx(t),y2:TY+Ssq,stroke:col,"stroke-width":wd}));
   g.appendChild(el("line",{x1:ox,y1:sy(t),x2:ox+Ssq,y2:sy(t),stroke:col,"stroke-width":wd})); }
  for(const t of [-2,0,2]){
   const la=el("text",{x:sx(t),y:TY+Ssq+13,fill:"#6b7580","font-family":"sans-serif","font-size":10,"text-anchor":"middle"});la.textContent=t;g.appendChild(la);
   const lb=el("text",{x:ox-6,y:sy(t)+3,fill:"#6b7580","font-family":"sans-serif","font-size":10,"text-anchor":"end"});lb.textContent=t;g.appendChild(lb); }
  for(const p of pts){ if(p[0]<DMIN||p[0]>DMAX||p[1]<DMIN||p[1]>DMAX) continue;
   g.appendChild(el("circle",{cx:sx(p[0]),cy:sy(p[1]),r:2,fill:ptc,"fill-opacity":ptop})); }
  const bw=(DMAX-DMIN)/NB, hx=new Array(NB).fill(0), hy=new Array(NB).fill(0);
  for(const p of pts){ hx[clamp(Math.floor((p[0]-DMIN)/bw),0,NB-1)]++; hy[clamp(Math.floor((p[1]-DMIN)/bw),0,NB-1)]++; }
  const mx=Math.max(1,...hx), my=Math.max(1,...hy);
  for(let i=0;i<NB;i++){ const bh=hx[i]/mx*HH; if(bh>0.5)
   g.appendChild(el("rect",{x:sx(DMIN+i*bw)+0.5,y:TY-bh,width:Ssq/NB-1,height:bh,fill:histc,"fill-opacity":.75})); }
  for(let j=0;j<NB;j++){ const bl=hy[j]/my*HH; if(bl>0.5)
   g.appendChild(el("rect",{x:ox+Ssq+1,y:sy(DMIN+(j+1)*bw),width:bl,height:Ssq/NB-1,fill:histc,"fill-opacity":.75})); }
  for(const c of cents) cross(g,sx(c.x),sy(c.y),c.c);
  const t=el("text",{x:ox,y:TY-HH-10,fill:"#e6e9ec","font-family":"sans-serif","font-size":13,"font-weight":700});
  t.textContent=title; g.appendChild(t);
 }
 // static population panel (drawn once)
 const gPop=el("g"); svg.appendChild(gPop);
 panel(gPop,LX,POP,"#6ab0f3",0.30,"#6ab0f3",[{x:CX,y:CY,c:"#ffffff"}],"Генеральная совокупность · N="+POP.length);
 const gSamp=el("g"); svg.appendChild(gSamp);
 function render(){
  const n=+nS.value; nV.textContent=n;
  while(gSamp.firstChild) gSamp.removeChild(gSamp.firstChild);
  const pool=biasCb.checked?POP.filter(p=>p[0]<0):POP;
  const m=Math.min(n,pool.length), samp=pool.slice(0,m), sc=centroid(samp);
  panel(gSamp,RX,samp,"#5fd08a",0.8,"#5fd08a",
    [{x:CX,y:CY,c:"#ffffff"},{x:sc[0],y:sc[1],c:"#ffce54"}],"Выборка · n="+m);
  const dist=Math.hypot(sc[0]-CX,sc[1]-CY);
  ro.innerHTML=`n=${m} · x̄=(${sc[0].toFixed(2)}, ${sc[1].toFixed(2)}) · μ=(${CX.toFixed(2)}, ${CY.toFixed(2)}) · `
    +`|x̄−μ|=<b>${dist.toFixed(3)}</b>`+(biasCb.checked?` · <span style="color:#e0757f">смещение не сходится к μ</span>`:``);
 }
 nS.addEventListener("input",render); biasCb.addEventListener("change",render); render();
})();
""".replace("__POP__", POP).replace("__CX__", repr(round(float(cx), 4))).replace("__CY__", repr(round(float(cy), 4)))

display(HTML(viz(body)))
display(HTML(viz(figure, script, wide=True)))
display(HTML(viz(after)))''')

# ============================================================================
# 3. ТЕОРИЯ S2 — гистограмма (bins slider + optional KDE)
# ============================================================================
code(r'''#@title Теория S2 — Гистограмма { display-mode: "form" }
import json
W_JSON = json.dumps([round(float(v), 1) for v in df['weight']])
H_JSON = json.dumps([round(float(v), 1) for v in df['height']])
SEX_JSON = json.dumps([str(s) for s in df['sex']])

intro = r"""
<h2>2. Гистограмма <span class="en">(histogram)</span></h2>
<p>Среднее и центроид сжимают признак до одной точки, но ничего не говорят о <em>форме</em> его
распределения. Простейший инструмент, чтобы эту форму увидеть, — <b>гистограмма</b>.</p>
<div class="box def"><div class="t">Как строится</div>
<ol>
<li>Диапазон значений признака разбивают на равные интервалы — <b>бины</b> <span class="en">(bins)</span>.</li>
<li>Подсчитывают, сколько наблюдений попало в каждый бин (<b>частоту</b> <span class="en">(frequency)</span>).</li>
<li>Над каждым бином рисуют столбик высотой в это число.</li>
</ol>
По горизонтальной оси — значения признака, по вертикальной — количество наблюдений
<span class="en">(count)</span>.</div>
<p>Гистограмма отвечает на вопросы, которые не видны из среднего: где значения сгущаются,
симметрично ли распределение, один у него горб или несколько, есть ли выбросы.</p>
"""

figure = r"""
<div class="widget"><div class="widget-title">Histogram of a Davis feature</div>
<div class="widget-sub">Столбики — число наблюдений в каждом интервале (бине). Меняйте число бинов
ползунком; включите <b>KDE</b>, чтобы наложить сглаженную кривую плотности.</div>
<svg viewBox="0 0 600 340" id="svg-hist"></svg>
<div class="controls">
<div class="control"><label>feature</label>
<select id="hist-feat"><option value="height">height</option><option value="weight">weight</option></select></div>
<div class="control"><label>bins =</label>
<input type="range" id="hist-bins" min="4" max="40" step="1" value="12"><span class="val" id="hist-bins-val">12</span></div>
<div class="control"><label><input type="checkbox" id="hist-kde"> KDE</label></div>
<div class="control"><label>bandwidth ×</label>
<input type="range" id="hist-bw" min="0.5" max="2" step="0.1" value="1.0"><span class="val" id="hist-bw-val">1.0</span></div>
</div>
<div class="readout" id="hist-ro"></div></div>
"""

after = r"""
<div class="box warn"><div class="t">Число бинов — это выбор</div>
Слишком мало бинов — форма огрубляется, детали теряются; слишком много — в каждый бин попадает
пара наблюдений, гистограмма становится «рваной» и отражает случайный шум, а не форму. Хорошее
число подбирают так, чтобы форма читалась, но не дробилась. Подвигайте ползунок и сравните.</div>

<h3>Ядерная оценка плотности <span class="en">(KDE)</span></h3>
<p>Форма гистограммы зависит и от числа бинов, и от положения их границ. Более гладкую и устойчивую
к границам оценку даёт <b>ядерная оценка плотности</b>
<span class="en">(kernel density estimate, KDE)</span>: вместо жёстких столбиков на каждое
наблюдение кладут маленький «холмик» — <b>ядро</b> <span class="en">(kernel)</span>, обычно
гауссово, — а затем складывают все холмики в одну гладкую кривую:</p>
$$ \hat f(x)=\frac{1}{n\,h}\sum_{i=1}^{n} K\!\left(\frac{x-x_i}{h}\right). $$
<div class="where">Где:
<ul>
<li>$\hat f(x)$ — оценка плотности в точке $x$ (высота гладкой кривой);</li>
<li>$n$ — объём выборки;</li>
<li>$x_1,\dots,x_n$ — наблюдения выборки;</li>
<li>$h$ — полоса пропускания <span class="en">(bandwidth)</span>, ширина одного холмика;</li>
<li>$K(\cdot)$ — ядро <span class="en">(kernel)</span>: функция-«холмик», задающая форму вклада одного наблюдения;</li>
<li>$\dfrac{x-x_i}{h}$ — отклонение точки $x$ от наблюдения $x_i$, выраженное в единицах $h$.</li>
</ul></div>
<p>Малая $h$ даёт изрезанную, шумную кривую, большая — переглаженную. На графике кривая KDE
масштабирована к числу наблюдений, чтобы её можно было наложить на столбики.</p>

<details><summary>Для любознательных: как строится кривая KDE</summary>
<p>Кривую собирают из одинаковых «холмиков» по шагам:</p>
<ol>
<li>над каждым наблюдением $x_i$ ставят ядро $K$, центрированное в $x_i$ и суженное или
расширенное параметром $h$;</li>
<li>вклад одного наблюдения — это $\dfrac{1}{n h}\,K\!\left(\dfrac{x-x_i}{h}\right)$; множитель
$\dfrac{1}{n h}$ нормирует кривую так, чтобы полная площадь под ней равнялась $1$;</li>
<li>складывают все $n$ вкладов — получается гладкая оценка $\hat f(x)$.</li>
</ol>
<p>Чаще всего ядро берут гауссовым:</p>
$$ K(u)=\frac{1}{\sqrt{2\pi}}\,e^{-u^{2}/2}. $$
<div class="where">Где: $u=\dfrac{x-x_i}{h}$ — стандартизованное расстояние от точки $x$ до
наблюдения $x_i$. При $u=0$ (точно над наблюдением) холмик максимален, а вдали быстро спадает к нулю.</div>
<p>Ниже видно, как это работает: тонкие синие кривые — отдельные холмики над наблюдениями
(отмечены штрихами по оси), жёлтая жирная — их сумма $\hat f$. Меняйте $h$ и проследите, как из
острых пиков рождается единая гладкая кривая, а при большом $h$ она переглаживается.</p>
<div class="widget"><div class="widget-title">Сумма ядер даёт кривую KDE</div>
<svg viewBox="0 0 600 220" id="svg-bumps"></svg>
<div class="controls"><div class="control"><label>bandwidth $h$ =</label>
<input type="range" id="bumps-h" min="0.15" max="1.6" step="0.05" value="0.5"><span class="val" id="bumps-h-val">0.50</span></div></div>
</div>
</details>
"""

mode_text = r"""
<h3>Мода <span class="en">(mode)</span></h3>
<p>Пик гистограммы (и вершина KDE) отвечает важной характеристике — <b>моде</b>. Мода — это
значение признака, которое встречается чаще всего; на графике это положение самого высокого
столбика или вершины кривой плотности. В отличие от среднего, мода показывает не «центр тяжести»,
а <em>самое типичное</em> значение.</p>
<ul>
<li><b>Унимодальное распределение</b> <span class="en">(unimodal)</span> — с одним пиком (одна мода).</li>
<li><b>Мультимодальное</b> <span class="en">(multimodal)</span> — с несколькими пиками; частный
случай с двумя пиками называют <b>бимодальным</b> <span class="en">(bimodal)</span>.</li>
</ul>
<p>Несколько мод — это сигнал: скорее всего, данные <b>смешаны из нескольких групп</b> с разными
центрами. Распределение роста в Davis <b>бимодально</b>. Причина — скрытая категориальная
переменная <code>sex</code>: у мужчин и женщин разный средний рост ($\approx 178$ и $\approx 165$ см),
и общая гистограмма оказывается наложением двух групп. Разделим её по полу и наложим KDE каждой группы:</p>
"""

figure_gender = r"""
<div class="widget"><div class="widget-title">Height distribution split by sex</div>
<div class="widget-sub">Серые столбики — рост всех 200 человек. Кривые KDE:
<span style="color:#6ab0f3">мужчины</span>, <span style="color:#e0757f">женщины</span>,
<span style="color:#ffce54">все вместе</span>. Общая кривая имеет два горба — по одному на каждую группу.</div>
<svg viewBox="0 0 600 340" id="svg-gender"></svg>
<div class="controls">
<div class="control"><label>bins =</label>
<input type="range" id="gen-bins" min="6" max="40" step="1" value="18"><span class="val" id="gen-bins-val">18</span></div>
<div class="control"><label>bandwidth ×</label>
<input type="range" id="gen-bw" min="0.5" max="2" step="0.1" value="1.0"><span class="val" id="gen-bw-val">1.0</span></div>
</div>
<div class="readout" id="gen-ro"></div></div>
"""

closing = r"""
<div class="box take"><div class="t">Итог по гистограмме и KDE</div>
Гистограмма и KDE — первый способ <em>увидеть распределение</em>: где его центр, каков разброс, одна
у него мода или несколько. Несколько мод почти всегда означают смесь разнородных групп. На следующем
занятии мы перейдём от эмпирической картинки к идеализированным распределениям, прежде всего к
нормальному.</div>
"""

script = r"""
(function(){
 const svg=document.getElementById("svg-hist"); if(!svg) return;
 const DATA={weight:{v:__W__,label:"weight (kg)"}, height:{v:__H__,label:"height (cm)"}};
 const featSel=document.getElementById("hist-feat"), binsS=document.getElementById("hist-bins"), binsV=document.getElementById("hist-bins-val");
 const kdeCb=document.getElementById("hist-kde"), bwS=document.getElementById("hist-bw"), bwV=document.getElementById("hist-bw-val");
 const ro=document.getElementById("hist-ro");
 const CW=600, CH=340, ML=50, MR=18, MT=18, MB=44, PW=CW-ML-MR, PH=CH-MT-MB, X0=ML, Y0=MT+PH;
 function mean(a){let s=0;for(const x of a)s+=x;return s/a.length;}
 function std(a){const m=mean(a);let s=0;for(const x of a)s+=(x-m)*(x-m);return Math.sqrt(s/a.length);}
 function nice(x){const e=Math.pow(10,Math.floor(Math.log10(x)));const f=x/e;return (f<1.5?1:f<3?2:f<7?5:10)*e;}
 function ticks(a,b,m){const st=nice((b-a)/m),t=[];let s=Math.ceil(a/st)*st;for(;s<=b+1e-9;s+=st)t.push(+s.toFixed(6));return t;}
 function render(){
  const feat=DATA[featSel.value], arr=feat.v, n=arr.length;
  const B=+binsS.value; binsV.textContent=B;
  const bwk=+bwS.value; bwV.textContent=bwk.toFixed(1);
  let lo=Math.min.apply(null,arr), hi=Math.max.apply(null,arr); const pad=(hi-lo)*0.04; lo-=pad; hi+=pad;
  const binW=(hi-lo)/B, counts=new Array(B).fill(0);
  for(const x of arr){let k=Math.floor((x-lo)/binW); if(k>=B)k=B-1; if(k<0)k=0; counts[k]++;}
  let ymax=Math.max.apply(null,counts);
  const showK=kdeCb.checked; const G=160, xs=[], dens=[]; let hband=0;
  if(showK){ hband=bwk*1.06*std(arr)*Math.pow(n,-0.2);
   for(let i=0;i<G;i++){const x=lo+(hi-lo)*i/(G-1); let s=0; for(const xi of arr){const u=(x-xi)/hband; s+=Math.exp(-0.5*u*u);}
    xs.push(x); dens.push(s/(n*hband*Math.sqrt(2*Math.PI))*n*binW);}
   ymax=Math.max(ymax,Math.max.apply(null,dens)); }
  ymax*=1.12;
  const sx=v=>X0+(v-lo)/(hi-lo)*PW, sy=v=>Y0-v/ymax*PH;
  while(svg.firstChild)svg.removeChild(svg.firstChild); const g=el("g"); svg.appendChild(g);
  for(const t of ticks(0,ymax,5)){ if(t>ymax)continue;
   g.appendChild(el("line",{x1:X0,y1:sy(t),x2:X0+PW,y2:sy(t),stroke:"#19212c","stroke-width":1}));
   const l=el("text",{x:X0-8,y:sy(t)+4,fill:"#6b7580","font-family":"sans-serif","font-size":11,"text-anchor":"end"});l.textContent=Math.round(t);g.appendChild(l); }
  for(let i=0;i<B;i++){ if(counts[i]<=0)continue; const x=sx(lo+i*binW), w=PW/B-1, y=sy(counts[i]);
   g.appendChild(el("rect",{x:x+0.5,y,width:Math.max(1,w),height:Y0-y,fill:"#5fd08a","fill-opacity":.42,stroke:"#5fd08a","stroke-width":1})); }
  g.appendChild(el("line",{x1:X0,y1:Y0,x2:X0+PW,y2:Y0,stroke:"#46505c","stroke-width":1.2}));
  g.appendChild(el("line",{x1:X0,y1:MT,x2:X0,y2:Y0,stroke:"#46505c","stroke-width":1.2}));
  for(const t of ticks(lo+pad,hi-pad,6)){ g.appendChild(el("line",{x1:sx(t),y1:Y0,x2:sx(t),y2:Y0+5,stroke:"#46505c","stroke-width":1}));
   const l=el("text",{x:sx(t),y:Y0+18,fill:"#8a929a","font-family":"sans-serif","font-size":11,"text-anchor":"middle"});l.textContent=(Math.abs(t)>=100?Math.round(t):+t.toFixed(1));g.appendChild(l); }
  const xl=el("text",{x:X0+PW/2,y:CH-6,fill:"#a7b0ba","font-family":"sans-serif","font-size":13,"text-anchor":"middle","font-weight":700});xl.textContent=feat.label;g.appendChild(xl);
  const yl=el("text",{x:15,y:MT+PH/2,fill:"#a7b0ba","font-family":"sans-serif","font-size":13,"text-anchor":"middle","font-weight":700,"transform":"rotate(-90 15 "+(MT+PH/2)+")"});yl.textContent="count";g.appendChild(yl);
  if(showK){ let d=""; for(let i=0;i<G;i++)d+=(i?"L":"M")+sx(xs[i]).toFixed(1)+" "+sy(dens[i]).toFixed(1);
   g.appendChild(el("path",{d,fill:"none",stroke:"#ffce54","stroke-width":2.5})); }
  ro.innerHTML="n="+n+" · bins="+B+" · bin width="+binW.toFixed(2)+(showK?" · KDE bandwidth h="+hband.toFixed(2):"");
 }
 featSel.addEventListener("change",render); binsS.addEventListener("input",render);
 kdeCb.addEventListener("change",render); bwS.addEventListener("input",render); render();
})();
""".replace("__W__", W_JSON).replace("__H__", H_JSON)

script_bumps = r"""
(function(){
 const svg=document.getElementById("svg-bumps"); if(!svg) return;
 const hS=document.getElementById("bumps-h"), hV=document.getElementById("bumps-h-val");
 const pts=[-2.4,-1.5,-1.1,0.2,0.7,1.0,2.3], n=pts.length;
 const CW=600,CH=220,ML=20,MR=16,MT=14,MB=26,PW=CW-ML-MR,PH=CH-MT-MB,X0=ML,Y0=MT+PH,LO=-4,HI=4;
 const sx=v=>X0+(v-LO)/(HI-LO)*PW;
 function render(){
  const h=+hS.value; hV.textContent=h.toFixed(2);
  const G=200, xs=[], sum=new Array(G).fill(0), bumps=[];
  for(let i=0;i<G;i++)xs.push(LO+(HI-LO)*i/(G-1));
  for(const xi of pts){ const b=[]; for(let i=0;i<G;i++){const u=(xs[i]-xi)/h;
    const v=1/(n*h*Math.sqrt(2*Math.PI))*Math.exp(-0.5*u*u); b.push(v); sum[i]+=v;} bumps.push(b); }
  const ymax=Math.max.apply(null,sum)*1.15, sy=v=>Y0-v/ymax*PH;
  while(svg.firstChild)svg.removeChild(svg.firstChild); const g=el("g"); svg.appendChild(g);
  g.appendChild(el("line",{x1:X0,y1:Y0,x2:X0+PW,y2:Y0,stroke:"#46505c","stroke-width":1.2}));
  for(const b of bumps){ let d=""; for(let i=0;i<G;i++)d+=(i?"L":"M")+sx(xs[i]).toFixed(1)+" "+sy(b[i]).toFixed(1);
   g.appendChild(el("path",{d,fill:"none",stroke:"#6ab0f3","stroke-width":1.2,"stroke-opacity":.7})); }
  let d=""; for(let i=0;i<G;i++)d+=(i?"L":"M")+sx(xs[i]).toFixed(1)+" "+sy(sum[i]).toFixed(1);
  g.appendChild(el("path",{d,fill:"none",stroke:"#ffce54","stroke-width":2.8}));
  for(const xi of pts) g.appendChild(el("line",{x1:sx(xi),y1:Y0,x2:sx(xi),y2:Y0+6,stroke:"#e6e9ec","stroke-width":1.5}));
 }
 hS.addEventListener("input",render); render();
})();
"""

script_gender = r"""
(function(){
 const svg=document.getElementById("svg-gender"); if(!svg) return;
 const HH=__H__, SEX=__SEX__;
 const binsS=document.getElementById("gen-bins"), binsV=document.getElementById("gen-bins-val");
 const bwS=document.getElementById("gen-bw"), bwV=document.getElementById("gen-bw-val"), ro=document.getElementById("gen-ro");
 const CW=600,CH=340,ML=50,MR=18,MT=18,MB=44,PW=CW-ML-MR,PH=CH-MT-MB,X0=ML,Y0=MT+PH;
 const men=[], women=[]; for(let i=0;i<HH.length;i++){(SEX[i]==="M"?men:women).push(HH[i]);}
 function mean(a){let s=0;for(const x of a)s+=x;return s/a.length;}
 function std(a){const m=mean(a);let s=0;for(const x of a)s+=(x-m)*(x-m);return Math.sqrt(s/a.length);}
 function nice(x){const e=Math.pow(10,Math.floor(Math.log10(x)));const f=x/e;return (f<1.5?1:f<3?2:f<7?5:10)*e;}
 function ticks(a,b,m){const st=nice((b-a)/m),t=[];let s=Math.ceil(a/st)*st;for(;s<=b+1e-9;s+=st)t.push(+s.toFixed(6));return t;}
 function kde(arr,xs,h,binW){const n=arr.length,c=1/(n*h*Math.sqrt(2*Math.PI));
  return xs.map(x=>{let s=0;for(const xi of arr){const u=(x-xi)/h;s+=Math.exp(-0.5*u*u);} return c*s*n*binW;});}
 let lo=Math.min.apply(null,HH), hi=Math.max.apply(null,HH); const pad=(hi-lo)*0.04; lo-=pad; hi+=pad;
 function render(){
  const B=+binsS.value; binsV.textContent=B; const bwk=+bwS.value; bwV.textContent=bwk.toFixed(1);
  const binW=(hi-lo)/B, counts=new Array(B).fill(0);
  for(const x of HH){let k=Math.floor((x-lo)/binW); if(k>=B)k=B-1; if(k<0)k=0; counts[k]++;}
  const G=180, xs=[]; for(let i=0;i<G;i++)xs.push(lo+(hi-lo)*i/(G-1));
  const hA=bwk*1.06*std(HH)*Math.pow(HH.length,-0.2), hM=bwk*1.06*std(men)*Math.pow(men.length,-0.2), hW=bwk*1.06*std(women)*Math.pow(women.length,-0.2);
  const dA=kde(HH,xs,hA,binW), dM=kde(men,xs,hM,binW), dW=kde(women,xs,hW,binW);
  let ymax=Math.max(Math.max.apply(null,counts),Math.max.apply(null,dA),Math.max.apply(null,dM),Math.max.apply(null,dW))*1.12;
  const sx=v=>X0+(v-lo)/(hi-lo)*PW, sy=v=>Y0-v/ymax*PH;
  while(svg.firstChild)svg.removeChild(svg.firstChild); const g=el("g"); svg.appendChild(g);
  for(const t of ticks(0,ymax,5)){ if(t>ymax)continue;
   g.appendChild(el("line",{x1:X0,y1:sy(t),x2:X0+PW,y2:sy(t),stroke:"#19212c","stroke-width":1}));
   const l=el("text",{x:X0-8,y:sy(t)+4,fill:"#6b7580","font-family":"sans-serif","font-size":11,"text-anchor":"end"});l.textContent=Math.round(t);g.appendChild(l);}
  for(let i=0;i<B;i++){ if(counts[i]<=0)continue; const x=sx(lo+i*binW),w=PW/B-1,y=sy(counts[i]);
   g.appendChild(el("rect",{x:x+0.5,y,width:Math.max(1,w),height:Y0-y,fill:"#8a929a","fill-opacity":.22,stroke:"#8a929a","stroke-width":0.8})); }
  function curve(d,color,wd){let p="";for(let i=0;i<G;i++)p+=(i?"L":"M")+sx(xs[i]).toFixed(1)+" "+sy(d[i]).toFixed(1);g.appendChild(el("path",{d:p,fill:"none",stroke:color,"stroke-width":wd}));}
  curve(dA,"#ffce54",2.8); curve(dM,"#6ab0f3",2.2); curve(dW,"#e0757f",2.2);
  g.appendChild(el("line",{x1:X0,y1:Y0,x2:X0+PW,y2:Y0,stroke:"#46505c","stroke-width":1.2}));
  g.appendChild(el("line",{x1:X0,y1:MT,x2:X0,y2:Y0,stroke:"#46505c","stroke-width":1.2}));
  for(const t of ticks(lo+pad,hi-pad,6)){ g.appendChild(el("line",{x1:sx(t),y1:Y0,x2:sx(t),y2:Y0+5,stroke:"#46505c","stroke-width":1}));
   const l=el("text",{x:sx(t),y:Y0+18,fill:"#8a929a","font-family":"sans-serif","font-size":11,"text-anchor":"middle"});l.textContent=Math.round(t);g.appendChild(l);}
  const xl=el("text",{x:X0+PW/2,y:CH-6,fill:"#a7b0ba","font-family":"sans-serif","font-size":13,"text-anchor":"middle","font-weight":700});xl.textContent="height (cm)";g.appendChild(xl);
  const yl=el("text",{x:15,y:MT+PH/2,fill:"#a7b0ba","font-family":"sans-serif","font-size":13,"text-anchor":"middle","font-weight":700,"transform":"rotate(-90 15 "+(MT+PH/2)+")"});yl.textContent="count";g.appendChild(yl);
  ro.innerHTML="men: n="+men.length+", mean "+mean(men).toFixed(1)+" cm · women: n="+women.length+", mean "+mean(women).toFixed(1)+" cm";
 }
 binsS.addEventListener("input",render); bwS.addEventListener("input",render); render();
})();
""".replace("__H__", H_JSON).replace("__SEX__", SEX_JSON)

display(HTML(viz(intro)))
display(HTML(viz(figure, script, wide=True)))
display(HTML(viz(after, script_bumps)))
display(HTML(viz(mode_text)))
display(HTML(viz(figure_gender, script_gender, wide=True)))
display(HTML(viz(closing)))''')

# ============================================================================
# 4. ТЕОРИЯ S3 — среднее, дисперсия, стандартное отклонение
# ============================================================================
code(r'''#@title Теория S3 — Среднее, дисперсия, стандартное отклонение { display-mode: "form" }
import json
hgt = df['height'].to_numpy(float)
H_JSON = json.dumps([round(float(v), 1) for v in hgt])
SEX_JSON = json.dumps([str(s) for s in df['sex']])
MEAN_H = repr(round(float(hgt.mean()), 3))

intro = r"""
<h2>3. Среднее, дисперсия и стандартное отклонение</h2>
<p>Гистограмма показала <em>форму</em> распределения. Теперь опишем его двумя числами: где его
<b>центр</b> и насколько велик <b>разброс</b>. Начнём с центра — <b>среднего арифметического</b>
<span class="en">(arithmetic mean)</span>:</p>
$$ \bar x=\frac{1}{n}\sum_{i=1}^{n} x_i. $$
<div class="where">Где:
<ul>
<li>$\bar x$ — выборочное среднее <span class="en">(sample mean)</span>;</li>
<li>$n$ — объём выборки;</li>
<li>$x_i$ — значение $i$-го наблюдения.</li>
</ul></div>
<div class="box idea"><div class="t">Спойлер: математическое ожидание</div>
Выборочное среднее $\bar x$ — оценка теоретического <b>математического ожидания</b>
<span class="en">(expected value)</span> $\mathbb{E}[X]$, то есть параметра $\mu$ всей совокупности.
Строгое определение потребует вероятности и будет дано позже; пока держим в уме, что $\bar x$
приближает $\mu$.</div>
"""

meanmode_text = r"""
<h3>Среднее — это не мода</h3>
<p>Среднее легко спутать с самым частым значением. Но <b>среднее</b> — это точка равновесия, а
<b>мода</b> — вершина распределения, и совпадают они далеко не всегда. Рост в Davis бимодален;
посмотрим, где на нём стоят глобальное среднее и средние по полу.</p>
"""

fig_meanmode = r"""
<div class="widget"><div class="widget-title">Mean vs mode on the height distribution</div>
<div class="widget-sub">Кривые KDE: <span style="color:#6ab0f3">мужчины</span>,
<span style="color:#e0757f">женщины</span>, <span style="color:#ffce54">все вместе</span>.
Пунктир — средние: <span style="color:#ffffff">общее</span>,
<span style="color:#6ab0f3">мужчин</span>, <span style="color:#e0757f">женщин</span>.
Общее среднее попадает во «впадину» между модами — среднее и мода не совпадают.</div>
<svg viewBox="0 0 600 320" id="svg-meanmode"></svg></div>
"""

central_box = r"""
<div class="box def"><div class="t">Меры центральной тенденции</div>
<p style="margin-top:0">Числа, отвечающие на вопрос <b>«где центр распределения»</b> — куда
стягиваются значения признака. Мы разобрали две такие меры:</p>
<table>
<tr><th>Мера</th><th>Обозначение</th><th>Что показывает</th></tr>
<tr><td>Среднее <span class="en">(mean)</span></td><td>$\bar x$</td>
<td>точка равновесия: сумма отклонений от неё равна нулю</td></tr>
<tr><td>Мода <span class="en">(mode)</span></td><td>—</td>
<td>самое частое значение — вершина распределения</td></tr>
</table>
<p style="margin-bottom:0">Как мы видели на бимодальном росте, среднее и мода
<b>не обязаны совпадать</b>.</p>
</div>
"""

varq_text = r"""
<h3>Как измерить разброс? Свойство среднего</h3>
<p>Естественный вопрос: <b>насколько в среднем каждое наблюдение отклоняется от среднего?</b>
Отклонение — это $x_i-\bar x$. Казалось бы, надо просто усреднить все отклонения. Но такая мера
всегда равна нулю:</p>
$$ \frac{1}{n}\sum_{i=1}^{n}(x_i-\bar x)=0 \qquad\Longleftrightarrow\qquad \sum_{i=1}^{n}(x_i-\bar x)=0. $$
<div class="where">Где: $x_i-\bar x$ — отклонение $i$-го наблюдения от среднего. Сумма равна нулю,
потому что положительные и отрицательные отклонения точно компенсируют друг друга. Это
<b>свойство среднего</b>: среднее есть точка равновесия данных.</div>
<details><summary>Для любознательных: почему сумма отклонений равна нулю</summary>
$$ \sum_i (x_i-\bar x)=\sum_i x_i - n\bar x = n\bar x - n\bar x = 0. $$
<div class="where">Где использовано $\sum_i x_i = n\bar x$ прямо из определения среднего.</div>
</details>
<p>Проверим на наших данных: построим гистограмму <em>отклонений</em> роста от среднего. Она
сидит симметрично вокруг нуля, и её собственное среднее равно нулю.</p>
"""

fig_dev = r"""
<div class="widget"><div class="widget-title">Deviations from the mean (height)</div>
<div class="widget-sub">Гистограмма отклонений $x_i-\bar x$ по росту. Белый пунктир — их среднее,
равное нулю: положительные и отрицательные отклонения гасят друг друга.</div>
<svg viewBox="0 0 600 300" id="svg-dev"></svg>
<div class="readout" id="dev-ro"></div></div>
"""

squares_text = r"""
<h3>Как побороть обнуление? Возвести в квадрат</h3>
<p>Отклонения гасят друг друга из-за знаков. Чтобы этого не происходило, отклонения
<b>возводят в квадрат</b> — тогда все слагаемые неотрицательны и уже не сокращаются (заодно
крупные отклонения штрафуются сильнее). Геометрически квадрат отклонения — это буквально
<b>площадь квадрата</b> со стороной $|x_i-\bar x|$.</p>
"""

fig_var = r"""
<div class="widget"><div class="widget-title">Squared deviations as areas</div>
<div class="widget-sub">Небольшой набор для наглядности. Сторона квадрата равна отклонению
$|x_i-\bar x|$, площадь — квадрату отклонения $(x_i-\bar x)^2$; все квадраты неотрицательны
(один знак). Дисперсия — средняя площадь; сторона <span style="color:#ffce54">жёлтого</span>
квадрата равна $\sigma$.</div>
<svg viewBox="0 0 600 300" id="svg-varsq"></svg>
<div class="readout" id="varsq-ro"></div></div>
"""

disp_text = r"""
<h3>Дисперсия и стандартное отклонение</h3>
<p>Средний квадрат отклонения и есть <b>дисперсия</b> <span class="en">(variance)</span> — мера
того, насколько в среднем наблюдения удалены от центра:</p>
$$ \sigma^2=\frac{1}{n}\sum_{i=1}^{n}(x_i-\bar x)^2. $$
<div class="where">Где: $\sigma^2$ — дисперсия; $(x_i-\bar x)^2$ — квадрат отклонения (площадь квадрата);
деление на $n$ даёт среднюю площадь.</div>
<p>У дисперсии есть неудобство <b>размерности</b>: если рост измерен в сантиметрах, то дисперсия —
в сантиметрах <em>в квадрате</em> (см²), что трудно истолковать. Поэтому берут корень и возвращаются
к исходным единицам — получается <b>стандартное отклонение</b>
<span class="en">(standard deviation)</span>:</p>
$$ \sigma=\sqrt{\sigma^2}. $$
<div class="where">Где: $\sigma$ — стандартное отклонение, «типичное» отклонение наблюдения от среднего,
выраженное в тех же единицах, что и сам признак (например, в см).</div>
<div class="box warn"><div class="t">n или n−1</div>
По выборке дисперсию чаще оценивают с делением на $n-1$ (поправка Бесселя
<span class="en">(Bessel's correction)</span>). Поэтому <code>numpy.std</code> (делит на $n$) и
<code>pandas.describe</code> (делит на $n-1$) дают чуть разные числа — это разный выбор знаменателя,
а не ошибка.</div>
"""

spread_box = r"""
<div class="box def"><div class="t">Меры изменчивости</div>
<p style="margin-top:0">Числа, отвечающие на вопрос <b>«насколько широко разбросаны значения»</b>
вокруг центра:</p>
<table>
<tr><th>Мера</th><th>Обозначение</th><th>Формула</th><th>Единицы</th></tr>
<tr><td>Размах <span class="en">(range)</span></td><td>$R$</td>
<td>$x_{\max}-x_{\min}$</td><td>как у признака</td></tr>
<tr><td>Дисперсия <span class="en">(variance)</span></td><td>$\sigma^2,\ s^2$</td>
<td>$\frac1n\sum (x_i-\bar x)^2$</td><td>квадрат единиц</td></tr>
<tr><td>Ст. отклонение <span class="en">(std)</span></td><td>$\sigma,\ s$</td>
<td>$\sqrt{\sigma^2}$</td><td>как у признака</td></tr>
</table>
<p style="margin-bottom:0">Размах смотрит только на две крайние точки, а дисперсия и стандартное
отклонение учитывают <b>все</b> отклонения сразу.</p>
</div>
"""

sigma_std_note = r"""
<div class="box warn"><div class="t" style="text-transform:none">σ или std — путаница обозначений</div>
Стандартное отклонение записывают по-разному, и здесь есть <b>терминологическая путаница</b>.
Греческой буквой $\sigma$ традиционно обозначают <b>истинное</b> отклонение по генеральной
совокупности (параметр), а латинской $s$ или сокращением <code>std</code> — <b>выборочную</b>
оценку. Но соглашение нестрогое: в коде, статьях и библиотеках <code>std</code> сплошь и рядом
пишут и для выборки, и для совокупности. Держи в уме главное: $\sigma$, $s$ и <code>std</code> —
про <b>одну и ту же</b> величину (стандартное отклонение); различается лишь, о выборке идёт речь
или о совокупности, — и даже это соблюдают не всегда.</div>
"""

sse_text = r"""
<h3>Сумма квадратов отклонений (SSE)</h3>
<p>Сумму всех квадратов отклонений (без деления на $n$) называют <b>суммой квадратов отклонений</b>
<span class="en">(sum of squared errors, SSE)</span>:</p>
$$ \mathrm{SSE}(c)=\sum_{i=1}^{n}(x_i-c)^2. $$
<div class="where">Где: $\mathrm{SSE}(c)$ — суммарная квадратичная ошибка при выборе центра $c$;
дисперсия — это $\mathrm{SSE}(\bar x)/n$.</div>
<p>Важное свойство: $\mathrm{SSE}(c)$ минимальна ровно при $c=\bar x$. Значит, среднее — не просто
точка равновесия, а точка, <b>наименее удалённая</b> от всех наблюдений в смысле квадратов. На этом
факте позже вырастут задачи оптимизации и метод наименьших квадратов. Двигайте пробный центр $c$ и
следите за кривой SSE.</p>
"""

fig_sse = r"""
<div class="widget"><div class="widget-title">SSE minimised at the mean</div>
<div class="widget-sub">Перетаскивайте жёлтую линию — пробный центр $c$. Внизу — кривая
$\mathrm{SSE}(c)=\sum(x_i-c)^2$; её минимум приходится ровно на среднее (белый пунктир).</div>
<svg viewBox="0 0 600 330" id="svg-sse"></svg>
<div class="readout" id="sse-ro"></div></div>
"""

closing = r"""
<div class="box take"><div class="t">Итог занятия</div>
<ul>
<li>Центр данных — <b>среднее</b> $\bar x=\frac1n\sum x_i$; оно не обязано совпадать с модой.</li>
<li>Сумма (и среднее) отклонений от среднего равны нулю — <b>свойство среднего</b>.</li>
<li>Чтобы измерить разброс, отклонения возводят в квадрат: <b>дисперсия</b> $\sigma^2$ — средний
квадрат отклонения, <b>стандартное отклонение</b> $\sigma$ — в исходных единицах.</li>
<li><b>SSE</b> минимальна при $c=\bar x$ — среднее наименее удалено от данных (основа оптимизации).</li>
</ul></div>
"""

script_meanmode = r"""
(function(){
 const svg=document.getElementById("svg-meanmode"); if(!svg) return;
 const HH=__H__, SEX=__SEX__;
 const CW=600,CH=320, ML=40,MR=18,MT=18,MB=42, PW=CW-ML-MR,PH=CH-MT-MB,X0=ML,Y0=MT+PH;
 const men=[],women=[]; for(let i=0;i<HH.length;i++){(SEX[i]==="M"?men:women).push(HH[i]);}
 const mean=a=>a.reduce((p,c)=>p+c,0)/a.length;
 const std=a=>{const m=mean(a);return Math.sqrt(a.reduce((p,x)=>p+(x-m)*(x-m),0)/a.length);};
 const nice=x=>{const e=Math.pow(10,Math.floor(Math.log10(x)));const f=x/e;return (f<1.5?1:f<3?2:f<7?5:10)*e;};
 const ticks=(a,b,m)=>{const st=nice((b-a)/m),t=[];let s=Math.ceil(a/st)*st;for(;s<=b+1e-9;s+=st)t.push(+s.toFixed(6));return t;};
 const kde=(arr,xs,h,scale)=>{const n=arr.length,c=1/(n*h*Math.sqrt(2*Math.PI));return xs.map(x=>{let s=0;for(const xi of arr){const u=(x-xi)/h;s+=Math.exp(-0.5*u*u);}return c*s*scale;});};
 let lo=Math.min.apply(null,HH),hi=Math.max.apply(null,HH);const pad=(hi-lo)*0.05;lo-=pad;hi+=pad;
 const sx=v=>X0+(v-lo)/(hi-lo)*PW;
 const G=200,xs=[];for(let i=0;i<G;i++)xs.push(lo+(hi-lo)*i/(G-1));
 const hA=1.06*std(HH)*Math.pow(HH.length,-0.2),hM=1.06*std(men)*Math.pow(men.length,-0.2),hW=1.06*std(women)*Math.pow(women.length,-0.2);
 const dA=kde(HH,xs,hA,1), dM=kde(men,xs,hM,men.length/HH.length), dW=kde(women,xs,hW,women.length/HH.length);
 const ymax=Math.max(Math.max.apply(null,dA),Math.max.apply(null,dM),Math.max.apply(null,dW))*1.2;
 const sy=v=>Y0-v/ymax*PH;
 const g=el("g"); svg.appendChild(g);
 g.appendChild(el("line",{x1:X0,y1:Y0,x2:X0+PW,y2:Y0,stroke:"#46505c","stroke-width":1.2}));
 for(const t of ticks(lo+pad,hi-pad,6)){g.appendChild(el("line",{x1:sx(t),y1:Y0,x2:sx(t),y2:Y0+5,stroke:"#46505c"}));
   const l=el("text",{x:sx(t),y:Y0+18,fill:"#8a929a","font-family":"sans-serif","font-size":11,"text-anchor":"middle"});l.textContent=Math.round(t);g.appendChild(l);}
 const curve=(d,col,wd)=>{let p="";for(let i=0;i<G;i++)p+=(i?"L":"M")+sx(xs[i]).toFixed(1)+" "+sy(d[i]).toFixed(1);g.appendChild(el("path",{d:p,fill:"none",stroke:col,"stroke-width":wd}));};
 curve(dM,"#6ab0f3",2); curve(dW,"#e0757f",2); curve(dA,"#ffce54",2.8);
 const mAll=mean(HH),mM=mean(men),mW=mean(women);
 const vline=(x,col,lab,dy)=>{g.appendChild(el("line",{x1:sx(x),y1:MT,x2:sx(x),y2:Y0,stroke:col,"stroke-width":1.8,"stroke-dasharray":"6 4"}));
   const t=el("text",{x:sx(x),y:MT+dy,fill:col,"font-family":"sans-serif","font-size":11,"text-anchor":"middle","font-weight":700});t.textContent=lab;g.appendChild(t);};
 vline(mM,"#6ab0f3","x̄ М "+mM.toFixed(0),12);
 vline(mW,"#e0757f","x̄ Ж "+mW.toFixed(0),12);
 vline(mAll,"#ffffff","x̄ общее "+mAll.toFixed(0),28);
 const xl=el("text",{x:X0+PW/2,y:CH-6,fill:"#a7b0ba","font-family":"sans-serif","font-size":13,"text-anchor":"middle","font-weight":700});xl.textContent="height (cm)";g.appendChild(xl);
})();
""".replace("__H__", H_JSON).replace("__SEX__", SEX_JSON)

script_dev = r"""
(function(){
 const svg=document.getElementById("svg-dev"); if(!svg) return;
 const HH=__H__, MH=__MEAN__; const ro=document.getElementById("dev-ro");
 const dev=HH.map(x=>x-MH);
 const CW=600,CH=300, ML=44,MR=18,MT=18,MB=42, PW=CW-ML-MR,PH=CH-MT-MB,X0=ML,Y0=MT+PH;
 const nice=x=>{const e=Math.pow(10,Math.floor(Math.log10(x)));const f=x/e;return (f<1.5?1:f<3?2:f<7?5:10)*e;};
 const ticks=(a,b,m)=>{const st=nice((b-a)/m),t=[];let s=Math.ceil(a/st)*st;for(;s<=b+1e-9;s+=st)t.push(+s.toFixed(6));return t;};
 let hiA=0; for(const d of dev) hiA=Math.max(hiA,Math.abs(d)); const A=hiA*1.1, lo=-A, hi=A;
 const B=20, binW=(hi-lo)/B, counts=new Array(B).fill(0);
 for(const x of dev){let k=Math.floor((x-lo)/binW);if(k>=B)k=B-1;if(k<0)k=0;counts[k]++;}
 const ymax=Math.max.apply(null,counts)*1.15;
 const sx=v=>X0+(v-lo)/(hi-lo)*PW, sy=v=>Y0-v/ymax*PH;
 const g=el("g"); svg.appendChild(g);
 for(const t of ticks(0,ymax,5)){if(t>ymax)continue; g.appendChild(el("line",{x1:X0,y1:sy(t),x2:X0+PW,y2:sy(t),stroke:"#19212c","stroke-width":1}));
   const l=el("text",{x:X0-8,y:sy(t)+4,fill:"#6b7580","font-family":"sans-serif","font-size":11,"text-anchor":"end"});l.textContent=Math.round(t);g.appendChild(l);}
 for(let i=0;i<B;i++){if(counts[i]<=0)continue;const x=sx(lo+i*binW),w=PW/B-1,y=sy(counts[i]);
   g.appendChild(el("rect",{x:x+0.5,y,width:Math.max(1,w),height:Y0-y,fill:"#6ab0f3","fill-opacity":.42,stroke:"#6ab0f3","stroke-width":1}));}
 g.appendChild(el("line",{x1:X0,y1:Y0,x2:X0+PW,y2:Y0,stroke:"#46505c","stroke-width":1.2}));
 for(const t of ticks(lo,hi,6)){g.appendChild(el("line",{x1:sx(t),y1:Y0,x2:sx(t),y2:Y0+5,stroke:"#46505c"}));
   const l=el("text",{x:sx(t),y:Y0+18,fill:"#8a929a","font-family":"sans-serif","font-size":11,"text-anchor":"middle"});l.textContent=(t>0?"+":"")+Math.round(t);g.appendChild(l);}
 g.appendChild(el("line",{x1:sx(0),y1:MT,x2:sx(0),y2:Y0,stroke:"#ffffff","stroke-width":1.8,"stroke-dasharray":"6 4"}));
 const zt=el("text",{x:sx(0),y:MT+12,fill:"#ffffff","font-family":"sans-serif","font-size":11,"text-anchor":"middle","font-weight":700});zt.textContent="среднее отклонение = 0";g.appendChild(zt);
 const xl=el("text",{x:X0+PW/2,y:CH-6,fill:"#a7b0ba","font-family":"sans-serif","font-size":13,"text-anchor":"middle","font-weight":700});xl.textContent="deviation from mean (cm)";g.appendChild(xl);
 const yl=el("text",{x:15,y:MT+PH/2,fill:"#a7b0ba","font-family":"sans-serif","font-size":13,"text-anchor":"middle","font-weight":700,"transform":"rotate(-90 15 "+(MT+PH/2)+")"});yl.textContent="count";g.appendChild(yl);
 const sumdev=dev.reduce((a,b)=>a+b,0);
 ro.innerHTML="n="+HH.length+" · сумма отклонений Σ(xᵢ−x̄) = "+sumdev.toFixed(1)+" ≈ 0 · среднее отклонение = 0";
})();
""".replace("__H__", H_JSON).replace("__MEAN__", MEAN_H)

script_v2 = r"""
(function(){
 const svg=document.getElementById("svg-varsq"); if(!svg) return;
 const ro=document.getElementById("varsq-ro");
 const data=[54,58,60,63,65,67,70,73,80], n=data.length;
 const mean=data.reduce((a,b)=>a+b,0)/n;
 const varp=data.reduce((s,x)=>s+(x-mean)*(x-mean),0)/n, sd=Math.sqrt(varp);
 const CW=600, ML=30,MR=16, LO=45,HI=92, AXY=252, PW=CW-ML-MR, X0=ML, pxu=PW/(HI-LO);
 const sx=v=>X0+(v-LO)*pxu;
 const g=el("g"); svg.appendChild(g);
 g.appendChild(el("line",{x1:X0,y1:AXY,x2:X0+PW,y2:AXY,stroke:"#46505c","stroke-width":1.2}));
 for(let t=50;t<=90;t+=10){g.appendChild(el("line",{x1:sx(t),y1:AXY,x2:sx(t),y2:AXY+5,stroke:"#46505c"}));
  const l=el("text",{x:sx(t),y:AXY+18,fill:"#8a929a","font-family":"sans-serif","font-size":11,"text-anchor":"middle"});l.textContent=t;g.appendChild(l);}
 data.forEach(x=>{const side=Math.abs(x-mean)*pxu, x0=Math.min(sx(x),sx(mean));
  g.appendChild(el("rect",{x:x0,y:AXY-side,width:side,height:side,fill:"#6ab0f3","fill-opacity":.22,stroke:"#6ab0f3","stroke-width":1}));
  g.appendChild(el("circle",{cx:sx(x),cy:AXY,r:3.5,fill:"#5fd08a"}));});
 g.appendChild(el("line",{x1:sx(mean),y1:40,x2:sx(mean),y2:AXY,stroke:"#ffffff","stroke-width":1.5,"stroke-dasharray":"5 4"}));
 const t1=el("text",{x:sx(mean),y:34,fill:"#ffffff","font-family":"sans-serif","font-size":11,"text-anchor":"middle"});t1.textContent="среднее x̄";g.appendChild(t1);
 const ss=sd*pxu;
 g.appendChild(el("rect",{x:sx(mean),y:AXY-ss,width:ss,height:ss,fill:"none",stroke:"#ffce54","stroke-width":2.5}));
 const t2=el("text",{x:sx(mean)+ss+6,y:AXY-ss+12,fill:"#ffce54","font-family":"sans-serif","font-size":11,"text-anchor":"start"});t2.textContent="сторона = σ";g.appendChild(t2);
 ro.innerHTML="дисперсия σ² = средняя площадь квадратов = "+varp.toFixed(1)+" · σ = √σ² = "+sd.toFixed(2);
})();
"""

script_sse = r"""
(function(){
 const svg=document.getElementById("svg-sse"); if(!svg) return;
 const ro=document.getElementById("sse-ro");
 const data=[54,58,60,63,65,67,70,73,80], n=data.length;
 const mean=data.reduce((a,b)=>a+b,0)/n;
 const CW=600, ML=44,MR=16, LO=45,HI=92, TY=34,TH=118, PY=214,PH=92, PW=CW-ML-MR, X0=ML;
 const sx=v=>X0+(v-LO)/(HI-LO)*PW;
 const sse=cc=>{let s=0;for(const x of data)s+=(x-cc)*(x-cc);return s;};
 const sumdev=cc=>{let s=0;for(const x of data)s+=(x-cc);return s;};
 const sseMax=Math.max(sse(LO),sse(HI)), py=v=>PY+PH - v/sseMax*PH;
 let c=(LO+HI)/2;
 function T(g,x,y,s,col,anc){const t=el("text",{x,y,fill:col||"#a7b0ba","font-family":"sans-serif","font-size":11,"text-anchor":anc||"start"});t.textContent=s;g.appendChild(t);}
 function render(){
  while(svg.firstChild)svg.removeChild(svg.firstChild); const g=el("g"); svg.appendChild(g);
  g.appendChild(el("line",{x1:X0,y1:TY+TH,x2:X0+PW,y2:TY+TH,stroke:"#46505c","stroke-width":1.2}));
  for(let t=50;t<=90;t+=10){g.appendChild(el("line",{x1:sx(t),y1:TY+TH,x2:sx(t),y2:TY+TH+5,stroke:"#46505c"}));T(g,sx(t),TY+TH+17,t,"#8a929a","middle");}
  g.appendChild(el("line",{x1:sx(mean),y1:TY-4,x2:sx(mean),y2:TY+TH,stroke:"#ffffff","stroke-width":1,"stroke-dasharray":"2 3","stroke-opacity":.5}));
  data.forEach((x,i)=>{const yy=TY+12+i*((TH-24)/(n-1));
   g.appendChild(el("line",{x1:sx(x),y1:yy,x2:sx(c),y2:yy,stroke:"#6ab0f3","stroke-width":1.5,"stroke-opacity":.6}));
   g.appendChild(el("circle",{cx:sx(x),cy:yy,r:3.5,fill:"#5fd08a"}));});
  g.appendChild(el("line",{x1:sx(c),y1:TY-8,x2:sx(c),y2:TY+TH,stroke:"#ffce54","stroke-width":2,"stroke-dasharray":"5 4"}));
  const hnd=el("circle",{cx:sx(c),cy:TY-8,r:8,fill:"#ffce54","fill-opacity":.3,stroke:"#ffce54","stroke-width":2}); g.appendChild(hnd);
  onDrag(svg,hnd,q=>{c=clamp(LO+(q.x-X0)/PW*(HI-LO),LO,HI); render();});
  T(g,sx(c),TY-14,"c","#ffce54","middle");
  g.appendChild(el("line",{x1:X0,y1:PY+PH,x2:X0+PW,y2:PY+PH,stroke:"#46505c","stroke-width":1.2}));
  let d=""; for(let i=0;i<=120;i++){const cc=LO+(HI-LO)*i/120; d+=(i?"L":"M")+sx(cc).toFixed(1)+" "+py(sse(cc)).toFixed(1);}
  g.appendChild(el("path",{d,fill:"none",stroke:"#6ab0f3","stroke-width":2}));
  g.appendChild(el("line",{x1:sx(mean),y1:PY-4,x2:sx(mean),y2:PY+PH,stroke:"#ffffff","stroke-width":1,"stroke-dasharray":"2 3","stroke-opacity":.5}));
  g.appendChild(el("circle",{cx:sx(c),cy:py(sse(c)),r:4,fill:"#ffce54"}));
  T(g,X0+4,PY-6,"SSE(c) = Σ(xᵢ − c)²","#6ab0f3","start");
  ro.innerHTML="c="+c.toFixed(1)+" · SSE(c)="+sse(c).toFixed(0)+" · минимум при c=x̄="+mean.toFixed(2)+" (там же Σ(xᵢ−c)=0)";
 }
 render();
})();
"""

display(HTML(viz(intro)))
display(HTML(viz(meanmode_text)))
display(HTML(viz(fig_meanmode, script_meanmode, wide=True)))
display(HTML(viz(central_box)))
display(HTML(viz(varq_text)))
display(HTML(viz(fig_dev, script_dev, wide=True)))
display(HTML(viz(squares_text)))
display(HTML(viz(fig_var, script_v2, wide=True)))
display(HTML(viz(disp_text)))
display(HTML(viz(spread_box)))
display(HTML(viz(sigma_std_note)))
display(HTML(viz(sse_text)))
display(HTML(viz(fig_sse, script_sse, wide=True)))
display(HTML(viz(closing)))''')

# ============================================================================
# 4. ПРАКТИКА S1–S3 — гайд по инструментам + задания
# ============================================================================
md(r"""## Инструменты: считаем статистику в `numpy` и `pandas`

Датафрейм `df` уже загружен. Ниже — короткая шпаргалка по инструментам, которые понадобятся в заданиях. Всё, что мы считали руками, в библиотеках уже есть; наша задача — уметь это вызвать и, главное, **сверить** библиотечный результат с ручным счётом и **истолковать** его.

### Описательные статистики

```python
df.describe()                # сводка по всем числовым признакам сразу
df['height'].mean()          # среднее
df['height'].std()           # стандартное отклонение (ddof=1 → делит на n−1)
df['height'].var()           # дисперсия (ddof=1)
df['height'].min(), df['height'].max()   # для размаха: max − min

import numpy as np
np.mean(df['height'])
np.std(df['height'])         # по умолчанию ddof=0 → делит на n
np.std(df['height'], ddof=1) # то же, что pandas
```
> **Про `ddof`.** `np.std`/`np.var` по умолчанию делят на $n$, а `pandas` — на $n-1$ (поправка Бесселя). Отсюда расхождение в последних цифрах — это разный знаменатель, а не ошибка.

### Статистики по группам

```python
df.groupby('sex')['height'].describe()               # сводка отдельно для M и F
df.groupby('sex')['height'].std()                    # только std по группам
df.groupby('sex')['height'].agg(['mean', 'std', 'min', 'max'])
```

### Распределения, гистограммы, KDE

```python
import matplotlib.pyplot as plt
import seaborn as sns

sns.histplot(data=df, x='height', bins=20)                # гистограмма
sns.histplot(data=df, x='height', hue='sex', kde=True)    # с разбивкой по полу + KDE
sns.kdeplot(data=df, x='height', hue='sex', fill=True)    # только сглаженные плотности
plt.show()
```

### Двумерная KDE: линии уровня и центроиды

```python
ax = sns.kdeplot(data=df, x='height', y='weight', hue='sex')  # линии уровня плотности
# центроид группы — это точка (среднее по X, среднее по Y)
cent = df.groupby('sex')[['height', 'weight']].mean()
ax.scatter(cent['height'], cent['weight'],
           c='black', s=140, marker='X', zorder=5)             # центроиды поверх
plt.show()
```
Линии уровня двумерной KDE показывают, где облако точек **гуще**; центроид — «центр тяжести» группы в пространстве двух признаков (тот самый вектор-центроид $\bar x$ из блока про совокупность и выборку).
""")

md("""### Задания

Выполняй каждое задание в пустой ячейке под ним. Везде, где считаешь что-то руками, **сверяй** результат с библиотечным; к графикам пиши **вывод словами**, а не только код.""")

md("""**Task 1.** Выведи сводку `df.describe()` по всем числовым признакам. Затем для признака `height` посчитай среднее, дисперсию и стандартное отклонение **вручную через numpy** (по формулам из теории S3) и сверь их со значениями из `df.describe()`, `df['height'].std()` и `df['height'].var()`. Если `std`/`var` расходятся в последних цифрах — объясни почему (подумай про `ddof`).""")
code("")

md("""**Task 2.** Посчитай размах (`max − min`) отдельно для `height` и для `weight`. У какого из двух признаков разброс «шире» по размаху? Совпадает ли этот вывод с тем, что говорит стандартное отклонение? Прокомментируй.""")
code("")

md("""**Task 3.** Построй гистограмму признака `height` и наложи на неё KDE. Затем построй KDE того же признака с разбивкой по полу (`hue='sex'`). Опиши словами: распределение одномодальное или бимодальное, симметрично ли оно, чем отличаются мужская и женская группы.""")
code("")

md("""**Task 4.** Построй двумерную KDE по (`height`, `weight`) с разбивкой по полу — линии уровня плотности. Поверх нанеси центроид каждой группы — точку (`mean_height`, `mean_weight`). Прокомментируй: где расположены центры групп, как вытянуты и как смещены облака точек.""")
code("")

md("""**Task 5.** По графикам из Task 3 и Task 4 предположи, у какой группы (M или F) больше изменчивость роста. Затем подтверди догадку **численно**: посчитай std роста по группам через `df.groupby('sex')['height'].std()` и сравни результат со своим предположением.""")
code("")

# ============================================================================
# 5. ТЕОРИЯ S4 — нормирование и z-стандартизация
# ============================================================================
code(r'''#@title Теория S4 — Нормирование и z-стандартизация { display-mode: "form" }
import json
W_JSON = json.dumps([round(float(v), 1) for v in df['weight']])
H_JSON = json.dumps([round(float(v), 1) for v in df['height']])

intro = r"""
<h2>4. Нормирование и z-стандартизация</h2>
<p>Мы описали признак центром и разбросом. Но как только признаков <em>несколько</em>, всплывает
новая беда: они измерены в <b>разных единицах и разных масштабах</b>. Рост в сантиметрах, вес в
килограммах, доход в тысячах — складывать и сравнивать их напрямую нельзя. Лекарство называется
<b>нормированием</b>.</p>

<div class="box idea"><div class="t">Нормирование вы делаете всю жизнь</div>
Нормирование — это <b>приведение несравнимого к общей единице и шкале</b>.
<ul>
<li>Рабочий A сделал 100 деталей за 8 часов, B — 70 за 5 часов. Сырые 100 и 70 несравнимы — разное
время. Делим на общий знаменатель → детали <b>в час</b>: 12.5 против 14, и теперь видно, что B
производительнее.</li>
<li>Зарплаты разных стран сравнивают, переведя в одну валюту; цены разных лет — «в ценах 2020 года»
(поправка на инфляцию).</li>
</ul>
Везде одно и то же: убрать произвол единиц, чтобы величины встали на общую шкалу.</div>

<p>У нормирования есть ступени — от бытовой к статистической:</p>
<ol>
<li><b>Общая единица / темп</b>: делим на знаменатель (детали в час, цена за кг, доход на душу).</li>
<li><b>Курс / инфляция</b>: переводим в общую валюту или «в цены такого-то года».</li>
<li><b>z-стандартизация</b>: центрируем и делим на разброс — самое интересное, к нему и переходим.</li>
</ol>
<p>Разница третьей ступени от первых двух: там знаменатель <b>внешний</b> (часы, кг дал нам мир),
а у z знаменатель <b>добыт из самих данных</b> — это стандартное отклонение $\sigma$ признака.</p>
"""

zdef = r"""
<h3>z-оценка: центр вычесть, на разброс поделить</h3>
<p>Чтобы сделать признаки сопоставимыми, каждое значение переводят в <b>z-оценку</b>
<span class="en">(z-score, standard score)</span> в два шага:</p>
$$ z_i=\frac{x_i-\bar x}{\sigma}. $$
<div class="where">Где:
<ul>
<li>$x_i-\bar x$ — <b>центрирование</b>: начало отсчёта сдвигаем в среднее (центроид едет в ноль);</li>
<li>деление на $\sigma$ — <b>масштабирование</b>: меряем отклонение в единицах стандартного отклонения.</li>
</ul></div>
<p>После стандартизации у признака <b>среднее 0 и стандартное отклонение 1</b>, и он становится
<b>безразмерным</b> — единицы (см, кг) сокращаются. Теперь рост и вес живут на одной шкале, их можно
честно сравнивать и складывать.</p>
<div class="box warn"><div class="t">Зачем это для ML</div>
В сыром евклидовом расстоянии каждый признак весит «единицу за свою единицу», поэтому признак с
большим разбросом <b>задавит</b> признак с малым. Пример: у X среднее 50 и $\sigma=2$, у Y среднее 50
и $\sigma=40$ — без стандартизации расстояние между наблюдениями почти целиком определяется одним Y.
z уравнивает вклад признаков.</div>
"""

l2bridge = r"""
<div class="box idea"><div class="t">Мост к L2-норме: это то же нормирование</div>
<p style="margin-top:0">Вспомним уроки про векторы. Раньше мы нормировали <b>наблюдение</b> — строку.
Теперь возьмём <b>столбец-признак</b> $x=(x_1,\dots,x_n)$, вычтем среднее и получим <b>вектор
отклонений</b> $x-\bar x$ — вектор, где каждая координата показывает, на сколько наблюдение
отклонилось от центра. Его L2-норма (корень из суммы квадратов отклонений) — это ровно то, что
стояло под знаком суммы в дисперсии:</p>
$$ \sigma^2=\frac1n\sum_i (x_i-\bar x)^2=\frac1n\lVert x-\bar x\rVert^2 \;\Rightarrow\;
   \sigma=\frac{\lVert x-\bar x\rVert}{\sqrt n}. $$
<p>Подставим это в формулу z:</p>
$$ z=\frac{x-\bar x}{\sigma}=\sqrt n\,\frac{x-\bar x}{\lVert x-\bar x\rVert}. $$
<p style="margin-bottom:0">То есть <b>z-стандартизация = центрирование + L2-нормирование вектора
отклонений</b> (с точностью до множителя $\sqrt n$, который добивает $\sigma$ ровно до 1). Тот же
аппарат нормы из первых уроков — просто применённый к центрированному признаку.</p>
</div>
"""

l2contrast = r"""
<div class="box def"><div class="t">Не путать: L2 наблюдения ≠ z-стандартизация</div>
<p style="margin-top:0">И там, и там мы делим на L2-норму — но нормируем <b>разные объекты и
по-разному</b>. В уроках 01–02 нормировали <b>строку-наблюдение</b> без центрирования; здесь —
<b>центрированный столбец-признак</b>.</p>
<table>
<tr><th></th><th>L2 наблюдения (01–02)</th><th>z-стандартизация признака (сейчас)</th></tr>
<tr><td>Что берём</td><td>строку — точку в пространстве признаков</td><td>столбец-признак</td></tr>
<tr><td>Центрируем?</td><td>нет</td><td>да, вычитаем $\bar x$</td></tr>
<tr><td>Делим на</td><td>$\lVert v\rVert$ — свою норму</td><td>$\sigma=\lVert x-\bar x\rVert/\sqrt n$</td></tr>
<tr><td>Итог</td><td>единичный вектор (длина 1)</td><td>среднее 0, $\sigma=1$</td></tr>
<tr><td>Что убираем</td><td>«громкость», остаётся направление</td><td>единицы и масштаб признака</td></tr>
<tr><td>Работает с</td><td>косинусом (похожесть направлений)</td><td>расстоянием (честный вклад признаков)</td></tr>
</table>
<p style="margin-bottom:0"><b>Коротко:</b> L2 наблюдения выкидывает длину и оставляет направление;
z выкидывает единицы признака и оставляет структуру распределения. Разные оси — разные цели.</p>
</div>
"""

space_transform = r"""
<details><summary>z как преобразование признакового пространства (для любознательных)</summary>
<p>z-стандартизацию можно прочитать как <b>аффинное преобразование</b> всего пространства признаков,
одно и то же для всех наблюдений:</p>
$$ T(v)=D^{-1}(v-\mu),\qquad D=\operatorname{diag}(\sigma_1,\dots,\sigma_p),\quad
   \mu=(\bar x_1,\dots,\bar x_p). $$
<p>Два действия: <b>сдвиг</b> (вычли вектор средних $\mu$ — центроид едет в начало координат) и
<b>диагональное масштабирование</b> (каждую ось $j$ делим на свой $\sigma_j$). Облако становится
«круглее» — по каждой оси разброс равен 1. Это уже тема «матрица как оператор»: z — применение
диагонального оператора $D^{-1}$ со сдвигом к каждой точке. Замечание: z уравнивает дисперсию
<em>по осям</em>, но <b>не убирает корреляции</b> между признаками (наклон облака остаётся) — это
сделает позже «отбеливание» через собственные векторы в PCA.</p>
<p><b>Что это даёт евклиду.</b> После z расстояние становится взвешенным, с весами $1/\sigma_j^2$:</p>
$$ d_z(a,b)=\sqrt{\textstyle\sum_j \big((a_j-b_j)/\sigma_j\big)^2}. $$
<p>Вклад каждого признака поделён на его дисперсию — все на равных (это «диагональная» версия
расстояния Махаланобиса). Тонкость: <b>сдвиг не меняет расстояний</b> (перенос — изометрия), всю
работу делает масштабирование $1/\sigma_j$.</p>
<p><b>Что это ломает у косинуса.</b> Косинус меряет угол <em>от начала координат</em> и потому
критически зависит от того, где стоит ноль. z делает две вещи: (1) центрирование <b>двигает ноль</b>
в центроид — косинус после z меряет «направление относительно центра», а не исходное направление;
(2) диагональное масштабирование <b>наклоняет</b> векторы (разные $\sigma_j$ по осям угол не
сохраняют). Поэтому косинус живёт в паре с <b>L2-нормированием сырого наблюдения</b>, где ноль
осмыслен (счётчики, TF-IDF, эмбеддинги). Гонять z перед косинусом обычно не нужно.</p>
<table>
<tr><th>Метрика</th><th>Про что</th><th>Своя нормировка</th><th>Почему</th></tr>
<tr><td>Евклид</td><td>разрывы между точками</td><td>z-стандартизация</td>
<td>инвариантен к сдвигу, чувствителен к масштабу осей → σ уравнивает</td></tr>
<tr><td>Косинус</td><td>угол/направление от нуля</td><td>L2 сырого наблюдения</td>
<td>чувствителен к нулю → центрирование в z ломает точку отсчёта</td></tr>
</table>
<p style="margin-bottom:0"><b>Одной строкой:</b> z «настроен» под евклид (делает вклад признаков
честным), а косинусу нужен неподвижный осмысленный ноль, который центрирование как раз убирает.</p>
</details>
"""

figure = r"""
<div class="widget"><div class="widget-title">Davis: до и после стандартизации</div>
<div class="widget-sub">Слева — сырые данные (вес в кг, рост в см): оси в разных единицах и разного
масштаба, облако смещено от начала координат. Справа — те же точки после z-стандартизации: обе оси
в единицах $\sigma$, центроид (<span style="color:#ffce54">жёлтый крест</span>) сидит в нуле, разброс
по каждой оси равен 1. Форма облака та же — изменились <b>единицы и центр</b>.</div>
<svg viewBox="0 0 600 320" id="svg-zstd"></svg>
<div class="readout" id="zstd-ro"></div></div>
"""

costidea = r"""
<h3>σ — это «цена» единичного отрезка</h3>
<p>После стандартизации мы меряем <b>в единицах σ</b>: один шаг по $z$ равен одному $\sigma$ в сырых
единицах. Значит сырой шаг $\Delta x$ превращается в $\Delta z=\Delta x/\sigma$ — <b>курс обмена</b>
«сырые единицы → σ-единицы» равен $1/\sigma$, и его выставляет само распределение своим разбросом.</p>
<div class="box def"><div class="t">Чем однороднее признак, тем дороже его единичный отрезок</div>
<p style="margin-top:0">Возьмём разрыв в <b>4 сырые единицы</b> у двух признаков:</p>
<table>
<tr><th>Признак</th><th>$\sigma$</th><th>4 единицы в σ</th><th>в z-оценке</th><th>«цена» шага</th></tr>
<tr><td>A (тесный)</td><td>2</td><td>$4/2=2\sigma$</td><td>2.0</td><td>дорого, весомо</td></tr>
<tr><td>B (широкий)</td><td>40</td><td>$4/40=0.1\sigma$</td><td>0.1</td><td>дёшево, почти шум</td></tr>
</table>
<p style="margin-bottom:0">Один и тот же сырой разрыв «много значит» в тесном A и «почти ничего» в
широком B. z <b>уравнивает валюту</b>: оценивает каждый разрыв в σ, а обменный курс $1/\sigma$ задаёт
разнообразие признака. Чем меньше разброс — тем «крепче» σ-валюта и <b>дороже</b> единичный шаг.</p></div>
<p>Так стандартизация <b>демократизирует</b> признаки: тесный получает такое же право голоса в
расстоянии, как широкий — вклад теперь пропорционален тому, на сколько σ отклонилось наблюдение, а не
произволу единиц.</p>
<details><summary>Тонкость на будущее</summary>
«Тесный признак → дорогой шаг» — это про <b>цену единичного отрезка</b>, а не про то, что тесный
признак «информативнее». Позже в PCA логика на уровне <em>направлений</em> будет обратной: большая
дисперсия там — это сигнал. Пока держим в уме только курс обмена $1/\sigma$.</details>
"""

cosine_spoiler = r"""
<div class="box idea"><div class="t">Спойлер: косинус вернётся корреляцией</div>
Центрирование — первый шаг z — это ровно та операция, после которой <b>косинус</b> из урока про
скалярное произведение превращается в коэффициент корреляции: для двух центрированных признаков
$$ \cos\angle(x-\bar x,\;y-\bar y)=r_{XY}. $$
Тот самый косинус, что мерил похожесть наблюдений, применённый к центрированным столбцам, окажется
<b>корреляцией</b> признаков. Разберём подробно, когда дойдём до ковариации.</div>
"""

closing = r"""
<div class="box take"><div class="t">Итог блока</div>
<ul>
<li><b>Нормирование</b> — приведение признаков к общей единице и шкале; z — его статистическая
ступень, где знаменатель добыт из самих данных.</li>
<li><b>z-оценка</b> $z=(x-\bar x)/\sigma$: центрирование + масштабирование; после неё среднее 0,
$\sigma=1$, признак безразмерен.</li>
<li>z-стандартизация = центрирование + <b>L2-нормирование</b> вектора отклонений:
$\sigma=\lVert x-\bar x\rVert/\sqrt n$.</li>
<li>σ — <b>цена</b> единичного отрезка: курс обмена $1/\sigma$; чем меньше разброс, тем дороже шаг.</li>
</ul></div>
"""

script = r"""
(function(){
 const svg=document.getElementById("svg-zstd"); if(!svg) return;
 const W=__W__, H=__H__, ro=document.getElementById("zstd-ro");
 const mean=a=>a.reduce((p,c)=>p+c,0)/a.length;
 const std=a=>{const m=mean(a);return Math.sqrt(a.reduce((p,x)=>p+(x-m)*(x-m),0)/a.length);};
 const q=(a,p)=>{const s=[...a].sort((x,y)=>x-y);return s[Math.floor(p*(s.length-1))];};
 const nice=x=>{const e=Math.pow(10,Math.floor(Math.log10(x)));const f=x/e;return (f<1.5?1:f<3?2:f<7?5:10)*e;};
 const ticks=(a,b,m)=>{const st=nice((b-a)/m),t=[];let s=Math.ceil(a/st)*st;for(;s<=b+1e-9;s+=st)t.push(+s.toFixed(6));return t;};
 const mW=mean(W), sW=std(W), mH=mean(H), sH=std(H);
 const PW=210, PH=210, PT=44, LOX=54, ROX=354;

 function panel(ox, xs, ys, xlo, xhi, ylo, yhi, xt, yt, xlab, ylab, title, cx, cy, zero){
  const sx=v=>ox+(v-xlo)/(xhi-xlo)*PW;
  const sy=v=>PT+PH-(v-ylo)/(yhi-ylo)*PH;
  const g=el("g"); svg.appendChild(g);
  g.appendChild(el("rect",{x:ox,y:PT,width:PW,height:PH,fill:"#0b0f14",stroke:"#2a313b","stroke-width":1}));
  for(const t of xt){ const z0=(zero&&Math.abs(t)<1e-9);
   g.appendChild(el("line",{x1:sx(t),y1:PT,x2:sx(t),y2:PT+PH,stroke:z0?"#46505c":"#19212c","stroke-width":z0?1.4:1}));
   const la=el("text",{x:sx(t),y:PT+PH+14,fill:"#6b7580","font-family":"sans-serif","font-size":10,"text-anchor":"middle"});la.textContent=t;g.appendChild(la);}
  for(const t of yt){ const z0=(zero&&Math.abs(t)<1e-9);
   g.appendChild(el("line",{x1:ox,y1:sy(t),x2:ox+PW,y2:sy(t),stroke:z0?"#46505c":"#19212c","stroke-width":z0?1.4:1}));
   const lb=el("text",{x:ox-6,y:sy(t)+3,fill:"#6b7580","font-family":"sans-serif","font-size":10,"text-anchor":"end"});lb.textContent=t;g.appendChild(lb);}
  for(let i=0;i<xs.length;i++){ const px=sx(xs[i]),py=sy(ys[i]);
   if(px<ox||px>ox+PW||py<PT||py>PT+PH) continue;
   g.appendChild(el("circle",{cx:px,cy:py,r:2.2,fill:"#6ab0f3","fill-opacity":.55}));}
  const cpx=sx(cx),cpy=sy(cy);
  g.appendChild(el("line",{x1:cpx-8,y1:cpy,x2:cpx+8,y2:cpy,stroke:"#0b0f14","stroke-width":5,"stroke-linecap":"round"}));
  g.appendChild(el("line",{x1:cpx,y1:cpy-8,x2:cpx,y2:cpy+8,stroke:"#0b0f14","stroke-width":5,"stroke-linecap":"round"}));
  g.appendChild(el("line",{x1:cpx-8,y1:cpy,x2:cpx+8,y2:cpy,stroke:"#ffce54","stroke-width":2.6,"stroke-linecap":"round"}));
  g.appendChild(el("line",{x1:cpx,y1:cpy-8,x2:cpx,y2:cpy+8,stroke:"#ffce54","stroke-width":2.6,"stroke-linecap":"round"}));
  const tt=el("text",{x:ox,y:PT-24,fill:"#e6e9ec","font-family":"sans-serif","font-size":13,"font-weight":700});tt.textContent=title;g.appendChild(tt);
  const xl=el("text",{x:ox+PW/2,y:PT+PH+30,fill:"#a7b0ba","font-family":"sans-serif","font-size":11,"text-anchor":"middle"});xl.textContent=xlab;g.appendChild(xl);
  const yl=el("text",{x:ox-40,y:PT+PH/2,fill:"#a7b0ba","font-family":"sans-serif","font-size":11,"text-anchor":"middle","transform":"rotate(-90 "+(ox-40)+" "+(PT+PH/2)+")"});yl.textContent=ylab;g.appendChild(yl);
 }

 let wlo=q(W,0.01),whi=q(W,0.99),hlo=q(H,0.01),hhi=q(H,0.99);
 const wp=(whi-wlo)*0.05, hp=(hhi-hlo)*0.05; wlo-=wp;whi+=wp;hlo-=hp;hhi+=hp;
 panel(LOX, W, H, wlo, whi, hlo, hhi, ticks(wlo,whi,5), ticks(hlo,hhi,5),
   "вес, кг", "рост, см", "До: сырые единицы", mW, mH, false);
 const Z=3.4, zW=W.map(v=>(v-mW)/sW), zH=H.map(v=>(v-mH)/sH);
 panel(ROX, zW, zH, -Z, Z, -Z, Z, [-3,-2,-1,0,1,2,3], [-3,-2,-1,0,1,2,3],
   "z(вес), σ", "z(рост), σ", "После: единицы σ", 0, 0, true);
 ro.innerHTML="вес: x&#772;="+mW.toFixed(1)+" кг, σ="+sW.toFixed(1)+" кг · рост: x&#772;="+mH.toFixed(1)
   +" см, σ="+sH.toFixed(1)+" см · после z обе оси центрированы в 0, σ=1";
})();
""".replace("__W__", W_JSON).replace("__H__", H_JSON)

display(HTML(viz(intro)))
display(HTML(viz(zdef)))
display(HTML(viz(l2bridge)))
display(HTML(viz(l2contrast)))
display(HTML(viz(space_transform)))
display(HTML(viz(figure, script, wide=True)))
display(HTML(viz(costidea)))
display(HTML(viz(cosine_spoiler)))
display(HTML(viz(closing)))''')

# ============================================================================
# 6. ПРАКТИКА S4 — задания на нормирование
# ============================================================================
md("""### Задания к S4 — нормирование и z-стандартизация

Выполняй каждое задание в пустой ячейке под ним. Где считаешь руками — **сверяй** с библиотекой; к числам и графикам пиши **вывод словами**.""")

md("""**Task 1.** Стандартизуй признак `height` своими руками: посчитай $z=(x-\\bar x)/\\sigma$ через numpy. Проверь численно, что у результата среднее $\\approx 0$ и стандартное отклонение $\\approx 1$. Затем сверь свой результат с `sklearn.preprocessing.StandardScaler`. Совпало ли до последней цифры? Если нет — вспомни про `ddof` (что делит на $n$, а что на $n-1$).""")
code("")

md("""**Task 2.** Стандартизуй `height` (см) и `weight` (кг). Покажи, что после z единицы измерения исчезли и оба признака оказались на одной шкале (среднее 0, разброс 1). Почему теперь их можно честно сравнивать и складывать, а до этого — нет?""")
code("")

md("""**Task 3.** Посчитай «курс обмена» $1/\\sigma$ для роста и для веса. У какого признака единичный отрезок «дороже» (даёт больше σ за одну сырую единицу)? Проверь на числах: сдвиг на 5 кг и сдвиг на 5 см — это сколько σ у каждого признака?""")
code("")

md("""**Task 4.** Возьми двух любых людей из датасета. Посчитай евклидово расстояние между ними по (`height`, `weight`) в сырых единицах, а потом — после z-стандартизации обоих признаков. Какой признак доминировал в сыром расстоянии и как стандартизация уравняла вклады?""")
code("")

md("""**Task 5.** Посчитай центроид (среднее по `height` и `weight`) отдельно для групп M и F. Найди между центроидами и евклидово расстояние, и косинус — до стандартизации и после. Покажи, что стандартизованный евклид разводит полы, а косинус к различию почти слеп. Объясни через карту «евклид ↔ z, косинус ↔ L2 сырого наблюдения».""")
code("")

md("""**Task 6.** Возьми одно наблюдение (одну строку) и L2-нормируй его как вектор: $v/\\lVert v\\rVert$ — получишь единичный вектор. Отдельно z-стандартизуй столбцы `height` и `weight`. Покажи на числах, что это **разные операции над разными объектами**: L2 по строке-наблюдению без центрирования против z по столбцу-признаку с центрированием.""")
code("")

md("""**Task 7.** Посчитай стандартное отклонение роста тремя способами: глобально по всем, и отдельно внутри групп M и F (`groupby('sex')`). Почему глобальная σ **больше** обеих внутригрупповых? Свяжи с тем, что глобальная σ «съедает» разрыв между мужским и женским центроидами, и как это удешевляет σ-валюту при глобальной z.""")
code("")

md("""**Task 8.** Построй scatter `height × weight` до и после z-стандартизации (сетку не забудь). Посчитай коэффициент корреляции между признаками в обоих случаях. Убедись, что z делает облако «круглее» по осям, но **корреляцию не меняет**. Как думаешь, почему форма связи признаков переживает стандартизацию?""")
code("")

# ============================================================================
nb = new_notebook(cells=cells)
nb.metadata = META
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "03_stat_intro.ipynb")
with open(out, "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("written", out, "cells:", len(cells))
