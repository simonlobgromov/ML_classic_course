# Data Science & Classic Machine Learning — Course Materials

A hands-on **introduction to Data Science for beginners**. It starts with the **mathematics for Data Science**
(statistics and linear algebra, taught on real data from the first lesson) and continues with **classic Machine
Learning** (decision trees, ensembles, dimensionality reduction, clustering). The course is built around
**interactive Google Colab notebooks**.

> **Language note.** The teaching materials (notebook prose, plots, widgets, the theory handbook) are written in
> **Russian**. This README and the project documentation are in English so that everyone on the team can navigate the
> project. Code comments are in English.

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

Beginners who know basic Python (numpy, pandas) and want to **understand the mathematics behind Data Science, not just
call `.fit()`**. School mathematics is enough to start: everything else is introduced from scratch, on real data
(Bishkek apartment listings, Lalafo marketplace ads, the Bishkek public-transport feed, speech embeddings).

## The course at a glance

The plan is a 16-week programme in four phases ([`syllabus.docx`](syllabus.docx), in Russian). Its topic order is
adapted from MIT 18.065. Each student works with one "anchor" dataset throughout.

| Phase | Weeks | Theme | Status |
|---|---|---|---|
| 1. Data as vectors | 1–4 | Descriptive statistics, distributions, vectors, dot product, covariance | **In progress:** 7 lessons, 2 seminars, homework, 3 practicums |
| 2. Matrices as operators | 5–8 | Operators, determinant, eigenvectors, PCA/SVD | Planned |
| 3. Estimation and first models | 9–12 | Least squares, linear regression, MLE, logistic regression | Planned |
| 4. Classic DS and the project | 13–16 | Trees, ensembles, metrics; research project | Modules `DT/` and `unsupervised/` ready |

The full teaching sequence, with notes on every lesson, is in **[docs/COURSE_MAP.md](docs/COURSE_MAP.md)**.

## What's inside

| Path | What it is | Status |
|---|---|---|
| [`math_for_ds/`](math_for_ds/) | **Mathematics for DS:** Colab lessons L1–L7, a seminar, homework, the bus practicum | actively developed |
| [`practice/`](practice/) | Practicums on dirty real data: Lalafo phones and cars (five cases each) | done for L1–L4 |
| [`DT/`](DT/) | **Decision trees and ensembles:** 4 notebooks and an interactive HTML theory handbook | ready, to be re-linked to the math block |
| [`unsupervised/`](unsupervised/) | **Unsupervised learning:** SVD/PCA/t-SNE, K-Means, GMM/EM, DBSCAN/HDBSCAN, hierarchical clustering | ready, to be re-linked to the math block |
| [`docs/`](docs/) | Course map and the protocol for contributors and AI agents | living documents |
| [`syllabus.docx`](syllabus.docx) | The 16-week programme (Russian), used as a guide | reference |

### Teaching order so far

1. **L1** Vectors → **L2** Dot product and cosine similarity → **Seminar 1** (speaker embeddings) →
   vector-algebra **homework**
2. **L3** Population and sample, descriptive statistics, z-scores → house.kg **seminar project** (separate repo) →
   **L4** Percentiles, boxplots, IQR, robust scaling → **practicums** Lalafo phones and cars
3. **L5** Probability, Bernoulli, binomial, normal, three sigma → **L6** From histogram to probability (PDF, CDF, z) →
   **bus practicum** «Моссовет → Азия Молл»
4. **L7** Sampling distribution, standard error, CLT → *next: L8 statistical tests*
5. Phase 4: `DT/` (trees → bias–variance → bagging/RF → gradient boosting), `unsupervised/` (01 → 05)

## Data and related repositories

- **Datasets:** [huggingface.co/aiacademy-kg](https://huggingface.co/aiacademy-kg). All the school's datasets used in
  the course are published there.
- **Code:** [github.com/ai-academy-bish](https://github.com/orgs/ai-academy-bish/repositories). The school's GitHub
  organization: scrapers that build these datasets, and seminar and project repositories.

## How to open the notebooks

**Google Colab (recommended).** The `math_for_ds/` lessons are built for Colab: theory is collapsed into form cells,
and the interactive widgets are self-contained HTML/JS. Choose *Runtime → Run all*. To open a notebook straight from
GitHub, use

```
https://colab.research.google.com/github/simonlobgromov/ML_classic_course/blob/main/<path-to-notebook>
```

or *File → Open notebook → GitHub* in Colab. Formulas need an internet connection (MathJax from a CDN); the widgets
work without it.

**Locally.**

```bash
python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install jupyter                 # if it is not installed yet
jupyter notebook
```

In local Jupyter, HTML/JS outputs may require *File → Trust Notebook*. The `DT/` and `unsupervised/` notebooks use
`ipywidgets` sliders, which need a running kernel.

**The DT theory handbook** (`DT/theory/`) is a set of HTML pages with slider-driven widgets (pure SVG and vanilla
JavaScript, no build step). Open `DT/theory/index.html` in a browser. Chapters: math warm-up, glossary, supervised
setup, decision trees, bias–variance, bagging and random forests, gradient boosting, a formula cheat sheet.

## For contributors

- Start with **[docs/COURSE_MAP.md](docs/COURSE_MAP.md)** (what exists and in what order, what students already know,
  open questions) and **[docs/AGENT_PROTOCOL.md](docs/AGENT_PROTOCOL.md)** (how to build, edit and validate
  material, for people and AI agents alike).
- Most lessons in `math_for_ds/` are **generated**: edit `build_lessonN.py`, then run
  `venv/bin/python math_for_ds/build_lessonN.py`. Some notebooks are edited by hand and must not be regenerated; the
  list is in AGENT_PROTOCOL §4.
- Conventions in brief: lesson prose in academic Russian; code comments in English; a «Где:» glossary under every
  formula; no ready answers in student notebooks; tasks use only concepts already taught.

## Third-party materials

`DT/*.pdf` are lecture notes by **E. A. Sokolov (HSE Faculty of Computer Science, 2021)**, included as supplementary
reading. They are not original materials of this course. Check their terms before redistributing them.

## Contributing & feedback

Because the material is a work in progress, **corrections, bug reports and teaching suggestions are very welcome**,
especially on derivations, terminology, and inconsistencies between lessons.

## License

To be decided. For now: educational use.
