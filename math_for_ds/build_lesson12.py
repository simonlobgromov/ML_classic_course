"""Build the standalone linear systems and inverse lesson with HTML theory and JS/SVG visuals."""
from pathlib import Path
import hashlib
import json
import nbformat as nbf
from theme import SETUP, META

HERE = Path(__file__).resolve().parent
WIDGET_JS = (HERE / "lesson12_widgets.js").read_text(encoding="utf-8")
cells = []


def md(source, tags=()):
    cells.append(nbf.v4.new_markdown_cell(source.strip(), metadata={"tags": list(tags)}))


def code(source, tags=("provided", "example")):
    cells.append(nbf.v4.new_code_cell(source.strip(), metadata={"tags": list(tags)}))


def eq(formula, meanings):
    """Require a glossary for every displayed equation."""
    if not meanings:
        raise ValueError("An equation needs a glossary")
    return ("<div class='d12-equation'>$$" + formula + "$$</div>"
            + "<div class='where'><b>Обозначения.</b> " + meanings + "</div>")


def box(title, body, kind="idea"):
    return f'<div class="box {kind}"><div class="t">{title}</div>{body}</div>'


def definition(title, body):
    return box(title, body, "def")


def theory(title, body):
    code(f'#@title {title} {{ display-mode: "form" }}\n'
         + 'display(HTML(lesson12_viz(' + repr(body) + ')))', ("provided", "theory"))


def widget(kind, title, instruction, question, data="None"):
    body = (f'<div class="widget"><div class="widget-title">{title}</div>'
            + f'<p class="widget-sub">{instruction}</p><div data-stage></div>'
            + '<div class="readout" data-readout role="status" aria-live="polite"></div>'
            + f'<p class="d12-question"><b>Проверь себя.</b> {question}</p>'
            + '<p class="d12-footnote">Интерактивная иллюстрация. Изменения здесь не меняют переменные в Python.</p></div>')
    code(f'#@title Интерактив — {title} {{ display-mode: "form" }}\n'
         + 'display(HTML(lesson12_viz(' + repr(body) + ', widget=' + repr(kind)
         + ', data=' + data + ')))', ("provided", "interactive"))


md(r"""
# Можно ли восстановить вход по результату?
## Занятие 12 — системы уравнений и обратимость

Мы уже умеем вычислять результат умножения матрицы на вектор. Теперь поставим обратную задачу:
**результат известен, а вход нужно найти**.

Научимся записывать системы линейных уравнений в матричном виде, разберёмся, когда решение существует
и когда оно единственное. Увидим, что делает обратная матрица и как определитель связан с площадью и обратимостью.

Основной материал рассчитан на одну встречу. В конце — четыре задачи для закрепления и две дополнительные:
матричные уравнения, СЛУ и применение готовой формулы для весов линейной регрессии.
Часть практики можно выполнить самостоятельно после занятия.

Запускайте ячейки по порядку. Теория и интерактивы находятся в свёрнутых HTML-ячейках, примеры NumPy открыты.
Все данные встроены; скачивания датасетов нет. Для отображения формул нужен интернет (MathJax).
""")

EXTRA_SETUP = r'''
import json
import uuid
import re
from html import escape

D12_CSS = r"""
.vec-root .d12-controls{display:flex;flex-wrap:wrap;gap:12px 24px;margin:16px 0 22px;font-family:system-ui,sans-serif;}
.vec-root .d12-control{display:flex;align-items:center;flex-wrap:wrap;gap:8px;color:var(--ink);font-size:14px;min-height:36px;}
.vec-root .d12-control input[type=range]{width:155px;min-height:30px;}
.vec-root .d12-control output{font-variant-numeric:tabular-nums;color:var(--green);min-width:42px;}
.vec-root .d12-control select{max-width:100%;padding:8px;}
.vec-root .d12-control input:disabled{opacity:.3;}
.vec-root .d12-charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,380px),1fr));gap:16px;}
.vec-root .d12-charts svg{display:block;width:100%;height:auto;background:#0e1319;border-radius:10px;}
.vec-root .d12-charts svg:last-child:nth-child(3){grid-column:1/-1;max-width:780px;justify-self:center;}
.vec-root .readout{overflow-wrap:anywhere;font:15px/1.75 system-ui,sans-serif;}
.vec-root .d12-question{font-family:system-ui,sans-serif;font-size:14px;color:var(--ink);}
.vec-root .d12-footnote{font-family:system-ui,sans-serif;font-size:12px;color:var(--soft);}
.vec-root .d12-equation{overflow-x:auto;overflow-y:hidden;padding:5px 0;}
.vec-root .where{line-height:1.7;}
.vec-root .d12-table{overflow-x:auto;}
.vec-root button:disabled{opacity:.45;cursor:wait;}
.vec-root .d12-controls .btn{min-height:38px;}
.vec-root input:focus-visible,.vec-root select:focus-visible,.vec-root button:focus-visible{outline:2px solid #e0b25a;outline-offset:4px;}
@media(max-width:600px){.vec-root .wrap{padding:14px;font-size:16px;}.vec-root .widget{padding:10px;}.vec-root .d12-control{width:100%;}}
"""

def lesson12_viz(body, widget=None, data=None):
    """Scope controls to a fresh root so rerunning cells keeps widgets independent."""
    # HTML is parsed before MathJax. Protect comparisons and ampersands in both
    # display equations and inline symbol glossaries without escaping HTML tags.
    body = re.sub(
        r"(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$.*?(?<!\\)\$",
        lambda match: escape(match.group(0), quote=False),
        body,
        flags=re.DOTALL,
    )
    root_id = "d12_" + uuid.uuid4().hex
    script = D12_WIDGET_JS + "\n" + r"""
    (function(){
      const root = document.getElementById(__ROOT__);
      const widget = __WIDGET__;
      if (widget) window.SystemsLesson12.mount(root, widget, __DATA__);
      const typeset = () => window.MathJax.typesetPromise([root]);
      if (!window.__D12_MATH_READY__) {
        if (window.MathJax && window.MathJax.typesetPromise) {
          window.__D12_MATH_READY__ = window.MathJax.startup.promise;
        } else {
          window.MathJax = {tex:{inlineMath:[['$','$']],displayMath:[['$$','$$']]},svg:{fontCache:'local'},startup:{typeset:false}};
          window.__D12_MATH_READY__ = new Promise((resolve, reject) => {
            const loader = document.createElement('script');
            loader.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
            loader.onload = () => window.MathJax.startup.promise.then(resolve, reject);
            loader.onerror = reject;
            document.head.appendChild(loader);
          });
        }
      }
      window.__D12_MATH_READY__ = window.__D12_MATH_READY__.then(typeset).catch(() => {
        if(root.querySelector('.d12-equation')) {
          const notice = document.createElement('p');
          notice.textContent = 'Для отображения формул подключитесь к интернету и перезапустите ячейку. Графики работают без загрузки MathJax.';
          root.appendChild(notice);
        }
      });
    })();
    """.replace("__ROOT__", json.dumps(root_id)).replace("__WIDGET__", json.dumps(widget)).replace("__DATA__", json.dumps(data, ensure_ascii=False))
    return ("<style>" + CSS + D12_CSS + "</style>"
            + '<div class="vec-root" data-widget="' + (widget or "theory") + '" id="' + root_id + '"><div class="wrap wide">'
            + body + '</div></div><script>' + script + '</script>')

print("Занятие 12 готово: графики работают в браузере; формулы загружаются через MathJax.")'''

code(SETUP + "\n\nD12_WIDGET_JS = " + repr(WIDGET_JS) + "\n" + EXTRA_SETUP + "\nimport numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt", ("provided", "setup"))

md("## 1. Известен результат — найдём неизвестные")
theory("Две покупки, две неизвестные цены",
    "<p>В учебном примере два чая и один пирог стоят 350 сомов, а один чай и два пирога — 400 сомов. "
    "Цены одинаковы в обеих покупках. Нужно найти цену чая и цену пирога.</p>"
    + eq(r"\begin{cases}2x_1+x_2=350,\\x_1+2x_2=400.\end{cases}",
         r"$x_1$ — цена чая, $x_2$ — цена пирога, в сомах. Числа перед неизвестными — количество товаров; "
         "350 и 400 — известные суммы покупок.")
    + "<p>Одна покупка даёт одно условие. Искомая пара цен должна удовлетворять <b>обоим условиям одновременно</b>.</p>")

theory("Что такое система линейных уравнений",
    definition("Линейное уравнение · linear equation",
        "<p><b>Линейное уравнение</b> относительно неизвестных — уравнение вида:</p>"
        + eq(r"a_1x_1+\cdots+a_nx_n=b.",
             r"$x_1,\ldots,x_n$ — неизвестные; $a_1,\ldots,a_n$ — известные коэффициенты; "
             r"$b$ — известная правая часть; $n$ — число неизвестных.")
        + "<p>Неизвестные умножаются только на известные числа. Произведения неизвестных между собой "
          "и их квадраты в эту форму не входят.</p>")
    + definition("Система линейных уравнений · system of linear equations",
        "<p><b>Система линейных уравнений (СЛУ)</b> — несколько линейных уравнений относительно одних и тех же неизвестных. "
        "<b>Решение системы</b> — набор значений неизвестных, при котором верны все её уравнения.</p>"))

theory("Запись той же задачи через матрицу",
    eq(r"A=\begin{pmatrix}2&1\\1&2\end{pmatrix},\qquad x=\begin{pmatrix}x_1\\x_2\end{pmatrix},\qquad b=\begin{pmatrix}350\\400\end{pmatrix},\qquad Ax=b.",
       r"$A$ — матрица коэффициентов: одна строка на уравнение; $x$ — столбец неизвестных цен; "
       r"$b$ — столбец правых частей. Порядок неизвестных в обеих строках один и тот же.")
    + "<p>Умножение первой строки на вектор даёт стоимость первой покупки, второй строки — второй покупки.</p>"
    + box("Размеры", r"В общем случае у системы $m$ уравнений и $n$ неизвестных: "
          r"матрица $A$ имеет размер $m\times n$, вектор $x$ — $n$ координат, вектор $b$ — $m$ координат. "
          "Число уравнений не обязано совпадать с числом неизвестных."))

code('''A = np.array([[2.0, 1.0], [1.0, 2.0]])
b = np.array([350.0, 400.0])
# Check a guess; this is not yet a method for finding the solution.
x_guess = np.array([100.0, 100.0])
print("Проверяем цены:", x_guess)
print("Получились суммы покупок:", A @ x_guess)
print("Нужны суммы:", b)
print("Все условия выполнены:", np.allclose(A @ x_guess, b))''')

md("## 2. Сколько решений бывает у системы?")
theory("Один вход, много входов или ни одного",
    "<p>Для двух неизвестных каждое линейное уравнение, в котором хотя бы один коэффициент при неизвестных ненулевой, задаёт прямую. "
    "Точки на этой прямой — пары чисел, удовлетворяющие уравнению. "
    "Решение системы должно лежать на обеих прямых.</p>"
    "<ul><li><b>Прямые пересекаются в одной точке:</b> единственное решение.</li>"
    "<li><b>Прямые совпадают:</b> бесконечно много решений.</li>"
    "<li><b>Прямые параллельны и различны:</b> решений нет.</li></ul>"
    + box("Для линейной системы над вещественными числами",
        "Возможны ровно три случая: нет решений, одно решение или бесконечно много решений. "
        "Ровно два или ровно три решения у такой системы быть не может."))

theory("Взгляд через столбцы матрицы",
    "<p>Вспомним L11: результат умножения — линейная комбинация столбцов.</p>"
    + eq(r"Ax=x_1c_1+x_2c_2=b.",
         r"$c_1,c_2$ — два столбца матрицы $A$; $x_1,x_2$ — искомые коэффициенты комбинации; "
         r"$b$ — результат, который нужно получить.")
    + "<p>Если комбинациями столбцов нельзя получить нужный вектор, система не имеет решения. "
      "Если получить его можно разными наборами коэффициентов, решений несколько — а для СЛУ тогда бесконечно много.</p>"
    + box("Два графика — два разных вопроса",
        "Слева в интерактиве ищем <b>неизвестный вход</b> на пересечении прямых. "
        "Справа смотрим, доступен ли <b>заданный выход</b> как комбинация столбцов. Координаты точек на этих графиках имеют разный смысл."))

widget("systems", "Одна матрица — разные правые части",
       "Выберите случай с одним решением, бесконечным числом решений или без решений. "
       "Ползунок b₂ меняет правую часть только второго уравнения. В первом она остаётся равной 3. "
       "Для графиков используются небольшие числа; это отдельный пример после задачи с покупками.",
       "Сравните два случая с зависимыми строками. Почему при одной и той же матрице A ответ зависит от правой части b? "
       "При каком b₂ две прямые совпадут?")

md("## 3. Обратная матрица отменяет преобразование")
theory("Определение обратной матрицы",
    "<p>Если поворот переместил точку, обратный поворот вернёт её на место. "
    "Если координату умножили на 2, обратное действие делит её на 2.</p>"
    + "<p><b>Единичная матрица</b> имеет единицы на главной диагонали и нули на остальных местах. "
      "Умножение на неё не меняет вектор.</p>"
    + definition("Обратная матрица · inverse matrix",
        "<p><b>Обратной к квадратной матрице A</b> называется матрица того же размера, "
        "произведение которой с A в любом из двух порядков равно единичной матрице.</p>"
        + eq(r"AA^{-1}=A^{-1}A=I.",
             r"$A$ — исходная квадратная матрица; $A^{-1}$ — обратная к ней; $I$ — единичная матрица того же размера. "
             "Соседство матриц означает матричное умножение."))
    + box("Что означает степень −1",
        r"$A^{-1}$ — обозначение обратной матрицы. Это <b>не</b> замена каждого элемента на обратное число. "
        "В NumPy <code>1 / A</code> делит 1 на отдельные элементы, а <code>np.linalg.inv(A)</code> вычисляет обратную матрицу."))

theory("Вырожденная означает необратимая",
    definition("Обратимая и необратимая матрицы",
        "<p>Квадратная матрица <b>обратима</b>, если для неё существует обратная. "
        "Если обратной нет, матрица <b>необратима</b>.</p>")
    + "<p>Из L11: квадратная матрица вырождена, если её ранг меньше числа строк. "
      "Для квадратных матриц <b>«вырожденная» и «необратимая» означают одно и то же</b>.</p>"
    + eq(r"A\in\mathbb R^{n\times n}:\qquad A^{-1}\text{ существует}\ \Longleftrightarrow\ \operatorname{rank}(A)=n.",
         r"$A$ — квадратная матрица порядка $n$; $\mathbb R$ — вещественные числа; "
         r"$\operatorname{rank}(A)$ — ранг; $\Longleftrightarrow$ означает «тогда и только тогда».")
    + box("Почему нельзя отменить схлопывание",
        "Если разные входы превратились в один выход, по этому выходу нельзя однозначно выбрать исходный вход. "
        "Поэтому преобразование, которое сжало всю плоскость в прямую, не имеет обратного действия для всей плоскости."))

widget("inverse", "Применить преобразование и вернуться",
       "Выберите матрицу. Ползунки x₁ и x₂ задают координаты одной выделенной точки. "
       "Сравните исходную фигуру, результат умножения на A и результат обратного преобразования.",
       "Что изменится при выборе вырожденной матрицы? Почему нельзя просто нарисовать единственную восстановленную фигуру?")

code('''A_inv = np.linalg.inv(A)
I = np.eye(A.shape[0])
print("Обратная матрица:\\n", A_inv)
print("A @ A_inv:\\n", np.round(A @ A_inv, 10))
print("Оба порядка дают единичную:",
      np.allclose(A @ A_inv, I) and np.allclose(A_inv @ A, I))''')

theory("Как читать проверку в NumPy",
    "<p><code>np.eye(n)</code> создаёт единичную матрицу размера n × n. "
    "<code>np.allclose</code> сравнивает числа с допуском на округление. "
    "<code>np.round</code> здесь нужен только для удобного вывода: сами расчёты не округляем.</p>"
    + box("Обратной может не быть, а решение — быть",
        "Необратимость не означает автоматически отсутствие решений СЛУ. "
        "Для квадратной вырожденной матрицы возможны отсутствие решений или бесконечно много решений — "
        "это зависит от правой части."))

md("## 4. Определитель: число и геометрический смысл")
theory("Определитель матрицы 2 × 2",
    definition("Определитель второго порядка · determinant",
        "<p><b>Определителем матрицы второго порядка</b> называется число, вычисляемое по формуле:</p>"
        + eq(r"A=\begin{pmatrix}a&b\\c&d\end{pmatrix},\qquad\det(A)=ad-bc.",
             r"$a,b,c,d$ — четыре элемента этой матрицы; $\det(A)$ — её определитель. "
             r"Здесь буква $b$ обозначает элемент матрицы, а не правую часть СЛУ."))
    + "<p>Перемножаем элементы главной диагонали и вычитаем произведение элементов другой диагонали. "
      "Результат — одно число.</p>"
    + eq(r"\det\begin{pmatrix}2&1\\1&2\end{pmatrix}=2\cdot2-1\cdot1=3.",
         "Вычисляется определитель матрицы коэффициентов задачи с покупками; 2 и 1 — её элементы.")
    + "<p>Определитель определён для квадратных матриц любого порядка. "
      "Вручную здесь вычисляем только случай 2 × 2; для больших матриц используем NumPy.</p>")

code('''det_manual = A[0, 0] * A[1, 1] - A[0, 1] * A[1, 0]
print("По формуле для 2 × 2:", det_manual)
print("Через NumPy:", np.linalg.det(A))''')

theory("Во сколько раз изменилась площадь",
    "<p>Преобразуем матрицей единичный квадрат — квадрат со сторонами длины 1 и площадью 1. "
    "Его стороны превратятся в столбцы матрицы, а сам квадрат — в параллелограмм, отрезок или точку.</p>"
    + eq(r"S_{\text{после}}=|\det(A)|\,S_{\text{до}}.",
         r"$A$ — матрица преобразования плоскости; $S_{\text{до}}$ и $S_{\text{после}}$ — площади фигуры до и после; "
         r"$|\det(A)|$ — модуль определителя, то есть определитель без знака.")
    + "<p><b>Ориентация фигуры</b> здесь — направление обхода её отмеченных вершин: по часовой стрелке или против неё. "
      "При положительном определителе направление обхода сохраняется, при отрицательном — меняется.</p>"
    + box("Три случая",
        "<ul><li>Определитель 2: площадь увеличилась в 2 раза, ориентация сохранена.</li>"
        "<li>Определитель −2: площадь тоже увеличилась в 2 раза, ориентация изменилась.</li>"
        "<li>Определитель 0: площадь стала нулевой; плоскость схлопнулась в прямую или точку.</li></ul>")
    + "<p>Для преобразования трёхмерного пространства модуль определителя аналогично задаёт коэффициент изменения объёма.</p>")

widget("determinant", "Площадь, знак и обратимость",
       "Ползунок s меняет первую координату второго столбца: наклоняет параллелограмм. "
       "Ползунок t меняет вторую координату этого столбца: высоту со знаком. "
       "Проследите за площадью и порядком вершин при t = 1, t = −1 и t = 0.",
       "Почему изменение s при неизменном t не меняет площадь? "
       "Существует ли обратная матрица при отрицательном определителе?")

theory("Связь с обратной матрицей",
    eq(r"A\in\mathbb R^{n\times n}:\quad\det(A)\ne0\ \Longleftrightarrow\ A^{-1}\text{ существует}\ \Longleftrightarrow\ \operatorname{rank}(A)=n.",
         r"$A$ — вещественная квадратная матрица порядка $n$; $\det(A)$ — определитель; "
         r"$A^{-1}$ — обратная матрица; $\operatorname{rank}(A)$ — ранг; $\Longleftrightarrow$ связывает равносильные условия.")
    + box("Для обратимости важен ноль, а не знак",
        "И положительный, и отрицательный ненулевой определитель допускают обратную матрицу. "
        "Нулевой определитель означает, что обратной нет.")
    + "<details><summary>Как не перепутать математическое равенство и вычисления</summary>"
      "<p>Вычисления с дробными числами дают небольшие ошибки округления. "
      "Поэтому очень маленькое число, выведенное вместо нуля, нужно интерпретировать с учётом точности. "
      "При этом малая величина определителя сама по себе не является универсальной оценкой устойчивости: "
      "она зависит и от масштаба элементов матрицы.</p></details>")

theory("Как найти обратную для 2 × 2",
    eq(r"A=\begin{pmatrix}a&b\\c&d\end{pmatrix},\qquad A^{-1}=\frac{1}{ad-bc}\begin{pmatrix}d&-b\\-c&a\end{pmatrix},\qquad ad-bc\ne0.",
         r"$a,b,c,d$ — элементы матрицы $A$; $ad-bc=\det(A)$ — её определитель; "
         r"$A^{-1}$ — обратная матрица. Формула относится только к размеру $2\times2$.")
    + "<p>Меняем местами два элемента главной диагонали, меняем знаки двух остальных "
      "и делим полученную матрицу на определитель.</p>"
    + box("Почему здесь нужен определитель",
        "Он стоит в знаменателе. При нуле формула не определена, и обратной матрицы действительно нет. "
        "Это удобный ручной способ для 2 × 2. Библиотечные алгоритмы могут вычислять обратную иначе — "
        "заранее считать определитель для вызова <code>np.linalg.inv</code> не требуется."))

code('''a11, a12 = A[0]
a21, a22 = A[1]
A_inv_manual = np.array([[a22, -a12], [-a21, a11]]) / det_manual
print("Обратная по формуле:\\n", A_inv_manual)
print("Совпадает с NumPy:", np.allclose(A_inv_manual, A_inv))
print("Проверка произведением:", np.allclose(A @ A_inv_manual, np.eye(2)))''')

md("## 5. Решаем СЛУ через обратную матрицу")
theory("Почему решение равно A⁻¹b",
    "<p>Пусть матрица коэффициентов квадратная и обратимая. "
    "Умножим обе части уравнения на обратную матрицу <b>слева</b>:</p>"
    + eq(r"Ax=b\quad\Longrightarrow\quad A^{-1}(Ax)=A^{-1}b\quad\Longrightarrow\quad Ix=A^{-1}b\quad\Longrightarrow\quad x=A^{-1}b.",
         r"$A$ — известная обратимая матрица коэффициентов; $b$ — известная правая часть; $x$ — искомый вектор; "
         r"$A^{-1}$ — обратная матрица; $I$ — единичная. $\Longrightarrow$ означает переход к следующему равенству.")
    + box("Порядок умножения имеет значение",
        r"Слева появляются соседние множители $A^{-1}A$, их произведение равно $I$. "
        "Менять порядок матриц произвольно нельзя. Операции «разделить на матрицу» в этом решении нет.")
    + "<p>Для квадратной обратимой матрицы это <b>единственное решение при любой правой части</b>.</p>")

code('''x_via_inverse = A_inv @ b
print("Цена чая и цена пирога:", x_via_inverse)
print("Подстановка в исходные уравнения:", A @ x_via_inverse)
print("Получили нужные суммы:", np.allclose(A @ x_via_inverse, b))''')

theory("Как решают такую систему в NumPy",
    "<p><code>np.linalg.solve(A, b)</code> находит решение системы с квадратной невырожденной матрицей A. "
    "Функция решает систему напрямую; отдельно получать обратную матрицу не нужно.</p>"
    + box("Два способа в этом занятии",
        "<code>np.linalg.inv(A) @ b</code> показывает изученную формулу. "
        "<code>np.linalg.solve(A, b)</code> — обычный выбор для вычисления решения такой системы. "
        "В обоих случаях проверяем ответ подстановкой в исходное уравнение.")
    + "<p>Если матрица вырождена, <code>solve</code> не выбирает одно из бесконечных решений: "
      "функция может сообщить <code>LinAlgError</code>. По одной этой ошибке нельзя заключить, "
      "что решений нет: нужно рассмотреть саму систему.</p>")

code('''x_direct = np.linalg.solve(A, b)
print("Решение solve:", x_direct)
print("Два способа согласуются:", np.allclose(x_direct, x_via_inverse))

A_singular = np.array([[1.0, 1.0], [2.0, 2.0]])
b_consistent = np.array([3.0, 6.0])
try:
    np.linalg.solve(A_singular, b_consistent)
except np.linalg.LinAlgError:
    print("solve не нашёл единственное решение: матрица вырождена.")
print("Но пара [1, 2] подходит:", np.allclose(A_singular @ np.array([1, 2]), b_consistent))''')

code('''# Each line describes all prices satisfying one purchase equation.
tea_prices = np.linspace(0, 220, 200)
fig, ax = plt.subplots(figsize=(6, 5))
ax.plot(tea_prices, 350 - 2 * tea_prices, label="2 чая + 1 пирог = 350")
ax.plot(tea_prices, (400 - tea_prices) / 2, label="1 чай + 2 пирога = 400")
ax.scatter(*x_direct, color="crimson", s=70, zorder=3, label="Общее решение")
ax.set(xlim=(0, 220), ylim=(0, 260), xlabel="Цена чая, сом", ylabel="Цена пирога, сом",
       title="Одна пара цен удовлетворяет обеим покупкам")
ax.set_aspect("equal")
ax.grid(alpha=0.3)
ax.legend()
plt.tight_layout()
plt.show()''')

md("## 6. Матричные уравнения: неизвестна целая матрица")
theory("Несколько правых частей сразу",
    definition("Матричное уравнение · matrix equation",
        "<p><b>Матричное уравнение</b> — равенство матричных выражений, в котором нужно найти неизвестную матрицу. "
        "Решение должно делать равными все соответствующие элементы обеих частей.</p>")
    + "<p>Например, в двух кафе покупают те же наборы товаров, но цены и суммы чеков разные. "
      "Состав покупок описывает одна матрица A. Суммы чеков каждого кафе запишем в отдельный столбец матрицы B; столбцы решения X будут содержать цены каждого кафе.</p>"
    + eq(r"AX=B,\qquad X=A^{-1}B.",
         r"$A$ — известная обратимая матрица размера $n\times n$; $B$ — матрица правых частей размера $n\times k$; "
         r"$X$ — неизвестная матрица размера $n\times k$; каждый её столбец решает одну из $k$ систем.")
    + "<p><code>np.linalg.solve</code> принимает и матрицу правых частей: решение возвращается с тем же расположением столбцов.</p>")

code('''B_many = np.column_stack([b, np.array([500.0, 400.0])])
X_many = np.linalg.solve(A, B_many)
print("Два столбца правых частей:\\n", B_many)
print("Каждый столбец — отдельное решение:\\n", X_many)
print("Подстановка всех решений сразу:", np.allclose(A @ X_many, B_many))''')

theory("С какой стороны умножать на обратную",
    eq(r"AX=B\ \Longrightarrow\ X=A^{-1}B,\qquad XA=B\ \Longrightarrow\ X=BA^{-1}.",
         r"$X$ — неизвестная матрица; $A$ — известная квадратная обратимая матрица; "
         r"$B$ — известная матрица подходящего размера; $A^{-1}$ — обратная к $A$.")
    + "<p>В первом случае убираем A умножением слева. Во втором — справа. "
      "В каждом шаге одинаково умножаем <b>обе части</b> уравнения.</p>"
    + box("Как подойти к более длинному уравнению",
        "Сначала перенесите известные слагаемые и уберите числовой коэффициент. "
        "Затем убирайте обратимую матрицу слева или справа от неизвестной, сохраняя порядок множителей. "
        "В конце подставьте результат именно в исходное уравнение."))

md("## 7. Что нужно унести с занятия")
theory("Связь между понятиями",
    box("СЛУ", "Один вектор неизвестных должен удовлетворять всем уравнениям сразу. "
        "Запись Ax = b собирает эти условия в одно матричное равенство.", "take")
    + box("Обратимость", "Квадратная матрица обратима тогда и только тогда, когда она имеет полный ранг. "
          "В этом случае для любой правой части решение единственно.", "take")
    + box("Определитель", "Ноль означает вырожденность. На плоскости модуль определителя задаёт изменение площади, "
          "а знак — сохранение или изменение ориентации.", "take")
    + box("Проверка результата", "Вычисленный ответ подставляем в исходное уравнение. "
          "Результат должен совпасть с правой частью с учётом округления.", "take"))

md("""Объясните своими словами:

1. Почему у вырожденной квадратной матрицы нет обратной, но у системы с этой матрицей могут быть решения?
2. В интерактиве найдите две разные матрицы с одинаковым определителем. Что у них общее, а что может различаться?
3. Почему при решении матричного уравнения нельзя переставить обратную матрицу на другую сторону произведения?
""", ("interpretation",))

md("## 8. Практика")
md("""Четыре основные задачи: вычислить обратную, решить матричное уравнение и СЛУ, применить готовую формулу.
Две дополнительные задачи находятся в следующем разделе. Числа и условия перенесены из набора упражнений преподавателя;
для задания со случайными данными закреплён генератор, чтобы результаты можно было воспроизвести.
""")

theory("Задача 1. Определитель и обратная 2 × 2",
    "<p>Для матрицы ниже вычислите определитель по формуле второго порядка. "
    "Затем составьте обратную по изученной формуле, используя только элементы матрицы и арифметические операции.</p>"
    "<p>Сравните определитель с <code>np.linalg.det</code>, а обратную — с <code>np.linalg.inv</code>. "
    "Что означает знак определителя для преобразования плоскости?</p>")
code('''A_det_task = np.array([[2.0, 4.0], [3.0, 1.0]])
# TODO: Compute the determinant and inverse using the 2x2 formulas.
det_task = ...
inv_task = ...''', ("student-core", "task-1"))
code('''if det_task is Ellipsis or inv_task is Ellipsis:
    print("Сначала заполните задачу 1.")
else:
    print("Определитель по вашей формуле:", det_task)
    print("Определитель NumPy:", np.linalg.det(A_det_task))
    print("Обратная по вашей формуле:\\n", inv_task)
    print("Совпадает с NumPy:", np.allclose(inv_task, np.linalg.inv(A_det_task)))
    print("Произведение даёт единичную:", np.allclose(A_det_task @ inv_task, np.eye(2)))''', ("provided", "task-check"))
md("**Вывод об обратимости, площади и ориентации:** …", ("interpretation",))

theory("Задача 2. Найдите неизвестную матрицу",
    eq(r"2AX-B=C.",
         r"$A,B,C$ — известные матрицы размера $3\times3$ из ячейки ниже; $X$ — неизвестная матрица того же размера; "
         r"$A$ обратима. Число 2 умножает каждый элемент произведения $AX$.")
    + "<p>Сначала выразите X на бумаге, сохранив порядок множителей. Затем вычислите её через обратную матрицу. "
      "Проверка подстановкой уже подготовлена.</p>")
code('''A_eq_task = np.array([[-1, 7, -1], [8, 2, -3], [1, 5, 9]])
B_eq_task = np.array([[5, 2, -2], [-2, 9, -5], [7, -4, 2]])
C_eq_task = np.array([[35, 48, 62], [-8, -5, 23], [161, 202, 226]])
# TODO: Isolate the unknown matrix and compute it using an inverse.
X_eq_task = ...''', ("student-core", "task-2"))
code('''if X_eq_task is Ellipsis:
    print("Сначала заполните задачу 2.")
else:
    print("Полученная матрица:\\n", X_eq_task)
    print("Подстановка в 2AX − B = C:",
          np.allclose(2 * A_eq_task @ X_eq_task - B_eq_task, C_eq_task))''', ("provided", "task-check"))
md("**Какие действия вы выполнили с обеими частями уравнения и почему именно в таком порядке?** …", ("interpretation",))

theory("Задача 3. СЛУ с четырьмя неизвестными",
    eq(r"\begin{cases}2x_1+2x_2-x_3+x_4=4,\\4x_1+3x_2-x_3+2x_4=6,\\8x_1+5x_2-3x_3+4x_4=12,\\3x_1+3x_2-2x_3+2x_4=6.\end{cases}",
         r"$x_1,x_2,x_3,x_4$ — четыре неизвестных; числа перед ними — коэффициенты; "
         "4, 6, 12, 6 — правые части уравнений.")
    + "<p>Сверьте запись системы с матрицей и вектором ниже. Найдите решение способом обратной матрицы, "
      "затем проверьте его через <code>np.linalg.solve</code> и подстановку.</p>")
code('''A_system_task = np.array([[2, 2, -1, 1],
                          [4, 3, -1, 2],
                          [8, 5, -3, 4],
                          [3, 3, -2, 2]], dtype=float)
b_system_task = np.array([4, 6, 12, 6], dtype=float)
# TODO: Find the solution via an inverse and with solve.
x_inverse_task = ...
x_solve_task = ...''', ("student-core", "task-3"))
code('''if x_inverse_task is Ellipsis or x_solve_task is Ellipsis:
    print("Сначала заполните задачу 3.")
else:
    print("Через обратную:", x_inverse_task)
    print("Через solve:", x_solve_task)
    print("Решения совпадают:", np.allclose(x_inverse_task, x_solve_task))
    print("Все уравнения выполнены:", np.allclose(A_system_task @ x_inverse_task, b_system_task))''', ("provided", "task-check"))
md("**Почему можно ожидать единственное решение? Как это проверить через ранг или определитель?** …", ("interpretation",))

theory("Задача 4. Примените готовую формулу для весов",
    definition("Линейная регрессия · linear regression",
        "<p><b>Задача регрессии</b> — прогнозирование числового значения по признакам. "
        "В <b>линейной регрессии</b> прогноз записывают как линейную комбинацию признаков, "
        "обычно с добавлением свободного члена — постоянного слагаемого. "
        "В этой задаче используем вариант <b>без свободного члена</b>.</p>")
    + "<p>Даны матрица признаков и целевые значения. Нужно применить готовую формулу, которая подбирает веса "
      "с минимальной суммой квадратов расхождений между прогнозами и целевыми значениями.</p>"
    + eq(r"w=(X^{\mathsf T}X)^{-1}X^{\mathsf T}y,\qquad\widehat y=Xw.",
         r"$X$ — матрица из $n$ строк-наблюдений и $p$ столбцов-признаков; $X^{\mathsf T}$ — транспонированная матрица; "
         r"$y$ — вектор из $n$ целевых значений; $w$ — вектор из $p$ весов; "
         r"$\widehat y$ — вектор из $n$ прогнозов. В скобках — матричное произведение, затем его обратная матрица.")
    + box("Условие применения формулы",
        r"Столбцы $X$ должны быть линейно независимы. Тогда квадратная матрица $X^{\mathsf T}X$ обратима. "
        "В подготовленных данных это условие проверено.")
    + "<p>Сегодня используем формулу как упражнение на транспонирование, обратную матрицу и порядок умножения. "
      "Её вывод и оценку качества прогнозов разберём в теме линейной регрессии.</p>"
    + "<p><b>До вычислений:</b> запишите размеры каждого промежуточного произведения и ожидаемые размеры весов и прогнозов. "
      "Затем вычислите веса и прогнозы.</p>")
code('''# Reproducible synthetic inputs, adapted from the supplied formula exercise.
rng = np.random.default_rng(12)
X_reg_task = rng.normal(size=(10, 7))
y_reg_task = rng.normal(size=10)
assert np.linalg.matrix_rank(X_reg_task) == X_reg_task.shape[1]
print("Размер матрицы признаков:", X_reg_task.shape)
print("Размер целевого вектора:", y_reg_task.shape)
# TODO: Apply the supplied weight formula and compute the predictions.
w_reg_task = ...
y_pred_task = ...''', ("student-core", "task-4"))
code('''if w_reg_task is Ellipsis or y_pred_task is Ellipsis:
    print("Сначала заполните задачу 4.")
else:
    print("Размер вектора весов:", np.shape(w_reg_task))
    print("Размер вектора прогнозов:", np.shape(y_pred_task))
    display(pd.DataFrame({"Целевое значение": y_reg_task, "Прогноз": y_pred_task}))
    fig, ax = plt.subplots(figsize=(7, 3.5))
    observation = np.arange(1, len(y_reg_task) + 1)
    ax.scatter(observation, y_reg_task, label="Целевые значения", s=55)
    ax.scatter(observation, y_pred_task, label="Прогнозы", marker="x", s=65)
    ax.vlines(observation, y_reg_task, y_pred_task, color="gray", alpha=0.5)
    ax.set(xlabel="Номер наблюдения", ylabel="Значение", title="Прогнозы могут отличаться от наблюдений")
    ax.set_xticks(observation)
    ax.legend()
    ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.show()''', ("provided", "task-check"))
md("""**Ваш вывод:** совпали ли ожидаемые размеры с полученными? Почему здесь нельзя просто вычислить обратную к исходной матрице признаков?

Точное совпадение всех прогнозов с целевыми значениями не требуется. Данные синтетические; этот расчёт сам по себе не проверяет качество прогнозов на новых наблюдениях.

_Ответ: …_
""", ("interpretation",))

md("## 9. Дополнительная практика")
md("Эти две задачи можно оставить для самостоятельной работы. Они используют те же операции, но матрицы здесь больше.")

theory("Задача 5. Неизвестная между двумя матрицами",
    eq(r"SXQ=B.",
         r"$S,Q,B$ — известные матрицы размера $5\times5$; $X$ — неизвестная матрица того же размера; "
         r"$S$ и $Q$ обратимы.")
    + "<p>Выразите X, последовательно убрав известные множители с нужных сторон. "
      "Вычислите её с помощью обратных матриц. Внимательно сохраните порядок умножения.</p>")
code('''S_two_task = np.array([[7, -4, 8, -3, 8],
                       [-3, -4, -3, -5, -1],
                       [-4, -5, 8, -4, 9],
                       [2, 0, -4, -3, 2],
                       [7, 1, -2, 3, 9]])
Q_two_task = np.array([[8, 7, 9, 4, 2],
                       [7, 1, 1, 4, -4],
                       [4, 2, 6, 5, 5],
                       [8, -4, 4, 3, 3],
                       [-3, 1, 4, -4, -3]])
B_two_task = np.array([[5016, 1289, 5240, 2404, 621],
                       [-4296, -1079, -4520, -2044, -531],
                       [4404, 1241, 4460, 2176, 549],
                       [-1233, -327, -1275, -597, -153],
                       [5958, 1542, 6210, 2862, 738]])
# TODO: Isolate and compute the unknown matrix.
X_two_task = ...''', ("student-core", "task-5", "optional"))
code('''if X_two_task is Ellipsis:
    print("Дополнительная задача 5 пока не заполнена.")
else:
    print("Полученная матрица:\\n", X_two_task)
    print("Подстановка в SXQ = B:", np.allclose(S_two_task @ X_two_task @ Q_two_task, B_two_task))''', ("provided", "task-check", "optional"))
md("**С какой стороны вы умножали на каждую обратную матрицу?** …", ("interpretation", "optional"))

theory("Задача 6. СЛУ с пятью неизвестными",
    eq(r"\begin{cases}x_1+2x_2+3x_3+4x_4+5x_5=2,\\2x_1+3x_2+7x_3+10x_4+13x_5=12,\\3x_1+5x_2+11x_3+16x_4+21x_5=17,\\2x_1-7x_2+7x_3+7x_4+2x_5=57,\\x_1+4x_2+5x_3+3x_4+10x_5=7.\end{cases}",
         r"$x_1,\ldots,x_5$ — пять неизвестных; числа перед ними — коэффициенты; "
         "2, 12, 17, 57, 7 — правые части уравнений.")
    + "<p>Составьте матрицу коэффициентов и вектор правой части, затем найдите решение с помощью "
      "<code>np.linalg.solve</code>. Проверка должна охватить все пять уравнений.</p>")
code('''# TODO: Transcribe the system and solve it.
A_five_task = ...
b_five_task = ...
x_five_task = ...''', ("student-core", "task-6", "optional"))
code('''if any(value is Ellipsis for value in [A_five_task, b_five_task, x_five_task]):
    print("Дополнительная задача 6 пока не заполнена.")
else:
    print("Решение:", x_five_task)
    print("Левые части:", A_five_task @ x_five_task)
    print("Все уравнения выполнены:", np.allclose(A_five_task @ x_five_task, b_five_task))''', ("provided", "task-check", "optional"))
md("**Какая строка матрицы соответствует уравнению с отрицательным коэффициентом? Как вы проверили перенос знаков?** …", ("interpretation", "optional"))

md("""**Источники и повторение**

- [Занятие 10: матрицы и порядок умножения](10_matrices.ipynb).
- [Занятие 11: зависимость, ранг и вырожденность](11_linear_dependence_rank.ipynb).
- [3Blue1Brown: обратные матрицы и геометрия систем](https://www.3blue1brown.com/lessons/inverse-matrices/).
- [3Blue1Brown: геометрический смысл определителя](https://www.3blue1brown.com/lessons/determinant/).
- [NumPy: обратная матрица](https://numpy.org/doc/stable/reference/generated/numpy.linalg.inv.html).
- [NumPy: решение систем](https://numpy.org/doc/stable/reference/generated/numpy.linalg.solve.html).
- [NumPy: определитель](https://numpy.org/doc/stable/reference/generated/numpy.linalg.det.html).

Задания адаптированы из набора упражнений преподавателя: исходные Task 5, 12–16.
Условия со скриншотов перепечатаны; все необходимые данные находятся в этом ноутбуке.
""")

nb = nbf.v4.new_notebook(cells=cells, metadata=json.loads(json.dumps(META)))
nb.metadata["colab"]["name"] = "12_linear_systems_inverse.ipynb"
nb.metadata["lesson"] = {
    "number": 12, "duration_minutes": 120,
    "format": "Shared dark HTML theory, self-contained SVG/JS widgets, worked NumPy examples.",
    "source": "build_lesson12.py + embedded lesson12_widgets.js",
    "prerequisites": ["10_matrices.ipynb", "11_linear_dependence_rank.ipynb"],
    "data": "Small synthetic matrices embedded in the notebook; no downloads.",
    "practice": "Four core tasks and two optional tasks for classroom practice or homework.",
    "exercise_provenance": "Adapted from instructor-supplied linal_lab.ipynb Tasks 5, 12, 15, 14, 13, 16; no runtime/build dependency on that temporary file.",
    "student_code_tags": ["student-core"],
}
for index, cell in enumerate(nb.cells):
    cell.id = hashlib.sha256(f"lesson12-{index}-{cell.source}".encode()).hexdigest()[:12]
nbf.validate(nb)
path = HERE / "12_linear_systems_inverse.ipynb"
nbf.write(nb, path)
print(f"Wrote {path.name}: {len(cells)} cells; standalone HTML/JS lesson")
