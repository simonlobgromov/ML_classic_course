# -*- coding: utf-8 -*-
"""Собирает Colab-ноутбук «Урок 1. Векторы» (тёмная тема, интерактив в #@title-ячейках).
Запуск:  ./venv/bin/python linear_algebra/build_lesson1.py
Результат: linear_algebra/01_vectors.ipynb
"""
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

cells = []
def md(src):   cells.append(new_markdown_cell(src))
def code(src): cells.append(new_code_cell(src))

# ============================================================================
# 0. Заголовок
# ============================================================================
md(r"""# Линейная алгебра для Data Science
## Урок 1 — Вектор: наблюдение как точка в пространстве признаков

Наша цель — перестать видеть в датасете таблицу и научиться
видеть **точки в пространстве**. Работаем на реальном датасете `Davis` (рост и вес 200
человек): каждая строка станет вектором, а весь датасет — облаком точек.

> Ячейки с теорией свёрнуты (`#@title`) — разверните код, если хотите заглянуть внутрь
> визуализации. Формулы и графики можно и нужно **крутить руками**: векторы на графиках
> перетаскиваются мышью.
""")

# ============================================================================
# 1. Загрузка данных
# ============================================================================
code(r"""import numpy as np
import pandas as pd
from datasets import load_dataset

dataset = load_dataset('aiacademy-kg/davis_dataset', split='train')
df = dataset.to_pandas()""")

code(r"""df.head()""")

# ============================================================================
#  Оформление: CSS (тёмная тема), JS-хелперы, функция viz()
# ============================================================================
code(r'''#@title Оформление и хелперы визуализации — запустите первой { display-mode: "form" }
from IPython.display import HTML, display

CSS = r"""
.vec-root{--bg:#12161c;--surface:#1a1f27;--ink:#e6e9ec;--soft:#a7b0ba;--line:#2a313b;
  --green:#5fd08a;--blue:#6ab0f3;--amber:#e0b25a;--rose:#e0757f;
  font-family:Georgia,'Times New Roman',serif;color:var(--ink);
  background:var(--bg);border-radius:14px;padding:2px 0;}
.vec-root .wrap{max-width:820px;margin:0 auto;padding:18px 22px;font-size:17px;line-height:1.65;}
.vec-root h2{font-family:-apple-system,'Segoe UI',sans-serif;font-size:1.5rem;color:#fff;
  border-top:2px solid var(--line);padding-top:.5em;margin:1.4em 0 .5em;}
.vec-root h3{font-family:sans-serif;color:var(--green);font-size:1.15rem;margin:1.3em 0 .3em;}
.vec-root p{margin:.6em 0;} .vec-root b,.vec-root strong{color:#fff;}
.vec-root em{color:var(--soft);} .vec-root ul,.vec-root ol{padding-left:1.4em;} .vec-root li{margin:.28em 0;}
.vec-root a{color:var(--green);}
.vec-root .box{border-radius:12px;padding:14px 18px;margin:1.2em 0;font-family:sans-serif;
  font-size:.95rem;border:1px solid var(--line);background:var(--surface);}
.vec-root .box .t{font-weight:700;font-size:.8rem;letter-spacing:.06em;text-transform:uppercase;margin-bottom:5px;}
.vec-root .box.def{background:#15251d;border-color:#27503a;} .vec-root .box.def .t{color:var(--green);}
.vec-root .box.idea{background:#14202e;border-color:#274a63;} .vec-root .box.idea .t{color:var(--blue);}
.vec-root .box.warn{background:#241f14;border-color:#5a4a27;} .vec-root .box.warn .t{color:var(--amber);}
.vec-root .box.take{background:#241419;border-color:#5a2730;} .vec-root .box.take .t{color:var(--rose);}
.vec-root .widget{border:1px solid var(--line);border-radius:12px;background:var(--surface);
  padding:16px;margin:1.4em 0;}
.vec-root .widget-title{font-family:sans-serif;font-weight:700;font-size:.95rem;margin-bottom:2px;color:#fff;}
.vec-root .widget-sub{font-family:sans-serif;font-size:.83rem;color:var(--soft);margin-bottom:10px;}
.vec-root .widget>svg{display:block;width:100%;height:auto;background:#0e1319;border-radius:10px;}
.vec-root .controls{display:flex;flex-wrap:wrap;gap:12px 20px;align-items:center;margin-top:12px;
  font-family:sans-serif;font-size:.88rem;color:var(--soft);}
.vec-root .control{display:flex;align-items:center;gap:8px;}
.vec-root input[type=range]{accent-color:var(--green);width:150px;}
.vec-root .val{font-family:'SF Mono',Menlo,monospace;font-size:.82rem;color:var(--green);min-width:40px;}
.vec-root .btn{font-family:sans-serif;font-size:.85rem;font-weight:600;border:1px solid var(--green);
  background:transparent;color:var(--green);padding:6px 14px;border-radius:8px;cursor:pointer;}
.vec-root .btn:hover{background:var(--green);color:#0e1319;}
.vec-root .readout{font-family:'SF Mono',Menlo,monospace;font-size:.84rem;background:#0e1319;
  padding:9px 12px;border-radius:8px;margin-top:12px;color:var(--soft);}
.vec-root .gridline{stroke:#20272f;stroke-width:1;} .vec-root .axis{stroke:#3a434f;stroke-width:1.2;}
.vec-root .tick-label{font-family:sans-serif;font-size:11px;fill:#6b7580;}
.vec-root code{font-family:Menlo,monospace;font-size:.86em;background:#0e1319;color:var(--amber);
  padding:1px 6px;border-radius:5px;}
.vec-root details{border:1px dashed #38414c;border-radius:10px;padding:4px 16px;margin:1.1em 0;background:#161b22;}
.vec-root summary{cursor:pointer;font-family:sans-serif;font-weight:700;color:var(--blue);padding:8px 0;}
"""

JS = r"""
if(!window.__VEC_READY__){window.__VEC_READY__=true;
const NS="http://www.w3.org/2000/svg";
window.scale=(d,r)=>{const[a,b]=d,[c,e]=r;return v=>c+(v-a)*(e-c)/(b-a);};
window.el=(t,at={})=>{const x=document.createElementNS(NS,t);for(const k in at)x.setAttribute(k,at[k]);return x;};
window.clamp=(v,lo,hi)=>Math.max(lo,Math.min(hi,v));
window.arrow=(x1,y1,x2,y2,o={})=>{const g=el("g");const c=o.color||"#5fd08a",w=o.width||2.6;
  const ln={x1,y1,x2,y2,stroke:c,"stroke-width":w,"stroke-linecap":"round"};if(o.dash)ln["stroke-dasharray"]=o.dash;
  g.appendChild(el("line",ln));const L=Math.hypot(x2-x1,y2-y1);
  if(L>4){const an=Math.atan2(y2-y1,x2-x1),hl=o.head||12,ha=.42;
   const p1x=x2-hl*Math.cos(an-ha),p1y=y2-hl*Math.sin(an-ha),p2x=x2-hl*Math.cos(an+ha),p2y=y2-hl*Math.sin(an+ha);
   g.appendChild(el("polygon",{points:`${x2},${y2} ${p1x},${p1y} ${p2x},${p2y}`,fill:c}));}return g;};
window.svgPoint=(svg,ev)=>{const p=svg.createSVGPoint();const s=(ev.touches&&ev.touches.length)?ev.touches[0]:ev;
  p.x=s.clientX;p.y=s.clientY;return p.matrixTransform(svg.getScreenCTM().inverse());};
window.onDrag=(svg,h,cb)=>{let on=false;const st=e=>{on=true;e.preventDefault();};
  const mv=e=>{if(!on)return;e.preventDefault();cb(svgPoint(svg,e));};const en=()=>on=false;
  h.style.cursor="grab";h.addEventListener("mousedown",st);h.addEventListener("touchstart",st,{passive:false});
  window.addEventListener("mousemove",mv);window.addEventListener("touchmove",mv,{passive:false});
  window.addEventListener("mouseup",en);window.addEventListener("touchend",en);};
window.drawFrame=(g,c)=>{const{x,y,x0,x1,y0,y1,xt=[],yt=[]}=c;
  for(const tx of xt){g.appendChild(el("line",{x1:x(tx),y1:y(y0),x2:x(tx),y2:y(y1),class:"gridline"}));
    const t=el("text",{x:x(tx),y:y(y0)+15,class:"tick-label","text-anchor":"middle"});t.textContent=tx;g.appendChild(t);}
  for(const ty of yt){g.appendChild(el("line",{x1:x(x0),y1:y(ty),x2:x(x1),y2:y(ty),class:"gridline"}));
    const t=el("text",{x:x(x0)-8,y:y(ty)+4,class:"tick-label","text-anchor":"end"});t.textContent=ty;g.appendChild(t);}
  const ax=(y0<=0&&y1>=0)?0:y0,ay=(x0<=0&&x1>=0)?0:x0;
  g.appendChild(el("line",{x1:x(x0),y1:y(ax),x2:x(x1),y2:y(ax),class:"axis"}));
  g.appendChild(el("line",{x1:x(ay),y1:y(y0),x2:x(ay),y2:y(y1),class:"axis"}));};
const W=600,H=380,PL=36,PR=16,PT=16,PB=28;
window.X0=-6;window.X1=6;window.Y0=-3.7;window.Y1=3.7;
window.SX=scale([X0,X1],[PL,W-PR]);window.SY=scale([Y0,Y1],[H-PB,PT]);
window.IX=scale([PL,W-PR],[X0,X1]);window.IY=scale([H-PB,PT],[Y0,Y1]);
window.OX=SX(0);window.OY=SY(0);window.XT=[-6,-4,-2,2,4,6];window.YT=[-3,-1,1,3];
window.COL={a:"#6ab0f3",b:"#e0b25a",sum:"#e0757f",v:"#6ab0f3",res:"#5fd08a"};
window.freshFrame=(svg)=>{while(svg.firstChild)svg.removeChild(svg.firstChild);
  const g=el("g");svg.appendChild(g);drawFrame(g,{x:SX,y:SY,x0:X0,x1:X1,y0:Y0,y1:Y1,xt:XT,yt:YT});return g;};
window.handle=(g,dx,dy,color,onMove,svg)=>{const c=el("circle",{cx:SX(dx),cy:SY(dy),r:9,
  fill:color,"fill-opacity":.25,stroke:color,"stroke-width":2});g.appendChild(c);
  onDrag(svg,c,p=>onMove(clamp(IX(p.x),X0,X1),clamp(IY(p.y),Y0,Y1)));return c;};
window.label=(g,dx,dy,text,color)=>{const t=el("text",{x:SX(dx),y:SY(dy),fill:color,
  "font-family":"-apple-system,Segoe UI,sans-serif","font-size":15,"font-weight":700});
  t.textContent=text;g.appendChild(t);return t;};
}
"""

MJ_CFG = "<script>window.MathJax=window.MathJax||{tex:{inlineMath:[['$','$']],displayMath:[['$$','$$']]},svg:{fontCache:'global'}};</script>"
MJ = '<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>'

def viz(body, script=""):
    """Обернуть HTML-тело темой + хелперами + MathJax. Каждый вывод самодостаточен (важно для Colab)."""
    head = "<style>" + CSS + "</style>"
    tail = ("<script>" + JS + "\n" + script +
            "\nif(window.MathJax&&MathJax.typesetPromise){MathJax.typesetPromise();}</script>")
    return head + '<div class="vec-root"><div class="wrap">' + body + "</div></div>" + MJ_CFG + MJ + tail

print("Оформление загружено. Функция viz() готова.")''')

# ============================================================================
# 2. ТЕОРИЯ 1 — векторное пространство и вектор
# ============================================================================
code(r'''#@title Теория 1 — Векторное пространство и вектор { display-mode: "form" }
body = r"""
<h2>1. Наблюдение, признак, вектор</h2>

<p>Пусть дана таблица данных. Её строки называют <b>наблюдениями</b> (или объектами):
это отдельные измеренные сущности — человек, транзакция, день. Столбцы называют
<b>признаками</b>: это измеряемые величины — рост, вес, температура. В датасете
<code>Davis</code> наблюдение — это человек, а числовые признаки — вес и рост.</p>

<p>Упорядоченный набор из $n$ чисел
$$ a = (a_1,\, a_2,\, \ldots,\, a_n) $$
называется <b>$n$-мерным вектором</b>. Числа $a_1,\ldots,a_n$ — его <b>координаты</b>.
Одно наблюдение с $n$ числовыми признаками есть вектор: значение первого признака —
первая координата, второго — вторая, и так далее. Условимся записывать наблюдение
вектором-столбцом, а в строку писать лишь для краткости.</p>

<div class="box def"><div class="t">Определение</div>
Множество всех $n$-мерных векторов с вещественными координатами обозначают
$\mathbb{R}^n$ и называют <b>вещественным координатным пространством</b> размерности $n$.
Запись $a \in \mathbb{R}^n$ читается: «вектор $a$ принадлежит пространству $\mathbb{R}^n$».
В машинном обучении $\mathbb{R}^n$, где $n$ — число признаков, называют
<b>признаковым пространством</b>, а наблюдения — его точками.</div>

<p>В $\mathbb{R}^n$ определены две операции. <b>Сложение</b> векторов
$a=(a_1,\ldots,a_n)$ и $b=(b_1,\ldots,b_n)$:
$$ a+b = (a_1+b_1,\ \ldots,\ a_n+b_n), $$
и <b>умножение вектора на число</b> $\lambda \in \mathbb{R}$:
$$ \lambda a = (\lambda a_1,\ \ldots,\ \lambda a_n). $$
Результат обеих операций снова принадлежит $\mathbb{R}^n$ — из пространства мы не выходим.</p>

<div class="box def"><div class="t">Определение (векторное пространство)</div>
<p>Множество $V$ называется <b>векторным (линейным) пространством</b> над полем вещественных
чисел $\mathbb{R}$, если на нём определены две операции:</p>
<ul>
<li><b>сложение</b> $+\colon V\times V\to V$, сопоставляющее векторам $a,b\in V$ вектор $a+b\in V$;</li>
<li><b>умножение на скаляр</b> $\cdot\colon\mathbb{R}\times V\to V$, сопоставляющее числу
$\lambda\in\mathbb{R}$ и вектору $a\in V$ вектор $\lambda a\in V$,</li>
</ul>
<p>замкнутые на $V$ (результат каждой операции вновь принадлежит $V$) и удовлетворяющие для
любых $a,b,c\in V$ и $\lambda,\mu\in\mathbb{R}$ следующим восьми аксиомам:</p>
<ol>
<li>$a+b=b+a$ — коммутативность сложения;</li>
<li>$(a+b)+c=a+(b+c)$ — ассоциативность сложения;</li>
<li>существует нулевой вектор $0\in V$, для которого $a+0=a$ при всех $a$;</li>
<li>для каждого $a\in V$ существует противоположный вектор $-a$, для которого $a+(-a)=0$;</li>
<li>$1\cdot a=a$;</li>
<li>$\lambda(\mu a)=(\lambda\mu)a$ — ассоциативность умножения на скаляр;</li>
<li>$\lambda(a+b)=\lambda a+\lambda b$ — дистрибутивность относительно сложения векторов;</li>
<li>$(\lambda+\mu)a=\lambda a+\mu a$ — дистрибутивность относительно сложения скаляров.</li>
</ol>
<p>Координатное пространство $\mathbb{R}^n$ — основной пример векторного пространства;
именно в нём разворачивается весь дальнейший курс.</p></div>

<details><summary>Замечание о размерности и о том, что «нарисовать» нельзя</summary>
<p>При $n=2$ вектор изображается точкой (или стрелкой) на плоскости, при $n=3$ — в
пространстве. При $n>3$ наглядного чертежа нет, однако все определения и формулы остаются
дословно теми же: меняется лишь число слагаемых. Реальные датасеты нередко имеют
десятки и сотни признаков ($n=50,\,300,\ldots$), и вся геометрия, освоенная на плоскости,
переносится туда без изменений. Поэтому интуицию мы строим в $\mathbb{R}^2$, а доверяем
формулам в $\mathbb{R}^n$.</p></details>

<p>Ниже — точка $a\in\mathbb{R}^2$ с координатами $(a_1,a_2)$. Перетащите её: координаты
суть длины проекций на оси, то есть значения двух признаков наблюдения.</p>

<div class="widget"><div class="widget-title">Вектор $a\in\mathbb{R}^2$ и его координаты</div>
<div class="widget-sub">Перетащите точку. Пунктир — проекции на оси признаков.</div>
<svg viewBox="0 0 600 380" id="svg-def"></svg>
<div class="readout" id="def-ro"></div></div>
"""
script = r"""
(function(){const svg=document.getElementById("svg-def");if(!svg)return;
 const ro=document.getElementById("def-ro");let v={x:3.4,y:1.9};
 function R(){const g=freshFrame(svg);
  g.appendChild(el("line",{x1:SX(v.x),y1:SY(v.y),x2:SX(v.x),y2:OY,stroke:"#4a5568","stroke-width":1.5,"stroke-dasharray":"4 4"}));
  g.appendChild(el("line",{x1:SX(v.x),y1:SY(v.y),x2:OX,y2:SY(v.y),stroke:"#4a5568","stroke-width":1.5,"stroke-dasharray":"4 4"}));
  g.appendChild(arrow(OX,OY,SX(v.x),SY(v.y),{color:COL.v,width:3}));
  handle(g,v.x,v.y,COL.v,(x,y)=>{v={x,y};R();},svg);
  label(g,v.x+.2,v.y+.35,"a",COL.v);
  label(g,v.x-.1,-.28,"a₁="+v.x.toFixed(1),"#8a929a");
  label(g,.15,v.y,"a₂="+v.y.toFixed(1),"#8a929a");
  ro.innerHTML=`a = (${v.x.toFixed(2)}, ${v.y.toFixed(2)}) ∈ ℝ²`;}
 R();})();
"""
display(HTML(viz(body, script)))''')

# ============================================================================
# 3. ТЕОРИЯ 2 — чем различаются векторы (реальные данные Davis)
# ============================================================================
code(r'''#@title Теория 2 — Чем различаются векторы (пример на Davis) { display-mode: "form" }
from itertools import combinations
P = df[['weight','height']].to_numpy(float)

best=(1e9,None); worst=(-1,None)
for i,j in combinations(range(len(P)),2):
    d=float(np.hypot(*(P[i]-P[j])))
    if 0<d<best[0]: best=(d,(i,j))
    if d>worst[0]: worst=(d,(i,j))
si,sj = best[1]; fi,fj = worst[1]
print("Похожие наблюдения (расстояние {:.1f}):".format(best[0])); print(df.iloc[[si,sj]][['sex','weight','height']])
print("\nНепохожие наблюдения (расстояние {:.1f}):".format(worst[0])); print(df.iloc[[fi,fj]][['sex','weight','height']])

Wp,Hp,pad = 600,360,44
x0,x1 = P[:,0].min()-3, P[:,0].max()+3
y0,y1 = P[:,1].min()-3, P[:,1].max()+3
sx = lambda v: pad+(v-x0)*(Wp-2*pad)/(x1-x0)
sy = lambda v: (Hp-pad)-(v-y0)*(Hp-2*pad)/(y1-y0)
dots = "".join('<circle cx="{:.1f}" cy="{:.1f}" r="3" fill="#4a5568"/>'.format(sx(w),sy(h)) for w,h in P)
def hl(i,c): return '<circle cx="{:.1f}" cy="{:.1f}" r="6.5" fill="{}" stroke="#0e1319" stroke-width="1.5"/>'.format(sx(P[i,0]),sy(P[i,1]),c)
def seg(i,j,c): return '<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}" stroke="{}" stroke-width="2" stroke-dasharray="4 3"/>'.format(sx(P[i,0]),sy(P[i,1]),sx(P[j,0]),sy(P[j,1]),c)

body = r"""
<h2>2. Чем различаются векторы</h2>
<p>Изобразим каждое наблюдение датасета точкой в признаковом пространстве $\mathbb{R}^2$
по осям <b>вес</b> (горизонталь) и <b>рост</b> (вертикаль). Тогда «похожие» наблюдения —
это <b>близкие</b> точки, а «непохожие» — <b>далёкие</b>.</p>
<div class="widget"><div class="widget-title">200 наблюдений Davis в осях «вес — рост»</div>
<div class="widget-sub"><span style="color:#5fd08a">Зелёная</span> пара — похожие люди
(точки почти совпали); <span style="color:#e0757f">красная</span> — непохожие.</div>
<svg viewBox="0 0 """ + str(Wp) + " " + str(Hp) + r"""">""" + seg(si,sj,"#5fd08a") + seg(fi,fj,"#e0757f") + dots + hl(si,"#5fd08a") + hl(sj,"#5fd08a") + hl(fi,"#e0757f") + hl(fj,"#e0757f") + r"""</svg></div>
<p>Осталось придать слову «близко» точный смысл. Близость точек измеряют <b>расстоянием</b>,
а расстояние выражается через <b>длину вектора</b> разности $a-b$. К длине и переходим.</p>
"""
display(HTML(viz(body)))''')

# ============================================================================
# 4. ТЕОРИЯ 3 — длина и направление вектора
# ============================================================================
code(r'''#@title Теория 3 — Длина (модуль) и направление вектора { display-mode: "form" }
body = r"""
<h2>3. Длина и направление</h2>

<p>Вектор задаётся координатами, но у него есть и две геометрические характеристики —
<b>длина</b> и <b>направление</b>. Начнём с плоскости, где всё сводится к теореме Пифагора,
знакомой с 8 класса.</p>

<h3>Плоскость: теорема Пифагора</h3>
<p>Стрелка вектора $a=(a_1,a_2)$ — это гипотенуза прямоугольного треугольника с катетами
$a_1$ и $a_2$. Поэтому её длину (её называют <b>модулем</b> или <b>нормой</b> и обозначают
$\lVert a\rVert$) даёт теорема Пифагора:
$$ \lVert a\rVert = \sqrt{a_1^{2}+a_2^{2}}. $$
Направление удобно задать углом $\varphi$ к оси $a_1$; координаты и длина связаны так:
$$ a_1 = \lVert a\rVert\cos\varphi, \qquad a_2 = \lVert a\rVert\sin\varphi. $$
Отсюда видно: <b>координаты — это проекции длины на оси</b>, а сама длина восстанавливается
по координатам обратно, по Пифагору.</p>

<div class="widget"><div class="widget-title">Модуль вектора как гипотенуза</div>
<div class="widget-sub">Перетащите конец вектора. Пунктирные катеты — координаты $a_1,a_2$.</div>
<svg viewBox="0 0 600 380" id="svg-len"></svg>
<div class="readout" id="len-ro"></div></div>

<h3>Общий случай: пространство $\mathbb{R}^n$</h3>
<p>В $n$-мерном пространстве прямой картинки нет, но формула обобщается дословно —
добавляются слагаемые. Модуль вектора $a=(a_1,\ldots,a_n)$ есть
$$ \lVert a\rVert=\sqrt{a_1^{2}+a_2^{2}+\cdots+a_n^{2}}=\sqrt{\sum_{i=1}^{n} a_i^{2}}. $$
Это прямое следствие теоремы Пифагора, применённой по очереди к каждой новой координате.
Такую длину называют <b>евклидовой нормой</b> (или $L_2$-нормой).</p>

<div class="box def"><div class="t">Связь координат и модуля</div>
Координаты $a_i$ — это «сколько вектора приходится на каждую ось». Модуль $\lVert a\rVert$
собирает их в единое число — <b>общий размер</b> наблюдения. Разные наборы координат могут
давать один и тот же модуль (все точки одной окружности радиуса $\lVert a\rVert$), поэтому
модуль описывает вектор не полностью — теряется направление.</div>

<div class="box idea"><div class="t">Зачем это в ML</div>
Норма — «размер» наблюдения. Расстояние между двумя наблюдениями $a$ и $b$ есть длина их
разности $\lVert a-b\rVert$ — та самая близость точек из раздела 2. На ней держатся метод
$k$ ближайших соседей, кластеризация и детекция выбросов.</div>
"""
script = r"""
(function(){const svg=document.getElementById("svg-len");if(!svg)return;
 const ro=document.getElementById("len-ro");let v={x:3.2,y:2.0};
 function R(){const g=freshFrame(svg);
  g.appendChild(el("line",{x1:OX,y1:OY,x2:SX(v.x),y2:OY,stroke:COL.b,"stroke-width":2,"stroke-dasharray":"5 4"}));
  g.appendChild(el("line",{x1:SX(v.x),y1:OY,x2:SX(v.x),y2:SY(v.y),stroke:COL.b,"stroke-width":2,"stroke-dasharray":"5 4"}));
  g.appendChild(arrow(OX,OY,SX(v.x),SY(v.y),{color:COL.v,width:3}));
  handle(g,v.x,v.y,COL.v,(x,y)=>{v={x,y};R();},svg);
  label(g,v.x/2-.3,-.28,"a₁="+v.x.toFixed(1),COL.b);
  label(g,v.x+.12,v.y/2,"a₂="+v.y.toFixed(1),COL.b);
  label(g,v.x/2+.05,v.y/2+.3,"‖a‖",COL.v);
  const n=Math.hypot(v.x,v.y),an=Math.atan2(v.y,v.x)*180/Math.PI;
  ro.innerHTML=`‖a‖ = √(${v.x.toFixed(2)}² + ${v.y.toFixed(2)}²) = <b>${n.toFixed(3)}</b> · φ ≈ ${an.toFixed(1)}°`;}
 R();})();
"""
display(HTML(viz(body, script)))''')

# ============================================================================
# 5. ЗАДАЧИ на модуль в numpy
# ============================================================================
md(r"""### Задание 1 — модуль вектора в numpy

Отработаем формулу $\lVert a\rVert=\sqrt{\sum_i a_i^2}$ на коде.

1. Для вектора `a = np.array([3, 4])` посчитайте модуль **вручную** (через `**2`, `sum`, `**0.5`)
   и сверьте с `np.linalg.norm(a)`.
2. Сделайте то же для трёхмерного `b = np.array([1, 2, 2])`. Какой ответ ожидаете до запуска?
3. Возьмите **первое наблюдение** Davis как вектор `(вес, рост)` и найдите его модуль.
""")

code(r"""# 1. Модуль вектора a = (3, 4) — вручную и через numpy
a = np.array([3, 4])

norm_manual = ...      # TODO: реализуйте формулу sqrt(суммы квадратов координат) вручную
norm_numpy  = ...      # TODO: та же величина через функцию np.linalg.norm

print('вручную:', norm_manual, ' | numpy:', norm_numpy)""")

code(r"""# 2. b = (1, 2, 2)
b = np.array([1, 2, 2])
# TODO: посчитайте модуль двумя способами и сравните
""")

code(r"""# 3. Модуль первого наблюдения Davis (вес, рост)
obs = df.iloc[0][['weight', 'height']].to_numpy(float)
print('наблюдение:', obs)
# TODO: найдите модуль этого наблюдения
""")

# ============================================================================
# 6. ТЕОРИЯ — сумма векторов
# ============================================================================
code(r'''#@title Теория 4 — Сложение векторов { display-mode: "form" }
body = r"""
<h2>4. Сложение векторов</h2>
<p>Сумму векторов вычисляют <b>покоординатно</b>:
$$ a+b=(a_1+b_1,\ a_2+b_2,\ \ldots,\ a_n+b_n). $$
Геометрически действует <b>правило «хвост к голове»</b>: если приставить начало $b$ к концу
$a$, то вектор из начала $a$ в конец $b$ и есть сумма. Тот же результат даёт <b>правило
параллелограмма</b>, построенного на $a$ и $b$.</p>

<div class="widget"><div class="widget-title">Сумма $a+b$: правило параллелограмма</div>
<div class="widget-sub">Перетащите концы $a$ (синяя) и $b$ (янтарная). Красная — сумма.</div>
<svg viewBox="0 0 600 380" id="svg-add"></svg>
<div class="readout" id="add-ro"></div></div>

<div class="box idea"><div class="t">Зачем это в ML</div>
Сложение и деление на число дают <b>среднее наблюдение</b> — центр облака точек:
$\bar a=\tfrac1m(a^{(1)}+\cdots+a^{(m)})$. Так считают центры кластеров в $k$-means, а
вычитание среднего из каждой точки — <b>центрирование данных</b> — станет первым шагом PCA.</div>
"""
script = r"""
(function(){const svg=document.getElementById("svg-add");if(!svg)return;
 const ro=document.getElementById("add-ro");let a={x:3,y:1},b={x:-1,y:2.2};
 function R(){const g=freshFrame(svg);const s={x:a.x+b.x,y:a.y+b.y};
  g.appendChild(el("line",{x1:SX(a.x),y1:SY(a.y),x2:SX(s.x),y2:SY(s.y),stroke:COL.b,"stroke-width":1.6,"stroke-dasharray":"5 4","stroke-opacity":.6}));
  g.appendChild(el("line",{x1:SX(b.x),y1:SY(b.y),x2:SX(s.x),y2:SY(s.y),stroke:COL.a,"stroke-width":1.6,"stroke-dasharray":"5 4","stroke-opacity":.6}));
  g.appendChild(arrow(OX,OY,SX(s.x),SY(s.y),{color:COL.sum,width:3}));
  g.appendChild(arrow(OX,OY,SX(a.x),SY(a.y),{color:COL.a}));
  g.appendChild(arrow(OX,OY,SX(b.x),SY(b.y),{color:COL.b}));
  handle(g,a.x,a.y,COL.a,(x,y)=>{a={x,y};R();},svg);
  handle(g,b.x,b.y,COL.b,(x,y)=>{b={x,y};R();},svg);
  label(g,a.x+.2,a.y+.3,"a",COL.a);label(g,b.x+.2,b.y+.3,"b",COL.b);label(g,s.x+.2,s.y+.3,"a+b",COL.sum);
  ro.innerHTML=`(${a.x.toFixed(1)}, ${a.y.toFixed(1)}) + (${b.x.toFixed(1)}, ${b.y.toFixed(1)}) = <b>(${s.x.toFixed(1)}, ${s.y.toFixed(1)})</b>`;}
 R();})();
"""
display(HTML(viz(body, script)))''')

# ============================================================================
# 7. ТЕОРИЯ — умножение на число и линейная комбинация + упражнения
# ============================================================================
code(r'''#@title Теория 5 — Умножение на число и линейная комбинация { display-mode: "form" }
body = r"""
<h2>5. Умножение на число и линейная комбинация</h2>
<p>Умножение на число $\lambda$ растягивает стрелку в $|\lambda|$ раз, а при $\lambda<0$ ещё
и разворачивает её на противоположную сторону. Направление либо сохраняется, либо меняется на
строго обратное — вектор остаётся на одной прямой через начало координат.</p>

<div class="widget"><div class="widget-title">$\lambda\cdot v$: масштабирование вектора</div>
<div class="widget-sub">Синяя — исходный $v$ (перетащите конец), зелёная — $\lambda v$.</div>
<svg viewBox="0 0 600 380" id="svg-sc"></svg>
<div class="controls"><div class="control"><label>$\lambda=$</label>
<input type="range" id="sc-t" min="-2" max="2" step="0.1" value="1.5"><span class="val" id="sc-tv">1.5</span></div></div>
<div class="readout" id="sc-ro"></div></div>

<p>Объединив обе операции, получаем <b>линейную комбинацию</b> векторов $a$ и $b$:
$$ \lambda a + \mu b, \qquad \lambda,\mu\in\mathbb{R}. $$
Меняя два числа, можно попасть в разные точки плоскости; множество всех достижимых точек
называют <b>линейной оболочкой</b> векторов $a$ и $b$.</p>

<div class="widget"><div class="widget-title">Линейная комбинация $\lambda a+\mu b$</div>
<div class="widget-sub">Крутите ползунки. Сплошные $\lambda a$ и $\mu b$ — слагаемые; пунктир достраивает
параллелограмм; красный вектор — результат $\lambda a+\mu b$.</div>
<svg viewBox="0 0 600 380" id="svg-lc"></svg>
<div class="controls">
<div class="control"><label>$\lambda=$</label><input type="range" id="lc-a" min="-2" max="2" step="0.1" value="1"><span class="val" id="lc-av">1.0</span></div>
<div class="control"><label>$\mu=$</label><input type="range" id="lc-b" min="-2" max="2" step="0.1" value="0.6"><span class="val" id="lc-bv">0.6</span></div></div>
<div class="readout" id="lc-ro"></div></div>

<div class="box warn"><div class="t">Забегая вперёд (недели 3, 8)</div>
Если $a$ и $b$ смотрят в разные стороны, их линейными комбинациями покрывается вся плоскость.
Но если они лежат на одной прямой (один — кратное другого), то сколько ни меняй $\lambda,\mu$,
останешься на этой прямой: двух независимых направлений нет. Это <b>линейная зависимость</b> —
причина <b>мультиколлинеарности</b> и падения <b>ранга</b> матрицы признаков. Подробно — на неделе 3.</div>
"""
script = r"""
(function(){const svg=document.getElementById("svg-sc");if(!svg)return;
 const ro=document.getElementById("sc-ro"),tS=document.getElementById("sc-t"),tV=document.getElementById("sc-tv");
 let v={x:2.6,y:1.4};
 function R(){const t=parseFloat(tS.value);tV.textContent=t.toFixed(1);const g=freshFrame(svg);
  const k=6/Math.max(Math.abs(v.x),Math.abs(v.y),.001);
  g.appendChild(el("line",{x1:SX(-k*v.x),y1:SY(-k*v.y),x2:SX(k*v.x),y2:SY(k*v.y),stroke:"#232a33","stroke-width":1.5}));
  g.appendChild(arrow(OX,OY,SX(t*v.x),SY(t*v.y),{color:COL.res,width:3}));
  g.appendChild(arrow(OX,OY,SX(v.x),SY(v.y),{color:COL.v}));
  handle(g,v.x,v.y,COL.v,(x,y)=>{v={x,y};R();},svg);
  label(g,v.x+.2,v.y+.3,"v",COL.v);label(g,t*v.x+.2,t*v.y-.2,"λv",COL.res);
  const d=t>0?"то же направление":t<0?"обратное направление":"нулевой вектор";
  ro.innerHTML=`λv = (${(t*v.x).toFixed(2)}, ${(t*v.y).toFixed(2)}) · длина ×${Math.abs(t).toFixed(1)} · ${d}`;}
 tS.addEventListener("input",R);R();})();
(function(){const svg=document.getElementById("svg-lc");if(!svg)return;
 const ro=document.getElementById("lc-ro"),aS=document.getElementById("lc-a"),aV=document.getElementById("lc-av"),
  bS=document.getElementById("lc-b"),bV=document.getElementById("lc-bv");const a={x:2.4,y:.8},b={x:-.9,y:2.1};
 function R(){const al=parseFloat(aS.value),be=parseFloat(bS.value);aV.textContent=al.toFixed(1);bV.textContent=be.toFixed(1);
  const g=freshFrame(svg);const p={x:al*a.x+be*b.x,y:al*a.y+be*b.y};
  const la={x:al*a.x,y:al*a.y},mb={x:be*b.x,y:be*b.y};
  // параллелограмм: стороны, параллельные λa и μb
  g.appendChild(el("line",{x1:SX(la.x),y1:SY(la.y),x2:SX(p.x),y2:SY(p.y),stroke:COL.b,"stroke-width":1.6,"stroke-dasharray":"5 4","stroke-opacity":.7}));
  g.appendChild(el("line",{x1:SX(mb.x),y1:SY(mb.y),x2:SX(p.x),y2:SY(p.y),stroke:COL.a,"stroke-width":1.6,"stroke-dasharray":"5 4","stroke-opacity":.7}));
  // базовые векторы a, b — тонким пунктиром для ориентира
  g.appendChild(arrow(OX,OY,SX(a.x),SY(a.y),{color:COL.a,dash:"2 3",width:1.4}));
  g.appendChild(arrow(OX,OY,SX(b.x),SY(b.y),{color:COL.b,dash:"2 3",width:1.4}));
  // слагаемые λa и μb
  g.appendChild(arrow(OX,OY,SX(la.x),SY(la.y),{color:COL.a,width:2.4}));
  g.appendChild(arrow(OX,OY,SX(mb.x),SY(mb.y),{color:COL.b,width:2.4}));
  // результирующий вектор
  g.appendChild(arrow(OX,OY,SX(p.x),SY(p.y),{color:COL.sum,width:3.2}));
  g.appendChild(el("circle",{cx:SX(p.x),cy:SY(p.y),r:5,fill:COL.sum}));
  label(g,a.x+.2,a.y+.3,"a",COL.a);label(g,b.x-.5,b.y+.3,"b",COL.b);
  label(g,la.x+.12,la.y-.15,"λa",COL.a);label(g,mb.x-.2,mb.y+.3,"μb",COL.b);
  label(g,p.x+.2,p.y+.3,"λa+μb",COL.sum);
  ro.innerHTML=`λ·a + μ·b = <b>(${p.x.toFixed(2)}, ${p.y.toFixed(2)})</b>`;}
 aS.addEventListener("input",R);bS.addEventListener("input",R);R();})();
"""
display(HTML(viz(body, script)))''')

md(r"""### Задание 2 — операции с векторами руками

Даны два наблюдения-вектора $a=(3,\,1)$ и $b=(-1,\,2)$.

1. Посчитайте $a+b$ и $2a-b$ **на бумаге**, затем проверьте в numpy.
2. Найдите **среднее** наблюдение $\tfrac12(a+b)$. Где оно на графике из раздела 4 — между какими точками?
3. Проверьте, что $\lVert 2a\rVert = 2\lVert a\rVert$. Почему множитель выносится из-под нормы?
""")

code(r"""a = np.array([3, 1])
b = np.array([-1, 2])

# TODO: a + b, 2*a - b, (a + b) / 2
# TODO: np.linalg.norm(2*a) и 2 * np.linalg.norm(a) — сравните
""")

# ============================================================================
# 8. ЗАДАЧИ на датасет
# ============================================================================
md(r"""## 6. Задачи на датасете Davis

Теперь всё вместе — на реальных данных. Работаем с признаками `weight` и `height`.
""")

code(r"""# Матрица наблюдений: строка = вектор (вес, рост)
X = df[['weight', 'height']].to_numpy(float)
X.shape   # (200, 2) — 200 векторов в R^2""")

md(r"""**Задача 6.1.** Посчитайте модуль (норму) каждого наблюдения и добавьте столбец `norm`
в `df`. Кто «самый большой» человек по этой мере — найдите строку с максимальной нормой.
Подсказка: `np.linalg.norm(X, axis=1)`.

**Задача 6.2.** Возьмите людей с индексами 0 и 1. Посчитайте расстояние между ними как
$\lVert a-b\rVert$. Интерпретируйте: близкие это наблюдения или далёкие относительно
разброса данных?

**Задача 6.3.** Для человека с индексом 0 найдите **ближайшего соседа** — наблюдение с
наименьшим расстоянием (кроме самого себя). Совпал ли его пол? Это и есть ядро метода
$k$ ближайших соседей.
""")

code(r"""# Задача 6.1 — норма каждого наблюдения; строка с максимальной нормой
""")

code(r"""# Задача 6.2 — расстояние между наблюдениями 0 и 1 как ||a - b||
""")

code(r"""# Задача 6.3 — ближайший сосед к наблюдению 0 (исключив само наблюдение)
""")

md(r"""**Задача 6.4 — центроиды.** <b>Центроид</b> облака точек — это среднее наблюдение
$\bar a=\tfrac1m\sum_{k=1}^{m} a^{(k)}$ (покоординатное среднее). Посчитайте:

1. общий центроид всех наблюдений;
2. центроид мужчин (`sex == 'M'`) и центроид женщин (`sex == 'F'`) по отдельности.

Сравните: чем отличается «средний мужчина» от «средней женщины» в осях вес–рост?
Подсказки: `X.mean(axis=0)`; маску по полу задаёт `df['sex'].to_numpy()`.
""")

code(r"""# Задача 6.4 — центроиды: общий и по полам
X = df[['weight', 'height']].to_numpy(float)
sex = df['sex'].to_numpy()
# TODO: общий центроид X.mean(axis=0)
# TODO: центроид X[sex == 'M'] и X[sex == 'F']
""")

md(r"""**Задача 6.5 — выбросы по расстоянию до центроида.** Насколько наблюдение «нетипично»,
можно измерить его евклидовым расстоянием до центроида **своей** группы (своего пола):
чем дальше от центра, тем более оно выбивается.

1. Для каждого наблюдения посчитайте расстояние $\lVert a-\bar a_{\text{пол}}\rVert$ до
   центроида его пола.
2. Выведите **топ-3** наблюдения с наибольшим расстоянием — это кандидаты в выбросы.

Подсказка: посчитайте расстояния отдельно для `M` и `F`, соберите в один столбец
`dist_to_centroid`, затем `df.nlargest(3, 'dist_to_centroid')`.
""")

code(r"""# Задача 6.5 — топ-3 выброса по расстоянию до центроида своего пола
# TODO: для каждой строки — расстояние до центроида её пола
# TODO: df.nlargest(3, 'dist_to_centroid')
""")

md(r"""**Задача 6.6 — заявленное против измеренного.** У каждого человека есть *измеренные*
вес и рост (`weight`, `height`) и *со слов* заявленные (`repwt`, `repht`). Расхождение —
это вектор $d=(\text{repwt}-\text{weight},\ \text{repht}-\text{height})$, а его модуль
$\lVert d\rVert$ показывает, насколько сильно человек ошибся в самооценке.

Часть значений `repwt`/`repht` отсутствует — сначала отбросьте такие строки
(`df.dropna(subset=['repwt', 'repht'])`).

1. **Систематическое смещение.** Сравните центроид измеренных признаков с центроидом
   заявленных. В какую сторону и на сколько в среднем расходятся оценки — склонны ли люди,
   например, занижать рост?
2. **Топ-3.** Найдите трёх человек с наибольшим модулем расхождения $\lVert d\rVert$.
""")

code(r"""# Задача 6.6 — расхождение заявленного и измеренного
rep = df.dropna(subset=['repwt', 'repht']).copy()
# TODO: центроид измеренных (weight, height) и центроид заявленных (repwt, repht) — сравните
# TODO: модуль расхождения ||(repwt - weight, repht - height)|| для каждой строки
# TODO: три наибольших расхождения
""")

md(r"""---
### Итог урока

- Строка датасета — это **вектор**; датасет — **облако точек** в признаковом пространстве $\mathbb{R}^n$.
- В $\mathbb{R}^n$ есть две операции — **сложение** и **умножение на число**; они не выводят из пространства (это и есть **векторное пространство**).
- **Модуль** $\lVert a\rVert=\sqrt{\sum_i a_i^2}$ — «размер» наблюдения; **расстояние** $\lVert a-b\rVert$ — мера непохожести.
- **Линейная комбинация** $\lambda a+\mu b$ и её оболочка — основа тем недели 3 (ранг, мультиколлинеарность).

**Домашнее задание на свой датасет-якорь.** Выберите два числовых признака своего датасета.
(1) Постройте матрицу наблюдений `X`. (2) Посчитайте норму каждого наблюдения. (3) Найдите
две самые похожие и две самые непохожие строки и объясните словами, что означает их близость
для *этих* данных.
""")

# ============================================================================
nb = new_notebook(cells=cells)
nb.metadata = {
    "colab": {"provenance": [], "toc_visible": True},
    "kernelspec": {"name": "python3", "display_name": "Python 3"},
    "language_info": {"name": "python"},
}
out = "linear_algebra/01_vectors.ipynb"
with open(out, "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("written", out, "cells:", len(cells))
