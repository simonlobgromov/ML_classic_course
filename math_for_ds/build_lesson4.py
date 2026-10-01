# -*- coding: utf-8 -*-
"""
Build 04_stat_boxplot.ipynb — "Непараметрические меры".

Part 1: the outlier problem — how the mean and, especially,
the standard deviation are distorted by extreme values because of the square.
  O1  histogram of real Bishkek apartment prices with dashed median / mean and a
      mean±2σ band, plus a "remove the outlier" toggle.
  O2  a from-scratch drag demo: drag one outlier and watch mean / median / σ /
      variance grow on a linear chart (variance is the parabola — the square).
  +   short text note that MSE inherits the same fragility (after the O2 chart).
Part 2: percentiles (strict definition, numpy), quartiles, IQR and the box plot.
Part 3: cleaning outliers — by percentiles and by the 1.5·IQR whiskers.
Part 4: IQR as a robust σ, RobustScaler; then tasks on house.kg (Bishkek).

Same dark HTML/JS lesson format as build_lesson3.py (theme.py). The notebook is
written un-executed; the JS renders in Colab and the data loads at runtime.

Run from repo root:  python3 math_for_ds/build_lesson4.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from theme import SETUP, META

cells = []
def md(s):   cells.append(new_markdown_cell(s.strip("\n")))
def code(s): cells.append(new_code_cell(s.strip("\n")))

# ============================================================================
# Title
# ============================================================================
md(r"""
# Непараметрические меры

Среднее и стандартное отклонение — «параметрические» меры: они хорошо описывают
распределение, когда его форма приличная (симметрична, без тяжёлых хвостов). Реальные
данные так ведут себя редко. Эта тетрадь — про то, почему на выбросах и скошенных
распределениях среднее и $\sigma$ подводят, и про **непараметрические меры**, которые
не опираются на форму распределения (что именно это значит — раскроем во второй части):
медиану, квартили и IQR, — и про **боксплот**, график, который их показывает.

Данные — объявления о продаже квартир в Бишкеке (house.kg), те же, что в семинаре.

## Часть 1 — Как выброс ломает среднее и, особенно, σ
""")

# ============================================================================
# Data
# ============================================================================
code(r"""
# В Colab: !pip install -q datasets
import numpy as np, pandas as pd, json
from huggingface_hub import hf_hub_download

_path = hf_hub_download("aiacademy-kg/house_kg_full_dataset",
                        "data/listings.parquet", repo_type="dataset")
df = pd.read_parquet(_path)

ap = df[(df.deal == "sale") & (df.type == "apartment") & (df.city == "Бишкек")].copy()
ap["price_usd"] = pd.to_numeric(ap["price_usd"], errors="coerce")
ap = ap.dropna(subset=["price_usd"])
price = ap["price_usd"].to_numpy() / 1000.0        # цена в тысячах USD (k)
print("объявлений:", len(price), "| медиана цены:", round(float(np.median(price))), "k USD")
""")

# ============================================================================
# Setup (theme + viz helpers)
# ============================================================================
code(SETUP)

# ============================================================================
# O1 — outlier distorts mean & sigma (histogram, remove-outlier toggle)
# ============================================================================
code(r'''#@title Теория — Один выброс ломает среднее и σ { display-mode: "form" }
import json, numpy as np
rng = np.random.default_rng(3)
_bulk = price[(price >= 25) & (price <= 350)]           # типичный диапазон, k USD
_samp = rng.choice(_bulk, size=249, replace=False)
_outlier = 2000.0                                       # одно объявление за $2 000 000
SAMPLE = np.append(_samp, _outlier)
SAMPLE_JSON = json.dumps([round(float(v), 1) for v in SAMPLE])

intro = r"""
<h2>Выброс и почему страдает именно σ</h2>
<p><b>Выброс</b> <span class="en">(outlier)</span> — наблюдение, далеко оторвавшееся от
основной массы. В нашей выборке из 250 квартир Бишкека одно объявление стоит
<b>$2 000 000</b> при типичной цене около $100k. Посмотрим, что оно делает с тремя
описаниями «центра и разброса»: медианой, средним и стандартным отклонением.</p>
<div class="box def"><div class="t">Что на графике</div>
Кривая плотности <span class="en">(KDE)</span> цен (в тысячах USD). Пунктиром — <span style="color:#ffffff">медиана</span> и
<span style="color:#e0b25a">среднее</span>; жёлтая полоса — диапазон
<b>среднее ± 2σ</b> (куда «по Гауссу» должно попадать ~95% значений). Сам выброс лежит
далеко за правым краем — на него показывает стрелка. Переключите флажок
<b>«убрать выброс»</b> и следите, что сдвинется, а что нет.</div>
"""

figure = r"""
<div class="widget"><div class="widget-title">Цены квартир: одна строка против трёх мер</div>
<div class="widget-sub">Кривая плотности (KDE) по 250 объявлениям. Пунктир — медиана и
среднее, жёлтая полоса — среднее ± 2σ.</div>
<svg viewBox="0 0 660 340" id="svg-o1"></svg>
<div class="controls">
<div class="control"><label><input type="checkbox" id="o1-rm"> убрать выброс</label></div>
</div>
<div class="readout" id="o1-ro"></div></div>
"""

after = r"""
<div class="box take"><div class="t">Что произошло</div>
<ul>
<li><b>Медиана</b> — серединное значение — почти не шелохнулась: одна строка её не сдвигает.</li>
<li><b>Среднее</b> ощутимо уехало вправо: выброс тянет его <em>линейно</em>.</li>
<li><b>σ</b> раздулась сильнее всего, а полоса среднее ± 2σ стала огромной и нижним
краем ушла <em>ниже нуля</em> — для цены это бессмыслица. Мало того: σ так раздулась, что
сам выброс всё равно оказался далеко <em>за</em> границей 2σ — правило его «не поймало».</li>
</ul>
Почему σ страдает больше всех — покажет следующий блок.</div>
"""

script = r"""
(function(){
 const svg=document.getElementById("svg-o1"); if(!svg) return;
 const DATA=__SAMPLE__;
 const cb=document.getElementById("o1-rm"), ro=document.getElementById("o1-ro");
 const CW=660,CH=340, ML=46,MR=20,MT=22,MB=44, PW=CW-ML-MR,PH=CH-MT-MB, X0=ML,Y0=MT+PH;
 const XMAX=450;
 const sx=v=>X0+Math.min(v,XMAX)/XMAX*PW;
 const mean=a=>a.reduce((p,c)=>p+c,0)/a.length;
 const median=a=>{const s=[...a].sort((x,y)=>x-y);const n=s.length,m=n>>1;return n%2?s[m]:(s[m-1]+s[m])/2;};
 const std=a=>{const m=mean(a);return Math.sqrt(a.reduce((p,x)=>p+(x-m)*(x-m),0)/a.length);};
 const kde=(arr,xs,h)=>{const n=arr.length,c=1/(n*h*Math.sqrt(2*Math.PI));return xs.map(x=>{let s=0;for(const xi of arr){const u=(x-xi)/h;s+=Math.exp(-0.5*u*u);}return c*s;});};
 function render(){
   const MX=Math.max.apply(null,DATA);
   const data = cb.checked ? DATA.filter(v=>v<MX) : DATA;
   while(svg.firstChild) svg.removeChild(svg.firstChild);
   const g=el("g"); svg.appendChild(g);
   g.appendChild(el("rect",{x:X0,y:MT,width:PW,height:PH,fill:"#0b0f14",stroke:"#2a313b"}));
   for(let t=0;t<=XMAX;t+=100){ g.appendChild(el("line",{x1:sx(t),y1:MT,x2:sx(t),y2:Y0,stroke:"#19212c"}));
     const tl=el("text",{x:sx(t),y:Y0+15,fill:"#6b7580","font-size":10,"text-anchor":"middle","font-family":"sans-serif"});tl.textContent=t+"k";g.appendChild(tl);}
   const m=mean(data), md=median(data), sd=std(data);
   const lo=Math.max(0,m-2*sd), hi=Math.min(XMAX,m+2*sd);
   g.appendChild(el("rect",{x:sx(lo),y:MT,width:Math.max(0,sx(hi)-sx(lo)),height:PH,fill:"#e0b25a","fill-opacity":.12}));
   const inr=data.filter(v=>v<XMAX);
   const sdi=std(inr), h=Math.max(8,1.06*sdi*Math.pow(inr.length,-0.2));
   const G=200, xs=[]; for(let i=0;i<G;i++) xs.push(XMAX*i/(G-1));
   const dens=kde(inr,xs,h), dmax=Math.max.apply(null,dens)||1;
   const syD=d=>Y0-d/dmax*(PH*0.92);
   let pth="M "+sx(0).toFixed(1)+" "+Y0.toFixed(1)+" ";
   for(let i=0;i<G;i++) pth+="L "+sx(xs[i]).toFixed(1)+" "+syD(dens[i]).toFixed(1)+" ";
   pth+="L "+sx(XMAX).toFixed(1)+" "+Y0.toFixed(1)+" Z";
   g.appendChild(el("path",{d:pth,fill:"#6ab0f3","fill-opacity":.18,stroke:"#6ab0f3","stroke-width":2}));
   const vline=(x,col)=>{ const cx=sx(x);
     g.appendChild(el("line",{x1:cx,y1:MT,x2:cx,y2:Y0,stroke:col,"stroke-width":2,"stroke-dasharray":"5 4"})); };
   vline(md,"#ffffff"); vline(m,"#e0b25a");
   const MX2=Math.max.apply(null,data);
   if(MX2>=XMAX){ g.appendChild(arrow(sx(XMAX)-30,MT+18,sx(XMAX)-6,MT+18,{color:"#e0757f",width:2,head:9}));
     const t=el("text",{x:sx(XMAX)-34,y:MT+15,fill:"#e0757f","font-size":11,"text-anchor":"end","font-family":"sans-serif"});
     t.textContent="выброс $"+(MX2/1000).toFixed(1)+"M"; g.appendChild(t); }
   const neg=(m-2*sd)<0 ? " — нижняя граница < 0 (бессмыслица для цены)" : "";
   ro.innerHTML="n="+data.length+" · медиана="+md.toFixed(0)+"k · среднее="+m.toFixed(0)
     +"k · σ="+sd.toFixed(0)+"k · 2σ-диапазон=["+(m-2*sd).toFixed(0)+"k, "+(m+2*sd).toFixed(0)+"k]"+neg;
 }
 cb.addEventListener("change",render); render();
})();
""".replace("__SAMPLE__", SAMPLE_JSON)

display(HTML(viz(intro)))
display(HTML(viz(figure, script, wide=True)))
display(HTML(viz(after)))''')

# ============================================================================
# O2 — drag the outlier; linear chart of mean / median / sigma / variance
# ============================================================================
code(r'''#@title Теория — Тащи выброс: кто как растёт { display-mode: "form" }
intro = r"""
<h3>Почему σ страдает сильнее среднего — из-за квадрата</h3>
<p>Вклад точки в дисперсию — это $(x_i-\bar x)^2$. Возведение в квадрат означает: чем
дальше выброс, тем <b>непропорционально</b> больше его вклад. Отодвинь выброс вдвое
дальше — среднее потянется вдвое сильнее, а вклад в дисперсию вырастет <b>вчетверо</b>.
Ниже — маленький набор точек с одним выбросом: тащи красную точку вправо и смотри на
правый график, во сколько раз выросла каждая мера относительно старта.</p>
"""

figure = r"""
<div class="widget"><div class="widget-title">Одна точка — четыре реакции</div>
<div class="widget-sub">Слева — данные (тащи <span style="color:#e0757f">красную</span>
точку); пунктир — <span style="color:#ffffff">медиана</span> и
<span style="color:#e0b25a">среднее</span>. Справа — во сколько раз выросли
<span style="color:#e0757f">дисперсия</span>,
<span style="color:#5fd08a">σ</span>,
<span style="color:#e0b25a">среднее</span> и
<span style="color:#ffffff">медиана</span> при движении выброса.</div>
<svg viewBox="0 0 920 340" id="svg-o2"></svg>
<div class="controls">
<div class="control"><label><input type="checkbox" id="o2-rm"> убрать выброс</label></div>
</div>
<div class="readout" id="o2-ro"></div></div>
"""

after = r"""
<div class="box idea"><div class="t">Что видно на графике</div>
<b>Медиана</b> — горизонтальная прямая (×1): выброс её не трогает вообще.
<b>Среднее</b> растёт <em>линейно</em>. <b>σ</b> — быстрее. А <b>дисперсия</b> — это
<b>парабола</b>: она взлетает круче всех, потому что в ней стоит квадрат. Именно квадрат
делает дисперсию (и σ = её корень) самой чувствительной к экстремальным значениям мерой.</div>
"""

script = r"""
(function(){
 const svg=document.getElementById("svg-o2"); if(!svg) return;
 const BASE=[8,9,9,10,10,10,11,11,12];
 const rm=document.getElementById("o2-rm"), ro=document.getElementById("o2-ro");
 const LX=44, LW=430, LY=150;
 const RX=560, RW=330, RT=34, RH=250, RB=RT+RH;
 const TMIN=12, TMAX=45;
 const mean=a=>a.reduce((p,c)=>p+c,0)/a.length;
 const median=a=>{const s=[...a].sort((x,y)=>x-y);const n=s.length,m=n>>1;return n%2?s[m]:(s[m-1]+s[m])/2;};
 const varf=a=>{const m=mean(a);return a.reduce((p,x)=>p+(x-m)*(x-m),0)/a.length;};
 const stats=t=>{const d=BASE.concat([t]);const v=varf(d);return {mean:mean(d),median:median(d),std:Math.sqrt(v),varr:v};};
 const b0=stats(TMIN);
 const TS=[],cv={mean:[],median:[],std:[],varr:[]};
 for(let t=TMIN;t<=TMAX+1e-9;t+=0.5){const s=stats(t);TS.push(t);
   cv.mean.push(s.mean/b0.mean); cv.median.push(s.median/b0.median);
   cv.std.push(s.std/b0.std); cv.varr.push(s.varr/b0.varr);}
 const ymax=Math.max.apply(null,cv.varr)*1.05;
 const sxL=v=>LX+v/48*LW;
 const sxR=t=>RX+(t-TMIN)/(TMAX-TMIN)*RW;
 const syR=y=>RB-y/ymax*RH;
 const COL={median:"#ffffff",mean:"#e0b25a",std:"#5fd08a",varr:"#e0757f"};
 let T=15, removed=false;
 function draw(){
   while(svg.firstChild) svg.removeChild(svg.firstChild);
   const g=el("g"); svg.appendChild(g);
   const data = removed ? BASE.slice() : BASE.concat([T]);
   const m=mean(data), md=median(data), sd=Math.sqrt(varf(data));
   // ---------- left: number line ----------
   const tl=el("text",{x:LX,y:24,fill:"#e6e9ec","font-size":13,"font-weight":700,"font-family":"sans-serif"});
   tl.textContent="Данные"+(removed?" (выброс убран)":" (тащи красную точку →)"); g.appendChild(tl);
   const band=el("rect",{x:sxL(Math.max(0,m-sd)),y:LY-34,width:sxL(m+sd)-sxL(Math.max(0,m-sd)),height:68,
     fill:"#e0b25a","fill-opacity":.10}); g.appendChild(band);
   g.appendChild(el("line",{x1:sxL(0),y1:LY,x2:sxL(48),y2:LY,stroke:"#3a434f","stroke-width":2}));
   for(let t=0;t<=45;t+=5){ g.appendChild(el("line",{x1:sxL(t),y1:LY-5,x2:sxL(t),y2:LY+5,stroke:"#3a434f"}));
     const x=el("text",{x:sxL(t),y:LY+20,fill:"#6b7580","font-size":11,"text-anchor":"middle","font-family":"sans-serif"});x.textContent=t;g.appendChild(x);}
   for(const v of BASE) g.appendChild(el("circle",{cx:sxL(v),cy:LY,r:6.5,fill:"#6ab0f3","fill-opacity":.85}));
   const tick=(x,col,lab,dy)=>{ g.appendChild(el("line",{x1:sxL(x),y1:LY-30,x2:sxL(x),y2:LY+30,stroke:col,"stroke-width":2,"stroke-dasharray":"4 3"}));
     const t=el("text",{x:sxL(x),y:LY-dy,fill:col,"font-size":11,"text-anchor":"middle","font-family":"sans-serif"});t.textContent=lab;g.appendChild(t);};
   tick(md,"#ffffff","медиана",34); tick(m,"#e0b25a","среднее",50);
   let hC=null;
   if(!removed){ hC=el("circle",{cx:sxL(T),cy:LY,r:8,fill:"#e0757f","fill-opacity":.35,stroke:"#e0757f","stroke-width":2.5}); g.appendChild(hC);
     const t=el("text",{x:sxL(T),y:LY+42,fill:"#e0757f","font-size":11,"text-anchor":"middle","font-family":"sans-serif"});t.textContent="выброс";g.appendChild(t);}
   // ---------- right: multiplier chart ----------
   g.appendChild(el("rect",{x:RX,y:RT,width:RW,height:RH,fill:"#0b0f14",stroke:"#2a313b"}));
   for(let k=1;k*10<=ymax;k++){ const y=syR(k*10);
     g.appendChild(el("line",{x1:RX,y1:y,x2:RX+RW,y2:y,stroke:"#19212c"}));
     const t=el("text",{x:RX-6,y:y+3,fill:"#6b7580","font-size":10,"text-anchor":"end","font-family":"sans-serif"});t.textContent="×"+(k*10);g.appendChild(t);}
   g.appendChild(el("line",{x1:RX,y1:syR(1),x2:RX+RW,y2:syR(1),stroke:"#46505c","stroke-dasharray":"2 3"}));
   const rt=el("text",{x:RX,y:22,fill:"#e6e9ec","font-size":13,"font-weight":700,"font-family":"sans-serif"});
   rt.textContent="Во сколько раз выросла мера"; g.appendChild(rt);
   const poly=(arr,col)=>{let d="";for(let i=0;i<TS.length;i++){d+=(i?"L":"M")+sxR(TS[i]).toFixed(1)+" "+syR(arr[i]).toFixed(1)+" ";}
     g.appendChild(el("path",{d:d,fill:"none",stroke:col,"stroke-width":2}));};
   poly(cv.varr,COL.varr); poly(cv.std,COL.std); poly(cv.mean,COL.mean); poly(cv.median,COL.median);
   if(!removed){ const cur=stats(T);
     const dot=(y,col)=>g.appendChild(el("circle",{cx:sxR(T),cy:syR(y),r:4,fill:col}));
     dot(cur.varr/b0.varr,COL.varr); dot(cur.std/b0.std,COL.std); dot(cur.mean/b0.mean,COL.mean); dot(cur.median/b0.median,COL.median); }
   const leg=[["дисперсия",COL.varr],["σ",COL.std],["среднее",COL.mean],["медиана",COL.median]];
   leg.forEach((L,i)=>{const y=RT+16+i*15;g.appendChild(el("line",{x1:RX+RW-96,y1:y,x2:RX+RW-78,y2:y,stroke:L[1],"stroke-width":3}));
     const t=el("text",{x:RX+RW-72,y:y+4,fill:"#a7b0ba","font-size":11,"font-family":"sans-serif"});t.textContent=L[0];g.appendChild(t);});
   // readout
   if(removed){ ro.innerHTML="выброс убран · среднее="+m.toFixed(2)+" · медиана="+md.toFixed(2)+" · σ="+sd.toFixed(2); }
   else { const c=stats(T);
     ro.innerHTML="выброс на "+T.toFixed(1)+" · среднее ×"+(c.mean/b0.mean).toFixed(2)
       +" · медиана ×"+(c.median/b0.median).toFixed(2)+" · σ ×"+(c.std/b0.std).toFixed(2)
       +" · <b>дисперсия ×"+(c.varr/b0.varr).toFixed(2)+"</b>"; }
   if(hC) onDrag(svg,hC,p=>{ T=clamp((p.x-LX)/LW*48,TMIN,TMAX); draw(); });
 }
 rm.addEventListener("change",()=>{ removed=rm.checked; draw(); });
 draw();
})();
"""

display(HTML(viz(intro)))
display(HTML(viz(figure, script, wide=True)))
display(HTML(viz(after)))''')

# ============================================================================
# MSE text (after the O2 chart) + teaser to Part 2
# ============================================================================
code(r'''#@title Заметка — MSE и мостик к части 2 { display-mode: "form" }
mse = r"""
<div class="box warn"><div class="t">Забегая вперёд: MSE наследует эту же слабость</div>
Модели часто учат, минимизируя <b>среднеквадратичную ошибку</b>
<span class="en">(mean squared error, MSE)</span> — среднее от квадратов ошибок. Но это
ровно та же конструкция, что и дисперсия: квадрат внутри. Значит и болезнь та же — один
далёкий выброс может <b>доминировать</b> в ошибке и утащить всю модель на себя, как он
утаскивал σ. Робастная альтернатива — линейный штраф $|{\cdot}|$
<span class="en">(MAE)</span>: он не возводит ошибку в квадрат и потому куда спокойнее
относится к выбросам. Подробно к этому вернёмся в теме про обучение моделей.
"""

teaser = r"""
<div class="box take"><div class="t">Что дальше</div>
Итак, среднее и σ уязвимы, а «чистить по 3σ» вдвойне неудобно: σ сама раздута выбросами
(правило их недоотлавливает), а на скошенном распределении симметричный забор
<em>среднее ± 3σ</em> стоит не там. Нужны меры, которые <b>вообще не смотрят на среднее и
σ</b> и не опираются на форму распределения, — их называют <b>непараметрическими</b>:
медиана, квартили, IQR. Показывают их на <b>боксплоте</b>. С него и начнём <b>часть 2</b>.
"""

display(HTML(viz(mse)))
display(HTML(viz(teaser)))''')

# ============================================================================
# Part 2 — Percentiles
# ============================================================================
md(r"""
## Часть 2 — Перцентили

Раз среднее и σ подводят, нужны меры, опирающиеся не на форму распределения, а только на
**порядок** значений. Начнём с базовой — перцентиля. Иллюстрируем на датасете **Davis**
(тот же, что в первом колабе): берём только **мужчин и их рост**.
""")

code(r"""
# Davis — рост мужчин и женщин (см). Тянем с HF, как в первом колабе.
from datasets import load_dataset
_dv = load_dataset("aiacademy-kg/davis_dataset", split="train").to_pandas()
def _height(sex):
    h = pd.to_numeric(_dv.loc[_dv["sex"] == sex, "height"], errors="coerce").dropna()
    return h[h.between(140, 210)].to_numpy(float)          # лёгкая страховка от опечаток
men_h   = _height("M")
women_h = _height("F")
print("мужчин:", len(men_h), "| женщин:", len(women_h),
      "| рост мужчин от", int(men_h.min()), "до", int(men_h.max()), "см")
""")

code(r'''#@title Теория — Перцентиль: строгое определение { display-mode: "form" }
import json, numpy as np
_srt = np.sort(men_h)
HS_JSON = json.dumps([round(float(v), 1) for v in _srt])
N = len(_srt)
ARR = ", ".join(f"{v:.0f}" for v in _srt[:4]) + ", …, " + ", ".join(f"{v:.0f}" for v in _srt[-4:])

intro = r"""
<h2>Перцентиль <span class="en">(percentile)</span></h2>
<p>Непараметрические меры <span class="en">(non-parametric measures)</span> не описывают
распределение формулой его формы — они опираются только на <b>порядок</b> значений. Базовая
из них — перцентиль.</p>
<div class="box def"><div class="t">Определение <span class="en">(definition)</span></div>
Отсортируем выборку по возрастанию — получим <b>порядковые статистики</b>
<span class="en">(order statistics)</span> (индексация с нуля, как в numpy):
$$ s_0 \le s_1 \le \dots \le s_{n-1}. $$
Для $0 \le p \le 100$ <b>$p$-й перцентиль</b> <span class="en">($p$-th percentile)</span>
$Q(p)$ — это значение, ниже которого лежит примерно $p\%$ наблюдений: около $p\%$ данных
<b>не превышают</b> $Q(p)$, а остальные $(100-p)\%$ — не меньше него.</div>
<div class="box idea"><div class="t">Квантиль <span class="en">(quantile)</span></div>
Близкий термин: <b>квантиль</b> — то же самое, что перцентиль, но уровень задают <b>долей от 0
до 1</b>, а не процентом. Квантиль $0{,}5$ — это 50-й перцентиль (медиана), квантиль $0{,}9$ —
90-й перцентиль. Короче: перцентиль $=$ квантиль, выраженный в процентах.</div>
"""

arr = r"""
<div class="box idea"><div class="t">Отсортированный массив <span class="en">(sorted array)</span></div>
Рост мужчин из датасета Davis, $n=__N__$, по возрастанию (см):
<div style="font-family:Menlo,monospace;color:#fff;margin:6px 0">__ARR__</div>
Найти перцентиль — значит пройти долю $p$ вдоль этого ряда и прочитать значение.</div>
""".replace("__N__", str(N)).replace("__ARR__", ARR)

formula = r"""
<div class="box def"><div class="t">Как это считается <span class="en">(numpy, method="linear")</span></div>
<p style="margin-top:0"><b>Шаг 1. Позиция.</b> Долю $p$ переводим в позицию внутри
отсортированного ряда <span class="en">(rank / position)</span>:
$$ h=(n-1)\cdot\frac{p}{100}. $$
Например, при $n=10$ и $p=50$: $h=(10-1)\cdot 0{,}5=4{,}5$ — позиция между 4-м и 5-м элементами
(индексы с нуля).</p>
<p><b>Шаг 2. Левый сосед.</b> $k=\lfloor h\rfloor$. Скобки $\lfloor\ \rfloor$ читаются как
<b>«пол»</b> <span class="en">(floor)</span> — это <b>целая часть</b>, число, округлённое
<b>вниз</b>: $\lfloor 4{,}5\rfloor=4$, $\lfloor 4{,}9\rfloor=4$. То есть $k$ — индекс наблюдения
<em>слева</em> от позиции.</p>
<p><b>Шаг 3. Линейная интерполяция</b> <span class="en">(linear interpolation)</span>.
Позиция $h$ почти всегда попадает <em>между</em> двумя соседними наблюдениями $s_k$ и $s_{k+1}$.
Тогда перцентиль — не одно из них, а точка <b>между</b> ними, тем ближе к правому, чем ближе к
нему позиция:
$$ Q(p)=s_k+(h-k)\,\bigl(s_{k+1}-s_k\bigr). $$
Здесь $(h-k)$ — дробная часть позиции, доля пути от левого соседа к правому (от 0 до 1):</p>
<ul>
<li>$h-k=0$ → берём ровно $s_k$;</li>
<li>$h-k=1$ → берём ровно $s_{k+1}$;</li>
<li>$h-k=0{,}5$ (позиция ровно посередине) → берём их <b>среднее</b> $\tfrac{s_k+s_{k+1}}{2}$.</li>
</ul>
В нашем примере ($h=4{,}5$): $k=4$, дробная часть $0{,}5$ ⇒ $Q(50)=\tfrac{s_4+s_5}{2}$ — то самое
«среднее двух центральных», которым и считают медиану при чётном $n$.
<div class="where">Частные случаи: $Q(0)$ — минимум <span class="en">(min)</span>,
$Q(100)$ — максимум <span class="en">(max)</span>, $Q(50)$ — <b>медиана</b>
<span class="en">(median)</span>. Соглашений об интерполяции несколько (параметр
<code>method</code> в numpy); берём принятое по умолчанию.</div></div>
"""

figure = r"""
<div class="widget"><div class="widget-title">Перцентиль на отсортированном росте мужчин (Davis)</div>
<div class="widget-sub">По горизонтали — доля $p$ (%), по вертикали — рост (см). Точки —
порядковые статистики $s_0,\dots,s_{n-1}$; ломаная — функция перцентиля. Двигайте $p$:
жёлтая вертикаль — позиция, <span style="color:#5fd08a">зелёные</span> точки — наблюдения
$\le Q(p)$, белые кольца — соседи, между которыми идёт интерполяция.</div>
<svg viewBox="0 0 720 380" id="svg-pc"></svg>
<div class="controls">
<div class="control"><label>p =</label>
<input type="range" id="pc-p" min="0" max="100" step="1" value="50"><span class="val" id="pc-pv">50</span></div>
</div>
<div class="readout" id="pc-ro"></div></div>
"""

after = r"""
<div class="box take"><div class="t">Чем перцентиль хорош</div>
Он не зависит от формы распределения и почти не реагирует на выбросы: один далёкий рост
сдвинет разве что $Q(100)$, но не $Q(50)$. Из перцентилей собираются <b>квартили</b>
<span class="en">(quartiles)</span> и медиана, а из них — боксплот. С квартилей продолжим.</div>
"""

script = r"""
(function(){
 const svg=document.getElementById("svg-pc"); if(!svg) return;
 const S=__HS__, n=S.length;
 const sl=document.getElementById("pc-p"), pv=document.getElementById("pc-pv"), ro=document.getElementById("pc-ro");
 const CW=720,CH=380, ML=54,MR=18,MT=20,MB=42, PW=CW-ML-MR,PH=CH-MT-MB, X0=ML,Y0=MT+PH;
 let lo=S[0], hi=S[n-1]; const pad=(hi-lo)*0.08||1; lo-=pad; hi+=pad;
 const sx=p=>X0+p/100*PW;
 const sy=v=>Y0-(v-lo)/(hi-lo)*PH;
 const pos=i=>100*i/(n-1);
 const Q=p=>{const h=(n-1)*p/100,k=Math.floor(h); return k>=n-1? S[n-1] : S[k]+(h-k)*(S[k+1]-S[k]);};
 function render(){
   const p=+sl.value; pv.textContent=p;
   while(svg.firstChild) svg.removeChild(svg.firstChild);
   const g=el("g"); svg.appendChild(g);
   g.appendChild(el("rect",{x:X0,y:MT,width:PW,height:PH,fill:"#0b0f14",stroke:"#2a313b"}));
   for(let t=0;t<=100;t+=20){ g.appendChild(el("line",{x1:sx(t),y1:MT,x2:sx(t),y2:Y0,stroke:"#19212c"}));
     const l=el("text",{x:sx(t),y:Y0+15,fill:"#6b7580","font-size":10,"text-anchor":"middle","font-family":"sans-serif"});l.textContent=t+"%";g.appendChild(l);}
   for(let v=Math.ceil(lo/5)*5;v<=hi;v+=5){ g.appendChild(el("line",{x1:X0,y1:sy(v),x2:X0+PW,y2:sy(v),stroke:"#19212c"}));
     const l=el("text",{x:X0-6,y:sy(v)+3,fill:"#6b7580","font-size":10,"text-anchor":"end","font-family":"sans-serif"});l.textContent=v;g.appendChild(l);}
   let d="";for(let i=0;i<n;i++){d+=(i?"L":"M")+sx(pos(i)).toFixed(1)+" "+sy(S[i]).toFixed(1)+" ";}
   g.appendChild(el("path",{d:d,fill:"none",stroke:"#3a6ea5","stroke-width":1.5}));
   for(let i=0;i<n;i++){ const under=pos(i)<=p+1e-9;
     g.appendChild(el("circle",{cx:sx(pos(i)),cy:sy(S[i]),r:3,fill:under?"#5fd08a":"#6ab0f3","fill-opacity":.85})); }
   const q=Q(p);
   g.appendChild(el("line",{x1:sx(p),y1:MT,x2:sx(p),y2:Y0,stroke:"#e0b25a","stroke-width":2,"stroke-dasharray":"5 4"}));
   g.appendChild(el("line",{x1:X0,y1:sy(q),x2:sx(p),y2:sy(q),stroke:"#e0b25a","stroke-width":1.5,"stroke-dasharray":"4 3"}));
   g.appendChild(el("circle",{cx:sx(p),cy:sy(q),r:5,fill:"#e0b25a"}));
   const h=(n-1)*p/100, k=Math.floor(h);
   if(k<n-1){ g.appendChild(el("circle",{cx:sx(pos(k)),cy:sy(S[k]),r:6,fill:"none",stroke:"#fff","stroke-width":1.6}));
              g.appendChild(el("circle",{cx:sx(pos(k+1)),cy:sy(S[k+1]),r:6,fill:"none",stroke:"#fff","stroke-width":1.6})); }
   let cnt=0; for(let i=0;i<n;i++) if(pos(i)<=p+1e-9) cnt++;
   ro.innerHTML="p="+p+"% · позиция h=(n−1)·p/100="+h.toFixed(2)+" · Q(p)=<b>"+q.toFixed(1)+" см</b> · наблюдений ≤ Q(p): "+cnt+" из "+n;
 }
 sl.addEventListener("input",render); render();
})();
""".replace("__HS__", HS_JSON)

display(HTML(viz(intro)))
display(HTML(viz(arr)))
display(HTML(viz(formula)))
display(HTML(viz(figure, script, wide=True)))
display(HTML(viz(after)))''')

md(r"""
### Как посчитать перцентиль в numpy

Руками — по формуле выше; в библиотеке — одной строкой. Полезно убедиться, что это одно и то же.

```python
import numpy as np

# библиотека: p-й перцентиль (p в процентах, 0..100)
np.percentile(men_h, 50)             # медиана (50-й перцентиль)
np.percentile(men_h, 25)             # первый квартиль
np.percentile(men_h, [25, 50, 75])   # сразу несколько

# то же через квантиль (уровень 0..1, а не проценты)
np.quantile(men_h, 0.5)              # == np.percentile(men_h, 50)
np.median(men_h)                     # == 50-й перцентиль

# руками, по той же формуле (method="linear"):
h    = np.sort(men_h)
n    = len(h)
p    = 75
pos  = (n - 1) * p / 100             # позиция
k    = int(np.floor(pos))            # индекс левого соседа (пол/floor)
frac = pos - k                       # дробная часть, доля пути к правому соседу
q    = h[-1] if k >= n - 1 else h[k] + frac * (h[k + 1] - h[k])

print(q, np.percentile(men_h, p))    # должны совпасть
```
""")

# ============================================================================
# Part 2 (cont.) — Quartiles & box plot
# ============================================================================
code(r'''#@title Теория — Зачем боксплот, квартили, IQR { display-mode: "form" }
motivation = r"""
<h2>Квартили и боксплот <span class="en">(quartiles &amp; box plot)</span></h2>
<p>Одно число (среднее, медиана) — это только центр. Часто нужно <b>одним взглядом</b> охватить
сразу несколько свойств распределения и <b>сравнить группы</b>. Для этого придуман <b>боксплот</b>
<span class="en">(box plot, «ящик с усами»)</span>.</p>
<div class="box def"><div class="t">На какие вопросы отвечает боксплот</div>
<ul>
<li><b>Где типичный уровень?</b> — линия медианы внутри ящика.</li>
<li><b>Насколько велик разброс?</b> — длина ящика (это IQR, средние 50% данных).</li>
<li><b>Симметрично или скошено?</b> — положение медианы в ящике и длины усов.</li>
<li><b>Есть ли выбросы?</b> — точки за усами.</li>
<li><b>Чем отличаются группы?</b> — поставив ящики рядом (например, рост мужчин и женщин).</li>
</ul></div>
<p>Ниже соберём боксплот по шагам, а в конце сравним рост мужчин и женщин из Davis.</p>
"""

quart = r"""
<div class="box def"><div class="t">Квартили <span class="en">(quartiles)</span></div>
Квартили — это перцентили, делящие отсортированные данные на <b>четыре равные части</b>
(по ~25% в каждой):
<ul>
<li><b>Q1</b> — первый (нижний) квартиль <span class="en">(first / lower quartile)</span> $=$ 25-й перцентиль;</li>
<li><b>Q2</b> — второй квартиль $=$ 50-й перцентиль $=$ <b>медиана</b> <span class="en">(median)</span>;</li>
<li><b>Q3</b> — третий (верхний) квартиль <span class="en">(third / upper quartile)</span> $=$ 75-й перцентиль.</li>
</ul>
Ниже Q1 лежит ~25% наблюдений, ниже Q2 — ~50%, ниже Q3 — ~75%. Считаются той же формулой
перцентиля, что и в прошлом блоке.</div>
"""

iqr = r"""
<div class="box idea"><div class="t">Межквартильный размах <span class="en">(IQR, interquartile range)</span></div>
$$ \mathrm{IQR}=Q_3-Q_1. $$
Это ширина «средних 50%» данных — <b>робастная мера разброса</b> (устойчивый к выбросам аналог σ).
Что такое IQR — важно уже сейчас: на нём строятся усы боксплота. А вот <b>как его применяют</b>
для чистки выбросов и нормировки — в следующей части.</div>
"""

display(HTML(viz(motivation)))
display(HTML(viz(quart)))
display(HTML(viz(iqr)))''')

code(r'''#@title Теория — Боксплот по шагам { display-mode: "form" }
import json, numpy as np
_W = json.dumps([round(float(v), 1) for v in np.sort(women_h)])

figure = r"""
<div class="widget"><div class="widget-title">Как собирается боксплот (рост женщин, Davis)</div>
<div class="widget-sub">Внизу — сами данные (каждая точка = один человек). Двигайте <b>шаг</b> и следите,
как элемент за элементом собирается «ящик с усами».
Шаг 1 — ящик Q1…Q3; шаг 2 — медиана; шаг 3 — забор (пунктир) и усы; шаг 4 — точки-выбросы.</div>
<svg viewBox="0 0 760 300" id="svg-bx"></svg>
<div class="controls">
<div class="control"><label>шаг =</label>
<input type="range" id="bx-step" min="1" max="4" step="1" value="1"><span class="val" id="bx-sv">1</span></div>
</div>
<div class="readout" id="bx-ro"></div></div>
"""

dots = r"""
<div class="box warn"><div class="t">Что означают точки на концах</div>
Точки за усами — наблюдения, вышедшие за <b>забор</b>
$[\,Q_1-1{,}5\cdot\mathrm{IQR},\; Q_3+1{,}5\cdot\mathrm{IQR}\,]$. Их рисуют отдельными точками и
называют <b>потенциальными выбросами</b> <span class="en">(outliers)</span>. «Потенциальными» —
потому что это <em>не обязательно ошибки</em>: просто необычно далёкие значения, на которые стоит
взглянуть.</div>
"""

script = r"""
(function(){
 const svg=document.getElementById("svg-bx"); if(!svg) return;
 const S=__W__, n=S.length;
 const sl=document.getElementById("bx-step"), sv=document.getElementById("bx-sv"), ro=document.getElementById("bx-ro");
 const CW=760,CH=300, ML=44,MR=24,MT=28, PW=CW-ML-MR, X0=ML;
 const AY=MT+72, RY=MT+168;
 let lo=S[0], hi=S[n-1]; const pad=(hi-lo)*0.10||1; lo-=pad; hi+=pad;
 const sx=v=>X0+(v-lo)/(hi-lo)*PW;
 const q=p=>{const h=(n-1)*p/100,k=Math.floor(h);return k>=n-1?S[n-1]:S[k]+(h-k)*(S[k+1]-S[k]);};
 function lab(g,x,y,txt,anchor,col){const a=anchor<0?"end":anchor>0?"start":"middle";
   const t=el("text",{x:x,y:y,fill:col,"font-size":11,"text-anchor":a,"font-family":"sans-serif"});t.textContent=txt;g.appendChild(t);}
 function render(){
   const step=+sl.value; sv.textContent=step;
   while(svg.firstChild) svg.removeChild(svg.firstChild);
   const g=el("g"); svg.appendChild(g);
   g.appendChild(el("line",{x1:X0,y1:RY,x2:X0+PW,y2:RY,stroke:"#3a434f"}));
   for(let v=Math.ceil(lo/5)*5;v<=hi;v+=5){ g.appendChild(el("line",{x1:sx(v),y1:RY-4,x2:sx(v),y2:RY+4,stroke:"#3a434f"}));
     const t=el("text",{x:sx(v),y:RY+18,fill:"#6b7580","font-size":10,"text-anchor":"middle","font-family":"sans-serif"});t.textContent=v;g.appendChild(t);}
   for(const v of S) g.appendChild(el("circle",{cx:sx(v),cy:RY-16,r:2.6,fill:"#6ab0f3","fill-opacity":.55}));
   const Q1=q(25),Q2=q(50),Q3=q(75),IQR=Q3-Q1,fLo=Q1-1.5*IQR,fHi=Q3+1.5*IQR;
   const inLo=S.filter(v=>v>=fLo)[0], inHi=[...S].reverse().find(v=>v<=fHi);
   const bh=40;
   if(step>=1){
     g.appendChild(el("rect",{x:sx(Q1),y:AY-bh,width:sx(Q3)-sx(Q1),height:2*bh,fill:"#5fd08a","fill-opacity":.14,stroke:"#5fd08a","stroke-width":2}));
     lab(g,sx(Q1),AY-bh-6,"Q1",-1,"#5fd08a"); lab(g,sx(Q3),AY-bh-6,"Q3",1,"#5fd08a");
   }
   if(step>=2){
     g.appendChild(el("line",{x1:sx(Q2),y1:AY-bh,x2:sx(Q2),y2:AY+bh,stroke:"#ffffff","stroke-width":2.5}));
     lab(g,sx(Q2),AY+bh+16,"медиана",0,"#ffffff");
   }
   if(step>=3){
     [fLo,fHi].forEach(f=>{ if(f>lo&&f<hi) g.appendChild(el("line",{x1:sx(f),y1:AY-bh-6,x2:sx(f),y2:AY+bh+6,stroke:"#5a4a27","stroke-width":1,"stroke-dasharray":"3 3"})); });
     g.appendChild(el("line",{x1:sx(Q1),y1:AY,x2:sx(inLo),y2:AY,stroke:"#a7b0ba","stroke-width":1.6}));
     g.appendChild(el("line",{x1:sx(Q3),y1:AY,x2:sx(inHi),y2:AY,stroke:"#a7b0ba","stroke-width":1.6}));
     g.appendChild(el("line",{x1:sx(inLo),y1:AY-10,x2:sx(inLo),y2:AY+10,stroke:"#a7b0ba","stroke-width":1.6}));
     g.appendChild(el("line",{x1:sx(inHi),y1:AY-10,x2:sx(inHi),y2:AY+10,stroke:"#a7b0ba","stroke-width":1.6}));
     lab(g,sx(fLo),AY-bh-12,"забор −1.5·IQR",0,"#8a7440"); lab(g,sx(fHi),AY-bh-12,"забор +1.5·IQR",0,"#8a7440");
   }
   if(step>=4){
     for(const v of S) if(v<fLo||v>fHi) g.appendChild(el("circle",{cx:sx(v),cy:AY,r:4,fill:"#e0757f",stroke:"#0b0f14","stroke-width":1}));
   }
   const outs=S.filter(v=>v<fLo||v>fHi);
   ro.innerHTML="Q1="+Q1.toFixed(1)+" · медиана="+Q2.toFixed(1)+" · Q3="+Q3.toFixed(1)
     +" · IQR=Q3−Q1="+IQR.toFixed(1)+" · забор=["+fLo.toFixed(1)+", "+fHi.toFixed(1)+"] · выбросов: "+outs.length;
 }
 sl.addEventListener("input",render); render();
})();
""".replace("__W__", _W)

display(HTML(viz(figure, script, wide=True)))
display(HTML(viz(dots)))''')

code(r'''#@title Теория — Правила и статистический смысл { display-mode: "form" }
rules = r"""
<div class="box def"><div class="t">Правила и нюансы построения</div>
<ul>
<li><b>Ящик</b> <span class="en">(box)</span> — от Q1 до Q3; линия внутри — медиана.</li>
<li><b>Забор</b> <span class="en">(fence)</span>: $Q_1-1{,}5\cdot\mathrm{IQR}$ и
$Q_3+1{,}5\cdot\mathrm{IQR}$. Множитель $1{,}5$ — соглашение Тьюки <span class="en">(Tukey)</span>;
иногда берут $3$ для «крайних» выбросов.</li>
<li><b>Усы</b> <span class="en">(whiskers)</span> тянутся <b>не до забора</b>, а до <b>последнего
реального наблюдения внутри</b> забора — поэтому ус всегда заканчивается на настоящем значении из данных.</li>
<li><b>Точки за усами</b> — выбросы.</li>
<li>Боксплот <b>не показывает форму</b>: очень разные распределения (например, бимодальное и
одногорбое) могут дать одинаковый ящик. Форму смотрят гистограммой/KDE — боксплот их дополняет, а не заменяет.</li>
<li>Рисуют и горизонтально, и вертикально — суть одна.</li>
</ul></div>
"""

meaning = r"""
<div class="box take"><div class="t">Статистический смысл</div>
<ul>
<li>Каждая из четырёх частей (до Q1, Q1–Q2, Q2–Q3, после Q3) содержит примерно <b>25%</b>
наблюдений; ящик — это <b>средние 50%</b>.</li>
<li>Положение медианы в ящике и длины усов — наглядная мера <b>асимметрии</b>: медиана ближе к Q1 и
длиннее верхний ус ⇒ распределение скошено вправо.</li>
<li>Всё построено на <b>порядковых статистиках</b>, а не на среднем и σ, поэтому боксплот
<b>устойчив к выбросам</b> — в отличие от мер из части 1.</li>
</ul></div>
"""

display(HTML(viz(rules)))
display(HTML(viz(meaning)))''')

code(r'''#@title Теория — Сравнение групп боксплотами { display-mode: "form" }
import json, numpy as np
_M  = json.dumps([round(float(v), 1) for v in np.sort(men_h)])
_W2 = json.dumps([round(float(v), 1) for v in np.sort(women_h)])

figure = r"""
<div class="widget"><div class="widget-title">Рост мужчин и женщин (Davis) — два боксплота</div>
<div class="widget-sub">Два ящика на одной шкале роста (см). Именно так боксплоты и применяют —
чтобы сравнить группы одним взглядом.</div>
<svg viewBox="0 0 760 220" id="svg-cmp"></svg></div>
"""

seen = r"""
<div class="box idea"><div class="t">Что сразу видно</div>
У мужчин медиана роста <b>выше</b>, а ящик (IQR) чуть <b>шире</b> — разброс больше. У женщин снизу
торчат <span style="color:#e0757f">точки-выбросы</span> — необычно низкие значения. Все вопросы из
начала блока получают ответ одним взглядом.</div>
"""

teaser = r"""
<div class="box take"><div class="t">Дальше</div>
IQR мы определили как $Q_3-Q_1$. В следующей части — <b>как им пользуются</b>: чистить выбросы
«по $1{,}5\cdot$IQR» и нормировать данные через <b>медиану и IQR</b> — устойчивый аналог
z-стандартизации.</div>
"""

script = r"""
(function(){
 const svg=document.getElementById("svg-cmp"); if(!svg) return;
 const M=__M__, W=__W2__;
 const CW=760,CH=220, ML=74,MR=24,MT=22,MB=42, PW=CW-ML-MR, X0=ML;
 const all=M.concat(W); let lo=Math.min.apply(null,all), hi=Math.max.apply(null,all);
 const pad=(hi-lo)*0.06||1; lo-=pad; hi+=pad;
 const sx=v=>X0+(v-lo)/(hi-lo)*PW;
 const q=(S,p)=>{const n=S.length,h=(n-1)*p/100,k=Math.floor(h);return k>=n-1?S[n-1]:S[k]+(h-k)*(S[k+1]-S[k]);};
 const g=el("g"); svg.appendChild(g);
 const AXY=CH-MB+6;
 g.appendChild(el("line",{x1:X0,y1:AXY,x2:X0+PW,y2:AXY,stroke:"#3a434f"}));
 for(let v=Math.ceil(lo/5)*5;v<=hi;v+=5){ g.appendChild(el("line",{x1:sx(v),y1:AXY-3,x2:sx(v),y2:AXY+3,stroke:"#3a434f"}));
   const t=el("text",{x:sx(v),y:AXY+16,fill:"#6b7580","font-size":10,"text-anchor":"middle","font-family":"sans-serif"});t.textContent=v;g.appendChild(t);}
 function boxplot(arr,cy,col,name){
   const S=[...arr].sort((a,b)=>a-b);
   const Q1=q(S,25),Q2=q(S,50),Q3=q(S,75),IQR=Q3-Q1,fLo=Q1-1.5*IQR,fHi=Q3+1.5*IQR;
   const inLo=S.filter(v=>v>=fLo)[0], inHi=[...S].reverse().find(v=>v<=fHi);
   const bh=26;
   g.appendChild(el("line",{x1:sx(Q1),y1:cy,x2:sx(inLo),y2:cy,stroke:"#a7b0ba"}));
   g.appendChild(el("line",{x1:sx(Q3),y1:cy,x2:sx(inHi),y2:cy,stroke:"#a7b0ba"}));
   g.appendChild(el("line",{x1:sx(inLo),y1:cy-8,x2:sx(inLo),y2:cy+8,stroke:"#a7b0ba"}));
   g.appendChild(el("line",{x1:sx(inHi),y1:cy-8,x2:sx(inHi),y2:cy+8,stroke:"#a7b0ba"}));
   g.appendChild(el("rect",{x:sx(Q1),y:cy-bh,width:sx(Q3)-sx(Q1),height:2*bh,fill:col,"fill-opacity":.16,stroke:col,"stroke-width":2}));
   g.appendChild(el("line",{x1:sx(Q2),y1:cy-bh,x2:sx(Q2),y2:cy+bh,stroke:"#ffffff","stroke-width":2.5}));
   for(const v of S) if(v<fLo||v>fHi) g.appendChild(el("circle",{cx:sx(v),cy:cy,r:4,fill:"#e0757f",stroke:"#0b0f14","stroke-width":1}));
   const t=el("text",{x:X0-12,y:cy+4,fill:col,"font-size":12,"font-weight":700,"text-anchor":"end","font-family":"sans-serif"});t.textContent=name;g.appendChild(t);
 }
 boxplot(M, MT+42, "#6ab0f3", "мужчины");
 boxplot(W, MT+104, "#e0757f", "женщины");
})();
""".replace("__M__", _M).replace("__W2__", _W2)

display(HTML(viz(figure, script, wide=True)))
display(HTML(viz(seen)))
display(HTML(viz(teaser)))''')

md(r"""
### Гайд: боксплоты в seaborn (`sns.boxplot`)

В Python боксплоты удобнее всего рисовать через seaborn. По шагам.

**Один признак.** Столбец передают в `x` (горизонтальный ящик) или `y` (вертикальный):

```python
import seaborn as sns
sns.boxplot(data=df, x="price_usd")     # горизонтальный
sns.boxplot(data=df, y="price_usd")     # вертикальный
```

**По группам.** Категориальный признак — на одну ось, числовой — на другую; получится по ящику на категорию:

```python
sns.boxplot(data=df, x="rooms_n", y="price_usd")   # ящик цены для каждого числа комнат
```

**Цвет и подгруппы — `hue`.** `hue` делит каждую категорию ещё на подгруппы разного цвета:

```python
sns.boxplot(data=df, x="rooms_n", y="price_usd", hue="deal")   # продажа/аренда рядом
```

**Палитра и порядок.** `palette` задаёт цвета, `order` / `hue_order` — порядок категорий:

```python
sns.boxplot(data=df, x="condition", y="ppm2",
            order=["евроремонт", "хорошее", "среднее"], palette="viridis")
```

**Полезные детали.**

- `whis=1.5` — множитель усов (по умолчанию 1.5·IQR; `whis=3` — для «крайних» выбросов);
- `showfliers=False` — скрыть точки-выбросы;
- поверх ящиков можно наложить сами наблюдения через `stripplot`:

```python
ax = sns.boxplot(data=df, x="rooms_n", y="price_usd", showfliers=False)
sns.stripplot(data=df, x="rooms_n", y="price_usd", ax=ax, color="k", size=2, alpha=.3)
```
""")

# ============================================================================
# Part 3 — Cleaning outliers
# ============================================================================
code(r'''#@title Теория — Чистка выбросов: проценты и усы { display-mode: "form" }
intro = r"""
<h2>Часть 3 — Чистка выбросов</h2>
<p>Выбросы искажают среднее и σ (часть 1) и мешают моделям. Два простых непараметрических способа
их отсечь — <b>по процентам</b> и <b>по усам</b>.</p>
<div class="box def"><div class="t">Способ 1. По процентам <span class="en">(percentile trimming)</span></div>
Отрезаем по несколько процентов с каждого края: например, всё ниже 1-го и выше 99-го перцентиля —
оставляем $[\,Q(p),\,Q(100-p)\,]$.
<ul>
<li>+ просто и предсказуемо: всегда удаляет <b>ровно</b> $2p\%$ данных;</li>
<li>− режет фиксированную долю <em>даже если выбросов нет</em>, и симметрично по числу, не глядя на форму.</li>
</ul>
Вариант «не удалять, а прижать к границе» называют <b>винзоризацией</b> <span class="en">(winsorizing)</span>.</div>
"""

fence = r"""
<div class="box def"><div class="t">Способ 2. По усам боксплота <span class="en">(Tukey fence)</span></div>
Отрезаем всё за забором $[\,Q_1-1{,}5\cdot\mathrm{IQR},\; Q_3+1{,}5\cdot\mathrm{IQR}\,]$ — те самые
точки за усами.
<ul>
<li>+ <b>адаптивно</b>: нет хвостов — не удалит ничего; шире разброс — дальше забор;</li>
<li>− забор <b>симметричен</b> вокруг ящика, а на скошенных данных это перекос: длинный правый хвост
будет помечен целиком, хотя это нормальная часть распределения.</li>
</ul></div>
"""

fig = r"""
<div class="widget"><div class="widget-title">Две границы на цене квартир Бишкека</div>
<div class="widget-sub">Кривая плотности (KDE) цены (тыс. USD).
<span style="color:#e0757f">Розовый пунктир</span> — отсечение по процентам ($p$ с краёв);
<span style="color:#e0b25a">жёлтый пунктир</span> — забор 1.5·IQR. Двигайте $p$ и сравнивайте,
сколько удаляет каждый способ.</div>
<svg viewBox="0 0 760 320" id="svg-cl"></svg>
<div class="controls">
<div class="control"><label>p (% с каждого края) =</label>
<input type="range" id="cl-p" min="0" max="10" step="0.5" value="1"><span class="val" id="cl-pv">1</span></div>
</div>
<div class="readout" id="cl-ro"></div></div>
"""

choose = r"""
<div class="box take"><div class="t">Что выбрать</div>
На умеренно симметричных данных — <b>по усам</b> (адаптивно). На сильно скошенных сначала лучше
выправить форму (например, логарифмом) или резать по процентам осознанно. И всегда: выброс — не
всегда ошибка; прежде чем удалять, <b>посмотри</b>, что это за наблюдения.</div>
"""

import json, numpy as np
_rng = np.random.default_rng(1)
_pr = price[price > 0]
_prs = _rng.choice(_pr, size=min(3000, len(_pr)), replace=False)
PRICE_JSON = json.dumps([round(float(v), 1) for v in _prs])

script = r"""
(function(){
 const svg=document.getElementById("svg-cl"); if(!svg) return;
 const S=__PRICE__.slice().sort((a,b)=>a-b), n=S.length;
 const sl=document.getElementById("cl-p"), pv=document.getElementById("cl-pv"), ro=document.getElementById("cl-ro");
 const CW=760,CH=320, ML=46,MR=20,MT=22,MB=44, PW=CW-ML-MR,PH=CH-MT-MB, X0=ML,Y0=MT+PH, XMAX=500;
 const sx=v=>X0+Math.min(v,XMAX)/XMAX*PW;
 const q=p=>{const h=(n-1)*p/100,k=Math.floor(h);return k>=n-1?S[n-1]:S[k]+(h-k)*(S[k+1]-S[k]);};
 const kde=(arr,xs,hh)=>{const c=1/(arr.length*hh*Math.sqrt(2*Math.PI));return xs.map(x=>{let s=0;for(const xi of arr){const u=(x-xi)/hh;s+=Math.exp(-0.5*u*u);}return c*s;});};
 function render(){
   const p=+sl.value; pv.textContent=p;
   while(svg.firstChild) svg.removeChild(svg.firstChild);
   const g=el("g"); svg.appendChild(g);
   g.appendChild(el("rect",{x:X0,y:MT,width:PW,height:PH,fill:"#0b0f14",stroke:"#2a313b"}));
   for(let t=0;t<=XMAX;t+=100){ g.appendChild(el("line",{x1:sx(t),y1:MT,x2:sx(t),y2:Y0,stroke:"#19212c"}));
     const l=el("text",{x:sx(t),y:Y0+15,fill:"#6b7580","font-size":10,"text-anchor":"middle","font-family":"sans-serif"});l.textContent=t+"k";g.appendChild(l);}
   const inr=S.filter(v=>v<XMAX);
   const m=inr.reduce((a,b)=>a+b,0)/inr.length, sd=Math.sqrt(inr.reduce((a,x)=>a+(x-m)*(x-m),0)/inr.length);
   const hh=Math.max(6,1.06*sd*Math.pow(inr.length,-0.2));
   const G=200,xs=[];for(let i=0;i<G;i++)xs.push(XMAX*i/(G-1));
   const dens=kde(inr,xs,hh),dmax=Math.max.apply(null,dens)||1, syD=d=>Y0-d/dmax*(PH*0.9);
   let pth="M "+sx(0).toFixed(1)+" "+Y0+" ";
   for(let i=0;i<G;i++)pth+="L "+sx(xs[i]).toFixed(1)+" "+syD(dens[i]).toFixed(1)+" ";
   pth+="L "+sx(XMAX).toFixed(1)+" "+Y0+" Z";
   g.appendChild(el("path",{d:pth,fill:"#6ab0f3","fill-opacity":.15,stroke:"#6ab0f3","stroke-width":1.5}));
   const pLo=q(p),pHi=q(100-p);
   const Q1=q(25),Q3=q(75),IQR=Q3-Q1,fLo=Math.max(0,Q1-1.5*IQR),fHi=Q3+1.5*IQR;
   const vline=(x,col,dash)=>{ if(x<=XMAX) g.appendChild(el("line",{x1:sx(x),y1:MT,x2:sx(x),y2:Y0,stroke:col,"stroke-width":2,"stroke-dasharray":dash})); };
   vline(pLo,"#e0757f","5 4"); vline(pHi,"#e0757f","5 4"); vline(fLo,"#e0b25a","2 3"); vline(fHi,"#e0b25a","2 3");
   const remP=S.filter(v=>v<pLo||v>pHi).length, remF=S.filter(v=>v<fLo||v>fHi).length;
   ro.innerHTML="<span style='color:#e0757f'>проценты "+p+"%</span>: [ "+pLo.toFixed(0)+"k, "+pHi.toFixed(0)+"k ] → удалено "+(100*remP/n).toFixed(1)+"%"
     +" &nbsp;|&nbsp; <span style='color:#e0b25a'>усы 1.5·IQR</span>: [ "+fLo.toFixed(0)+"k, "+fHi.toFixed(0)+"k ] → удалено "+(100*remF/n).toFixed(1)+"%";
 }
 sl.addEventListener("input",render); render();
})();
""".replace("__PRICE__", PRICE_JSON)

display(HTML(viz(intro)))
display(HTML(viz(fence)))
display(HTML(viz(fig, script, wide=True)))
display(HTML(viz(choose)))''')

md(r"""
### Как чистить в коде

```python
import numpy as np
s = df["price_usd"]

# способ 1 — по процентам (1% с каждого края)
lo, hi = np.percentile(s, [1, 99])
clean_pct = s[(s >= lo) & (s <= hi)]

# способ 2 — по усам (1.5·IQR)
q1, q3 = np.percentile(s, [25, 75])
iqr = q3 - q1
lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
clean_iqr = s[(s >= lo) & (s <= hi)]

print(len(s) - len(clean_pct), "удалено по процентам")
print(len(s) - len(clean_iqr), "удалено по усам")
```
""")

# ============================================================================
# Part 4 — IQR as robust sigma; RobustScaler; kNN context
# ============================================================================
code(r'''#@title Теория — IQR как робастная σ и RobustScaler { display-mode: "form" }
iqr_sigma = r"""
<h2>Часть 4 — IQR как робастная σ и RobustScaler</h2>
<div class="box idea"><div class="t">IQR — устойчивый аналог σ</div>
И σ, и IQR измеряют разброс. Но σ считается через <b>квадраты</b> отклонений (часть 1) и потому
раздувается от выбросов, а <b>IQR</b> $=Q_3-Q_1$ смотрит только на середину и выбросов не замечает.
Для нормального распределения они прямо связаны: $\sigma \approx \mathrm{IQR}/1{,}349$. То есть IQR —
это та же σ, но <b>робастная</b>.</div>
"""

robust = r"""
<div class="box def"><div class="t">Робастная стандартизация <span class="en">(RobustScaler)</span></div>
Вспомним z-стандартизацию $z=(x-\bar x)/\sigma$. Заменим неустойчивые центр и масштаб на робастные —
медиану и IQR:
$$ x_{\text{rob}}=\frac{x-\mathrm{median}}{\mathrm{IQR}}. $$
Это ровно то, что делает <code>sklearn.preprocessing.RobustScaler</code>. Медиана и IQR не
раздуваются выбросами, поэтому масштаб признака ставится <b>по основной массе</b> данных, а не по хвосту.</div>
"""

knn = r"""
<div class="box take"><div class="t">Связь с поиском соседей (kNN)</div>
Зачем мы стандартизовали признаки в прошлом колабе? Чтобы <b>евклидово расстояние было честным</b> и
соседи находились правильно: без масштабирования признак с крупными числами давит остальные. Но у
обычной z-стандартизации есть слабость — <b>σ сама раздувается выбросом</b>: признак с выбросом
получает большую σ, его z-значения сжимаются, и он <em>недооценивается</em> в расстоянии.
<p style="margin-bottom:0"><b>Можно ли брать робастный скейлинг для kNN? Да, и часто он лучше.</b>
<code>RobustScaler</code> ставит масштаб по медиане и IQR, которые выброс не сдвигает, — вклад
признаков уравнивается по <b>типичному</b> разбросу, и соседи находятся корректнее. Оговорка: сам
скейлинг <b>не удаляет</b> выбросы — экстремальная координата отдельного объекта всё ещё раздувает его
расстояния. Поэтому на практике комбинируют: робастный масштаб + при необходимости отсечение или лог.</p></div>
"""

display(HTML(viz(iqr_sigma)))
display(HTML(viz(robust)))
display(HTML(viz(knn)))''')

md(r"""
### RobustScaler в коде

```python
from sklearn.preprocessing import RobustScaler, StandardScaler
import numpy as np

X = df[["price_usd", "area_m2", "rooms_n"]].to_numpy(float)

Xz   = StandardScaler().fit_transform(X)   # (x - mean) / std   — чувствителен к выбросам
Xrob = RobustScaler().fit_transform(X)     # (x - median) / IQR — устойчив к выбросам

# руками, для одного столбца:
col = X[:, 0]
med = np.median(col)
iqr = np.percentile(col, 75) - np.percentile(col, 25)
col_rob = (col - med) / iqr
```
""")

md(r"""
### Задания — боксплоты на данных Бишкека

Датасет house.kg (Бишкек, квартиры). Строй боксплоты **с группировкой** и к каждому пиши вывод словами.

**Task 1.** Боксплот цены за м² (`ppm2`) по числу комнат (`rooms_n`). Растёт ли медиана с числом комнат? В какой группе разброс (IQR) больше?

**Task 2.** Боксплот `ppm2` по состоянию (`condition`), упорядочив категории. Насколько «евроремонт» дороже «под самоотделку» по медиане?

**Task 3.** Боксплот `ppm2` по серии дома (`building_series`, оставь серии с ≥100 объявлений). У какой серии самая высокая медиана — совпадает ли с интуицией «элитка дороже»?

**Task 4.** Сравни продажу и аренду через `hue="deal"` — но сначала реши, можно ли вообще класть их на одну шкалу (вспомни: total vs month/day).

**Task 5.** Почисти цену от выбросов двумя способами (по процентам и по усам). Сколько удалил каждый? Как изменился боксплот? Какой способ уместнее на скошенной цене и почему?

**Task 6.** Отмасштабируй `price_usd`, `area_m2`, `rooms_n` через `StandardScaler` и `RobustScaler`, найди 5 ближайших соседей заданной квартиры в обоих пространствах. Отличаются ли списки соседей? Почему при выбросах робастный масштаб может дать более честных соседей?
""")

# ============================================================================
# Write
# ============================================================================
nb = new_notebook(cells=cells)
nb.metadata = META
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "04_stat_boxplot.ipynb")
with open(out, "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("wrote", out, "cells:", len(cells))
