# Data Science & Classic Machine Learning — Course Materials

A hands-on **introduction to Data Science for beginners**. It starts with the **mathematics for Data Science**
(statistics and linear algebra, taught on real data from the first lesson) and continues with **classic Machine
Learning** (linear models, decision trees, ensembles, dimensionality reduction, clustering). The course is built around
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
| 1. Data as vectors | 1–4 | Descriptive statistics, distributions, vectors, dot product, covariance | 13 math lessons; covariance, correlation and multicollinearity followed by calculus and MSE seminars; general basis theory remains pending |
| 2. Matrices as operators | 5–8 | Operators, determinant, eigenvectors, PCA/SVD | L10–L12 introduce operations, transformations, rank, linear systems, inverse and the 2D determinant; eigenvectors and later groundwork remain planned |
| 3. Estimation and first models | 9–12 | Least squares, linear regression, MLE, logistic regression | Calculus, MSE regression and `LinModels/02–04` completed; OLS, preprocessing and Ridge taught; `LinModels/05` adds model diagnostics for review |
| 4. Classic DS and the project | 13–16 | Trees, ensembles, metrics; research project | Modules `DT/` and `unsupervised/` ready |

The full teaching sequence, with notes on every lesson, is in **[docs/COURSE_MAP.md](docs/COURSE_MAP.md)**.

## What's inside

| Path | What it is | Status |
|---|---|---|
| [`math_for_ds/`](math_for_ds/) | **Mathematics for DS:** Colab lessons L1–L13; speaker, calculus and MSE seminars; homework | actively developed |
| [`LinModels/`](LinModels/) | **Introduction to ML and linear models:** visual introduction and four applied seminars | ML2–ML4 completed; ML5 awaiting review/classroom use; ML1 classroom status unconfirmed |
| [`practice/`](practice/) | Lalafo phones and cars; bus travel/waiting and bus comparison with bootstrap and permutations (both with student and KEY versions) | Lalafo: L1–L4; buses: L1–L6, then L7–L8 |
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
   **bus practicum** «Моссовет → Азия Молл» — [student notebook](practice/practicum_mossovet_asia_mall.ipynb),
   [teacher's answers (KEY)](practice/practicum_mossovet_asia_mall_KEY.ipynb)
4. **L7** Sampling distribution, standard error, CLT → **L8** Confidence intervals and bootstrap →
   **bus resampling practicum** — [student notebook](practice/practicum_mossovet_asia_mall_bootstrap.ipynb),
   [teacher's answers (KEY)](practice/practicum_mossovet_asia_mall_bootstrap_KEY.ipynb)
   → **[L9 hypotheses, p-values and statistical significance](math_for_ds/09_stat_hypotheses.ipynb)**
   (one final statistics meeting, using delivery data)
5. **[L10 matrices and matrix multiplication](math_for_ds/10_matrices.ipynb)** — return to linear algebra:
   rows and columns, operations in NumPy, geometric transformations and composition, weighted sums for all
   observations at once. One theory meeting, followed by four short class/homework tasks: rotation, car prices
   with given weights, several weight sets at once, and a small threshold network's forward calculation.
6. **[L11 linear dependence and rank](math_for_ds/11_linear_dependence_rank.ipynb)** — redundant columns,
   reachable linear combinations, a plane collapsing to a line or point, and square-matrix singularity defined
   through rank. Four interactive visuals, NumPy examples and three short student tasks on synthetic data.
7. **[L12 linear systems and inverse matrices](math_for_ds/12_linear_systems_inverse.ipynb)** — one, no or infinitely
   many solutions; recovering an input with an inverse; a short geometric introduction to the determinant.
   Three interactive visuals connect the theory to NumPy. Six adapted exercises cover matrix equations,
   linear systems and a first weight calculation using a supplied least-squares formula; two are optional.
   The core theory is one meeting, with exercises available for class or homework.
8. **[L13 covariance and correlation](math_for_ds/13_covariance_correlation.ipynb)** — synthetic apartment
   area, room count and price; covariance and Pearson correlation, their matrices, and the connection to
   centered feature vectors. A brief Spearman/rank comparison, exact and near multicollinearity, and feature
   transformations prepare later modelling. Four interactive visuals accompany NumPy/pandas/SciPy/seaborn
   examples. Eight tasks add hand calculations and interpretation: five core tasks plus three extensions
   for class or homework. The entire practice block need not fit the theory meeting.
9. **[Calculus seminar](math_for_ds/matan_seminar.ipynb)** →
   **[MSE optimization seminar](math_for_ds/mse_optimization.ipynb)** — derivatives, partial derivatives,
   gradient descent and a hand-coded linear model, including vectorized calculations. Both seminars have been
   completed in class. They are maintained by hand.
10. **[ML introduction](LinModels/01_intro_ml.ipynb)** — a visual introduction to models, features and targets,
    labelled data, training/inference, train/validation/test sets, loss versus evaluation metrics, parameters
    versus hyperparameters, and underfitting/overfitting. Synthetic experiments, modern application diagrams
    and a Russian–English glossary. Awaiting review and classroom use.
11. **[First applied linear-regression seminar](LinModels/02_linear_regression.ipynb)** — Ames house prices,
    training-only exploration, a mean baseline, one- and three-feature sklearn models, coefficient interpretation
    and validation metrics. Completed in class on November 4, including the matrix OLS derivation; the derivation
    and MAPE explanation were added to the notebook on November 5. The fixed test set stays unused.
12. **[Data preprocessing seminar](LinModels/03_data_preprocessing.ipynb)** — missing values and train-only
    imputation, `fit/transform`, scaling, Pipeline, categorical features and OneHot/ColumnTransformer. Compare
    numeric and mixed-feature OLS models using MAE, RMSE and MAPE on the same validation set. Mainly Markdown/Python,
    with one interactive HTML explainer on transformers; maintained by hand. Completion was confirmed on
    November 9; the exact class date is not recorded.
13. **[Regularization seminar](LinModels/04_regularization.ipynb)** — coefficient instability, multicollinearity,
    loss geometry, Ridge and feature scale; a brief geometric Lasso comparison. Synthetic examples and an
    embedded HTML/JS widget lead to Ridge on the same Ames pipeline and split. Students select alpha using
    validation MAE, inspect RMSE/MAPE and plot training/validation curves; test stays unused. Completion was
    confirmed on November 17; the exact class date is not recorded.
14. **[Model diagnostics seminar](LinModels/05_model_diagnostics.ipynb)** — R², residuals and group errors,
    five difficult predictions compared with similar training houses, coefficients and prediction contributions,
    synthetic/Ames bootstrap stability and permutation feature importance. An optional synthetic OLS example
    separates significance from predictive importance. Reuses the Ames split and preprocessing; test stays unused.
    Mainly Markdown/Python, maintained by hand, for review.
15. Cross-validation and further model selection, eigenvectors and PCA remain planned. Phase 4 materials are in
   `DT/` (trees → bias–variance → bagging/RF → gradient boosting) and `unsupervised/` (01 → 05).

## Data and related repositories

- **Datasets:** [huggingface.co/aiacademy-kg](https://huggingface.co/aiacademy-kg). All the school's datasets used in
  the course are published there.
- **Code:** [github.com/ai-academy-bish](https://github.com/orgs/ai-academy-bish/repositories). The school's GitHub
  organization: scrapers that build these datasets, and seminar and project repositories.

## How to open the notebooks

**Google Colab (recommended).** The generated `math_for_ds/` and `LinModels/` lessons are built for Colab, with collapsed HTML theory cells
and self-contained HTML/JS visuals. Short Python examples show how to calculate the same quantities and plot
them with matplotlib/seaborn. Run cells in order and complete the marked tasks. To open a notebook straight from
GitHub, use

```
https://colab.research.google.com/github/simonlobgromov/ML_classic_course/blob/main/<path-to-notebook>
```

or *File → Open notebook → GitHub* in Colab. Formulas need an internet connection (MathJax from a CDN);
the JS widgets work offline once their cells have been run, without further Python calls.

`LinModels/02_linear_regression.ipynb` uses Markdown/Python. `03_data_preprocessing.ipynb` follows that format
with one self-contained interactive HTML explainer on `fit/transform` before section 2; `04_regularization.ipynb`
adds one embedded geometry widget to its Markdown/Python seminar. `05_model_diagnostics.ipynb` uses Markdown/Python
with one collapsible R² explanation using native HTML `details/summary`. Its similar-house explorer uses
`ipywidgets` and needs a running Python kernel; a static example and an ordinary function call are also provided.
Their small Ames CSV downloads from the author's source without a Kaggle login; run cells in order.
All four applied seminars retain the same split, with test unused.

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
- The ML introduction is generated with `venv/bin/python LinModels/build_intro_ml.py`. Edit that builder and
  `LinModels/intro_ml_widgets.js`; its notebook embeds the data and widgets and runs without those source files.
- Edit `LinModels/02_linear_regression.ipynb`, `03_data_preprocessing.ipynb`, `04_regularization.ipynb` and
  `05_model_diagnostics.ipynb` directly: they have no build scripts. Preserve the embedded widgets,
  Markdown/Python cells and unanswered tasks;
  the HTML/SVG format of `LinModels/01` is unchanged.
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
