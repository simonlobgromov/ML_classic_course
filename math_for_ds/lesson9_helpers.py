"""Numerical experiments and plots embedded by build_lesson9.py; no runtime file import."""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams.update({"figure.figsize": (10, 4), "axes.spines.top": False,
                     "axes.spines.right": False})
COLOR_A, COLOR_B = "#2b75b8", "#24865b"
COLOR_OBS, COLOR_TAIL = "#7b43b5", "#d76e21"


def delivery_samples(n=200, gain=6, seed=9120):
    """Independent shifted-exponential samples; preserve prefixes across n."""
    a = 10 + np.random.default_rng(seed).exponential(20, n)
    b = 10 + np.random.default_rng(seed + 1).exponential(20, n) - gain
    return a, b


def permutation_differences(a, b, repeats, rng):
    """Shuffle group labels without replacement; retain original group sizes."""
    pooled = np.concatenate([a, b])
    diffs = np.empty(repeats)
    for i in range(repeats):
        shuffled = rng.permutation(pooled)
        diffs[i] = shuffled[len(a):].mean() - shuffled[:len(a)].mean()
    return diffs


def bootstrap_differences(a, b, repeats, rng):
    """Resample independent groups separately, preserving each sample size."""
    diffs = np.empty(repeats)
    for i in range(repeats):
        a_star = rng.choice(a, size=len(a), replace=True)
        b_star = rng.choice(b, size=len(b), replace=True)
        diffs[i] = b_star.mean() - a_star.mean()
    return diffs


def extreme_mask(differences, observed):
    """Include ties with a small floating-point tolerance."""
    tolerance = 100 * np.finfo(float).eps * max(1, abs(observed))
    return np.abs(differences) >= abs(observed) - tolerance


def permutation_p(differences, observed):
    return (np.count_nonzero(extreme_mask(differences, observed)) + 1) / (len(differences) + 1)


def plot_deliveries(a, b):
    fig, ax = plt.subplots(figsize=(9, 3.7))
    bins = np.histogram_bin_edges(np.concatenate([a, b]), bins=24)
    sns.histplot(a, bins=bins, stat="density", color=COLOR_A, alpha=.35, label="A: прежний способ", ax=ax)
    sns.histplot(b, bins=bins, stat="density", color=COLOR_B, alpha=.35, label="B: новый способ", ax=ax)
    ax.axvline(a.mean(), color=COLOR_A, lw=2, label=f"Среднее A: {a.mean():.2f}")
    ax.axvline(b.mean(), color=COLOR_B, lw=2, label=f"Среднее B: {b.mean():.2f}")
    ax.set(xlabel="Время доставки, мин", ylabel="Плотность, 1/мин",
           title="Доставки двух способов: данные имеют правый хвост")
    ax.legend(fontsize=9)
    fig.tight_layout()
    plt.show()


def plot_permutations(differences, observed, ax=None):
    own_figure = ax is None
    if own_figure:
        _, ax = plt.subplots(figsize=(10, 3.7))
    mask = extreme_mask(differences, observed)
    radius = max(abs(observed), np.max(np.abs(differences)), .5) * 1.15
    bins = np.linspace(-radius, radius, 36)
    # Keep the extreme-result tails visible even when their observed counts are tiny.
    ax.axvspan(-radius, -abs(observed), color=COLOR_TAIL, alpha=.12)
    ax.axvspan(abs(observed), radius, color=COLOR_TAIL, alpha=.12)
    ax.hist([differences[~mask], differences[mask]], bins=bins, stacked=True,
            color=["#94a3b8", COLOR_TAIL], label=["Ближе к нулю", "Не менее экстремальные"])
    ax.axvline(0, color="#64748b", ls=":")
    ax.axvline(observed, color=COLOR_OBS, lw=2, label=f"Наша разница: {observed:.2f}")
    if abs(observed) > 1e-12:
        ax.axvline(-observed, color=COLOR_OBS, ls="--", label="Та же величина в другую сторону")
    ax.set(xlim=(-radius, radius),
           xlabel="Разница средних B − A после перестановки, мин", ylabel="Число перестановок",
           title="Нулевая модель: меняем метки A и B")
    ax.legend(fontsize=8)
    if own_figure:
        plt.tight_layout()
        plt.show()


def plot_bootstrap(differences, observed, ci, ax=None):
    own_figure = ax is None
    if own_figure:
        _, ax = plt.subplots(figsize=(10, 3.7))
    sns.histplot(differences, bins=35, color=COLOR_B, ax=ax)
    ax.axvspan(*ci, color=COLOR_B, alpha=.17, label="Центральные 95% бутстрап-разниц")
    ax.axvline(observed, color=COLOR_OBS, lw=2, label=f"Наша разница: {observed:.2f}")
    ax.axvline(0, color="#64748b", ls="--", label="Нулевая разница")
    ax.set(xlabel="Разница средних B − A в повторных выборках, мин", ylabel="Число повторений",
           title="Бутстрап: оцениваем точность разницы")
    ax.legend(fontsize=8)
    if own_figure:
        plt.tight_layout()
        plt.show()


def plot_interval(observed, ci, ax=None):
    own_figure = ax is None
    if own_figure:
        _, ax = plt.subplots(figsize=(10, 2.8))
    ax.hlines(0, *ci, color=COLOR_B, lw=5)
    ax.scatter(observed, 0, s=65, color=COLOR_OBS, zorder=3, label="Оценка разницы")
    ax.axvline(0, color="#64748b", ls="--", label="Нет средней разницы")
    ax.axvline(-5, color=COLOR_TAIL, ls="--", label="Выигрыш B в 5 минут")
    ax.annotate(f"95%-й ДИ: [{ci[0]:.2f}; {ci[1]:.2f}]",
                ((ci[0] + ci[1]) / 2, 0), xytext=(0, 20), textcoords="offset points", ha="center")
    left, right = min(ci[0], -5), max(ci[1], 0)
    pad = max(1, .15 * (right - left))
    ax.set(xlim=(left - pad, right + pad), ylim=(-.5, .7), yticks=[],
           xlabel="Истинная средняя разница B − A, мин", title="Ноль и практический порог — разные ориентиры")
    ax.legend(loc="lower left", fontsize=8)
    if own_figure:
        plt.tight_layout()
        plt.show()


def null_experiments(count=100, start=0):
    """Independent experiments with a true null, each using a fresh permutation test."""
    values = []
    for i in range(start, start + count):
        a, b = delivery_samples(n=50, gain=0, seed=9300 + 3 * i)
        diffs = permutation_differences(a, b, 999, np.random.default_rng(100000 + i))
        values.append(permutation_p(diffs, b.mean() - a.mean()))
    return np.array(values)


def plot_null_pvalues(values, ax=None):
    own_figure = ax is None
    if own_figure:
        _, ax = plt.subplots(figsize=(10, 3.5))
    colors = np.where(values <= .05, COLOR_TAIL, "#94a3b8")
    ax.scatter(np.arange(1, len(values) + 1), values, c=colors, s=24)
    ax.axhline(.05, color=COLOR_TAIL, ls="--", label="Уровень значимости α = 0,05")
    ax.set(ylim=(-.02, 1.02), xlabel="Номер нового исследования", ylabel="p-value",
           title="Эффекта нет во всех исследованиях. Ложные сигналы выделены цветом")
    ax.legend(fontsize=9)
    if own_figure:
        plt.tight_layout()
        plt.show()


