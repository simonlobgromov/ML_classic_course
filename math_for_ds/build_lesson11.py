"""Build the standalone linear dependence and rank lesson with HTML theory and JS/SVG visuals."""
from pathlib import Path
import hashlib
import json
import nbformat as nbf
from theme import SETUP, META

HERE = Path(__file__).resolve().parent
WIDGET_JS = (HERE / "lesson11_widgets.js").read_text(encoding="utf-8")
cells = []


def md(source, tags=()):
    cells.append(nbf.v4.new_markdown_cell(source.strip(), metadata={"tags": list(tags)}))


def code(source, tags=("provided", "example")):
    cells.append(nbf.v4.new_code_cell(source.strip(), metadata={"tags": list(tags)}))


def eq(formula, meanings):
    """Require a glossary for every displayed equation."""
    if not meanings:
        raise ValueError("An equation needs a glossary")
    return ("<div class='d11-equation'>$$" + formula + "$$</div>"
            + "<div class='where'><b>Обозначения.</b> " + meanings + "</div>")


def box(title, body, kind="idea"):
    return f'<div class="box {kind}"><div class="t">{title}</div>{body}</div>'


def definition(title, body):
    return box(title, body, "def")


def theory(title, body):
    code(f'#@title {title} {{ display-mode: "form" }}\n'
         + 'display(HTML(lesson11_viz(' + repr(body) + ')))', ("provided", "theory"))


def widget(kind, title, instruction, question, data="None"):
    body = (f'<div class="widget"><div class="widget-title">{title}</div>'
            + f'<p class="widget-sub">{instruction}</p><div data-stage></div>'
            + '<div class="readout" data-readout role="status" aria-live="polite"></div>'
            + f'<p class="d11-question"><b>Проверь себя.</b> {question}</p>'
            + '<p class="d11-footnote">Интерактивная иллюстрация. Изменения здесь не меняют переменные в Python.</p></div>')
    code(f'#@title Интерактив — {title} {{ display-mode: "form" }}\n'
         + 'display(HTML(lesson11_viz(' + repr(body) + ', widget=' + repr(kind)
         + ', data=' + data + ')))', ("provided", "interactive"))


md(r"""
# Сколько независимых столбцов в матрице?
## Занятие 11 — линейная зависимость и ранг

В прошлом занятии мы вычисляли произведение матрицы на вектор. Теперь разберёмся,
почему добавление нового столбца не всегда добавляет новую возможность для вычислений.

Путь занятия: **линейная комбинация → зависимость векторов → ранг матрицы → смысл для данных**.
Увидим, как матрица может превратить плоскость в прямую, и что означает слово «вырожденная».

Занятие рассчитано на одну встречу. Все данные — небольшие учебные примеры.
Запускайте ячейки по порядку: сначала сделайте предположение, затем проверьте его на графике и в NumPy.
В конце — три короткие задачи для закрепления.

Теория оформлена в свёрнутых HTML-ячейках; примеры Python открыты.
Код интерактивов встроен в ноутбук, скачивать данные не нужно. Интернет нужен для загрузки формул MathJax.
""")

EXTRA_SETUP = r'''
import json
import uuid
import re
from html import escape

D11_CSS = r"""
.vec-root .d11-controls{display:flex;flex-wrap:wrap;gap:12px 24px;margin:16px 0 22px;font-family:system-ui,sans-serif;}
.vec-root .d11-control{display:flex;align-items:center;flex-wrap:wrap;gap:8px;color:var(--ink);font-size:14px;min-height:36px;}
.vec-root .d11-control input[type=range]{width:155px;min-height:30px;}
.vec-root .d11-control output{font-variant-numeric:tabular-nums;color:var(--green);min-width:42px;}
.vec-root .d11-control select{max-width:100%;padding:8px;}
.vec-root .d11-control input:disabled{opacity:.3;}
.vec-root .d11-charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,380px),1fr));gap:16px;}
.vec-root .d11-charts svg{display:block;width:100%;height:auto;background:#0e1319;border-radius:10px;}
.vec-root .d11-charts svg:last-child:nth-child(3){grid-column:1/-1;max-width:780px;justify-self:center;}
.vec-root .readout{overflow-wrap:anywhere;font:15px/1.75 system-ui,sans-serif;}
.vec-root .d11-question{font-family:system-ui,sans-serif;font-size:14px;color:var(--ink);}
.vec-root .d11-footnote{font-family:system-ui,sans-serif;font-size:12px;color:var(--soft);}
.vec-root .d11-equation{overflow-x:auto;overflow-y:hidden;padding:5px 0;}
.vec-root .where{line-height:1.7;}
.vec-root .d11-table{overflow-x:auto;}
.vec-root button:disabled{opacity:.45;cursor:wait;}
.vec-root .d11-controls .btn{min-height:38px;}
.vec-root input:focus-visible,.vec-root select:focus-visible,.vec-root button:focus-visible{outline:2px solid #e0b25a;outline-offset:4px;}
@media(max-width:600px){.vec-root .wrap{padding:14px;font-size:16px;}.vec-root .widget{padding:10px;}.vec-root .d11-control{width:100%;}}
"""

def lesson11_viz(body, widget=None, data=None):
    """Scope controls to a fresh root so rerunning cells keeps widgets independent."""
    # HTML is parsed before MathJax. Protect comparisons and ampersands in both
    # display equations and inline symbol glossaries without escaping HTML tags.
    body = re.sub(
        r"(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$.*?(?<!\\)\$",
        lambda match: escape(match.group(0), quote=False),
        body,
        flags=re.DOTALL,
    )
    root_id = "d11_" + uuid.uuid4().hex
    script = D11_WIDGET_JS + "\n" + r"""
    (function(){
      const root = document.getElementById(__ROOT__);
      const widget = __WIDGET__;
      if (widget) window.RankLesson11.mount(root, widget, __DATA__);
      const typeset = () => window.MathJax.typesetPromise([root]);
      if (!window.__D11_MATH_READY__) {
        if (window.MathJax && window.MathJax.typesetPromise) {
          window.__D11_MATH_READY__ = window.MathJax.startup.promise;
        } else {
          window.MathJax = {tex:{inlineMath:[['$','$']],displayMath:[['$$','$$']]},svg:{fontCache:'local'},startup:{typeset:false}};
          window.__D11_MATH_READY__ = new Promise((resolve, reject) => {
            const loader = document.createElement('script');
            loader.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
            loader.onload = () => window.MathJax.startup.promise.then(resolve, reject);
            loader.onerror = reject;
            document.head.appendChild(loader);
          });
        }
      }
      window.__D11_MATH_READY__ = window.__D11_MATH_READY__.then(typeset).catch(() => {
        if(root.querySelector('.d11-equation')) {
          const notice = document.createElement('p');
          notice.textContent = 'Для отображения формул подключитесь к интернету и перезапустите ячейку. Графики работают без загрузки MathJax.';
          root.appendChild(notice);
        }
      });
    })();
    """.replace("__ROOT__", json.dumps(root_id)).replace("__WIDGET__", json.dumps(widget)).replace("__DATA__", json.dumps(data, ensure_ascii=False))
    return ("<style>" + CSS + D11_CSS + "</style>"
            + '<div class="vec-root" data-widget="' + (widget or "theory") + '" id="' + root_id + '"><div class="wrap wide">'
            + body + '</div></div><script>' + script + '</script>')

print("Занятие 11 готово: графики работают в браузере; формулы загружаются через MathJax.")'''

code(SETUP + "\n\nD11_WIDGET_JS = " + repr(WIDGET_JS) + "\n" + EXTRA_SETUP + "\nimport numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt", ("provided", "setup"))

md("## 1. Три столбца — сколько разных величин?")
theory("Начнём с таблицы",
    "<p>В таблице записано число доставок за четыре дня: утром, вечером и за весь день. "
    "Последний столбец вычислен из первых двух. Можно удалить его и затем точно восстановить.</p>"
    + box("Вопрос занятия", "Какое наибольшее число столбцов можно выбрать, чтобы ни один из выбранных не получался из других умножением на числа и сложением?"))

code('''# Synthetic counts for four days.
X = np.array([[1, 2, 3],
              [2, 1, 3],
              [1, 3, 4],
              [3, 2, 5]])
names = ["Утро", "Вечер", "Весь день"]
display(pd.DataFrame(X, columns=names, index=["День 1", "День 2", "День 3", "День 4"]))
print("Третий столбец равен сумме первых двух:",
      np.array_equal(X[:, 2], X[:, 0] + X[:, 1]))''')

theory("Столбец тоже является вектором",
    "<p>Одна строка — один день с тремя признаками. Один столбец — один признак, измеренный за четыре дня. "
    "В этом занятии мы в основном сравниваем <b>столбцы</b>, поэтому каждый такой вектор содержит четыре числа.</p>"
    + eq(r"c_3=c_1+c_2.",
         r"$c_1$ — столбец «Утро»; $c_2$ — «Вечер»; $c_3$ — «Весь день». Равенство выполняется сразу для всех четырёх строк.")
    + "<p>В NumPy <code>X[:, 0]</code> означает: взять все строки первого столбца. "
      "Знак <code>:</code> выбирает все элементы вдоль этой оси.</p>")

md("## 2. Вспомним линейную комбинацию")
theory("Как получить новый вектор из нескольких",
    definition("Линейная комбинация · linear combination",
        "<p><b>Линейная комбинация</b> векторов — сумма этих векторов, умноженных на числа. "
        "Числа называют <b>коэффициентами</b>. Они могут быть положительными, отрицательными и нулевыми.</p>"
        + eq(r"v=\alpha_1v_1+\alpha_2v_2+\cdots+\alpha_kv_k.",
             r"$v_1,\ldots,v_k$ — исходные векторы с одинаковым числом координат; $k$ — число векторов; "
             r"$\alpha_1,\ldots,\alpha_k$ — вещественные коэффициенты; $v$ — результат."))
    + "<p>В таблице доставок третий столбец — линейная комбинация первых двух с коэффициентами 1 и 1. "
      "Для геометрии возьмём векторы с двумя координатами: их можно нарисовать на плоскости.</p>")

code('''a = np.array([1, 0])
b = np.array([1, 1])
alpha, beta = -1, 1
result = alpha * a + beta * b
print("Линейная комбинация:", result)''')

md("## 3. Линейная зависимость и независимость")
theory("Когда один вектор можно получить из остальных",
    "<p>Если второй вектор равен первому, их комбинации остаются на одной прямой. "
    "Если второй направлен в сторону от этой прямой, комбинациями двух векторов можно получить любую точку плоскости.</p>"
    + "<p><b>Нулевой вектор</b> — вектор, все координаты которого равны нулю.</p>"
    + definition("Линейная зависимость · linear dependence",
        "<p>Векторы <b>линейно зависимы</b>, если существуют коэффициенты, <b>не все равные нулю</b>, "
        "при которых их линейная комбинация равна нулевому вектору.</p>"
        + eq(r"\alpha_1v_1+\cdots+\alpha_kv_k=\mathbf0,\qquad\text{хотя бы одно }\alpha_i\ne0.",
             r"$v_1,\ldots,v_k$ — проверяемые векторы с одинаковым числом координат; $\alpha_1,\ldots,\alpha_k$ — коэффициенты; "
             r"$\mathbf0$ — нулевой вектор с тем же числом координат; $i$ — номер коэффициента."))
    + definition("Линейная независимость · linear independence",
        "<p>Векторы <b>линейно независимы</b>, если их линейная комбинация равна нулевому вектору "
        "<b>только тогда, когда все коэффициенты равны нулю</b>.</p>")
    + box("Как читать определение",
        "<p>Умножить все векторы на ноль и получить ноль можно всегда. Это ничего не говорит о зависимости. "
        "Поэтому мы ищем другой способ получить нулевой вектор.</p>"
        "<p>Для набора из двух и более векторов зависимость означает: хотя бы один вектор можно выразить "
        "через остальные линейной комбинацией. Например, перенести третий столбец нашей таблицы в левую часть:</p>"
        + eq(r"1\cdot c_1+1\cdot c_2-1\cdot c_3=\mathbf0.",
             r"$c_1,c_2,c_3$ — столбцы таблицы доставок; $\mathbf0$ — вектор из четырёх нулей. "
             "Коэффициенты 1, 1 и −1 не равны нулю.")))

theory("Что видно на плоскости",
    "<ul><li>Два ненулевых вектора на одной прямой через начало координат зависимы. "
    "Они могут смотреть в одну сторону или в противоположные.</li>"
    "<li>Два вектора, которые не лежат на одной такой прямой, независимы. "
    "Перпендикулярность для этого не требуется.</li>"
    "<li>Любой набор с нулевым вектором зависим: перед ним можно поставить коэффициент 1, перед остальными — 0.</li></ul>"
    + definition("Линейная оболочка · span",
        "<p><b>Линейная оболочка</b> набора векторов — множество всех их линейных комбинаций. "
        "Коэффициенты могут принимать любые вещественные значения.</p>")
    + "<p>Для двух независимых векторов на плоскости оболочка — вся плоскость. "
      "Для двух зависимых, хотя бы один из которых ненулевой, — прямая через начало координат. "
      "Если оба нулевые — только начало координат.</p>")

widget("span", "Какие точки можно получить?",
       "Ползунок t меняет вторую координату вектора b = (1, t). Вектор a = (1, 0) остаётся на месте. "
       "Ползунки λ и μ задают коэффициенты комбинации λa + μb. Сравните t = 1 и t = 0. "
       "Серые точки — лишь часть комбинаций с ограниченными коэффициентами; оболочка этим участком не ограничена.",
       "При t = 0 получится ли достичь точки (0, 1), если разрешить любые коэффициенты? "
       "Изменится ли ответ при t = 1?")

code('''# A nonzero set of coefficients is enough to demonstrate dependence.
a = np.array([1, 0])
b_dependent = np.array([2, 0])
b_independent = np.array([1, 1])
print("Для зависимой пары 2a − b:", 2 * a - b_dependent)
print("Для другой пары те же коэффициенты дают:", 2 * a - b_independent)''')

theory("Что доказывает эта проверка",
    "<p>В первой строке найден нулевой вектор с коэффициентами 2 и −1: этого достаточно для зависимости. "
    "Во второй строке проверена только одна пара коэффициентов. Неудачная попытка получить ноль ещё не доказывает независимость.</p>"
    + box("Почему вторая пара всё же независима",
        "У вектора a вторая координата равна 0, у b — 1. Чтобы комбинация дала ноль по второй координате, "
        "коэффициент перед b должен быть нулевым. Тогда для нуля по первой координате нужен и нулевой коэффициент перед a.")
    + box("Два разных смысла слова «независимость»",
        "Здесь речь о <b>линейной независимости векторов</b>. Это не определение статистической независимости случайных величин.", "warn"))

md("## 4. Ранг: сколько независимых столбцов можно выбрать?")
theory("Определение ранга",
    definition("Ранг матрицы · matrix rank",
        "<p><b>Ранг матрицы</b> — наибольшее число её линейно независимых столбцов. "
        "То же число получится, если искать наибольшее число линейно независимых строк.</p>"
        + eq(r"r=\operatorname{rank}(A),\qquad 0\le r\le\min(m,n).",
             r"$A$ — матрица размера $m\times n$; $m$ — число строк, $n$ — число столбцов; "
             r"$r$ — ранг; $\min(m,n)$ — меньшее из чисел $m$ и $n$."))
    + "<p>В таблице доставок первые два столбца независимы: один не является числом, умноженным на другой. "
      "Третий равен их сумме. Поэтому можно выбрать два независимых столбца, но нельзя выбрать три: <b>ранг равен 2</b>.</p>"
    + box("Зависимость бывает между тремя и более столбцами",
        "В нашей таблице никакие два столбца не пропорциональны. При этом все три вместе зависимы. "
        "Проверки только на одинаковые или пропорциональные пары недостаточно."))

code('''print("Размер:", X.shape)
print("Ранг:", np.linalg.matrix_rank(X))
print("Ранг первых двух столбцов:", np.linalg.matrix_rank(X[:, :2]))
print("Ранг после транспонирования:", np.linalg.matrix_rank(X.T))''')

widget("columns", "Добавили столбец — увеличился ли ранг?",
       "Выбирайте столбцы галочками. Сначала оставьте «Утро», затем добавьте «Вечер» и «Весь день». "
       "После этого измените только итог за первый день: ползунок δ прибавляет число к одной ячейке. "
       "При ненулевой поправке столбец «Весь день» становится условным числовым признаком и уже не означает точную сумму доставок.",
       "Почему добавление третьего столбца при δ = 0 не меняет ранг? "
       "А что происходит с рангом всех трёх столбцов при δ = 1?")

theory("Размер и полный ранг",
    "<p>Размер говорит, сколько чисел расположено по каждой оси матрицы. Ранг говорит о линейной независимости её строк и столбцов.</p>"
    + definition("Полный ранг · full rank",
        "<p>Матрица имеет <b>полный ранг</b>, если её ранг равен меньшему из числа строк и числа столбцов. "
        "Если он меньше, говорят о <b>неполном ранге</b>.</p>")
    + "<ul><li>Ранг равен нулю только у нулевой матрицы.</li>"
      "<li>Матрица с независимыми столбцами имеет ранг, равный числу столбцов.</li>"
      "<li>Если столбцов больше, чем строк, все столбцы независимыми быть не могут. "
      "Например, у матрицы размера 2 × 5 максимальный ранг — 2.</li></ul>"
    + box("Обратите внимание", "Полный ранг не всегда означает независимость всех столбцов. "
          "У матрицы размера 2 × 5 ранг 2 является полным, но пять столбцов всё равно зависимы."))

code('''examples = {
    "Нулевая": np.zeros((2, 3)),
    "Три пропорциональных столбца": np.array([[1, 2, 3], [2, 4, 6]]),
    "Два независимых столбца": np.array([[1, 0], [0, 1], [1, 1]]),
}
for name, matrix in examples.items():
    print(name, "| размер:", matrix.shape, "| ранг:", np.linalg.matrix_rank(matrix))''')

md("## 5. Ранг как число направлений после преобразования")
theory("Умножение на матрицу собирает комбинацию столбцов",
    "<p>В прошлом занятии мы видели: умножение матрицы на вектор — это линейная комбинация столбцов матрицы.</p>"
    + eq(r"Ax=x_1c_1+\cdots+x_nc_n.",
         r"$A$ — матрица с $n$ столбцами; $c_1,\ldots,c_n$ — её столбцы; "
         r"$x$ — входной вектор из $n$ координат; $x_i$ — его $i$-я координата; $Ax$ — выходной вектор.")
    + box("Геометрический смысл ранга",
        "Ранг — число независимых направлений среди всех возможных выходных векторов. "
        "Для матрицы 2 × 2: ранг 2 — выходы заполняют плоскость; ранг 1 — лежат на прямой через начало координат; "
        "ранг 0 — все совпадают с нулевым вектором.")
    + definition("Вырожденная матрица · singular matrix",
        "<p><b>Квадратная матрица называется вырожденной, если её ранг меньше её порядка.</b> "
        "Порядок квадратной матрицы — число её строк, равное числу столбцов. Если ранг равен порядку, матрица невырожденная.</p>"
        + eq(r"A\in\mathbb R^{n\times n}:\qquad A\text{ вырождена}\ \Longleftrightarrow\ \operatorname{rank}(A)<n.",
             r"$A$ — квадратная матрица; $n$ — её порядок; $\mathbb R$ — вещественные числа; "
             r"$\operatorname{rank}(A)$ — ранг; $\Longleftrightarrow$ означает «тогда и только тогда»."))
    + "<p>Для прямоугольных матриц здесь используем слова «полный» и «неполный ранг».</p>")

widget("collapse", "Плоскость, прямая или точка",
       "Переключайте три матрицы. Слева — исходные точки, справа — результаты умножения на матрицу. "
       "Особенно проследите за двумя разными входами u = (1, 0) и v = (0, 1).",
       "При каком преобразовании u и v дают один и тот же результат? "
       "Сможем ли мы по такому результату однозначно узнать, какой из этих двух входов использовался?")

code('''A = np.array([[1, 1], [2, 2]])
u = np.array([1, 0])
v = np.array([0, 1])
print("Ранг:", np.linalg.matrix_rank(A))
print("Разные входы:", u, "и", v)
print("Выходы:", A @ u, "и", A @ v)
print("Выходы совпали:", np.array_equal(A @ u, A @ v))''')

theory("Почему теряется возможность различить входы",
    "<p>Столбцы этой матрицы одинаковы. Поэтому два разных входа дали один результат. "
    "Зная только результат, нельзя определить, какой именно вход был использован.</p>"
    + box("Вырожденность и потеря информации",
        "У вырожденной квадратной матрицы обязательно найдутся разные входные векторы с одинаковым выходом. "
        "Это свойство преобразования, а не ошибка вычислений."))

code('''# Observations are rows: multiply by A.T to transform each point.
grid = np.arange(-2, 3)
points = np.array([(x, y) for x in grid for y in grid])
transformed = points @ A.T
colors = points[:, 0] + 2 * points[:, 1]
fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
for ax, data, title in zip(axes, [points, transformed],
                           ["Входы: часть плоскости", "Выходы: точки на прямой"]):
    ax.scatter(data[:, 0], data[:, 1], c=colors, cmap="viridis", s=65)
    ax.axhline(0, color="gray", lw=0.8)
    ax.axvline(0, color="gray", lw=0.8)
    ax.set(xlim=(-9, 9), ylim=(-9, 9), xlabel="Первая координата",
           ylabel="Вторая координата", title=title)
    ax.set_aspect("equal")
    ax.grid(alpha=0.25)
plt.tight_layout()
plt.show()''')

md("## 6. Зачем это знать при работе с признаками?")
theory("Один объём двигателя, две единицы измерения",
    "<p>Пусть мы записали объём двигателя и в литрах, и в миллилитрах. "
    "Второй столбец в 1000 раз больше первого. Два названия столбцов не делают их линейно независимыми.</p>"
    + "<p>Как в прошлом занятии, посчитаем взвешенную сумму признаков. "
      "Это учебный <b>вклад объёма в оценку цены</b>, а не полная цена машины. Веса заданы заранее.</p>"
    + eq(r"\widehat y=w_{\text{л}}v_{\text{л}}+w_{\text{мл}}v_{\text{мл}},\qquad v_{\text{мл}}=1000v_{\text{л}}.",
         r"$v_{\text{л}}$ и $v_{\text{мл}}$ — один объём в литрах и миллилитрах; "
         r"$w_{\text{л}}$ — вес в тысячах сомов на литр; $w_{\text{мл}}$ — вес в тысячах сомов на миллилитр; "
         r"$\widehat y$ — полученный вклад в цену, в тысячах сомов.")
    + "<p>Проверим два разных набора весов. Первый использует только литры. "
      "Второй использует оба столбца. Получится ли различить их по результатам?</p>")

code('''volume_l = np.array([1.0, 1.5, 2.0, 2.5])
X_car = np.column_stack([volume_l, 1000 * volume_l])
w_a = np.array([300.0, 0.0])
w_b = np.array([-200.0, 0.5])
print("Размер:", X_car.shape, "| ранг:", np.linalg.matrix_rank(X_car))
display(pd.DataFrame({
    "Объём, л": X_car[:, 0], "Объём, мл": X_car[:, 1],
    "Вклад с весами A, тыс. сом": X_car @ w_a,
    "Вклад с весами B, тыс. сом": X_car @ w_b,
}))
print("Вклады совпадают:", np.allclose(X_car @ w_a, X_car @ w_b))''')

theory("Что делает этот код",
    "<p><code>np.column_stack</code> собирает одномерные массивы в столбцы одной матрицы. "
    "<code>X_car @ w_a</code> считает взвешенную сумму для каждой строки. "
    "<code>np.allclose</code> проверяет равенство чисел с небольшим допуском на округление.</p>"
    + box("Одинаковые результаты с разными весами",
        "Из-за зависимости столбцов можно менять веса так, что результаты для всех строк останутся прежними. "
        "Поэтому сами по себе эти результаты не позволяют однозначно определить отдельный вес для литров и для миллилитров."))

widget("weights", "Веса меняются, сумма остаётся",
       "Ползунок t задаёт вес при объёме в миллилитрах. Вес при литрах автоматически меняется по правилу "
       "w_л = 300 − 1000t. Посмотрите, как меняются два отдельных вклада и их сумма. "
       "Результат показан в тысячах сомов.",
       "При t = 0 и t = 0,5 веса разные. Почему итог для каждого автомобиля одинаков? "
       "Какой один столбец можно оставить, чтобы всё ещё вычислять этот вклад в цену?")

theory("Практический вывод и одно ограничение",
    box("Что проверять в таблице", "Ищите столбцы, которые точно выражаются через другие: "
        "дубликаты, разные единицы одной величины, сумму нескольких столбцов. "
        "Прежде чем использовать их вместе, проверьте, нужна ли такая повторная запись.")
    + box("Ранг не измеряет полезность признаков",
        "Высокий ранг не гарантирует хорошего прогноза. Даже случайные числа могут образовать независимые столбцы. "
        "Ранг описывает линейные связи в данной матрице; полезность для задачи нужно оценивать отдельно.", "warn")
    + "<details><summary>Если столбцы почти зависимы</summary>"
      "<p>Линейная зависимость — точное равенство. Небольшое изменение одного элемента может его нарушить "
      "и увеличить математический ранг, хотя столбцы останутся почти повторяющими друг друга.</p>"
      "<p><code>np.linalg.matrix_rank</code> работает с конечной точностью и использует численный допуск: "
      "очень малые отличия могут считаться нулевыми. Поэтому ответ функции на реальных измерениях "
      "нужно рассматривать вместе с масштабом данных и точностью измерений.</p></details>")

md("## 7. Проверим главное")
theory("Три понятия, которые нужно различать",
    box("Линейная зависимость", "Можно получить нулевой вектор линейной комбинацией, у которой не все коэффициенты нулевые.", "take")
    + box("Ранг матрицы", "Наибольшее число независимых столбцов; столько же независимых строк. "
          "Размер матрицы и её ранг — разные характеристики.", "take")
    + box("Вырожденная квадратная матрица", "Ранг меньше числа строк. "
          "Есть разные входы, которые преобразование переводит в один выход.", "take"))

md("""Перед задачами объясните своими словами:

1. Почему три разных, попарно непропорциональных столбца всё-таки могут быть зависимыми?
2. Может ли матрица размера 4 × 3 иметь ранг 4? Что ограничивает её ранг?
3. В интерактиве выберите два разных набора весов с одинаковым итогом. Запишите их и объясните, почему это получилось.
""", ("interpretation",))

md("## 8. Три короткие задачи")
theory("Задача 1. Найдите линейную связь",
    "<p>Ниже заданы три вектора. Подберите два коэффициента, чтобы получить третий из первых двух, "
    "и проверьте результат в NumPy.</p>"
    + eq(r"c=\alpha a+\beta b.",
         r"$a,b,c$ — векторы из ячейки ниже; $\alpha,\beta$ — числа, которые нужно подобрать.")
    + "<p>Затем перенесите всё в левую часть. Какие три коэффициента дают нулевой вектор? "
      "Почему найденная связь доказывает зависимость тройки?</p>")
code('''a_task = np.array([1, 2])
b_task = np.array([2, 1])
c_task = np.array([0, 3])
# TODO: Choose the two coefficients and compute their linear combination.
alpha_task = ...
beta_task = ...
combination_task = ...''', ("student-core", "task-1"))
code('''if combination_task is Ellipsis:
    print("Сначала заполните ячейку задачи 1.")
else:
    print("Полученный вектор:", combination_task)
    print("Целевой вектор:", c_task)
    print("Совпали:", np.allclose(combination_task, c_task))''', ("provided", "task-check"))
md("**Ваше объяснение зависимости:** …", ("interpretation",))

theory("Задача 2. Четыре столбца — какой ранг?",
    "<p>Рассмотрите матрицу ниже. Сначала без вычисления ранга найдите столбцы, которые можно получить "
    "из первых двух. Затем проверьте ранг в NumPy.</p>"
    "<p>Укажите размер, максимально возможный ранг для такого размера и фактический ранг. "
    "Имеет ли эта матрица полный ранг? Объясните ответ через её столбцы.</p>")
code('''C_task = np.array([[1, 0, 1,  2],
                   [0, 1, 1, -1],
                   [1, 1, 2,  1]])
print(C_task)
# TODO: Compute the rank of this matrix.
rank_task = ...''', ("student-core", "task-2"))
code('''if rank_task is Ellipsis:
    print("Сначала заполните ячейку задачи 2.")
else:
    print("Размер:", C_task.shape, "| вычисленный ранг:", rank_task)''', ("provided", "task-check"))
md("**Размер, предел ранга, найденный ранг и связи между столбцами:** …", ("interpretation",))

theory("Задача 3. Разные входы — одинаковый результат?",
    "<p>Вычислите ранг матрицы B и результаты её умножения на два вектора ниже. "
    "Вырождена ли эта матрица? Что произойдёт со всей плоскостью: она останется плоскостью, станет прямой или точкой?</p>"
    "<p>Сопоставьте ответ с двумя вычисленными выходами: какую информацию мы уже не можем восстановить по ним?</p>")
code('''B_task = np.array([[2, -1], [4, -2]])
u_task = np.array([1, 0])
v_task = np.array([2, 2])
# TODO: Compute the matrix rank and the two matrix-vector products.
rank_B_task = ...
Bu_task = ...
Bv_task = ...''', ("student-core", "task-3"))
code('''if any(value is Ellipsis for value in [rank_B_task, Bu_task, Bv_task]):
    print("Сначала заполните ячейку задачи 3.")
else:
    print("Ранг:", rank_B_task)
    print("Первый выход:", Bu_task, "| второй выход:", Bv_task)
    print("Выходы совпали:", np.allclose(Bu_task, Bv_task))''', ("provided", "task-check"))
md("**Вывод о матрице и о возможности различить входы:** …", ("interpretation",))

md("""**Источники и повторение**

- [Занятие 10: матрицы, произведение и преобразования](10_matrices.ipynb).
- [3Blue1Brown: линейные комбинации, оболочка и зависимость](https://www.3blue1brown.com/lessons/span/).
- [3Blue1Brown: геометрия линейных преобразований](https://www.3blue1brown.com/lessons/linear-transformations/).
- [NumPy: вычисление ранга и численный допуск](https://numpy.org/doc/stable/reference/generated/numpy.linalg.matrix_rank.html).

Геометрические примеры и таблицы в этом ноутбуке — учебные, созданные для занятия.
""")

nb = nbf.v4.new_notebook(cells=cells, metadata=json.loads(json.dumps(META)))
nb.metadata["colab"]["name"] = "11_linear_dependence_rank.ipynb"
nb.metadata["lesson"] = {
    "number": 11, "duration_minutes": 120,
    "format": "Shared dark HTML theory, self-contained SVG/JS widgets, worked NumPy examples.",
    "source": "build_lesson11.py + embedded lesson11_widgets.js",
    "prerequisites": ["01_vectors.ipynb", "10_matrices.ipynb"],
    "data": "Small synthetic matrices embedded in the notebook; no downloads.",
    "practice": "Three short student tasks with guarded result cells and interpretation prompts.",
    "student_code_tags": ["student-core"],
}
for index, cell in enumerate(nb.cells):
    cell.id = hashlib.sha256(f"lesson11-{index}-{cell.source}".encode()).hexdigest()[:12]
nbf.validate(nb)
path = HERE / "11_linear_dependence_rank.ipynb"
nbf.write(nb, path)
print(f"Wrote {path.name}: {len(cells)} cells; standalone HTML/JS lesson")
