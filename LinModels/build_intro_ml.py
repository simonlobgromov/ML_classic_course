"""Build the first ML lesson; all runtime assets are embedded in the notebook."""
from pathlib import Path
import hashlib
import importlib.util
import json
from html import escape

import nbformat as nbf
import numpy as np
from intro_ml_diagrams import lane, ml_map, learning_cycle, evaluation_flow

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("course_theme", HERE.parent / "math_for_ds" / "theme.py")
theme = importlib.util.module_from_spec(spec)
spec.loader.exec_module(theme)
cells = []


def md(text, tags=()):
    cells.append(nbf.v4.new_markdown_cell(text.strip(), metadata={"tags": list(tags)}))


def code(text, tags=("provided", "example")):
    cells.append(nbf.v4.new_code_cell(text.strip(), metadata={"tags": list(tags)}))


def box(title, text, kind="idea"):
    return f'<div class="box {kind}"><div class="t">{title}</div>{text}</div>'


def definition(ru, en, text):
    return box(f'{ru} · {en}', text, "def")


def eq(formula, meanings):
    if not meanings:
        raise ValueError("Each formula requires a symbol glossary")
    return '<div class="ml-equation">$$' + formula + '$$</div><div class="where"><b>Где:</b> ' + meanings + '</div>'


def slide(title, body):
    code(f'#@title {title} {{ display-mode: "form" }}\n'
         + 'display(HTML(intro_viz(' + repr('<h2>' + title + '</h2>' + body) + ')))', ("provided", "theory"))


def widget(kind, title, instructions, question, data="None"):
    body = (f'<h2>{title}</h2><p>{instructions}</p><div data-stage></div>'
            '<div data-readout class="readout" role="status" aria-live="polite"></div>'
            f'<p class="ml-question"><b>Обсудите.</b> {question}</p>'
            '<p class="ml-small">Синтетические данные. Управление графиком не меняет переменные в Python.</p>')
    code(f'#@title Интерактив — {title} {{ display-mode: "form" }}\n'
         + f'display(HTML(intro_viz({body!r}, widget={kind!r}, data={data})))', ("provided", "interactive"))


def table(headers, rows):
    return '<div class="ml-table"><table><thead><tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>' for row in rows) + '</tbody></table></div>'


def small_plot(kind):
    """Use explicit domains, units and legends in every task illustration."""
    rng = np.random.default_rng(8)
    left, right, top, bottom = 48, 384, 42, 212
    domains = {
        'Регрессия': (10, 60, 'Расстояние, км', 'Время доставки, мин', [0, 5, 10], [0, 30, 60]),
        'Классификация': (1000, 8, 'Длина сообщения, символы', 'Число ссылок, шт.', [0, 500, 1000], [0, 4, 8]),
        'Кластеризация': (12, 6000, 'Покупок за месяц, шт.', 'Средний чек, сом', [0, 6, 12], [0, 3000, 6000]),
    }
    xmax, ymax, xlabel, ylabel, xticks, yticks = domains[kind]
    sx = lambda x: left + x / xmax * (right - left)
    sy = lambda y: bottom - y / ymax * (bottom - top)
    elements = [f'<svg viewBox="0 0 400 300" role="img" aria-label="{kind}: {xlabel}; {ylabel}">',
                f'<title>{kind}: {xlabel}; {ylabel}</title>']
    def label(x, y, value, color='#a7b0ba', anchor='middle', size=14):
        elements.append(f'<text x="{x}" y="{y}" fill="{color}" text-anchor="{anchor}" font-size="{size}" font-family="system-ui,sans-serif">{escape(str(value))}</text>')
    for t in xticks:
        elements.append(f'<path d="M{sx(t)} {top} V{bottom}" stroke="#293440"/>')
        label(sx(t), bottom+20, t)
    for t in yticks:
        elements.append(f'<path d="M{left} {sy(t)} H{right}" stroke="#293440"/>')
        label(left-7, sy(t)+5, t, anchor='end')
    elements.append(f'<path d="M{left} {top} V{bottom} H{right}" stroke="#647487" fill="none"/>')
    label(left, 23, ylabel, '#e6e9ec', 'start', 16)
    label((left+right)/2, 254, xlabel, '#e6e9ec', size=16)
    for i in range(34):
        if kind == 'Регрессия':
            x = rng.uniform(.5, 9.5)
            y = 10 + 4*x + rng.normal(0, 4)
            color = '#6ab0f3'
        elif kind == 'Классификация':
            x = int(rng.integers(60, 941))
            y = int(rng.integers(0, 9))
            color = '#e0757f' if y > 1 + .004*x else '#6ab0f3'
        else:
            group = i % 3
            x = np.clip(round([2, 6, 10][group] + rng.normal(0, .7)), 0, 12)
            y = np.clip([1500, 4500, 2200][group] + rng.normal(0, 380), 0, 6000)
            color = ['#6ab0f3', '#5fd08a', '#e0b25a'][group]
        elements.append(f'<circle cx="{sx(x):.2f}" cy="{sy(y):.2f}" r="4" fill="{color}"/>')
    if kind == 'Регрессия':
        elements.append(f'<path d="M{sx(0)} {sy(10)} L{sx(10)} {sy(50)}" stroke="#5fd08a" stroke-width="3"/>')
        label(115, 285, '● Доставка', '#6ab0f3')
        label(280, 285, '— Прогноз', '#5fd08a')
    elif kind == 'Классификация':
        elements.append(f'<path d="M{sx(0)} {sy(1)} L{sx(1000)} {sy(5)}" stroke="#a7b0ba" stroke-dasharray="5 5"/>')
        label(120, 285, '● Не спам', '#6ab0f3')
        label(280, 285, '● Спам', '#e0757f')
    else:
        for x, title, color in [(80, '● Группа 1', '#6ab0f3'), (210, '● Группа 2', '#5fd08a'), (340, '● Группа 3', '#e0b25a')]:
            label(x, 285, title, color)
    elements.append('</svg>')
    return ''.join(elements)


def simulation_data():
    """Fit all demonstrations at build time with independent, seeded held-out data."""
    def truth(x):
        z = (x - 5) / 4.5
        return 50 + 8*z + 24*z**3

    rng = np.random.default_rng(101)
    x = np.linspace(.5, 9.5, 55)
    signal = {"x": x.tolist(), "truth": truth(x).tolist(), "noise": rng.normal(size=len(x)).tolist()}
    cases = []
    grid = np.linspace(.5, 9.5, 151)
    for rep in range(3):
        rng = np.random.default_rng(10100 + rep)
        # Reuse the same random draws across controls to isolate each change.
        xt = rng.uniform(.5, 9.5, 120)
        et = rng.normal(size=120)
        xv, ev = rng.uniform(.5, 9.5, 120), rng.normal(size=120)
        xs, es = rng.uniform(.5, 9.5, 180), rng.normal(size=180)
        for n in [15, 40, 120]:
            for sigma in [1, 4, 8]:
                split_arrays = [(xt[:n], truth(xt[:n])+sigma*et[:n]),
                                (xv, truth(xv)+sigma*ev), (xs, truth(xs)+sigma*es)]
                c = {"n": n, "sigma": sigma, "rep": rep, "grid": grid.tolist(), "truth": truth(grid).tolist(), "models": []}
                for name, (xx, yy) in zip(["train", "validation", "test"], split_arrays):
                    c[name] = {"x": xx.tolist(), "y": yy.tolist()}
                for degree in [1, 3, 12]:
                    model = np.polynomial.Polynomial.fit(*split_arrays[0], degree)
                    item = {"degree": degree, "prediction": model(grid).tolist()}
                    for name, (xx, yy) in zip(["train", "validation", "test"], split_arrays):
                        item[name+"_mse"] = float(np.mean((yy-model(xx))**2))
                    c["models"].append(item)
                cases.append(c)
    return signal, {"cases": cases}


def token_probabilities():
    """Give the illustrative categorical distribution one explicit common axis."""
    left, right, bottom = 135, 475, 190
    parts = ['<svg class="ml-static-chart" viewBox="0 0 500 245" role="img" aria-label="Вероятности следующего токена: скоро 45%, завтра 30%, остальные токены вместе 25%">',
             '<title>Распределение вероятностей следующего токена, %</title>',
             '<text x="125" y="17" fill="#e6e9ec" text-anchor="end" font-size="16">Токен / группа</text>']
    for value in [0, 25, 50, 75, 100]:
        x = left + (right-left)*value/100
        parts.append(f'<path d="M{x} 25 V{bottom}" stroke="#293440"/>')
        anchor = 'end' if value == 100 else 'middle'
        parts.append(f'<text x="{x}" y="212" fill="#a7b0ba" text-anchor="{anchor}" font-size="16">{value}</text>')
    for y, lines, prob in [(45, ['скоро'], 45), (100, ['завтра'], 30), (155, ['Остальные', 'токены'], 25)]:
        for i, text in enumerate(lines):
            parts.append(f'<text x="125" y="{y+5+(i-(len(lines)-1)/2)*18}" fill="#e6e9ec" text-anchor="end" font-size="17">{text}</text>')
        width = (right-left)*prob/100
        parts.append(f'<rect x="{left}" y="{y-12}" width="{width}" height="24" fill="#5fd08a"/>')
        parts.append(f'<text x="{left+width+8}" y="{y+6}" fill="#e6e9ec" font-size="17">{prob}%</text>')
    parts += [f'<path d="M{left} 25 V{bottom} H{right}" fill="none" stroke="#647487"/>',
              '<text x="305" y="238" fill="#e6e9ec" text-anchor="middle" font-size="17">Вероятность следующего токена, %</text>', '</svg>']
    return ''.join(parts)


def speaker_timeline():
    """Use a labeled categorical y-axis and a seconds scale for the speaker intervals."""
    left, right, bottom = 90, 475, 135
    sx = lambda t: left+(right-left)*t/11
    parts = ['<svg class="ml-static-chart" viewBox="0 0 500 185" role="img" aria-label="Говорящий 1: от 0 до 4 и от 7 до 11 секунд; говорящий 2: от 4 до 7 секунд">',
             '<title>Кто говорил и когда: учебная запись длительностью 11 секунд</title>',
             '<text x="10" y="20" fill="#e6e9ec" font-size="17">Говорящий</text>']
    for start, end, y, color in [(0, 4, 45, '#6ab0f3'), (4, 7, 88, '#e0b25a'), (7, 11, 45, '#6ab0f3')]:
        parts.append(f'<rect x="{sx(start)}" y="{y}" width="{sx(end)-sx(start)}" height="25" rx="3" fill="{color}"/>')
    for label, y in [(1, 63), (2, 106)]:
        parts.append(f'<text x="72" y="{y}" text-anchor="end" fill="#e6e9ec" font-size="18">{label}</text>')
    for t in [0, 4, 7, 11]:
        parts.append(f'<path d="M{sx(t)} 32 V{bottom+5}" stroke="#647487" stroke-dasharray="3 4"/>')
        parts.append(f'<text x="{sx(t)}" y="157" text-anchor="middle" fill="#a7b0ba" font-size="16">{t}</text>')
    parts += [f'<path d="M{left} 30 V{bottom} H{right}" fill="none" stroke="#647487"/>',
              '<text x="282" y="181" text-anchor="middle" fill="#e6e9ec" font-size="17">Время записи, с</text>', '</svg>']
    return ''.join(parts)


EXTRA_SETUP = r'''
import json
import uuid
import re
from html import escape
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", context="notebook")

INTRO_CSS = r"""
.vec-root .wrap{font-family:system-ui,-apple-system,sans-serif;font-size:18px;line-height:1.6;}
.vec-root .wrap.wide{max-width:1080px;padding:24px 28px;}
.vec-root h2{margin:0 0 20px;border:0;padding:0;font-size:26px;line-height:1.25;}
.vec-root .ml-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,255px),1fr));gap:18px;margin:22px 0;}
.vec-root .ml-card{padding:16px;border-top:3px solid var(--green);background:#17212a;min-width:0;}
.vec-root .ml-card h3{margin:0 0 10px;font-size:20px;}.vec-root .ml-card p{font-size:16px;}
.vec-root .ml-card svg{display:block;width:100%;height:auto;}
.vec-root .ml-static-chart{display:block;width:100%;max-width:740px;height:auto;margin:20px auto;font-family:system-ui,sans-serif;}
.vec-root .ml-equation,.vec-root .ml-table{overflow-x:auto;max-width:100%;}
.vec-root .where{font-size:15px;line-height:1.7;}
.vec-root .ml-small{font-size:14px;color:var(--soft);}
.vec-root .ml-question{font-size:16px;border-left:3px solid var(--amber);padding-left:12px;margin-top:22px;}
.vec-root .readout{white-space:normal;font-family:system-ui,sans-serif;font-size:15px;line-height:1.6;}
.vec-root .en{white-space:normal;}.vec-root .box{font-size:16px;margin:18px 0;}.vec-root .box .t{font-size:14px;text-transform:none;letter-spacing:0;}
@media(max-width:600px){.vec-root .wrap.wide{padding:16px;font-size:16px;}.vec-root h2{font-size:23px;}.vec-root th,.vec-root td{padding:7px;font-size:14px;}}
"""

def intro_viz(body, widget=None, data=None):
    """Make every output independent of the surrounding Colab document."""
    body = re.sub(r"(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$.*?(?<!\\)\$",
                  lambda m: escape(m.group(0), quote=False), body, flags=re.DOTALL)
    root_id = "intro_" + uuid.uuid4().hex
    script = INTRO_WIDGET_JS + r"""
    (function(){
      const root = document.getElementById(__ROOT__);
      const kind = __KIND__;
      if(kind) window.IntroML.mount(root,kind,__DATA__);
      if(!root.textContent.includes('$')) return;
      if(!window.__INTRO_MATH_READY__){
        if(window.MathJax && window.MathJax.typesetPromise){
          window.__INTRO_MATH_READY__=window.MathJax.startup.promise;
        } else {
          window.MathJax={tex:{inlineMath:[['$','$']],displayMath:[['$$','$$']]},svg:{fontCache:'local'},startup:{typeset:false}};
          window.__INTRO_MATH_READY__=new Promise((resolve,reject)=>{
            const loader=document.createElement('script');
            loader.src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
            loader.onload=()=>window.MathJax.startup.promise.then(resolve,reject);
            loader.onerror=reject;document.head.appendChild(loader);
          });
        }
      }
      window.__INTRO_MATH_READY__=window.__INTRO_MATH_READY__.then(()=>window.MathJax.typesetPromise([root])).catch(()=>{
        const p=document.createElement('p');p.className='ml-small';
        p.textContent='Для отображения формул нужен интернет и повторный запуск ячейки. Интерактивы работают без сети.';root.appendChild(p);
      });
    })();
    """.replace('__ROOT__',json.dumps(root_id)).replace('__KIND__',json.dumps(widget)).replace('__DATA__',json.dumps(data,ensure_ascii=False))
    return ('<style>'+CSS+INTRO_CSS+'</style><div class="vec-root" data-widget="'+(widget or 'theory')+'" id="'+root_id+'"><div class="wrap wide">'+body+'</div></div><script>'+script+'</script>')
'''


md('''# Как модель учится на данных?
## Модуль ML · Занятие 1 — общая картина и основные термины

На прошлом семинаре мы подбирали веса линейной модели, уменьшая MSE. Теперь разберёмся,
как называется каждый шаг этой работы и как проверить, что модель полезна на новых данных.

**Маршрут:** задача → данные → модель → обучение → проверка → современные ML-системы.

Одна встреча: теория, три интерактивных эксперимента и обсуждение задач. Кейсы можно распределить
между группами, а оставшиеся задания закончить самостоятельно. Подробности в раскрывающихся
блоках и глоссарий можно читать после занятия. Данные синтетические; скачивать датасеты не нужно.
Запускайте ячейки по порядку. Для формул MathJax нужен интернет. Код оформления свёрнут,
короткие примеры Python открыты. Термины даны на русском и английском.
''')

# The assets are captured only at build time; the notebook needs no local files.
signal_data, complexity_data = simulation_data()
widget_source = (HERE / "intro_ml_widgets.js").read_text(encoding="utf-8")
code(theme.SETUP + '\nINTRO_WIDGET_JS = ' + repr(widget_source) + '\n' + EXTRA_SETUP
     + '\nSIGNAL_DATA = json.loads(' + repr(json.dumps(signal_data)) + ')'
     + '\nCOMPLEXITY_DATA = json.loads(' + repr(json.dumps(complexity_data, separators=(',', ':'))) + ')'
     + '\nprint("Готово: три интерактива и все учебные данные встроены в ноутбук.")', ("provided", "setup"))

md('## 1. От задачи к машинному обучению')
slide('Предсказать время новой доставки',
      lane([('История доставок', 'Расстояние, загруженность дорог и фактическое время'),
            ('Обучение', 'Подобрать модель по накопленным примерам'),
            ('Новая доставка', 'Оценить время до того, как заказ доставлен')])
      + definition('Машинное обучение', 'machine learning, ML',
        'Область методов, в которых система использует данные или опыт взаимодействия со средой, '
        'чтобы улучшать решение задачи по выбранному критерию качества.')
      + '<p>Далее сначала разберём <b>предсказание по примерам с известными значениями целевой переменной</b>. '
        'Затем поместим его на общую карту ML.</p>')

md('## 2. Карта машинного обучения')
slide('Как организовано обучение',
      ml_map()
      + '<p><b>Снижение размерности:</b> строим представление с меньшим числом координат, сохраняя полезную структуру данных. '
        '<b>Обучение с подкреплением:</b> учимся выбирать действия, чтобы увеличивать ожидаемую суммарную награду (reward).</p>'
      + box('Карта для ориентации', 'Это основные направления, а не исчерпывающая классификация. '
            'Регрессия и классификация описывают тип задачи; способ получения обучающего сигнала — другой вопрос.')
      + '<p class="ml-small">Упрощённая авторская схема. Отдельная <a href="https://scikit-learn.org/stable/machine_learning_map.html" target="_blank" rel="noopener">карта scikit-learn</a> '
        'помогает выбирать алгоритмы; её подробные ветви будем осваивать дальше.</p>')

slide('Число, категория или группы?',
      '<div class="ml-cards">' + ''.join('<div class="ml-card"><h3>'+title+'</h3>'+small_plot(title)+'<p>'+text+'</p></div>' for title,text in [
          ('Регрессия', 'Точка — доставка. По горизонтали — расстояние; по вертикали — целевая переменная: время. Линия — прогноз.'),
          ('Классификация', 'Точка — сообщение. Обе оси — признаки. Целевая переменная показана цветом: спам или не спам. Линия разделяет области прогнозируемых классов.'),
          ('Кластеризация', 'Точка — покупатель. Обе оси — признаки. Цвета обозначают найденные группы; целевая переменная заранее не задана.')]) + '</div>'
      + box('Число в столбце не определяет тип задачи', 'Коды «0 — спам, 1 — не спам» остаются категориями. '
            'При кластеризации номера групп тоже не являются величинами для сравнения «больше / меньше».')
      + '<p class="ml-small">Схематические рисунки: иллюстрация разных задач, не результат запуска алгоритма.</p>')

md('## 3. Объекты, признаки и целевая переменная')
slide('Одна строка — одна доставка',
      table(['Объект · observation', 'Расстояние, км · feature', 'Час заказа · feature', 'Время, мин · target'],
            [('Заказ 1', '2', '12', '18'), ('Заказ 2', '5', '18', '34'), ('Заказ 3', '3', '9', '23')])
      + definition('Объект / наблюдение', 'object / observation / example',
                   'Один случай, который мы описываем данными. Здесь это одна доставка.')
      + definition('Признак / фича', 'feature', 'Измеряемое или вычисляемое свойство объекта, которое подаём модели на вход.')
      + definition('Целевая переменная / таргет', 'target', 'Величина, которую модель должна предсказать. Здесь — фактическое время доставки.')
      + '<p><b>Разметка · labels / annotations</b> — известные значения целевой переменной для обучающих примеров. '
        '<b>Размеченные данные · labeled data</b> содержат признаки и известные значения целевой переменной. '
        'В классификации значение целевой переменной часто называют <b>меткой класса · class label</b>.</p>'
      + box('Значение целевой переменной может появиться позже', 'В момент заказа мы знаем расстояние и час. Фактическое время узнаем после доставки. '
            'Разметка не обязательно создаётся человеком: её можно получить из журнала завершённых заказов. '
            '«Правильный ответ» здесь означает наблюдаемый ответ; в нём тоже возможны ошибки измерения.'))

slide('Та же таблица математическим языком',
      eq(r'\mathbf{x}_i=(x_{i1},\ldots,x_{ip})^{\mathsf T},\qquad \mathcal D=\{(\mathbf{x}_i,y_i)\}_{i=1}^{n}.',
         r'$\mathbf{x}_i$ — вектор признаков (feature vector) объекта $i$; $x_{ij}$ — его признак $j$; '
         r'$p$ — число признаков; $y_i$ — значение целевой переменной у объекта $i$; $n$ — число объектов; '
         r'$\mathcal D$ — размеченный набор данных (dataset); $\mathsf T$ — транспонирование.')
      + eq(r'X=\begin{pmatrix}2&12\\5&18\\3&9\end{pmatrix}\in\mathbb R^{3\times2},\qquad \mathbf y=\begin{pmatrix}18\\34\\23\end{pmatrix}.',
           r'$X$ — матрица признаков (feature matrix): строки — объекты, столбцы — признаки; '
           r'$\mathbf y$ — вектор значений целевой переменной (target vector); $\mathbb R^{3\times2}$ — вещественные матрицы из 3 строк и 2 столбцов.')
      + box('Уже знакомый объект', 'Столбец X — один признак у разных доставок. Вектор одного объекта содержит разные признаки одной доставки.'))

code('''# A small labeled dataset: the target is stored separately from features.
deliveries = pd.DataFrame({
    "distance_km": [2., 5., 3.],
    "order_hour": [12., 18., 9.],
    "duration_min": [18., 34., 23.],
})
X = deliveries[["distance_km", "order_hour"]].to_numpy()
y = deliveries["duration_min"].to_numpy()
display(deliveries)
print("Размер матрицы признаков:", X.shape)
print("Размер вектора целевой переменной:", y.shape)''')

md('## 4. Модель, её параметры и прогноз')
slide('Модель превращает признаки в прогноз',
      lane([('Признаки x', 'Например, расстояние 5 км'), ('Модель fθ', 'Вычисляет ответ по своим параметрам'), ('Прогноз ŷ', 'Например, 28 минут')])
      + definition('Предсказательная модель', 'predictive model', 'Математическое правило, которое по входным признакам вычисляет прогноз. '
                   'У обучаемой модели это правило зависит от параметров, найденных по данным.')
      + eq(r'\widehat y_i=f_{\boldsymbol\theta}(\mathbf{x}_i).',
           r'$\widehat y_i$ — прогноз (prediction) для объекта $i$; шляпка отличает прогноз от наблюдаемого значения целевой переменной $y_i$; '
           r'$f_{\boldsymbol\theta}$ — модель с параметрами $\boldsymbol\theta$; $\mathbf{x}_i$ — признаки объекта.')
      + definition('Параметры модели', 'model parameters', 'Величины внутри модели, значения которых изменяются (корректируются) в процессе обучения. '
                   'Например, коэффициенты линейной модели.')
      + eq(r'\widehat y=b+wx,\qquad \boldsymbol\theta=(b,w).',
           r'$x$ — расстояние; $\widehat y$ — прогноз времени; $b$ — свободный член (intercept / bias); '
           r'$w$ — коэффициент, или вес (weight); $\boldsymbol\theta$ — оба параметра модели.')
      + '<p>При $b=8$ и $w=4$ модель для 5 км выдаёт 28 минут. Здесь значения заданы; '
        'на прошлом семинаре мы находили такие коэффициенты из данных.</p>')

slide('Обучение и применение — два разных шага',
      lane([('Признаки + целевая переменная', 'Обучающие примеры'), ('Алгоритм обучения', 'Подбирает параметры'), ('Обученная модель', 'Параметры найдены')])
      + lane([('Новые признаки', 'Ответ пока неизвестен'), ('Обученная модель', 'Использует найденные параметры'), ('Прогноз', 'Ответ модели')])
      + definition('Обучение', 'training / fitting', 'Процесс определения параметров модели по обучающим данным в соответствии с выбранной целью обучения.')
      + definition('Применение модели / инференс', 'inference / prediction', 'Вычисление результата обученной моделью для новых входных данных.')
      + '<p><b>Алгоритм обучения · learning algorithm</b> задаёт способ поиска параметров. '
        'Знакомый пример — градиентный спуск (gradient descent). Линейная модель задаёт форму прогноза, '
        'а градиентный спуск — способ подобрать её коэффициенты.</p>')

md('## 5. Закономерность, шум и приближение')
slide('Почему одинаковые признаки не гарантируют одинаковый ответ',
      eq(r'y=f^*(x)+\varepsilon,\qquad \widehat y=f_{\boldsymbol\theta}(x).',
           r'$x$ — известный признак; $y$ — наблюдаемый ответ; $f^*(x)$ — средний ответ при данном $x$; '
           r'$\varepsilon$ — отклонение от этого среднего; $\widehat y$ — прогноз модели; '
           r'$\boldsymbol\theta$ — её параметры. Для такого определения среднего $\mathbb E[\varepsilon\mid x]=0$: '
           'среднее отклонение при фиксированном x равно нулю.')
      + definition('Шум', 'noise', 'Часть изменчивости ответа, которую нельзя предсказать по доступным в этой постановке признакам.')
      + '<p>Даже для одинакового расстояния время меняется из-за ожидания, дорожной ситуации и других факторов. '
        'Добавив полезные признаки, иногда можно объяснить часть этого разброса.</p>'
      + box('Что именно мы знаем в эксперименте', 'В синтетике средняя зависимость задана нами. В реальных данных она неизвестна: '
            'модель лишь приближает её по наблюдениям. При обучении по MSE мы стремимся предсказывать средний ответ при заданных признаках.')
      + '<details><summary>Как получены учебные доставки</summary>'
      + eq(r'z=(x-5)/4.5,\quad f^*(x)=50+8z+24z^3,\quad \varepsilon=\sigma\xi,\quad \xi\sim\mathcal N(0,1).',
           r'$x$ — расстояние от 0.5 до 9.5 км; $z$ — вспомогательная координата; $f^*(x)$ — среднее время в минутах; '
           r'$\sigma$ — стандартное отклонение шума; $\xi$ — стандартная нормальная случайная величина; '
           r'$\varepsilon$ — шум в минутах. Нормальный шум выбран для иллюстрации; ML не требует нормальности всех данных.')
      + '</details>')

widget('signal', 'Одна зависимость — разные наблюдения',
       'Изменяйте стандартное отклонение шума. Сначала рассмотрите только точки, затем включите среднюю зависимость. '
       'При перемещении ползунка меняется масштаб тех же случайных отклонений.',
       'Можно ли провести кривую через все точки? Будет ли такая кривая лучше предсказывать новые доставки?', 'SIGNAL_DATA')

md('## 6. Чему учимся и на чём проверяем')
slide('Обобщение проверяют на новых объектах',
      definition('Обобщающая способность', 'generalization', 'Способность обученной модели хорошо решать задачу на новых объектах, '
                   'которые не использовались при её обучении. Проверка должна соответствовать будущим условиям применения.')
      + evaluation_flow()
      + eq(r'\mathcal D=\mathcal D_{\mathrm{train}}\;\dot\cup\;\mathcal D_{\mathrm{val}}\;\dot\cup\;\mathcal D_{\mathrm{test}}.',
           r'$\mathcal D$ — исходный набор наблюдений; $\mathcal D_{\mathrm{train}}$ — обучающая выборка (training set); '
           r'$\mathcal D_{\mathrm{val}}$ — валидационная выборка (validation set); '
           r'$\mathcal D_{\mathrm{test}}$ — тестовая выборка (test set); $\dot\cup$ — объединение без общих наблюдений.')
      + box('Отложенная выборка · holdout set', 'Данные, отложенные от подбора параметров. Часто так называют test; '
            'validation тоже отложена от обучения параметров. Всегда уточняйте роль выборки. '
            'Если постоянно выбирать модель по test, он начинает выполнять роль validation.')
      + '<details><summary>Когда случайно перемешать строки недостаточно</summary>'
        '<p>В этом занятии наблюдения независимы и получены одним способом. Для прогноза будущего '
        'может потребоваться разбиение по времени, а для нескольких записей одного человека — по людям. '
        'Дубликаты и связанные наблюдения по разные стороны разбиения могут сделать оценку слишком оптимистичной.</p></details>')

code('''# Independent synthetic examples: shuffle indices, keeping feature-target pairs together.
rng = np.random.default_rng(101)
distance = rng.uniform(0.5, 9.5, 150)
z = (distance - 5) / 4.5
duration = 50 + 8*z + 24*z**3 + rng.normal(0, 4, 150)
X_demo = distance.reshape(-1, 1)
y_demo = duration

indices = rng.permutation(len(y_demo))
train_idx, val_idx, test_idx = indices[:90], indices[90:120], indices[120:]
X_train, y_train = X_demo[train_idx], y_demo[train_idx]
X_val, y_val = X_demo[val_idx], y_demo[val_idx]
X_test, y_test = X_demo[test_idx], y_demo[test_idx]
print("Размеры train / validation / test:", len(y_train), len(y_val), len(y_test))

fig, ax = plt.subplots(figsize=(8, 4))
for ids, label, marker in [(train_idx, "Обучение · train", "o"),
                           (val_idx, "Выбор настроек · validation", "s")]:
    sns.scatterplot(x=distance[ids], y=duration[ids], label=label, marker=marker, ax=ax)
ax.set(xlabel="Расстояние, км", ylabel="Время, мин", title="Test отложен: его ответы пока не рассматриваем")
plt.tight_layout()
plt.show()''')

slide('Данные из будущего не должны помогать обучению',
      definition('Утечка данных', 'data leakage', 'Использование при обучении или выборе модели информации, '
                   'которая не должна быть доступна для этой цели. Это приводит к чрезмерно оптимистичной оценке качества.')
      + lane([('Сначала разделить данные', 'Зафиксировать train / validation / test'),
              ('По train найти настройки обработки', 'Например, среднее и масштаб признаков'),
              ('Применить ту же обработку', 'К train, validation, test и новым объектам')])
      + '<p>Для прогноза времени заказа нельзя использовать фактическое время его завершения как признак. '
        'А знакомый стандартизатор (standard scaler) нужно обучать только на train: '
        'средние и масштабы из test не участвуют в подготовке модели.</p>')

md('## 7. Loss и метрика: что уменьшаем и что измеряем')
slide('От ошибки одного прогноза к цели обучения',
      definition('Функция потерь', 'loss function', 'Функция, которая оценивает ошибку прогноза. '
                   'Зафиксируем обозначение для одного объекта: чем меньше потеря, тем лучше прогноз по этому критерию.')
      + eq(r'\ell(y_i,\widehat y_i)=(y_i-\widehat y_i)^2.',
           r'$\ell$ — квадратичная функция потерь (squared error loss); $y_i$ — наблюдаемый ответ; '
           r'$\widehat y_i$ — прогноз; $i$ — номер объекта. Если время измерено в минутах, потеря измерена в минутах в квадрате.')
      + eq(r'\begin{aligned}L_{\mathrm{train}}(\boldsymbol\theta)&=\frac{1}{n_{\mathrm{train}}}\sum_{i\in I_{\mathrm{train}}}\ell\big(y_i,f_{\boldsymbol\theta}(\mathbf{x}_i)\big),\\ \widehat{\boldsymbol\theta}&\approx\arg\min_{\boldsymbol\theta}L_{\mathrm{train}}(\boldsymbol\theta).\end{aligned}',
           r'$L_{\mathrm{train}}$ — средняя потеря на train, или эмпирический риск (empirical risk); '
           r'$I_{\mathrm{train}}$ — номера обучающих объектов; $n_{\mathrm{train}}$ — их количество; '
           r'$\ell$ — потеря одного прогноза; $\mathbf{x}_i,y_i$ — признаки и ответ; '
           r'$f_{\boldsymbol\theta}$ — модель; $\boldsymbol\theta$ — параметры; '
           r'$\widehat{\boldsymbol\theta}$ — найденные параметры; $\arg\min$ означает «значения параметров, при которых функция минимальна»; '
           r'$\approx$ напоминает, что численный алгоритм может найти лишь приближённое решение.')
      + learning_cycle()
      + box('Знакомая задача', 'Для квадратичной потери средняя потеря — это MSE. '
            'Именно её мы уменьшали градиентным спуском. В коде словом loss часто называют и потерю объекта, и среднюю потерю.'))

slide('Метрика оценивает результат модели',
      definition('Метрика / функционал качества', 'evaluation metric / scoring function',
                   'Числовой критерий, который оценивает качество работы модели на указанном наборе данных. '
                   'Для метрики нужно знать направление улучшения: меньше или больше.')
      + eq(r'\begin{aligned}\operatorname{MAE}_{S}&=\frac1{n_S}\sum_{i\in I_S}|y_i-\widehat y_i|,\\ '
           r'\operatorname{MSE}_{S}&=\frac1{n_S}\sum_{i\in I_S}(y_i-\widehat y_i)^2,\\ '
           r'\operatorname{RMSE}_{S}&=\sqrt{\operatorname{MSE}_{S}}.\end{aligned}',
           r'$S$ — выбранная выборка (train, validation или test); $I_S$ — номера её объектов; $n_S$ — её размер; '
           r'$y_i$ — ответ; $\widehat y_i$ — прогноз; MAE — mean absolute error, средняя абсолютная ошибка; '
           'MSE — mean squared error, средняя квадратичная ошибка; RMSE — root mean squared error, корень из MSE.')
      + table(['Роль', 'Пример', 'Как читаем результат'], [
          ('Цель обучения · training objective', 'Минимизируем MSE на train', 'По этой величине изменяем параметры.'),
          ('Оценка качества · evaluation', 'Считаем MAE на test', 'Средняя абсолютная ошибка прогноза в минутах.'),
          ('Та же формула, другая роль', 'Считаем MSE на test', 'Оцениваем уже выбранную модель; веса по test не меняем.')])
      + box('Loss и метрика могут совпадать', 'Разница — в роли, а не в обязательном различии формул. '
            'Метрики можно отслеживать и во время обучения. MAE и RMSE имеют единицы ответа; MSE — квадрат этих единиц. '
            'У всех трёх меньше — лучше. RMSE сильнее реагирует на крупные ошибки, чем MAE.')
      + '<p class="ml-small">«Функционал» здесь означает критерий, который сопоставляет модели число. '
        'В литературе так называют и среднюю потерю. Метрика качества не обязана быть метрикой расстояния из линейной алгебры.</p>')

widget('loss', 'Те же прогнозы — разные оценки ошибки',
       'Меняйте прогноз только для третьей доставки. Посмотрите, как меняются его потеря и общие показатели. '
       'Здесь ползунок меняет готовый прогноз: это исследование метрик, а не алгоритм обучения.',
       'Почему одна крупная ошибка сильнее меняет MSE? Как объяснить MAE в минутах заказчику?')

code('''# The same predictions can be evaluated with different criteria.
y_true_example = np.array([10., 20., 30.])
y_pred_example = np.array([12., 18., 40.])
squared_losses = (y_true_example - y_pred_example)**2
mse = np.mean(squared_losses)
mae = np.mean(np.abs(y_true_example - y_pred_example))
rmse = np.sqrt(mse)
display(pd.DataFrame({"Ответ": y_true_example, "Прогноз": y_pred_example,
                      "Квадратичная потеря": squared_losses}))
print(f"MSE: {mse:.2f} мин²; MAE: {mae:.2f} мин; RMSE: {rmse:.2f} мин")''')

md('## 8. Параметры и гиперпараметры')
slide('Что находит обучение, а что мы выбираем для обучения',
      definition('Гиперпараметры', 'hyperparameters', 'Настройки семейства моделей или процедуры обучения, '
                   'которые не определяются тем же шагом подбора параметров. Их задают заранее или выбирают по валидации.')
      + eq(r'\widehat y=w_0+w_1x+\cdots+w_dx^d.',
           r'$x$ — входной признак; $\widehat y$ — прогноз; $d$ — выбранная степень полинома; '
           r'$w_0,\ldots,w_d$ — коэффициенты, которые находим при обучении.')
      + table(['Параметры · parameters', 'Гиперпараметры · hyperparameters'], [
          ('Значения коэффициентов w₀, …, w_d', 'Степень полинома d: какие степени признака доступны модели'),
          ('Находятся по train при выбранной настройке', 'Задаются до конкретного запуска обучения; могут выбираться по validation'),
          ('После обучения определяют прогноз', 'Пример настройки обучения: шаг градиентного спуска · learning rate')])
      + box('Два уровня выбора', 'Выбрать степень 3 — выбрать форму модели. Найти четыре её коэффициента — обучить модель. '
            'Проверять степени по test нельзя: тогда test будет участвовать в выборе.')
      + '<p class="ml-small">В библиотеках параметры конструктора, например <code>degree</code>, '
        'часто называются parameters в смысле настроек программы. Здесь различаем их по роли в обучении.</p>')

md('## 9. Недообучение и переобучение')
slide('Малая ошибка на train ещё не означает хорошую модель',
      '<div class="ml-cards">'
      '<div class="ml-card"><h3>Недообучение</h3><p><b>Underfitting</b></p><p>Модель недостаточно хорошо усвоила закономерность: '
      'ошибка велика даже на train. Возможные причины — слишком простая форма или незавершённое обучение.</p></div>'
      '<div class="ml-card"><h3>Хорошее обобщение</h3><p><b>Good generalization</b></p><p>Модель даёт приемлемую ошибку '
      'на новых объектах. Полезный ориентир — качество по сравнению с простым решением.</p></div>'
      '<div class="ml-card"><h3>Переобучение</h3><p><b>Overfitting</b></p><p>Модель подстроилась под особенности обучающей выборки, '
      'которые плохо переносятся на новые данные. Обучающая ошибка выглядит слишком оптимистично.</p></div></div>'
      + definition('Сложность модели', 'model complexity', 'Способность семейства моделей описывать разнообразные зависимости. '
                   'В нашем эксперименте ею управляет максимальная степень полинома.')
      + box('Сложная модель не обязательно переобучена', 'Результат зависит также от количества данных, шума и обучения. '
            'Высокая ошибка из-за сильного шума сама по себе не означает недообучение. Небольшая разница между train и validation естественна; один разрыв не доказывает переобучение. '
            'В нашем эксперименте данные получены одинаково, поэтому удобно исследовать именно влияние сложности.'))

widget('complexity', 'Выберите сложность, затем откройте test',
       'Начните с 40 наблюдений и шума 4 минуты. Сравните степени 1, 3 и 12 по train и validation. '
       'Затем исследуйте размер train и шум. Перед итоговой проверкой выберите один вариант и нажмите '
       '«Зафиксировать выбор и открыть test». После этого менять настройки в этом повторе нельзя.',
       'Какая модель лучше по validation и почему? Что изменилось на test? '
       'Проверьте на новом повторе, всегда ли выигрывает одна и та же степень.', 'COMPLEXITY_DATA')

slide('Нужна точка отсчёта',
      definition('Базовое решение', 'baseline', 'Простое решение, с которым сравнивают более сложные модели.')
      + lane([('Baseline', 'Всегда предсказывать среднее время по train'), ('Модель по расстоянию', 'Использовать признаки доставки'), ('Сравнение', 'Одинаковые новые объекты и одна метрика')])
      + '<p>Для MSE среднее обучающих ответов — естественный постоянный прогноз. '
        'Среднее нельзя вычислять по ответам test. Сама по себе ошибка «5 минут» ещё не объясняет, '
        'полезна ли модель: важны базовое решение и требования задачи.</p>'
      + box('Схема работы', 'Поставить задачу → подготовить и разделить данные → обучить варианты на train → '
            'выбрать по validation → один раз оценить выбранный вариант на test → применять к новым объектам.'))

md('## 10. Простые задачи внутри современных систем')
slide('Генерация текста: много последовательных предсказаний',
      definition('Большая языковая модель', 'large language model, LLM', 'Языковая модель с большим числом параметров, '
                   'обученная на больших объёмах данных. Рассмотрим генерацию через предсказание следующего токена.')
      + '<p><b>Токен · token</b> — единица текста, с которой работает модель: слово, часть слова или символ. '
        '<b>Словарь · vocabulary</b> — набор возможных токенов.</p>'
      + lane([('Контекст', '«Курьер привезёт заказ …»'), ('Вероятности токенов', 'Вероятность каждого продолжения из словаря'), ('Следующий токен', 'Выбираем и добавляем к контексту')])
      + token_probabilities()
      + '<p class="ml-small">Условный учебный пример: вероятности придуманы; «остальные токены» — сумма вероятностей всех других продолжений. Реальные токены могут делить слова на части.</p>'
      + box('Связь с классификацией', 'На одном шаге модель предсказывает распределение вероятностей по категориям-токенам. '
            'Повторяя этот шаг, получаем последовательность. Всю систему генерации нельзя свести к одному выбору категории.')
      + definition('Самообучение по целям из данных', 'self-supervised learning', 'Способ обучения, при котором значения целевой переменной '
                   'формируются из самих данных. При предсказании следующего токена контекст — вход, '
                   'а следующий токен исходного текста — обучающий ответ.')
      + '<p class="ml-small">Базовое обучение LLM — один пример self-supervised learning. '
        'Дополнительные этапы обучения могут быть организованы иначе. '
        '<a href="https://huggingface.co/docs/transformers/tasks/language_modeling" target="_blank" rel="noopener">Источник: Hugging Face — causal language modeling.</a></p>')

slide('Диаризация: кто говорил и когда',
      definition('Диаризация говорящих', 'speaker diarization', 'Разделение записи на фрагменты с указанием, '
                   'какой говорящий произносит речь в каждый момент.')
      + lane([('Запись', 'Выделяем речевые фрагменты'), ('Векторы голосов', 'Получаем эмбеддинги'), ('Кластеризация', 'Группируем похожие голоса')])
      + speaker_timeline()
      + '<p class="ml-small">Учебная временная шкала: числа 1 и 2 — обозначения говорящих, а не количественная величина.</p>'
      + '<p><b>Эмбеддинг · embedding</b> — векторное представление объекта, в котором полезные свойства '
        'отражены в координатах. Сравнение голосовых векторов мы уже использовали в семинаре по речи.</p>'
      + box('Кластеризация — часть системы', 'Один распространённый подход группирует фрагменты по близости голосовых векторов. '
            'Метки «говорящий 1» и «говорящий 2» не сообщают имён. Отдельные блоки такой системы могут быть обучены с учителем. Распознавание произнесённых слов — отдельная задача.')
      + '<p class="ml-small">Схема одного подхода, а не всех систем диаризации. '
        '<a href="https://www.pyannote.ai/speaker-diarization-api" target="_blank" rel="noopener">Источник: pyannote.</a></p>')

slide('Регрессия помогает принимать решения',
      lane([('Данные заказа', 'Расстояние, время суток, дорожная ситуация'), ('Регрессионная модель', 'Предсказывает время доставки'), ('Система доставки', 'Использует прогноз при распределении заказов')])
      + '<p>Модель отвечает на узкий вопрос: <b>«Сколько минут займёт доставка?»</b> '
        'Приложение использует ответ вместе с другими данными и правилами. '
        'Оценка времени и выбор курьера — разные шаги системы.</p>'
      + box('Как анализировать любой ML-пример', 'Укажите объект, доступные признаки и желаемый результат. '
            'Затем выясните, откуда берётся обучающий сигнал и как проверяется качество.')
      + '<p class="ml-small">Это иллюстративная архитектура сервиса, не описание конкретной компании.</p>')

md('## 11. Практика и обсуждение')
# Preserve the author's exercise wording; do not add questions or explanatory notes.
slide('Задача 1. Опишите постановку задачи',
      '<p>Для каждого случая укажите объект, признаки, ожидаемый результат и тип задачи. Если требуется разметка — объясните, откуда её получить.</p>'
      + '<ol>'
      + '<li>Предсказать стоимость подержанного автомобиля.</li>'
      + '<li>Первичный кредитный скоринг - предсказать, вернет ли заемщик полученные средства.</li>'
      + '<li>Предсказать, выдержит ли построенный жилой многоквартирный дом землетрясение определенной магнитуды или при определенной балльности.</li>'
      + '<li>Определить, какова "резервационная цена" поездки в такси. (Это максимально возможная цена, при которой данный конкретный клиент ещё готов воспользоваться услугой. Если цена выше - отказывается))</li>'
      + '<li>Определить, какой объем воды будет накоплен в Токтогульском водохранилище к началу лета. Насколько такой прогноз можно сделать в принципе? что влияет на точность такого прогноза?</li>'
      + '</ol>')
md('…', ("student-answer",))

slide('Задача 2',
      '<ol>'
      + '<li>Вы решили сестре перевести некоторую сумму денег на карту в банковском приложении так как у нее скоро свадьба. При попытке это сделать банк Вам блокирует счет. Почему такое могло произойти? что за система могла сработать? Для чего такие технические решения придумали и как на ваш взгляд они работают?</li>'
      + '<li>Вы в очередной раз воспользовались каршерингом (сервис краткосрочной аренды автомобиля). Однако у Вас на работе случилась беда - Вас сократили... В чувствах полной фрустрации и отчаяния вы едете домой... Но беда не приходит одна - вас останавливает ДПС (инспектор ГАИ) и просит вас показать ему аккаунт вашего сервисного профиля и в тоже самое время вам звонят из службы поддержки каршеринговой службы с вопросом "пользуетесь ли вы в данный момент сервисом?" Почему такое могло произойти?</li>'
      + '<li>Вы на известной доске объявлений (типа Авито) продаете велосипед. Вам написал потенциальный покупатель и у вас начинается переписка в чате самой платформы. И тут Вам приходит уведомление с предупреждением о мошеннических действиях и мерах предосторожности... Как это работает?</li>'
      + '</ol>')
md('…', ("student-answer",))

slide('Задача 3. Посчитайте и объясните ошибку',
      '<p>Фактическое время трёх доставок: <b>15, 25, 35 минут</b>. '
      'Прогнозы модели: <b>18, 21, 40 минут</b>.</p>'
      '<ol><li>Вручную найдите квадратичную потерю каждого прогноза, MSE и MAE.</li>'
      '<li>Проверьте результаты в NumPy.</li><li>Объясните единицы измерения обеих метрик.</li>'
      '<li>Можно ли по этим числам понять, была ли модель обучена на этих же объектах?</li></ol>')
code('''y_task = np.array([15., 25., 35.])
pred_task = np.array([18., 21., 40.])
# TODO: Compute the individual squared losses, their mean, and the mean absolute error.
losses_task = None
mse_task = None
mae_task = None
if mse_task is not None and mae_task is not None:
    print("Потери:", losses_task)
    print("MSE:", mse_task, "MAE:", mae_task)''', ("student-core",))
md('**Ваше объяснение:**\n\n…', ("student-answer",))

slide('Задача 4. Найдите проблему в процессе',
      '<p>Исследователь вычислил средние и масштабы признаков по всей таблице. Затем разделил её на train и test, '
      'обучил пять моделей, выбрал лучшую по test и сообщил эту же ошибку как итоговое качество.</p>'
      '<p>Назовите две проблемы и предложите исправленный порядок действий. '
      'Разделите выбор параметров и гиперпараметров.</p>')
md('**Исправленный порядок и объяснение:**\n\n…', ("student-answer",))

md('## 12. Глоссарий · glossary')
glossary = [
    ('Данные', [
        ('Объект / наблюдение', 'object / observation / example', 'Один описываемый случай: доставка, письмо, запись.'),
        ('Признак / фича', 'feature', 'Свойство объекта, используемое как вход модели.'),
        ('Вектор признаков объекта', 'feature vector', 'Набор признаков одного объекта; в таблице соответствует строке.'),
        ('Матрица признаков', 'feature matrix', 'Таблица X: строки — объекты, столбцы — признаки.'),
        ('Целевая переменная / таргет', 'target', 'Величина, которую требуется предсказать.'),
        ('Разметка / метка', 'labels / annotations; class label', 'Известные значения целевой переменной; в классификации — метки классов.'),
        ('Размеченные данные', 'labeled data', 'Примеры с признаками и известными значениями целевой переменной.'),
        ('Набор данных / датасет', 'dataset', 'Совокупность наблюдений для задачи.'),
        ('Вектор целевой переменной', 'target vector', 'Значения целевой переменной в том же порядке, что и строки X.'),
    ]),
    ('Модель и обучение', [
        ('Машинное обучение', 'machine learning, ML', 'Методы улучшения решения задач на основе данных или опыта по выбранному критерию.'),
        ('Предсказательная модель', 'predictive model', 'Математическое правило вычисления прогноза по признакам.'),
        ('Прогноз / предсказание', 'prediction', 'Результат, вычисленный моделью для входного объекта.'),
        ('Параметры модели', 'model parameters', 'Величины внутри модели, значения которых изменяются (корректируются) в процессе обучения.'),
        ('Вес / коэффициент', 'weight / coefficient', 'Параметр, задающий вклад соответствующего признака в линейной формуле.'),
        ('Свободный член', 'intercept / bias', 'Добавочный постоянный член модели.'),
        ('Гиперпараметры', 'hyperparameters', 'Настройки формы модели или процедуры обучения, выбираемые вне подбора её параметров.'),
        ('Обучение', 'training / fitting', 'Определение параметров по обучающим данным согласно цели обучения.'),
        ('Алгоритм обучения', 'learning algorithm', 'Процедура, определяющая, как искать параметры.'),
        ('Градиентный спуск', 'gradient descent', 'Обновление параметров против направления градиента целевой функции.'),
        ('Шаг обучения', 'learning rate', 'Настройка величины шага при обновлении параметров градиентным спуском.'),
        ('Применение / инференс', 'inference', 'Вычисление результатов с помощью уже обученной модели.'),
        ('Шум', 'noise', 'Непредсказуемая по имеющимся признакам часть изменчивости ответа.'),
    ]),
    ('Проверка качества', [
        ('Обучающая выборка', 'training set / train', 'Данные для подбора параметров модели.'),
        ('Валидационная выборка', 'validation set / validation', 'Данные для сравнения вариантов и выбора настроек.'),
        ('Тестовая выборка', 'test set / test', 'Отложенные данные для итоговой оценки выбранной модели.'),
        ('Отложенная выборка', 'holdout set', 'Данные, не используемые для подбора параметров; нужно уточнять роль.'),
        ('Обобщающая способность', 'generalization', 'Способность хорошо работать на новых объектах в целевых условиях.'),
        ('Утечка данных', 'data leakage', 'Использование информации, которая не должна участвовать в обучении или выборе модели.'),
        ('Функция потерь', 'loss function', 'Критерий ошибки прогноза; в формулах урока ℓ относится к одному объекту.'),
        ('Средняя потеря / эмпирический риск', 'average loss / empirical risk', 'Средняя потеря на рассматриваемой выборке.'),
        ('Цель обучения', 'training objective', 'Критерий, который оптимизирует процедура обучения.'),
        ('Метрика / функционал качества', 'evaluation metric / scoring function', 'Число, оценивающее качество модели на указанном наборе данных.'),
        ('Средняя квадратичная ошибка', 'mean squared error, MSE', 'Среднее квадратов ошибок; меньше — лучше.'),
        ('Средняя абсолютная ошибка', 'mean absolute error, MAE', 'Среднее модулей ошибок в единицах ответа; меньше — лучше.'),
        ('Корень из MSE', 'root mean squared error, RMSE', 'Корень средней квадратичной ошибки в единицах ответа; меньше — лучше.'),
        ('Сложность модели', 'model complexity', 'Способность семейства моделей описывать разнообразные зависимости.'),
        ('Недообучение', 'underfitting', 'Недостаточно хорошее усвоение закономерности, заметное и на обучающих данных.'),
        ('Переобучение', 'overfitting', 'Подстройка под особенности train, которые плохо переносятся на новые данные.'),
        ('Базовое решение', 'baseline', 'Простое решение, относительно которого оценивают другие модели.'),
    ]),
    ('Карта ML и современные примеры', [
        ('Обучение с учителем', 'supervised learning', 'Обучение на примерах с известными значениями целевой переменной.'),
        ('Регрессия', 'regression', 'Предсказание числовых величин.'),
        ('Классификация', 'classification', 'Предсказание принадлежности к заданным категориям.'),
        ('Обучение без учителя', 'unsupervised learning', 'Поиск структуры данных без заданной для этой задачи целевой переменной.'),
        ('Кластеризация', 'clustering', 'Объединение объектов в группы по выбранному понятию сходства.'),
        ('Снижение размерности', 'dimensionality reduction', 'Представление объектов меньшим числом координат с сохранением полезной структуры.'),
        ('Обучение с подкреплением', 'reinforcement learning, RL', 'Обучение действиям по обратной связи с целью увеличить ожидаемую суммарную награду.'),
        ('Награда', 'reward', 'Числовая обратная связь, используемая в обучении с подкреплением.'),
        ('Самообучение по целям из данных', 'self-supervised learning', 'Формирование значений целевой переменной из самих данных.'),
        ('Большая языковая модель', 'large language model, LLM', 'Языковая модель с большим числом параметров, обученная на больших объёмах данных.'),
        ('Токен', 'token', 'Единица текста, используемая языковой моделью.'),
        ('Словарь токенов', 'vocabulary', 'Набор токенов, которыми оперирует модель.'),
        ('Эмбеддинг', 'embedding', 'Векторное представление объекта, отражающее полезные свойства.'),
        ('Диаризация говорящих', 'speaker diarization', 'Определение того, какой говорящий произносит речь в каждый момент записи.'),
    ]),
]
for title, rows in glossary:
    slide('Глоссарий: '+title.lower(), table(['Термин', 'English', 'Короткое определение'], rows))

md('''## Источники и продолжение

- [scikit-learn: словарь терминов](https://scikit-learn.org/stable/glossary.html).
- [Google ML Crash Course: обучение с учителем](https://developers.google.com/machine-learning/intro-to-ml/supervised).
- [Google ML Crash Course: параметры и гиперпараметры](https://developers.google.com/machine-learning/crash-course/linear-regression/hyperparameters).
- [scikit-learn: разбиение данных, обучение и проверка](https://scikit-learn.org/stable/modules/cross_validation.html).
- [scikit-learn: утечка данных и подготовка признаков](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage).
- [scikit-learn: метрики качества](https://scikit-learn.org/stable/modules/model_evaluation.html).
- [scikit-learn: недообучение и переобучение на полиномах](https://scikit-learn.org/stable/auto_examples/model_selection/plot_underfitting_overfitting.html).
- [scikit-learn: карта выбора алгоритмов](https://scikit-learn.org/stable/machine_learning_map.html).
- [Hugging Face: предсказание следующего токена](https://huggingface.co/docs/transformers/tasks/language_modeling).
- [pyannote: этапы диаризации](https://www.pyannote.ai/speaker-diarization-api).

Повторение: [MSE и обучение линейной модели](../math_for_ds/mse_optimization.ipynb),
[производная и градиент](../math_for_ds/matan_seminar.ipynb),
[векторы голосов](../math_for_ds/seminar_1.ipynb).

**Далее:** полный процесс работы с линейной регрессией — от постановки задачи и базового решения
до обучения, проверки на отложенных данных и содержательного разбора результата.
''')

nb = nbf.v4.new_notebook(cells=cells, metadata=json.loads(json.dumps(theme.META)))
nb.metadata['colab']['name'] = '01_intro_ml.ipynb'
nb.metadata['lesson'] = {
    'module': 'LinModels', 'number': 1, 'duration_minutes': 120,
    'status': 'Draft for author review; not yet taught.',
    'source': 'build_intro_ml.py + intro_ml_diagrams.py + intro_ml_widgets.js + ../math_for_ds/theme.py (build-time only)',
    'prerequisites': ['../math_for_ds/matan_seminar.ipynb', '../math_for_ds/mse_optimization.ipynb'],
    'data': 'Seeded synthetic deliveries and exact small arrays; no runtime data downloads.',
    'format': 'Presentation-like dark HTML, bilingual definitions, three standalone JS/SVG widgets, Python examples, unanswered tasks and glossary.',
}
for index, cell in enumerate(nb.cells):
    cell.id = hashlib.sha256(f'intro-ml-{index}-{cell.source}'.encode()).hexdigest()[:12]
nbf.validate(nb)
path = HERE / '01_intro_ml.ipynb'
nbf.write(nb, path)
print(f'Wrote {path}: {len(cells)} cells, no saved outputs.')
