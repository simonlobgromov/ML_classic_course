"""Build the standalone covariance and correlation lesson with HTML theory and SVG widgets."""
from pathlib import Path
import hashlib
import json
import nbformat as nbf
from theme import SETUP, META
from lesson13_tasks import add_tasks

HERE = Path(__file__).resolve().parent
WIDGET_JS = (HERE / "lesson13_widgets.js").read_text(encoding="utf-8")
cells = []


def md(source, tags=()):
    cells.append(nbf.v4.new_markdown_cell(source.strip(), metadata={"tags": list(tags)}))


def code(source, tags=("provided", "example")):
    cells.append(nbf.v4.new_code_cell(source.strip(), metadata={"tags": list(tags)}))


def eq(formula, meanings):
    """Require a glossary for every displayed equation."""
    if not meanings:
        raise ValueError("An equation needs a glossary")
    return ("<div class='d13-equation'>$$" + formula + "$$</div>"
            + "<div class='where'><b>Обозначения.</b> " + meanings + "</div>")


def box(title, body, kind="idea"):
    return f'<div class="box {kind}"><div class="t">{title}</div>{body}</div>'


def definition(title, body):
    return box(title, body, "def")


def theory(title, body):
    code(f'#@title {title} {{ display-mode: "form" }}\n'
         + 'display(HTML(lesson13_viz(' + repr(body) + ')))', ("provided", "theory"))


def widget(kind, title, instruction, question, data="None"):
    body = (f'<div class="widget"><div class="widget-title">{title}</div>'
            + f'<p class="widget-sub">{instruction}</p><div data-stage></div>'
            + '<div class="readout" data-readout role="status" aria-live="polite"></div>'
            + f'<p class="d13-question"><b>Проверь себя.</b> {question}</p>'
            + '<p class="d13-footnote">Интерактивная иллюстрация. Изменения здесь не меняют переменные в Python.</p></div>')
    code(f'#@title Интерактив — {title} {{ display-mode: "form" }}\n'
         + 'display(HTML(lesson13_viz(' + repr(body) + ', widget=' + repr(kind)
         + ', data=' + data + ')))', ("provided", "interactive"))


EXTRA_SETUP = r'''
import json
import uuid
import re
from html import escape

D13_CSS = r"""
.vec-root .d13-controls{display:flex;flex-wrap:wrap;gap:13px 24px;margin:16px 0 22px;font-family:system-ui,sans-serif;}
.vec-root .d13-control{display:flex;align-items:center;flex-wrap:wrap;gap:8px;color:var(--ink);font-size:14px;min-height:36px;}
.vec-root .d13-control input[type=range]{width:155px;min-height:30px;}
.vec-root .d13-control output{font-variant-numeric:tabular-nums;color:var(--green);min-width:42px;}
.vec-root .d13-control select{max-width:100%;padding:8px;}
.vec-root .d13-control input:disabled{opacity:.3;}
.vec-root .d13-charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,380px),1fr));gap:16px;}
.vec-root .d13-charts svg{display:block;width:100%;height:auto;background:#0e1319;border-radius:10px;}
.vec-root .d13-charts svg:last-child:nth-child(3){grid-column:1/-1;max-width:780px;justify-self:center;}
.vec-root .readout{overflow-wrap:anywhere;font:15px/1.75 system-ui,sans-serif;}
.vec-root .d13-question{font-family:system-ui,sans-serif;font-size:14px;color:var(--ink);}
.vec-root .d13-footnote{font-family:system-ui,sans-serif;font-size:13px;color:var(--soft);}
.vec-root .d13-equation{overflow-x:auto;overflow-y:hidden;padding:5px 0;}
.vec-root .where{line-height:1.7;}
.vec-root .d13-table{overflow-x:auto;}
.vec-root button:disabled{opacity:.45;cursor:wait;}
.vec-root .d13-controls .btn{min-height:38px;}
.vec-root input:focus-visible,.vec-root select:focus-visible,.vec-root button:focus-visible{outline:2px solid #e0b25a;outline-offset:4px;}
@media(max-width:600px){.vec-root .wrap{padding:14px;font-size:16px;}.vec-root .widget{padding:10px;}.vec-root .d13-control{width:100%;}}
"""

def lesson13_viz(body, widget=None, data=None):
    """Scope controls to a fresh root so rerunning cells keeps widgets independent."""
    # HTML is parsed before MathJax. Protect comparisons and ampersands in both
    # display equations and inline symbol glossaries without escaping HTML tags.
    body = re.sub(
        r"(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$.*?(?<!\\)\$",
        lambda match: escape(match.group(0), quote=False),
        body,
        flags=re.DOTALL,
    )
    root_id = "d13_" + uuid.uuid4().hex
    script = D13_WIDGET_JS + "\n" + r"""
    (function(){
      const root = document.getElementById(__ROOT__);
      const widget = __WIDGET__;
      if (widget) window.CorrelationLesson13.mount(root, widget, __DATA__);
      const typeset = () => window.MathJax.typesetPromise([root]);
      if (!window.__D13_MATH_READY__) {
        if (window.MathJax && window.MathJax.typesetPromise) {
          window.__D13_MATH_READY__ = window.MathJax.startup.promise;
        } else {
          window.MathJax = {tex:{inlineMath:[['$','$']],displayMath:[['$$','$$']]},svg:{fontCache:'local'},startup:{typeset:false}};
          window.__D13_MATH_READY__ = new Promise((resolve, reject) => {
            const loader = document.createElement('script');
            loader.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
            loader.onload = () => window.MathJax.startup.promise.then(resolve, reject);
            loader.onerror = reject;
            document.head.appendChild(loader);
          });
        }
      }
      window.__D13_MATH_READY__ = window.__D13_MATH_READY__.then(typeset).catch(() => {
        if(root.querySelector('.d13-equation')) {
          const notice = document.createElement('p');
          notice.textContent = 'Для отображения формул подключитесь к интернету и перезапустите ячейку. Графики работают без загрузки MathJax.';
          root.appendChild(notice);
        }
      });
    })();
    """.replace("__ROOT__", json.dumps(root_id)).replace("__WIDGET__", json.dumps(widget)).replace("__DATA__", json.dumps(data, ensure_ascii=False))
    return ("<style>" + CSS + D13_CSS + "</style>"
            + '<div class="vec-root" data-widget="' + (widget or "theory") + '" id="' + root_id + '"><div class="wrap wide">'
            + body + '</div></div><script>' + script + '</script>')

print("Занятие 13 готово: графики работают в браузере; формулы загружаются через MathJax.")'''

md(r"""
# Как связаны признаки?
## Занятие 13 — ковариация и корреляция

Большие квартиры обычно стоят дороже. Как описать эту связь числом? Почему результат зависит
от единиц измерения? И что значит «корреляция равна нулю»?

Разберём эти вопросы на **синтетических данных**: они созданы специально для занятия и не описывают
рынок недвижимости. Свяжем новые понятия с векторами признаков, скалярным произведением и рангом матрицы.
В конце увидим, как квадрат или синус признака помогает описать нелинейную связь.

Теория и начало практики рассчитаны на одну встречу. В конце — **восемь задач**: пять основных
и три дополнительных. Сначала считайте на бумаге, затем проверяйте в Python. Оставшиеся задачи
можно закончить самостоятельно.

Запускайте ячейки по порядку. Теория и интерактивы находятся в свёрнутых HTML-ячейках,
примеры Python открыты. Все данные и интерактивы встроены; интернет нужен только для формул MathJax.
""")

code(SETUP + "\n\nD13_WIDGET_JS = " + repr(WIDGET_JS) + "\n" + EXTRA_SETUP + '''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr, spearmanr, rankdata

sns.set_theme(style="whitegrid", context="notebook")
np.set_printoptions(precision=3, suppress=True)
''', ("provided", "setup"))

md("## 1. От таблицы к вопросу о связи")
theory("Что будем сравнивать",
    "<p>У каждой учебной квартиры есть площадь, число комнат и цена. Начнём с двух признаков: "
    "площади и цены. <b>Одна точка на графике — одна квартира.</b> Её положение по горизонтали задаёт "
    "площадь, по вертикали — цена.</p>"
    + definition("Вектор признака · feature vector",
        "<p>В этом занятии <b>вектор признака</b> — столбец значений одного признака у всех объектов. "
        "Например, все площади квартир. Его координаты соответствуют разным квартирам.</p>")
    + box("Порядок наблюдений", "Векторы площади и цены должны описывать одни и те же квартиры "
          "в одном порядке. Нельзя независимо отсортировать столбцы: это разрушит пары наблюдений."))

code('''# Generate one reproducible teaching dataset.
rng = np.random.default_rng(13)
n_apartments = 120
area = rng.uniform(25, 120, n_apartments)
rooms = np.clip(np.rint(area / 28 + rng.normal(0, 0.55, n_apartments)), 1, 5).astype(int)
price = 1.2 + 0.075 * area + 0.4 * rooms + rng.normal(0, 0.7, n_apartments)
apartments = pd.DataFrame({
    "Площадь, м²": area,
    "Комнаты": rooms,
    "Цена, млн сом": price,
})
display(apartments.head().round(2))

fig, ax = plt.subplots(figsize=(7, 4))
sns.scatterplot(data=apartments, x="Площадь, м²", y="Цена, млн сом",
                hue="Комнаты", palette="viridis", ax=ax)
ax.set_title("Учебные квартиры: одна точка — один объект")
plt.tight_layout()
plt.show()''')
md("**Посмотрите на график.** Как меняется цена при увеличении площади? "
   "У всех ли квартир одной площади одинаковая цена?", ("discussion",))

md("## 2. Вместе ли меняются признаки?")
theory("Сравним каждое значение со средним",
    "<p>Проведём через облако точек две линии: среднюю площадь и среднюю цену. "
    "Для каждой квартиры запишем два отклонения от средних.</p>"
    + definition("Центрирование · centering",
        "<p><b>Центрировать признак</b> — вычесть его выборочное среднее из каждого значения.</p>"
        + eq(r"x_{c,i}=x_i-\bar x,\qquad y_{c,i}=y_i-\bar y.",
             r"$i$ — номер объекта; $x_i,y_i$ — его значения двух признаков; "
             r"$\bar x,\bar y$ — средние по всем объектам; $x_{c,i},y_{c,i}$ — значения после центрирования. "
             "Буква c напоминает о центрировании."))
    + "<ul><li>Оба отклонения одного знака → их произведение положительно.</li>"
      "<li>Отклонения разных знаков → произведение отрицательно.</li>"
      "<li>Хотя бы одно отклонение равно нулю → произведение равно нулю.</li></ul>"
    + box("Что складываем", "Мы учитываем и знак, и величину произведений отклонений. "
          "Одного подсчёта точек по сторонам от средних недостаточно."))

widget("covariance", "Отклонения и их произведения",
       "Выберите наблюдение и посмотрите на его отклонения в таблице. Затем измените характер связи. "
       "В конце переключите площадь из м² в квадратные футы: сами квартиры остаются теми же.",
       "Какие точки дают положительные слагаемые? Почему смена единиц площади меняет сумму произведений?")

theory("Выборочная ковариация",
    definition("Выборочная ковариация · sample covariance",
        "<p><b>Выборочная ковариация</b> двух признаков — сумма произведений их отклонений от выборочных "
        "средних, делённая на число наблюдений минус один:</p>"
        + eq(r"s_{xy}=\frac{1}{n-1}\sum_{i=1}^{n}(x_i-\bar x)(y_i-\bar y),\qquad n\geq 2.",
             r"$s_{xy}$ — выборочная ковариация; $n$ — число пар наблюдений; $i$ — номер пары; "
             r"$x_i,y_i$ — значения признаков у одного объекта; $\bar x,\bar y$ — выборочные средние; "
             r"$\sum$ означает сложение по всем объектам."))
    + "<p>Положительный результат получается, когда сумма положительных произведений больше "
      "модуля суммы отрицательных. При отрицательном результате — наоборот. "
      "Это способ описать совместное изменение признаков.</p>"
    + box("Единицы измерения", "У ковариации площади и цены единицы <b>м² · млн сом</b>. "
          "По одному её числу нельзя сравнивать силу связей между признаками в разных единицах.")
    + "<details><summary>Ковариация случайных величин</summary>"
    + eq(r"\operatorname{Cov}(X,Y)=\mathbb E[(X-\mathbb E[X])(Y-\mathbb E[Y])].",
         r"$X,Y$ — случайные величины с конечными дисперсиями; $\mathbb E$ — математическое ожидание, "
         "то есть среднее с учётом вероятностей; "
         r"$\operatorname{Cov}(X,Y)$ — ковариация в распределении, из которого получены наблюдения.")
    + "<p>В этом занятии считаем по конечной выборке. Везде используем делитель "
      "$n-1$, как в исправленной выборочной дисперсии. При независимых одинаково распределённых "
      "парах это даёт несмещённую оценку: её среднее по повторным выборкам равно ковариации распределения.</p></details>"
    + box("Нулевой результат", "Нулевая ковариация не доказывает отсутствие зависимости. "
          "Положительные и отрицательные слагаемые могут взаимно сократиться. Ниже увидим пример.", "take"))

theory("Один расчёт целиком",
    "<p>Возьмём три пары значений. Это отдельный небольшой пример, чтобы видеть каждое слагаемое.</p>"
    + "<table><tr><th>Объект</th><th>x</th><th>y</th><th>x − среднее x</th><th>y − среднее y</th>"
      "<th>Произведение</th></tr><tr><td>1</td><td>1</td><td>2</td><td>−1</td><td>−1</td><td>1</td></tr>"
      "<tr><td>2</td><td>2</td><td>4</td><td>0</td><td>1</td><td>0</td></tr>"
      "<tr><td>3</td><td>3</td><td>3</td><td>1</td><td>0</td><td>0</td></tr></table>"
    + eq(r"\bar x=2,\qquad \bar y=3,\qquad s_{xy}=\frac{1+0+0}{3-1}=0.5.",
         r"$\bar x,\bar y$ — средние столбцов; $s_{xy}$ — их выборочная ковариация; "
         "1, 0, 0 — произведения отклонений из последнего столбца; 3 — число объектов."))
code('''x_small = np.array([1., 2., 3.])
y_small = np.array([2., 4., 3.])
xc_small = x_small - x_small.mean()
yc_small = y_small - y_small.mean()
products_small = xc_small * yc_small
cov_small = products_small.sum() / (len(x_small) - 1)

display(pd.DataFrame({"x": x_small, "y": y_small,
                      "Отклонение x": xc_small, "Отклонение y": yc_small,
                      "Произведение": products_small}))
print("По формуле:", cov_small)
print("NumPy:", np.cov(x_small, y_small, ddof=1)[0, 1])''')

md("## 3. Корреляция: убираем зависимость от единиц")
theory("Нормируем ковариацию",
    "<p>Перевод площади в другие единицы увеличивает каждое отклонение в одно и то же число раз. "
    "Ковариация меняется, хотя связь осталась прежней. Разделим её на стандартные отклонения признаков.</p>"
    + eq(r"s_x=\sqrt{\frac{1}{n-1}\sum_{i=1}^{n}(x_i-\bar x)^2},\qquad "
         r"s_y=\sqrt{\frac{1}{n-1}\sum_{i=1}^{n}(y_i-\bar y)^2}.",
         r"$s_x,s_y$ — выборочные стандартные отклонения; $n$ — число объектов; "
         r"$x_i,y_i$ — значения признаков; $\bar x,\bar y$ — их средние. Под корнем — выборочные дисперсии.")
    + definition("Коэффициент корреляции Пирсона · Pearson correlation coefficient",
        "<p><b>Выборочный коэффициент корреляции Пирсона</b> — ковариация двух признаков, "
        "делённая на произведение их стандартных отклонений. Он описывает направление и силу "
        "линейной связи в выборке.</p>"
        + eq(r"r_{xy}=\frac{s_{xy}}{s_xs_y},\qquad s_x>0,\quad s_y>0.",
             r"$r_{xy}$ — коэффициент Пирсона; $s_{xy}$ — выборочная ковариация; "
             r"$s_x,s_y$ — выборочные стандартные отклонения. Все три величины вычислены по одним парам "
             "и с одинаковым делителем $n-1$."))
    + "<ul><li>Коэффициент не имеет единиц измерения и лежит от −1 до 1.</li>"
      "<li>Знак показывает направление линейной связи.</li>"
      "<li>Чем ближе модуль к 1, тем сильнее линейная связь.</li>"
      "<li>Если один признак постоянный, коэффициент не определён: в знаменателе ноль.</li></ul>"
    + box("Что не означает число", "Корреляция 0.8 не означает «80% точек связаны» или «причина объясняет 80% результата». "
          "Это безразмерная мера линейной связи, а не вероятность.", "warn"))
code('''x_area = apartments["Площадь, м²"].to_numpy()
y_price = apartments["Цена, млн сом"].to_numpy()
xc_area = x_area - x_area.mean()
yc_price = y_price - y_price.mean()

cov_area_price = (xc_area * yc_price).sum() / (len(x_area) - 1)
sx_area = x_area.std(ddof=1)
sy_price = y_price.std(ddof=1)
r_manual = cov_area_price / (sx_area * sy_price)
print("Ковариация:", round(cov_area_price, 3), "м² · млн сом")
print("Пирсон по формуле:", round(r_manual, 3))
print("Пирсон в SciPy:", round(pearsonr(x_area, y_price).statistic, 3))

# The input pairs stay in the same order.
x_feet = 10.764 * x_area
print("После перевода площади в футы²:")
print("Ковариация:", round(np.cov(x_feet, y_price, ddof=1)[0, 1], 3), "фут² · млн сом")
print("Пирсон:", round(pearsonr(x_feet, y_price).statistic, 3))''')
theory("Что возвращает SciPy",
    "<p><code>pearsonr(x, y).statistic</code> — значение коэффициента. "
    "Функция возвращает также <code>pvalue</code>, но здесь мы используем только коэффициент "
    "для описания данных. Проверка гипотез о корреляции — отдельная задача со своими условиями.</p>"
    + "<p>Для самого вычисления коэффициента нормальное распределение признаков не требуется. "
      "Нужны парные наблюдения и ненулевой разброс обоих признаков.</p>"
    + box("Смена масштаба и сдвиг", "Прибавление константы не меняет корреляцию. Умножение признака "
          "на положительное число тоже её не меняет; на отрицательное — меняет знак. "
          "Умножение на ноль делает признак постоянным, и коэффициент перестаёт быть определён."))

widget("pearson", "Направление, шум и сдвиг",
       "Сначала уберите шум. Измените наклон, затем добавьте шум. Сдвиг перемещает всё облако "
       "по вертикали. При движении ползунков используется один и тот же набор шумовых отклонений.",
       "Сохраняется ли r при вертикальном сдвиге? Что происходит, если и наклон, и шум равны нулю?")

md("## 4. Корреляция — это угол между векторами")
theory("Возвращаемся к скалярному произведению",
    "<p>Вспомним: <b>скалярное произведение</b> — сумма произведений соответствующих координат двух векторов. "
    "Именно такую сумму мы уже считали для центрированных признаков.</p>"
    + eq(r"s_{xy}=\frac{x_c^\top y_c}{n-1},\qquad "
         r"r_{xy}=\frac{x_c^\top y_c}{\|x_c\|\,\|y_c\|}=\cos\theta.",
         r"$x_c,y_c$ — векторы признаков после вычитания их средних; $n$ — число объектов; "
         r"$\top$ — транспонирование; $x_c^\top y_c$ — скалярное произведение; "
         r"$\|x_c\|,\|y_c\|$ — евклидовы длины векторов; $\theta$ — угол между ними; "
         r"$s_{xy}$ — выборочная ковариация; $r_{xy}$ — Пирсон. Оба вектора должны быть ненулевыми.")
    + "<p>При подстановке стандартных отклонений делители $n-1$ сокращаются. "
      "Получается знакомая формула косинусного сходства.</p>"
    + box("Что изменилось по сравнению с занятием 2", "Для Пирсона мы сначала центрируем каждый "
          "вектор. Косинус между исходными столбцами вообще говоря не равен корреляции.", "take"))

widget("geometry", "Угол между центрированными признаками",
       "Изменяйте угол. На схеме показаны два центрированных вектора после приведения к единичной длине. "
       "Это рисунок в плоскости этих векторов, а не облако из двух наблюдений: в самих векторах может быть много координат.",
       "Какому углу соответствуют r = 1, r = 0 и r = −1? Что означает перпендикулярность для скалярного произведения?")
code('''dot_centered = np.dot(xc_area, yc_price)
r_cosine = dot_centered / (np.linalg.norm(xc_area) * np.linalg.norm(yc_price))
cosine_uncentered = np.dot(x_area, y_price) / (np.linalg.norm(x_area) * np.linalg.norm(y_price))
print("Косинус после центрирования:", round(r_cosine, 3))
print("Пирсон:", round(r_manual, 3))
print("Косинус исходных столбцов:", round(cosine_uncentered, 3))''')

md("## 5. Все пары признаков в одной матрице")
theory("Ковариационная матрица",
    definition("Выборочная ковариационная матрица · sample covariance matrix",
        "<p><b>Ковариационная матрица</b> содержит выборочные ковариации всех пар признаков. "
        "Номера строки и столбца указывают, какую пару сравниваем.</p>")
    + eq(r"S=\frac{1}{n-1}X_c^\top X_c.",
         r"$X$ — матрица данных размера $n\times d$: $n$ объектов в строках, $d$ признаков в столбцах; "
         r"$X_c$ — та же матрица после вычитания среднего из каждого столбца; $\top$ — транспонирование; "
         r"$S$ — ковариационная матрица размера $d\times d$; $n-1$ — делитель выборочной оценки.")
    + r"<p>Элемент произведения $X_c^\top X_c$ — скалярное произведение двух центрированных столбцов. "
      "Значит, уже знакомое матричное умножение считает все нужные суммы сразу.</p>"
    + "<ul><li>На диагонали — дисперсии: признак сравнивается с самим собой.</li>"
      "<li>Вне диагонали — ковариации разных признаков.</li>"
      "<li>Матрица симметрична: перестановка признаков не меняет ковариацию.</li></ul>"
    + box("Сначала центрируем", r"Произведение $X^\top X$ ещё не является ковариационной матрицей. "
          "Сначала центрируем столбцы, затем считаем произведение и делим на число наблюдений минус один.", "warn"))
code('''X = apartments.to_numpy(dtype=float)
X_centered = X - X.mean(axis=0)
S_manual = X_centered.T @ X_centered / (len(X) - 1)
S_numpy = np.cov(X, rowvar=False, ddof=1)
print("Размер матрицы данных:", X.shape)
print("Размер ковариационной матрицы:", S_manual.shape)
print("Два способа совпали:", np.allclose(S_manual, S_numpy))
display(pd.DataFrame(S_manual, index=apartments.columns, columns=apartments.columns).round(3))''')
theory("Матрица корреляций",
    definition("Корреляционная матрица · correlation matrix",
        "<p><b>Корреляционная матрица</b> содержит коэффициенты корреляции всех пар признаков. "
        "Здесь используем коэффициент Пирсона.</p>"
        + eq(r"R_{jk}=\frac{S_{jk}}{\sqrt{S_{jj}}\sqrt{S_{kk}}}.",
             r"$j,k$ — номера признаков; $S_{jk}$ — их ковариация; $S_{jj},S_{kk}$ — их дисперсии; "
             r"$R_{jk}$ — корреляция этих признаков. Дисперсии должны быть положительными."))
    + "<p>На диагонали стоят единицы, если все признаки непостоянны. Остальные элементы лежат "
      "от −1 до 1. Цветовая таблица, или <b>тепловая карта</b>, позволяет быстро увидеть знак и величину каждого элемента.</p>"
    + box("Данные в строках", "В <code>np.cov</code> и <code>np.corrcoef</code> указываем "
          "<code>rowvar=False</code>: признаки у нас в столбцах. В pandas методы "
          "<code>df.cov()</code> и <code>df.corr()</code> уже сравнивают столбцы."))
code('''S_df = apartments.cov()
R_df = apartments.corr(method="pearson")
R_numpy = np.corrcoef(X, rowvar=False)
print("pandas и NumPy совпали:", np.allclose(R_df.to_numpy(), R_numpy))

fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
sns.heatmap(S_df, annot=True, fmt=".2f", cmap="vlag", center=0, ax=axes[0])
sns.heatmap(R_df, annot=True, fmt=".2f", cmap="vlag", vmin=-1, vmax=1, center=0, ax=axes[1])
axes[0].set_title("Ковариации: зависят от единиц")
axes[1].set_title("Корреляции: шкала от −1 до 1")
for ax in axes:
    ax.tick_params(axis="x", rotation=25)
    ax.tick_params(axis="y", rotation=0)
plt.tight_layout()
plt.show()''')
md("**Прочитайте одну клетку каждой матрицы.** Какие признаки она сравнивает? "
   "Почему на диагонали двух матриц разные числа?", ("discussion",))

md("## 6. Связь признаков и линейная зависимость")
theory("Когда новый столбец повторяет старый",
    "<p>В занятии 11 <b>линейной комбинацией</b> называли сумму векторов, умноженных на числа. "
    "Столбцы линейно зависимы, если существует их линейная комбинация, равная нулевому вектору, "
    "с хотя бы одним ненулевым коэффициентом.</p>"
    + eq(r"x_{\text{футы}^2}=10.764\,x_{\text{м}^2}.",
         r"$x_{\text{м}^2}$ — вектор площадей в квадратных метрах; "
         r"$x_{\text{футы}^2}$ — тот же признак в квадратных футах; 10.764 — округлённый коэффициент перевода.")
    + "<p>Второй столбец — точная кратная копия первого. Их добавление в одну матрицу "
      "даёт два столбца, но ранг остаётся равен одному. Для непостоянной площади корреляция равна 1.</p>"
    + definition("Мультиколлинеарность · multicollinearity",
        "<p><b>Мультиколлинеарность</b> — точная или приближённая линейная зависимость между "
        "признаками линейной модели. Один признак можно точно или почти выразить через остальные. "
        "В модели со свободным членом — постоянной добавкой к прогнозу — учитывается также столбец единиц.</p>")
    + box("Точная и приблизительная зависимость", "Точная зависимость делает столбцы линейно зависимыми. "
          "Приблизительная зависимость может сохранять полный ранг. Поэтому сильная корреляция "
          "сама по себе не означает потерю ранга.", "take"))
code('''# Keep the exact conversion separate from a slightly noisy measurement.
rng_duplicate = np.random.default_rng(1306)
area_feet_exact = 10.764 * x_area
area_feet_noisy = area_feet_exact + rng_duplicate.normal(0, 12, len(x_area))

comparison = []
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, title, second in zip(axes, ["Точная копия", "Почти копия"],
                            [area_feet_exact, area_feet_noisy]):
    matrix = np.column_stack([x_area, second])
    r = pearsonr(x_area, second).statistic
    comparison.append({"Пример": title, "Ранг двух столбцов": np.linalg.matrix_rank(matrix), "Пирсон": r})
    sns.scatterplot(x=x_area, y=second, s=22, ax=ax)
    ax.set(xlabel="Площадь, м²", ylabel="Второй признак, фут²", title=title)
display(pd.DataFrame(comparison).round(6))
plt.tight_layout()
plt.show()''')
theory("Почему важно центрирование",
    "<p>Корреляция 1 означает, что точки лежат на возрастающей прямой, но эта прямая "
    "не обязана проходить через начало координат.</p>"
    + eq(r"y=2x+10\cdot\mathbf 1,\qquad y_c=2x_c.",
         r"$x,y$ — векторы исходных значений признаков; $\mathbf 1$ — вектор из единиц той же длины; "
         r"$x_c,y_c$ — центрированные векторы. 2 — множитель, 10 — одинаковый сдвиг всех значений.")
    + "<p>Исходные два столбца здесь могут быть независимыми. После центрирования они зависимы. "
      "Если включить столбец единиц, исходные <b>три</b> столбца тоже будут зависимыми.</p>"
    + box("Связь с углом", "При корреляции 1 или −1 линейно зависимы именно центрированные векторы. "
          "Это согласуется с формулой косинуса из раздела 4.")
    + "<details><summary>Что это означает для ковариационной матрицы</summary>"
    + "<p>Ранг ковариационной матрицы равен рангу центрированной матрицы признаков. "
      "Если её столбцы линейно зависимы, ковариационная матрица вырождена и не имеет обратной.</p></details>")
code('''x_affine = np.array([1., 2., 3., 4.])
y_affine = 2 * x_affine + 10
X_affine = np.column_stack([x_affine, y_affine])
print("Пирсон:", pearsonr(x_affine, y_affine).statistic)
print("Ранг исходных двух столбцов:", np.linalg.matrix_rank(X_affine))
print("Ранг после центрирования:", np.linalg.matrix_rank(X_affine - X_affine.mean(axis=0)))
print("Ранг трёх столбцов [1, x, y]:",
      np.linalg.matrix_rank(np.column_stack([np.ones(len(x_affine)), X_affine])))''')
theory("Для чего это понадобится в модели",
    "<p>Если признаки почти повторяют друг друга, модели трудно устойчиво разделить их вклады: "
    "небольшое изменение данных может заметно изменить отдельные веса. При этом прогнозы на похожих "
    "данных могут оставаться близкими. Это проверим, когда будем обучать регрессию.</p>"
    + box("Попарной таблицы недостаточно", "Зависимость может включать сразу несколько столбцов. "
          "Например, число поездок за день равно сумме утренних и вечерних поездок. "
          "Ни одна пара при этом не обязана иметь корреляцию 1 или −1. Такой случай будет в задаче 6.", "warn"))

md("## 7. Что Пирсон может пропустить? Коротко о Спирмене")
theory("Нулевая линейная связь — ещё не отсутствие зависимости",
    "<p>Пусть второй признак равен квадрату первого. При симметричном наборе положительных "
    "и отрицательных значений первого признака корреляция Пирсона равна нулю. "
    "Но второй признак полностью определяется первым: на графике видна парабола.</p>"
    + definition("Монотонная зависимость · monotonic relationship",
        "<p>Зависимость <b>монотонна</b>, если при увеличении аргумента значение функции "
        "на всей рассматриваемой области либо не убывает, либо не возрастает. "
        "Например, куб возрастает на всей числовой прямой. Квадрат на всей числовой прямой "
        "сначала убывает, затем возрастает.</p>")
    + "<p>Для данных с шумом можно оценить, насколько согласован порядок значений двух признаков. "
      "Для этого используют ранги.</p>"
    + definition("Ранг значения · rank of a value",
        "<p><b>Ранг значения</b> — его место при упорядочивании значений по возрастанию, начиная с 1. "
        "При равенстве значений им присваивают среднее занятых мест. "
        "Например, у значений 10, 20, 20, 40 ранги 1, 2.5, 2.5, 4.</p>")
    + box("Два разных значения слова «ранг»", "Ранг отдельного значения — место в упорядоченном ряду. "
          "Ранг матрицы — число линейно независимых столбцов. Это разные понятия.", "warn"))
theory("Корреляция Спирмена",
    definition("Коэффициент корреляции Спирмена · Spearman rank correlation",
        "<p><b>Коэффициент Спирмена</b> — коэффициент Пирсона между рангами значений двух признаков. "
        "Он описывает направление и силу монотонной связи.</p>"
        + eq(r"\rho_s=r_{R_x,R_y}.",
             r"$\rho_s$ — выборочный коэффициент Спирмена; $R_x,R_y$ — векторы рангов "
             "значений исходных признаков с сохранением порядка объектов; "
             r"$r$ — коэффициент Пирсона. Ранги обоих признаков должны иметь ненулевой разброс."))
    + "<p>Если значения строго возрастают вместе, порядок полностью совпадает и Спирмен равен 1. "
      "Если порядок противоположен — −1. Шум и нарушения порядка могут уменьшать модуль коэффициента.</p>"
    + box("Граница применения", "Спирмен описывает монотонную связь, в том числе нелинейную. "
          "Он не обнаруживает любую нелинейную зависимость. Для симметричной параболы "
          "он тоже может быть равен нулю.", "take"))
code('''x_rank_demo = np.array([1., 2., 3., 4., 5.])
y_rank_demo = x_rank_demo**3
rx_demo = rankdata(x_rank_demo, method="average")
ry_demo = rankdata(y_rank_demo, method="average")
display(pd.DataFrame({"x": x_rank_demo, "y = x³": y_rank_demo,
                      "Ранг x": rx_demo, "Ранг y": ry_demo}))
print("Пирсон исходных значений:", round(pearsonr(x_rank_demo, y_rank_demo).statistic, 3))
print("Пирсон рангов:", pearsonr(rx_demo, ry_demo).statistic)
print("Спирмен в SciPy:", spearmanr(x_rank_demo, y_rank_demo).statistic)''')
code('''# Integer symmetry preserves exact pairs of equal squared values.
x_shapes = np.arange(-50, 51, dtype=float) / 25
relations = [("Прямая", 2 * x_shapes + 1),
             ("Возрастающий куб", x_shapes**3),
             ("Парабола", x_shapes**2)]
fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
for ax, (name, y_values) in zip(axes, relations):
    r = pearsonr(x_shapes, y_values).statistic
    rho = spearmanr(x_shapes, y_values).statistic
    sns.scatterplot(x=x_shapes, y=y_values, s=17, ax=ax)
    ax.set(xlabel="x", ylabel="y", title=f"{name}\\nПирсон = {r:.2f}; Спирмен = {rho:.2f}")
plt.tight_layout()
plt.show()''')
theory("Всегда начинаем с графика",
    "<p>Одинаковый коэффициент может получиться у разных облаков точек. "
    "В частности, Пирсон чувствителен к отдельным далёким точкам: их произведения отклонений велики.</p>"
    + box("Корреляция и причина", "Ни Пирсон, ни Спирмен сами по себе не доказывают причинную связь. "
          "Связь площади и цены в наблюдениях ещё не объясняет, что произойдёт при вмешательстве. "
          "Для описания данных смотрим и на коэффициент, и на график.", "warn"))

md("## 8. А если преобразовать признак?")
theory("Одна зависимость в разных координатах",
    "<p>Вернёмся к параболе. На горизонтальной оси отложим квадрат исходного признака. "
    "Теперь точки окажутся на прямой. Для волны можно аналогично попробовать синус.</p>"
    + eq(r"z=x^2\quad\text{или}\quad z=\sin(x).",
         r"$x$ — исходное значение признака; $z$ — новое значение, полученное из него; "
         r"$x^2$ — квадрат; $\sin(x)$ — синус. В NumPy и в интерактиве аргумент синуса задаётся в радианах: "
         r"$\pi$ радиан соответствует 180 градусам.")
    + definition("Создание признаков · feature engineering",
        "<p><b>Создание признаков</b> — получение новых характеристик объектов из имеющихся данных. "
        "Например, квадрат площади или синус угла.</p>")
    + definition("Полиномиальные признаки · polynomial features",
        "<p><b>Полиномиальные признаки</b> — признаки, полученные из степеней и произведений исходных "
        "признаков. Для одного признака это, например, квадрат и куб; для нескольких — также их произведения.</p>"))

widget("transform", "До и после преобразования",
       "Выберите зависимость и сначала уберите шум. Слева исходный признак, справа его преобразование. "
       "В обоих графиках вертикальные значения одни и те же. Затем постепенно увеличьте шум.",
       "Почему Спирмен хорошо описывает куб, но может пропустить параболу? "
       "Каким стал график после подходящего преобразования?")
code('''rng_transform = np.random.default_rng(1308)
x_curve = np.linspace(-3, 3, 101)
y_curve = x_curve**2 + rng_transform.normal(0, 0.5, len(x_curve))
z_curve = x_curve**2

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, horizontal, label in zip(axes, [x_curve, z_curve], ["Исходный x", "Новый признак z = x²"]):
    r = pearsonr(horizontal, y_curve).statistic
    sns.scatterplot(x=horizontal, y=y_curve, s=22, ax=ax)
    ax.set(xlabel=label, ylabel="y", title=f"Пирсон = {r:.3f}")
plt.tight_layout()
plt.show()

# The same operation can create a column in a data table.
curve_data = pd.DataFrame({"x": x_curve, "y": y_curve})
curve_data["x²"] = curve_data["x"] ** 2
display(curve_data.head().round(3))''')
theory("Связь с линейной моделью",
    eq(r"\widehat y=b+w_1x+w_2x^2.",
         r"$\widehat y$ — прогноз; $x$ — исходный признак; $x^2$ — новый признак; "
         r"$b$ — свободный член, одинаковая добавка к каждому прогнозу; $w_1,w_2$ — веса признаков.")
    + "<p>Это линейная модель <b>по неизвестным весам</b>: каждый вес умножается на известное значение "
      "признака, затем результаты складываются. При этом график прогноза относительно исходного признака "
      "может быть параболой. Как находить веса по данным, разберём далее.</p>"
    + box("Два вида зависимости", "Функциональная зависимость означает, что значение одного признака "
          "полностью определяется значением другого. Например, квадрат определяется через исходное значение. "
          "Но векторы значений признака и его квадрата могут быть линейно независимыми. "
          "Функциональная зависимость шире линейной.", "take")
    + "<p>Преобразование выбираем осмысленно: по форме графика и смыслу признака. "
      "В примерах закон задан заранее, поэтому мы точно знаем подходящее преобразование.</p>")

md("## 9. Проверьте понимание")
theory("Что теперь можно объяснить",
    "<ol><li>Как из отклонений от средних получить ковариацию?</li>"
    "<li>Почему перевод рублей в тысячи рублей меняет ковариацию, но не Пирсона?</li>"
    "<li>Почему перед вычислением косинуса для Пирсона нужно центрировать признаки?</li>"
    "<li>Что находится на диагонали ковариационной матрицы?</li>"
    "<li>Почему корреляция, близкая к 1, не обязана означать неполный ранг?</li>"
    "<li>Какую связь описывает Спирмен и какую может пропустить?</li>"
    "<li>Почему добавление квадрата признака может быть полезно линейной модели?</li></ol>")

add_tasks(md, code, theory, eq, box)

md("""## Источники и повторение

- [Занятие 2: скалярное произведение и косинус](02_dot_product.ipynb).
- [Занятие 11: линейная зависимость и ранг](11_linear_dependence_rank.ipynb).
- [Занятие 12: системы и обратимость](12_linear_systems_inverse.ipynb).
- [NumPy: ковариационная матрица и порядок осей](https://numpy.org/doc/stable/reference/generated/numpy.cov.html).
- [NumPy: матрица корреляций](https://numpy.org/doc/stable/reference/generated/numpy.corrcoef.html).
- [SciPy: коэффициент Пирсона](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html).
- [SciPy: коэффициент Спирмена](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html).
- [SciPy: ранги и одинаковые значения](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rankdata.html).
- [scikit-learn: линейные модели и чувствительность коэффициентов при зависимых признаках](https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares).
- [scikit-learn: полиномиальные признаки](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PolynomialFeatures.html).

Все численные примеры в этом занятии синтетические. Они показывают свойства методов и не являются
выводами о реальном рынке недвижимости.
""")

nb = nbf.v4.new_notebook(cells=cells, metadata=json.loads(json.dumps(META)))
nb.metadata["colab"]["name"] = "13_covariance_correlation.ipynb"
nb.metadata["lesson"] = {
    "number": 13, "duration_minutes": 120,
    "format": "Shared dark HTML theory, standalone SVG/JS widgets, worked NumPy/pandas/SciPy/seaborn examples.",
    "source": "build_lesson13.py + embedded lesson13_widgets.js + build-only lesson13_tasks.py",
    "prerequisites": ["02_dot_product.ipynb", "03_stat_intro.ipynb", "10_matrices.ipynb",
                      "11_linear_dependence_rank.ipynb", "12_linear_systems_inverse.ipynb"],
    "data": "Seeded synthetic apartments and small exact tables; no runtime downloads.",
    "practice": "Five core tasks and three extensions; hand calculations first, Python checks second. Finish remaining tasks as homework.",
    "student_code_tags": ["student-core"],
}
for index, cell in enumerate(nb.cells):
    cell.id = hashlib.sha256(f"lesson13-{index}-{cell.source}".encode()).hexdigest()[:12]
nbf.validate(nb)
path = HERE / "13_covariance_correlation.ipynb"
nbf.write(nb, path)
print(f"Wrote {path.name}: {len(cells)} cells; standalone HTML/JS lesson")
