# -*- coding: utf-8 -*-
"""
Build 05_stat_normal.ipynb — "Случайность, вероятность и нормальное распределение".

Genetic order: from the language of probability (trial/outcome/event) through one
coin (Bernoulli) and sums of coins (binomial) up to the normal distribution and
its 2D form, cashed out as the three-sigma rule.

Cells:
  title, SETUP, preamble (photos),
  Часть 0  — основные понятия (испытание/исход/событие/вероятность/сл. величина),
  Часть 1  — распределение Бернулли (+ виджет),
  Часть 2  — биномиальное (+ виджет, нормальное приближение),
  Часть 3  — нормальное (гауссово) распределение (+ виджет с боксплотом),
  Часть 3b — двумерное нормальное распределение (скаттер + KDE + σ-эллипсы),
  data     — Davis рост + цена Бишкека,
  Часть 4  — правило трёх сигм (+ виджет с боксплотом),
  задания.

Photos embedded as base64. Same dark HTML/JS format as build_lesson4.py (theme.py).
Written un-executed; the JS renders in Colab.

Run:  python3 math_for_ds/build_lesson5.py
"""
import os
import sys
import io
import base64

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from theme import SETUP, META

cells = []
def md(s):   cells.append(new_markdown_cell(s.strip("\n")))
def code(s): cells.append(new_code_cell(s.strip("\n")))

# ---------------------------------------------------------------------------
# Image helper: resize, composite onto a dark ground, re-encode as JPEG, embed.
# ---------------------------------------------------------------------------
from PIL import Image
try:
    _LANCZOS = Image.Resampling.LANCZOS
except AttributeError:
    _LANCZOS = Image.LANCZOS

def data_uri(name, max_w, bg=(14, 18, 24), q=80):
    im = Image.open(os.path.join(HERE, "images", name))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        ground = Image.new("RGB", im.size, bg)
        ground.paste(im, mask=im.split()[-1])
        im = ground
    else:
        im = im.convert("RGB")
    if im.width > max_w:
        h = round(im.height * max_w / im.width)
        im = im.resize((max_w, h), _LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=q, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

GYM  = data_uri("2sccjshx.jpg", 340)
ROAD = data_uri("7eaaad0d-4b83-4490-882f-cd47684c5aa1.png", 380)
DIAG = data_uri("fae694e9-db41-4e1e-be7d-a2f6e0c90cbf.png", 320)

# ============================================================================
# Title
# ============================================================================
md(r"""
# Случайность, вероятность и нормальное распределение

До сих пор мы **описывали** данные, которые уже лежат перед нами: среднее, разброс, выбросы. Эта
тетрадь — про другой взгляд: за данными стоит **случайный процесс**, и у него есть устойчивая форма.
Мы соберём главное такое распределение — **нормальное (гауссово)** — с нуля: от одной монетки до
непрерывного распределения, а в конце превратим его в рабочее правило **трёх сигм** для поиска
выбросов.

Запустите первую ячейку с оформлением, затем читайте по порядку.
""")

# ============================================================================
# Setup (theme + viz helpers)
# ============================================================================
code(SETUP)

# ============================================================================
# Preamble — random processes are everywhere; wear as a histogram
# ============================================================================
_preamble_body = r"""
<h2>Случайные процессы вокруг нас</h2>
<p>В прошлых тетрадях мы работали в режиме «вот данные — опишем их числом». Теперь делаем шаг
в сторону — к <b>случайности</b>. <b>Случайный процесс</b> <span class="en">(random process)</span> —
это то, исход чего заранее не определён: какой вес возьмёт следующий посетитель зала, на сколько
сантиметров вильнёт колесо очередной машины, орёл или решка. Предсказать <em>один</em> исход
нельзя. Но у массы исходов есть устойчивая <b>форма</b> — и природа порой рисует её сама.</p>

<h3>Стёртая краска — это гистограмма</h3>
<p>Селектор весов в тренажёре. Краску стёрли рука и штырь: где вес выбирают часто — металл
блестит, где почти никогда — краска цела. Посмотрите, <em>где</em> стёрто: середина диапазона —
сильно, лёгкие и тяжёлые края — почти нетронуты. Эта полоса износа — буквально <b>гистограмма</b>
выбора веса, «напечатанная» тысячами посетителей. И форма её — знакомый колокол.</p>
<figure style="margin:1.1em auto;max-width:300px;">
  <img src="__GYM__" style="width:100%;height:auto;display:block;border-radius:10px;border:1px solid #2a313b;">
  <figcaption style="font-family:sans-serif;font-size:.82rem;color:#a7b0ba;margin-top:6px;text-align:center;">
    Износ краски на селекторе веса. Подпись автора снимка: «Normal distribution».</figcaption>
</figure>

<h3>Колея на асфальте — та же форма</h3>
<p>Колёса идут вдоль полосы, но каждая машина чуть смещается вбок — на пару сантиметров
влево-вправо, случайно. За тысячи проездов износ копится вокруг средней линии и сходит на нет
к краям: получается плавная <b>колея</b>-впадина. Приложите к ней ровную рейку (красная линия) —
и увидите тот же колоколообразный профиль. Правый рисунок поясняет механизм: смещение колеса от
центра $0$ — это случайная величина, а глубина износа в точке пропорциональна тому, как
<em>часто</em> колесо туда попадает. Часто около центра, редко по краям.</p>
<div style="display:flex;gap:14px;flex-wrap:wrap;align-items:flex-start;margin:1.1em 0;">
  <figure style="margin:0;flex:1 1 300px;">
    <img src="__ROAD__" style="width:100%;height:auto;display:block;border-radius:10px;border:1px solid #2a313b;">
    <figcaption style="font-family:sans-serif;font-size:.82rem;color:#a7b0ba;margin-top:6px;">
      Колея от колёс: впадина износа с колоколообразным профилем.</figcaption>
  </figure>
  <figure style="margin:0;flex:1 1 260px;">
    <img src="__DIAG__" style="width:100%;height:auto;display:block;border-radius:10px;border:1px solid #2a313b;">
    <figcaption style="font-family:sans-serif;font-size:.82rem;color:#a7b0ba;margin-top:6px;">
      Почему такая форма: колесо гуляет вокруг центра $0$, износ ∝ частоте попадания.</figcaption>
  </figure>
</div>

<div class="box take"><div class="t">К чему это всё</div>
Эти следы — гистограммы случайного процесса, <b>нарисованные самой физикой</b>. И форма повторяется.
Позже мы дадим ей имя — <b>нормальное распределение</b>. Почему она возникает так упрямо — соберём
в этой тетради <b>с нуля</b>: от одной монетки (Бернулли) через сумму монеток (биномиальное) к
нормальному распределению. А в конце превратим его в рабочий инструмент — правило <b>трёх сигм</b>
для поиска выбросов.</div>
"""
_preamble_body = (_preamble_body
                  .replace("__GYM__", GYM)
                  .replace("__ROAD__", ROAD)
                  .replace("__DIAG__", DIAG))

code('#@title Введение — случайные процессы вокруг нас { display-mode: "form" }\n'
     'body = r"""\n' + _preamble_body + '\n"""\n'
     'display(HTML(viz(body, wide=True)))')

# ============================================================================
# Часть 0 — basic concepts: trial, outcome, event, probability, random variable
# ============================================================================
code(r'''#@title Часть 0 — Язык случайного: испытание, исход, событие, вероятность { display-mode: "form" }
body = r"""
<h2>Часть 0. Язык случайного: испытание, исход, событие, вероятность</h2>
<p>Прежде чем считать, договоримся о словах. В теории вероятностей есть строгая цепочка понятий —
пройдём её по порядку, на простых примерах (бросок игрального кубика, выбор случайной квартиры из
базы объявлений).</p>

<div class="box def"><div class="t">Испытание и исход</div>
<b>Испытание</b> <span class="en">(trial)</span> — воспроизводимое действие, результат которого
заранее не известен: бросить кубик, вытащить случайную квартиру из объявлений.
<b>Исход</b> (элементарный исход) <span class="en">(outcome)</span> — один конкретный результат
испытания: «выпало 5», «попалась квартира за \$80k». Все возможные исходы одного испытания образуют
<b>пространство исходов</b> $\Omega$.</div>

<div class="box def"><div class="t">Событие и благоприятствующие исходы</div>
<b>(Случайное) событие</b> <span class="en">(event)</span> $A$ — то, что по итогам испытания либо
происходит, либо нет: «выпало чётное», «квартира дороже медианы». Событие — это <b>набор исходов</b>.
Исход, при котором событие наступает, называют <b>благоприятствующим</b>
<span class="en">(favourable)</span>; остальные — <b>неблагоприятными</b>. Для «выпало чётное»
благоприятствующие исходы — $\{2,4,6\}$, неблагоприятные — $\{1,3,5\}$.</div>

<div class="box def"><div class="t">Вероятность</div>
<b>Вероятность</b> <span class="en">(probability)</span> события $A$ — число $P(A)$ от $0$ до $1$,
измеряющее, насколько часто $A$ наступает.
<ul>
<li><b>Классически</b>, когда все исходы равновозможны — доля благоприятствующих:
$$P(A)=\frac{m}{n},$$
где $m$ — число благоприятствующих исходов, $n$ — число всех исходов. Для «выпало чётное»:
$P=\tfrac{3}{6}=0.5$.</li>
<li><b>Частотно</b>, когда равновозможности нет (как у цен квартир): повторяем испытание $N$ раз,
считаем, в скольких $k$ наступило $A$, и берём <b>частоту</b> $W(A)=\dfrac{k}{N}$.</li>
</ul></div>

<div class="box idea"><div class="t">Почему «повторить много раз» — ключевая и непростая мысль</div>
Вероятности <em>одного</em> исхода как будто «нет»: монета либо орёл, либо решка, никакой «$0.5$»
в единственном броске не видно. Смысл появляется только <b>в массе повторений</b>: частота $k/N$ по
мере роста $N$ перестаёт скакать и <b>устойчиво</b> оседает около одного числа — его и называют
вероятностью. Эта <b>устойчивость частот</b> — экспериментальный факт, на котором стоит вся теория.
Ровно это мы увидим в симуляторе Бернулли: чем больше бросков, тем спокойнее доля единиц липнет
к $p$.</div>

<div class="box def"><div class="t">Случайная величина</div>
<b>Случайная величина</b> <span class="en">(random variable)</span> $X$ — число, которое ставится
в соответствие исходу испытания: число очков на кубике, цена случайной квартиры, рост случайного
человека. Если значений конечный список — величина <b>дискретная</b>; если значения заполняют
промежуток (рост, цена) — <b>непрерывная</b>. <b>Распределение</b> — правило, которое каждому
значению (или диапазону) сопоставляет его вероятность.</div>

<div class="box idea"><div class="t">Связь с прошлыми тетрадями</div>
Раньше среднее и $\sigma$ мы считали <em>по</em> выборке — как сводку того, что уже есть. Теперь у
самой случайной величины есть «истинные» математическое ожидание $\mu$ и разброс $\sigma$, а наши
данные — лишь одна её <b>выборка</b>. Оценки $\bar x$ и $s$ из 03-й тетради — приближения этих
истинных величин: чем больше данных, тем точнее (та же устойчивость частот).</div>
"""
display(HTML(viz(body, wide=True)))''')

# ============================================================================
# Часть 1 — Bernoulli (expanded) + widget
# ============================================================================
code(r'''#@title Часть 1 — Распределение Бернулли: атом случайности { display-mode: "form" }
intro = r"""
<h2>Часть 1. Распределение Бернулли — атом случайности</h2>
<p>Самое простое испытание — с <b>двумя исходами</b>. Один назовём <b>успехом</b>, другой —
<b>неудачей</b>. Подбрасывание монеты (орёл/решка), клик по объявлению (кликнул/нет), признак
квартиры (есть парковка/нет) — всё это испытания Бернулли. Параметр один: вероятность успеха $p$.
Тогда вероятность неудачи $q=1-p$ (других исходов нет, сумма вероятностей равна $1$).</p>

<div class="box def"><div class="t">Распределение Бернулли</div>
<b>Случайная величина Бернулли</b> <span class="en">(Bernoulli random variable)</span> $X$ кодирует
исход числом: $X=1$ при успехе, $X=0$ при неудаче. Её вероятности:
$$P(X=1)=p,\qquad P(X=0)=q=1-p.$$
Пишут $X\sim\mathrm{Bernoulli}(p)$. Параметр $p$ полностью задаёт величину.</div>

<div class="box def"><div class="t">Ряд распределения</div>
Полный список значений и их вероятностей:
<table>
<tr><th>значение $x$</th><td>0</td><td>1</td></tr>
<tr><th>вероятность</th><td>$q=1-p$</td><td>$p$</td></tr>
</table>
Сумма вероятностей: $q+p=1$ — как и должно быть.</div>
"""

figure = r"""
<div class="widget"><div class="widget-title">Одно испытание: теория против эксперимента</div>
<div class="widget-sub">Тяни ползунок $p$. Слева — вероятности $P(0)=1-p$ и $P(1)=p$. Справа —
доли, которые дают настоящие броски; жёлтый пунктир — истинное $p$. Жми «+100 бросков» и смотри,
как эксперимент подтягивается к теории (устойчивость частот из Части 0).</div>
<svg viewBox="0 0 660 300" id="svg-bern"></svg>
<div class="controls">
<div class="control"><label>p</label><input type="range" id="bern-p" min="0" max="1" step="0.01" value="0.5"><span class="val" id="bern-pv">0.50</span></div>
<button class="btn" id="bern-add">+100 бросков</button>
<button class="btn" id="bern-res">сброс</button>
</div>
<div class="readout" id="bern-ro"></div></div>
"""

after = r"""
<div class="box def"><div class="t">Математическое ожидание и дисперсия</div>
<b>Математическое ожидание</b> — среднее значение по многим повторениям, взвешенное по вероятностям:
$$\mu=E[X]=0\cdot q+1\cdot p=p.$$
То есть «в среднем» величина Бернулли равна доле успехов $p$ — ровно то, к чему липнет частота в
эксперименте справа. <b>Дисперсия</b> — разброс вокруг $\mu$:
$$\sigma^2=D[X]=p(1-p)=pq.$$
Она максимальна при $p=0.5$ (исход самый непредсказуемый) и обращается в $0$ при $p=0$ или $p=1$
(случайности нет — исход известен заранее). Среднее квадратическое отклонение $\sigma=\sqrt{pq}$.</div>

<div class="box idea"><div class="t">Бернулли = «индикатор события» = доля</div>
Любое событие $A$ порождает величину Бернулли: $X=1$, если $A$ наступило, иначе $X=0$ (её называют
<b>индикатором</b> события). Тогда $p=P(A)$, а <b>среднее индикатора по выборке — это просто доля</b>
случаев, где $A$ произошло. Поэтому «доля квартир дороже медианы», «доля кликов», «доля бракованных»
устроены как среднее бернуллиевой величины. Это связывает частоту $k/N$ из Части 0 с арифметикой
средних из 03-й тетради.</div>

<div class="box take"><div class="t">Дальше</div>
Одно испытание предсказать нельзя. Но если <b>сложить $n$ независимых Бернулли</b> — посчитать число
успехов в серии — из суммы на глазах вырастет колоколообразная форма. Этим займёмся в Части 2.</div>
"""

script = r"""
(function(){
 const svg=document.getElementById("svg-bern"); if(!svg) return;
 const sl=document.getElementById("bern-p"), pv=document.getElementById("bern-pv");
 const bAdd=document.getElementById("bern-add"), bRes=document.getElementById("bern-res");
 const ro=document.getElementById("bern-ro");
 const LT=34, LB=250, LH=LB-LT;
 const LX=60, LW=210, RX=390, RW=210;
 let p=0.5, n0=0, n1=0;
 const yOf=q=>LB-q*LH;
 function bar(g,cx,w,q,col,lab,val){
   const y=yOf(q), h=LB-y;
   g.appendChild(el("rect",{x:cx-w/2,y:y,width:w,height:Math.max(0,h),fill:col,"fill-opacity":.85,rx:3}));
   const t=el("text",{x:cx,y:LB+16,fill:"#9aa4ae","font-size":12,"text-anchor":"middle","font-family":"sans-serif"});
   t.textContent=lab; g.appendChild(t);
   if(val!=null){const v=el("text",{x:cx,y:y-6,fill:col,"font-size":12,"text-anchor":"middle","font-family":"sans-serif","font-weight":700});
     v.textContent=val; g.appendChild(v);}
 }
 function panelFrame(g,X,W,title){
   g.appendChild(el("rect",{x:X,y:LT,width:W,height:LH,fill:"#0b0f14",stroke:"#2a313b"}));
   for(let q=0;q<=1.0001;q+=0.25){const y=yOf(q);
     g.appendChild(el("line",{x1:X,y1:y,x2:X+W,y2:y,stroke:"#19212c"}));
     const t=el("text",{x:X-6,y:y+3,fill:"#6b7580","font-size":10,"text-anchor":"end","font-family":"sans-serif"});
     t.textContent=q.toFixed(2); g.appendChild(t);}
   const tt=el("text",{x:X+W/2,y:LT-12,fill:"#e6e9ec","font-size":12,"font-weight":700,"text-anchor":"middle","font-family":"sans-serif"});
   tt.textContent=title; g.appendChild(tt);
 }
 function draw(){
   while(svg.firstChild) svg.removeChild(svg.firstChild);
   const g=el("g"); svg.appendChild(g);
   panelFrame(g,LX,LW,"Теория: P(0)=1−p, P(1)=p");
   bar(g,LX+LW*0.32,54,1-p,"#6ab0f3","0",(1-p).toFixed(2));
   bar(g,LX+LW*0.68,54,p,"#5fd08a","1",p.toFixed(2));
   panelFrame(g,RX,RW,"Эксперимент: доли по броскам");
   const n=n0+n1, e0=n?n0/n:0, e1=n?n1/n:0;
   bar(g,RX+RW*0.32,54,e0,"#6ab0f3","0",n?e0.toFixed(2):"—");
   bar(g,RX+RW*0.68,54,e1,"#5fd08a","1",n?e1.toFixed(2):"—");
   g.appendChild(el("line",{x1:RX,y1:yOf(p),x2:RX+RW,y2:yOf(p),stroke:"#e0b25a","stroke-width":1.5,"stroke-dasharray":"5 4"}));
   const pt=el("text",{x:RX+RW-4,y:yOf(p)-5,fill:"#e0b25a","font-size":10,"text-anchor":"end","font-family":"sans-serif"});
   pt.textContent="p="+p.toFixed(2); g.appendChild(pt);
   const va=p*(1-p);
   ro.innerHTML="p="+p.toFixed(2)+" · μ=p="+p.toFixed(2)+" · σ²=p(1−p)="+va.toFixed(3)
     +"  |  бросков n="+n+(n?(" · p̂="+(n1/n).toFixed(3)):"");
 }
 function addDraws(k){ for(let i=0;i<k;i++){ if(Math.random()<p) n1++; else n0++; } draw(); }
 sl.addEventListener("input",()=>{ p=+sl.value; pv.textContent=p.toFixed(2); n0=0; n1=0; draw(); });
 bAdd.addEventListener("click",()=>addDraws(100));
 bRes.addEventListener("click",()=>{ n0=0; n1=0; draw(); });
 draw();
})();
"""

display(HTML(viz(intro)))
display(HTML(viz(figure, script, wide=True)))
display(HTML(viz(after)))''')

# ============================================================================
# Часть 2 — Binomial + widget (bell emerges)
# ============================================================================
code(r'''#@title Часть 2 — Биномиальное: сумма монеток рождает колокол { display-mode: "form" }
intro = r"""
<h2>Часть 2. Биномиальное — сумма монеток рождает колокол</h2>
<p>Сложим $n$ независимых испытаний Бернулли и посчитаем <b>число успехов</b>. Сколько орлов в
20 бросках? Сколько квартир с парковкой из 50 объявлений? Это уже не $0/1$, а число от $0$ до
$n$ — <b>биномиальная</b> случайная величина.</p>
<div class="box def"><div class="t">Биномиальное распределение</div>
<b>Биномиальная случайная величина</b> <span class="en">(binomial random variable)</span>
$X \sim \mathrm{Binomial}(n,p)$ — число успехов в $n$ независимых испытаниях Бернулли с
вероятностью успеха $p$ (то есть сумма $n$ бернуллиевых величин-индикаторов). Значения: $0,1,\dots,n$;
вероятность ровно $k$ успехов
$$P(X=k)=\binom{n}{k}\,p^k(1-p)^{n-k},$$
где:
<ul>
<li>$p^k$ — вероятность, что $k$ «нужных» испытаний окажутся успехами (каждое с вероятностью $p$);</li>
<li>$(1-p)^{n-k}$ — вероятность, что остальные $n-k$ испытаний окажутся неудачами;</li>
<li>$\dbinom{n}{k}$ (читается «$n$ по $k$») — это <b>число сочетаний</b>
<span class="en">(binomial coefficient)</span>, а не дробь и не вектор-столбец: оно говорит,
<b>сколькими способами</b> $k$ успехов могут разместиться среди $n$ испытаний. Считается как
$\dbinom{n}{k}=\dfrac{n!}{k!\,(n-k)!}$. Множитель нужен потому, что успехи могут выпасть в любом
порядке, и вероятности всех этих порядков складываются.</li>
</ul></div>
"""

figure = r"""
<div class="widget"><div class="widget-title">Число успехов в n испытаниях</div>
<div class="widget-sub">Столбики — вероятности $P(X=k)$ для $\mathrm{Binomial}(n,p)$. Тяни $n$ и $p$;
включи <span style="color:#e0b25a">нормальное приближение</span> и увеличивай $n$ — смотри, как
столбики ложатся на колоколообразную кривую.</div>
<svg viewBox="0 0 760 340" id="svg-bin"></svg>
<div class="controls">
<div class="control"><label>n</label><input type="range" id="bin-n" min="1" max="60" step="1" value="10"><span class="val" id="bin-nv">10</span></div>
<div class="control"><label>p</label><input type="range" id="bin-p" min="0.01" max="0.99" step="0.01" value="0.5"><span class="val" id="bin-pv">0.50</span></div>
<div class="control"><label><input type="checkbox" id="bin-ov"> нормальное приближение</label></div>
</div>
<div class="readout" id="bin-ro"></div></div>
"""

after = r"""
<div class="box def"><div class="t">Два числа биномиального</div>
Среднее $\mu = np$, дисперсия $\sigma^2 = np(1-p)$ — это просто $n$ таких же слагаемых, как у
одной Бернулли. Биномиальное — <b>счётчик событий</b> в серии; к счётчикам во времени и
пространстве (звонки, ДТП) вернёмся, когда пойдёт распределение Пуассона.</div>
<div class="box take"><div class="t">Главное — колокол появляется сам</div>
Включи «нормальное приближение» и увеличивай $n$. Столбики, даже родившись из грубого
«орёл/решка», всё точнее ложатся на плавную колоколообразную кривую. Это не совпадение: <b>сумма
многих мелких независимых случайностей стремится к одной и той же форме</b>. Поэтому рост (сумма
множества генов и условий), ошибки измерения, шум — все тяготеют к ней. В Части 3 дадим этой форме
имя и разберём её как самостоятельный непрерывный объект — <b>нормальное распределение</b>.</div>
"""

script = r"""
(function(){
 const svg=document.getElementById("svg-bin"); if(!svg) return;
 const sn=document.getElementById("bin-n"), nv=document.getElementById("bin-nv");
 const sp=document.getElementById("bin-p"), pv=document.getElementById("bin-pv");
 const ov=document.getElementById("bin-ov"), ro=document.getElementById("bin-ro");
 const ML=46,MR=18,MT=22,MB=40,CW=760,CH=340,PW=CW-ML-MR,PH=CH-MT-MB,X0=ML,YB=MT+PH;
 const pdf=(x,mu,s)=>Math.exp(-0.5*((x-mu)/s)**2)/(s*Math.sqrt(2*Math.PI));
 function binom(n,p){
   const pmf=new Array(n+1).fill(0);
   if(p<=0){pmf[0]=1;return pmf;}
   if(p>=1){pmf[n]=1;return pmf;}
   let lg=n*Math.log(1-p); pmf[0]=Math.exp(lg);
   for(let k=1;k<=n;k++){ lg+=Math.log((n-k+1)/k)+Math.log(p/(1-p)); pmf[k]=Math.exp(lg); }
   return pmf;
 }
 function render(){
   const n=+sn.value, p=+sp.value; nv.textContent=n; pv.textContent=p.toFixed(2);
   const pmf=binom(n,p), ymax=(Math.max.apply(null,pmf)*1.15)||1;
   const bw=PW/(n+1), xpix=x=>X0+(x+0.5)*bw, syP=v=>YB-v/ymax*PH;
   while(svg.firstChild) svg.removeChild(svg.firstChild);
   const g=el("g"); svg.appendChild(g);
   g.appendChild(el("rect",{x:X0,y:MT,width:PW,height:PH,fill:"#0b0f14",stroke:"#2a313b"}));
   const tstep=Math.max(1,Math.round(n/10));
   for(let k=0;k<=n;k+=tstep){ const cx=xpix(k);
     const tl=el("text",{x:cx,y:YB+15,fill:"#6b7580","font-size":10,"text-anchor":"middle","font-family":"sans-serif"});tl.textContent=k;g.appendChild(tl);}
   for(let k=0;k<=n;k++){ const h=YB-syP(pmf[k]);
     g.appendChild(el("rect",{x:xpix(k)-bw*0.42,y:syP(pmf[k]),width:bw*0.84,height:Math.max(0,h),fill:"#5fd08a","fill-opacity":.75}));}
   const mu=n*p, sd=Math.sqrt(n*p*(1-p));
   if(ov.checked && sd>0){
     let d="M";
     for(let i=0;i<=120;i++){ const x=i/120*n; d+=" "+xpix(x).toFixed(1)+" "+syP(pdf(x,mu,sd)).toFixed(1); }
     g.appendChild(el("path",{d:d,fill:"none",stroke:"#e0b25a","stroke-width":2.4}));
   }
   ro.innerHTML="Binomial(n="+n+", p="+p.toFixed(2)+") · μ=np="+mu.toFixed(2)
     +" · σ²=np(1−p)="+(n*p*(1-p)).toFixed(2)+" · σ="+sd.toFixed(2);
 }
 sn.addEventListener("input",render); sp.addEventListener("input",render); ov.addEventListener("change",render);
 render();
})();
"""

display(HTML(viz(intro)))
display(HTML(viz(figure, script, wide=True)))
display(HTML(viz(after)))''')

# ---------------------------------------------------------------------------
# Guide: generating Bernoulli / binomial with numpy (markdown, play with it)
# ---------------------------------------------------------------------------
md(r"""
### Сгенерируем случайность сами: Бернулли и биномиальное

Прежде чем идти дальше — потрогайте случайность руками. `numpy` умеет «бросать монетку» за нас.

**Способ 1 — сравнить равномерное число с $p$.** `np.random.rand()` даёт число из $[0,1)$, где все
значения равновероятны. Значит событие «число $< p$» наступает с вероятностью ровно $p$:

```python
import numpy as np
p = 0.3
x  = int(np.random.rand() < p)               # 1 с вероятностью p, иначе 0
xs = (np.random.rand(1000) < p).astype(int)  # сразу 1000 испытаний Бернулли
print(xs[:20])
print("доля единиц:", xs.mean())             # ≈ p (устойчивость частот из Части 0)
```

**Способ 2 — готовые функции numpy** (современный генератор `default_rng` и явные вероятности):

```python
rng = np.random.default_rng(0)
xs = rng.binomial(1, p, size=1000)           # Bernoulli(p): биномиальное с n=1
xs = rng.choice([0, 1], size=1000, p=[1-p, p])   # выбор из {0,1} с заданными вероятностями
print("μ ≈", xs.mean(), " σ² ≈", xs.var())   # сравните с p и p(1-p)
```

**Биномиальное — это сумма $n$ бернуллиевых**, её тоже можно получить одним вызовом:

```python
k = rng.binomial(n=20, p=0.3, size=1000)     # 1000 раз «сколько успехов из 20»
print("μ ≈", k.mean(), " против np =", 20*0.3)
```

> **Поиграйтесь:** меняйте `p` и размер выборки. Куда идёт `xs.mean()`, когда испытаний становится
> больше? При каком `p` дисперсия `p(1-p)` максимальна? Постройте гистограмму `k` (`plt.hist(k)`) —
> на что она похожа при большом `n`?
""")

# ============================================================================
# Часть 3 — Normal distribution (rebuilt) + widget with boxplot
# ============================================================================
code(r'''#@title Часть 3 — Нормальное (гауссово) распределение { display-mode: "form" }
intro = r"""
<h2>Часть 3. Нормальное (гауссово) распределение</h2>
<p><b>Постановка.</b> Рост, цена, вес — <b>непрерывные</b> величины: между любыми двумя значениями
есть промежуточные, исходов бесконечно много. Ряд распределения (таблицу «значение → вероятность»)
тут не построить: вероятность попасть <em>точно</em> в одну точку равна нулю. Нужен другой способ
описания — через <b>плотность</b>.</p>

<div class="box def"><div class="t">Функция плотности вероятности</div>
Для непрерывной величины задают <b>функцию плотности вероятности</b>
<span class="en">(probability density function)</span> $f(x)$. Сама высота $f(x)$ — не вероятность.
Вероятность $P(a<X<b)$ — это <b>площадь под кривой</b> $f(x)$ на участке от $a$ до $b$. Два правила:
$f(x)\ge 0$ всюду, и <b>вся площадь под кривой равна $1$</b> (величина точно принимает
<em>какое-то</em> значение). В симуляторе ниже эти площади показаны штриховкой — зелёные полосы —
и есть вероятности попасть в $\mu\pm\sigma$, $\mu\pm2\sigma$, $\mu\pm3\sigma$.</div>

<div class="box def"><div class="t">Нормальное распределение $N(\mu,\sigma)$</div>
Величина распределена <b>нормально</b> (по Гауссу), если её плотность —
$$f(x)=\frac{1}{\sigma\sqrt{2\pi}}\;e^{-\frac12\left(\frac{x-\mu}{\sigma}\right)^2}.$$
У неё два параметра, оба знакомы из 03-й тетради:
<ul>
<li>$\mu$ — <b>математическое ожидание</b>: центр, вершина кривой (двигает график влево-вправо);</li>
<li>$\sigma$ — <b>среднее квадратическое отклонение</b>: ширина (растягивает или сжимает).</li>
</ul>
Кривая симметрична относительно $\mu$ и имеет колоколообразную форму. Пишут $X\sim N(\mu,\sigma)$.</div>
"""

figure = r"""
<div class="widget"><div class="widget-title">Нормальное распределение и его сигма-полосы</div>
<div class="widget-sub">Тяни $\mu$ (сдвиг) и $\sigma$ (ширина). Зелёные полосы (площади под кривой) —
$\mu\pm1\sigma$, $\pm2\sigma$, $\pm3\sigma$. Снизу — боксплот того же распределения. Строка внизу:
доли площади держатся у 68/95/99.7% при любых $\mu$ и $\sigma$.</div>
<svg viewBox="0 0 760 400" id="svg-gauss"></svg>
<div class="controls">
<div class="control"><label>μ</label><input type="range" id="g-mu" min="-3" max="3" step="0.1" value="0"><span class="val" id="g-muv">0.0</span></div>
<div class="control"><label>σ</label><input type="range" id="g-sd" min="0.5" max="2.5" step="0.1" value="1"><span class="val" id="g-sdv">1.0</span></div>
</div>
<div class="readout" id="g-ro"></div></div>
"""

after = r"""
<div class="box idea"><div class="t">Боксплот под кривой — что он показывает</div>
Под плотностью нарисован боксплот того же распределения. Для нормального распределения усы стоят
примерно на $\mu\pm2.7\sigma$ (это $Q_1,Q_3\pm1.5\cdot\mathrm{IQR}$ при $\mathrm{IQR}\approx1.35\sigma$)
— почти там же, где забор трёх сигм. Поэтому на нормальных данных боксплот и правило $3\sigma$
помечают почти одно и то же. Расхождение начнётся на скошенных данных — в Части 4.</div>

<div class="box idea"><div class="t">Стандартизация и стандартное нормальное распределение</div>
Замена $z=\dfrac{x-\mu}{\sigma}$ (<b>центрирование</b> — вычли $\mu$; <b>нормирование</b> — поделили
на $\sigma$) переводит <em>любое</em> нормальное распределение в одно и то же — <b>стандартное
нормальное распределение</b> $N(0,1)$ с центром $0$ и шириной $1$. Это ровно z-преобразование из
03-й тетради; теперь у него вероятностный смысл: $z$ — это «на сколько сигм значение отстоит от
центра».</div>

<div class="box take"><div class="t">Правило 68–95–99.7</div>
Куда ни двигай $\mu$ и как ни тяни $\sigma$ — доли площади (вероятности) в полосах <b>не
меняются</b>:
<ul>
<li>$\mu\pm1\sigma$ — около <b>68%</b> значений;</li>
<li>$\mu\pm2\sigma$ — около <b>95%</b>;</li>
<li>$\mu\pm3\sigma$ — около <b>99.7%</b>.</li>
</ul>
Значит, расстояние в сигмах — это сразу вероятность. $|z|>2$ — редкое значение (внешние ~5%),
$|z|>3$ — совсем редкое (~0.3%). На этом построим детектор выбросов в Части 4.
<br><span style="color:#7f8a96;font-size:.9em">(«95% значений в $\mu\pm2\sigma$» — это про отдельные
наблюдения; не путать с доверительным интервалом для оценки — к нему придём в теме оценивания.)</span></div>
"""

script = r"""
(function(){
 const svg=document.getElementById("svg-gauss"); if(!svg) return;
 const sm=document.getElementById("g-mu"), mv=document.getElementById("g-muv");
 const ss=document.getElementById("g-sd"), sv=document.getElementById("g-sdv");
 const ro=document.getElementById("g-ro");
 const ML=30,MR=18,MT=18,CW=760,PW=CW-ML-MR,X0=ML;
 const DPH=250, YB=MT+DPH, BY=YB+64, BH=30;
 const XMIN=-6,XMAX=6, sx=v=>X0+(v-XMIN)/(XMAX-XMIN)*PW;
 const pdf=(x,mu,s)=>Math.exp(-0.5*((x-mu)/s)**2)/(s*Math.sqrt(2*Math.PI));
 const ymax=1/(0.5*Math.sqrt(2*Math.PI))*1.08;
 const syD=d=>YB-d/ymax*DPH;
 function render(){
   const mu=+sm.value, sd=+ss.value; mv.textContent=mu.toFixed(1); sv.textContent=sd.toFixed(1);
   while(svg.firstChild) svg.removeChild(svg.firstChild);
   const g=el("g"); svg.appendChild(g);
   g.appendChild(el("rect",{x:X0,y:MT,width:PW,height:DPH,fill:"#0b0f14",stroke:"#2a313b"}));
   for(let t=XMIN;t<=XMAX;t++) g.appendChild(el("line",{x1:sx(t),y1:MT,x2:sx(t),y2:YB,stroke:"#141b23"}));
   const G=240, xs=[]; for(let i=0;i<G;i++) xs.push(XMIN+(XMAX-XMIN)*i/(G-1));
   const band=k=>{ const a=mu-k*sd,b=mu+k*sd; let d="M "+sx(a).toFixed(1)+" "+YB.toFixed(1);
     for(let i=0;i<G;i++){ if(xs[i]<a||xs[i]>b) continue; d+=" L "+sx(xs[i]).toFixed(1)+" "+syD(pdf(xs[i],mu,sd)).toFixed(1);}
     d+=" L "+sx(b).toFixed(1)+" "+YB.toFixed(1)+" Z";
     g.appendChild(el("path",{d:d,fill:"#5fd08a","fill-opacity":.14})); };
   band(3); band(2); band(1);
   let pth="M"; for(let i=0;i<G;i++) pth+=" "+sx(xs[i]).toFixed(1)+" "+syD(pdf(xs[i],mu,sd)).toFixed(1);
   g.appendChild(el("path",{d:pth,fill:"none",stroke:"#6ab0f3","stroke-width":2.4}));
   for(let k=-3;k<=3;k++){ const x=mu+k*sd; if(x<XMIN||x>XMAX) continue;
     g.appendChild(el("line",{x1:sx(x),y1:YB,x2:sx(x),y2:YB+5,stroke:"#3a434f"}));
     const t=el("text",{x:sx(x),y:YB+18,fill:"#6b7580","font-size":10,"text-anchor":"middle","font-family":"sans-serif"});
     t.textContent=(k===0?"μ":(k>0?"+":"")+k+"σ"); g.appendChild(t);}
   const q1=mu-0.6745*sd, q3=mu+0.6745*sd, med=mu, iqr=q3-q1, wlo=q1-1.5*iqr, whi=q3+1.5*iqr;
   const cl=x=>Math.max(XMIN,Math.min(XMAX,x));
   const bt=el("text",{x:X0,y:BY-BH/2-8,fill:"#9aa4ae","font-size":11,"font-family":"sans-serif"});
   bt.textContent="боксплот того же распределения"; g.appendChild(bt);
   g.appendChild(el("line",{x1:sx(cl(wlo)),y1:BY,x2:sx(cl(whi)),y2:BY,stroke:"#e0757f","stroke-width":1.5}));
   [wlo,whi].forEach(w=>g.appendChild(el("line",{x1:sx(cl(w)),y1:BY-7,x2:sx(cl(w)),y2:BY+7,stroke:"#e0757f","stroke-width":1.5})));
   g.appendChild(el("rect",{x:sx(q1),y:BY-BH/2,width:sx(q3)-sx(q1),height:BH,fill:"#6ab0f3","fill-opacity":.20,stroke:"#6ab0f3","stroke-width":1.5}));
   g.appendChild(el("line",{x1:sx(med),y1:BY-BH/2,x2:sx(med),y2:BY+BH/2,stroke:"#ffffff","stroke-width":2}));
   const area=k=>{ const a=mu-k*sd,b=mu+k*sd,M=400,dx=(b-a)/M; let s=0;
     for(let i=0;i<M;i++){ const x=a+(i+0.5)*dx; s+=pdf(x,mu,sd)*dx;} return s; };
   ro.innerHTML="μ±1σ = "+area(1).toFixed(3)+" · μ±2σ = "+area(2).toFixed(3)
     +" · μ±3σ = "+area(3).toFixed(3)+"  — не зависят от μ и σ · усы боксплота ≈ μ±2.7σ";
 }
 sm.addEventListener("input",render); ss.addEventListener("input",render);
 render();
})();
"""

display(HTML(viz(intro)))
display(HTML(viz(figure, script, wide=True)))
display(HTML(viz(after)))''')

# ---------------------------------------------------------------------------
# Guide: generating normal values with numpy (markdown, play with it)
# ---------------------------------------------------------------------------
md(r"""
### Сгенерируем нормальные значения сами

Так же можно «сгенерировать» рост, шум, ошибку измерения — любую нормальную величину.

**Стандартное нормальное $N(0,1)$** — функция `randn` (или `standard_normal`):

```python
import numpy as np
z = np.random.randn(1000)                    # 1000 значений из N(0,1)
print("μ ≈", z.mean().round(2), " σ ≈", z.std().round(2))   # ≈ 0 и 1
```

**Произвольное $N(\mu,\sigma)$** — задаём центр и ширину:

```python
rng = np.random.default_rng(0)
x = rng.normal(loc=170, scale=8, size=1000)  # рост: μ=170, σ=8
x = 170 + 8 * rng.standard_normal(1000)      # то же вручную: μ + σ·z (обратная сторона стандартизации)
```

**Проверьте правило 68–95–99.7 прямо на своей выборке:**

```python
mu, sd = x.mean(), x.std()
for k in (1, 2, 3):
    share = np.mean(np.abs(x - mu) < k*sd)
    print(f"в μ±{k}σ попало {share:.1%}")     # ≈ 68% / 95% / 99.7%
```

> **Поиграйтесь:** меняйте `μ` и `σ`, стройте гистограмму (`plt.hist(x, bins=40)`). Сдвигается ли
> центр вслед за `μ`? Как ширина колокола зависит от `σ`? Совпадают ли доли с обещанными
> 68/95/99.7?
""")

# ============================================================================
# Часть 3b — 2D normal distribution (scatter + KDE + sigma ellipses)
# ============================================================================
code(r'''#@title Часть 3 (продолжение) — Двумерное нормальное распределение { display-mode: "form" }
intro = r"""
<h2>Часть 3 (продолжение). Двумерное нормальное распределение</h2>
<p>Одно наблюдение с двумя признаками — это <b>точка на плоскости</b> $(x_1,x_2)$. Группа похожих
объектов образует <b>облако</b> точек; если по каждому признаку разброс примерно нормальный, то и
облако — <b>двумерное нормальное</b>. Посмотрим на него двумя способами: как на скаттер точек и как
на карту плотности.</p>
<div class="box def"><div class="t">Линии уровня и σ-эллипсы</div>
<b>Линия уровня</b> плотности — след, вдоль которого плотность одна и та же (как изолинии высоты на
топографической карте). У двумерного нормального облака линии уровня — <b>эллипсы</b> вокруг центра.
Полосы «одна / две / три сигмы» из одномерного случая здесь становятся <b>вложенными эллипсами</b>:
внутри эллипса $1\sigma$ — самые типичные объекты, за $3\sigma$ — далёкие одиночки.</div>
"""

figure = r"""
<div class="widget"><div class="widget-title">Двумерное нормальное облако: точки и плотность</div>
<div class="widget-sub">Слева — облако наблюдений (скаттер), справа — та же выборка как карта плотности
(KDE). Зелёные <span style="color:#5fd08a">эллипсы</span> — уровни 1σ, 2σ, 3σ. Тяни
$\sigma_x$, $\sigma_y$ или пересэмплируй.</div>
<svg viewBox="0 0 760 380" id="svg-2d"></svg>
<div class="controls">
<div class="control"><label>σx</label><input type="range" id="d2-sx" min="0.5" max="2" step="0.1" value="1.4"><span class="val" id="d2-sxv">1.4</span></div>
<div class="control"><label>σy</label><input type="range" id="d2-sy" min="0.5" max="2" step="0.1" value="0.9"><span class="val" id="d2-syv">0.9</span></div>
<button class="btn" id="d2-re">пересэмплировать</button>
</div>
<div class="readout" id="d2-ro"></div></div>
"""

after = r"""
<div class="box idea"><div class="t">Зачем это дальше</div>
Это картинка, к которой курс будет возвращаться. «Наблюдение = точка в пространстве признаков» — та
самая идея из линала. Расстояние до центра облака (в сигмах по каждой оси) — способ измерить,
насколько объект типичен; на этом стоят поиск похожих (kNN) и детекция аномалий. А форма облака —
вход в <b>ковариационную матрицу</b> (неделя 4), где мы разрешим осям эллипса наклоняться (сейчас
они строго вдоль признаков).</div>
"""

script = r"""
(function(){
 const svg=document.getElementById("svg-2d"); if(!svg) return;
 const ssx=document.getElementById("d2-sx"), vx=document.getElementById("d2-sxv");
 const ssy=document.getElementById("d2-sy"), vy=document.getElementById("d2-syv");
 const btn=document.getElementById("d2-re"), ro=document.getElementById("d2-ro");
 const DX=6, PPU=25, P0=300, Lx=40, Rx=420, TY=40;
 const sxL=v=>Lx+(v+DX)*PPU, syL=v=>TY+(DX-v)*PPU;
 const sxR=v=>Rx+(v+DX)*PPU, syR=v=>TY+(DX-v)*PPU;
 let sgx=1.4, sgy=0.9, pts=[];
 function randn(){ let u=0,v=0; while(u===0)u=Math.random(); while(v===0)v=Math.random(); return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v); }
 function sample(){ pts=[]; for(let i=0;i<300;i++) pts.push([randn()*sgx, randn()*sgy]); }
 function panel(g,ox,title){
   g.appendChild(el("rect",{x:ox,y:TY,width:P0,height:P0,fill:"#0b0f14",stroke:"#2a313b"}));
   for(let t=-6;t<=6;t+=2){
     g.appendChild(el("line",{x1:ox+(t+DX)*PPU,y1:TY,x2:ox+(t+DX)*PPU,y2:TY+P0,stroke:"#141b23"}));
     g.appendChild(el("line",{x1:ox,y1:TY+(DX-t)*PPU,x2:ox+P0,y2:TY+(DX-t)*PPU,stroke:"#141b23"}));
   }
   const tt=el("text",{x:ox+P0/2,y:TY-10,fill:"#e6e9ec","font-size":12,"font-weight":700,"text-anchor":"middle","font-family":"sans-serif"});
   tt.textContent=title; g.appendChild(tt);
 }
 function ellipses(g,cx,cy){
   for(let k=1;k<=3;k++)
     g.appendChild(el("ellipse",{cx:cx,cy:cy,rx:k*sgx*PPU,ry:k*sgy*PPU,fill:"none",stroke:"#5fd08a","stroke-width":1.6,"stroke-opacity":(0.9-0.2*k).toFixed(2)}));
 }
 function render(){
   vx.textContent=sgx.toFixed(1); vy.textContent=sgy.toFixed(1);
   while(svg.firstChild) svg.removeChild(svg.firstChild);
   const g=el("g"); svg.appendChild(g);
   panel(g,Lx,"Скаттер: облако наблюдений");
   for(const p of pts) g.appendChild(el("circle",{cx:sxL(p[0]),cy:syL(p[1]),r:2.3,fill:"#6ab0f3","fill-opacity":.7}));
   ellipses(g,sxL(0),syL(0));
   panel(g,Rx,"Плотность (KDE) и σ-эллипсы");
   const NX=32,NY=32,h=0.7; let dens=[],dmax=0;
   for(let iy=0;iy<NY;iy++){ dens.push([]); const gy=-DX+(iy+0.5)/NY*2*DX;
     for(let ix=0;ix<NX;ix++){ const gx=-DX+(ix+0.5)/NX*2*DX; let s=0;
       for(const p of pts){ const ux=(gx-p[0])/h, uy=(gy-p[1])/h; s+=Math.exp(-0.5*(ux*ux+uy*uy)); }
       dens[iy].push(s); if(s>dmax)dmax=s; } }
   const cw=P0/NX, ch=P0/NY;
   for(let iy=0;iy<NY;iy++)for(let ix=0;ix<NX;ix++){ const o=dmax?dens[iy][ix]/dmax:0; if(o<0.03) continue;
     g.appendChild(el("rect",{x:Rx+ix*cw,y:TY+(NY-1-iy)*ch,width:cw+0.6,height:ch+0.6,fill:"#6ab0f3","fill-opacity":(o*0.85).toFixed(3)})); }
   ellipses(g,sxR(0),syR(0));
   ro.innerHTML="σx="+sgx.toFixed(1)+" · σy="+sgy.toFixed(1)+" · N="+pts.length
     +" · зелёные эллипсы — 1σ, 2σ, 3σ";
 }
 ssx.addEventListener("input",()=>{ sgx=+ssx.value; sample(); render(); });
 ssy.addEventListener("input",()=>{ sgy=+ssy.value; sample(); render(); });
 btn.addEventListener("click",()=>{ sample(); render(); });
 sample(); render();
})();
"""

display(HTML(viz(intro)))
display(HTML(viz(figure, script, wide=True)))
display(HTML(viz(after)))''')

# ============================================================================
# Data for the three-sigma demo (Davis height + Bishkek price)
# ============================================================================
code(r"""
# В Colab: !pip install -q datasets
import numpy as np, pandas as pd, json
from huggingface_hub import hf_hub_download
from datasets import load_dataset

# Почти нормальный признак: рост мужчин (Davis)
_dv   = load_dataset("aiacademy-kg/davis_dataset", split="train").to_pandas()
men_h = pd.to_numeric(_dv.loc[_dv["sex"] == "M", "height"], errors="coerce").dropna()
men_h = men_h[men_h.between(140, 210)].to_numpy(float)

# Скошенный признак: цена квартир Бишкека (house.kg)
_p  = hf_hub_download("aiacademy-kg/house_kg_full_dataset",
                      "data/listings.parquet", repo_type="dataset")
_ap = pd.read_parquet(_p)
_ap = _ap[(_ap.deal == "sale") & (_ap.type == "apartment") & (_ap.city == "Бишкек")].copy()
_ap["price_usd"] = pd.to_numeric(_ap["price_usd"], errors="coerce")
price = _ap.dropna(subset=["price_usd"])["price_usd"].to_numpy() / 1000.0   # тыс. USD

print("рост мужчин:", len(men_h), "| цена квартир:", len(price))
""")

# ============================================================================
# Часть 4 — three-sigma rule + widget with boxplot
# ============================================================================
code(r'''#@title Часть 4 — Правило трёх сигм: детектор выбросов { display-mode: "form" }
import numpy as np, json
_rng = np.random.default_rng(0)
def _samp(a, k):
    a = a[np.isfinite(a)]
    return a if len(a) <= k else _rng.choice(a, size=k, replace=False)
NORM_JSON = json.dumps([round(float(v), 2) for v in _samp(men_h, 400)])
_pr = price[(price >= 10) & (price <= 700)]                  # без ультра-выбросов-ошибок, скос сохраняем
SKEW_JSON = json.dumps([round(float(v), 1) for v in _samp(_pr, 1200)])

intro = r"""
<h2>Часть 4. Правило трёх сигм — детектор выбросов</h2>
<p>Раз в нормальном распределении за $\mu\pm3\sigma$ лежит лишь ~0.3% значений, напрашивается
правило: <b>считать выбросом всё, что дальше трёх сигм от среднего</b>. Просто и популярно. Но у
него есть скрытое условие — <b>данные должны быть распределены нормально</b>. Проверим на двух
признаках.</p>
<div class="box def"><div class="t">Правило трёх сигм</div>
<span class="en">(three-sigma rule)</span> Точка $x$ — кандидат в выбросы, если
$|z|=\left|\dfrac{x-\mu}{\sigma}\right|>3$, то есть $x<\mu-3\sigma$ или $x>\mu+3\sigma$. Иногда
берут порог $2\sigma$ (строже) — им управляет ползунок $k$.</div>
"""

figure = r"""
<div class="widget"><div class="widget-title">Правило трёх сигм на реальных данных</div>
<div class="widget-sub">Сверху — кривая плотности с <span style="color:#e0b25a">средним</span> и
<span style="color:#e0757f">забором $\mu\pm k\sigma$</span>. Снизу — боксплот того же признака (по
квартилям, не зависит от формы). Переключи признак и число сигм; следи за строкой: сколько точек за
забором против ожидаемых для нормали.</div>
<svg viewBox="0 0 760 400" id="svg-ts"></svg>
<div class="controls">
<div class="control"><label>признак</label><select id="ts-feat"><option value="norm">рост (≈нормаль)</option><option value="skew">цена (скошен)</option></select></div>
<div class="control"><label>k·σ</label><input type="range" id="ts-k" min="1" max="4" step="0.5" value="3"><span class="val" id="ts-kv">3.0</span></div>
</div>
<div class="readout" id="ts-ro"></div></div>
"""

after = r"""
<div class="box take"><div class="t">Где правило врёт</div>
<ul>
<li><b>Рост</b> ≈ нормаль: за $3\sigma$ ловится ~0.3% — как обещано, и усы боксплота стоят почти на
том же месте, что забор $3\sigma$. Правило работает.</li>
<li><b>Цена</b> скошена вправо: за $3\sigma$ оказывается заметно больше 0.3%, и почти все «выбросы»
— справа. Это не значит, что данные полны выбросов — <b>это само правило врёт</b>: $\mu$ и $\sigma$
раздуты длинным хвостом, а симметричный забор $\pm3\sigma$ не подходит скошенной форме. Боксплот
снизу тоже перекошен, но его правый ус ближе, чем $\mu+3\sigma$.</li>
</ul>
Диагностика прямо из силлабуса: <em>«3σ пометило 8% — это выбросы или признак не нормальный?»</em>
Ответ — сравни долю флагов с ожидаемыми ~0.3%. Сильно больше → дело в форме, а не в данных.</div>
<div class="box idea"><div class="t">Параметрика против непараметрики (мост к 04)</div>
Правило $3\sigma$ — <b>параметрическое</b>: опирается на форму (нормаль) и ломается, если угадали
неверно. Боксплот и усы $1.5\cdot\mathrm{IQR}$ из 04 — <b>непараметрические</b>: формы не знают,
считают по квартилям и на скошенной цене ведут себя честнее. Отсюда правило: похоже на нормальное
распределение — можно $3\sigma$; скошено или тяжёлые хвосты — бери квартили/усы.</div>
"""

script = r"""
(function(){
 const svg=document.getElementById("svg-ts"); if(!svg) return;
 const DN=__NORM__, DS=__SKEW__;
 const sel=document.getElementById("ts-feat"), sk=document.getElementById("ts-k"),
       kv=document.getElementById("ts-kv"), ro=document.getElementById("ts-ro");
 const ML=46,MR=18,MT=20,CW=760,PW=CW-ML-MR,X0=ML;
 const DPH=232, YB=MT+DPH, BY=YB+70, BH=30;
 const mean=a=>a.reduce((p,c)=>p+c,0)/a.length;
 const std=a=>{const m=mean(a);return Math.sqrt(a.reduce((p,x)=>p+(x-m)*(x-m),0)/a.length);};
 const quant=(s,q)=>{const h=(s.length-1)*q,k=Math.floor(h);return k>=s.length-1?s[s.length-1]:s[k]+(h-k)*(s[k+1]-s[k]);};
 const kde=(arr,xs,h)=>{const n=arr.length,c=1/(n*h*Math.sqrt(2*Math.PI));return xs.map(x=>{let s=0;for(const xi of arr){const u=(x-xi)/h;s+=Math.exp(-0.5*u*u);}return c*s;});};
 const erf=x=>{const t=1/(1+0.3275911*Math.abs(x));const y=1-(((((1.061405429*t-1.453152027)*t)+1.421413741)*t-0.284496736)*t+0.254829592)*t*Math.exp(-x*x);return x<0?-y:y;};
 const Phi=z=>0.5*(1+erf(z/Math.SQRT2));
 function niceStep(x){const p=Math.pow(10,Math.floor(Math.log10(x)));const f=x/p;return (f<1.5?1:f<3?2:f<7?5:10)*p;}
 function render(){
   const skew=sel.value==="skew";
   const data=(skew?DS:DN).slice().sort((a,b)=>a-b);
   const k=+sk.value; kv.textContent=k.toFixed(1);
   const n=data.length, m=mean(data), sd=std(data);
   const q1=quant(data,0.25), q3=quant(data,0.75), med=quant(data,0.5), iqr=q3-q1;
   const wlo=data.find(v=>v>=q1-1.5*iqr), whi=[...data].reverse().find(v=>v<=q3+1.5*iqr);
   const lo=data[0], hi=data[n-1], pad=(hi-lo)*0.06, xmin=lo-pad, xmax=hi+pad;
   const sx=v=>X0+(v-xmin)/(xmax-xmin)*PW;
   while(svg.firstChild) svg.removeChild(svg.firstChild);
   const g=el("g"); svg.appendChild(g);
   g.appendChild(el("rect",{x:X0,y:MT,width:PW,height:DPH,fill:"#0b0f14",stroke:"#2a313b"}));
   const step=niceStep((xmax-xmin)/6);
   for(let t=Math.ceil(xmin/step)*step;t<=xmax;t+=step){
     g.appendChild(el("line",{x1:sx(t),y1:MT,x2:sx(t),y2:YB,stroke:"#19212c"}));
     const tl=el("text",{x:sx(t),y:BY+BH/2+18,fill:"#6b7580","font-size":10,"text-anchor":"middle","font-family":"sans-serif"});tl.textContent=Math.round(t);g.appendChild(tl);}
   const h=Math.max(1e-6,1.06*sd*Math.pow(n,-0.2));
   const G=220, xs=[]; for(let i=0;i<G;i++) xs.push(xmin+(xmax-xmin)*i/(G-1));
   const dens=kde(data,xs,h), dmax=Math.max.apply(null,dens)||1, syD=d=>YB-d/dmax*(DPH*0.9);
   let pth="M "+sx(xmin).toFixed(1)+" "+YB.toFixed(1);
   for(let i=0;i<G;i++) pth+=" L "+sx(xs[i]).toFixed(1)+" "+syD(dens[i]).toFixed(1);
   pth+=" L "+sx(xmax).toFixed(1)+" "+YB.toFixed(1)+" Z";
   g.appendChild(el("path",{d:pth,fill:"#6ab0f3","fill-opacity":.16,stroke:"#6ab0f3","stroke-width":2}));
   const flo=m-k*sd, fhi=m+k*sd;
   const vline=(x,col,w,dash)=>{const cx=sx(x); if(cx<X0-2||cx>X0+PW+2)return;
     g.appendChild(el("line",{x1:cx,y1:MT,x2:cx,y2:BY+BH/2,stroke:col,"stroke-width":w||2,"stroke-dasharray":dash||""}));};
   vline(m,"#e0b25a",2,"5 4"); vline(flo,"#e0757f",2,"6 4"); vline(fhi,"#e0757f",2,"6 4");
   const cl=x=>Math.max(X0+18,Math.min(X0+PW-18,sx(x)));
   const lbl=(x,txt,col)=>{const t=el("text",{x:cl(x),y:MT+13,fill:col,"font-size":11,"text-anchor":"middle","font-family":"sans-serif"});t.textContent=txt;g.appendChild(t);};
   lbl(flo,"μ−"+k+"σ","#e0757f"); lbl(fhi,"μ+"+k+"σ","#e0757f");
   const bxt=el("text",{x:X0,y:BY-BH/2-8,fill:"#9aa4ae","font-size":11,"font-family":"sans-serif"});
   bxt.textContent="боксплот (по квартилям — не зависит от формы)"; g.appendChild(bxt);
   g.appendChild(el("line",{x1:sx(wlo),y1:BY,x2:sx(whi),y2:BY,stroke:"#e0b25a","stroke-width":1.5}));
   [wlo,whi].forEach(w=>g.appendChild(el("line",{x1:sx(w),y1:BY-7,x2:sx(w),y2:BY+7,stroke:"#e0b25a","stroke-width":1.5})));
   g.appendChild(el("rect",{x:sx(q1),y:BY-BH/2,width:sx(q3)-sx(q1),height:BH,fill:"#e0b25a","fill-opacity":.16,stroke:"#e0b25a","stroke-width":1.5}));
   g.appendChild(el("line",{x1:sx(med),y1:BY-BH/2,x2:sx(med),y2:BY+BH/2,stroke:"#ffffff","stroke-width":2}));
   for(const v of data){ if(v<wlo||v>whi) g.appendChild(el("circle",{cx:sx(v),cy:BY,r:2.4,fill:"#e0757f","fill-opacity":.5})); }
   const outHi=data.filter(v=>v>fhi).length, outLo=data.filter(v=>v<flo).length, out=outHi+outLo;
   const outW=data.filter(v=>v<wlo||v>whi).length, exp=2*(1-Phi(k))*100;
   ro.innerHTML="признак: "+(skew?"цена (скошен)":"рост (≈нормаль)")+" · n="+n
     +" · μ="+m.toFixed(1)+" · σ="+sd.toFixed(1)
     +" || за |z|>"+k.toFixed(1)+": "+out+" ("+(100*out/n).toFixed(1)+"%), ждали ~"+exp.toFixed(2)+"%"
     +" · за усами боксплота: "+outW+" ("+(100*outW/n).toFixed(1)+"%)";
 }
 sel.addEventListener("change",render); sk.addEventListener("input",render);
 render();
})();
""".replace("__NORM__", NORM_JSON).replace("__SKEW__", SKEW_JSON)

display(HTML(viz(intro)))
display(HTML(viz(figure, script, wide=True)))
display(HTML(viz(after)))''')

# ============================================================================
# Practice tasks
# ============================================================================
md(r"""
### Задания — распределения и выбросы на своих данных

Датасет house.kg (Бишкек, квартиры). К каждому пункту — вывод словами, а не только число.

**Task 1.** Возьми признак, похожий на нормальный (напр. `ppm2` — цена за м², или `area_m2` в
пределах типичных квартир), и признак, категорически не нормальный (`price_usd`). Построй
гистограммы. Обоснуй словами и графиком, кто на нормальное распределение похож, а кто нет.

**Task 2.** Для «нормального» признака посчитай $\mu$ и $\sigma$ и проверь правило 68–95–99.7:
какие доли реально попадают в $\mu\pm1\sigma$, $\mu\pm2\sigma$, $\mu\pm3\sigma$? Близко ли к
обещанному?

**Task 3.** Примени правило трёх сигм к `price_usd`. Сколько процентов помечено? Сравни с ~0.3%.
Это выбросы или признак просто не нормальный? Как ты это доказываешь?

**Task 4.** На том же `price_usd` найди выбросы по усам боксплота (1.5·IQR) и по трём сигмам.
Совпадают ли множества? Какой способ уместнее на скошенной цене и почему (вспомни 04)?

**Task 5 (Бернулли / биномиальное).** Заведи бинарный признак («дороже медианы» = 1, иначе 0) —
это Бернулли. Оцени $p$ как долю единиц. Если случайно взять 20 квартир, сколько из них в среднем
будут «дорогими» и какова дисперсия этого числа? (подсказка: биномиальное, $np$ и $np(1-p)$.)
""")

# ============================================================================
# Write
# ============================================================================
nb = new_notebook(cells=cells)
nb.metadata = META
out = os.path.join(HERE, "05_stat_normal.ipynb")
with open(out, "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("wrote", out, "cells:", len(cells))
