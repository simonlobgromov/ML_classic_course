# -*- coding: utf-8 -*-
"""Builds the Colab notebook «Урок 2. Скалярное произведение, косинусная близость,
нормализация». Theory prose is Russian (academic); code and exercises are English.
Run:  ./venv/bin/python math_for_ds/build_lesson2.py
Out:  math_for_ds/02_dot_product.ipynb
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
# 0. Заголовок (учебная проза — русский)
# ============================================================================
md(r"""# Линейная алгебра для Data Science
## Урок 2 — Скалярное произведение, косинусная близость и нормализация

На прошлом уроке вектор описывался длиной и координатами. Теперь введём операцию, которая
связывает **два** вектора и измеряет, насколько они *сонаправлены*, — **скалярное
произведение**. Из него вырастут угол между наблюдениями, косинусная близость и
нормализация, а в конце мы увидим, что ровно эта операция лежит в основе механизма
внимания (attention) в больших языковых моделях.

Продолжаем работать с датасетом `Davis` (вес и рост 200 человек).
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
# 2. ТЕОРИЯ 1 — скалярное произведение (+ проекция, физика)
# ============================================================================
code(r'''#@title Теория 1 — Скалярное произведение { display-mode: "form" }
body = r"""
<h2>1. Скалярное произведение</h2>

<p><b>Скалярным произведением</b> векторов $a=(a_1,\ldots,a_n)$ и $b=(b_1,\ldots,b_n)$
называется число
$$ \langle a,b\rangle \;=\; a_1b_1+a_2b_2+\cdots+a_nb_n \;=\; \sum_{i=1}^{n} a_ib_i. $$
Наряду с $\langle a,b\rangle$ употребляют записи $a\cdot b$ и $a^{\top}b$. Результат —
именно <b>скаляр</b> (число), а не вектор; отсюда и название.</p>

<div class="widget"><div class="widget-title">Строка на столбец: перемножаем одноимённые координаты и складываем</div>
<div class="widget-sub">В записи $a^{\top}b$ вектор-строка $a^{\top}$ умножается на вектор-столбец $b$.
Стрелки соединяют координаты с одинаковыми номерами: $a_1$ с $b_1$, $a_2$ с $b_2$, и так далее.</div>
<svg viewBox="0 0 600 250" id="svg-dotmul"></svg></div>

<div class="box def"><div class="t">Геометрическая форма</div>
Скалярное произведение выражается через длины векторов и угол $\varphi$ между ними:
$$ \langle a,b\rangle = \lVert a\rVert\,\lVert b\rVert\cos\varphi. $$
Отсюда его знак несёт геометрический смысл: $\langle a,b\rangle>0$ при остром угле,
$\langle a,b\rangle=0$ при $\varphi=90^\circ$ (векторы <b>ортогональны</b>),
$\langle a,b\rangle<0$ при тупом угле.</p></div>

<p>Две формы согласованы: алгебраическая (сумма произведений координат) удобна для
вычислений, геометрическая ($\lVert a\rVert\lVert b\rVert\cos\varphi$) — для истолкования.
В частности, при $a=b$ получаем связь с длиной из прошлого урока:
$$ \langle a,a\rangle = \lVert a\rVert^2. $$</p>

<h3>Проекция одного вектора на другой</h3>
<p>Скалярное произведение измеряет, какая часть вектора $a$ приходится на направление $b$.
<b>Скалярная проекция</b> вектора $a$ на направление $b$ — это число со знаком
$$ \operatorname{pr}_b a = \frac{\langle a,b\rangle}{\lVert b\rVert}=\lVert a\rVert\cos\varphi, $$
положительное при остром угле и отрицательное при тупом; его модуль равен длине проекции.
Соответствующий <b>вектор-проекция</b> равен $\dfrac{\langle a,b\rangle}{\lVert b\rVert^2}\,b$.
На графике ниже проекция показана точкой на прямой $b$; перетаскивайте концы векторов.</p>

<div class="widget"><div class="widget-title">Скалярное произведение и проекция</div>
<div class="widget-sub">Перетащите концы $a$ (синий) и $b$ (янтарный). Зелёным — проекция
$a$ на $b$, пунктиром — перпендикуляр.</div>
<svg viewBox="0 0 600 380" id="svg-dot"></svg>
<div class="readout" id="dot-ro"></div></div>

<div class="box idea"><div class="t">Связь с физикой</div>
В школьном курсе физики <b>работа</b> постоянной силы $\vec F$ на перемещении $\vec s$
равна $A=\lVert\vec F\rVert\,\lVert\vec s\rVert\cos\varphi$ — это и есть скалярное
произведение $\langle \vec F,\vec s\rangle$. Сила, направленная поперёк движения
($\varphi=90^\circ$), работы не совершает: проекция равна нулю. Тот же самый механизм —
«сколько одного направления содержится в другом» — оказывается центральным и в машинном
обучении.</div>
"""
script = r"""
(function(){const svg=document.getElementById("svg-dotmul");if(!svg)return;
 while(svg.firstChild)svg.removeChild(svg.firstChild);const g=el("g");svg.appendChild(g);
 const cols=["#6ab0f3","#e0b25a","#5fd08a"],A=["a₁","a₂","a₃"],B=["b₁","b₂","b₃"];
 function box(x,y,w,h,s,c){g.appendChild(el("rect",{x,y,width:w,height:h,rx:6,fill:"#0e1319",stroke:c,"stroke-width":1.7}));
  const t=el("text",{x:x+w/2,y:y+h/2+6,fill:"#fff","text-anchor":"middle","font-family":"SF Mono,Menlo,monospace","font-size":18});t.textContent=s;g.appendChild(t);}
 function txt(x,y,s,c,sz,mono){const t=el("text",{x,y,fill:c||"#a7b0ba","font-family":(mono?"SF Mono,Menlo,monospace":"-apple-system,Segoe UI,sans-serif"),"font-size":sz||18,"font-weight":700});t.textContent=s;g.appendChild(t);}
 function brk(x,y,h,d){g.appendChild(el("path",{d:`M${x} ${y} h${d*10} v${h} h${-d*10}`,fill:"none",stroke:"#5a636d","stroke-width":2}));}
 // curved connector a_i -> b_i, routed BELOW the boxes (never crosses the numbers)
 function link(x1,y1,x2,y2,c){const cy=(y1+y2)/2+18;
  g.appendChild(el("path",{d:`M${x1} ${y1} C ${x1} ${cy}, ${x2-58} ${y2}, ${x2} ${y2}`,fill:"none",stroke:c,"stroke-width":2}));
  g.appendChild(el("polygon",{points:`${x2},${y2} ${x2-9},${y2-5} ${x2-9},${y2+5}`,fill:c}));}
 // row vector aᵀ (top)
 txt(20,64,"aᵀ =");const rx=[70,124,178],rw=46,rh=34,ry=40;
 brk(64,36,42,-1);brk(230,36,42,1);
 // column vector b (right, vertically centred)
 txt(296,127,"b =");const cbx=337,cby=[52,110,168],cw=46,ch=34;
 brk(331,48,154,-1);brk(389,48,154,1);
 // connectors first, boxes on top so numbers stay readable
 for(let i=0;i<3;i++)link(rx[i]+rw/2,ry+rh,cbx,cby[i]+ch/2,cols[i]);
 A.forEach((s,i)=>box(rx[i],ry,rw,rh,s,cols[i]));
 B.forEach((s,i)=>box(cbx,cby[i],cw,ch,s,cols[i]));
 // result line
 txt(20,232,"⟨a, b⟩ = aᵀb =");
 txt(196,232,"a₁b₁",cols[0],18,true);txt(250,232,"+");txt(268,232,"a₂b₂",cols[1],18,true);
 txt(322,232,"+");txt(340,232,"a₃b₃",cols[2],18,true);
})();
(function(){const svg=document.getElementById("svg-dot");if(!svg)return;
 const ro=document.getElementById("dot-ro");let a={x:3.4,y:2.2},b={x:4.2,y:-0.6};
 function R(){const g=freshFrame(svg);
  const bb=b.x*b.x+b.y*b.y, dot=a.x*b.x+a.y*b.y, t=dot/bb;
  const pr={x:t*b.x,y:t*b.y};
  // guide line along b
  const k=6/Math.max(Math.abs(b.x),Math.abs(b.y),.001);
  g.appendChild(el("line",{x1:SX(-k*b.x),y1:SY(-k*b.y),x2:SX(k*b.x),y2:SY(k*b.y),stroke:"#232a33","stroke-width":1.4}));
  // perpendicular from tip of a to projection
  g.appendChild(el("line",{x1:SX(a.x),y1:SY(a.y),x2:SX(pr.x),y2:SY(pr.y),stroke:"#5fd08a","stroke-width":1.6,"stroke-dasharray":"5 4"}));
  g.appendChild(arrow(OX,OY,SX(b.x),SY(b.y),{color:COL.b}));
  g.appendChild(arrow(OX,OY,SX(a.x),SY(a.y),{color:COL.a}));
  g.appendChild(el("circle",{cx:SX(pr.x),cy:SY(pr.y),r:5,fill:"#5fd08a"}));
  handle(g,a.x,a.y,COL.a,(x,y)=>{a={x,y};R();},svg);
  handle(g,b.x,b.y,COL.b,(x,y)=>{b={x,y};R();},svg);
  label(g,a.x+.2,a.y+.3,"a",COL.a);label(g,b.x+.2,b.y+.3,"b",COL.b);
  const na=Math.hypot(a.x,a.y),nb=Math.hypot(b.x,b.y);
  const cos=dot/(na*nb),ang=Math.acos(Math.max(-1,Math.min(1,cos)))*180/Math.PI;
  const sign=dot>0.001?"острый угол":dot<-0.001?"тупой угол":"ортогональны";
  ro.innerHTML=`⟨a,b⟩ = ${dot.toFixed(2)} = ‖a‖·‖b‖·cosφ = ${na.toFixed(2)}·${nb.toFixed(2)}·${cos.toFixed(2)} · φ≈${ang.toFixed(0)}° · ${sign}`;}
 R();})();
"""
display(HTML(viz(body, script)))''')

# ============================================================================
# 3. ТЕОРИЯ 2 — норма через ⟨a,a⟩ и L2-нормализация
# ============================================================================
code(r'''#@title Теория 2 — Нормализация (L2) { display-mode: "form" }
body = r"""
<h2>2. Длина через скалярное произведение и нормализация</h2>

<p>Как отмечено выше, $\langle a,a\rangle=\lVert a\rVert^2$, то есть евклидова норма
(«длина», $L_2$-норма) выражается через скалярное произведение:
$$ \lVert a\rVert=\sqrt{\langle a,a\rangle}=\sqrt{\sum_{i=1}^{n} a_i^2}. $$</p>

<div class="box def"><div class="t">Определение (нормализация)</div>
<b>$L_2$-нормализацией</b> ненулевого вектора $a$ называют переход к вектору
$$ \hat a=\frac{a}{\lVert a\rVert}, $$
имеющему единичную длину ($\lVert\hat a\rVert=1$) и <b>то же направление</b>, что и $a$.
Полученный $\hat a$ называют <b>единичным</b> (нормированным) вектором. Все единичные
векторы плоскости образуют окружность радиуса $1$; в $\mathbb{R}^n$ — единичную сферу.</div>

<p>Нормализация «стирает» длину, сохраняя направление: остаётся только информация о
<em>соотношении</em> координат, но не об их абсолютной величине. Перетащите $a$ и
проследите, как нормированный $\hat a$ скользит по единичной окружности.</p>

<div class="widget"><div class="widget-title">$L_2$-нормализация: проекция на единичную окружность</div>
<div class="widget-sub">Перетащите $a$ (янтарный). Зелёный $\hat a=a/\lVert a\rVert$ всегда лежит на окружности.</div>
<svg viewBox="0 0 600 380" id="svg-nrm"></svg>
<div class="readout" id="nrm-ro"></div></div>

<h3>Две разные операции со словом «нормализация»</h3>
<p>Здесь важно не смешивать два действия, которые по-русски часто называют одинаково.</p>
<ul>
<li><b>Нормализация вектора ($L_2$, по строке)</b> — определённая выше $\hat a=a/\lVert a\rVert$.
Она делит <em>все координаты одного наблюдения</em> на общее число — его длину. Соотношение
признаков внутри строки при этом не меняется, меняется лишь длина. Нужна для косинусной
близости и сравнения эмбеддингов.</li>
<li><b>Масштабирование признаков (по столбцу)</b> — приведение <em>каждого столбца</em> к
сравнимому масштабу (например, вычесть среднее и поделить на стандартное отклонение —
$z$-оценка). Нужна, чтобы ни один признак не доминировал в мерах близости только из-за
единиц измерения.</li>
</ul>
<p>Первое <b>не заменяет</b> второго: деля строку на её длину, мы масштабируем все признаки
одинаково, поэтому «крупный» по величине признак как подавлял остальные, так и подавляет.
Рассмотрим пример.</p>

<div class="box warn"><div class="t">Пример: без масштабирования вклад признака подавляется</div>
<p>Три автомобиля; признаки — марка (one-hot: $0$ — Toyota, $1$ — BMW), пробег (км) и цена:</p>
<table>
<tr><th>авто</th><th>марка</th><th>пробег, км</th><th>цена</th></tr>
<tr><td>A</td><td>0</td><td>50 000</td><td>1 000 000</td></tr>
<tr><td>B</td><td>1</td><td>50 000</td><td>1 000 000</td></tr>
<tr><td>C</td><td>0</td><td>52 000</td><td>1 020 000</td></tr>
</table>
<p>Найдём евклидовы расстояния до A <b>без масштабирования</b>:
$$ d(A,B)=\sqrt{1^2+0+0}=1,\qquad d(A,C)=\sqrt{0+2000^2+20000^2}\approx 20100. $$
Расстояние целиком определяется ценой и пробегом, а смена марки даёт вклад ровно $1$ — на их
фоне он <b>незаметен</b>. Формально ближайшим к A оказывается B (другой марки!), а C — «далёким»,
хотя различие в цене на $20\,000$ при цене в миллион ничтожно. Признак «марка» на своей шкале
$\{0,1\}$ на близость не влияет никак.</p></div>

<p>Эту проблему устраняет <b>масштабирование по столбцам</b>: приведя каждый признак к единому
масштабу, мы делаем смену марки сопоставимой с типичными различиями в цене и пробеге, и она
начинает учитываться. Это касается <em>и</em> евклидова расстояния, <em>и</em> косинуса:
скалярное произведение $\sum_i a_ib_i$ точно так же определяется преимущественно признаком с
наибольшим масштабом.
Само по себе $L_2$-нормирование строки эту проблему не решает — оно про направление, а не про
соизмеримость признаков.</p>

<details><summary>Почему $L_2$-нормализация строки здесь не помогает</summary>
<p>Обе операции действуют вдоль разных осей таблицы данных, где строки — наблюдения, а
столбцы — признаки. $L_2$-нормализация делит каждую строку на её собственную длину, поэтому
соотношение признаков внутри строки сохраняется, и признак, крупный по абсолютной величине,
остаётся крупным. Применим её к тем же автомобилям:
$$ \hat a_A=(0,\ 0{,}050,\ 0{,}999),\quad
   \hat a_B=(0,\ 0{,}050,\ 0{,}999),\quad
   \hat a_C=(0,\ 0{,}051,\ 0{,}999). $$
Цена ($\approx 0{,}999$) по-прежнему подавляет пробег ($\approx 0{,}05$) и марку ($0$); все
три вектора почти совпадают, и косинусная близость между любыми двумя равна $1{,}000$ —
различить автомобили невозможно.</p>
<p>Масштабирование признаков делит каждый <em>столбец</em> на его стандартное отклонение,
вычисленное по всем наблюдениям, и лишь тогда вклад марки становится соизмерим с ценой и
пробегом. Итог:</p>
<table>
<tr><th>операция</th><th>ось</th><th>делит на</th><th>что устраняет</th></tr>
<tr><td>$L_2$-нормализация</td><td>строка (наблюдение)</td><td>длину строки $\lVert x\rVert$</td><td>общий размер наблюдения</td></tr>
<tr><td>масштабирование признаков</td><td>столбец (признак)</td><td>разброс столбца $\sigma$</td><td>несоизмеримость шкал признаков</td></tr>
</table>
</details>

<div class="box idea"><div class="t">Итог различения</div>
<b>$L_2$-нормализация (по строке)</b> убирает длину наблюдения — нужна для косинуса и
эмбеддингов. <b>Масштабирование признаков (по столбцу, $z$-оценка)</b> уравнивает вклад
признаков — нужно, чтобы близость не определялась одной «крупной» колонкой. Про $z$-оценку
подробно — в статистическом треке (неделя 1).</div>
"""
script = r"""
(function(){const svg=document.getElementById("svg-nrm");if(!svg)return;
 const ro=document.getElementById("nrm-ro");const P=plane(2.6);let a={x:1.9,y:1.2};
 function R(){while(svg.firstChild)svg.removeChild(svg.firstChild);const g=el("g");svg.appendChild(g);P.frame(g);
  g.appendChild(el("circle",{cx:P.ox,cy:P.oy,r:P.ppu,fill:"none",stroke:"#3a434f","stroke-width":1.4,"stroke-dasharray":"4 4"}));
  const n=Math.hypot(a.x,a.y)||1e-9;const h={x:a.x/n,y:a.y/n};
  g.appendChild(el("line",{x1:P.ox,y1:P.oy,x2:P.sx(a.x),y2:P.sy(a.y),stroke:COL.b,"stroke-width":1.4,"stroke-dasharray":"2 3"}));
  g.appendChild(arrow(P.ox,P.oy,P.sx(h.x),P.sy(h.y),{color:COL.res,width:3}));
  g.appendChild(arrow(P.ox,P.oy,P.sx(a.x),P.sy(a.y),{color:COL.b,width:2.2}));
  P.drag(svg,g,a.x,a.y,COL.b,(x,y)=>{a={x,y};R();});
  const t1=el("text",{x:P.sx(a.x)+6,y:P.sy(a.y),fill:COL.b,"font-family":"sans-serif","font-size":15,"font-weight":700});t1.textContent="a";g.appendChild(t1);
  const t2=el("text",{x:P.sx(h.x)+6,y:P.sy(h.y)-4,fill:COL.res,"font-family":"sans-serif","font-size":15,"font-weight":700});t2.textContent="â";g.appendChild(t2);
  ro.innerHTML=`‖a‖ = ${n.toFixed(3)} · â = (${h.x.toFixed(3)}, ${h.y.toFixed(3)}) · ‖â‖ = ${Math.hypot(h.x,h.y).toFixed(3)}`;}
 R();})();
"""
display(HTML(viz(body, script)))''')

# ============================================================================
# 4. ТЕОРИЯ 3 — косинусная близость и косинусное расстояние
# ============================================================================
code(r'''#@title Теория 3 — Косинусная близость vs евклидово расстояние { display-mode: "form" }
body = r"""
<h2>3. Косинусная близость и косинусное расстояние</h2>

<p>Из геометрической формы скалярного произведения выражается косинус угла между векторами:
$$ \cos\varphi=\frac{\langle a,b\rangle}{\lVert a\rVert\,\lVert b\rVert}. $$
Эту величину называют <b>косинусной близостью</b> (cosine similarity). Она лежит в
пределах $[-1,1]$: значение $1$ — сонаправленные векторы, $0$ — ортогональные, $-1$ —
противоположно направленные. Соответствующее <b>косинусное расстояние</b> определяют как
$$ d_{\cos}(a,b)=1-\cos\varphi. $$</p>

<div class="box def"><div class="t">Ключевое отличие от евклидова расстояния</div>
Евклидово расстояние $\lVert a-b\rVert$ учитывает и направление, и <b>длину</b> векторов;
косинусная близость зависит <b>только от направления</b> и не меняется при умножении любого
из векторов на положительное число. Поэтому косинус отвечает на вопрос «насколько похожи
<em>соотношения</em> признаков», а не «насколько близки сами величины».</div>

<p>Связь двух мер становится точной <b>после нормализации</b>. Для единичных векторов
$\hat a,\hat b$ прямым раскрытием квадрата нормы получаем
$$ \lVert\hat a-\hat b\rVert^2=\langle\hat a-\hat b,\ \hat a-\hat b\rangle
   =2-2\langle\hat a,\hat b\rangle=2\,(1-\cos\varphi). $$
То есть на единичной окружности евклидово расстояние — это <b>монотонная функция</b>
косинусного: они упорядочивают пары одинаково. Вот почему для нормированных векторов
косинусная близость показательна — она измеряет ровно то же, что и расстояние по прямой,
но не зависит от исходных длин.</p>

<div class="widget"><div class="widget-title">Евклид против косинуса: включите нормализацию</div>
<div class="widget-sub">Перетащите $a,b$. Пунктирная хорда — евклидово расстояние. Флажок
переносит векторы на единичную окружность (нормализация); угол при этом не меняется.</div>
<svg viewBox="0 0 600 380" id="svg-ec"></svg>
<div class="controls"><div class="control">
<label><input type="checkbox" id="ec-norm"> нормализовать (перенести на окружность)</label></div></div>
<div class="readout" id="ec-ro"></div></div>

<p>Обратите внимание: при нормализации <b>косинус не меняется</b> (угол тот же), а евклидово
расстояние меняется и становится согласованным с косинусным по формуле выше.</p>

<div class="box warn"><div class="t">Осторожно с неотрицательными признаками</div>
Если все признаки положительны (как вес и рост), все векторы лежат в одном квадранте, углы
малы, и косинусная близость почти всегда близка к $1$ — различия слабые. Чтобы косинус стал
информативным, данные обычно предварительно <b>центрируют</b> (вычитают среднее). Мы
вернёмся к центрированию при изучении ковариации и PCA.</div>
"""
script = r"""
(function(){const svg=document.getElementById("svg-ec");if(!svg)return;
 const ro=document.getElementById("ec-ro"),cb=document.getElementById("ec-norm");
 const P=plane(2.6);let a={x:2.0,y:0.7},b={x:0.8,y:1.9};
 function R(){while(svg.firstChild)svg.removeChild(svg.firstChild);const g=el("g");svg.appendChild(g);P.frame(g);
  g.appendChild(el("circle",{cx:P.ox,cy:P.oy,r:P.ppu,fill:"none",stroke:"#2a313b","stroke-width":1.3,"stroke-dasharray":"4 4"}));
  const na=Math.hypot(a.x,a.y)||1e-9,nb=Math.hypot(b.x,b.y)||1e-9,norm=cb.checked;
  const A=norm?{x:a.x/na,y:a.y/na}:a,B=norm?{x:b.x/nb,y:b.y/nb}:b;
  // raw thin references
  g.appendChild(arrow(P.ox,P.oy,P.sx(a.x),P.sy(a.y),{color:COL.a,dash:"2 3",width:1.2}));
  g.appendChild(arrow(P.ox,P.oy,P.sx(b.x),P.sy(b.y),{color:COL.b,dash:"2 3",width:1.2}));
  // euclid chord
  g.appendChild(el("line",{x1:P.sx(A.x),y1:P.sy(A.y),x2:P.sx(B.x),y2:P.sy(B.y),stroke:COL.sum,"stroke-width":2,"stroke-dasharray":"5 4"}));
  g.appendChild(arrow(P.ox,P.oy,P.sx(A.x),P.sy(A.y),{color:COL.a,width:2.6}));
  g.appendChild(arrow(P.ox,P.oy,P.sx(B.x),P.sy(B.y),{color:COL.b,width:2.6}));
  P.drag(svg,g,a.x,a.y,COL.a,(x,y)=>{a={x,y};R();});
  P.drag(svg,g,b.x,b.y,COL.b,(x,y)=>{b={x,y};R();});
  const dot=a.x*b.x+a.y*b.y,cos=dot/(na*nb),eu=Math.hypot(A.x-B.x,A.y-B.y);
  let s=`евклид = ${eu.toFixed(3)} · cos = ${cos.toFixed(3)} · cos-dist = ${(1-cos).toFixed(3)}`;
  if(norm)s+=` · √(2(1−cos)) = ${Math.sqrt(Math.max(0,2*(1-cos))).toFixed(3)}`;
  ro.innerHTML=s;}
 cb.addEventListener("change",R);R();})();
"""
display(HTML(viz(body, script)))''')

# ============================================================================
# 5. ТЕОРИЯ 4 — где это в ML: embeddings + attention
# ============================================================================
code(r'''#@title Теория 4 — Где это в ML: эмбеддинги и внимание { display-mode: "form" }
body = r"""
<h2>4. Где это работает в машинном обучении</h2>

<h3>Эмбеддинги и поиск похожего</h3>
<p>Современные модели превращают слова, тексты, изображения и товары в <b>эмбеддинги</b> —
векторы в пространстве $\mathbb{R}^n$ высокой размерности ($n$ порядка сотен и тысяч),
устроенные так, что близкие по смыслу объекты получают близкие по <em>направлению</em>
векторы. Стандартная мера похожести здесь — <b>косинусная близость</b>: поиск похожих
документов, рекомендации, кластеризация текстов сводятся к отысканию векторов с наибольшим
$\cos\varphi$ к запросу. Длина эмбеддинга часто малоинформативна, поэтому берут именно
косинус, а не евклидово расстояние.</p>

<h3>Механизм внимания (attention) в языковых моделях</h3>
<p>В основе трансформеров — тех самых моделей, что стоят за большими языковыми моделями, —
лежит скалярное произведение. Каждому элементу последовательности сопоставляют три вектора:
<b>запрос</b> $q$ (query), <b>ключ</b> $k$ (key) и <b>значение</b> $v$ (value). Насколько
один элемент должен «обратить внимание» на другой, определяется <b>скалярным произведением</b>
запроса и ключа:
$$ \text{score}(q,k)=\frac{\langle q,k\rangle}{\sqrt{d}}, $$
где $d$ — размерность (деление на $\sqrt{d}$ стабилизирует масштаб). Полученные оценки
пропускают через $\operatorname{softmax}$, получая веса $w_i\ge 0$, $\sum_i w_i=1$, и
итоговый вектор есть взвешенная сумма значений $\sum_i w_i v_i$. Иными словами, чем сильнее
запрос сонаправлен с ключом, тем больший вес получает соответствующее значение.</p>

<p>Ниже — упрощённая модель внимания: перетаскивайте <b>запрос</b> $q$ (белый) и смотрите,
как перераспределяются веса между тремя ключами и куда смещается результат (зелёная точка).</p>

<div class="widget"><div class="widget-title">Внимание как softmax по скалярным произведениям</div>
<div class="widget-sub">Перетащите $q$. Веса $w_i=\operatorname{softmax}(\langle q,k_i\rangle/\sqrt2)$;
результат — $\sum_i w_i k_i$.</div>
<svg viewBox="0 0 600 380" id="svg-att"></svg>
<div class="readout" id="att-ro"></div></div>

<div class="box take"><div class="t">Главная мысль урока</div>
Скалярное произведение — это способ измерить «сколько одного направления содержится в
другом». Из него следуют длина ($\langle a,a\rangle$), угол и косинусная близость, а на
нормированных векторах косинус согласован с евклидовым расстоянием. Эта же операция
управляет вниманием в языковых моделях — поэтому она одна из самых востребованных в ML.</div>
"""
script = r"""
(function(){const svg=document.getElementById("svg-att");if(!svg)return;
 const ro=document.getElementById("att-ro");
 const keys=[{x:3.6,y:1.3,n:"k₁"},{x:-2.6,y:2.4,n:"k₂"},{x:-1.2,y:-2.8,n:"k₃"}];
 const cols=["#6ab0f3","#e0b25a","#e0757f"];let q={x:2.9,y:1.7};
 function R(){const g=freshFrame(svg);const d=Math.sqrt(2);
  const s=keys.map(k=>(q.x*k.x+q.y*k.y)/d);const m=Math.max(...s);
  const ex=s.map(v=>Math.exp(v-m));const Z=ex.reduce((p,c)=>p+c,0);const w=ex.map(v=>v/Z);
  const c={x:keys.reduce((p,k,i)=>p+w[i]*k.x,0),y:keys.reduce((p,k,i)=>p+w[i]*k.y,0)};
  keys.forEach((k,i)=>{g.appendChild(arrow(OX,OY,SX(k.x),SY(k.y),{color:cols[i],width:1.6+3*w[i]}));
    label(g,k.x+.15,k.y+.3,k.n,cols[i]);});
  g.appendChild(el("circle",{cx:SX(c.x),cy:SY(c.y),r:6,fill:"#5fd08a"}));
  label(g,c.x+.2,c.y-.2,"итог",'#5fd08a');
  g.appendChild(arrow(OX,OY,SX(q.x),SY(q.y),{color:"#ffffff",width:3}));
  handle(g,q.x,q.y,"#ffffff",(x,y)=>{q={x,y};R();},svg);
  label(g,q.x+.2,q.y+.3,"q",'#ffffff');
  ro.innerHTML="softmax-веса: "+w.map((v,i)=>`<span style="color:${cols[i]}">${keys[i].n} = ${v.toFixed(2)}</span>`).join("  ·  ");}
 R();})();
"""
display(HTML(viz(body, script)))''')

# ============================================================================
# 6. PRACTICE (English tasks + English code)
# ============================================================================
md(r"""## Practice

We work with the `weight` and `height` columns as 2-D observation vectors.
Fill in the `# TODO` lines. Do each computation **by hand with numpy first**, then
cross-check against the library helper.""")

code(r"""# Observation matrix: each row is a vector (weight, height)
X = df[['weight', 'height']].to_numpy(float)
X.shape   # (200, 2)""")

md(r"""### Task 1 — dot product two ways

Take observations 0 and 1. Compute the dot product $\langle a,b\rangle$ two ways:
elementwise `(a*b).sum()` and via the operator `a @ b`. They must match.
Then verify the identity $\langle a,a\rangle = \lVert a\rVert^2$.""")

code(r"""a = X[0]
b = X[1]

# TODO: dot product as elementwise sum: (a * b).sum()
# TODO: dot product via the @ operator: a @ b
# TODO: check that a @ a equals np.linalg.norm(a) ** 2
""")

md(r"""### Task 2 — cosine similarity

Implement cosine similarity $\cos\varphi = \dfrac{\langle a,b\rangle}{\lVert a\rVert\,\lVert b\rVert}$
as a function, then apply it to observations 0 and 1. Also report the angle in degrees
(`np.degrees(np.arccos(...))`).""")

code(r"""def cosine_similarity(u, v):
    # TODO: return (u @ v) / (norm(u) * norm(v))
    ...

# TODO: cosine_similarity(X[0], X[1]) and the angle in degrees
""")

md(r"""### Task 3 — magnitude vs direction

Cosine ignores length; euclidean distance does not. Build a vector with the **same
direction** but a larger magnitude and observe the two measures disagree.""")

code(r"""p = X[0]
p_scaled = 3.0 * p          # same direction, three times longer

# TODO: euclidean distance np.linalg.norm(p - p_scaled)  -> large
# TODO: cosine_similarity(p, p_scaled)                    -> 1.0 (identical direction)
""")

md(r"""### Task 4 — nearest neighbour: euclidean vs cosine

For observation 0, find its nearest neighbour under **euclidean** distance and under
**cosine** distance, and compare. Because weight/height are positive, first **center** the
data (subtract the mean) so that cosine becomes informative.""")

code(r"""Xc = X - X.mean(axis=0)                       # center the cloud
Xn = Xc / np.linalg.norm(Xc, axis=1, keepdims=True)   # L2-normalize the centered rows

# TODO: euclidean nearest neighbour of row 0
#   d_euc = np.linalg.norm(Xc - Xc[0], axis=1); d_euc[0] = np.inf; d_euc.argmin()
# TODO: cosine nearest neighbour of row 0 (largest cosine = smallest cosine distance)
#   sims = Xn @ Xn[0]; sims[0] = -np.inf; sims.argmax()
# TODO: are the two neighbours the same row? print both
""")

md(r"""### Homework

1. Write a function `cosine_distance(u, v)` returning $1-\cos\varphi$ and confirm it is
   `0` for a vector with itself and `2` for a vector and its negation.
2. Using the **centered, L2-normalized** matrix `Xn`, verify the identity
   $\lVert \hat a-\hat b\rVert^2 = 2\,(1-\cos\varphi)$ on a few random pairs.
3. Pick two people with a similar height-to-weight ratio but different overall size.
   Show numerically that their **cosine** similarity is high while their **euclidean**
   distance is not small. Explain in one sentence what this means for the data.
4. *(Embeddings framing.)* Explain in two or three sentences why cosine similarity, rather
   than euclidean distance, is the default measure for comparing high-dimensional
   embeddings, and how this reuses the dot-product identity from this lesson.""")

md(r"""---
### Итог урока

- **Скалярное произведение** $\langle a,b\rangle=\sum_i a_ib_i=\lVert a\rVert\lVert b\rVert\cos\varphi$ — число, измеряющее сонаправленность.
- Из него следуют длина ($\langle a,a\rangle=\lVert a\rVert^2$), проекция и угол.
- **$L_2$-нормализация** $\hat a=a/\lVert a\rVert$ убирает длину, оставляя направление.
- **Косинусная близость** зависит только от направления; на нормированных векторах согласована с евклидовым расстоянием: $\lVert\hat a-\hat b\rVert^2=2(1-\cos\varphi)$.
- Эта операция — основа сравнения эмбеддингов и механизма внимания в языковых моделях.
""")

# ============================================================================
nb = new_notebook(cells=cells)
nb.metadata = META
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "02_dot_product.ipynb")
with open(out, "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("written", out, "cells:", len(cells))
