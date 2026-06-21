# Classic Machine Learning — Course Materials

A hands-on **introduction to Data Science and classic Machine Learning for beginners**.
The course is built around **interactive Jupyter/Colab notebooks** and an
**interactive theory handbook**, and walks from school-level math all the way up to
ensembles (random forests and gradient boosting).

> **Language note.** The teaching materials (notebook prose, plots, the theory handbook)
> are written in **Russian**. This README is in English so the project is easy to navigate
> for everyone. Code comments are in English.

---

## ⚠️ Disclaimer / Дисклеймер / Эскертүү

> **EN — Work in progress.** This handbook is under active development. The material is
> **incomplete, unedited, and unfinished**. It may contain **errors, methodological gaps,
> and inconsistencies**. Please use it critically and at your own discretion.

> **RU — Пособие в стадии разработки.** Материал **неполный, не вычитанный и не
> дописанный**. В нём возможны **ошибки, методологические недоработки и несостыковки**.
> Пользуйтесь критически и на свой страх и риск.

> **KY — Колдонмо иштелип жатат.** Материал **толук эмес, текшерилбеген жана аякталбаган**.
> Анда **каталар, методологиялык кемчиликтер жана дал келбестиктер** болушу мүмкүн. Сын
> көз караш менен жана өз жоопкерчилигиңизде пайдаланыңыз.

---

## Who this is for

Beginners in Data Science and Machine Learning who want to **understand the math, not just
call `.fit()`**. You need only school-level mathematics to start — everything else
(probability, derivatives, gradients, convexity) is reintroduced from scratch in the
handbook.

## What's inside

| Path | What it is | Status |
|------|------------|--------|
| `DT/` | **Decision Trees & Ensembles** — the most developed module | actively developed |
| `DT/theory/` | **Interactive theory handbook** (HTML), from school math to boosting | in progress |
| `DT/*.ipynb` | Lesson notebooks: decision trees, bias–variance, bagging/RF, gradient boosting | in progress |
| `DT/*.pdf` | Accompanying lecture slides | — |
| `Clustering/` | Clustering module | planned / empty |

### The interactive theory handbook (`DT/theory/`)

A self-contained set of HTML pages with **live, slider-driven widgets** (pure SVG + vanilla
JavaScript — no build step, no frameworks) and full, expandable derivations.

**Chapters:**

1. Math warm-up — probability, mean/variance, expectation, logarithm, derivative & gradient, convexity & Jensen
2. Glossary — English ML terms with Russian translations
3. Supervised learning setup — loss functions and empirical risk
4. Decision trees — impurity criteria, information gain, full derivations
5. Bias–variance decomposition
6. Bagging & random forests
7. Gradient boosting — including the link to gradient descent / SGD
8. Formula cheat sheet

**How to open it:**

```bash
# just open the entry page in your browser
open DT/theory/index.html          # macOS
xdg-open DT/theory/index.html      # Linux
start DT/theory/index.html         # Windows
```

- The **interactive graphs work fully offline.**
- Math formulas are rendered by **MathJax from a CDN**, so formula rendering needs an
  internet connection. The graphs do not.

## Notebooks

The lesson notebooks are standard Jupyter notebooks and also open directly in
**Google Colab**.

### Run locally

```bash
# 1. create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate

# 2. install dependencies
pip install -r requirements.txt

# 3. launch Jupyter and open a notebook from DT/
jupyter notebook
```

### Run in Google Colab

Open any `DT/*.ipynb` in [Google Colab](https://colab.research.google.com/) and run the
cells top to bottom. Most dependencies are preinstalled there; a few are installed by the
notebooks as needed.

## Suggested learning path

1. Skim **`DT/theory/index.html`** chapters 1–3 to get the language and the framing.
2. Work through the notebooks in this order:
   `dt_demo` → `bias_variance_demo` → `bagging_rf` → `gradient_boosting`.
3. After each notebook, revisit the matching handbook chapter (4 → 5 → 6 → 7) for the
   full derivations and the interactive widgets.

## Contributing & feedback

Because the material is a work in progress, **corrections, bug reports, and pedagogical
suggestions are very welcome** — especially on derivations, terminology, and any
inconsistencies between the notebooks and the handbook.

## License

To be decided. For now: educational use.
