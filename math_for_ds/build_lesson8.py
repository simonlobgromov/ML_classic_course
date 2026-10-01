"""Build the self-contained Colab lesson 08_stat_ci_bootstrap.ipynb.

Run from any directory: venv/bin/python math_for_ds/build_lesson8.py
Widget source is embedded into the notebook; students need only the .ipynb.
"""
from pathlib import Path
import hashlib
import json

import nbformat as nbf
from theme import SETUP, META

HERE = Path(__file__).resolve().parent
WIDGET_JS = (HERE / "lesson8_widgets.js").read_text(encoding="utf-8")
cells = []


def md(source):
    cells.append(nbf.v4.new_markdown_cell(source.strip()))


def code(source):
    cells.append(nbf.v4.new_code_cell(source.strip()))


def eq(formula, meanings):
    """Every displayed theory equation must have a local symbol glossary."""
    if not meanings:
        raise ValueError("An equation needs its symbol glossary")
    return ("<div class='d8-equation'>$$" + formula + "$$</div>"
            + "<div class='where'><b>Обозначения.</b> " + meanings + "</div>")


def definition(title, body):
    return f'<div class="box def"><div class="t">{title}</div>{body}</div>'


def theory(title, body):
    code(f'#@title {title} {{ display-mode: "form" }}\n'
         + 'display(HTML(lesson8_viz(' + repr(body) + ')))')


def slider(key, label, low, high, step, default):
    return (f'<label class="d8-control"><span>{label}</span>'
            f'<input type="range" data-control="{key}" min="{low}" max="{high}" step="{step}" value="{default}">'
            f'<output data-value="{key}">{default}</output></label>')


def select(key, label, choices):
    return (f'<label class="d8-control"><span>{label}</span><select data-control="{key}">'
            + ''.join(f'<option value="{value}">{name}</option>' for value, name in choices)
            + '</select></label>')


def widget(kind, title, instruction, charts, controls, question, optional=False, intro=""):
    svg = ''.join(f'<svg data-chart="{key}"></svg>' for key in charts)
    body = (f'<div class="widget"><div class="widget-title">{title}</div>'
            + intro + f'<p class="widget-sub">{instruction}</p>'
            f'<div class="d8-controls">{controls}</div>'
            f'<div class="d8-charts">{svg}</div>'
            '<div class="readout" data-readout role="status" aria-live="polite"></div>'
            f'<p class="d8-question"><b>Проверь себя.</b> {question}</p>'
            '<p class="d8-footnote">Учебная симуляция. Числа округлены; новое повторение может дать другой результат.</p></div>')
    if optional:
        body = '<details><summary>Дополнительно: ' + title + '</summary>' + body + '</details>'
    code(f'#@title Интерактив — {title} {{ display-mode: "form" }}\n'
         + 'display(HTML(lesson8_viz(' + repr(body) + ', widget=' + repr(kind) + ')))')




def box(title, body, kind="take"):
    return f'<div class="box {kind}"><div class="t">{title}</div>{body}</div>'


def button(action, label):
    return f'<button class="btn" data-action="{action}">{label}</button>'


md(r"""
# Насколько точно мы знаем среднее?
## Занятие 8 — доверительный интервал и бутстрап

По 100 доставкам получили среднее время. Другая сотня заказов дала бы немного другой ответ.
**Как показать точность нашей оценки, если среднее всех доставок неизвестно?**

Продолжаем занятие 7: среднее меняется от выборки к выборке, а стандартная ошибка описывает этот разброс.
Теперь построим **интервал для неизвестного среднего**, затем научимся оценивать неопределённость
по одной выборке с помощью **бутстрапа**.

**План двух встреч:** первая — разделы 1–5 (смысл доверительного интервала и задача о доставках);
вторая — раздел 6 (бутстрап), обзор раздела 7 и практика 8. Дополнительные опыты можно оставить на семинар.
Перед проверкой гипотез разберём точность оценки. Статистические тесты и p-value будем изучать отдельно.

Перед опытом предскажите результат, после — объясните наблюдение. Важные выводы выделены рамками.
После интерактивов идут разобранные примеры NumPy и seaborn; задания для самостоятельной работы отмечены отдельно.
Все данные **синтетические**: известный генератор позволяет проверять наши методы.

В Colab: **«Среда выполнения → Выполнить все»**. Ноутбук содержит весь код интерактивов;
формулы загружаются через MathJax. Ползунки работают независимо от Python-ячеек:
чтобы повторить опыт в коде, измените числа в самой ячейке. Блоки «Дополнительно» можно пропускать.
""")

EXTRA_SETUP = r'''
import json
import uuid
import re
from html import escape

D8_CSS = r"""
.vec-root .d8-controls{display:flex;flex-wrap:wrap;gap:12px 24px;margin:16px 0 22px;font-family:system-ui,sans-serif;}
.vec-root .d8-control{display:flex;align-items:center;flex-wrap:wrap;gap:8px;color:var(--ink);font-size:14px;min-height:36px;}
.vec-root .d8-control input[type=range]{width:155px;min-height:30px;}
.vec-root .d8-control output{font-variant-numeric:tabular-nums;color:var(--green);min-width:42px;}
.vec-root .d8-control select{max-width:100%;padding:8px;}
.vec-root .d8-control input:disabled{opacity:.3;}
.vec-root .d8-charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,380px),1fr));gap:16px;}
.vec-root .d8-charts svg{display:block;width:100%;height:auto;background:#0e1319;border-radius:10px;}
.vec-root .d8-charts svg:last-child:nth-child(3){grid-column:1/-1;max-width:780px;justify-self:center;}
.vec-root[data-widget=clusters] .d8-charts svg:first-child{grid-column:1/-1;max-width:780px;justify-self:center;}
.vec-root[data-widget=clusters] .d8-charts svg:last-child{grid-column:auto;max-width:none;}
.vec-root .readout{overflow-wrap:anywhere;font:15px/1.75 system-ui,sans-serif;}
.vec-root .d8-question{font-family:system-ui,sans-serif;font-size:14px;color:var(--ink);}
.vec-root .d8-footnote{font-family:system-ui,sans-serif;font-size:12px;color:var(--soft);}
.vec-root .d8-equation{overflow-x:auto;overflow-y:hidden;padding:5px 0;}
.vec-root .where{line-height:1.7;}
.vec-root .d8-table{overflow-x:auto;}
.vec-root input:focus-visible,.vec-root select:focus-visible,.vec-root button:focus-visible{outline:2px solid #e0b25a;outline-offset:4px;}
@media(max-width:600px){.vec-root .wrap{padding:14px;font-size:16px;}.vec-root .widget{padding:10px;}.vec-root .d8-control{width:100%;}}
"""

def lesson8_viz(body, widget=None):
    """Scope controls to a fresh root so rerunning cells keeps widgets independent."""
    # HTML is parsed before MathJax. Protect comparisons and ampersands in both
    # display equations and inline symbol glossaries without escaping HTML tags.
    body = re.sub(
        r"(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$.*?(?<!\\)\$",
        lambda match: escape(match.group(0), quote=False),
        body,
        flags=re.DOTALL,
    )
    root_id = "d8_" + uuid.uuid4().hex
    script = D8_WIDGET_JS + "\n" + r"""
    (function(){
      const root = document.getElementById(__ROOT__);
      const widget = __WIDGET__;
      if (widget) window.InferenceLesson8.mount(root, widget);
      const typeset = () => window.MathJax.typesetPromise([root]);
      if (!window.__D8_MATH_READY__) {
        if (window.MathJax && window.MathJax.typesetPromise) {
          window.__D8_MATH_READY__ = window.MathJax.startup.promise;
        } else {
          window.MathJax = {tex:{inlineMath:[['$','$']],displayMath:[['$$','$$']]},svg:{fontCache:'local'},startup:{typeset:false}};
          window.__D8_MATH_READY__ = new Promise((resolve, reject) => {
            const loader = document.createElement('script');
            loader.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
            loader.onload = () => window.MathJax.startup.promise.then(resolve, reject);
            loader.onerror = reject;
            document.head.appendChild(loader);
          });
        }
      }
      window.__D8_MATH_READY__ = window.__D8_MATH_READY__.then(typeset).catch(() => {
        if(root.querySelector('.d8-equation')) {
          const notice = document.createElement('p');
          notice.textContent = 'Для отображения формул подключитесь к интернету и перезапустите ячейку. Графики работают без загрузки MathJax.';
          root.appendChild(notice);
        }
      });
    })();
    """.replace("__ROOT__", json.dumps(root_id)).replace("__WIDGET__", json.dumps(widget))
    return ("<style>" + CSS + D8_CSS + "</style>"
            + '<div class="vec-root" data-widget="' + (widget or "theory") + '" id="' + root_id + '"><div class="wrap wide">'
            + body + '</div></div><script>' + script + '</script>')

print("Занятие 8 готово: графики работают в браузере; формулы загружаются через MathJax.")
'''
code(SETUP + '\n\nD8_WIDGET_JS = ' + repr(WIDGET_JS) + '\n' + EXTRA_SETUP)

code('''import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm, bootstrap

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams.update({"figure.figsize": (10, 4), "axes.spines.top": False,
                     "axes.spines.right": False})
rng = np.random.default_rng(2026)
''')

md(r"""
## 1. Среднее посчитали. Насколько оно точное?

Изучаем доставки одного процесса при неизменных условиях. В нашей модели каждое время независимо
от других, а распределение времён одно и то же. Одна выборка содержит 100 доставок.

Нас интересует **среднее время всех доставок этого процесса**. Сначала мы знаем ответ из генератора
и проверяем расчёты. Позже скроем его и будем использовать только выборку.
""")
widget("sampling", "Одна выборка — один ответ",
       "Предскажите, изменится ли среднее. Получите одну новую выборку, затем ещё 200. Сравните левую и правую оси.",
       ["data", "means"],
       select("n", "Доставок в выборке", [(100,"100"),(20,"20"),(400,"400")])
       + button("one", "Новая выборка") + button("many", "Ещё 200 выборок"),
       "Почему столбцы справа описывают средние, а не отдельные доставки?")
theory("Оценка и её точность", definition("Точечная оценка · point estimate",
       "<p>Число, рассчитанное по выборке для приближения неизвестного параметра генеральной совокупности. "
       "Например, выборочное среднее оценивает среднее ГС.</p>")
       + box("Что предстоит добавить", "<p>Одного среднего недостаточно для описания точности. "
             "Добавим интервал, способ построения которого учитывает случайность выборки.</p>")
       + box("Два разных вопроса", "<p><b>Каково среднее всех доставок?</b> — вопрос об оценке параметра.<br>"
             "<b>Сколько займёт следующая доставка?</b> — вопрос об отдельном наблюдении. "
             "В этом занятии строим интервал для среднего.</p>", "idea"))

md(r"""
**Разобранный пример: получаем выборку и строим гистограмму.**

`rng.exponential(scale=20, size=n)` создаёт `n` независимых положительных времён ожидания
из экспоненциального распределения — распределения с длинным правым хвостом, у которого здесь
среднее и SD равны 20. Добавление 10 минут даёт модель из занятия 7: среднее 30, SD 20.
Изучать формулу этого распределения сейчас не требуется: это наш известный учебный генератор.

Повторный запуск ячейки даст новые доставки. `mu_true` и `sigma_true` — сведения о генераторе;
в реальном исследовании такие сведения могут быть недоступны.
""")
code('''n = 100
mu_true = 30.0
sigma_true = 20.0
delivery_times = 10 + rng.exponential(scale=20, size=n)
sample_mean = delivery_times.mean()

ax = sns.histplot(delivery_times, bins=20, color="#478ac9")
ax.axvline(sample_mean, color="#14804a", lw=2, label="Среднее выборки")
ax.axvline(mu_true, color="#b67a10", ls="--", lw=2, label="Истинное среднее")
ax.set(xlabel="Время одной доставки, мин", ylabel="Число доставок",
       title=f"{n} наблюдений; среднее выборки {sample_mean:.2f} мин")
ax.legend()
plt.show()
''')

md(r"""
## 2. Где окажутся средние новых выборок?

При повторном сборе данных меняется выборочное среднее. **Стандартная ошибка (SE)** — стандартное
отклонение распределения этих средних. Вспомним её смысл из занятия 7.

Теперь выделим область, в которую среднее выборки должно попадать примерно в 95% повторений.
Это пока **фиксированная область вокруг известного среднего ГС**.
""")
widget("band", "95% под кривой распределения средних",
       "Начните со 100 доставок. Уменьшите n до 5, затем увеличьте до 400. Сравните заданную площадь и фактическую долю попаданий.",
       ["band"],
       select("n", "Размер выборки n", [(100,"100"),(5,"5"),(20,"20"),(400,"400")])
       + select("level", "Центральная область", [(.95,"95%"),(.8,"80%"),(.9,"90%"),(.99,"99%")])
       + button("new", "Новые 3000 выборок"),
       "Почему число 95% относится здесь к выборочным средним, а не к отдельным доставкам?")
theory("От SE к границам области", r"""
<p>Если распределение выборочного среднего близко к нормальному, центральная область шириной
примерно четыре SE содержит около 95% средних. Точный коэффициент для каждой стороны — примерно 1,96.</p>"""
    + eq(r"SE(\bar X)=\frac{\sigma}{\sqrt n},\qquad h=1.96\frac{\sigma}{\sqrt n}.",
         r"$\bar X$ — среднее случайной выборки; $SE$ — его стандартная ошибка; $\sigma$ — известное SD ГС; "
         r"$n$ — размер выборки; $h$ — расстояние от центра до каждой границы. Число 1,96 получено из стандартного нормального распределения.")
    + eq(r"P\!\left(\mu-h\leq\bar X\leq\mu+h\right)\approx0.95.",
         r"$P$ — вероятность; $\mu$ — истинное среднее ГС; $\bar X$ — случайное выборочное среднее; "
         r"$h=1.96\sigma/\sqrt n$ — половина ширины области; $\sigma$ — SD ГС; $n$ — размер выборки.")
    + box("Условия имеют значение", "<p>Формула SE требует независимых одинаково распределённых наблюдений "
          "с конечной дисперсией. Нормальная форма средних точна для нормальной ГС; для наших асимметричных доставок "
          "используем приближение по ЦПТ. Единого правила «n ≥ 30 всегда достаточно» нет.</p>", "warn")
    + r"""<details><summary>Откуда 1,96 и как получить другой уровень?</summary>
<p>Квантиль — значение, слева от которого лежит заданная доля распределения. Для центральных 95%
остаётся по 2,5% в каждом хвосте: нужна квантиль уровня 97,5%. Функция <code>norm.ppf</code>
находит квантиль стандартной нормали. Это обратная операция к знакомой <code>norm.cdf</code>.</p>"""
    + eq(r"z=\Phi^{-1}\!\left(\frac{1+c}{2}\right),\qquad h=z\frac{\sigma}{\sqrt n}.",
         r"$c$ — выбранная центральная вероятность (например, 0,95); $\Phi$ — CDF стандартной нормали; "
         r"$\Phi^{-1}$ — её функция квантилей; $z$ — нужная квантиль; $h$ — половина ширины; "
         r"$\sigma$ — известное SD ГС; $n$ — размер выборки.")
    + '</details><p>Источник: <a href="https://www.itl.nist.gov/div898/handbook/prc/section1/prc14.htm">NIST — доверительные интервалы при известной σ</a>.</p>')

md(r"""
**Разобранный пример: повторяем сбор данных в цикле.** В списке `sample_means` одна запись — среднее
целой выборки. `norm.ppf(0.975)` даёт коэффициент без округления до 1,96.
Гистограмма оценивает плотность средних, поэтому её можно сравнивать с нормальной плотностью на той же шкале.
""")
code('''n = 100
repetitions = 3000
sample_means = []
for _ in range(repetitions):
    new_sample = 10 + rng.exponential(scale=20, size=n)
    sample_means.append(new_sample.mean())
sample_means = np.array(sample_means)

se_known = sigma_true / np.sqrt(n)
z = norm.ppf(0.975)
h = z * se_known
x_grid = np.linspace(sample_means.min(), sample_means.max(), 400)
density = norm.pdf(x_grid, loc=mu_true, scale=se_known)

ax = sns.histplot(sample_means, bins=35, stat="density", color="#478ac9")
ax.plot(x_grid, density, color="#b67a10", label="Нормальное приближение")
inside = (x_grid >= mu_true - h) & (x_grid <= mu_true + h)
ax.fill_between(x_grid, 0, density, where=inside, color="#e0b25a", alpha=0.4)
ax.axvline(mu_true, color="#b67a10", ls="--", label="Среднее ГС")
ax.set(xlabel="Среднее одной выборки, мин", ylabel="Плотность, 1/мин")
ax.legend()
plt.show()
print("Доля средних внутри области:", np.mean(np.abs(sample_means - mu_true) <= h))
''')

md(r"""
## 3. Истинное среднее неизвестно: меняем центр интервала

Предыдущая область требовала знания среднего ГС. В исследовании именно его и нужно найти.
Но выражение «два числа отличаются не больше чем на h» одинаково в обе стороны.
Используем это, чтобы построить интервал **вокруг наблюдаемого среднего**.
""")
widget("inversion", "Одно событие — два способа его показать",
       "Двигайте среднее выборки. Найдите момент, когда попадание сменится промахом. Затем измените размер выборки и уровень доверия.",
       ["fixed", "moving"],
       slider("estimate", "Среднее выборки, мин", 15, 60, .1, 33)
       + select("n", "Размер выборки", [(100,"100"),(25,"25"),(400,"400")])
       + select("level", "Уровень", [(.95,"95%"),(.8,"80%"),(.99,"99%")])
       + button("new", "Среднее новой случайной выборки"),
       "Что случайно на левом графике? Что случайно на правом? Почему цвет меняется одновременно?")
theory("Почему вероятность сохраняется", eq(
    r"\mu-h\leq\bar X\leq\mu+h\quad\Longleftrightarrow\quad\bar X-h\leq\mu\leq\bar X+h.",
    r"$\mu$ — фиксированное среднее ГС; $\bar X$ — случайное выборочное среднее; $h$ — одна и та же половина ширины. "
    r"$\Longleftrightarrow$ означает равносильность: условия выполняются одновременно.")
    + box("Меняется то, что мы считаем неизвестным", "<p>Слева неподвижный интервал и случайная точка. "
          "Справа неподвижное среднее ГС и случайный интервал. Это одно событие попадания.</p>", "idea")
    + definition("Доверительный интервал · confidence interval (CI)",
          "<p>Интервал, границы которого вычисляют по выборке по правилу с заданной вероятностью "
          "покрытия неизвестного параметра. При повторном сборе данных это правило должно накрывать "
          "параметр с указанной вероятностью; для приближённых методов — приблизительно.</p>")
    + eq(r"I(\bar X)=[\bar X-h,\ \bar X+h],\qquad P\!\left(\mu\in I(\bar X)\right)\approx0.95.",
         r"$I(\bar X)$ — случайный интервал по выборке; $\bar X$ — её среднее; $h=1.96\sigma/\sqrt n$; "
         r"$\sigma$ — известное SD ГС; $n$ — размер выборки; $\mu$ — среднее ГС; $P$ — вероятность; $\in$ означает «принадлежит».")
    + box("Формулировка для устного ответа", "<p>95%-й доверительный интервал строят способом, "
          "который при многократном повторении исследования накрывает истинный параметр примерно в 95% случаев.</p>")
    + box("После вычисления границ", "<p>У конкретного рассчитанного интервала границы уже фиксированы. "
          "Он либо накрыл фиксированное среднее ГС, либо нет; мы обычно не знаем, какой случай произошёл. "
          "95% характеризуют процедуру построения. Само выборочное среднее находится в центре нашего "
          "симметричного интервала всегда.</p>", "warn"))

md(r"""
**Разобранный пример: один интервал на обычном графике.** Используем `delivery_times` из раздела 1.
Функции `hlines` и `scatter` из Matplotlib рисуют отрезок и точку; seaborn задаёт оформление.
Это интервал из явно рассчитанных границ, без автоматического расчёта библиотекой.
""")
code('''estimate = delivery_times.mean()
margin = norm.ppf(0.975) * sigma_true / np.sqrt(len(delivery_times))
ci_low, ci_high = estimate - margin, estimate + margin

fig, ax = plt.subplots(figsize=(10, 3))
ax.hlines(y=0, xmin=ci_low, xmax=ci_high, color="#14804a", lw=5)
ax.scatter([estimate], [0], color="#14804a", s=80, zorder=3, label="Среднее выборки")
ax.axvline(mu_true, color="#b67a10", ls="--", label="Среднее ГС: известно для проверки")
ax.set(xlabel="Среднее время доставки, мин", yticks=[], ylim=(-1, 1),
       title=f"Приближённый 95%-й ДИ: [{ci_low:.2f}; {ci_high:.2f}] мин")
ax.legend()
plt.show()
''')

md(r"""
## 4. 95% интервалов: повторяем всё исследование

Один интервал не показывает надёжность метода. Для проверки нужно каждый раз получать **новые исходные данные**.
В симуляции мы можем это сделать и подсчитать долю попаданий. В реальном исследовании истинный ответ обычно скрыт.
""")
widget("coverage", "Истинное среднее неподвижно, интервалы меняются",
       "Посмотрите на точки и отрезки. Поднимите уровень с 95% до 99%, сохраняя выборки. Затем увеличьте размер выборки и получите новую серию.",
       ["forest"],
       select("n", "Наблюдений n", [(100,"100"),(5,"5"),(20,"20"),(400,"400")])
       + select("M", "Исследований", [(500,"500"),(100,"100"),(2000,"2000")])
       + select("level", "Уровень доверия", [(.95,"95%"),(.8,"80%"),(.99,"99%")])
       + select("shape", "Источник", [("skew","Асимметричные доставки"),("normal","Нормальная модель для сравнения")])
       + button("new", "Новая серия исследований"),
       "Почему в серии из 100 исследований не обязано быть ровно 95 попаданий? Что даёт более высокий уровень доверия?")
theory("Покрытие, ширина и размер выборки", definition("Покрытие · coverage",
    "<p>Вероятность того, что построенный по случайной выборке интервал содержит истинный параметр. "
    "Долю накрывших параметр интервалов в серии симуляций называем наблюдаемой частотой покрытия.</p>")
    + box("Три закономерности", "<ul><li>При фиксированных σ и уровне доверия увеличение n в четыре раза "
          "уменьшает ширину нашего интервала вдвое.</li><li>При фиксированных n и σ повышение уровня доверия "
          "расширяет интервал.</li><li>Увеличение числа симулированных исследований уточняет оценку покрытия; "
          "оно не сужает интервал отдельного исследования.</li></ul>")
    + box("Условия не исчезают", "<p>Заявленные 95% относятся к модели и процедуре. Смещённый отбор, "
          "зависимость наблюдений или плохое нормальное приближение могут нарушить покрытие.</p>", "warn")
    + '<p>Источник: <a href="https://itl.nist.gov/div898/handbook/eda/section3/eda352.htm">NIST — частотный смысл доверительного интервала</a>.</p>')

md("**Разобранный пример: 200 исследований в Python.** Цвет каждого интервала определяем сравнением его границ с известной истиной.")
code('''n = 100
experiments = 200
margin = norm.ppf(0.975) * sigma_true / np.sqrt(n)
records = []
for experiment in range(experiments):
    new_sample = 10 + rng.exponential(scale=20, size=n)
    estimate = new_sample.mean()
    low, high = estimate - margin, estimate + margin
    records.append([experiment + 1, estimate, low, high, low <= mu_true <= high])
intervals = pd.DataFrame(records, columns=["experiment", "estimate", "low", "high", "covered"])

fig, ax = plt.subplots(figsize=(10, 6))
for row in intervals.head(40).itertuples():
    color = "#14804a" if row.covered else "#c44555"
    ax.hlines(row.experiment, row.low, row.high, color=color, lw=2)
    ax.scatter(row.estimate, row.experiment, color=color, s=15)
ax.axvline(mu_true, color="#b67a10", ls="--", label="Среднее ГС")
ax.set(xlabel="Среднее время, мин", ylabel="Номер исследования", title="Первые 40 интервалов из 200")
ax.legend()
plt.show()
print(f"Частота покрытия по всем {experiments} исследованиям: {intervals['covered'].mean():.1%}")
''')

md(r"""
## 5. Задача о доставке: что можно сообщить руководителю?

**Самостоятельно.** В следующей ячейке — новая выборка из 100 доставок. В учебной постановке
SD ГС известно и равно 20 минутам, а истинное среднее исследователь не использует.

1. Рассчитайте среднее и приближённый 95%-й доверительный интервал при известном SD ГС.
2. Покажите гистограмму отдельных времён и рядом отдельный график среднего с интервалом.
3. Напишите вывод о среднем времени в двух предложениях. Можно ли этим интервалом обосновать
   обещание «95% заказов доставим внутри указанных границ»? Объясните по графикам.
4. Предскажите, как изменится типичная ширина при 400 наблюдениях. Затем проверьте на новой выборке.

Фраза «среднее истинной ГС попало» здесь недоступна исследователю: для вывода используйте только наблюдения
и известное SD. Генератор нужен нам для учебной проверки, а не как источник готового ответа.
""")
code('''task_rng = np.random.default_rng(808)
task_delivery = 10 + task_rng.exponential(scale=20, size=100)
task_sigma = 20.0

# TODO: Compute the mean and the standard error under the stated assumptions.
# TODO: Find the interval bounds and draw both requested plots.
# TODO: Explain the result in the next Markdown cell.
''')
md("**Ваш вывод:** …")
theory("Граница первой встречи", box("Что мы уже умеем", "<p>Различаем разброс доставок и точность среднего. "
    "Строим интервал при известном SD ГС, объясняем его уровень доверия и проверяем покрытие на симуляциях.</p>")
    + box("Следующий вопрос", "<p>Параметры ГС обычно неизвестны. Как оценить неопределённость, "
          "если доступна только одна выборка? И как поступить, если интересует медиана?</p>", "idea")
    + r"""<details><summary>Если вместо известной σ подставить выборочное s?</summary>
<p>Так получают нормальный приближённый интервал с оценённой SE. Для больших подходящих выборок он может
работать хорошо, но подстановка добавляет неопределённость: точность 95% для малых выборок не гарантирована.
Специальные методы на основе t-распределения будем изучать отдельно.</p>
</details>""")

md(r"""
## 6. Бутстрап: одна выборка, много повторных расчётов

### 6.1. Что можно сделать с уже собранными наблюдениями?

Новые исследования дороги, а сохранённые данные доступны. Попробуем использовать их распределение
как приближение к распределению ГС. Из имеющихся записей будем случайно выбирать столько же записей,
сколько было исходно, **с возвращением**. После каждого выбора запись снова доступна для выбора.

Начнём с 12 наблюдений, чтобы каждое было видно. Это демонстрация механики; маленькая выборка сама по себе
не становится надёжной благодаря бутстрапу.
""")
widget("resampling", "Как получается одна бутстрап-выборка",
       "Сделайте одно повторение и найдите повторившиеся номера. Накопите 200 средних. Затем сравните с отбором всех записей без возвращения.",
       ["original", "resample", "bootmeans"],
       select("replace", "Способ отбора", [("yes","С возвращением — бутстрап"),("no","Без возвращения — сравнение")])
       + button("one", "Одно повторение") + button("many", "Ещё 200 повторений")
       + button("source", "Новые 12 исходных наблюдений"),
       "Почему без возвращения среднее не меняется? Сколько новых реальных наблюдений появилось после 200 повторений?")
theory("Определение бутстрапа и зачем он нужен", definition("Бутстрап · bootstrap",
    "<p>Метод приближённого оценивания выборочного распределения статистики путём многократного "
    "создания повторных выборок на основе имеющихся данных и пересчёта статистики.</p>")
    + definition("Обычный непараметрический бутстрап · nonparametric bootstrap",
    "<p>Для независимых одинаково распределённых наблюдений получаем повторные выборки того же размера "
    "случайным отбором исходных записей с возвращением. Каждая исходная запись имеет одинаковую вероятность "
    "выбора. Если значения нескольких записей совпадают, их вероятности складываются.</p>")
    + definition("Эмпирическое распределение · empirical distribution",
    "<p>Распределение, которое приписывает наблюдённым значениям вероятности, равные их долям в выборке. "
    "Его CDF — знакомая эмпирическая функция распределения. При обычном бутстрапе выбираем из этого распределения.</p>")
    + box("Для чего нужен бутстрап", "<p>Для оценки стандартной ошибки, построения доверительных интервалов "
          "и изучения того, как меняется результат при повторном сборе данных. Он полезен, когда статистику "
          "легко посчитать, а удобная формула её неопределённости неизвестна — например, для медианы.</p>")
    + box("Что мы предполагаем", "<p>Наблюдаемая выборка должна достаточно хорошо описывать интересующее "
          "распределение, а схема повторного отбора — сохранять существенное устройство данных. "
          "В основной части считаем доставки независимыми. Бутстрап не исправляет смещённый сбор данных.</p>", "warn")
    + '<p>Объяснение идеи: <a href="https://arxiv.org/html/1411.5279">T. Hesterberg — Bootstrap and Resampling</a>.</p>')

md(r"""
**Разобранный пример: выбор с возвращением в NumPy.** `rng.choice` выбирает случайные элементы массива.
`size` задаёт число выбранных элементов, `replace=True` разрешает выбирать одну запись повторно.
`np.arange` создаёт номера записей; по ним видно, какие доставки повторились.
""")
code('''small_sample = delivery_times[:12]
indices = rng.choice(np.arange(len(small_sample)), size=len(small_sample), replace=True)
resampled = small_sample[indices]
display(pd.DataFrame({"Номер исходной записи": indices + 1, "Время, мин": resampled.round(2)}))
print("Среднее исходных 12 записей:", small_sample.mean())
print("Среднее повторной выборки:", resampled.mean())
print("Число разных выбранных записей:", len(np.unique(indices)))
''')
md("**Самостоятельно:** предскажите результат при `replace=False`, затем проверьте его в предыдущей ячейке. Почему этот опыт не показывает неопределённость среднего?")

md(r"""
### 6.2. От повторных средних к стандартной ошибке

Фиксируем исходные 100 наблюдений. Для каждой повторной выборки сохраняем **одно число** — её среднее.
Разброс этих чисел используем как оценку стандартной ошибки.

Обратите внимание: бутстрап-средние располагаются около **исходного выборочного среднего**.
Оно не обязано совпадать с истинным средним ГС.
""")
code('''bootstrap_rng = np.random.default_rng(8008)
B = 2000
boot_means = []
for _ in range(B):
    repeated_sample = bootstrap_rng.choice(delivery_times, size=len(delivery_times), replace=True)
    boot_means.append(repeated_sample.mean())
boot_means = np.array(boot_means)

se_boot = boot_means.std(ddof=1)
se_formula = delivery_times.std(ddof=1) / np.sqrt(len(delivery_times))
ax = sns.histplot(boot_means, bins=35, color="#14804a")
ax.axvline(delivery_times.mean(), color="#14804a", lw=2, label="Исходное выборочное среднее")
ax.axvline(mu_true, color="#b67a10", ls="--", label="Истинное среднее — только для проверки")
ax.set(xlabel="Среднее бутстрап-выборки, мин", ylabel="Число повторений")
ax.legend()
plt.show()
print(f"SE по бутстрапу: {se_boot:.3f} мин; оценка s / √n: {se_formula:.3f} мин")
''')
theory("Что именно мы оценили", box("SE — разброс оценок", "<p>Стандартное отклонение исходных времён "
    "описывает различия между доставками. Стандартное отклонение бутстрап-средних оценивает неопределённость "
    "среднего. Не смешивайте два массива.</p>")
    + eq(r"\widehat{SE}_{\mathrm{boot}}=\operatorname{SD}(\bar x_1^*,\ldots,\bar x_B^*).",
         r"$\widehat{SE}_{\mathrm{boot}}$ — бутстрап-оценка стандартной ошибки; "
         r"$\bar x_b^*$ — среднее b-й повторной выборки; звёздочка отмечает бутстрап; "
         r"$B$ — число повторений; $\operatorname{SD}$ — выборочное стандартное отклонение с делителем B − 1.")
    + box("n и B отвечают за разное", "<p><b>n</b> — сколько исходных наблюдений мы собрали. "
          "<b>B</b> — сколько повторных выборок посчитал компьютер. Увеличение B уменьшает вычислительные "
          "колебания оценки SE и квантилей, но не добавляет информации о ГС.</p>", "idea")
    + r"""<details><summary>Почему две оценки SE близки, но не обязаны совпасть?</summary>
<p>Бутстрап использует конечное эмпирическое распределение, а формула с выборочным SD содержит поправку
через делитель n − 1. Дополнительно влияет конечное число бутстрап-повторений. Сравниваем близость,
а не требуем равенства до последнего знака.</p></details>""")

md(r"""
### 6.3. Простой интервал по квантилям

Возьмём квантили 2,5% и 97,5% **бутстрап-значений статистики**. Это границы центральных 95%.
Такой способ называют **квантильным, или процентильным, бутстрап-интервалом (percentile interval)**.
Он прост для знакомства; его фактическую надёжность мы проверим в следующем опыте.
""")
theory("Формула квантильного интервала", eq(r"I_{\mathrm{perc}}=[q^*_{0.025},\ q^*_{0.975}].",
    r"$I_{\mathrm{perc}}$ — приближённый 95%-й процентильный интервал; "
    r"$q^*_{0.025}$ и $q^*_{0.975}$ — квантили уровней 2,5% и 97,5% распределения бутстрап-оценок. "
    r"Звёздочка обозначает бутстрап; это квантили средних (или другой выбранной статистики), а не исходных наблюдений.")
    + box("Две разные доли", "<p>Мы берём центральные 95% <b>бутстрап-оценок</b>. "
          "Это ещё не доказывает, что полученный метод накрывает <b>истинный параметр</b> в 95% новых исследований. "
          "Для такого вывода нужны условия и проверка точности приближения.</p>", "warn"))
widget("bootstrap", "Среднее и доверительный интервал по одной выборке",
       "Сначала меняйте только B и повторяйте бутстрап. Затем получите новую исходную выборку. Откройте истину для проверки. Медиану можно исследовать дополнительно.",
       ["data", "distribution", "interval"],
       select("n", "Исходных доставок n", [(100,"100"),(20,"20"),(50,"50"),(400,"400")])
       + select("B", "Повторений B", [(2000,"2000"),(200,"200"),(5000,"5000")])
       + select("level", "Уровень интервала", [(.95,"95%"),(.8,"80%"),(.99,"99%")])
       + select("stat", "Что оцениваем", [("mean","Среднее"),("median","Медиана — дополнительный опыт")])
       + select("truth", "Истинный ответ", [("hide","Скрыт"),("show","Показать для проверки")])
       + button("repeat", "Повторить бутстрап") + button("source", "Новая исходная выборка"),
       "Какая кнопка создаёт новые наблюдения? Почему 5000 повторений не равны 5000 изученным доставкам?")

md("**Разобранный пример: границы интервала и два обычных графика.** Данные для гистограммы — сохранённые `boot_means`, а не новые доставки.")
code('''boot_low, boot_high = np.quantile(boot_means, [0.025, 0.975])
estimate = delivery_times.mean()
fig, axes = plt.subplots(1, 2, figsize=(13, 4))
sns.histplot(boot_means, bins=35, color="#14804a", ax=axes[0])
axes[0].axvspan(boot_low, boot_high, color="#14804a", alpha=0.15)
axes[0].axvline(estimate, color="#14804a", lw=2)
axes[0].set(xlabel="Среднее бутстрап-выборки, мин", ylabel="Число повторений",
            title="Центральные 95% бутстрап-средних")
axes[1].hlines(0, boot_low, boot_high, color="#14804a", lw=5)
axes[1].scatter([estimate], [0], color="#14804a", s=80, label="Среднее выборки")
axes[1].axvline(mu_true, color="#b67a10", ls="--", label="Истина — для проверки")
axes[1].set(xlabel="Среднее время, мин", yticks=[], ylim=(-1, 1),
            title=f"Интервал [{boot_low:.2f}; {boot_high:.2f}]")
axes[1].legend()
plt.tight_layout()
plt.show()
''')

md(r"""
### 6.4. Проверяем покрытие бутстрап-интервала

Здесь два уровня повторения. **Внешний:** собираем совершенно новую исходную выборку.
**Внутренний:** для этой одной выборки делаем бутстрап и получаем один интервал.

Сначала предскажите: будет ли метод, который берёт центральные 95% бутстрап-средних,
всегда давать около 95% покрытия истинного среднего? Проверьте на малых и более крупных выборках.
""")
widget("bootcoverage", "Много новых исследований, внутри каждого — свой бутстрап",
       "Начните с n = 10. Увеличьте размер до 100 и повторите серию. Сравните частоты покрытия, не только отдельные отрезки.",
       ["known", "bootstrap"],
       select("n", "Доставок в каждом исследовании", [(10,"10"),(30,"30"),(100,"100")])
       + select("M", "Новых исследований", [(100,"100"),(300,"300")])
       + button("new", "Повторить серию исследований"),
       "Почему нельзя оценить покрытие, просто многократно выполняя бутстрап одной и той же исходной выборки?")
theory("Что считать проверкой метода", box("В симуляции мы знаем истину", "<p>Для оценки покрытия "
    "повторяем весь путь: новая исходная выборка → её бутстрап → один интервал → проверка попадания истины. "
    "Один удачный интервал не доказывает надёжность метода.</p>")
    + box("Ограничения обычного бутстрапа", "<ul><li>Малая выборка может плохо представлять ГС, "
          "особенно редкие большие значения.</li><li>Повторный отбор не исправляет исходное смещение "
          "и не восстанавливает события, которых мы не наблюдали.</li><li>Зависимость требует подходящей схемы "
          "отбора.</li><li>Для крайних квантилей, максимума и других чувствительных статистик простой бутстрап "
          "может работать плохо. Его универсальность не означает автоматическую точность.</li></ul>", "warn")
    + '<p>Источник: <a href="https://research.google/pubs/what-teachers-should-know-about-the-bootstrap-resampling-in-the-undergraduate-statistics-curriculum/">Hesterberg — точность бутстрап-интервалов, особенно на малых выборках</a>.</p>')

md(r"""
**Разобранный пример: два цикла.** Внешний цикл создаёт 120 новых исследований.
Внутренний делает 400 повторных выборок для каждого из них. Это небольшой учебный расчёт:
его частота покрытия и квантили ещё заметно колеблются.
""")
code('''coverage_rng = np.random.default_rng(8064)
outer_experiments = 120
inner_repeats = 400
coverage_n = 30
coverage_records = []
for experiment in range(outer_experiments):
    observed = 10 + coverage_rng.exponential(scale=20, size=coverage_n)
    repeated_means = []
    for _ in range(inner_repeats):
        repeated = coverage_rng.choice(observed, size=coverage_n, replace=True)
        repeated_means.append(repeated.mean())
    low, high = np.quantile(repeated_means, [0.025, 0.975])
    coverage_records.append([experiment + 1, observed.mean(), low, high, low <= mu_true <= high])
boot_intervals = pd.DataFrame(coverage_records, columns=["experiment", "estimate", "low", "high", "covered"])

fig, ax = plt.subplots(figsize=(10, 6))
for row in boot_intervals.head(40).itertuples():
    color = "#14804a" if row.covered else "#c44555"
    ax.hlines(row.experiment, row.low, row.high, color=color)
    ax.scatter(row.estimate, row.experiment, color=color, s=15)
ax.axvline(mu_true, color="#b67a10", ls="--")
ax.set(xlabel="Среднее время, мин", ylabel="Исследование", title="Бутстрап-интервалы: первые 40 исследований")
plt.show()
print(f"Частота покрытия по {outer_experiments} исследованиям: {boot_intervals['covered'].mean():.1%}")
''')

md(r"""
### 6.5. После ручного цикла — библиотечная функция

В `scipy.stats.bootstrap` передаём данные, функцию статистики и число повторений.
`(delivery_times,)` — кортеж с одной выборкой. Явно выбираем `method="percentile"`, чтобы повторить
изученный алгоритм: значение по умолчанию у SciPy — другой метод, BCa, с которым познакомимся обзорно ниже.
Числа могут немного отличаться от нашего цикла из-за других случайных повторных выборок.
""")
code('''result = bootstrap(
    (delivery_times,), np.mean,
    n_resamples=2000, confidence_level=0.95, method="percentile",
    random_state=np.random.default_rng(865),
)
print("Стандартная ошибка:", result.standard_error)
print("Границы интервала:", result.confidence_interval.low, result.confidence_interval.high)
''')

md(r"""
## 7. Какие бывают бутстрапы и зачем нужны варианты?

Здесь важно различить два выбора: **как получать повторные выборки** и **как по ним строить интервал**.
Ниже — карта методов для ориентировки. Для основной практики достаточно обычного бутстрапа
независимых наблюдений и интервала по квантилям. Дополнительные интерактивы можно оставить на семинар.
""")
theory("Откуда берутся повторные данные", r"""
<div class="d8-table"><table>
<tr><th>Вариант</th><th>Что делаем</th><th>Когда и зачем</th></tr>
<tr><td><b>Непараметрический</b><br>nonparametric</td><td>Выбираем наблюдённые записи с возвращением.</td><td>Оцениваем неопределённость без задания конкретного семейства распределений. Для обычного отбора строк предполагаем их независимость.</td></tr>
<tr><td><b>Параметрический</b><br>parametric</td><td>Выбираем семейство распределений, оцениваем его параметры по данным и генерируем новые выборки из подобранной модели.</td><td>Когда модель распределения обоснована. Результат зависит от правильности этой модели.</td></tr>
</table></div>
<p>Например, среднее и SD можно оценить по выборке и генерировать нормальные данные с этими параметрами.
Так мы добавляем предположение о форме распределения. Большое число повторений не проверяет это предположение.</p>
""" + box("Непараметрический не означает «без условий»", "<p>Мы не задаём конкретную форму распределения ГС, "
    "но по-прежнему учитываем отбор данных, зависимость, размер выборки и свойства вычисляемой статистики.</p>", "warn"))
widget("model", "Выбирать наблюдения или генерировать из модели?",
       "Переключите способ генерации. Сравните отдельные значения на верхних графиках и средние внизу. Найдите проблему нормальной модели для этих доставок.",
       ["observed", "generated", "statistics"],
       select("kind", "Источник повторных выборок", [("empirical","Наблюдаемые записи"),("normal","Подобранная нормальная модель")])
       + button("new", "Новые исходные данные"),
       "Почему гладкий вид гистограммы сам по себе не подтверждает правильность модели?",
       optional=True)
theory("Что пересэмплировать целиком", r"""
<p><b>Пересэмплирование (resampling)</b> — повторный случайный отбор данных по заданной схеме.
Единицу отбора определяет устройство исследования.</p>
<div class="d8-table"><table>
<tr><th>Схема</th><th>Единица повторного отбора</th><th>Пример и причина</th></tr>
<tr><td><b>Парный</b><br>paired</td><td>Пара измерений одного объекта.</td><td>«До» и «после» для одного пациента выбираем вместе; независимо перемешивать два столбца нельзя.</td></tr>
<tr><td><b>Кластерный</b><br>cluster</td><td>Целая группа связанных наблюдений. Такая группа называется кластером.</td><td>Выбираем дни вместе со всеми их поездками, если дни можно считать независимыми. Сохраняем связь внутри дня.</td></tr>
<tr><td><b>Блочный</b><br>block</td><td>Последовательный отрезок временного ряда — блок.</td><td>При связи соседних измерений сохраняем их локальный порядок. Длина блока влияет на результат.</td></tr>
</table></div>
<p>Эти схемы описывают, какие связи сохранить. Например, кластерный бутстрап можно делать
непараметрически: выбирать с возвращением наблюдённые кластеры.</p>
<details><summary>Дополнительно: стратифицированный бутстрап</summary>
<p><b>Страта (stratum)</b> — заранее выделенная подгруппа, например район города в плане обследования.
При стратифицированном бутстрапе повторный отбор проводят отдельно внутри страт, сохраняя предусмотренную
планом структуру выборки. При расчёте итогов могут понадобиться веса. Это другая причина группировки,
чем зависимость наблюдений внутри кластера.</p></details>
<p>Документация: <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html">SciPy — парный отбор</a>;
<a href="https://stat.ethz.ch/R-manual/R-devel/library/boot/html/boot.html">R boot — схемы генерации и страты</a>;
<a href="https://bashtage.github.io/arch/bootstrap/timeseries-bootstraps.html">arch — блочный бутстрап временных рядов</a>.</p>
""")
widget("clusters", "Почему поездки одного дня нельзя всегда перемешивать по одной",
       "Посмотрите на группы на верхнем графике. Увеличьте общий сдвиг внутри дня. Сравните ширину двух распределений средних; их горизонтальные шкалы одинаковы.",
       ["groups", "rows", "whole"],
       select("groups", "Независимых дней", [(12,"12"),(6,"6"),(30,"30")])
       + slider("tau", "SD общего сдвига дня", 0, 10, .5, 5)
       + button("new", "Новые данные"),
       "Что теряется при отборе отдельных строк? Почему тысячи повторений не заменяют большое число независимых дней?",
       optional=True)

theory("Как получить границы из бутстрап-распределения", r"""
<div class="d8-table"><table>
<tr><th>Метод интервала</th><th>Идея</th></tr>
<tr><td><b>Percentile</b> — квантильный</td><td>Берём соответствующие квантили бутстрап-оценок. Этот способ уже реализовали вручную.</td></tr>
<tr><td><b>Basic</b> — базовый, обратный процентильный</td><td>Отражаем границы квантильного интервала относительно исходной оценки. Так переносим оценённые ошибки на неизвестный параметр.</td></tr>
<tr><td><b>BCa</b> — bias-corrected and accelerated</td><td>Используем скорректированные уровни квантилей с учётом оценки смещения и изменения разброса статистики. Это более сложная процедура; здесь достаточно знать её назначение.</td></tr>
</table></div>
<p><b>Смещение оценки (bias)</b> — разность между средним значением оценки по повторным исследованиям
и истинным параметром. Это свойство процедуры, а не ошибка одного наблюдения.</p>
""" + box("Схема выборок и метод интервала — разные настройки", "<p>Например, обычный непараметрический "
    "бутстрап может использовать интервалы percentile, basic или BCa. BCa не означает иной способ "
    "выбирать строки. Ни один вариант автоматически не исправляет неподходящие данные или нарушенные условия.</p>")
    + r"""<details><summary>Дополнительно: формула basic-интервала</summary>"""
    + eq(r"I_{\mathrm{basic}}=[2\widehat\theta-q^*_{0.975},\ 2\widehat\theta-q^*_{0.025}].",
         r"$I_{\mathrm{basic}}$ — базовый приближённый 95%-й интервал; $\widehat\theta$ — исходная оценка "
         r"параметра (например, среднее выборки); $q^*_{0.025}$ и $q^*_{0.975}$ — квантили бутстрап-оценок; "
         r"звёздочка обозначает бутстрап. Меньшая граница получается из верхней квантили.")
    + '</details><p>Источник: <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html">SciPy — методы percentile, basic и BCa</a>.</p>')

code('''#@title Дополнительно — сравниваем методы интервала на одних данных { display-mode: "form" }
method_rows = []
for method in ["percentile", "basic", "BCa"]:
    result = bootstrap((delivery_times,), np.mean, n_resamples=2000,
                       method=method, confidence_level=0.95,
                       random_state=np.random.default_rng(877))
    method_rows.append([method, result.confidence_interval.low, result.confidence_interval.high])
method_intervals = pd.DataFrame(method_rows, columns=["method", "low", "high"])
fig, ax = plt.subplots(figsize=(10, 3))
for index, row in enumerate(method_intervals.itertuples()):
    ax.hlines(index, row.low, row.high, color="#14804a", lw=4)
    ax.scatter(delivery_times.mean(), index, color="#14804a", s=45)
ax.axvline(mu_true, color="#b67a10", ls="--", label="Истина — для проверки")
ax.set(yticks=range(3), yticklabels=method_intervals["method"], xlabel="Среднее время, мин",
       title="Одни данные и повторные выборки, разные правила границ")
ax.legend()
plt.show()
display(method_intervals)
''')
md("**Обсудите:** можно ли выбрать лучший метод только по тому, какой из этих трёх интервалов оказался короче? Какая симуляция нужна для проверки надёжности?")

md(r"""
## 8. Практика и проверка понимания

**Задача A. Что изменилось?** Зафиксируйте выборку в интерактиве 6.3. Увеличьте B с 200 до 5000,
затем отдельно увеличьте n. Объясните различие действий и приложите два наблюдения с графиков.

**Задача B. Медиана доставок.** Для `task_delivery` из раздела 5 постройте бутстрап-распределение медианы
и процентильный 95%-й интервал. Сначала реализуйте цикл самостоятельно, затем проверьте через библиотеку.
Формулу SE среднего к медиане не применяйте. Интерпретируйте, какой параметр оцениваете.

**Задача C. Проверка обещания 95%.** В коде 6.4 сравните размеры исходной выборки 10 и 100.
Запишите частоты покрытия. Объясните, почему из одной конечной серии нельзя требовать точного совпадения с 95%.

**Задача D. Перенос на автобусы — словами.** В поездках одного дня есть общий фактор пробок.
Предложите единицу повторного отбора и назовите условие, при котором такая схема разумна.
Отдельно рассмотрите случай, когда соседние дни тоже связаны. Данных для расчёта здесь нет: используйте
синтетический пример из раздела 7 и знания о сборе автобусного практикума.
""")
code('''# TODO: Bootstrap the median of task_delivery and draw its distribution and interval.
# TODO: Compare the custom loop with scipy.stats.bootstrap using the same statistic.
''')
md("**Ваши выводы по A–D:** …")
theory("Короткие формулировки для устного ответа", r"""
<div class="d8-table"><table>
<tr><th>Понятие</th><th>Что нужно уметь сказать</th></tr>
<tr><td>Доверительный интервал</td><td>Интервал по выборке, построенный процедурой с заданной вероятностью покрытия неизвестного параметра.</td></tr>
<tr><td>Уровень доверия 95%</td><td>При повторении исследования процедура накрывает истинный параметр примерно в 95% случаев, если выполнены её условия.</td></tr>
<tr><td>Бутстрап</td><td>Приближение выборочного распределения статистики повторными выборками на основе наблюдаемых данных.</td></tr>
<tr><td>Обычный непараметрический бутстрап</td><td>Отбор исходных наблюдений с возвращением, с сохранением размера выборки, и пересчёт статистики.</td></tr>
<tr><td>Бутстрап-SE</td><td>Стандартное отклонение полученных бутстрап-оценок.</td></tr>
<tr><td>Percentile-интервал</td><td>Интервал между соответствующими квантилями бутстрап-оценок; его покрытие приближённое.</td></tr>
</table></div>
""" + box("Один вывод о точности", "<p>Сообщайте оценку, интервал, способ его построения и основные "
    "условия. По одному среднему или одной ширине интервала надёжность исследования не определяется.</p>"))

md(r"""
## 9. Подводка: что делать с утверждением «среднее равно 30»?

Служба доставки утверждает: истинное среднее равно 30 минутам.
**Статистическая гипотеза** — предположение о распределении или его параметрах, которое проверяют по данным.
Здесь гипотеза относится к среднему ГС.

На графике уже можно отметить 30 и увидеть его положение относительно интервала.
Попадание 30 внутрь интервала не доказывает точного равенства. Промах требует оценивать результат с учётом
модели и надёжности процедуры: случайные промахи встречаются даже при верных условиях.

Дальше нам нужен способ ответить: **насколько необычен наблюдаемый результат, если проверяемое предположение верно?**
На следующем занятии введём p-value, правила проверки гипотез и статистическую значимость.
В этом колабе такие решения не принимаем.
""")
theory("Бутстрап и проверяемое предположение", box("Что важно сохранить к следующему занятию",
    "<p>Обычный бутстрап среднего даёт распределение около наблюдаемого среднего. Если оно равно 33, "
    "центр бутстрап-распределения тоже будет около 33. Это само по себе не моделирует предположение "
    "«истинное среднее равно 30». Для проверки гипотез потребуется отдельно учесть проверяемое предположение.</p>", "idea"))

md(r"""
**Источники и документация**

- [NIST: смысл доверительного интервала и формула при известном SD ГС](https://www.itl.nist.gov/div898/handbook/prc/section1/prc14.htm).
- [NIST: интерпретация покрытия при повторном сборе данных](https://itl.nist.gov/div898/handbook/eda/section3/eda352.htm).
- [Hesterberg: как преподавать бутстрап, возможности и ограничения](https://arxiv.org/html/1411.5279).
- [SciPy: bootstrap, парные выборки, SE и методы интервалов](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html).
- [NumPy: случайный отбор с возвращением, Generator.choice](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.choice.html).
- [Seaborn: гистограммы, histplot](https://seaborn.pydata.org/generated/seaborn.histplot.html).
- [R boot: параметрическая генерация, страты и другие схемы](https://stat.ethz.ch/R-manual/R-devel/library/boot/html/boot.html).
- [arch: блочный бутстрап временных рядов](https://bashtage.github.io/arch/bootstrap/timeseries-bootstraps.html).

Все вычисления работают на синтетике без загрузки датасетов. Числа в интерактивах и Python могут различаться:
они используют разные случайные выборки. Для старых версий SciPy в примерах использован совместимый
аргумент `random_state`; в новых версиях его заменяет `rng`.
В локальном Jupyter может потребоваться доверить ноутбук через меню Trust Notebook.
""")

nb = nbf.v4.new_notebook(cells=cells, metadata=json.loads(json.dumps(META)))
nb.metadata["colab"]["name"] = "08_stat_ci_bootstrap.ipynb"
for index, cell in enumerate(nb.cells):
    cell.id = hashlib.sha256(f"lesson8-{index}-{cell.source}".encode()).hexdigest()[:12]
nbf.validate(nb)
output = HERE / "08_stat_ci_bootstrap.ipynb"
nbf.write(nb, output)
print(f"Wrote {output.name}: {len(cells)} cells; {len(WIDGET_JS)} characters of embedded widget code")
