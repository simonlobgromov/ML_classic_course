"""Build self-contained, responsive SVG flowcharts for the introductory ML lesson."""
from html import escape, unescape
import math
import re
import textwrap


COLORS = {
    "blue": "#6ab0f3", "green": "#5fd08a", "gold": "#e0b25a",
    "rose": "#e0757f", "violet": "#bd9ce8", "ink": "#e6e9ec",
    "soft": "#a7b0ba", "edge": "#64798c", "bg": "#111820",
}

CSS = """
.ml-diagram{width:100%;max-width:1040px;margin:22px auto 26px;overflow:hidden;}
.ml-diagram svg{display:block;width:100%;height:auto;overflow:hidden;}
.ml-diagram .ml-diagram-narrow{display:none;}
.ml-diagram text{font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;}
@media(max-width:760px){
  .ml-diagram .ml-diagram-wide{display:none;}
  .ml-diagram .ml-diagram-narrow{display:block;max-width:440px;margin:0 auto;}
}
"""


def _plain(value):
    """Keep diagram labels literal even if a caller supplies simple HTML."""
    return unescape(re.sub(r"<[^>]*>", "", str(value)))


def _lines(value, width, size):
    count = max(8, int(width / (size * 0.54)))
    return [line for part in _plain(value).split("\n")
            for line in (textwrap.wrap(part, width=count, break_long_words=False,
                                       break_on_hyphens=False) or [""])]


class _Canvas:
    def __init__(self, width, height, title, description):
        self.width, self.height = width, height
        self.title, self.description = title, description
        self.edges, self.nodes = [], []

    def text(self, x, y, value, color="soft", size=18, weight=400, anchor="middle"):
        self.nodes.append(
            f'<text x="{x:g}" y="{y:g}" fill="{COLORS.get(color, color)}" '
            f'font-size="{size:g}" font-weight="{weight}" text-anchor="{anchor}">'
            f'{escape(str(value))}</text>'
        )

    def arrow(self, points, color="edge", dashed=False, end=True):
        """Draw routed edges and their arrowheads without shared SVG marker IDs."""
        if len(points) < 2:
            return
        stroke = COLORS.get(color, color)
        path = "M " + " L ".join(f"{x:g} {y:g}" for x, y in points)
        dash = ' stroke-dasharray="6 5"' if dashed else ""
        self.edges.append(f'<path d="{path}" fill="none" stroke="{stroke}" '
                          f'stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"{dash}/>')
        if end:
            (px, py), (x, y) = points[-2:]
            angle = math.atan2(y - py, x - px)
            ux, uy = math.cos(angle), math.sin(angle)
            length, half = 9, 4.7
            corners = [(x, y), (x - length * ux + half * uy, y - length * uy - half * ux),
                       (x - length * ux - half * uy, y - length * uy + half * ux)]
            self.edges.append('<polygon points="' + " ".join(f"{a:g},{b:g}" for a, b in corners)
                              + f'" fill="{stroke}"/>')

    def box(self, x, y, width, height, title, caption="", color="blue", shape="process",
            head=21, body=18):
        stroke = COLORS.get(color, color)
        if shape == "data":
            indent = 13
            pts = [(x + indent, y), (x + width, y), (x + width - indent, y + height), (x, y + height)]
            element = '<polygon points="' + " ".join(f"{a:g},{b:g}" for a, b in pts) + '"'
            text_width = width - 46
        elif shape == "decision":
            pts = [(x + width / 2, y), (x + width, y + height / 2),
                   (x + width / 2, y + height), (x, y + height / 2)]
            element = '<polygon points="' + " ".join(f"{a:g},{b:g}" for a, b in pts) + '"'
            text_width = width * .6
        else:
            element = f'<rect x="{x:g}" y="{y:g}" width="{width:g}" height="{height:g}" rx="12"'
            text_width = width - 28
        self.nodes.append(element + f' fill="#17212d" stroke="{stroke}" stroke-width="1.8"/>')
        title_lines = _lines(title, text_width, head)
        caption_lines = _lines(caption, text_width, body) if caption else []
        height_text = len(title_lines) * head * 1.2 + len(caption_lines) * body * 1.26
        if caption_lines:
            height_text += 7
        baseline = y + (height - height_text) / 2 + head
        for value in title_lines:
            self.text(x + width / 2, baseline, value, color, head, 600)
            baseline += head * 1.2
        if caption_lines:
            baseline += 7 + (body - head) * .3
            for value in caption_lines:
                self.text(x + width / 2, baseline, value, "ink", body)
                baseline += body * 1.26

    def svg(self, variant):
        return (f'<svg class="ml-diagram-{variant}" viewBox="0 0 {self.width} {self.height}" '
                f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{escape(self.title, quote=True)}">'
                f'<title>{escape(self.title)}</title><desc>{escape(self.description)}</desc>'
                + "".join(self.edges + self.nodes) + '</svg>')


def _responsive(wide, narrow):
    return '<style>' + CSS + '</style><div class="ml-diagram">' + wide.svg("wide") + narrow.svg("narrow") + '</div>'


def lane(items):
    """Return a connected process lane; each item is a (heading, caption) pair."""
    items = list(items)
    if not items:
        return ""
    count, gap, margin = len(items), 44, 22
    width = (1000 - margin * 2 - gap * (count - 1)) / count
    head, body = 21, 18
    def box_height(title, caption, w, hfont, bfont):
        return max(104, 32 + len(_lines(title, w - 46, hfont)) * hfont * 1.2
                   + len(_lines(caption, w - 46, bfont)) * bfont * 1.26 + 7)
    height = max(box_height(a, b, width, head, body) for a, b in items)
    description = " → ".join(_plain(a) + ": " + _plain(b) for a, b in items)
    wide = _Canvas(1000, math.ceil(height + 34), "Последовательность действий", description)
    narrow_heights = [box_height(a, b, 288, 20, 18) for a, b in items]
    narrow = _Canvas(360, math.ceil(sum(narrow_heights) + 43 * (count - 1) + 28),
                     "Последовательность действий", description)
    top = 14
    for i, (title, caption) in enumerate(items):
        x = margin + i * (width + gap)
        shape = "data" if re.search(r"данн|признак|запись|история|контекст|прогноз|новая доставка", _plain(title), re.I) else "process"
        color = ["blue", "green", "gold"][i % 3]
        wide.box(x, 16, width, height, title, caption, color, shape, head, body)
        narrow.box(36, top, 288, narrow_heights[i], title, caption, color, shape, 20, 18)
        if i < count - 1:
            wide.arrow([(x + width, 16 + height / 2), (x + width + gap - 3, 16 + height / 2)], "green")
            narrow.arrow([(180, top + narrow_heights[i] + 3), (180, top + narrow_heights[i] + 36)], "green")
        top += narrow_heights[i] + 43
    return _responsive(wide, narrow)


def ml_map():
    """Return a branching map of learning settings and their typical tasks."""
    title = "Карта машинного обучения"
    description = ("Машинное обучение разделяется здесь по организации обучения. С учителем: известна целевая "
                   "переменная; примеры задач — регрессия и классификация. Без учителя: целевая переменная "
                   "не задана; примеры — кластеризация и снижение размерности. С подкреплением: агент "
                   "выбирает действия и получает награду от среды.")
    wide, narrow = _Canvas(1020, 646, title, description), _Canvas(360, 1130, title, description)
    wide.box(350, 16, 320, 82, "Машинное обучение", "Machine learning", "blue", head=23, body=19)
    branches = [
        ("С учителем", "Supervised learning\nИзвестны значения целевой переменной", "blue",
         [("Регрессия", "Regression\nПредсказать число"), ("Классификация", "Classification\nПредсказать класс")]),
        ("Без учителя", "Unsupervised learning\nЦелевая переменная не задана", "green",
         [("Кластеризация", "Clustering\nНайти группы объектов"), ("Снижение размерности", "Dimensionality reduction\nМеньше координат")]),
        ("С подкреплением", "Reinforcement learning\nДействия → награда", "gold",
         [("Действия и награда", "Actions and rewards\nУчиться выбирать действия")]),
    ]
    wide.arrow([(510, 98), (510, 127)], end=False)
    wide.arrow([(170, 127), (850, 127)], end=False)
    narrow.box(36, 14, 288, 86, "Машинное обучение", "Machine learning", "blue", head=21, body=18)
    narrow.arrow([(180, 100), (180, 124), (16, 124), (16, 941)], end=False)
    for i, (name, caption, color, children) in enumerate(branches):
        x = 20 + 340 * i
        wide.arrow([(x + 150, 127), (x + 150, 164)], color)
        wide.box(x, 164, 300, 140, name, caption, color, head=22, body=18)
        ys = [352, 496] if len(children) == 2 else [390]
        wide.arrow([(x + 150, 304), (x + 150, 328), (x + 16, 328), (x + 16, ys[-1] + 63)], color, end=False)
        for (head, body), y in zip(children, ys):
            wide.arrow([(x + 16, y + 63), (x + 46, y + 63)], color)
            wide.box(x + 46, y, 254, 126, head, body, color, head=20, body=17)
        y = [158, 518, 878][i]
        narrow.arrow([(16, y + 63), (42, y + 63)], color)
        narrow.box(42, y, 300, 126, name, caption, color, head=21, body=18)
        child_y = [y + 160, y + 267] if len(children) == 2 else [y + 160]
        # Two sibling nodes share a branch rail rather than forming a sequence.
        narrow.arrow([(192, y + 126), (192, y + 143), (54, y + 143), (54, child_y[-1] + 45)], color, end=False)
        for (head, body), yy in zip(children, child_y):
            narrow.arrow([(54, yy + 45), (72, yy + 45)], color)
            narrow.box(72, yy, 270, 90, head, body, color, head=19, body=17)
    return _responsive(wide, narrow)


def learning_cycle():
    """Return the parameter-learning feedback loop, with a separate target input."""
    title = "Цикл обучения модели"
    description = ("Обучающие признаки поступают в модель с параметрами theta. Прогноз сравнивается с известным "
                   "значением целевой переменной. Вычисляется значение функции потерь. Алгоритм обучения "
                   "корректирует параметры модели, после чего цикл повторяется.")
    wide, narrow = _Canvas(1020, 500, title, description), _Canvas(360, 820, title, description)
    # The wide feedback edge returns to the model, never to the target data.
    wide.arrow([(196, 207), (244, 207)], "blue")
    wide.arrow([(434, 207), (478, 207)], "blue")
    wide.arrow([(656, 207), (704, 207)], "blue")
    wide.arrow([(841, 102), (841, 155)], "gold")
    wide.arrow([(841, 259), (841, 354)], "rose")
    wide.arrow([(704, 406), (574, 406)], "rose")
    wide.arrow([(339, 354), (339, 259)], "green")
    wide.box(14, 155, 182, 104, "Признаки x", "Из train", "blue", "data", 22, 18)
    wide.box(244, 155, 190, 104, "Модель", "Параметры θ", "blue", head=22)
    wide.box(478, 155, 178, 104, "Прогноз ŷ", "Значение модели", "blue", "data", 22, 18)
    wide.box(704, 18, 274, 84, "Наблюдаемое y", "Целевая переменная", "gold", "data", 21, 18)
    wide.box(704, 155, 274, 104, "Сравнить", "Прогноз ŷ и факт y", "gold", head=22)
    wide.box(704, 354, 274, 104, "Значение loss", "Ошибка на train", "rose", head=22)
    wide.box(244, 354, 330, 104, "Алгоритм обучения", "Корректирует параметры θ", "green", head=22)
    wide.text(510, 491, "Повторяем цикл обучения", "soft", 18)
    narrow.arrow([(180, 92), (180, 126)], "blue")
    narrow.arrow([(180, 218), (180, 241), (98, 241), (98, 270)], "blue")
    narrow.arrow([(98, 362), (98, 387), (180, 387), (180, 413)], "blue")
    narrow.arrow([(262, 374), (262, 387), (180, 387)], "gold", end=False)
    narrow.arrow([(180, 505), (180, 545)], "rose")
    narrow.arrow([(180, 629), (180, 670)], "rose")
    narrow.arrow([(300, 720), (346, 720), (346, 172), (300, 172)], "green")
    narrow.box(60, 14, 240, 78, "Признаки x", "Из train", "blue", "data", 21, 18)
    narrow.box(60, 126, 240, 92, "Модель", "Параметры θ", "blue", head=21, body=18)
    narrow.box(30, 270, 136, 92, "Прогноз ŷ", "От модели", "blue", "process", 20, 17)
    narrow.box(194, 270, 136, 104, "Наблюдаемое y", "Целевая\nпеременная", "gold", "process", 18, 17)
    narrow.box(60, 413, 240, 92, "Сравнить", "Прогноз ŷ и факт y", "gold", head=21, body=18)
    narrow.box(60, 545, 240, 84, "Значение loss", "Ошибка на train", "rose", head=21, body=18)
    narrow.box(60, 670, 240, 100, "Алгоритм обучения", "Корректирует параметры θ", "green", head=20, body=18)
    narrow.text(180, 807, "Повторяем цикл", "soft", 18)
    return _responsive(wide, narrow)


def evaluation_flow():
    """Return the split/train/select/test workflow with a validation feedback loop."""
    title = "Обучение, выбор модели и итоговая проверка"
    description = ("Данные заранее разделяются на train, validation и test. Train используется для обучения "
                   "параметров. Validation сравнивает варианты. Пока выбор не завершён, обучается новый вариант. "
                   "После фиксации модели выполняется итоговая проверка на test; обратной стрелки от test к выбору нет.")
    wide, narrow = _Canvas(1020, 770, title, description), _Canvas(360, 1145, title, description)
    wide.box(358, 14, 304, 80, "Исходные данные", "Разделить заранее", "blue", "data", 22, 18)
    wide.arrow([(510, 94), (510, 119)], end=False)
    wide.arrow([(160, 119), (854, 119)], end=False)
    for center, color in [(160, "blue"), (507, "green"), (854, "violet")]:
        wide.arrow([(center, 119), (center, 148)], color)
    wide.box(24, 148, 272, 86, "Train · обучение", "Подбор параметров", "blue", "data", 21, 18)
    wide.box(371, 148, 272, 86, "Validation", "Выбор варианта модели", "green", "data", 21, 18)
    wide.box(718, 148, 272, 86, "Test · закрыт", "До фиксации выбора", "violet", "data", 21, 18)
    wide.arrow([(160, 234), (160, 280)], "blue")
    wide.arrow([(160, 366), (160, 404)], "blue")
    wide.arrow([(296, 447), (371, 447)], "blue")
    wide.arrow([(507, 234), (507, 404)], "green")
    wide.arrow([(507, 490), (507, 534)], "green")
    wide.arrow([(389, 590), (10, 590), (10, 323), (24, 323)], "green")
    wide.arrow([(625, 590), (718, 590)], "green")
    wide.arrow([(854, 633), (854, 679)], "violet")
    wide.arrow([(990, 191), (1007, 191), (1007, 722), (990, 722)], "violet")
    wide.box(24, 280, 272, 86, "Обучить параметры", "Только на train", "blue", head=21, body=18)
    wide.box(24, 404, 272, 86, "Модель-кандидат", "Один вариант", "blue", head=21, body=18)
    wide.box(371, 404, 272, 86, "Сравнить варианты", "По ошибке validation", "green", head=21, body=18)
    wide.box(389, 534, 236, 112, "Выбор\nзавершён?", color="green", shape="decision", head=21)
    wide.text(193, 574, "Нет: другой вариант", "green", 18)
    wide.text(670, 574, "Да", "green", 18)
    wide.box(718, 547, 272, 86, "Выбранная модель", "Параметры зафиксированы", "green", head=21, body=18)
    wide.box(718, 679, 272, 86, "Итоговая проверка", "Один раз на test", "violet", head=21, body=18)
    # The narrow version keeps separate rails for validation, test and the retry loop.
    narrow.box(60, 14, 240, 80, "Исходные данные", "Разделить заранее", "blue", "data", 20, 18)
    narrow.arrow([(180, 94), (180, 119)], end=False)
    narrow.arrow([(68, 119), (292, 119)], end=False)
    for x, title_, caption, color in [(18, "Train", "Обучение", "blue"), (130, "Validation", "Выбор", "green"), (242, "Test", "Закрыт", "violet")]:
        narrow.arrow([(x + 50, 119), (x + 50, 150)], color)
        narrow.box(x, 150, 100, 78, title_, caption, color, head=18, body=17)
    narrow.arrow([(68, 228), (68, 248), (150, 248), (150, 278)], "blue")
    narrow.arrow([(150, 364), (150, 410)], "blue")
    narrow.arrow([(150, 492), (150, 546)], "blue")
    narrow.arrow([(180, 228), (180, 244), (294, 244), (294, 589), (266, 589)], "green")
    narrow.arrow([(150, 632), (150, 656)], "green")
    narrow.arrow([(34, 714), (14, 714), (14, 321), (34, 321)], "green")
    narrow.arrow([(150, 772), (150, 834)], "green")
    narrow.arrow([(150, 920), (150, 1018)], "violet")
    narrow.arrow([(292, 228), (292, 238), (348, 238), (348, 1067), (266, 1067)], "violet")
    narrow.box(34, 278, 232, 86, "Обучить параметры", "Только на train", "blue", head=20, body=18)
    narrow.box(34, 410, 232, 82, "Модель-кандидат", "Один вариант", "blue", head=20, body=18)
    narrow.box(34, 546, 232, 86, "Сравнить варианты", "По ошибке validation", "green", head=20, body=18)
    narrow.box(34, 656, 232, 116, "Выбор\nзавершён?", color="green", shape="decision", head=20)
    narrow.text(17, 743, "Нет", "green", 18, anchor="start")
    narrow.text(173, 811, "Да", "green", 18, anchor="start")
    narrow.box(34, 834, 232, 86, "Выбранная модель", "Параметры зафиксированы", "green", head=20, body=17)
    narrow.box(34, 1018, 232, 98, "Итоговая проверка", "Один раз на test", "violet", head=20, body=18)
    return _responsive(wide, narrow)


__all__ = ["lane", "ml_map", "learning_cycle", "evaluation_flow"]
