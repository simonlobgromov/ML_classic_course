"""Build the self-contained HTML/JS Colab lesson 09_stat_hypotheses.ipynb.

Theory uses the shared lesson theme. Numerical examples remain ordinary Python.
Widget and helper sources are embedded; students need only the notebook.
"""
from pathlib import Path
import hashlib
import json

import nbformat as nbf
from theme import SETUP, META

HERE = Path(__file__).resolve().parent
WIDGET_JS = (HERE / "lesson9_widgets.js").read_text(encoding="utf-8")
HELPERS = (HERE / "lesson9_helpers.py").read_text(encoding="utf-8")
cells = []


def md(source, tags=()):
    cells.append(nbf.v4.new_markdown_cell(source.strip(), metadata={"tags": list(tags)}))


def code(source, tags=("provided",)):
    cells.append(nbf.v4.new_code_cell(source.strip(), metadata={"tags": list(tags)}))


def eq(formula, meanings):
    """Every displayed equation must have a local symbol glossary."""
    if not meanings:
        raise ValueError("An equation needs its symbol glossary")
    return ("<div class='d9-equation'>$$" + formula + "$$</div>"
            + "<div class='where'><b>Обозначения.</b> " + meanings + "</div>")


def definition(title, body):
    return f'<div class="box def"><div class="t">{title}</div>{body}</div>'


def box(title, body, kind="take"):
    return f'<div class="box {kind}"><div class="t">{title}</div>{body}</div>'


def theory(title, body):
    code(f'#@title {title} {{ display-mode: "form" }}\n'
         + 'display(HTML(lesson9_viz(' + repr(body) + ')))', tags=("provided", "theory"))


def select(key, label, choices):
    return (f'<label class="d9-control"><span>{label}</span><select data-control="{key}">'
            + ''.join(f'<option value="{value}">{name}</option>' for value, name in choices)
            + '</select></label>')


def button(action, label):
    return f'<button class="btn" data-action="{action}">{label}</button>'


def widget(kind, title, instruction, charts, controls, question, data):
    body = (f'<div class="widget"><div class="widget-title">{title}</div>'
            + f'<p class="widget-sub">{instruction}</p>'
            + f'<div class="d9-controls">{controls}</div><div class="d9-charts">'
            + ''.join(f'<svg data-chart="{key}"></svg>' for key in charts)
            + '</div><div class="readout" data-readout role="status" aria-live="polite"></div>'
            + f'<p class="d9-question"><b>Проверь себя.</b> {question}</p>'
            + '<p class="d9-footnote">Учебная симуляция. Повторные выборки в интерактиве и в Python '
              'генерируются независимо; результаты могут немного различаться.</p></div>')
    code(f'#@title Интерактив — {title} {{ display-mode: "form" }}\n'
         + 'display(HTML(lesson9_viz(' + repr(body) + ', widget=' + repr(kind)
         + ', data=' + data + ')))', tags=("provided", "interactive"))


md(r"""
# Новая доставка действительно быстрее?
## Занятие 9 — гипотезы, p-value и статистическая значимость

Служба доставки проверяет новый способ работы. По выборкам времена различаются.
**Есть ли основания считать изменение реальным и достаточно ли оно велико для внедрения?**

Продолжим задачу о доставках: сравним два способа работы, проверим различие перестановками
и оценим его величину с помощью бутстрапа. Все данные **синтетические**.

Перед опытом предскажите результат, после — объясните наблюдение.
После интерактивов идут примеры NumPy и seaborn; в конце — три коротких задания.

В Colab запускайте ячейки по порядку. Ноутбук содержит весь код визуализаций.
После запуска интерактивы работают в браузере; формулы загружаются через MathJax.
Изменения в интерактиве не меняют переменные в Python-ячейках.
""")

EXTRA_SETUP = r'''
import json
import uuid
import re
from html import escape

D9_CSS = r"""
.vec-root .d9-controls{display:flex;flex-wrap:wrap;gap:12px 24px;margin:16px 0 22px;font-family:system-ui,sans-serif;}
.vec-root .d9-control{display:flex;align-items:center;flex-wrap:wrap;gap:8px;color:var(--ink);font-size:14px;min-height:36px;}
.vec-root .d9-control input[type=range]{width:155px;min-height:30px;}
.vec-root .d9-control output{font-variant-numeric:tabular-nums;color:var(--green);min-width:42px;}
.vec-root .d9-control select{max-width:100%;padding:8px;}
.vec-root .d9-control input:disabled{opacity:.3;}
.vec-root .d9-charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,380px),1fr));gap:16px;}
.vec-root .d9-charts svg{display:block;width:100%;height:auto;background:#0e1319;border-radius:10px;}
.vec-root .d9-charts svg:last-child:nth-child(3){grid-column:1/-1;max-width:780px;justify-self:center;}
.vec-root .readout{overflow-wrap:anywhere;font:15px/1.75 system-ui,sans-serif;}
.vec-root .d9-question{font-family:system-ui,sans-serif;font-size:14px;color:var(--ink);}
.vec-root .d9-footnote{font-family:system-ui,sans-serif;font-size:12px;color:var(--soft);}
.vec-root .d9-equation{overflow-x:auto;overflow-y:hidden;padding:5px 0;}
.vec-root .where{line-height:1.7;}
.vec-root .d9-table{overflow-x:auto;}
.vec-root button:disabled{opacity:.45;cursor:wait;}
.vec-root .d9-controls .btn{min-height:38px;}
.vec-root input:focus-visible,.vec-root select:focus-visible,.vec-root button:focus-visible{outline:2px solid #e0b25a;outline-offset:4px;}
@media(max-width:600px){.vec-root .wrap{padding:14px;font-size:16px;}.vec-root .widget{padding:10px;}.vec-root .d9-control{width:100%;}}
"""

def lesson9_viz(body, widget=None, data=None):
    """Scope controls to a fresh root so rerunning cells keeps widgets independent."""
    # HTML is parsed before MathJax. Protect comparisons and ampersands in both
    # display equations and inline symbol glossaries without escaping HTML tags.
    body = re.sub(
        r"(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$.*?(?<!\\)\$",
        lambda match: escape(match.group(0), quote=False),
        body,
        flags=re.DOTALL,
    )
    root_id = "d9_" + uuid.uuid4().hex
    script = D9_WIDGET_JS + "\n" + r"""
    (function(){
      const root = document.getElementById(__ROOT__);
      const widget = __WIDGET__;
      if (widget) window.InferenceLesson9.mount(root, widget, __DATA__);
      const typeset = () => window.MathJax.typesetPromise([root]);
      if (!window.__D9_MATH_READY__) {
        if (window.MathJax && window.MathJax.typesetPromise) {
          window.__D9_MATH_READY__ = window.MathJax.startup.promise;
        } else {
          window.MathJax = {tex:{inlineMath:[['$','$']],displayMath:[['$$','$$']]},svg:{fontCache:'local'},startup:{typeset:false}};
          window.__D9_MATH_READY__ = new Promise((resolve, reject) => {
            const loader = document.createElement('script');
            loader.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
            loader.onload = () => window.MathJax.startup.promise.then(resolve, reject);
            loader.onerror = reject;
            document.head.appendChild(loader);
          });
        }
      }
      window.__D9_MATH_READY__ = window.__D9_MATH_READY__.then(typeset).catch(() => {
        if(root.querySelector('.d9-equation')) {
          const notice = document.createElement('p');
          notice.textContent = 'Для отображения формул подключитесь к интернету и перезапустите ячейку. Графики работают без загрузки MathJax.';
          root.appendChild(notice);
        }
      });
    })();
    """.replace("__ROOT__", json.dumps(root_id)).replace("__WIDGET__", json.dumps(widget)).replace("__DATA__", json.dumps(data, ensure_ascii=False))
    return ("<style>" + CSS + D9_CSS + "</style>"
            + '<div class="vec-root" data-widget="' + (widget or "theory") + '" id="' + root_id + '"><div class="wrap wide">'
            + body + '</div></div><script>' + script + '</script>')

print("Занятие 9 готово: графики работают в браузере; формулы загружаются через MathJax.")'''

code(SETUP + '\n\nD9_WIDGET_JS = ' + repr(WIDGET_JS) + '\n' + EXTRA_SETUP + '\n' + HELPERS)

md("## 1. Что сравниваем?")
theory("Два способа доставки", r"""
<p>Заказы случайно распределяют между <b>A — прежним способом</b> и <b>B — новым</b>.
В нашей модели каждая доставка независима от других. Условия двух групп сопоставимы.</p>
<p>У A время состоит из 10 минут обязательной работы и случайной задержки из генератора занятия 8.
У B обязательная часть может стать короче; распределение задержки остаётся прежним.
Среднее A — 30 минут. В основном опыте истинный выигрыш B — 6 минут.
В реальной задаче этот выигрыш неизвестен: его нужно оценить по заказам.</p>
""" + box("Что важно для службы доставки",
    "<p>До анализа выбираем показатель — <b>среднее время</b>. Внедрение интересно, "
    "если выигрыш составляет хотя бы <b>5 минут</b>. Сравним по 200 доставок каждого способа.</p>", "idea"))

code('# Provided: independent samples from the same delivery model as in lessons 7–8.\na, b = delivery_samples(n=200, gain=6, seed=9120)\nplot_deliveries(a, b)')

theory("Разница средних", eq(
    r"\Delta=\mu_B-\mu_A,\qquad\widehat\Delta=\overline x_B-\overline x_A.",
    r"$\mu_A,\mu_B$ — истинные средние времена двух способов; $\Delta$ — истинная разница; "
    r"$\overline x_A,\overline x_B$ — средние выборок; $\widehat\Delta$ — оценка разницы. Всё в минутах.")
    + box("Как читать знак", "<p><b>Минус означает, что B быстрее.</b> Различие средних выборок "
          "само по себе ещё не доказывает различие истинных средних.</p>"))

code("# Worked example: estimate the mean difference.\nobserved = b.mean() - a.mean()\nprint(f'Среднее A: {a.mean():.2f} мин; среднее B: {b.mean():.2f} мин.')\nprint(f'Наблюдаемая разница B − A: {observed:.2f} мин.')")

md("## 2. Сформулируем гипотезы")
theory("Нулевая и альтернативная гипотезы",
    definition("Статистическая гипотеза · statistical hypothesis",
        "<p>Предположение о распределении генеральной совокупности или его параметрах, "
        "которое проверяют по выборочным данным.</p>")
    + definition("Нулевая и альтернативная гипотезы",
        "<p><b>Нулевая гипотеза</b> $H_0$ — проверяемое предположение, относительно которого оценивают данные. "
        "<b>Альтернативная гипотеза</b> $H_1$ — предположение, описывающее отличие от $H_0$ "
        "в рамках выбранной модели.</p>")
    + "<p>У нас исходное предположение — новый способ не изменил время доставки. "
      "Альтернатива — среднее изменилось. Проверяем обе стороны: B мог стать быстрее или медленнее.</p>"
    + eq(r"H_0:\Delta=0,\qquad H_1:\Delta\ne0.",
        r"$H_0$ — нулевая гипотеза; $H_1$ — двусторонняя альтернативная гипотеза; "
        r"$\Delta=\mu_B-\mu_A$ — истинная разница средних времён."))
theory("Что дают перестановки", r"""
<p>В <b>нашей модели</b> способы могут отличаться только постоянным сдвигом времени.
Поэтому при нулевой разнице их распределения полностью совпадают, и метки A/B можно переставлять.</p>
<ol><li>Соберём времена вместе и случайно перемешаем их.</li>
<li>Разделим обратно на две группы прежних размеров.</li>
<li>Пересчитаем разницу средних. Повторим много раз.</li></ol>
""" + box("Смысл опыта", "<p>Получаем различия, возможные при случайном распределении меток A/B. "
    "Сами времена сохраняются, меняется только принадлежность к группе.</p>", "idea")
    + "<p>В автобусном практикуме обмен был внутри дня; здесь группы независимы.</p>"
    + "<details><summary>Когда можно переставлять метки?</summary><p>В нашей модели равенство средних "
      "означает совпадение распределений. Для произвольных данных одного равенства средних "
      "для такого обоснования недостаточно.</p></details>")

code("# Worked example: one permutation, without replacement.\nrng_once = np.random.default_rng(9100)\npooled = np.concatenate([a, b])\nshuffled = rng_once.permutation(pooled)\na_perm = shuffled[:len(a)]\nb_perm = shuffled[len(a):]\nprint(f'Разница после одной перестановки: {b_perm.mean() - a_perm.mean():.2f} мин.')")

md("## 3. P-value и статистическая значимость")
theory("От разницы к p-value",
    definition("Статистика критерия · test statistic",
        "<p>Число, рассчитанное по выборке и используемое для проверки гипотезы. "
        "Здесь это разница средних B − A.</p>")
    + definition("P-value",
        "<p>Вероятность <b>при верной нулевой гипотезе и выполненных предположениях модели</b> получить "
        "значение статистики критерия <b>не менее экстремальное, чем наблюдаемое</b>, "
        "в направлении или направлениях, заданных альтернативной гипотезой.</p>")
    + "<p>В нашей задаче: если способы в действительности одинаковы, какова вероятность получить "
      "такую же или ещё большую по модулю разницу средних? «По модулю» означает величину без учёта знака: "
      "учитываем отклонения в обе стороны.</p>"
    + eq(r"p=P_{H_0}\!\left(|T|\ge|t_{\mathrm{набл}}|\right).",
        r"$p$ — p-value нашего двустороннего теста; $T$ — разница средних при случайном распределении меток; "
        r"$t_{\mathrm{набл}}=\widehat\Delta$ — наблюдаемая разница; $|\cdot|$ — модуль; "
        r"$P_{H_0}$ — вероятность в нулевой модели при зафиксированных временах и размерах групп."))
theory("Как посчитать p-value по перестановкам",
    "<p>Все перестановки перебирать долго. Оценим вероятность по случайным повторениям: "
    "посчитаем, сколько раз получилось не меньшее по модулю различие.</p>"
    + eq(r"\widehat p=\frac{k+1}{R+1}.",
        r"$\widehat p$ — оценка p-value; $R$ — число случайных перестановок; "
        r"$k$ — число перестановок с разницей не меньше наблюдаемой по модулю.")
    + "<p>Добавление единицы учитывает исходное разбиение и не позволяет сообщить "
      "нулевую вероятность по конечной симуляции.</p>")
widget("permutation", "Какие разницы не менее экстремальны?",
    "Сделайте одну перестановку, затем добавьте 999. Оранжевые области — оба хвоста; "
    "оранжевые столбцы показывают число попавших туда результатов.",
    ["permutations"], button("one", "Одна перестановка") + button("many", "Ещё 999") + button("reset", "Сброс"),
    "Почему считаем результаты в обоих хвостах, хотя в нашей выборке B быстрее?",
    "{'a': a.tolist(), 'b': b.tolist()}")
md("**Пример в Python.** Выполним 9999 перестановок тех же времён и построим гистограмму.")

code("rng_perm = np.random.default_rng(9102)\nR = 9999\nperm_diffs = []\nfor _ in range(R):\n    shuffled = rng_perm.permutation(pooled)\n    perm_diffs.append(shuffled[len(a):].mean() - shuffled[:len(a)].mean())\nperm_diffs = np.array(perm_diffs)\n\n# Include ties; the tiny tolerance only handles floating-point rounding.\ntolerance = 100 * np.finfo(float).eps * max(1, abs(observed))\nk = np.count_nonzero(np.abs(perm_diffs) >= abs(observed) - tolerance)\np_value = (k + 1) / (R + 1)\nprint(f'Не менее экстремальных результатов: {k} из {R}; p-value ≈ {p_value:.4f}.')\nplot_permutations(perm_diffs, observed)")

theory("Когда результат называют статистически значимым?",
    definition("Уровень значимости · significance level",
        "<p>Заранее выбранная верхняя граница вероятности ошибочно отвергнуть верную нулевую гипотезу "
        r"при выполнении предположений теста. Обозначается $\alpha$.</p>")
    + definition("Ошибка первого рода · type I error",
        "<p>Отклонение нулевой гипотезы, когда она верна.</p>")
    + r"<p>До просмотра результата выбираем $\alpha=0{,}05$. При выполнении условий теста вероятность "
      "ошибки первого рода в каждом исследовании не превышает 5%.</p>"
    + definition("Статистическая значимость · statistical significance",
        r"<p>Результат называют <b>статистически значимым на уровне $\alpha$</b>, "
        r"если p-value не превышает $\alpha$. При таком правиле нулевую гипотезу отвергают.</p>")
    + box("Если p-value больше выбранного уровня",
        "<p>Говорим: <b>«Нет достаточных оснований отвергнуть $H_0$».</b> Это не доказывает равенство способов. "
        "Числа 0,049 и 0,051 близки, хотя формальное решение различается.</p>", "warn")
    + box("Что p-value не означает",
        "<ul><li>Вероятность истинности $H_0$.</li><li>Вероятность «случайности различия».</li>"
        "<li>Размер выигрыша.</li></ul><p>Маленькое p-value само по себе не определяет решение о внедрении.</p>"))

code("alpha = 0.05  # Chosen before inspecting the result.\nprint('Отвергаем H₀: результат статистически значим.' if p_value <= alpha\n      else 'Нет достаточных оснований отвергнуть H₀.')")

theory("Может ли тест ошибиться?", r"""
<p>Теперь в генераторе эффект строго нулевой. Проведём много независимых исследований:
каждый раз получим по 50 новых доставок A и B и выполним свой перестановочный тест.</p>
<p>Цветом отметим ошибочные отклонения верной гипотезы. В конечной серии их доля не обязана быть ровно 5%.</p>
""")

code("# Provided: a static result remains available without the widget controls.\nnull_pvalues = null_experiments(count=100)\nplot_null_pvalues(null_pvalues)\nprint(f'Ложные сигналы: {np.count_nonzero(null_pvalues <= alpha)} из {len(null_pvalues)} исследований.')")

widget("null", "Ложные отклонения верной гипотезы",
    "Предскажите, все ли p-value окажутся выше 0,05. Добавьте 100 новых исследований и сравните долю ошибок.",
    ["null"], button("many", "Ещё 100 исследований") + button("reset", "Сброс"),
    "Почему повторять исследование до появления маленького p-value — не то же самое, что провести один заранее выбранный тест?",
    "{'initial': null_pvalues.tolist()}")
theory("Правило выбирают заранее", box("Один анализ — одно заранее выбранное правило",
    "<p>Для реального решения заранее фиксируем объём данных и способ анализа. "
    "Если повторять тест до первого маленького p-value, вероятность хотя бы одного ложного вывода растёт.</p>", "warn"))

md("## 4. На сколько минут изменилась доставка?")
theory("Интервал для разницы средних",
    "<p>P-value оценивает необычность результата при нулевой модели. Теперь оценим "
    "<b>величину изменения и её точность</b>.</p>"
    + definition("Доверительный интервал · confidence interval",
        "<p>Интервал со случайными границами, построенный по выборке методом, "
        "который покрывает неизвестный параметр с заданной вероятностью.</p>")
    + "<p>Для 95%-го метода при многократном повторении исследования около 95% построенных интервалов "
      "содержали бы истинный параметр, если условия выполнены. Наш бутстрап-интервал приближённый.</p>"
    + box("Какой параметр оцениваем",
        "<p>Строим интервал <b>для истинной разницы средних B − A</b>. "
        "Он описывает точность оценки средней разницы, а не время следующего заказа.</p>", "idea"))
theory("Бутстрап двух независимых групп", r"""
<ol><li>Отберём с возвращением времена внутри A, сохраняя размер группы.</li>
<li>Независимо сделаем то же внутри B.</li><li>Посчитаем разницу средних. Повторим много раз.</li></ol>
<p><code>choice</code> выбирает значения, <code>size</code> задаёт число наблюдений,
<code>replace=True</code> разрешает повторы. Метки A/B сохраняются: группы для отбора не объединяем.</p>
""")

code('# Worked example: separate bootstrap resampling within the two groups.\nrng_boot = np.random.default_rng(9104)\nB = 9999\nboot_diffs = []\nfor _ in range(B):\n    a_star = rng_boot.choice(a, size=len(a), replace=True)\n    b_star = rng_boot.choice(b, size=len(b), replace=True)\n    boot_diffs.append(b_star.mean() - a_star.mean())\nboot_diffs = np.array(boot_diffs)')

theory("Границы бутстрап-интервала", eq(
    r"I_{95\%}=\left[q^*_{0.025};\ q^*_{0.975}\right].",
    r"$I_{95\%}$ — процентильный 95%-й бутстрап-интервал для $\Delta=\mu_B-\mu_A$; "
    r"$q^*_{0.025},q^*_{0.975}$ — квантили 2,5% и 97,5% среди бутстрап-разниц средних. "
    r"Звёздочка отмечает величины, полученные бутстрапом."))

code("ci = np.quantile(boot_diffs, [0.025, 0.975])\nprint(f'Оценка разницы: {observed:.2f} мин; 95%-й бутстрап-ДИ: [{ci[0]:.2f}; {ci[1]:.2f}] мин.')\nplot_bootstrap(boot_diffs, observed, ci)")

theory("Что сравнивать с интервалом?", r"""
<p>Сравниваем предполагаемую <b>истинную разницу</b> с границами интервала.</p>
<ul><li><b>0 внутри</b> — нулевая разница остаётся совместимой с интервалом; равенство не доказано.</li>
<li><b>Весь интервал ниже 0</b> — интервал поддерживает преимущество B по среднему времени.</li>
<li><b>Весь интервал выше 0</b> — интервал поддерживает преимущество A.</li></ul>
""" + box("Перестановки и бутстрап отвечают на разные вопросы",
    "<p><b>Перестановки:</b> какие разницы возможны при нулевой модели? Гистограмма собирается около нуля.</p>"
    "<p><b>Бутстрап:</b> насколько неточна наша оценка? Гистограмма собирается около наблюдаемой разницы.</p>", "idea")
    + "<p>При сравнении групп строим интервал <b>для разницы</b>, а не судим по пересечению "
      "двух отдельных интервалов средних.</p>"
    + "<details><summary>Всегда ли p-value и интервал дают одинаковое решение?</summary>"
      "<p>Точное соответствие требует согласованных процедур. Наш перестановочный тест и процентильный "
      "бутстрап не являются такой парой: около границы решения могут различаться.</p></details>")
md("## 5. Есть различие — достаточно ли оно полезно?")
theory("Статистическая и практическая значимость",
    definition("Практическая значимость · practical significance",
        "<p>Достаточная для задачи величина эффекта.</p>")
    + "<p>Наш ориентир выбран заранее: выигрыш B хотя бы в 5 минут, то есть разница B − A не больше −5 минут.</p>"
    + box("Сравним интервал с −5 минутами",
        "<p>Чтобы весь интервал поддерживал выигрыш <b>больше 5 минут</b>, его верхняя граница должна быть ниже −5. "
        "Если интервал пересекает −5, данных недостаточно для такого уверенного вывода.</p>", "idea"))

code('plot_interval(observed, ci)')

code("a_base, b_base = delivery_samples(n=800, gain=0, seed=9120)")
widget("decision", "Размер выборки и величина эффекта",
    "Сначала при 200 доставках меняйте истинный выигрыш. Затем зафиксируйте выигрыш в 2 минуты "
    "и сравните размеры групп. Предскажите, как изменятся интервал и p-value.",
    ["interval"],
    select("n", "Доставок в каждой группе", [(200,"200"),(50,"50"),(800,"800")])
    + select("gain", "Истинный выигрыш B, мин", [(6,"6"),(0,"0"),(2,"2"),(8,"8")]),
    "Найдите статистически значимое различие, которое слишком мало для внедрения. "
    "В каком опыте весь интервал поддерживает выигрыш больше пяти минут?",
    "{'a': a_base.tolist(), 'b': b_base.tolist()}")
theory("Как сформулировать решение", box("Сообщаем вместе",
    "<p><b>Оценку разницы, доверительный интервал, p-value и практический ориентир.</b> "
    "Статистически значимый результат может быть слишком мал для внедрения.</p>")
    + "<p>Примеры ниже условные; они показывают, как читать интервал.</p>"
    + "<div class='d9-table'><table><thead><tr><th>95%-й интервал, мин</th><th>Что он показывает</th></tr></thead><tbody>"
    "<tr><td>[−8; +2]</td><td>Допускает как ускорение, так и замедление</td></tr>"
    "<tr><td>[−2; −0,5]</td><td>Поддерживает небольшой выигрыш B, существенно меньше пяти минут</td></tr>"
    "<tr><td>[−9; −6]</td><td>Целиком поддерживает выигрыш B больше пяти минут</td></tr></tbody></table></div>")
md(r"""
## 6. Проверьте себя

Ниже новая серия доставок. Группы независимы; показатель, уровень значимости 0,05 и ориентир в 5 минут прежние.
Код повторных выборок готов. Допишите три фрагмента: вместо `...` должно получиться выражение Python.
""")

code('# Provided: a new synthetic series and both resampling distributions.\na_task, b_task = delivery_samples(n=200, gain=4, seed=9150)\nperms_task = permutation_differences(a_task, b_task, 9999, np.random.default_rng(9152))\nboots_task = bootstrap_differences(a_task, b_task, 9999, np.random.default_rng(9153))')

md('**A. Оценка.** Сохраните разницу средних B − A в `observed_task`. Среднее массива вычисляет `.mean()`.')

code('# TODO: Calculate the observed mean difference B minus A.\nobserved_task = ...\nobserved_task', tags=('student-core', 'task-a'))

md('**B. P-value.** Посчитайте в `k_task` число перестановок с не меньшей по модулю разницей. Сохраните оценку p-value в `p_task`. Модуль вычисляет `np.abs`, число истинных условий — `np.count_nonzero`. Используйте поправку +1 в числителе и знаменателе.')

code('# TODO: Count equally or more extreme permutation differences.\nk_task = ...\n# TODO: Estimate the permutation p-value with the plus-one correction.\np_task = ...\np_task', tags=('student-core', 'task-b'))

md('**C. Интервал.** Сохраните границы процентильного 95%-го интервала в `ci_task`. Используйте `np.quantile` для бутстрап-разниц; нужные уровни — 0,025 и 0,975.')

code('# TODO: Calculate the two bootstrap percentile bounds.\nci_task = ...\nci_task', tags=('student-core', 'task-c'))

md(r"""
**Сформулируйте вывод для руководителя.**

1. Какова наблюдаемая разница и в чью пользу?
2. Какое получили p-value и что оно означает для выбранной нулевой модели?
3. Какой получился интервал и входит ли в него ноль?
4. Поддерживает ли весь интервал выигрыш больше пяти минут? Что рекомендуете?

_Ваш ответ: …_

**Вопросы для повторения.** Что такое p-value? Когда результат называют статистически значимым?
Почему «не отвергли гипотезу» не означает «доказали её»?
""", tags=("interpretation",))

md('**Источники и повторение**\n\n- [Занятие 8: доверительные интервалы и бутстрап](08_stat_ci_bootstrap.ipynb).\n- [Автобусный практикум: знакомые перестановки и бутстрап](../practice/practicum_mossovet_asia_mall_bootstrap.ipynb).\n- [Hesterberg, разделы 2 и 7: обучение через повторные выборки](https://arxiv.org/html/1411.5279).\n- [ASA: смысл p-value и ограничения статистической значимости](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf).\n- [SciPy: предпосылки перестановок и поправка +1](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html).\n- [SciPy: независимый и парный бутстрап, процентильный интервал](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html).\n')

nb = nbf.v4.new_notebook(cells=cells, metadata=json.loads(json.dumps(META)))
nb.metadata["colab"]["name"] = "09_stat_hypotheses.ipynb"
nb.metadata["lesson"] = {
    "number": 9, "duration_minutes": 120,
    "format": "Shared dark HTML theory, self-contained SVG/JS widgets, Python examples.",
    "source": "build_lesson9.py + embedded lesson9_widgets.js and lesson9_helpers.py",
    "student_code_tags": ["student-core"],
}
for index, cell in enumerate(nb.cells):
    cell.id = hashlib.sha256(f"lesson9-{index}-{cell.source}".encode()).hexdigest()[:12]
nbf.validate(nb)
path = HERE / "09_stat_hypotheses.ipynb"
nbf.write(nb, path)
print(f"Wrote {path.name}: {len(cells)} cells; self-contained HTML/JS lesson")

