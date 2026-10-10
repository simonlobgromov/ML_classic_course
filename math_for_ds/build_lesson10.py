"""Build the standalone matrices lesson with HTML theory and JS/SVG visuals."""
from pathlib import Path
import base64
import hashlib
import json
import nbformat as nbf
from theme import SETUP, META

HERE = Path(__file__).resolve().parent
WIDGET_JS = (HERE / "lesson10_widgets.js").read_text(encoding="utf-8")
cells = []


def md(source, tags=()):
    cells.append(nbf.v4.new_markdown_cell(source.strip(), metadata={"tags": list(tags)}))


def code(source, tags=("provided", "example")):
    cells.append(nbf.v4.new_code_cell(source.strip(), metadata={"tags": list(tags)}))


def network_image():
    """Embed the instructor's original image without modifying its bytes."""
    image = (HERE / "images" / "lesson10_threshold_network.png").read_bytes()
    cell = nbf.v4.new_markdown_cell(
        "![Схема: три входных признака, два скрытых нейрона и один выходной](attachment:image.png)",
        metadata={"tags": ["provided", "task-network-image"]},
    )
    cell["attachments"] = {"image.png": {"image/png": base64.b64encode(image).decode("ascii")}}
    cells.append(cell)


def eq(formula, meanings):
    """Require a glossary for every displayed equation."""
    if not meanings:
        raise ValueError("An equation needs a glossary")
    return ("<div class='d10-equation'>$$" + formula + "$$</div>"
            + "<div class='where'><b>Обозначения.</b> " + meanings + "</div>")


def box(title, body, kind="idea"):
    return f'<div class="box {kind}"><div class="t">{title}</div>{body}</div>'


def definition(title, body):
    return box(title, body, "def")


def theory(title, body):
    code(f'#@title {title} {{ display-mode: "form" }}\n'
         + 'display(HTML(lesson10_viz(' + repr(body) + ')))', ("provided", "theory"))


def widget(kind, title, instruction, question, data="None"):
    body = (f'<div class="widget"><div class="widget-title">{title}</div>'
            + f'<p class="widget-sub">{instruction}</p><div data-stage></div>'
            + '<div class="readout" data-readout role="status" aria-live="polite"></div>'
            + f'<p class="d10-question"><b>Проверь себя.</b> {question}</p>'
            + '<p class="d10-footnote">Интерактивная иллюстрация. Изменения здесь не меняют переменные в Python.</p></div>')
    code(f'#@title Интерактив — {title} {{ display-mode: "form" }}\n'
         + 'display(HTML(lesson10_viz(' + repr(body) + ', widget=' + repr(kind)
         + ', data=' + data + ')))', ("provided", "interactive"))


md(r"""
# Как матрица преобразует данные?
## Занятие 10 — матрицы и матричное умножение

В первых занятиях каждое наблюдение было вектором, а датасет — облаком точек.
Теперь научимся записывать несколько векторов одной матрицей и выполнять операции сразу с ними всеми.

Разберём, **как вычисляется матричное произведение и что оно делает с векторами**.
В начале вернёмся к росту и весу из Davis; для вычислений и геометрии возьмём небольшие учебные примеры.
В конце — четыре задачи для практики: поворот, оценка стоимости автомобилей и небольшая нейросеть с заданными весами.

Запускайте ячейки по порядку. Сначала предскажите результат, затем проверьте его в интерактиве и в NumPy.
Определения и графики находятся в свёрнутых HTML-ячейках, примеры Python открыты.
Ноутбук содержит весь код и небольшую таблицу данных. Формулы загружаются через MathJax;
после запуска интерактивы работают без обращений к Python.
""")

EXTRA_SETUP = r'''
import json
import uuid
import re
from html import escape

D10_CSS = r"""
.vec-root .d10-controls{display:flex;flex-wrap:wrap;gap:12px 24px;margin:16px 0 22px;font-family:system-ui,sans-serif;}
.vec-root .d10-control{display:flex;align-items:center;flex-wrap:wrap;gap:8px;color:var(--ink);font-size:14px;min-height:36px;}
.vec-root .d10-control input[type=range]{width:155px;min-height:30px;}
.vec-root .d10-control output{font-variant-numeric:tabular-nums;color:var(--green);min-width:42px;}
.vec-root .d10-control select{max-width:100%;padding:8px;}
.vec-root .d10-control input:disabled{opacity:.3;}
.vec-root .d10-charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,380px),1fr));gap:16px;}
.vec-root .d10-charts svg{display:block;width:100%;height:auto;background:#0e1319;border-radius:10px;}
.vec-root .d10-charts svg:last-child:nth-child(3){grid-column:1/-1;max-width:780px;justify-self:center;}
.vec-root .readout{overflow-wrap:anywhere;font:15px/1.75 system-ui,sans-serif;}
.vec-root .d10-question{font-family:system-ui,sans-serif;font-size:14px;color:var(--ink);}
.vec-root .d10-footnote{font-family:system-ui,sans-serif;font-size:12px;color:var(--soft);}
.vec-root .d10-equation{overflow-x:auto;overflow-y:hidden;padding:5px 0;}
.vec-root .where{line-height:1.7;}
.vec-root .d10-table{overflow-x:auto;}
.vec-root button:disabled{opacity:.45;cursor:wait;}
.vec-root .d10-controls .btn{min-height:38px;}
.vec-root input:focus-visible,.vec-root select:focus-visible,.vec-root button:focus-visible{outline:2px solid #e0b25a;outline-offset:4px;}
@media(max-width:600px){.vec-root .wrap{padding:14px;font-size:16px;}.vec-root .widget{padding:10px;}.vec-root .d10-control{width:100%;}}
"""

def lesson10_viz(body, widget=None, data=None):
    """Scope controls to a fresh root so rerunning cells keeps widgets independent."""
    # HTML is parsed before MathJax. Protect comparisons and ampersands in both
    # display equations and inline symbol glossaries without escaping HTML tags.
    body = re.sub(
        r"(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$.*?(?<!\\)\$",
        lambda match: escape(match.group(0), quote=False),
        body,
        flags=re.DOTALL,
    )
    root_id = "d10_" + uuid.uuid4().hex
    script = D10_WIDGET_JS + "\n" + r"""
    (function(){
      const root = document.getElementById(__ROOT__);
      const widget = __WIDGET__;
      if (widget) window.MatricesLesson10.mount(root, widget, __DATA__);
      const typeset = () => window.MathJax.typesetPromise([root]);
      if (!window.__D10_MATH_READY__) {
        if (window.MathJax && window.MathJax.typesetPromise) {
          window.__D10_MATH_READY__ = window.MathJax.startup.promise;
        } else {
          window.MathJax = {tex:{inlineMath:[['$','$']],displayMath:[['$$','$$']]},svg:{fontCache:'local'},startup:{typeset:false}};
          window.__D10_MATH_READY__ = new Promise((resolve, reject) => {
            const loader = document.createElement('script');
            loader.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
            loader.onload = () => window.MathJax.startup.promise.then(resolve, reject);
            loader.onerror = reject;
            document.head.appendChild(loader);
          });
        }
      }
      window.__D10_MATH_READY__ = window.__D10_MATH_READY__.then(typeset).catch(() => {
        if(root.querySelector('.d10-equation')) {
          const notice = document.createElement('p');
          notice.textContent = 'Для отображения формул подключитесь к интернету и перезапустите ячейку. Графики работают без загрузки MathJax.';
          root.appendChild(notice);
        }
      });
    })();
    """.replace("__ROOT__", json.dumps(root_id)).replace("__WIDGET__", json.dumps(widget)).replace("__DATA__", json.dumps(data, ensure_ascii=False))
    return ("<style>" + CSS + D10_CSS + "</style>"
            + '<div class="vec-root" data-widget="' + (widget or "theory") + '" id="' + root_id + '"><div class="wrap wide">'
            + body + '</div></div><script>' + script + '</script>')

print("Занятие 10 готово: графики работают в браузере; формулы загружаются через MathJax.")'''

code(SETUP + "\n\nD10_WIDGET_JS = " + repr(WIDGET_JS) + "\n" + EXTRA_SETUP + "\nimport numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt", ("provided", "setup"))

md("## 1. От таблицы данных к матрице")
theory("Матрица, размер и элемент",
    "<p>В Davis одна строка описывает человека двумя числами: весом и ростом. "
    "Соберём шесть таких строк вместе.</p>"
    + definition("Матрица · matrix", "<p><b>Матрица</b> — прямоугольная таблица чисел. "
        "Её <b>размер</b> записывают как число строк × число столбцов.</p>"
        + eq(r"A=(a_{ij})\in\mathbb R^{m\times n}.",
             r"$A$ — матрица; $m$ — число строк; $n$ — число столбцов; "
             r"$a_{ij}$ — число в строке $i$ и столбце $j$; $\mathbb R$ — вещественные числа."))
    + "<p>В <b>матрице данных</b> строки обычно соответствуют наблюдениям, столбцы — признакам. "
      r"В нашем примере размер равен $6\times2$: шесть людей и два признака.</p>"
    + box("Нумерация", "В формулах номера строк и столбцов начинаются с 1. "
          "В NumPy индексы начинаются с 0: элемент $a_{ij}$ записывается как <code>A[i-1, j-1]</code>."))

code('''# First six rows of Davis, in the original order; no download is needed.
# Source: aiacademy-kg/davis_dataset, revision cfb0d88e0d0a8814998ecfb36179bd18d0cbbb5a.
X = np.array([[77, 182], [58, 161], [53, 161],
              [68, 177], [59, 157], [76, 170]])
display(pd.DataFrame(X, columns=["Вес, кг", "Рост, см"]))
print("Размер матрицы:", X.shape)
print("Первая строка — один человек:", X[0, :])
print("Первый столбец — вес всех людей:", X[:, 0])
print("Строка 2, столбец 1:", X[1, 0])''')

widget("data", "Строка матрицы — точка на графике",
       "Выберите строку: найдите этого человека на графике «вес — рост».",
       "Что изменится в размере матрицы, если добавить ещё одного человека? А если добавить новый признак?",
       "{'X': X.tolist(), 'labels': ['Вес, кг', 'Рост, см']}")

md("## 2. Простые операции с матрицами")
theory("Сложение, вычитание и умножение на число",
    "<p>Две матрицы <b>равны</b>, если их размеры совпадают и все элементы на одинаковых местах равны. "
    "Складывать и вычитать матрицы можно, если их размеры совпадают: работаем с числами на одинаковых местах.</p>"
    + eq(r"(A+B)_{ij}=a_{ij}+b_{ij},\qquad (A-B)_{ij}=a_{ij}-b_{ij},\qquad (\lambda A)_{ij}=\lambda a_{ij}.",
         r"$A,B$ — матрицы одного размера; $a_{ij},b_{ij}$ — их элементы в строке $i$, столбце $j$; "
         r"$\lambda$ — число, на которое умножается каждый элемент матрицы.")
    + "<p><b>Нулевая матрица</b> состоит из нулей. <b>Квадратная матрица</b> имеет одинаковое число строк и столбцов.</p>"
    + box("В NumPy", "<code>A + B</code>, <code>A - B</code>, <code>2 * A</code>. "
          "В этих примерах обе матрицы имеют один и тот же размер."))

code('''A_basic = np.array([[1, 2, 3], [4, 5, 6]])
B_basic = np.array([[6, 5, 4], [3, 2, 1]])
print("Сумма:\\n", A_basic + B_basic)
print("Разность:\\n", A_basic - B_basic)
print("Умножение на 2:\\n", 2 * A_basic)
print("Нулевая матрица размера 2 × 3:\\n", np.zeros((2, 3), dtype=int))''')

theory("Транспонирование · transpose",
    definition("Транспонированная матрица",
        "<p>При <b>транспонировании</b> строки исходной матрицы становятся столбцами новой матрицы, "
        "с сохранением их порядка.</p>"
        + eq(r"(A^{\mathsf T})_{ji}=a_{ij},\qquad A:\ m\times n\ \longrightarrow\ A^{\mathsf T}:\ n\times m.",
             r"$A$ — исходная матрица; $A^{\mathsf T}$ — транспонированная; "
             r"$a_{ij}$ — элемент строки $i$, столбца $j$; $m,n$ — число строк и столбцов исходной матрицы."))
    + "<p>В NumPy: <code>A.T</code>. Например, таблица из двух строк и трёх столбцов станет таблицей из трёх строк и двух столбцов.</p>")

code('''print("Исходная матрица:", A_basic.shape, "\\n", A_basic)
print("Транспонированная:", A_basic.T.shape, "\\n", A_basic.T)
print("Два транспонирования возвращают исходную:", np.array_equal(A_basic.T.T, A_basic))''')

widget("operations", "Что происходит с отдельными элементами?",
       "Выберите операцию и элемент исходной матрицы A. Проследите, что с ним происходит.",
       "Выберите «Умножение на число k». Что получится при k = 2, k = 0 и k = −1? "
       "Какая из остальных операций меняет размер прямоугольной матрицы?")

md("## 3. Вспомним скалярное произведение")
theory("Скалярное произведение · dot product",
    definition("Скалярное произведение вещественных векторов",
        "<p><b>Скалярное произведение</b> двух векторов с одинаковым числом координат — сумма произведений их соответствующих координат. "
        "Результат — одно число.</p>"
        + eq(r"a\cdot b=\sum_{k=1}^{n}a_kb_k=a_1b_1+\cdots+a_nb_n.",
             r"$a,b$ — векторы из $n$ вещественных координат; $a_k,b_k$ — их $k$-е координаты; "
             r"$\sum$ означает сложение всех слагаемых от $k=1$ до $k=n$."))
    + r"<p>Например, для векторов $(1,2,3)$ и $(4,0,-1)$ получаем $1\cdot4+2\cdot0+3\cdot(-1)=1$.</p>"
    + box("Что означает название np.dot?",
        "Математический термин <b>dot product</b> здесь означает скалярное произведение векторов. "
        "Но функция <code>np.dot</code> работает с разными формами массивов: "
        "для двух одномерных массивов она считает скалярное произведение, "
        "для двух двумерных — матричное произведение. Поэтому всегда смотрим на <code>.shape</code>.", "warn"))

code('''a = np.array([1, 2, 3])
b = np.array([4, 0, -1])
print("Размеры:", a.shape, b.shape)
print("По определению:", (a * b).sum())
print("Через np.dot:", np.dot(a, b))
print("Через @:", a @ b)
print("Только попарные произведения:", a * b)''')

theory("Вектор в математике и массив в NumPy",
    "<p>В формулах будем записывать вектор <b>столбцом</b>. "
    "В NumPy массив <code>np.array([1, 2])</code> имеет форму <code>(2,)</code>: "
    "он одномерный, у него ещё нет отдельного направления «строка» или «столбец». "
    "Операция <code>.T</code> его не меняет.</p>"
    + "<p>Чтобы явно получить столбец, используем <code>x.reshape(-1, 1)</code>. "
      "Число <code>-1</code> означает: NumPy сам определит нужное число строк.</p>")

code('''x = np.array([1, 2])
x_col = x.reshape(-1, 1)
print("Одномерный массив:", x.shape, x)
print("После .T:", x.T.shape, x.T)
print("Явный столбец:", x_col.shape, "\\n", x_col)
print("Явная строка:", x_col.T.shape, x_col.T)''')

md("## 4. Матрица × вектор: два взгляда на один результат")
theory("Каждая строка даёт одну координату",
    "<p>Возьмём скалярное произведение <b>каждой строки матрицы</b> с входным вектором. "
    "Запишем полученные числа в столбец — это результат умножения матрицы на вектор.</p>"
    + eq(r"y=Ax,\qquad y_i=\sum_{k=1}^{n}a_{ik}x_k.",
         r"$A$ — матрица размера $m\times n$; $x$ — входной вектор из $n$ координат; "
         r"$y$ — результат из $m$ координат; $y_i$ — его $i$-я координата; "
         r"$a_{ik}$ — элемент строки $i$, столбца $k$; $x_k$ — $k$-я координата входа; $\sum$ — сумма по $k=1,\ldots,n$.")
    + eq(r"\begin{pmatrix}2&1\\0&1\end{pmatrix}\begin{pmatrix}1\\2\end{pmatrix}"
         r"=\begin{pmatrix}2\cdot1+1\cdot2\\0\cdot1+1\cdot2\end{pmatrix}=\begin{pmatrix}4\\2\end{pmatrix}.",
         r"Слева — матрица $A$ и вектор $x$; справа — две координаты результата $y=Ax$.")
    + box("Условие умножения", "Число столбцов матрицы должно совпасть с числом координат вектора. "
          "Число строк матрицы определяет число координат результата."))

code('''A = np.array([[2, 1], [0, 1]])
x = np.array([1, 2])
y_rows = np.array([(A[0] * x).sum(), (A[1] * x).sum()])
print("Через скалярные произведения строк:", y_rows)
print("Через @:", A @ x)
print("Через np.dot:", np.dot(A, x))
print("Для явного столбца результат тоже столбец:\\n", A @ x.reshape(-1, 1))''')

theory("Вспомним линейную комбинацию",
    definition("Линейная комбинация · linear combination",
        "<p><b>Линейной комбинацией</b> векторов называют сумму этих векторов, умноженных на числовые коэффициенты. "
        "Все складываемые векторы должны иметь одинаковое число координат.</p>"
        + eq(r"\lambda_1v_1+\cdots+\lambda_nv_n.",
             r"$v_1,\ldots,v_n$ — векторы; $\lambda_1,\ldots,\lambda_n$ — вещественные числа, "
             r"называемые коэффициентами; $n$ — число слагаемых."))
    + "<p>Умножение матрицы на вектор можно прочитать по столбцам: "
      "берём столбцы матрицы с коэффициентами из входного вектора и складываем.</p>"
    + eq(r"Ax=x_1a^{(1)}+\cdots+x_na^{(n)}.",
         r"$A$ — матрица с $n$ столбцами; $a^{(k)}$ — её $k$-й столбец целиком; "
         r"$x_k$ — $k$-я координата вектора $x$, коэффициент перед этим столбцом. "
         r"Верхний индекс в скобках обозначает номер столбца, а не степень.")
    + eq(r"Ax=1\begin{pmatrix}2\\0\end{pmatrix}+2\begin{pmatrix}1\\1\end{pmatrix}=\begin{pmatrix}4\\2\end{pmatrix}.",
         r"$A=\begin{pmatrix}2&1\\0&1\end{pmatrix}$, $x=(1,2)^{\mathsf T}$; "
         r"два столбца справа — столбцы $A$, числа 1 и 2 — координаты $x$.")
    + box("Одна операция, два объяснения",
          "<b>По строкам:</b> считаем координаты результата через скалярные произведения. "
          "<b>По столбцам:</b> собираем результат как линейную комбинацию."))

code('''first_column = A[:, 0]
second_column = A[:, 1]
y_columns = x[0] * first_column + x[1] * second_column
print("Первое слагаемое:", x[0] * first_column)
print("Второе слагаемое:", x[1] * second_column)
print("Их сумма:", y_columns)
print("Совпало с A @ x:", np.array_equal(y_columns, A @ x))''')

md("## 5. Геометрия: что матрица делает с точками?")
theory("Линейное преобразование",
    "<p>Применим одну и ту же матрицу к каждой точке плоскости. "
    "Каждый входной вектор превратится в выходной. Это можно увидеть как изменение целого рисунка.</p>"
    + definition("Линейное преобразование · linear transformation",
        "<p><b>Линейное преобразование</b> — функция из векторов в векторы, которая сохраняет "
        "сложение и умножение на число. Эти два требования можно записать вместе:</p>"
        + eq(r"T(\alpha u+\beta v)=\alpha T(u)+\beta T(v).",
             r"$T$ — преобразование; $u,v$ — любые входные векторы; $\alpha,\beta$ — любые вещественные числа; "
             r"$T(u),T(v)$ — результаты преобразования этих векторов."))
    + "<p>Умножение на фиксированную матрицу задаёт такое преобразование: $T(x)=Ax$. "
      "Здесь $x$ — входной вектор, $A$ — одна и та же матрица для всех входов. "
      "Нулевой вектор остаётся нулевым.</p>"
    + box("Две роли матрицы", "Матрица $X$ может хранить наблюдения. Матрица $A$ может задавать правило их изменения. "
          "Геометрическая иллюстрация ниже показывает именно <b>действие</b> матрицы $A$."))

theory("Почему столбцы определяют всю картинку?",
    "<p>Выделим два единичных вектора вдоль осей. Они образуют <b>стандартный базис плоскости</b>: "
    "любой вектор плоскости единственным образом получается как их линейная комбинация.</p>"
    + eq(r"e_1=\begin{pmatrix}1\\0\end{pmatrix},\quad e_2=\begin{pmatrix}0\\1\end{pmatrix},\quad x=x_1e_1+x_2e_2.",
         r"$e_1,e_2$ — единичные векторы вдоль первой и второй осей; $x$ — произвольный вектор; "
         r"$x_1,x_2$ — его координаты.")
    + eq(r"Ae_1=a^{(1)},\qquad Ae_2=a^{(2)},\qquad Ax=x_1a^{(1)}+x_2a^{(2)}.",
         r"$A$ — матрица размера $2\times2$; $a^{(1)},a^{(2)}$ — её первый и второй столбцы; "
         r"$e_1,e_2$ — единичные векторы; $x_1,x_2$ — координаты входного вектора $x$.")
    + box("Что читать в столбцах?", "<b>Первый столбец</b> показывает, куда попадёт $e_1$. "
          "<b>Второй столбец</b> показывает, куда попадёт $e_2$. "
          "Положение остальных точек определяется той же линейной комбинацией.")
    + "<p>Попробуйте растяжение, поворот и отражение. В режиме <b>скоса</b> "
      "горизонтальная координата увеличивается на вертикальную, а вертикальная сохраняется: квадрат становится параллелограммом.</p>")

widget("transform", "Меняем матрицу — меняется рисунок",
       "Выберите готовое преобразование, затем измените элементы матрицы или координаты входного вектора. "
       "Сравните столбцы матрицы с двумя цветными стрелками после преобразования.",
       "Что произойдёт с результатом, если удвоить обе координаты входного вектора? "
       "Какая матрица оставляет все точки на месте?")

theory("Та же геометрия в NumPy",
    "<p>В следующем примере матрица $A$ применяется к каждой точке небольшого рисунка. "
    "Сначала вычисляем <code>A @ point</code> для каждой точки отдельно; "
    "ниже научимся преобразовывать всю таблицу одной командой.</p>"
    + "<p>На обоих графиках одинаковый масштаб осей. Поэтому растяжение и изменение углов видны без искажений.</p>")

code('''# A small synthetic polygon; every row is one point.
points = np.array([[0, 0], [2, 0], [2, 1], [1, 2], [0, 1], [0, 0]])
A = np.array([[2, 1], [0, 1]])
transformed = np.array([A @ point for point in points])

fig, axes = plt.subplots(1, 2, figsize=(9, 4), sharex=True, sharey=True)
for ax, data, title in zip(axes, [points, transformed], ["Исходные точки", "После умножения на A"]):
    ax.plot(data[:, 0], data[:, 1], "o-", color="#318b62")
    ax.axhline(0, color="gray", linewidth=0.7)
    ax.axvline(0, color="gray", linewidth=0.7)
    ax.set(xlim=(-1, 6), ylim=(-1, 6), xlabel="Первая координата", ylabel="Вторая координата", title=title)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=0.25)
plt.tight_layout()
plt.show()''')

md("## 6. Матрица × матрица")
theory("Каждая ячейка — скалярное произведение",
    definition("Матричное произведение · matrix multiplication",
        "<p>Пусть число столбцов матрицы $A$ равно числу строк матрицы $B$. "
        "Их <b>матричным произведением</b> называют матрицу $C$, в которой элемент "
        "строки $i$ и столбца $j$ равен скалярному произведению строки $i$ матрицы $A$ и столбца $j$ матрицы $B$.</p>"
        + eq(r"C=AB,\qquad c_{ij}=\sum_{k=1}^{n}a_{ik}b_{kj}.",
             r"$A$ имеет размер $m\times n$, $B$ — $n\times p$, $C$ — $m\times p$; "
             r"$c_{ij}$ — элемент результата; $a_{ik}$ — элемент строки $i$, столбца $k$ матрицы $A$; "
             r"$b_{kj}$ — элемент строки $k$, столбца $j$ матрицы $B$; $\sum$ — сумма по $k=1,\ldots,n$."))
    + eq(r"(m\times\underbrace{n}_{\text{совпадают}})\;\cdot\;(\underbrace{n}_{\text{совпадают}}\times p)"
         r"\quad\longrightarrow\quad m\times p.",
         r"$m,n,p$ — числа строк и столбцов: внутренние размеры должны совпасть, "
         r"внешние определяют размер результата.")
    + box("Связь с предыдущим шагом", "Каждый столбец $B$ — отдельный входной вектор. "
          "Матрица $A$ преобразует каждый из них. Полученные векторы становятся столбцами $AB$."))

widget("multiply", "Строка × столбец → одна ячейка",
       "Выберите ячейку произведения. Проследите, какие элементы перемножаются и складываются. "
       "Смените пример и проверьте размеры.",
       "У матрицы A две строки и три столбца. Какой размер должна иметь B, чтобы произведение AB имело четыре столбца?")

code('''A_mul = np.array([[1, 2, 0], [-1, 3, 1]])
B_mul = np.array([[2, 1], [0, 4], [3, -2]])

# Compute the first entry by definition, then the whole product.
first_entry = (A_mul[0, :] * B_mul[:, 0]).sum()
C = A_mul @ B_mul
print("Первая ячейка по определению:", first_entry)
print("A @ B:\\n", C)
print("Размеры:", A_mul.shape, "×", B_mul.shape, "→", C.shape)
print("np.dot даёт то же матричное произведение:\\n", np.dot(A_mul, B_mul))
print("np.matmul даёт то же произведение:\\n", np.matmul(A_mul, B_mul))
print("Первый столбец результата — A @ первый столбец B:", A_mul @ B_mul[:, 0])''')

theory("Что выбирать в NumPy: *, @ или np.dot?",
    "<table><tr><th>Вход</th><th>Действие</th><th>Запись</th><th>Результат</th></tr>"
    "<tr><td>Два одномерных массива с одинаковым числом элементов</td><td>Скалярное произведение</td>"
    "<td><code>a @ b</code> или <code>np.dot(a, b)</code></td><td>Число</td></tr>"
    "<tr><td>Матрица и вектор подходящей длины</td><td>Матрица × вектор</td>"
    "<td><code>A @ x</code> или <code>np.dot(A, x)</code></td><td>Вектор</td></tr>"
    "<tr><td>Две матрицы с согласованными размерами</td><td>Матричное произведение</td>"
    "<td><code>A @ B</code> или <code>np.dot(A, B)</code></td><td>Матрица</td></tr>"
    "<tr><td>Два массива одинаковой формы</td><td>Поэлементное умножение</td>"
    "<td><code>A * B</code></td><td>Массив той же формы</td></tr></table>"
    + box("Практическое правило", "Для матричного умножения используем <code>@</code> "
          "или равнозначную функцию <code>np.matmul</code>. "
          "<code>*</code> перемножает элементы попарно и не складывает произведения.", "warn")
    + "<p>Здесь рассматриваем только вещественные векторы и двумерные матрицы. "
      "Для массивов с тремя и более осями <code>np.dot</code> и <code>@</code> могут действовать по-разному.</p>"
    + "<details><summary>Почему NumPy иногда складывает массивы разных форм?</summary>"
      "<p>NumPy умеет автоматически расширять некоторые формы массивов — это называется <b>broadcasting</b>. "
      "Например, прибавить одну строку к каждой строке таблицы. Это отдельное правило NumPy; "
      "в определении сложения матриц выше размеры матриц должны совпадать.</p></details>")

code('''P = np.array([[1, 2], [3, 4]])
Q = np.array([[5, 6], [7, 8]])
print("Поэлементное P * Q:\\n", P * Q)
print("Матричное P @ Q:\\n", P @ Q)
print("Первая ячейка P @ Q:", 1 * 5 + 2 * 7)

# An incompatible pair is checked before multiplication.
wrong = np.ones((4, 2))
if A_mul.shape[1] != wrong.shape[0]:
    print("Умножение невозможно: число столбцов A не равно числу строк второй матрицы.")''')

md("## 7. Два преобразования подряд и свойства умножения")
theory("Порядок действий имеет значение",
    "<p>Сначала растянем рисунок по горизонтали, затем повернём на 90° против часовой стрелки. "
    "Это <b>композиция преобразований</b> — последовательное применение одного преобразования после другого.</p>"
    + eq(r"R(Sx)=(RS)x,\qquad S=\begin{pmatrix}2&0\\0&1\end{pmatrix},\quad R=\begin{pmatrix}0&-1\\1&0\end{pmatrix}.",
         r"$x$ — исходный вектор; $S$ — растяжение по горизонтали в 2 раза; "
         r"$R$ — поворот на 90° против часовой стрелки; $RS$ — матрица общего действия.")
    + box("Как читать порядок", "В записи $RSx$ сначала действует $S$, затем $R$: "
          "первой применяется матрица, ближайшая к вектору.")
    + "<p>Если сначала повернуть, а затем растянуть, получится $SRx$. "
      "Например, точка $(1,0)$ в первом случае попадёт в $(0,2)$, а во втором — в $(0,1)$. "
      "Значит, перестановка множителей может менять результат.</p>")

widget("composition", "Растяжение и поворот: меняем порядок",
       "Пройдите два шага преобразования. Затем поменяйте порядок и сравните конечные точки. "
       "Посмотрите на матрицу общего действия.",
       "Почему горизонтальное растяжение до поворота и после поворота даёт разные результаты?")

code('''S = np.array([[2, 0], [0, 1]])
R = np.array([[0, -1], [1, 0]])
x_order = np.array([1, 0])
print("Сначала S, затем R:", R @ (S @ x_order))
print("Одним произведением R @ S:", (R @ S) @ x_order)
print("Сначала R, затем S:", S @ (R @ x_order))
print("R @ S:\\n", R @ S)
print("S @ R:\\n", S @ R)''')

theory("Свойства: что сохраняется, а что меняется?",
    definition("Единичная матрица · identity matrix",
        "<p><b>Единичная матрица</b> — квадратная матрица с единицами на главной диагонали "
        "и нулями на остальных местах. Главная диагональ состоит из элементов с одинаковыми номерами строки и столбца.</p>"
        + eq(r"I_2=\begin{pmatrix}1&0\\0&1\end{pmatrix},\qquad I_2x=x.",
             r"$I_2$ — единичная матрица размера $2\times2$; $x$ — любой вектор с двумя координатами."))
    + "<p>Для матриц подходящих размеров выполняются свойства:</p>"
    + "<ul><li><b>Сочетательность:</b> можно менять расстановку скобок.</li></ul>"
    + eq(r"(AB)C=A(BC).", r"$A,B,C$ — матрицы, размеры которых позволяют выполнить указанные произведения.")
    + "<ul><li><b>Распределительность:</b> умножение раскрывает сумму.</li></ul>"
    + eq(r"A(B+C)=AB+AC,\qquad (A+B)C=AC+BC.",
         r"$A,B,C$ — матрицы согласованных размеров; складываемые матрицы имеют одинаковый размер.")
    + "<ul><li><b>Единичная матрица:</b> умножение на неё оставляет матрицу неизменной.</li></ul>"
    + eq(r"I_mA=AI_n=A.", r"$A$ имеет размер $m\times n$; $I_m,I_n$ — единичные матрицы размеров $m\times m$ и $n\times n$.")
    + box("Скобки можно менять, порядок множителей — обычно нельзя",
          r"В общем случае $AB\ne BA$. Иногда одно произведение существует, а другое не определено из-за размеров. "
          "Для некоторых пар равенство всё же выполняется, например при умножении на единичную матрицу.", "warn")
    + "<details><summary>Свойства сложения и транспонирования</summary>"
    + eq(r"A+B=B+A,\quad (A+B)+C=A+(B+C),\quad (A^{\mathsf T})^{\mathsf T}=A.",
         r"$A,B,C$ в суммах — матрицы одного размера; $\mathsf T$ обозначает транспонирование.")
    + "</details>")

code('''I = np.eye(2, dtype=int)
print("Единичная матрица:\\n", I)
print("I @ S совпало с S:", np.allclose(I @ S, S))
print("Сочетательность:", np.allclose((R @ S) @ P, R @ (S @ P)))
print("Распределительность:", np.allclose(R @ (S + P), R @ S + R @ P))
# allclose compares numerical values with a small floating-point tolerance.
print("R @ S и S @ R совпали:", np.allclose(R @ S, S @ R))''')

md("## 8. Зачем это нужно при работе с данными?")
theory("Одна формула для всех наблюдений",
    "<p>Вернёмся к таблице: наблюдения стоят <b>по строкам</b>. "
    "Пусть для каждого заказа известны расстояние в километрах и число остановок. "
    "Зададим простое учебное правило: 3 минуты на километр и 2 минуты на остановку.</p>"
    + eq(r"\widehat t=X_{\text{заказы}}w,\qquad w=\begin{pmatrix}3\\2\end{pmatrix}.",
         r"$X_{\text{заказы}}$ — матрица, где строки — заказы, первый столбец — километры, второй — остановки; "
         r"$w$ — коэффициенты: 3 мин/км и 2 мин/остановку; $\widehat t$ — вектор расчётных времён в минутах.")
    + "<p>Для одной строки это скалярное произведение. Для всей таблицы — одно умножение матрицы на вектор.</p>"
    + box("Связь с ML", "В линейных моделях предсказание строится из взвешенной суммы признаков, "
          "часто с добавлением постоянного слагаемого. Здесь коэффициенты заданы вручную. "
          "Обучение модели позже позволит подбирать их по данным. Этот пример показывает только вычисление по готовым коэффициентам."))

code('''# Synthetic orders; coefficients are illustrative, not fitted to data.
X_orders = np.array([[2, 1], [5, 2], [3, 4]])
w = np.array([3, 2])
times = X_orders @ w
display(pd.DataFrame({"Расстояние, км": X_orders[:, 0],
                      "Остановки": X_orders[:, 1],
                      "Расчётное время, мин": times}))
print("Первый заказ отдельно:", X_orders[0] @ w)''')

theory("Как преобразовать целую таблицу точек?",
    "<p>В геометрии входной вектор был столбцом: $y=Ax$. "
    "В таблице каждый такой вектор записан строкой. Чтобы применить <b>то же самое преобразование</b> "
    "ко всем строкам, умножаем таблицу справа на транспонированную матрицу.</p>"
    + eq(r"Y=XA^{\mathsf T}.",
         r"$X$ — таблица размера $N\times n$ с $N$ наблюдениями по строкам; "
         r"$A$ — матрица преобразования размера $m\times n$; "
         r"$A^{\mathsf T}$ имеет размер $n\times m$; $Y$ — результат размера $N\times m$.")
    + "<p>Рассмотрим первую координату результата: для каждого наблюдения она должна быть скалярным произведением "
      "с первой строкой $A$. В матричном произведении справа берётся <b>столбец</b>, "
      "поэтому нужная строка $A$ должна стать столбцом — для этого и требуется транспонирование.</p>"
    + box("Проверяем на знакомом рисунке", "Сравним одну команду для таблицы с уже выполненным "
          "умножением каждой точки отдельно. Результаты должны совпасть."))

code('''A = np.array([[2, 1], [0, 1]])
Y = points @ A.T
print("Таблица до:", points.shape, "→ после:", Y.shape)
print("Первая ненулевая точка отдельно:", A @ points[1])
print("Та же точка в таблице результата:", Y[1])
print("Все точки совпали с поочерёдным расчётом:", np.allclose(Y, transformed))''')

theory("Что теперь можно объяснить",
    box("Основные идеи", "<ul><li>Размер матрицы задаёт число её строк и столбцов.</li>"
        "<li>Каждая ячейка матричного произведения — скалярное произведение строки и столбца.</li>"
        "<li>Матрица × вектор — линейная комбинация столбцов матрицы.</li>"
        "<li>Столбцы матрицы преобразования показывают, куда переходят единичные векторы вдоль осей.</li>"
        "<li>Произведение двух матриц объединяет два преобразования; порядок обычно важен.</li>"
        "<li>В NumPy выбираем операцию по смыслу и проверяем <code>.shape</code>.</li></ul>", "take"))

md("""**Проверьте понимание словами**

1. Чем матрица размера 2 × 3 отличается от матрицы 3 × 2?
2. Что означает `np.dot(a, b)` для двух одномерных массивов? А для двух матриц?
3. Чем `A * B` отличается от `A @ B`?
4. Как объяснить результат `A @ x` через строки? А через столбцы?
5. Почему в произведении `R @ S @ x` первым действует `S`?
6. Что означает каждое число в результате `X_orders @ w` и в каких оно единицах?
""", ("interpretation",))

md("""## 9. Практика: от поворота к нейросети

В следующих задачах данные и веса уже заданы. Заполните пропуски `...` в расчётах.
После вычислений объясните, что означает результат. Графики и итоговые таблицы подготовлены:
они появятся, когда вы заполните соответствующие ячейки.
""")

md("### Задача 1. Повернуть точку и целую фигуру")
theory("Условие — поворот на 90°",
    "<p>Точка имеет координаты $(2,1)$. Поверните её на 90° против часовой стрелки вокруг начала координат. "
    "Затем тем же способом поверните три вершины треугольника, записанные в таблице по строкам.</p>"
    + eq(r"R=\begin{pmatrix}0&-1\\1&0\end{pmatrix}.",
         r"$R$ — матрица поворота на 90° против часовой стрелки; входной вектор в математической записи — столбец.")
    + "<ol><li>До запуска кода предскажите, в какой четверти окажется точка.</li>"
      "<li>Вычислите новые координаты одной точки с помощью матрицы $R$.</li>"
      "<li>Поверните все вершины одним матричным умножением. Учтите, что в таблице точки стоят по строкам.</li>"
      "<li>По графику объясните, изменились ли форма треугольника и расстояния его вершин до начала координат.</li></ol>")

code('''R_task = np.array([[0, -1], [1, 0]])
point_task = np.array([2, 1])
triangle_task = np.array([[1, 0], [3, 0], [1, 2]])

# TODO: Apply the rotation to one vector.
rotated_point = ...

# TODO: Rotate the whole table, with observations stored in rows.
rotated_triangle = ...''', ("student-core", "task-rotation"))

code('''# Provided: draw the result after the calculation is completed.
if rotated_point is Ellipsis or rotated_triangle is Ellipsis:
    print("Сначала заполните расчёт поворота выше.")
else:
    rotated_point = np.asarray(rotated_point)
    rotated_triangle = np.asarray(rotated_triangle)
    if rotated_point.shape != (2,) or rotated_triangle.shape != (3, 2):
        print("Проверьте формы: точка — (2,), таблица вершин — (3, 2).")
    else:
        fig, ax = plt.subplots(figsize=(5, 5))
        for vertices, color, label in [(triangle_task, "#438dd1", "До поворота"),
                                        (rotated_triangle, "#318b62", "После поворота")]:
            closed = np.vstack([vertices, vertices[0]])
            ax.plot(closed[:, 0], closed[:, 1], "o-", color=color, label=label)
        ax.scatter(*point_task, marker="x", s=80, color="#438dd1")
        ax.scatter(*rotated_point, marker="x", s=80, color="#318b62")
        ax.axhline(0, color="gray", linewidth=0.7)
        ax.axvline(0, color="gray", linewidth=0.7)
        ax.set(xlim=(-4, 4), ylim=(-4, 4), xlabel="Первая координата", ylabel="Вторая координата",
               title="Треугольник и отдельная точка (крестик)")
        ax.set_aspect("equal")
        ax.grid(alpha=0.25)
        ax.legend()
        plt.show()
        print("Координаты точки после поворота:", rotated_point)''', ("provided", "task-output"))

md("**Ваш вывод:** почему в расчёте для таблицы понадобилось транспонирование?\n\n_Ответ: …_", ("interpretation",))

md("### Задача 2. Оценить стоимость автомобиля")
theory("Условие — признаки и их веса",
    "<p>Есть четыре вымышленных автомобиля. Оценим их стоимость по готовой формуле. "
    "<b>Все цены выражены в тысячах сомов</b>, а пробег — в тысячах километров. "
    "Например, число 45 в столбце пробега означает 45 000 км.</p>"
    + "<table><tr><th>Столбец</th><th>Что записано</th><th>Вес</th><th>Смысл веса</th></tr>"
      "<tr><td>0</td><td>Постоянное число 1</td><td>1000</td><td>Добавляет к каждой оценке базовую часть 1000 тыс. сомов.</td></tr>"
      "<tr><td>1</td><td>Объём двигателя, л</td><td>300</td><td>Каждый дополнительный литр увеличивает оценку на 300 тыс. сомов.</td></tr>"
      "<tr><td>2</td><td>Возраст, лет</td><td>−70</td><td>Каждый дополнительный год уменьшает оценку на 70 тыс. сомов.</td></tr>"
      "<tr><td>3</td><td>Пробег, тыс. км</td><td>−2</td><td>Каждые дополнительные 1000 км уменьшают оценку на 2 тыс. сомов.</td></tr></table>"
    + "<p>Смысл каждого изменения описан <b>при неизменных остальных признаках</b>. "
      "Это условные коэффициенты учебной формулы, а не результат исследования рынка. Подбирать или обучать их не нужно.</p>"
    + eq(r"\widehat p=1\cdot w_0+v\cdot w_1+a\cdot w_2+d\cdot w_3.",
         r"$\widehat p$ — оценка цены в тыс. сомов; $v$ — объём двигателя в литрах; "
         r"$a$ — возраст в годах; $d$ — пробег в тыс. км; "
         r"$w_0=1000$, $w_1=300$, $w_2=-70$, $w_3=-2$ — веса в порядке столбцов таблицы.")
    + "<ol><li>Посчитайте цену первого автомобиля через произведения признаков на их веса и сумму.</li>"
      "<li>Вычислите цены всех автомобилей одним умножением матрицы на вектор.</li>"
      "<li>Объясните, почему первая колонка состоит из единиц.</li>"
      "<li>Как изменится оценка, если пробег увеличится на 10 000 км? Ответьте сначала без пересчёта всей таблицы.</li></ol>"
    + box("Связь с линейной комбинацией", "Для одной машины мы складываем взвешенные значения признаков. "
          "Для всей таблицы вектор цен — линейная комбинация <b>столбцов</b> матрицы данных; коэффициентами служат веса."))

code('''# Provided: synthetic features and fixed coefficients.
X_cars = np.array([[1, 1.6, 3, 45],
                   [1, 2.0, 5, 90],
                   [1, 2.5, 2, 30],
                   [1, 1.8, 8, 140]])
w_price = np.array([1000, 300, -70, -2])
car_names = ["Авто A", "Авто B", "Авто C", "Авто D"]
cars_table = pd.DataFrame(X_cars, index=car_names,
                         columns=["Константа", "Объём, л", "Возраст, лет", "Пробег, тыс. км"])
display(cars_table)

# TODO: Calculate the first price as a sum of weighted feature values.
first_car_price = ...

# TODO: Calculate all prices with one matrix-vector product.
car_prices = ...''', ("student-core", "task-car-price"))

code('''# Provided: show student results, without supplying the calculation.
if first_car_price is Ellipsis or car_prices is Ellipsis:
    print("Сначала заполните два расчёта стоимости выше.")
elif np.asarray(car_prices).shape != (4,):
    print("Ожидаем четыре цены: проверьте форму результата (4,).")
else:
    display(cars_table.assign(**{"Оценка, тыс. сомов": car_prices}))
    print("Первый автомобиль, отдельный расчёт:", first_car_price)
    print("Отдельный расчёт совпал с первой ценой:", np.isclose(first_car_price, car_prices[0]))''', ("provided", "task-output"))

md("**Ваш вывод:** что означают положительные и отрицательные веса? Какую роль играет столбец единиц?\n\n_Ответ: …_", ("interpretation",))

md("### Задача 3. Две формулы цены одним умножением")
theory("Условие — каждый столбец весов задаёт свою формулу",
    "<p>Второй оценщик использует другие коэффициенты: базовая часть — 900, вес объёма — 350, "
    "вес возраста — −60, вес пробега — −3. Единицы измерения те же, что в предыдущей задаче.</p>"
    + "<p>Соберём две формулы в одну матрицу весов. В <b>первом столбце</b> — веса первого оценщика, "
      "во <b>втором</b> — второго; строки идут в порядке признаков.</p>"
    + eq(r"W=\begin{pmatrix}1000&900\\300&350\\-70&-60\\-2&-3\end{pmatrix}.",
         r"$W$ — матрица из четырёх строк и двух столбцов; строки соответствуют константе, "
         r"объёму двигателя, возрасту и пробегу; столбцы — двум формулам цены.")
    + "<ol><li>До вычислений определите форму результата: четыре автомобиля, две оценки для каждого.</li>"
      "<li>Получите все оценки одним матричным умножением.</li>"
      "<li>Проверьте, совпал ли первый столбец результата с ценами из задачи 2.</li>"
      "<li>Для какого автомобиля второй оценщик даёт более высокую цену? "
      "Объясните это через признаки автомобиля и различия весов.</li></ol>")

code('''W_prices = np.array([[1000, 900],
                     [300, 350],
                     [-70, -60],
                     [-2, -3]])

# TODO: Apply both sets of weights to every car with one matrix product.
two_price_estimates = ...''', ("student-core", "task-two-prices"))

code('''# Provided: format the two columns of calculated prices.
if two_price_estimates is Ellipsis:
    print("Сначала заполните матричное умножение выше.")
elif np.asarray(two_price_estimates).shape != (4, 2):
    print("Проверьте форму результата: четыре автомобиля × два оценщика.")
else:
    display(pd.DataFrame(two_price_estimates, index=car_names,
                         columns=["Оценщик 1, тыс. сомов", "Оценщик 2, тыс. сомов"]))
    if car_prices is not Ellipsis and np.asarray(car_prices).shape == (4,):
        print("Первый столбец совпал с задачей 2:", np.allclose(two_price_estimates[:, 0], car_prices))''', ("provided", "task-output"))

md("**Ваш вывод:** что означает одна строка результата? Что означает один столбец?\n\n_Ответ: …_", ("interpretation",))

md("### Задача 4. Небольшая нейросеть: понравится ли парень?")
theory("Условие — три признака и одно решение",
    "<p>Некоторая прекрасная леди выбирает себе парня. В этой вымышленной задаче её предпочтения "
    "описываются небольшой нейросетью с уже заданными весами.</p>"
    + "<p>На вход подаются три признака, строго в таком порядке:</p>"
    + "<ol><li><b>Недвижимость:</b> 1 — есть, 0 — нет.</li>"
      "<li><b>Рок-музыка:</b> 1 — любит рок, 0 — не любит.</li>"
      "<li><b>Внешность:</b> 1 — считает парня привлекательным, 0 — нет.</li></ol>"
    + "<p>На выходе одно число: <b>1 — парень понравился, 0 — не понравился</b>. "
      "Требуется написать алгоритм, который вычисляет это решение по схеме.</p>")

network_image()

theory("Как читать схему: сумма, порог, следующий слой",
    definition("Нейрон и вес", "<p><b>Искусственный нейрон</b> в этой задаче — вычислительный узел, "
        "который сначала складывает входящие сигналы с заданными весами, затем применяет к сумме функцию активации. "
        "<b>Вес</b> — числовой коэффициент на стрелке: он умножается на сигнал, проходящий по этой стрелке.</p>")
    + "<p><b>Нейросеть</b> объединяет такие узлы: выходы одних нейронов становятся входами других.</p>"
    + "<p>Три значка слева только передают значения признаков. Два кружка посередине — "
      "<b>скрытый слой</b>: промежуточные нейроны, результаты которых поступают следующему нейрону. "
      "Кружок справа — <b>выходной нейрон</b>, который выдаёт итоговое решение.</p>"
    + eq(r"s=\sum_{i=1}^{n}w_i u_i.",
         r"$s$ — взвешенная сумма внутри нейрона; $u_i$ — его $i$-й входящий сигнал; "
         r"$w_i$ — вес этого сигнала; $n$ — число входов; $\sum$ означает сумму по всем входам. "
         r"У скрытого нейрона три входа, у выходного — два.")
    + definition("Пороговая функция активации", "<p><b>Функция активации</b> преобразует взвешенную сумму в выходной сигнал нейрона. "
        "Здесь у всех трёх нейронов одна и та же пороговая функция:</p>"
        + eq(r"f(s)=\begin{cases}1,&s\ge0.5,\\0,&s<0.5.\end{cases}",
             r"$s$ — взвешенная сумма; $f(s)$ — выход нейрона, 0 или 1; $0.5$ — порог."))
    + box("На границе", "Если сумма равна ровно <b>0,5</b>, нейрон выдаёт <b>1</b>. "
          "Порог применяется после взвешенной суммы в каждом нейроне. "
          "На выходной нейрон поступают уже нули и единицы скрытого слоя.", "warn")
    + "<p>Веса на схеме уже заданы, дополнительных слагаемых нет. "
      "Нужно только выполнить расчёт слева направо; обучение нейросети в эту задачу не входит.</p>")

theory("Что нужно реализовать",
    "<ol><li>Напишите <code>activation(s)</code>: функция должна применять заданный порог "
    "и к одному числу, и к каждому элементу массива.</li>"
    "<li>По картинке заполните матрицу <code>W_hidden</code> размера <b>2 × 3</b>. "
    "Первая строка — веса верхнего скрытого нейрона, вторая — нижнего. "
    "Столбцы: недвижимость, рок, внешность.</li>"
    "<li>В функции <code>choose_partner(x)</code> одним матричным умножением получите две суммы скрытого слоя. "
    "Примените к ним порог.</li>"
    "<li>Посчитайте взвешенную сумму выходного нейрона по двум полученным сигналам и весам −1 и 1. "
    "Ещё раз примените порог и верните итоговые 0 или 1.</li>"
    "<li>Проверьте все восемь комбинаций признаков с помощью подготовленной таблицы.</li></ol>"
    + box("Подсказка по NumPy", "Сравнение массива с числом выполняется поэлементно и даёт <code>True</code> или <code>False</code>. "
          "Метод <code>.astype(int)</code> переводит эти значения в 1 или 0. "
          "<code>np.asarray(s)</code> позволяет одинаково начать обработку числа и массива."))

code('''def activation(s):
    # TODO: Apply the threshold elementwise; equality must produce one.
    return ...


# TODO: Read the six hidden-layer weights from the picture.
# Rows: upper and lower neurons. Columns: property, rock, appearance.
W_hidden = ...
w_output = np.array([-1, 1])


def choose_partner(x):
    # TODO: Calculate both hidden weighted sums with one matrix-vector product.
    hidden_sums = ...
    # TODO: Apply the threshold to both hidden neurons.
    hidden_outputs = ...
    # TODO: Calculate the output neuron's weighted sum.
    output_sum = ...
    # TODO: Apply the threshold once more and return the final decision.
    result = ...
    return result''', ("student-core", "task-network"))

code('''# Provided: inspect the threshold boundary and all possible binary inputs.
from itertools import product

boundary_inputs = np.array([0.49, 0.5, 0.51])
boundary_outputs = activation(boundary_inputs)
if boundary_outputs is Ellipsis:
    print("Сначала напишите функцию activation.")
else:
    print("Проверка порога: входы", boundary_inputs, "→ выходы", boundary_outputs)

candidate_inputs = np.array(list(product([0, 1], repeat=3)))
if W_hidden is Ellipsis:
    print("Сначала заполните веса скрытого слоя по рисунку.")
else:
    decisions = [choose_partner(row) for row in candidate_inputs]
    if any(value is Ellipsis for value in decisions):
        print("Сначала допишите функцию choose_partner.")
    elif any(np.asarray(value).shape != () for value in decisions):
        print("Функция должна возвращать одно число для одного набора признаков.")
    elif any(value not in (0, 1) for value in decisions):
        print("Ожидаем только 0 или 1. Проверьте применение порога в выходном нейроне.")
    else:
        result_table = pd.DataFrame(candidate_inputs, columns=["Недвижимость", "Рок", "Внешность"])
        result_table["Понравился"] = np.asarray(decisions, dtype=int)
        display(result_table)''', ("provided", "task-output"))

md("""**Объясните результат**

1. Для входа `x = [0, 1, 1]` посчитайте вручную обе суммы скрытого слоя, его выходы и решение выходного нейрона.
   Где в этом расчёте важно условие «больше **или равно** 0,5»?
2. Что делает отрицательный вес −1 перед выходным нейроном?
3. Почему выходному нейрону нужно передавать результаты активации, а не исходные суммы скрытого слоя?

_Ваш ответ: …_
""", ("interpretation",))

md("""**Источники и повторение**

- [Занятие 1: векторы и линейные комбинации](01_vectors.ipynb).
- [Занятие 2: скалярное произведение](02_dot_product.ipynb).
- [3Blue1Brown: геометрический смысл матриц](https://www.3blue1brown.com/lessons/linear-transformations/).
- [3Blue1Brown: умножение как последовательность преобразований](https://www.3blue1brown.com/lessons/matrix-multiplication/).
- [NumPy: поведение `np.dot` для разных форм массивов](https://numpy.org/doc/stable/reference/generated/numpy.dot.html).
- [NumPy: `np.matmul` и оператор `@`](https://numpy.org/doc/stable/reference/generated/numpy.matmul.html).
- [Davis: источник шести наблюдений, закреплённая версия](https://huggingface.co/datasets/aiacademy-kg/davis_dataset/tree/cfb0d88e0d0a8814998ecfb36179bd18d0cbbb5a).
""")

nb = nbf.v4.new_notebook(cells=cells, metadata=json.loads(json.dumps(META)))
nb.metadata["colab"]["name"] = "10_matrices.ipynb"
nb.metadata["lesson"] = {
    "number": 10, "duration_minutes": 120,
    "format": "Shared dark HTML theory, self-contained SVG/JS widgets, worked NumPy examples.",
    "source": "build_lesson10.py + embedded lesson10_widgets.js",
    "prerequisites": ["01_vectors.ipynb", "02_dot_product.ipynb"],
    "data_revision": "cfb0d88e0d0a8814998ecfb36179bd18d0cbbb5a",
    "practice": "Four student tasks for classroom practice or homework; separate from the two-hour theory block.",
    "student_code_tags": ["student-core"],
    "image_source": "images/lesson10_threshold_network.png (instructor-supplied image, embedded attachment)",
}
for index, cell in enumerate(nb.cells):
    cell.id = hashlib.sha256(f"lesson10-{index}-{cell.source}".encode()).hexdigest()[:12]
nbf.validate(nb)
path = HERE / "10_matrices.ipynb"
nbf.write(nb, path)
print(f"Wrote {path.name}: {len(cells)} cells; standalone HTML/JS lesson")
