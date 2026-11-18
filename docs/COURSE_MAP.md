# Course Map

**What has been built, where it lives, in what order it is taught, and why it looks the way it does.**

> **This document is kept up to date as the course grows.** Last updated: **2026-11-17**, after recording ML4's classroom completion and adding the model-diagnostics seminar for review.
> It combines a course programme, a table of contents and methodological notes.
> The teaching materials are in Russian; this map is in English so the whole team can use it.
> How to work in the repo (build, validate, edit) is in [AGENT_PROTOCOL.md](AGENT_PROTOCOL.md).

**Contents**

1. [The course in one page](#1-the-course-in-one-page)
2. [Phases and status](#2-phases-and-status)
3. [Teaching sequence](#3-teaching-sequence)
4. [Lesson and practicum notes](#4-lesson-and-practicum-notes)
5. [Syllabus vs. what was built](#5-syllabus-vs-what-was-built)
6. [What students know so far](#6-what-students-know-so-far)
7. [ML modules](#7-ml-modules)
8. [Datasets](#8-datasets)
9. [Methodological conventions](#9-methodological-conventions)
10. [Open questions and next steps](#10-open-questions-and-next-steps)
11. [Changelog](#11-changelog)

**How to maintain this map.** Whenever a lesson, practicum or homework is added or substantially changed:
add a row to §3, a note to §4, update §5 and the concept inventory in §6, and add a line to §11.
If a material changes position in the sequence, update the "Relies on" column too.

---

## 1. The course in one page

**Audience.** Beginners who already know basic Python (numpy, pandas). The mathematics is taught from scratch, on real data.

**Shape.** A 16-week programme in four phases. Statistics and linear algebra run as two parallel tracks that merge at
covariance (week 4), PCA (week 8) and linear regression (weeks 9–10). After that come classic ML models and a research
project. The plan is in [`syllabus.docx`](../syllabus.docx) (Russian).

**Principles** (from the syllabus, condensed):

1. **Mathematics arrives to answer a question about data**, not the other way round. Each topic is tied to an ML
   application within 1–2 weeks.
2. **Topic order follows MIT 18.065** (*Linear Algebra and Learning from Data*), not the classic 18.06:
   column space → multiplication as composition → orthogonality and projections → least squares → eigenvectors →
   SVD → covariance matrices.
3. **"By hand, then with the library", with the weight on interpretation.** Each concept is first computed in numpy and
   then checked against pandas/sklearn. LLMs now write the code, so the student's value is in checking and
   interpreting it. Tasks therefore say "explain what this means *for these data*", not "prove" or "derive".
4. **Anchor dataset.** Each student keeps one dataset for the whole course and returns to it in every phase.
5. **Assessment** (as in 18.065): 50% regular assignments on the anchor dataset, 50% final research project.
   Milestone presentations are planned for weeks 4, 8 and 12.

**Deliberately left out:** LU decomposition by hand, Cramer's rule, the 3×3 determinant formula, manual Gram–Schmidt,
the four fundamental subspaces as a separate topic. The geometric meaning of the determinant is kept; the hand
technique is not.

**How we use the syllabus.** The syllabus is a compass, not a contract: it fixes the philosophy, the phases and a bank of
interpretation questions. The actual order follows what the students need next and what the data allow. Every
deviation is recorded in §5. If this map and the syllabus disagree about *what exists*, this map is right. If they
disagree about *intent*, ask the course author.

---

## 2. Phases and status

| Phase | Weeks | Theme (syllabus) | Status (2026-11-17) |
|---|---|---|---|
| **1. Data as vectors** | 1–4 | Descriptive statistics, distributions; vector, norm, dot product; rank; covariance | L1–L13 built; the group has progressed through covariance/correlation to the completed calculus and MSE seminars. General basis theory remains pending. |
| **2. Matrices as operators** | 5–8 | Operators, determinant and inverse, eigenvectors, PCA (+ SVD overview) | Matrix operations and transformations in L10; rank and singularity in L11; linear systems, inverse and 2D determinant geometry in L12. Eigenvectors and later groundwork remain pending. `unsupervised/01` already covers SVD/PCA as an ML lesson. |
| **3. Estimation and first models** | 9–12 | Projections and least squares, linear regression, MLE, logistic regression | Calculus/MSE and ML2–ML4 are completed; matrix OLS, preprocessing and Ridge are taught. ML5 adds model diagnostics for review. ML1's classroom status remains unconfirmed. MLE and logistic regression remain pending; estimation and permutation tests were brought forward into L7–L9. |
| **4. Classic DS and the project** | 13–16 | Trees, ensembles, metrics, cross-validation; research project | Modules `DT/` and `unsupervised/` exist (built June 2026, before the math block). Project not designed. |

---

## 3. Teaching sequence

Kinds: **L** = lesson (Colab), **S** = seminar, **H** = homework, **P** = practicum.
Paths are relative to the repo root. **Dated** is the date of the materials. It was reconstructed from file timestamps
and from references inside the notebooks, and is not necessarily the date of the class.

| # | Kind | Material | Main topics | Relies on | Syllabus | Dated |
|---|---|---|---|---|---|---|
| 1 | L | **L1 — Vectors** · `math_for_ds/01_vectors.ipynb` | observation = vector, feature space, norm, distance, addition and scaling, linear combination, centroid | — | W1 (LA) | Aug 25 |
| 2 | L | **L2 — Dot product** · `math_for_ds/02_dot_product.ipynb` | dot product, projection, L2 normalization, cosine vs. Euclidean, embeddings, attention | L1 | W1 (LA) | Aug 26 |
| 3 | S | **Seminar 1 — speaker embeddings** · `math_for_ds/seminar_1.ipynb` | cosine and Euclidean matrices on WavLM embeddings, verification threshold, nearest-centroid classifier, anomaly search | L1–L2 | W1 (ML link) | Aug 27 |
| 4 | H | **Vector-algebra problem set** · `math_for_ds/vektornaya-algebra-hw.md` / `.pdf` | 97 textbook problems: coordinates, lengths, dot product, angles, collinearity | L1–L2 | W1 | Aug 31 |
| 5 | L | **L3 — Population and sample (S1–S4)** · `math_for_ds/03_stat_intro.ipynb` | population/sample/bias, histogram, KDE, mean/variance/SD, z-standardization | L1–L2 | W1 (stats) | Sep 3 |
| 6 | P | **house.kg seminar project** · external repo `ai-academy-bish/ds8_house_kg_proj` | guided walkthrough on Bishkek apartments for sale: cleaning, shape, an outlier hunt, price per m², z, kNN on raw vs. standardized features; then a research topic of choice | L1–L3 | W1 assignment | Sep 4–8 |
| 7 | L | **L4 — Non-parametric measures** · `math_for_ds/04_stat_boxplot.ipynb` | outliers vs. mean and σ, percentiles, quartiles, boxplot, 1.5·IQR, cleaning, RobustScaler | L3 | beyond plan | Sep 9 |
| 8 | P | **Lalafo practicums: phones, cars** · `practice/phones/`, `practice/cars/` | 5 cases each on dirty marketplace data, using only L1–L4 tools | L1–L4 | Phase 1 practice | Sep 10 |
| 9 | L | **L5 — Randomness, probability, the normal distribution** · `math_for_ds/05_stat_normal.ipynb` | event, probability, Bernoulli, binomial, normal, 2D normal, three-sigma rule | L3–L4 | W2 | Sep 16 |
| 10 | L | **L6 — From histogram to probability** · `math_for_ds/06_stat_distribution.ipynb` | random variable, PMF, density histogram, PDF, area, CDF, z, tails, model vs. sample | L5 | W2, extended | Sep 22 |
| 11 | P | **Bus practicum "Моссовет → Азия Молл"** · [student tasks](../practice/practicum_mossovet_asia_mall.ipynb), [teacher KEY](../practice/practicum_mossovet_asia_mall_KEY.ipynb) | real GPS feed; trips via vectors and dot product; ECDF, normal model vs. data, waiting-time paradox, Monte Carlo | L1–L6 | integrative | Sep 28 |
| 12 | L | **L7 — Sampling, standard error, CLT** · `math_for_ds/07_stat_sampling_clt.ipynb` | sampling distribution, SE, LLN, CLT, difference of two means; reuses the bus data | L6, bus practicum | beyond plan (prepares W12) | Sep 30 |
| 13 | L | **L8 — Confidence intervals and bootstrap** · `math_for_ds/08_stat_ci_bootstrap.ipynb` | known-σ intervals, coverage, bootstrap SE and percentile intervals, resampling schemes | L7 | estimation brought forward | Oct 1 |
| 14 | P | **Bus comparison: permutations and bootstrap** · [student tasks](../practice/practicum_mossovet_asia_mall_bootstrap.ipynb), [teacher KEY](../practice/practicum_mossovet_asia_mall_bootstrap_KEY.ipynb) | paired daily route means, sign-flip simulation, one-sample bootstrap of daily differences, approximate normal and percentile CIs | L7–L8, bus practicum | estimation in practice | Oct 2 |
| 15 | L | **L9 — Hypotheses, p-values and statistical significance** · [09_stat_hypotheses.ipynb](../math_for_ds/09_stat_hypotheses.ipynb) | two delivery methods; permutation p-value, null/alternative, α and false rejections, bootstrap CI for a difference, practical threshold | L7–L8, bus resampling practicum | W12 brought forward; final statistics meeting | Oct 8 |
| 16 | L | **L10 — Matrices and matrix multiplication** · [10_matrices.ipynb](../math_for_ds/10_matrices.ipynb) | dimensions and operations; dot product and linear combination revisited; Ax as a transformation; matrix multiplication, composition and NumPy; Xw; rotation, given weights and threshold-network tasks | L1–L2, basic NumPy | develops W2 linear combinations; groundwork for W3 and introductory W5 operators | Oct 9 |
| 17 | L | **L11 — Linear dependence and rank** · [11_linear_dependence_rank.ipynb](../math_for_ds/11_linear_dependence_rank.ipynb) | dependence/independence, redundant columns, rank, square-matrix singularity, nonunique given weights | L1–L2, L10 | W3 dependence/rank; geometric part of W5–W6 | Oct 14 |
| 18 | L | **L12 — Linear systems and inverse matrices** · [12_linear_systems_inverse.ipynb](../math_for_ds/12_linear_systems_inverse.ipynb) | Ax = b, one/no/infinitely many solutions, inverse, determinant and area, NumPy solve, matrix equations and a supplied least-squares weight formula | L10–L11, basic NumPy | W5–W6; first formula application from W9–W10 | Oct 15 |
| 19 | L | **L13 — Covariance and correlation** · [13_covariance_correlation.ipynb](../math_for_ds/13_covariance_correlation.ipynb) | sample covariance, Pearson as a centered-vector cosine, covariance/correlation matrices, Spearman, exact/near multicollinearity, feature transformations | L2–L3, L10–L12, NumPy/pandas | W3 multicollinearity and W4 covariance/correlation; prepares W9–W10 | Oct 16 |
| 20 | S | **Calculus seminar** · [matan_seminar.ipynb](../math_for_ds/matan_seminar.ipynb) | limits, derivatives and tangents, finite differences, partial derivatives, gradients, one- and two-dimensional gradient descent | functions, vectors, NumPy and plots | added optimization groundwork for W9–W10 | completion confirmed Oct 30 |
| 21 | S | **MSE optimization seminar** · [mse_optimization.ipynb](../math_for_ds/mse_optimization.ipynb) | one-feature linear regression, MSE, analytic gradients, scaling, hand-coded and vectorized gradient descent, prediction and introductory error metrics | calculus seminar, L10–L13 | W9–W10 first model fitting | completion confirmed Oct 30 |
| 22 | L | **ML1 — Introduction to machine learning** · [01_intro_ml.ipynb](../LinModels/01_intro_ml.ipynb) | model and generalization; feature/target notation; labelled data; train/validation/test; loss/metrics; parameters/hyperparameters; complexity; ML map; modern systems; bilingual glossary | completed calculus and MSE seminars; L1–L2 vectors/embeddings | W9–W10 workflow and terminology; quality assessment brought forward | Nov 2, awaiting review/classroom use |
| 23 | S | **ML2 — First applied linear regression** · [02_linear_regression.ipynb](../LinModels/02_linear_regression.ipynb) | Ames; baseline and one-/three-feature OLS; matrix derivation via gradient = 0; coefficients; MAE/RMSE/MAPE; unused test | calculus/MSE seminars, L13, ML1 terminology | W9–W10 applied fitting and analytical solution | built Nov 3; completed Nov 4; OLS/MAPE text added Nov 5 |
| 24 | S | **ML3 — Data preprocessing** · [03_data_preprocessing.ipynb](../LinModels/03_data_preprocessing.ipynb) | missing values, train-only median imputation, scaling, fit/transform, Pipeline, OneHot/ColumnTransformer, unknown categories, OLS comparison | completed ML2; scaling, medians and rank from math block | W9–W10 applied workflow | built Nov 5; completion confirmed Nov 9, exact class date unrecorded |
| 25 | S | **ML4 — Regularization** · [04_regularization.ipynb](../LinModels/04_regularization.ipynb) | coefficient instability, exact/near multicollinearity, Gram matrix, loss geometry, Ridge, alpha and feature scale, brief Lasso geometry, validation selection on Ames | completed ML2–ML3, L10–L13, calculus/MSE | W9–W10 linear-model extension | built Nov 9; completion confirmed Nov 17, exact class date unrecorded |
| 26 | S | **ML5 — Model diagnostics** · [05_model_diagnostics.ipynb](../LinModels/05_model_diagnostics.ipynb) | R², residuals/groups, difficult predictions and similar houses, coefficients and prediction contributions, bootstrap stability, permutation feature importance, optional OLS inference | completed ML2–ML4; bootstrap from L8; scaled distances from math block | W9–W10 model interpretation; quality assessment brought forward | Nov 17, awaiting review/classroom use |
| — | — | **Phase 4 modules** · `DT/`, `unsupervised/` | trees and ensembles; dimensionality reduction and clustering (§7) | Phases 1–3 | W13+ | June 2026 |

Evidence for the less obvious positions:

- **Seminar 1 after L2:** it is built entirely on cosine similarity and Gram matrices (L2 material). It is dated between
  the L2 build and the final L1/L2 notebooks.
- **house.kg seminar project between L3 and L4:** its `PHASES.md` lists the tools students "already have" (L1–L3)
  and says percentiles, correlation and logarithms are "not yet introduced". Its outlier hunt (one data-entry error
  moves the mean and inflates σ ~100×) is exactly where L4 begins. Commits: Sep 4–8.
- **Lalafo practicums after L4:** their `RECON.md` files list exactly L1–L4 topics as the target ("векторы, скалярное
  произведение/косинус, описательная статистика, боксплоты"), and "корреляции нет нигде — её ещё не проходили".
- **Bus practicum between L6 and L7:** the notebook has a table "На что опирается работа" mapping its tools to
  lessons 1–6. L7 §8 quotes the "saved output of task 1.2 of the previous practicum".
- **Calculus → MSE → ML1:** the author confirmed that both hand-maintained seminars were completed after the
  L13 discussion, then requested `LinModels` as the ML module. The confirmation date is not a claimed class date.

Not in the sequence: `math_for_ds/theory/` (Aug 24) is an early HTML-handbook prototype of L1, replaced by the
Colab format the next day (see §10).

---

## 4. Lesson and practicum notes

Each note lists the files, the data, the structure, the tasks, and methodological remarks. **Bridges** are places
where a material deliberately prepares a later topic. They are worth keeping when lessons are revised.

### L1 — «Вектор: наблюдение как точка в пространстве признаков»

- **Files.** `math_for_ds/01_vectors.ipynb` is the **canonical file, edited by hand**. `build_lesson1.py` generated the
  first version and is now historical (see §10).
- **Data.** Davis: height and weight of 200 people, measured and self-reported (`repwt`, `repht`).
- **Theory** (collapsed HTML cells, draggable vectors): 1) observation, feature, vector; 2) how vectors differ;
  3) length and direction, from Pythagoras to ℝⁿ; 4) addition; 5) scaling and linear combination.
- **Tasks.** Norm by hand and with `np.linalg.norm`; operations by hand. Davis tasks 6.1–6.6: the norm of each row,
  the distance between two observations, the nearest neighbour, centroids (overall and by sex), outliers by distance
  to the own-sex centroid, reported vs. measured values.
- **Homework.** On the anchor dataset: the matrix `X`, row norms, the two most similar and the two most dissimilar rows,
  explained in words.
- **Notes.** After generation, the author removed the TODO hints from the task cells, so students see bare `...`.
  The SETUP cell is local to this lesson (it predates `theme.py`).
- **Bridges.** Linear combination and span → rank and multicollinearity (W3).

### L2 — «Скалярное произведение, косинусная близость и нормализация»

- **Files.** `math_for_ds/02_dot_product.ipynb` ← `build_lesson2.py`.
- **Data.** Davis.
- **Theory.** 1) dot product and projection; 2) length through the dot product, L2 normalization, and the two different
  meanings of the word «нормализация»; 3) cosine similarity and distance vs. Euclidean distance; 4) where this is used
  in ML: embeddings and search, attention in language models.
- **Practice** (in English): the dot product two ways, cosine similarity, magnitude vs. direction, nearest neighbour by
  Euclidean vs. cosine distance on the centred cloud.
- **Homework** (in English): `cosine_distance`; the identity ‖â − b̂‖² = 2(1 − cos φ); two people with the same shape
  and different size; why embeddings are compared by cosine.
- **Notes.** The committed notebook was built with an older `theme.py`. A rebuild only adds CSS classes and is safe.

### Seminar 1 — «Скалярное произведение в задачах анализа речи»

- **Files.** `math_for_ds/seminar_1.ipynb`, written by hand (no build script).
- **Data.** `aiacademy-kg/audio-3-speaker-dataset-v2`: clips from 3 speakers (andrew, kore, puck), each with a
  128-dimensional WavLM embedding. The notebook pins `datasets==3.6.0`.
- **Flow.** Why angles between vectors matter → waveforms and listening → a t-SNE map (shown only as a preview) →
  a Gram matrix of cosine similarities → a matrix of Euclidean distances → Task 1: an empirical verification
  threshold; Task 2: a 3-class nearest-centroid classifier; Task 3: find the anomalous clip and listen to it.
- **Bridges.** The same speakers are used again in `unsupervised/` (PCA, k-means, GMM, DBSCAN).

### H — Vector-algebra problem set

- **Files.** `math_for_ds/vektornaya-algebra-hw.md` (Markdown + LaTeX) and the `.pdf` rendering.
- **Content.** «Глава 14. Элементы векторной алгебры, §73», 97 problems, the harder ones starred. Coordinates, linear
  operations, collinearity, lengths and distances, the dot product, angles, perpendicularity.
- **Notes.** Pen-and-paper drill that complements the data-driven L1–L2. The source textbook is not credited (§10).

### L3 — «Генеральная совокупность и выборка» (statistics sessions S1–S4)

- **Files.** `math_for_ds/03_stat_intro.ipynb` ← `build_lesson3.py`.
- **Data.** Davis.
- **Theory.** S1) population, sample, representativeness, bias; S2) histogram, KDE, mode; S3) mean, variance, SD
  (why squares; SSE). Then a tools section in numpy/pandas: `describe`, `groupby`, histograms and KDE, 2D KDE with
  centroids. S4) normalization and z-standardization (σ as the "price" of one unit).
- **Tasks.** Five on descriptive statistics, by group. Eight on z: by hand, units disappearing, 1/σ as an "exchange
  rate", distances before and after z, centroids, L2 vs. z normalization, SD globally vs. within groups, the scatter
  before and after z.
- **Notes.** The statistics track starts **from data, with no formal probability**: probability is intuitive here
  and is formalised in L5–L6. **S4 Task 8 asks for a correlation coefficient before it is introduced in the
  teaching order**; the dedicated correlation lesson is now L13 (§10).
- **Bridges.** z as the diagonal operator D⁻¹ (→ Phase 2). The cosine of centred vectors equals r, given as a
  "spoiler" (→ W4 covariance). Whitening via eigenvectors (→ PCA).

### Seminar project — house.kg (external repository)

- **Repo.** [`ai-academy-bish/ds8_house_kg_proj`](https://github.com/ai-academy-bish/ds8_house_kg_proj):
  `seminar_1.ipynb` (the worked reference) and `PHASES.md` (the programme). Each student pushes findings to their own
  branch.
- **Data.** `aiacademy-kg/house_kg_full_dataset`, table `listings`, one slice: Bishkek · sale · apartments.
- **Phase 1** (guided, done together): load (a row is an *ad*, not an apartment) → build the slice → clean (missing
  `rooms_n` is not random) → look at the shape first (histograms + KDE; `log10` only as a spoiler) → centre, spread
  and an outlier hunt (a single data-entry error; the median only as a "careful spoiler") → two normalizations
  (price per m²; z, checked with `StandardScaler`) → an object as a point: kNN on raw vs. standardized features.
- **Phase 2.** A menu of research topics T1…Tn: each student picks one and takes it deep.
- **Notes.** `PHASES.md` states the rules: compute by hand, then verify with a library; one sentence of
  interpretation for every number; anything not yet taught may appear only as a flagged spoiler.

### L4 — «Непараметрические меры»

- **Files.** `math_for_ds/04_stat_boxplot.ipynb` ← `build_lesson4.py`.
- **Data.** house.kg apartments in Bishkek (`aiacademy-kg/house_kg_full_dataset`, filtered to sale + apartment +
  Бишкек) and Davis heights.
- **Parts.** 1) one outlier breaks the mean and, even more, σ (a histogram toggle and a drag-the-outlier demo; the
  variance grows as a parabola; a note that MSE inherits the same fragility); 2) percentiles (strict definition, numpy
  methods), quartiles, the boxplot step by step, comparing groups, a seaborn guide; 3) cleaning outliers by percent
  trimming vs. by whiskers; 4) IQR as a robust σ, RobustScaler.
- **Tasks.** Six on house.kg: price per m² by rooms, by condition, by building series; the sale-vs-rent scale trap;
  cleaning two ways; StandardScaler vs. RobustScaler neighbours.
- **Notes.** **Not in the syllabus.** It was added because real, dirty data needs robust tools before the normal
  distribution. The committed notebook contains **17 extra cells (cells 20–36) of live coding from class** that are
  not in the build script.

### Practicums — Lalafo phones and cars

- **Folders.** `practice/phones/`, `practice/cars/`. Each has `recon.py` and `RECON.md` (a teacher-facing study of the
  dataset), and `build_<topic>.py` → `<topic>_practice.ipynb`. Local parquet copies are in `data/` (gitignored).
- **Data.** `aiacademy-kg/lalafo-kg-phones` (8,160 listings) and `aiacademy-kg/lalafo-kg-cars` (54,518 listings).
  Only the `listings` and `users` configs are loaded, never `images` (~5 GB and 78 GB).
- **Format.** Markdown and code only, no HTML. Loading and rough feature engineering are done in advance. **Outliers
  and garbage are left in on purpose.** Then a data dictionary with known traps, a warm-up, five cases T1–T5, and a
  guide for the oral defence.
- **Case design.** Each case sets the layperson's reading («обыватель») against the researcher's («исследователь»),
  and recommends mathematics "tied to necessity". Across the five cases: robust statistics and boxplots;
  groupby/KDE/centroids/z; vectors and norms; cosine vs. Euclidean kNN; data cleaning.

  | | Phones | Cars |
  |---|---|---|
  | T1 | Phones for a call centre (median vs. mean, boxplot, IQR) | "Newer = cheaper?!" (the currency trap) |
  | T2 | Gigabytes or the logo? (group medians, confounding) | Does mileage matter? (masked by brand and year) |
  | T3 | 1,000 views and zero calls (ratio feature, 2D cloud) | Find an alternative to this car (choice of metric) |
  | T4 | "Like my friend's, but cheaper" (vectors, z, cosine kNN) | 1,000 views and no calls |
  | T5 | Hunting resellers (percentiles; IQR degenerates) | Dealers and junk listings |

- **Notes.** Correlation is deliberately absent everywhere. Recurring traps: a feature present only in a subgroup
  (battery data exist only for iPhones / EVs); IQR degenerating on counts (Q1 = Q3 = 1, so a high percentile is used
  instead); mixed currencies (≈40% of car prices are in USD, converted at USD × ≈89).

### L5 — «Случайность, вероятность и нормальное распределение»

- **Files.** `math_for_ds/05_stat_normal.ipynb` ← `build_lesson5.py`. Photos from `math_for_ds/images/` are embedded
  as base64.
- **Data.** Davis heights of men (nearly normal) and house.kg prices (skewed).
- **Parts.** Introduction: random processes around us (worn paint and ruts in asphalt as natural histograms).
  0) the language of chance: trial, outcome, event, probability; 1) Bernoulli; 2) binomial: a sum of coins produces a
  bell; 3) normal; 3b) 2D normal (scatter, KDE, σ-ellipses); 4) the three-sigma rule as an outlier detector.
- **Tasks.** Five on house.kg: which feature looks normal and which does not; checking 68–95–99.7; 3σ on price
  (this is the syllabus question "3σ flagged 8% — outliers or a non-normal feature?"); 3σ vs. IQR; Bernoulli and
  binomial (np, np(1−p)).
- **Notes.** A "genetic" order: language → one coin → a sum of coins → the normal curve.
- **Bridges.** Counts in time and space → Poisson (W3). "95% within μ ± 2σ" is about single observations, not a
  confidence interval → estimation.

### L6 — «От гистограммы к вероятности»

- **Files.** `math_for_ds/06_stat_distribution.ipynb` ← `build_lesson6.py` + `lesson6_widgets.js` (embedded at build
  time).
- **Data.** Synthetic only: a teaching normal model of height (μ = 170, σ = 10). Because the law is known, every
  calculation can be checked by an experiment. An optional cell at the end accepts the student's own real feature.
- **Sections.** 1) from observations to a probabilistic model (proportion vs. probability, a random variable and its
  law, discrete values); 2) count, proportion and density histograms; 3) density and area (PDF, the integral as a sum
  of rectangles); 4) CDF, with the PDF as its derivative; 5) the normal model and the standard scale (z preserves
  the probability of an event); 6) which area to shade: one tail, two tails, the middle; where 68–95–99.7 comes from;
  7) from probability to counts ("how many of 1,000 people are ≥ 190 cm?"; repeated samples; a model with the wrong
  shape); 8) practice with explanations.
- **Tasks.** Tasks 1–3 inside the sections, a practice block (`cdf`/`sf` events, simulation), an oral comprehension
  check.
- **Notes.** **Designed for two meetings** (sections 1–4 and 5–8). This lesson introduced the current build pattern:
  an `eq()` helper that refuses a formula without a symbol glossary, widgets kept in a separate JS file, deterministic
  cell ids, and references to NIST and the SciPy docs.

### Bus practicum — «Какой автобус выбрать? Моссовет → Азия Молл»

- **Files.** Both notebooks live in `practice/` and are maintained by hand, without a build script:
  [practicum_mossovet_asia_mall.ipynb](../practice/practicum_mossovet_asia_mall.ipynb) contains **student tasks**
  without teacher notes or saved outputs;
  [practicum_mossovet_asia_mall_KEY.ipynb](../practice/practicum_mossovet_asia_mall_KEY.ipynb) contains
  **teacher answers**, saved outputs and «Для преподавателя» notes.
- **Data.** `aiacademy-kg/bishkek-transport`, the open feed of Bishkek's public-transport monitoring system for
  25.07–22.09.2026 (372 M rows), pinned to revision `4aa20aab…` (23.09.2026). The notebook downloads a prepared 21 MB
  extract (`practicum/mossovet_asia_mall_2026.zip`). If the extract is missing, it rebuilds it from the raw feed
  (~3.7 GB).
- **Question.** Which route, No. 118 or No. 169, gives better odds of getting from «Моссовет» to «Азия Молл»
  within 15 or 20 minutes?
- **Part 0** (pre-built, explained step by step): raw feed → duplicates → metres → bus step vectors → stop passages
  via projection and the dot product → A→B trips → calendar and data completeness → a first look.
- **Part 1, both buses at the stop.** 1.1 unit of observation; 1.2 centre and spread by time window; 1.3 the chance
  to arrive in time (ECDF F(t)); 1.4 a recommendation table; 1.5 the trap of one pooled number; 1.6 where the normal
  model fails; 1.7 summer vs. September; 1.8* paired comparison; 1.9* twenty trips a month (binomial). Then a memo.
- **Part 2, a person arriving at the stop.** 2.1 headways; 2.2 the waiting-time paradox; 2.3 total time under three
  strategies (Monte Carlo); 2.4 what matters more, speed or frequency; 2.5* the best choice in hindsight; 2.6
  assumptions and limits. Then a memo.
- **New tools introduced here:** the empirical CDF, Monte Carlo simulation of random arrivals, the
  inspection (waiting-time) paradox.
- **Notes.** This practicum pulls L1–L6 together. L7 §8 reuses the output of its task 1.2.

### L7 — «Почему у нас получились разные средние?» (sampling, SE, CLT)

- **Files.** `math_for_ds/07_stat_sampling_clt.ipynb` ← `build_lesson7.py` + `lesson7_widgets.js`.
- **Data.** A synthetic delivery-time generator, plus rounded bus summaries from the practicum embedded in the
  notebook.
- **Sections.** 1) we see only part of the deliveries; 2) the sample mean vs. the true mean; 3) collecting means
  instead of times (the sampling distribution); 4) the standard error: the definition after the experiment, σ/√n,
  and s/√n when σ is unknown; 5) the law of large numbers; 6) the CLT; 7) drug vs. control: a non-zero difference
  without any effect; 8) back to the buses: a small SE does not mean identical trips; 9) self-check and short
  formulations for oral answers. Extras: a proportion as a mean, dependence and precision, two properties of an
  estimator.
- **Notes.** **Designed for two meetings** (1–4; then 5–8 and practice). Sources: Penn State STAT 200/414/555 and
  OpenStax.
- **Bridges.** §7 ends with "is the difference large compared with ordinary random spread?" and announces
  **statistical tests and significance** for the next lesson. The author subsequently inserted L8 on
  confidence intervals and bootstrap; formal tests are covered in L9. The original L7 bridge is unchanged.


### L8 — «Насколько точно мы знаем среднее?» (confidence intervals and bootstrap)

- **Files.** `math_for_ds/08_stat_ci_bootstrap.ipynb` ← `build_lesson8.py` + `lesson8_widgets.js`.
- **Data.** The synthetic delivery generator from L7 (10 + exponential waiting time; mean 30, SD 20).
  Truth is available for method validation, then hidden when estimating from one sample. No data downloads.
- **Sections.** 1) point estimate and precision; 2) central area for sampling means; 3) inversion into a CI;
  4) repeated-study coverage; 5) delivery interpretation task; 6) a full bootstrap chapter (replacement,
  empirical distribution, SE, percentile interval, nested coverage simulation, SciPy); 7) parametric vs.
  nonparametric bootstrap, paired/cluster/block schemes, optional strata, and percentile/basic/BCa intervals;
  8) practice and oral definitions; 9) a short hypothesis-testing bridge.
- **Visuals.** Nine self-contained SVG widgets: sampling, shaded sampling distribution, interval inversion,
  coverage forest, indexed resampling cards, bootstrap estimate/interval, bootstrap coverage, optional fitted
  model comparison, optional row vs. cluster bootstrap. Eight matplotlib/seaborn figures in worked code.
- **Notes.** Two meetings (1–5; 6 plus the overview in 7 and practice); optional experiments can move to a seminar.
  Every displayed theory equation has a glossary. Important conclusions are boxed. Worked code is explicitly
  separated from unanswered student tasks. Normal intervals use known population SD; for skewed deliveries
  coverage is approximate. Bootstrap percentile coverage is checked, not promised. No t-tests or p-values.
- **Limits.** Bus data appear only as a reasoning task about dependence; cluster resampling is illustrated on
  synthetic equal-size independent days. A glossary of bootstrap variants is introductory, not a claim that
  students can independently apply every advanced method.
- **Bridges.** Which parameter values agree with our interval? A hypothesis is defined, but p-values, test rules
  and statistical significance are left for L9.

---

### Bus resampling practicum — «Какой маршрут быстрее: №118 или №169?»

- **Files.** [practicum_mossovet_asia_mall_bootstrap.ipynb](../practice/practicum_mossovet_asia_mall_bootstrap.ipynb)
  contains student tasks; [practicum_mossovet_asia_mall_bootstrap_KEY.ipynb](../practice/practicum_mossovet_asia_mall_bootstrap_KEY.ipynb)
  contains teacher answers and saved outputs. Both are maintained by hand; the author approved the shortened KEY.
- **Preparation.** Dependencies and all of Part 0 (source cells 4–39) are copied unchanged from the original bus
  KEY. Both versions preserve cell sources and metadata; only the KEY retains saved outputs. The student copy
  clears outputs and execution counts throughout. The same loader uses a local zip, a prepared HF extract, or a raw-HF
  rebuild. The author explicitly authorized the fallback download for validation of this practicum.
- **Question and unit.** Compare travel time of routes 118 and 169, first by time window, then within one morning
  window (07–10). One analysis observation is the difference between two route means from the same date/window.
  Every date has equal weight; this is not the trip-weighted mean or a prediction for an individual trip.
- **Flow.** Three-window overview → one morning comparison per date → mean difference → one label-swap example
  and a short permutation loop → one bootstrap sample and a short bootstrap loop → two approximate confidence
  intervals → a 3–4 sentence answer for a passenger. The main analysis uses 07–10 only; no separate season study
  or additional three-window resampling task.
- **Teaching.** One meeting after the shared preparation. Four short cells tagged `student-core` contain tasks
  A–D in the student version and solutions in the KEY; grouping and plotting are provided in both.
  Students fill eight expressions: one mean, two steps in each resampling loop, and three interval calculations.
  Plain Markdown and Python only, without custom HTML/JS or widgets.
  Four standard figures show the overview, daily differences, permutation means, and bootstrap means/intervals.
  Brief method reminders precede the code; every displayed equation has a glossary. Teacher notes contain actual
  numerical conclusions; the student version has questions and places to write answers instead.
  KEY prose outside preparation was reduced from about 3,240 to 1,340 whitespace-delimited words.
- **Conditions.** Sign flips model symmetric daily differences about zero, not arbitrary equal-mean distributions.
  Bootstrap assumes sufficiently independent, comparable days; the text states this briefly.
  Intervals are approximate; neither normal nor percentile intervals promise exact coverage.
  The permutation output is the empirical fraction of simulated means at least as far from zero, not a posterior
  probability that a difference is random. No formal hypothesis decision rule, t-test or p-value lesson is introduced.
- **Sources.** L8; Hesterberg §2; SciPy paired permutations and bootstrap.
- **Checked results.** Full HF data reproduce the original trip counts and 37 paired mornings. With the fixed
  seeds: mean daily difference ≈ −0.578 min; normal CI [−1.160, +0.003], percentile CI [−1.143, −0.008];
  605/9999 sign-flip means are at least as far from zero. A teacher note explains the near-zero boundaries and
  why approximate methods need not agree on which side of zero their last decimal falls.
- **Validation.** The shortened notebook was executed locally against the full prepared HF extract. The earlier
  statistical checks against SciPy remain applicable to the retained permutation/bootstrap loops. All four new PNG
  figures were inspected; source/metadata/output identity of the copied preparation was verified. No custom browser runtime remains;
  execution in Colab itself has not been checked.
- **Student validation.** Cell sources and metadata in the shared preparation match the KEY, and all provided
  code is unchanged. A temporary copy with the four KEY solutions substituted was executed on the full local
  extract; the distributed assignment remains unexecuted, with no teacher notes or saved answers.
- **Next.** Use the student assignment after L8, before introducing formal statistical tests in L9.

### L9 — «Новая доставка действительно быстрее?» (hypotheses and significance)

- **Files.** [09_stat_hypotheses.ipynb](../math_for_ds/09_stat_hypotheses.ipynb) ← `build_lesson9.py` +
  `lesson9_widgets.js` + `lesson9_helpers.py`. Both sources are embedded; only the notebook is needed in Colab.
- **Scope.** One final statistics meeting: 110 minutes of work plus a 10-minute break. The author has two months
  left for the course and explicitly requested closure of this block. No t-test, Student distribution, extra
  bootstrap variants or separate advanced-statistics session. Short explanations progress from the delivery
  question to the definitions and their interpretation.
- **Data and question.** Independent synthetic deliveries: 10 plus exponential delay with mean 20 for A;
  B differs only by a constant time shift. Default: 200 per group, true improvement 6 minutes. Estimate B − A.
  The business threshold (5 minutes) and α = 0.05 are chosen before inspecting results.
- **Flow.** Observe the difference → formulate null and two-sided alternative → permute labels → define and
  calculate p-value → observe false rejections under a true null → separately bootstrap each group → interpret
  a 95% percentile CI against zero and −5 → write a four-sentence recommendation.
- **Definitions.** Named definition boxes explain statistical hypotheses, test statistic, p-value, significance level,
  type-I error, statistical significance and the confidence interval. The p-value definition conditions on H0
  and model assumptions and specifies extremeness through the alternative. Failing to reject does not prove H0.
- **Format.** The same dark HTML theory cells and self-contained JS/SVG visuals as L6–L8. Three widgets show
  accumulating label permutations with both tails, repeated null experiments, and sample-size/effect comparison.
  Standard Python examples and matplotlib/seaborn figures connect these demonstrations to code. Only three
  short coding tasks: observed difference, p-value, bootstrap bounds.
- **Statistical conditions.** In the teaching shift model equal means imply identical distributions, justifying
  pooled label permutations; this is not asserted for arbitrary equal-mean distributions. Equal group sizes give
  a symmetric exhaustive permutation distribution; use absolute tails and the (k+1)/(R+1) Monte Carlo correction.
  Bootstrap preserves the independent groups. The CI is approximate and is not an exact inversion of this test.
- **Verified Python example.** Estimated difference −7.538 min, p ≈ 0.0004, percentile CI [−11.753, −3.372] min.
  The result is significant at 0.05, but the full interval does not support improvement beyond five minutes.
  The initial null simulation produces 3 false rejections in 100 trials, not a forced 5%. Controls include
  both a small detectable effect (800/group, gain 2) and a CI fully below −5 (800/group, gain 8).
  JS uses the same delivery values with independent resampling draws: its default p ≈ 0.0007 and CI
  [−11.657, −3.319] min give the same conclusions; the widget footnote explains the numerical difference.
- **Validation.** Ready cells and a completed copy executed locally; Python results match the previous numerical
  example. Exact permutation tails and independent bootstrap SE were checked. Node checks cover JS probability
  calculations, reproducibility and every control handler using a simulated DOM. HTML outputs were exported;
  actual browser rendering could not be inspected because browser/computer access was unavailable in this session.
  Neither browser appearance nor the Colab UI is claimed as verified. Build is deterministic; the distributed
  notebook remains unexecuted and the author's edited bus notebook is unchanged.
- **Sources.** ASA p-value statement, Hesterberg, SciPy permutation/bootstrap documentation; links back to L8
  and the student bus practicum. Existing course notebooks were not rebuilt.

### L10 — «Как матрица преобразует данные?» (matrices and multiplication)

- **Files.** [10_matrices.ipynb](../math_for_ds/10_matrices.ipynb) ← `build_lesson10.py` +
  `lesson10_widgets.js` + `images/lesson10_threshold_network.png`. The widget code, small data extract and
  diagram attachment are embedded; only the notebook is needed in Colab.
- **Scope.** One beginner two-hour theory meeting after the final statistics lesson, followed by short practice
  for class or homework. The full assignment is not promised to fit the same meeting. Returns to the observations,
  vectors and dot product of L1–L2. The aim is to understand matrix multiplication and what it computes;
  no general basis/rank theory, determinants, inverses, eigenvectors or model fitting. The standard basis of
  the plane is defined briefly to explain why the transformed unit vectors are the matrix columns.
- **Data.** First six Davis observations, with measured weight and height, embedded from
  `aiacademy-kg/davis_dataset` at revision `cfb0d88e0d0a8814998ecfb36179bd18d0cbbb5a`,
  file `data/train-00000-of-00001.parquet`. Integer matrices and synthetic two-dimensional points are used for
  arithmetic and geometry. The final example uses synthetic courier orders with distance and stop count;
  its weights (3 min/km and 2 min/stop) are given, not fitted. Practice uses synthetic car features and given
  price weights; the network diagram is supplied by the instructor and preserved byte-for-byte. No runtime downloads.
- **Flow.** A data table and its observation vectors → matrix dimensions, indexing, rows and columns →
  addition, subtraction, scalar multiplication and transpose → dot product and linear combination revisited →
  Ax as row dot products and a combination of columns → action on a plane → matrix multiplication and
  compatible dimensions → properties and composition → Xw for all observations, then X @ A.T for row-stored
  points → four student tasks.
- **Definitions and NumPy.** Repeat precise definitions of the real-vector dot product and linear combination
  before using them. Explicitly distinguish elementwise `*` from matrix `@`/`np.matmul`;
  `np.dot` is a scalar product for two one-dimensional vectors and a matrix product for two matrices.
  Examples expose shapes and zero-based indexing, and explain that a one-dimensional array's `.T` does not
  make it a column. Column-vector formulas and row-oriented data use the same operation with consistent shapes.
- **Visuals.** Five self-contained JS/SVG widgets: select a Davis row and its point; inspect basic operations;
  transform a grid and vectors; inspect a selected entry of a matrix product; compare orders of composition.
  In the operations widget, k is explicitly identified as the scalar multiplier; its control appears only
  when scalar multiplication is selected.
  Geometric planes use equal scales. The standard basis vectors e1 = (1, 0) and e2 = (0, 1) show the matrix
  columns after transformation; composition acts rightmost first. NumPy examples calculate the same operations,
  with standard Python figures where useful.
- **Properties.** Identity, associativity, distributivity and noncommutativity, with dimensions respected.
  The course's existing linear-combination idea now explains each column of a product and the ML weighted-sum link.
- **Practice (§9).** Four short student tasks with unanswered TODOs and interpretation questions:
  a 90-degree rotation of a vector and row-stored triangle points; car prices from given weights; two weight
  sets stored as columns of W for all cars at once; a three-input/two-hidden-unit/one-output threshold network.
  Car features are a constant 1, engine volume in litres, age in years and mileage in thousands of kilometres;
  weights [1000, 300, −70, −2] produce prices in thousands of som. The task makes feature order and coefficient
  units explicit. A short introduction defines weighted sum, weight, threshold activation, hidden layer and
  forward calculation before the network task. All three neurons use the author-confirmed threshold:
  output 1 for a weighted sum ≥ 0.5, otherwise 0, without bias terms. The students check the boundary case.
  No training is introduced. Plotting and result tables are provided with guards for unfinished answers;
  no KEY was requested. Existing separate exercises remain intact.
- **Format.** Shared dark HTML theory, boxed definitions, equation glossaries and standalone JS/SVG widgets,
  following L8–L9. The distributed notebook is unexecuted.
- **Validation.** The 72-cell student notebook executed with its unanswered TODOs and guards intact; a temporary
  completed copy passed independent numerical checks for all four tasks, including all eight binary network
  inputs and the inclusive threshold boundary. The output guard rejects nonbinary results without silently
  truncating them. Node checks covered all five widgets, control and drag handlers, mathematical invariants,
  repeated embedding, and the k slider's visibility, disabled state and scalar values. All 27 displayed formulas
  have glossaries; all 201 TeX fragments rendered with MathJax 3 offline without errors. Python figures, including
  the provided rotation plot, and exported SVG geometry snapshots were rendered to PNG and visually inspected.
  These checks do not verify the full HTML layout or browser interactions: no browser was available, and
  computer-use permissions were denied. Actual Colab UI remains unverified. The supplied diagram, source asset
  and notebook attachment are byte-identical. The build is byte-identical from a different working directory;
  the distributed notebook is unexecuted and unanswered. Preview exports are in gitignored
  `data/lesson10_validation/`. Other course notebooks and separate exercises were not changed.
- **Bridges.** Matrix columns and their linear combinations prepare basis and rank. The Xw example explains
  the calculation used in a linear model without introducing regression training.

### L11 — Linear dependence and rank

- **Classroom status.** Completed by the group, as confirmed by the author on October 15.
- **Files.** [11_linear_dependence_rank.ipynb](../math_for_ds/11_linear_dependence_rank.ipynb) ←
  `build_lesson11.py` + `lesson11_widgets.js`. Widget code and small synthetic data are embedded;
  only the notebook is needed in Colab, with no dataset download.
- **Scope.** Continue L10's matrix operations by asking which vectors or feature columns add a new direction.
  Introduce linear dependence, linear independence and rank, then define a square matrix as singular when
  its rank is smaller than its size. No determinant/inverse or linear-systems chapter, general basis theory,
  SVD, model fitting or training.
- **Data and flow.** A delivery table with morning, evening and total counts → two-vector linear combinations
  and their span → dependent and independent vectors → selectable columns and redundancy → rank as the
  number of independent directions → rank 2, 1 and 0
  transformations of a plane → duplicate volume units (litres and millilitres) and different weight vectors
  giving the same weighted sum. All examples are small and synthetic; the weights are given, not learned.
- **Visuals.** Four self-contained JS/SVG widgets show reachable combinations, column redundancy, a plane
  mapped to a plane/line/point, and duplicate units with nonunique weights. NumPy examples and standard
  matplotlib figures connect these geometric views to calculations.
- **Definitions.** Revisit linear combination and briefly define linear span before using them. Dependence means that a linear combination
  equals the zero vector with at least one nonzero coefficient; independence means that only all-zero
  coefficients do so. Matrix rank is the maximum number of linearly independent columns; row and column
  ranks are equal. Full rank means rank = min(number of rows, number of columns), including rectangular matrices.
  Distinguish a rectangular matrix with dependent columns from a singular square matrix. A short optional note
  explains that numerical rank depends on tolerance for nearly dependent data; no SVD lesson is introduced.
- **Practice.** Three short student tasks, with unanswered code and interpretation questions. A completed
  copy is used only for validation; no teacher KEY is added.
- **Format.** Shared dark HTML theory, boxed definitions, formula glossaries, embedded JS/SVG widgets and
  worked NumPy code, following L10. The distributed notebook is unexecuted.
- **Validation.** All 50 cells executed with blank guarded tasks; a temporary completed copy passed independent
  arithmetic checks on the tasks, dependence, perturbations and weights. All four widgets passed control,
  column-subset, weight, repeated-embedding and equal-axis checks. Exported SVG snapshots and the matplotlib
  plot were rendered to PNG and visually inspected. All 50 TeX expressions rendered locally with MathJax;
  the nine displayed formulas have glossaries. Rebuilding from a different working directory is byte-identical;
  the distributed notebook is unexecuted. Browser layout/interactions and actual Colab UI remain unverified:
  computer-use permissions were not granted. `git diff --check` passes.
- **Bridges.** Exact feature redundancy connects rank to later multicollinearity and model identifiability.
  These examples explain why weights can be nonunique without introducing model fitting.

### L12 — Linear systems and inverse matrices

- **Classroom status.** Completed by the group, as confirmed by the author on October 16.
- **Files.** [12_linear_systems_inverse.ipynb](../math_for_ds/12_linear_systems_inverse.ipynb) ←
  `build_lesson12.py` + `lesson12_widgets.js`. The notebook embeds its widgets, exercise statements and small
  seeded synthetic data; no dataset download or temporary source notebook is needed to build or run it.
- **Scope.** One beginner two-hour core meeting after the completed L11, before the planned correlation lesson.
  Explain linear systems and matrix equations, why a solution can be unique, absent or nonunique, and when a
  square matrix has an inverse. Introduce the determinant briefly through 2D area scaling and orientation.
  Keep the hand calculation to 2×2 matrices. No minors, Cramer's rule, LU decomposition, cross products,
  MNIST or Gradio. Class/homework exercises extend the core; the entire task set need not fit the meeting.
- **Flow.** Equations as simultaneous constraints → `Ax = b` and the intersection of two lines → connection
  to rank and singularity → defining an inverse and undoing a transformation → determinant as signed area
  scaling and the 2×2 inverse formula → `x = A⁻¹b` → `np.linalg.solve(A, b)` and checking `A @ x` →
  matrix equations → adapted exercises.
- **Visuals and definitions.** Three self-contained JS/SVG widgets show one/no/infinitely many solutions,
  forward and inverse transformations, and determinant magnitude/sign through a transformed unit square.
  Define a linear equation, a linear system and its solution, the identity and inverse matrices, and the
  determinant before using the terms. Connect invertibility to full rank for square matrices; a singular
  matrix has no inverse. Explain why a zero determinant does not by itself distinguish no solutions from
  infinitely many: that also depends on the right-hand side.
- **NumPy.** Use `np.linalg.solve` for nonsingular square systems. `np.linalg.inv` illustrates the inverse
  operation and `np.linalg.det` checks determinants. Verify results with matrix multiplication and
  `np.allclose`, without comparing floating-point results to zero as an exact mathematical singularity test.
- **Practice and provenance.** Six unanswered exercises were adapted from the teacher's temporary
  `linal_lab.ipynb`: source task 5 (2×2 determinant and inverse), 12 (`2AX − B = C`), 15 (4×4 system),
  14 (weights from the supplied formula `w = (XᵀX)⁻¹Xᵀy`, seeded 10×7 synthetic data), and optional tasks
  13 (`SXQ = B`, 5×5 matrices) and 16 (5×5 system). The two image-based statements are transcribed into
  LaTeX and NumPy. The original temporary notebook is preserved and is not a runtime or build dependency.
  The weight task is the first numerical least-squares weight calculation: state the full-column-rank
  condition and calculate predictions, but do not present a derivation or a full ML training/evaluation pipeline.
- **Format.** Shared dark HTML theory, boxed definitions, formula glossaries, standalone JS/SVG widgets and
  visible worked NumPy examples, following L10–L11. Student task cells retain unanswered placeholders;
  ready plotting/checking code is provided. No teacher KEY was requested.
- **Validation.** All 67 cells executed with blank guarded tasks. A temporary completed copy passed independent
  checks of all six solutions; the supplied weight formula also agrees with `np.linalg.lstsq`. The transcribed
  matrices and signs were checked against the source screenshots. All three widgets passed arithmetic and
  control checks across 34 systems, 867 inverse inputs and 289 determinant states, including singular cases,
  equal-axis scales and unique SVG IDs after repeated embedding. Exported SVG/PNG views and two matplotlib
  figures were visually inspected. All 111 TeX expressions render with MathJax; all 19 displayed equations
  have symbol glossaries. An isolated rebuild using only the builder, JS and `theme.py` is byte-identical,
  confirming independence from `linal_lab.ipynb`. The source notebook and older lesson hashes are unchanged;
  the distributed L12 notebook is unexecuted. Browser layout/interactions and actual Colab UI remain unverified:
  computer-use permissions were not granted. `git diff --check` passes.
- **Bridges.** Continue next with correlation and covariance. The weight formula gives a concrete future
  application of matrix operations; regression theory and a full model-training workflow remain separate topics.

### L13 — Covariance and correlation

- **Classroom status.** The sequence has progressed past L13 to the calculus and MSE seminars, whose completion
  the author confirmed. The author approved L13's scope and expanded hand-calculation practice block.
- **Files.** [13_covariance_correlation.ipynb](../math_for_ds/13_covariance_correlation.ipynb) ←
  `build_lesson13.py` + `lesson13_widgets.js` + `lesson13_tasks.py` + shared `theme.py`. The tasks module is
  used only when building the notebook. All task cells, widget code and small synthetic data are embedded;
  students need only the notebook and no dataset download.
- **Scope and data.** One beginner theory meeting on synthetic apartment area, room count and price.
  Begin with a scatterplot and paired deviations from feature means. Introduce sample covariance, revisit
  sample standard deviation, and normalize covariance to obtain Pearson correlation. Connect the same
  calculation to centered feature vectors, then covariance/correlation matrices and exact/near multicollinearity.
  Briefly introduce Spearman through ranks and monotonic relationships, then preview feature transformations
  `x²`, `x³`, `sin(x)`. No mutual information, eigenvalues/PCA or regression fitting.
- **Definitions and conventions.** Sample covariance is the sum of paired centered products divided by
  `n − 1`, for at least two paired observations. Use the same sample normalization for standard deviations.
  Covariance has the product of feature units; Pearson is dimensionless and defined only when both sample
  standard deviations are nonzero. It is the cosine between the two nonzero centered feature vectors, whose
  entries run across observations, rather than between two individual observation vectors. Covariance-matrix
  entries are pairwise covariances and diagonal entries are sample variances; the correlation matrix contains
  pairwise Pearson coefficients. Spearman is Pearson correlation of ranks, using average ranks for ties.
- **Interpretation.** Pearson measures linear association, not all dependence or causation. A zero coefficient
  can coexist with a deterministic nonlinear relationship. Spearman describes monotonic association; it does
  not detect every nonlinear relationship either. Exact linear dependence reduces the rank of the columns
  involved. Near dependence may leave the matrix full rank; strong pairwise correlation alone does not imply
  rank deficiency. Several columns can be dependent even when no pair has a coefficient close to ±1.
- **Visuals and code.** Four self-contained JS/SVG widgets accompany ordinary NumPy/pandas/SciPy calculations
  and seaborn figures. Show intermediate centered values/products and the standardization step before using
  library results. Matrix calculations use rows as observations and columns as features. SciPy is used for
  coefficients/ranks without opening a new chapter on correlation significance tests.
- **Practice.** Eight unanswered tasks emphasize small calculations by hand, NumPy verification and written
  interpretation. The first five form the core practice; three extensions may continue in class or as homework.
  Do not promise that the complete practice set fits the two-hour theory meeting. Task definitions live in
  `lesson13_tasks.py`; a completed copy is for validation only, with no teacher KEY requested.
- **Format.** The established dark HTML theory, boxed definitions, formula glossaries, standalone widgets and
  visible Python examples. The distributed notebook remains unexecuted and the student tasks unanswered.
- **Validation.** All 83 cells executed with blank guarded tasks; a temporary completed copy with an additional
  assertion cell also executed cleanly, covering all eight tasks. The five ready matplotlib/seaborn figure outputs
  and seven figure outputs in the completed copy were visually inspected. All 88 TeX expressions render with
  MathJax, including 16 displayed equations with symbol glossaries. The four widgets passed a Node DOM harness
  covering 117 slope/noise states and 37 angles, with actual SVG angles and equal vector lengths checked;
  unit changes, offsets, zero variance, ties, controls and repeated mounts also passed. Exported SVG/PNG views
  were visually inspected. An isolated rebuild using only the builder, JS, task module and `theme.py` is
  byte-identical from a different working directory. Hashes of all 13 existing notebooks are unchanged. Browser layout/interactions and
  actual Colab UI remain unverified: the browser connector was unavailable and native computer-use access
  was still pending.
- **Bridges.** Calculus and hand-coded MSE regression now follow L13, then the ML introduction in `LinModels/`.
  This places the W9–W10 modelling introduction before W7–W8 in the practical sequence. Eigenvectors/PCA remain
  planned. Feature transformations in L13 itself are a preview, with no fitting or feature-selection procedure.

### Calculus seminar — derivatives and gradient descent

- **Files and status.** [matan_seminar.ipynb](../math_for_ds/matan_seminar.ipynb), maintained by hand, with no
  builder. The author confirmed classroom completion before the MSE seminar. Do not regenerate it.
- **Content.** Sequence and function limits; derivative and finite-difference approximation; a tangent;
  one-dimensional descent, learning rate and stopping; surfaces, level curves, partial derivatives and gradients;
  numerical and analytic derivatives; two-dimensional gradient descent and local minima.
- **Practice.** Compute and plot derivatives, verify them analytically, visualize descent trajectories and
  minimize example functions. An optional decorator section implements finite differences; despite the name
  `autodiff`, it is not a lesson on automatic differentiation. No Hessian, Jacobian, Taylor expansion or SGD block.
- **Bridge.** A gradient gives the direction used to change model weights when minimizing MSE.

### MSE seminar — first hand-coded linear regression

- **Files and status.** [mse_optimization.ipynb](../math_for_ds/mse_optimization.ipynb), maintained by hand,
  with no builder. Classroom completion was confirmed by the author. Preserve the author's notebook and edits.
- **Data and flow.** The code generates 600 synthetic height/weight observations; fit an intercept and slope by
  minimizing MSE with analytic gradients and a hand-coded scaler. Inspect loss, gradient norms and trajectories,
  calculate predictions and introductory MAE/MAPE, then express the same model and updates in matrix form.
- **Practice and limits.** An additional Graduate Admissions task requests multiple features and an 80/20
  train/test split. The saved notebook has the task and loading/exploration, but does not contain a complete
  worked holdout solution. Do not infer mastery of a full evaluation workflow from that statement alone.
  Classical coefficient inference, regularization, cross-validation and a complete sklearn pipeline are absent.
- **Review debt.** The October audit identified wording and calculation issues, recorded in §10. This
  documentation update does not silently correct the hand-maintained seminar.
- **Bridge.** Students have already fitted a model. ML1 names the parts of that process and explains how to
  measure its generalization, rather than repeating gradient-descent derivations.

### ML1 — Introduction to machine learning (`LinModels/01`)

- **Status.** Newly built for the author's review; classroom use is pending. This starts the `LinModels/`
  module after the completed calculus and MSE seminars, rather than continuing the math lesson numbering.
- **Files.** [01_intro_ml.ipynb](../LinModels/01_intro_ml.ipynb) ← `LinModels/build_intro_ml.py` +
  build-only `LinModels/intro_ml_diagrams.py` + `LinModels/intro_ml_widgets.js` + shared `math_for_ds/theme.py`. Widget code, diagrams and seeded synthetic
  data are embedded in the notebook; no source-file upload, large download or API access is needed in Colab.
- **Scope.** One beginner two-hour meeting, with short presentation-like HTML/SVG sections. Start with the
  model students have already trained, then move from the general idea to dataset notation, training and
  inference, evaluation and selection. Every introduced professional term has Russian and English names;
  formulas have symbol glossaries, and the notebook ends with a bilingual term glossary and source links.
- **Definitions.** Observation and feature vector, feature matrix `X`, target `y`, labelled data, prediction,
  train/validation/test subsets, model parameters and hyperparameters, per-observation loss and empirical
  training objective, evaluation metrics, generalization, underfitting and overfitting. Loss and metrics are
  distinguished by purpose and data, not by disjoint formulas: MSE can serve both roles.
- **Visuals and examples.** Three standalone widgets show a known synthetic dependence plus noise, polynomial
  complexity and new observations, and the effect of prediction errors on squared loss/MSE, MAE and RMSE.
  Short ordinary Python examples make data construction and evaluation visible. The complexity experiment
  selects settings using validation, then freezes the choice before revealing test results.
  The three task illustrations now name concrete axes and units: delivery distance/time, message length/link
  count, and customer purchase count/average receipt. Token probabilities, the speaker timeline and MSE bars
  also have explicit labeled scales. Early terminology uses «целевая переменная» and its observed values;
  model parameters are explicitly described as values adjusted during training.
  Connected SVG diagrams replace the earlier process cards: an ML tree, training/inference sequences,
  the loss-to-parameter-update feedback loop, and a train/validation/test workflow with a decision branch.
  Separate wide and narrow diagram layouts keep text readable without hiding the relationships.
- **ML map and systems.** Supervised regression/classification, unsupervised clustering/dimensionality
  reduction, and a short reinforcement-learning overview. Self-supervised learning is explained as obtaining
  targets from the data. Modern diagrams connect next-token prediction to text generation, embedding
  clustering to a common diarization pipeline, and numerical forecasts to delivery decisions.
- **Practice (revised after author review).** Task 1 asks students to formulate five problems: used-car price,
  initial credit scoring, a building's response to an earthquake, a taxi customer's reservation price, and
  Toktogul reservoir volume by early summer. Task 2 contains three scenarios: a blocked wedding transfer,
  a police stop and support calls during a car-sharing trip, and a marketplace-chat fraud warning.
  All eight case texts preserve the author's wording, with only authorized gross typos corrected; no extra
  questions, explanations, source notes or answers are added. Task 3 retains the MSE/MAE calculation;
  Task 4 retains the original workflow/leakage question. The recorded-widget-experiment task was removed,
  while the widget itself remains.
- **Boundaries.** The true dependence is known only in the synthetic demonstration; unpredictable noise is
  relative to the available inputs. Complexity alone does not establish overfitting: compare performance on
  held-out observations. No formal bias–variance decomposition, model-architecture course, cross-validation
  chapter or new advanced-statistics block. Mini tasks remain unanswered; the distributed notebook is unexecuted.
- **Validation (Nov 2).** All ready Python cells and a temporary completed calculation task ran locally;
  all precomputed model errors were independently recalculated. `nbformat` validation and a byte-identical
  rebuild from another working directory pass. Headless Chrome checks cover all three widgets, test-choice
  locking/reset, MathJax rendering (no formula errors), and desktop/mobile layouts; Python and SVG figures
  were visually inspected. The actual Google Colab UI has not been checked. The notebook includes four
  unanswered exercises and a reference glossary; it is saved without execution outputs.
- **Bridge.** ML2 applies these ideas to Ames house prices with sklearn, a baseline and validation metrics.

### ML2 — First applied linear regression (`LinModels/02`)

- **File and status.** [02_linear_regression.ipynb](../LinModels/02_linear_regression.ipynb), maintained by hand
  without a builder. Completed in class on November 4, including a teacher-led matrix OLS derivation; the
  derivation and MAPE explanation were added to the notebook on November 5. The original root-level
  `sem_1_linregr.ipynb` and `sem_2_linregr.ipynb` are reference material and remain unchanged.
- **Format.** Markdown and Python only, explicitly requested by the author, in the style of the original
  first seminar. Short explanations precede visible sklearn code and ordinary matplotlib/seaborn plots.
  This does not change the HTML/SVG format of the theoretical ML1 notebook.
- **Data.** The original Ames/Kaggle House Prices `train.csv`, 1,460 rows and 81 columns, loaded with
  `pd.read_csv` from the author's Dropbox URL with `dl=1`; no Kaggle login is needed. Snapshot SHA-256
  `1e18addf81e5e4d347cc17ee6075bbe4a42b7fa26b9e5b063e8f692a5f929d41` is recorded in notebook metadata.
  The main features are `GrLivArea`, `GarageArea` and `TotalBsmtSF`, with no missing values in this snapshot.
  Their areas and `LotArea` are converted to square metres using a fixed conversion factor.
- **Flow.** A short regression-history/sklearn introduction → fixed train/validation/test split
  (876/292/292 rows; two `train_test_split` calls with `random_state=42`) → explore train only → mean baseline
  → one-feature OLS → three-feature OLS → coefficient interpretation and manual prediction → MAE/RMSE/MAPE on
  validation → short student tasks. Test remains unused throughout, reserved for a later final evaluation.
- **Visuals.** Training-target distribution, correlations for eight interpretable numeric features, and the
  original three-panel raw scatterplots plus sqrt-feature/log-target scatterplots (16×5, black, alpha 0.2),
  with explicit axis names. These transformations illustrate relationships; the core models predict the
  original price target. Explain OLS fitting versus the gradient-descent implementation students already know.
- **Analytical OLS addition (Nov 5).** Form the design matrix with an intercept column, differentiate MSE
  with the `2/n` factor, set its gradient to zero and obtain the normal equations. The inverse expression
  requires full column rank. Compare `np.linalg.solve`, `np.linalg.lstsq` and sklearn using the same small
  feature set; linear independence of columns is distinct from statistical independence of variables.
  MAPE is displayed in percent, with the factor 100 and zero/near-zero target limitations stated explicitly;
  no universal percentage threshold is treated as a quality guarantee. MAE remains the primary comparison
  metric, with RMSE and MAPE providing additional views of the errors.
- **Practice and boundaries.** Unanswered tasks ask for a manual prediction, adding `YearBuilt` and fitting/
  predicting/evaluating, and a comparison in words. Complete baseline and one-/three-feature examples are
  provided separately. No cross-validation, regularized-model fitting, scaling or categorical encoding is
  introduced; Ridge/Lasso are only briefly mentioned as future variants.
- **Validation (Nov 3 version).** NotebookClient executed the provided cells with the live Dropbox download and a separate
  temporary copy with completed student tasks. Checks covered disjoint splits, row alignment, the baseline
  fitted on train, numerical results, and repeatable unit conversion from a fresh copy of `raw_data`.
  Both scatterplot rows and the residual figures were visually inspected. Markdown formulas rendered in
  a Chrome nbconvert preview without errors; the actual Google Colab UI has not been checked. The distributed
  notebook retains unanswered tasks and no execution outputs.
- **Validation (Nov 5 addition).** `nbformat` and code compilation pass; all 27 code cells ran in memory
  against the local CSV snapshot. The 876×4 design matrix has rank 4, and solve/lstsq coefficients agree
  with sklearn; validation predictions differ by less than 3e-10 dollars. MAPE values were independently
  checked against the percentage formula. A temporary completed copy also passed a full NotebookClient run
  and assertions. All 113 math objects rendered without errors in a Chrome nbconvert preview; the matrix,
  inverse and MAPE formulas and ordinary figures were visually inspected. Actual Colab UI remains unverified.
  Test was not scored, and the distributed notebook retains unanswered tasks and no outputs.
- **Bridge.** ML3 adds missing values, scaling, categorical features and preprocessing pipelines. Regularization
  and model selection remain later topics.

### ML3 — Data preprocessing (`LinModels/03`)

- **File and status.** [03_data_preprocessing.ipynb](../LinModels/03_data_preprocessing.ipynb), maintained by
  hand without a builder. Successful classroom completion was confirmed by the author on November 9;
  the exact class date is not recorded. The main seminar uses
  Markdown/Python, with one author-approved self-contained HTML/CSS/JS explainer before section 2.
- **Transformer explainer.** A short Markdown lead-in connects the baseline model to preprocessing and feature
  engineering, introduces the shared transformer interface and ColumnTransformer's role in joining separately
  prepared column groups, and links to the official sklearn guide/API. Diagrams distinguish `fit`, `transform`
  and `fit_transform`, an interactive
  StandardScaler shows retained fitted values, and a Pipeline-saving example connects preparation to later
  predictions. A compact reference covers StandardScaler, MinMaxScaler, RobustScaler, OneHotEncoder and
  SimpleImputer. Diagrams label stored values with their actual fitted attribute names: `mean_`, `scale_`,
  `data_min_`, `data_max_`, `center_`, `categories_` and `statistics_`. The embedded notebook cell is canonical;
  `data/transformer_preview/transformer-memory.html` is only a preview, not a runtime dependency or builder.
- **Explainer validation (Nov 5).** The embedded cell executes independently in NotebookClient. Its five
  formulas and two SVG diagrams render in Chrome, including nbconvert output; slider endpoints, keyboard
  control and unchanged fitted values were checked. Layouts at 320, 390, 768 and 1024 pixels and the dark theme
  pass without clipped diagram labels or horizontal overflow. Numerical examples and student tasks are
  unchanged; the duplicate transformer definition below was removed. Actual Colab UI remains unverified.
- **Data and split.** Reuse ML2's Ames CSV snapshot, 60/20/20 split and observation IDs (876/292/292 rows).
  Test remains unused. Repeat the three-area model as the comparison point, then use five numeric features:
  `GrLivArea`, `GarageArea`, `TotalBsmtSF`, `YearBuilt`, `LotFrontage`. The last is street-frontage length,
  converted from feet to metres by 0.3048, not an area; 163 training rows have it missing.
  `Neighborhood` supplies 24 categories in train; validation contains `Blueste`, unseen in train.
- **Flow.** Baseline from ML2 → transformer explainer → missing-value inspection → `SimpleImputer(strategy="median")` fitted on train
  → `fit/transform` and `StandardScaler` → numeric Pipeline → a small OneHot example → ColumnTransformer
  combining numeric preparation and category encoding → a complete OLS pipeline and validation comparison.
  Show that scaled and unscaled unregularized OLS predictions are practically identical in this example;
  scaling changes representation and coefficients, not automatically forecast quality.
- **Encoding.** The toy example keeps all category indicators for clarity. The real encoder uses
  `drop="first"`, `handle_unknown="ignore"` and `sparse_output=False`: five numeric columns plus 23 indicators
  produce 28 features. Dropping one category avoids the exact indicator/intercept dependence; it does not
  promise full rank for arbitrary additional features. An unknown category gets the reference category's
  all-zero code, which is a fallback, not evidence that their actual effects are equal.
- **Comparison and practice.** Compare three areas, five imputed numeric features, and five numeric features
  plus neighborhood using MAE/RMSE in dollars and MAPE in percent on the same validation observations.
  Short unanswered tasks cover fitting a toy imputer on train and applying it to new rows, adding `LotArea`
  to the complete chain, and interpreting the three metrics and unseen categories. No CV, Ridge/Lasso
  training or target encoding is included. MAPE's limitations at zero and near-zero targets are explicit.
- **Validation (Nov 5, before the HTML explainer addition).** The provided notebook passed NotebookClient with a live Dropbox download; a
  temporary completed copy passed both student calculations and additional assertions. Checks confirmed
  matching ML2 split IDs, train-only imputer/scaler statistics, exclusion of `Blueste` from fitted categories,
  876×28 prepared features and rank 29 after adding the intercept. Scaled/unscaled OLS validation predictions
  differ by at most 4.1e-10 dollars; percentage MAPE was checked directly. Validation MAE decreases from
  $29,307.78 to $26,022.31 to $23,046.50; MAPE from 17.70% to 15.40% to 13.59% across the three models.
  All 14 math objects rendered without errors in a Chrome nbconvert preview, and ordinary figures were
  visually inspected. Actual Colab UI remains unverified. Test stays unused; the distributed notebook
  contains neither saved outputs nor student-task answers.
- **Bridge.** ML4 continues with coefficient stability, regularization and validation-based alpha selection.

### ML4 — Regularization (`LinModels/04`, third applied seminar)

- **File and status.** [04_regularization.ipynb](../LinModels/04_regularization.ipynb), maintained by hand,
  without a builder. Successful classroom completion was confirmed by the author on November 17;
  the exact class date is not recorded. It follows the completed ML2–ML3
  applied seminars rather than adding another theoretical ML introduction.
- **Format.** Markdown/Python with ordinary figures and one approved self-contained HTML/JS geometry widget
  embedded in a code cell. All widget source is inside the notebook; temporary preview/helper files under
  `data/` are not runtime dependencies or canonical build sources. Tasks remain unanswered.
- **Synthetic theory.** Revisit exact versus near multicollinearity and show how large, compensating
  coefficients can produce similar fitted values. Connect the Gram matrix `X.T @ X` to compression geometry,
  then inspect a three-dimensional SSE surface and its contours. Introduce Ridge with the SSE convention
  `||y - Xw||² + alpha * ||w||²` and the normal equations `(X.T @ X + alpha * I)w = X.T @ y` in the
  weight-only/centered setup; the intercept is handled separately and is not penalized.
- **Geometry and interpretation.** Compare the original loss contours with the Ridge constraint disk;
  distinguish a coefficient vector (parameters) from alpha (a hyperparameter). Demonstrate the effect of
  feature scale and excessive regularization. The widget varies feature correlation, alpha and a small
  perturbation of the target. Lasso appears only as a short diamond-versus-disk geometric comparison, without
  Lasso fitting. No eigenvalue/spectral derivation, statistical-significance chapter or CV chapter is added.
- **Ames continuation.** Reuse the same CSV snapshot and 60/20/20 observation IDs (876/292/292 rows), with
  test unused. The comparison model and preprocessing are ML3's five numeric features plus `Neighborhood`:
  train-fitted median imputation/scaling and the same OneHot/ColumnTransformer setup. Replace the regressor
  with Ridge while keeping the comparison data and preprocessing fixed.
- **Practice.** Unanswered tasks select alpha using validation MAE, also report RMSE and percentage MAPE,
  plot training/validation curves and interpret underfitting. Existing preprocessing and metric definitions
  are reused; no new grading threshold or guarantee that Ridge improves every dataset is introduced.
- **Validation (Nov 9).** The ready notebook ran end to end with the live CSV loader, and a separate temporary
  completed copy passed the 13-alpha search and final-model tasks. Checks confirmed the reused snapshot,
  split IDs and preprocessing, train-only fitted statistics, closed test, manual/sklearn Ridge agreement,
  scale invariance after StandardScaler and correct constraint tangencies. In the worked example alpha 10
  has validation MAE $23,279.41 versus OLS $23,046.50; this intentionally does not reveal the task optimum.
  The widget passed 144 numerical states and 724 contour-coordinate checks; browser checks covered
  320–1024 px and both themes. The final nbconvert preview rendered 88 math objects without errors;
  ordinary figures and the embedded widget were inspected. Actual Colab UI remains unverified. The
  distributed notebook contains no execution outputs or student-task solutions.
- **Reference and bridge.** The official [sklearn Ridge documentation](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html)
  documents the estimator and objective convention. ML5 continues with model diagnostics and interpretation;
  cross-validation follows that seminar.

### ML5 — Model diagnostics (`LinModels/05`, fourth applied seminar)

- **File and status.** [05_model_diagnostics.ipynb](../LinModels/05_model_diagnostics.ipynb), maintained by hand
  without a builder. Prepared for author review after the completed ML4; classroom use is pending.
- **Format and data.** Seven numbered core sections, mainly Markdown/Python, with ordinary figures and
  unanswered student tasks; the revised notebook has 72 cells, including 30 code and three `student-core`.
  The author approved one narrow HTML exception: a native `details/summary` block in Markdown for optional
  R² depth, not a return to generated HTML/JS theory. The similar-house explorer uses kernel-backed ipywidgets.
  Reuse the same Ames snapshot, 60/20/20 observation IDs (876/292/292 rows), five numeric features plus
  `Neighborhood`, and the ML3/ML4 preprocessing chain. Five ML4 cells for loading, unit conversion,
  splitting, preprocessing and the model factory are reused unchanged. Fit Ames models on train only;
  test remains unused. Small synthetic examples illustrate R², residual patterns, strongly correlated
  features and permutation importance. Global warnings suppression is explicitly requested by the author;
  the explanations of unknown-category encoding and method limitations remain in the text.
- **Quality and errors.** For nonconstant evaluated targets, introduce R² through squared error relative to
  their mean, which differs from the deployable baseline fitted to the training mean. Explain negative R², then inspect
  residuals and group errors alongside MAE/RMSE/MAPE. Concrete interpretations distinguish underprediction
  of expensive houses, unequal error spread and opposing group biases. Suggested experiments include
  additional quality features, transformed area/target and segment comparisons; none is asserted to fix the
  model without validation. Russian prose uses «изменчивость», reserving «дисперсия» for variance rather than
  an unnormalized sum of squares.
- **Optional R² depth.** The collapsible explanation relates SST to variance with divisor n, gives the
  exact training-sample decomposition for OLS with an intercept, and states why it does not generally apply
  to Ridge or held-out predictions. A separate population argument uses the conditional mean and a
  finite-variance noise decomposition to explain the best possible R² for fixed available features.
  It does not infer a noise level from a single measured R² or equate unexplained error with pure noise.
- **Five difficult predictions.** The five largest validation errors (IDs 1170, 179, 1182, 54 and 1325) are
  compared with training houses from the same Neighborhood. Euclidean distance uses only the five numeric
  features after the existing train-fitted imputer/scaler; neither price nor Id enters the distance.
  An overview and three global scatterplots locate all five cases. A selected-case table reports original
  feature/price statistics, nonmissing counts and the chosen/available neighbor counts; three local scatterplots
  distinguish the case's observed price, its prediction, neighbors and same-neighborhood train observations.
  ID 54 has only four eligible training houses; no hidden fallback broadens the comparison pool.
- **House explorer and interpretation.** A static first-case example is followed by a dropdown for the five
  cases, an n slider from 5 to 20 and a manual update button. These ipywidgets controls require a live Python
  kernel and call `show_house_context`, which can also be called directly as the fallback. Tables retain
  missing values when computing descriptive statistics even though distance uses imputation. Written notes
  interpret each case at n = 10 and propose checks of data quality, feature coverage, rare house types or
  model form. Nearest neighbors provide context, not proof of a bad price or sufficiently close analogues.
- **Coefficients and contributions.** Translate numeric coefficients back to original feature units and
  decompose one model prediction into its intercept and feature contributions. These describe the fitted
  model conditional on its other inputs; coefficient size, prediction contribution, predictive importance
  and statistical significance answer different questions. A reminder links back to ML3's `drop="first"`,
  reference category and unknown-category all-zero code. None alone establishes a causal effect.
- **Synthetic stability first.** Two almost identical features with known coefficients illustrate
  multicollinearity and compensating weights. OLS and Ridge (fixed alpha 5) use the same 120 bootstrap samples,
  refitting scaling and the regressor. Coefficient scatterplots, SD summaries and predictions at one fixed
  point distinguish weight instability from prediction instability; a stable but shifted Ridge prediction
  demonstrates that more stable weights do not guarantee smaller prediction error.
- **Ames bootstrap stability.** Resample complete training rows 80 times, keeping each target with its features,
  and refit the entire preprocessing/model pipeline. Compare OLS and Ridge on the same resamples with
  `alpha=10` fixed. Inspect the five numeric coefficients in common original units and predictions for one
  fixed house. The five coefficients occupy one figure; a separate figure shows the same house's price
  prediction across resamples. Category coefficients are not compared because categories can disappear.
  Concrete interpretation and an SD table acknowledge that Ridge need not reduce every coefficient's spread.
  These are stability experiments for specified fitting procedures; their spread is not presented as a formal
  confidence interval or a coefficient-significance test. Alpha is not retuned within resamples.
- **Permutation feature importance.** Keep the fitted full pipeline frozen and shuffle raw validation
  columns, so a categorical feature is inspected as one input rather than separate dummy columns. With
  `neg_mean_absolute_error`, score deterioration equals an increase in MAE. Repeated permutations describe
  shuffle variability. Importance depends on the fitted model, metric and evaluated data; correlated features
  can substitute for one another, and shuffling can create implausible feature combinations.
  A worked ablation removes `Neighborhood` and refits at the same alpha, illustrating why removal with
  retraining answers a different question from shuffling one input of a frozen model.
- **Practice.** Three unanswered code tasks: compare neighborhood MAE and mean residual for groups with at
  least ten validation houses; calculate OLS permutation importance and compare it with Ridge; predict the
  change for an extra 10 m² using both the original-unit coefficient and `predict`. A final written report
  combines quality, an error pattern, a coefficient/stability observation, feature importance and a proposed
  follow-up. The group-size threshold is a teaching convenience, not a reliability guarantee.
- **Optional inference and limits.** A separate synthetic sample has 400 independent rows, two independent
  features and a linear mean with heteroscedastic errors. `statsmodels.OLS` with `cov_type="HC3"` and
  `use_t=False` illustrates standard errors, approximate normal confidence intervals and p-values.
  Statistical significance is distinct from practical or predictive importance. The assumptions and results
  of this synthetic example do not transfer to Ames or Ridge; HC3 does not repair a misspecified mean,
  dependent rows or hypothesis selection after inspecting results. This is an introduction, not a complete
  inference course. Cross-validation and final test evaluation are not introduced here.
- **Dependency.** `statsmodels>=0.14,<0.16` is listed in `requirements.txt`; the optional inference cell
  installs it only when the package is absent. The main seminar does not import it. `ipywidgets` is already
  a project dependency and supplies the optional house-explorer controls; the static example does not need them.
- **Validation (Nov 17, final revision).** All 72 cells (30 code, three student-core) pass `nbformat` and
  compilation. The notebook ran with the live Dropbox loader, and a separate completed copy passed all three
  tasks; the five preparation cells and three student-core sources remain unchanged. Neighbor checks cover
  all five cases at n = 5/10/20: same-neighborhood train candidates, correct distances/statistics, no price/Id
  dependence or fitting during display. Ten native widget button clicks exercised all cases at n = 5/20.
  All five case figures were inspected and clipped axis labels corrected. Chrome rendered 109 MathJax objects
  without formula or JS errors; the collapsible block and displayed controls were checked. Execution outputs
  contain no UserWarnings. Reports are in gitignored `data/diagnostics_revision/` (`render_report.json` and
  `native_callback_report.json`). The distributed notebook has no outputs or task answers, test remains unused,
  and actual Colab UI remains unverified.
- **Official references and bridge.** [sklearn R²](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.r2_score.html),
  [permutation feature importance](https://scikit-learn.org/stable/modules/permutation_importance.html) and
  [statsmodels OLS](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLS.html)
  with [robust covariance](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLSResults.get_robustcov_results.html)
  document the metrics and inspection/inference tools. Cross-validation is the next planned topic.

---

## 5. Syllabus vs. what was built

| Syllabus | Planned | Built | Comment |
|---|---|---|---|
| W1 | Random variable, mean, variance, SD; vector, norm, dot product; z | L1, L2, L3, Seminar 1, H, house.kg seminar project | **Done.** The random variable is kept intuitive and formalised in L5–L6. |
| W2 | Normal, three sigma, Bernoulli, binomial; LA: linear combinations | L5, L6; L1 and L10 (LA) | Statistics done and extended (PDF/CDF in L6). L10 revisits linear combinations through matrix columns and multiplication. |
| W3 | Poisson; basis, rank, multicollinearity | L10–L11; L13 multicollinearity | **Partly built.** Exact/near dependence and the limits of pairwise correlation are included. General basis theory and Poisson remain pending. |
| W4 | Covariance, correlation, covariance matrix; milestone presentation 1 | L13 | Includes Pearson/Spearman, covariance/correlation matrices and their geometric connection; the sequence has since moved into calculus/MSE. The milestone presentation is not designed. |
| W5 | Matrices as operators | L10; inverse transformations in L12 | Matrix action, composition and undoing a nonsingular transformation introduced visually. Later Phase 2 topics remain pending. |
| W6 | Determinant and inverse; singularity | L11–L12 | **Introductory scope built.** Rank-based singularity, linear systems, inverse and 2D determinant geometry. Hand determinant calculation stops at 2×2. |
| — | *(not in the syllabus)* | L4 | Robust, non-parametric tools, needed because the real data are dirty. |
| — | *(not in the syllabus)* | Bus practicums, L7–L9 | Sampling, SE, CLT, CIs and bootstrap; L9 closes the block with permutation hypotheses, p-values and practical interpretation. Tests were brought forward from W12. |
| — | *(not explicit in the syllabus)* | Calculus seminar | Derivatives, gradients and numerical optimization were added before first model training; completed in class. |
| W7 | Eigenvectors and eigenvalues | — | **Not built in the math sequence.** Planned after the OLS introduction rather than before it. |
| W8 | PCA, SVD overview | `unsupervised/01`; covariance groundwork in L13 | Exists as an ML lesson; the eigenvector groundwork and its integration remain pending. The new math sequence plans PCA after OLS and eigenvectors. |
| W9–W10 | Projections, least squares, linear regression | L12 formula exercise; completed MSE/ML2–ML4; `LinModels/01–05` | Fitting, matrix OLS, preprocessing and Ridge are taught. ML5 adds diagnostics, coefficient interpretation/stability and permutation importance for review; geometric projection treatment and CV remain pending. |
| W13 | Trees, ensembles, metrics, cross-validation | `DT/`; introductory metrics in MSE seminar and ML1 | The tree module predates the math block. Basic loss/metric roles are now introduced earlier; a dedicated cross-validation lesson remains pending. |

**The overall pattern:** the statistics track is ahead of the plan. L10–L12 resume linear algebra through matrix
operations, transformations, dependence, rank, linear systems and inverses. L13 connects those tools to covariance,
correlation and multicollinearity. Calculus and MSE regression now precede the `LinModels` introduction; this
deliberately moves the W9–W10 introduction ahead of W7–W8. ML2–ML4 are completed and ML5 adds diagnostics
and interpretation for review. Cross-validation, eigenvectors/PCA groundwork and general basis theory remain pending.

---

## 6. What students know so far

*The sequence has progressed through L13, the calculus/MSE seminars, ML2 (completed November 4), ML3
(completion confirmed November 9) and ML4 (completion confirmed November 17). ML5 awaits review/classroom use;
ML1's classroom status is unconfirmed.* Practice tasks
must account for these statuses; new concepts must be introduced before they are required. The separate
L9 classroom status below has not been confirmed.
Anything outside the inventory has to be taught first.

**Linear algebra (L1–L2).** Vector as an observation; feature space ℝⁿ; addition, scaling, linear combination
(introduced); L2 norm, distance; centroid as the mean vector; dot product, projection, angle; cosine similarity and
distance; L2 normalization; nearest neighbour by Euclidean vs. cosine distance; embeddings and attention (as ideas).

**Matrices (L10).** Dimensions, elements, rows and columns; equality, addition, subtraction,
scalar multiplication and transpose; dot product and linear combination revisited; matrix-vector multiplication
as row dot products and a combination of columns. Linear transformations in two dimensions, the standard basis
e1 = (1, 0), e2 = (0, 1) and its images; matrix multiplication and compatible shapes; identity, associativity,
distributivity, noncommutativity and composition order. Weighted sums Xw and transforming row-stored
observations with X @ A.T. Practice adds feature order and coefficient units, multiple given weight sets as
matrix columns, and a small threshold network's forward calculation: weighted sum, weight, threshold activation
and hidden layer. No model fitting or neural-network training.

**Dependence and rank (L11, completed in class).** Linear span; linear dependence and independence;
zero and nonzero coefficient combinations; redundant columns and the maximum number of independent columns
(rank). Equality of row and column rank; full rank for square and rectangular matrices. Two-dimensional matrix
images with rank 2, 1 or 0; square-matrix singularity defined through rank. Duplicate units as exact feature
redundancy; nonunique given weights can produce identical weighted sums. Numerical rank tolerance is mentioned
in a short optional note, without SVD.

**Linear systems and inverse (L12, completed in class).** Linear equation, system and solution; `Ax = b`
with compatible shapes; one, no or infinitely many solutions; connection between square-matrix rank,
singularity and invertibility. Inverse defined by `A⁻¹A = AA⁻¹ = I`; recovering an input, `x = A⁻¹b`, and
checking by substitution. The 2×2 determinant formula, determinant magnitude as area scaling and its sign as
orientation; zero determinant and collapse. Matrix equations preserve multiplication order. A first
least-squares weight calculation uses the supplied formula `w = (XᵀX)⁻¹Xᵀy` for full-column-rank synthetic
data, followed by predictions `Xw`; there is no derivation, regression-theory chapter or full training workflow.

**Covariance and correlation (L13, preceding the completed seminars).** Centering paired observations, sample
covariance with `n − 1`, covariance units, sample-standard-deviation normalization and Pearson correlation.
Pearson as the cosine between centered feature vectors; covariance/correlation matrices and their diagonals.
Pearson is undefined for a constant feature and does not measure every nonlinear relationship or imply causation.
Ranks, average ranks for ties, Spearman as Pearson of ranks, monotonic versus general nonlinear relationships.
Exact and near multicollinearity, full rank despite strong correlation, and dependencies among several columns
that pairwise coefficients may miss. Feature transformations `x²`, `x³`, `sin(x)` are a preview, without fitting.

**Calculus (completed seminar).** Sequence/function limits; derivatives and tangents; analytic checks and
finite-difference derivatives; one-dimensional descent, learning rate and stopping; level curves, partial
derivatives, gradient as a vector and two-dimensional gradient descent. Local minima and dependence on
initialization are explored. The optional `autodiff` decorator is numerical differencing, not automatic
differentiation; no Hessian/Jacobian, general chain-rule course or SGD is assumed.

**First regression fitting (completed MSE seminar).** An intercept/slope model, MSE, analytic weight gradients,
hand-coded full-batch gradient descent, loss and parameter trajectories; scaling for optimization; predictions,
the design matrix and vectorized updates. MAE and MAPE are introduced, chiefly on training observations.
The multifeature holdout task is present as an assignment, not a complete saved evaluation solution. Do not
equate coefficient magnitude with feature importance or statistical significance.

**ML introduction (ML1, pending review/classroom use).** Model, training and inference; observation, feature,
target/label and labelled data; `x_i`, `y_i`, `X`, `y` and dataset notation; train/validation/test roles;
parameters versus hyperparameters; per-object loss, empirical objective and evaluation metrics (MSE/MAE/RMSE);
generalization, underfitting/overfitting and the effect of sample size/noise. An introductory map of supervised,
unsupervised and reinforcement learning, with regression/classification/clustering, dimensionality reduction
and self-supervised targets. Next-token prediction, speaker-embedding clustering and delivery forecasts are
application illustrations, not training lessons for large language or audio models.

**Applied linear regression (ML2, completed November 4).** Fixed train/validation/test split;
training-only exploration; the training mean as a baseline; `LinearRegression.fit/predict`, `coef_` and
`intercept_`; manual prediction and conditional coefficient interpretation; comparison of one- and three-feature
models with MAE/RMSE on validation. Matrix OLS was derived in class: intercept column, gradient of MSE,
normal equations, full-column-rank condition and the inverse expression. The November 5 notebook addition
records this derivation, compares `solve`/`lstsq`/sklearn and adds explicit percentage MAPE with zero/near-zero
limitations. Test is reserved, not repeatedly used for comparison. No regularization or CV chapter is included.

**Data preprocessing (ML3, completion confirmed November 9).** Preprocessing and feature engineering terminology;
missing numeric values and train-fitted median
imputation; `fit`, `transform`, `fit_transform`; scaling and coefficients versus OLS predictions; Pipeline;
categorical features, OneHot indicators, reference category and unseen categories; ColumnTransformer and
a complete mixed-feature OLS chain. Compare MAE/RMSE/MAPE on the same validation observations, with all
learned preprocessing fitted on train and test kept unused.
The added transformer explainer names fitted attributes, compares five common transformers and introduces
saving the fitted Pipeline for later predictions.

**Regularization (ML4, completion confirmed November 17).** Exact/near multicollinearity and compensating weights;
Gram matrix `X.T @ X`, compression and SSE surface/contour geometry; Ridge penalty and normal equations with
an unpenalized intercept; weights versus alpha; feature scale; a Ridge constraint disk and a brief Lasso
diamond comparison. Perturbation experiments examine stability. Choose alpha on validation MAE, also inspect
RMSE/MAPE and training/validation curves; distinguish excessive regularization and underfitting. No Lasso
fitting, CV, spectral theory or coefficient inference is assumed.

**Model diagnostics (ML5, pending review/classroom use).** R² and its evaluated-target mean reference;
optional OLS variance decomposition and population noise bound. Residuals and group errors; closest training
analogues by scaled numeric distance within a neighborhood, with counts and limitations; coefficients in
original units, reference category and contributions to one prediction. Strong-correlation synthetic and
full-pipeline Ames row bootstrap at fixed alpha separate coefficient stability from prediction stability,
without claiming formal confidence intervals. Permutation
feature importance evaluates the frozen pipeline on shuffled raw validation columns, with negative-MAE
scoring and correlated-feature limitations; a worked drop-column comparison refits after removing an input.
An optional OLS inference introduction uses separate synthetic data and HC3/normal approximation to distinguish
significance from predictive importance; it does not establish mastery of a complete inference workflow.

**Descriptive statistics.** Population vs. sample, representativeness, bias; histogram, 1D and 2D KDE, mode; mean,
median, variance, SD, SSE; group statistics (`groupby`); z-standardization; normalization by a meaningful
quantity (a rate, e.g. price per m²); percentiles and quantiles, quartiles,
IQR, boxplot, the 1.5·IQR rule; cleaning outliers by percent or by whiskers; StandardScaler, RobustScaler.

**Probability.** Trial, outcome, event; probability as a long-run proportion; a random variable and its law;
Bernoulli and binomial (np, np(1−p)); the normal and 2D normal distributions; three sigma (68–95–99.7); PMF, PDF,
CDF and the survival function; area as probability; moving an event to the z-scale; one and two tails; model vs.
observed frequencies. From the bus practicum: the empirical CDF, Monte Carlo simulation, the waiting-time paradox.

**Sampling.** The sample mean as a statistic; the sampling distribution; SE = σ/√n and its estimate s/√n; the law of
large numbers; the classical CLT; the difference of two group means and its SE.

**Estimation (L8).** Confidence intervals, confidence level, repeated-study coverage; known-σ normal intervals
(exact for normal observations, CLT approximation otherwise); ordinary nonparametric bootstrap, bootstrap SE,
percentile intervals and nested coverage simulation. Parametric, paired, cluster, block and stratified schemes
and basic/BCa intervals are introduced as an overview. A statistical hypothesis is defined as a bridge only.

**From the completed post-L8 bus practicum.** Pairing by date/window, equally weighted daily
differences, within-pair label swaps/sign flips, a two-sided empirical tail fraction under an explicit symmetric
scenario, one-sample bootstrap of differences, two approximate intervals. These do not yet constitute a formal
lesson on hypotheses, p-values or significance rules.

**Hypothesis testing (L9, pending classroom use).** Null and two-sided alternative, test statistic, conditional
p-value definition, Monte Carlo plus-one correction, preselected α, type-I error and statistical significance.
Failure to reject vs. proof of equality; independent two-sample bootstrap for the mean difference; CI vs. test;
practical improvement threshold. No t-distribution or t-test, power calculation, multiple-testing correction,
or comprehensive test-selection catalogue.

**Tools.** numpy, pandas (`describe`, `groupby`, `quantile`), seaborn (histograms, KDE, boxplots),
`scipy.stats.norm` (`cdf`, `sf`, `ppf`), `scipy.stats.bootstrap`, NumPy resampling (`Generator.choice`), sklearn scalers and `NearestNeighbors`.
L10 adds explicit array-shape conventions, transpose, `@`, `np.matmul`, vector/matrix uses of `np.dot`,
and their distinction from elementwise `*`. L11 adds `np.linalg.matrix_rank` on small synthetic matrices.
L12 adds `np.linalg.solve`, `np.linalg.inv`, `np.linalg.det` and verification with `np.allclose`.
L13 adds sample covariance/correlation calculations with NumPy and pandas, rank-based coefficients with
SciPy, and seaborn scatterplots/heatmaps; row/column conventions and sample normalization are explicit.

**Not taught yet. Do not use without teaching it first:** Poisson; t-tests and the Student distribution;
general basis theory and eigenvectors; mutual information; PCA/SVD; geometric least-squares derivation;
MLE; logistic regression; regression coefficient inference; model diagnostics and permutation feature importance;
cross-validation; neural-network learning/backpropagation. ML5's new concepts await classroom use; ML3's
preprocessing pipelines and ML4's regularization are available prerequisites. The sklearn workflow and matrix
OLS derivation are available from completed ML2; its train/validation/test
practice is confirmed independently of ML1's unconfirmed classroom status. L10/L12 retain their narrower
given-weight/supplied-formula scope.

---

## 7. ML modules

### `LinModels/` — introduction to ML and linear models (Phase 3)

| Order | Notebook | Content | Status |
|---|---|---|---|
| 1 | `01_intro_ml.ipynb` | ML terminology, features/targets and dataset notation, train/validation/test, loss/metrics, parameters/hyperparameters, generalization/complexity, map and modern systems, bilingual glossary | Awaiting author review and classroom use |
| 2 | `02_linear_regression.ipynb` | Ames regression, matrix OLS derivation, baseline, coefficients and validation metrics; unanswered tasks | Completed Nov 4; OLS/MAPE text added Nov 5 |
| 3 | `03_data_preprocessing.ipynb` | Missing values, scaling, Pipeline, OneHot/ColumnTransformer, unseen categories, mixed-feature OLS and MAE/RMSE/MAPE | Completed; confirmed Nov 9, exact class date unrecorded |
| 4 | `04_regularization.ipynb` | Coefficient stability, loss/constraint geometry, Ridge, scale, brief Lasso comparison, validation-based alpha selection on Ames | Completed; confirmed Nov 17, exact class date unrecorded |
| 5 | `05_model_diagnostics.ipynb` | R², residuals/groups and similar-house explorer, coefficient units and prediction contributions, synthetic/Ames bootstrap stability, permutation feature importance, optional OLS inference | Awaiting author review and classroom use |

The module follows the hand-maintained calculus and MSE seminars. Its generated theoretical notebooks retain
the shared dark HTML/SVG format; the first builder is `LinModels/build_intro_ml.py`. ML2–ML5 are hand-maintained
seminars without builders: Markdown/Python, plus one approved embedded transformer explainer in ML3 and one
geometry widget in ML4. ML5 has a native `details/summary` block in Markdown and a live-kernel ipywidgets
explorer with static/manual alternatives. Cross-validation follows ML5; broader model-selection lessons remain planned.

The following two modules were built in **June 2026, before the math block**, as standalone ML lessons. In the syllabus they become
week 13, "classic models with understanding". When Phases 2–3 exist, they should be re-linked to the new math (the
re-linking points are listed below).

### `DT/` — decision trees and ensembles

| Order | Notebook | Content |
|---|---|---|
| 1 | `dt_demo.ipynb` | Splitting Iris by hand (boolean rules → a tree); impurity criteria and their probabilistic meaning; information gain; a 1D task with threshold search; sklearn `DecisionTreeClassifier` vs. logistic regression; pruning (`max_depth`, `min_samples_leaf`) on the Rice dataset; feature importances; regression trees (MSE/MAE/Poisson criteria, step approximation, Gaussian noise) |
| 2 | `bias_variance_demo.ipynb` | True dependence and noise, model complexity, resampling, the bias–variance decomposition, a tree vs. a linear model, averaging |
| 3 | `bagging_rf.ipynb` | Bootstrap and OOB (~37%), bagging and when it helps, random forest (`max_features` and decorrelation), a churn case (telecom churn): validation curves, `GridSearchCV`, OOB estimate, feature importance |
| 4 | `gradient_boosting.ipynb` | Boosting vs. bagging, learning on residuals, the link to gradient descent (boosting linear models converges to OLS), learning rate and number of trees, classification, XGBoost/LightGBM/CatBoost, tuning and early stopping, stochastic GB, interpretation (SHAP) |
| — | `theory/index.html` | Interactive HTML handbook (SVG + vanilla JS, offline; MathJax from a CDN), 8 chapters: math warm-up, glossary, supervised setup, trees, bias–variance, bagging, boosting, cheat sheet |
| — | `*.pdf` | **Third-party:** E. A. Sokolov's lecture notes (HSE Faculty of Computer Science, 2021), lectures 8–10: trees; bagging, RF and bias–variance; gradient boosting. Supplementary reading |

Recommended order: handbook ch. 1–3 → `dt_demo` → `bias_variance_demo` → `bagging_rf` → `gradient_boosting`, with
handbook chapters 4–7 after each notebook.

**Notes.** The interactive parts use `ipywidgets` and need a live kernel, unlike the math_for_ds widgets, which are
self-contained HTML/JS. `dt_demo` has older origins (its first cell credits 2024 lecture notes).
**Re-linking points:** these notebooks assume logistic regression, loss functions, gradient descent, train/test split,
classification metrics (accuracy, F1, ROC-AUC) and cross-validation. In the syllabus, logistic regression and MLE
come in Phase 3, and metrics and cross-validation in W13. The added calculus/MSE seminars now supply derivatives,
gradients and first fitting; ML1 introduces evaluation terminology. Classification metrics and cross-validation
still need teaching. The handbook's chapter 1 offers further groundwork: probability, expectation, logarithm,
derivative and gradient, convexity, Jensen.

**Related project (external).** [`ai-academy-bish/kws-project`](https://github.com/ai-academy-bish/kws-project)
detects the keyword «Акылай» in audio. It was a project assignment for the topic «Классификация: линейные модели,
деревья и ансамбли» (June 2026, built alongside this module). Its stages: a baseline with honest metrics, linear
models, trees and ensembles, error analysis, the choice of model and threshold, streaming inference. Data: HF
`aiacademy-kg/kws-dataset` (ready-made audio features). It assumes logistic regression and SVM, which are not in this
repo.

### `unsupervised/` — dimensionality reduction and clustering

| Order | Notebook | Content |
|---|---|---|
| 1 | `01_dimensionality_reduction.ipynb` | Why reduce dimension; SVD as principal directions; compression; PCA; PCA on speaker embeddings; non-linear manifolds (swiss roll); t-SNE and perplexity, its pitfalls; PCA vs. t-SNE |
| 2 | `02_clustering_foundations_kmeans.ipynb` | Problem setting and types; similarity = distance, scaling; internal and external metrics; K-Means (objective, Lloyd, k-means++, assumptions); choosing k; speakers |
| 3 | `03_gmm_em.ipynb` | Soft clustering; Gaussian mixtures; responsibilities; EM; the link to K-Means; covariance types; BIC/AIC; confidence of assignments; speakers |
| 4 | `04_density_dbscan_hdbscan.ipynb` | Core, border and noise points; `eps`; the k-distance plot; varying density; HDBSCAN; comparison; anomaly search; atypical speaker clips |
| 5 | `05_hierarchical_dendrograms.ipynb` | Agglomerative algorithm; linkage; distance metrics; reading and cutting a dendrogram; a bioinformatics heatmap; 20 Newsgroups with TF-IDF |

**Data.** Speaker embeddings from `aiacademy-kg/audio-3-speaker-dataset`. Only the embedding columns are pulled, not the
2.65 GB of audio, and they are cached locally as `speaker_emb.npz` (gitignored). Also sklearn toy sets and
20 Newsgroups.
**Re-linking points.** `01` overlaps syllabus W8 (PCA/SVD). When Phase 2 is built, decide whether `01` stays the
applied continuation of W8 or is reworked to build PCA from covariance and eigenvectors, as the syllabus intends.
`03` (Gaussians, likelihood, EM) relies on MLE from W11. Seminar 1 already uses the same speakers, which gives
students a familiar dataset here.

---

## 8. Datasets

| Dataset | Source | Used in | Notes |
|---|---|---|---|
| Davis (height and weight, 200 people) | HF `aiacademy-kg/davis_dataset` | L1–L5; six-row embedded extract in L10 | Measured and self-reported values; small enough to compute by hand |
| house.kg listings (Bishkek) | HF `aiacademy-kg/house_kg_full_dataset`, file `data/listings.parquet` | house.kg seminar project, L4, L5 | Filter `deal == "sale"`, `type == "apartment"`, `city == "Бишкек"`; `price_usd` is strongly skewed |
| Lalafo phones | HF `aiacademy-kg/lalafo-kg-phones` | `practice/phones` | Load `listings` and `users`; never `images` (~5 GB) |
| Lalafo cars | HF `aiacademy-kg/lalafo-kg-cars` | `practice/cars` | Never `images` (78 GB); ≈40% of prices are in USD |
| Bishkek public-transport feed | HF `aiacademy-kg/bishkek-transport` (pinned revision) | Two bus practicums; L7 (embedded summaries) | 372 M rows; 21 MB extract or original loader fallback |
| Speaker audio + WavLM embeddings | HF `aiacademy-kg/audio-3-speaker-dataset-v2` / `aiacademy-kg/audio-3-speaker-dataset` | Seminar 1 / `unsupervised/` | Load only the embedding columns where possible |
| Iris; Rice (zip on Dropbox) | seaborn; Dropbox link in the notebook | `dt_demo` | |
| Telecom churn | CSV from the mlcourse.ai GitHub repo | `bagging_rf` | |
| sklearn toy sets, 20 Newsgroups | sklearn | `DT/`, `unsupervised/` | |
| Keyword-spotting audio features | HF `aiacademy-kg/kws-dataset` | `kws-project` (external) | Features already extracted |
| Ames / Kaggle House Prices training table | Author's Dropbox copy of `train.csv` (download URL and snapshot SHA-256 in the notebooks) | `LinModels/02–05` | 1,460×81; no Kaggle login; identical 876/292/292 split, train-only exploration/preprocessing, test unused |
| Synthetic data | generated or embedded in the notebook | L6–L13, calculus/MSE seminars, `LinModels/01`, `04–05`, `bias_variance_demo`, `gradient_boosting` | Known laws in statistics; small matrices and points, courier/car features (L10), totals and duplicate volume units (L11), linear systems and seeded 10×7 features (L12), apartment features and nonlinear relationships (L13); height/weight regression (MSE); delivery dependence, noise and held-out observations (ML1); coefficient stability and regularization geometry (ML4); R², residual patterns, strong-correlation stability, permutation importance and optional OLS inference (ML5) |

**Where the data come from.** All `aiacademy-kg/*` datasets are published on the school's Hugging Face organization,
[huggingface.co/aiacademy-kg](https://huggingface.co/aiacademy-kg). The scrapers that build the house.kg and Lalafo
datasets live in the school's GitHub organization,
[ai-academy-bish](https://github.com/orgs/ai-academy-bish/repositories) (`house_kg_parser`, `lalafo_parser`). Their
docs describe every field and the known pitfalls, so read them before designing a task on these data.

**Anchor datasets.** The syllabus asks that the group's anchor datasets together cover: a nearly normal feature, a
count of events (for Poisson), strongly correlated or exactly redundant features, structure for PCA, and a
binary target. Strong correlation does not by itself imply rank deficiency; exact linear dependence of columns
does. The list of students' anchor datasets is not recorded in the repo.

---

## 9. Methodological conventions

### 9.1 Teaching

- **Experience first, then the name, then the formula.** L5–L8 use this "genetic" order explicitly: an experiment or
  widget → «что мы увидели» → a precise definition.
- **Predict, act, explain.** Before moving a slider, the student predicts the result; afterwards, they explain it in
  words.
- **A «Где: …» block under every displayed formula**, explaining every symbol (CSS class `.where`; in L6–L13 enforced
  by the `eq()` helper).
- **Optional depth** goes into `<details>` blocks («для тех, кто хочет глубже»), so the main line stays short.
- **English terminology is introduced gradually:** an English gloss next to the Russian term (class `.en`).
- **By hand in numpy first, then the library.**
- **Interpretation over derivation.** Each assignment includes at least one question from the syllabus's
  interpretation bank, or one written in its spirit. Such a question cannot be answered by pasting an LLM's output:
  it requires linking a mathematical fact to *these* data.
- **No ready answers in student materials.** TODO hints are given in words, never as the finished line of code.
  Teacher answers live in KEY versions («Для преподавателя»).
- **Only concepts already taught** (§6). Before students complete L13, express a relationship between features
  with group medians, a scatter or 2D KDE, and centroids. Correlation becomes available after its definitions
  and limitations have been taught in L13; do not retrofit it into earlier prerequisite-limited assignments.
- **Practicum framing.** The layperson vs. the researcher. Real dirty data are left dirty. Mathematics is
  recommended only where it is needed. Students defend their conclusions with plots and a short memo or talk.
- **Long lessons mark their split points** (L6, L7 and L8 are each designed for two meetings).

### 9.2 Tone and language

- **Lesson prose is in Russian**: academic but accessible, in the manner of good Soviet textbooks. No GPT-style
  jargon, no ideology, no conversational metaphors: «устраняет», «подавляется», «определяется преимущественно»
  rather than «лекарство», «тонет», «захватывается». Axioms and properties are given as lists, not as running text.
- **Practicums may be livelier** (emoji headings, a "rules of the game" section), but definitions stay strict.
- **Code comments and docstrings are in English.** Strings students read (plot titles, axis labels, widget labels,
  printed messages) are in Russian.
- **Task statements:** L2's practice block is in English; L3 onwards are in Russian (§10).

### 9.3 Generated lesson format (`math_for_ds/` and `LinModels/`)

- Google Colab `.ipynb`, **committed un-executed**, generated by `build_lessonN.py` with nbformat. Change the script,
  not the notebook, except for the hand-maintained files (see AGENT_PROTOCOL §4).
- The first code cell is **SETUP** from `theme.py`: dark-theme CSS, SVG/JS helpers and `viz(body, script, wide)`.
- Theory is HTML in collapsed `#@title … { display-mode: "form" }` cells. **Each output is self-contained** (CSS +
  JS + MathJax inline), because Colab isolates cell outputs.
- Theory visualisations are **live JS/SVG** (draggable points, sliders), not matplotlib. Matplotlib/seaborn appear in
  the code students write. Angles and circles need the square plane `plane(half)`.
- MathJax with `$…$` and `$$…$$` delimiters only.
- Current pattern (L6–L13): widgets in `lessonN_widgets.js` embedded at build time; deterministic cell ids; the `eq()`
  glossary guard; references to authoritative sources (NIST, SciPy, Penn State, OpenStax).
- `LinModels/01` follows the same pattern with `build_intro_ml.py` and `intro_ml_widgets.js`, a presentation-like
  visual flow and a final bilingual glossary. Its build-time dependency on `math_for_ds/theme.py` is embedded;
  no repository source files are required at runtime in Colab.
- L9 uses this same theoretical-lesson format, with short definitions and explanations. Its numerical helpers
  and standard Python plots are also embedded. The Markdown-only bus practicum format does not carry over
  to theoretical lessons.

### 9.4 Practicum format

- **Applied ML seminars (`LinModels/02–05`):** hand-maintained Markdown and Python, ordinary figures and visible
  worked sklearn examples, followed by unanswered student tasks. The author requested the original seminar's
  scatterplot style and a short library/algorithm explanation. ML3 has a local exception: one self-contained
  HTML/CSS/JS transformer explainer before section 2. ML4 has one approved embedded HTML/JS geometry widget.
  ML5 has one approved native `details/summary` block inside Markdown, plus an ipywidgets similar-house
  explorer requiring a live kernel; its static example and direct function call remain available.
  The remaining sections retain Markdown/Python.
  ML1 remains an HTML/SVG theoretical lesson.
- **Lalafo pattern:** study the dataset first (`recon.py` → teacher-facing `RECON.md`), then `build_<topic>.py`,
  Markdown only, feature engineering done in advance, five cases. Before shipping, run the feature-engineering cell on
  the local parquet and confirm that each case has a real signal (in medians).
- **Bus pattern:** one research question; Part 0 is a pipeline built in advance and explained step by step; tasks
  have a «Ваш вывод» cell and a teacher note; two memos; a pinned data revision and a small prepared extract.

---

## 10. Open questions and next steps

**Next to build**

The author requested one final statistics meeting, now L9, then moving on within the remaining two months.
Further statistical detail should be introduced when a later task needs it.

1. **Review ML5, then teach cross-validation:** ML2–ML4 are completed, including matrix OLS, preprocessing
   and Ridge. `LinModels/05` adds diagnostics, coefficient interpretation, bootstrap stability and permutation
   importance. Cross-validation and broader model selection follow; their concrete scopes need agreement.
   ML1's classroom status
   is not inferred from ML2's completion. Eigenvectors/PCA and general basis theory remain backlog;
   the regression introduction deliberately precedes W7–W8 topics.
2. **Milestone presentation 1** (W4): not designed yet.
3. **Poisson** remains syllabus backlog; do not add another statistics meeting automatically.

**Decisions needed**

- **L3, S4 Task 8** asks for a correlation coefficient before L13 in the teaching order.
  Reword it, defer it until L13, or treat it as a deliberate spoiler?
- **Language of task statements:** English (L2) or Russian (L3 onwards) from now on?
- **`04_stat_boxplot.ipynb`:** keep the 17 in-class cells in the canonical version, or move them to the build script
  or to a separate class log? A rebuild currently drops them.
- **`vektornaya-algebra-hw`:** credit the source textbook.
- **`math_for_ds/theory/`** (Aug 24, L1 only; L2 marked «готовится») has been replaced by the Colab format. Archive or
  delete it?
- **`DT/*.pdf`** are third-party (HSE). Check redistribution rights before the repo is made public.

**Technical debt**

- The hand-maintained `mse_optimization.ipynb` has audit findings not corrected by the ML1 addition:
  its introductory text calls generated observations real; one vectorized gradient omits the factor 2 for
  the stated MSE; residual-versus-observed-target trends are overinterpreted; the final task's scaling order
  risks leakage; standardized coefficient size is described as importance (the author acknowledged this
  wording error). Review these in a separate authorized edit. Normal errors are not required simply to fit
  least squares, and percentage-error thresholds are not universal quality guarantees.

- L7 §7 still announces tests for “the next lesson”. The author-approved sequence now inserts L8 (CI/bootstrap)
  before tests in L9. L8 explains the detour; update that historical bridge when L7 is next revised.

- `build_lesson1.py` still writes to the old folder `linear_algebra/`. This is left as is on purpose: the L1 notebook
  is edited by hand, and a rebuild would overwrite those edits.
- `practice/*/build_*.py` write to the current directory, so run them from inside their folder.

---

## 11. Changelog

- **2026-11-17 (ML5 author revision):** Added optional collapsible R² depth using native `details/summary`
  in Markdown; clarified variability, variance, the OLS decomposition and the population noise limit.
  Interpreted residual/group plots and the five worst validation predictions through same-neighborhood train
  analogues, statistics and scatterplots, with a live-kernel ipywidgets selector and static/manual alternatives.
  Revisited reference-category encoding and multicollinearity; added a strong-correlation synthetic bootstrap
  before separating the Ames coefficient and fixed-house prediction figures. Added concrete next-experiment
  suggestions and global warnings suppression at the author's explicit request. The notebook remains
  hand-maintained and awaits review/classroom use. The revised notebook and completed tasks passed execution;
  neighbor calculations, native controls, figures and Chrome rendering were checked (§4). Colab UI remains unverified.

- **2026-11-17:** Recorded ML4's classroom completion, confirmed today without an exact class date.
  Added `LinModels/05_model_diagnostics.ipynb` for review as the fourth applied seminar, maintained directly
  in Markdown/Python without HTML. It reuses the Ames split/preprocessing and unused test, adding R²,
  residual/group diagnostics, coefficient units and prediction contributions, full-pipeline bootstrap
  stability at fixed alpha, and permutation importance on raw validation columns. OLS inference is an
  optional HC3/normal-approximation introduction on separate synthetic data, distinguishing significance
  from importance; `statsmodels` is added as a dependency. Three unanswered code tasks and a final report
  close the main line. Cross-validation follows this seminar. ML1's classroom status is unchanged.

- **2026-11-09:** Recorded successful completion of ML3, confirmed today without an exact class date.
  Added `LinModels/04_regularization.ipynb`, the third applied seminar, for author review: synthetic
  multicollinearity/coefficient-stability examples, Gram and loss geometry, Ridge, scale and a brief geometric
  Lasso comparison. One embedded HTML/JS widget accompanies Markdown/Python. The Ames continuation preserves
  ML3's pipeline, snapshot and split; student tasks choose alpha on validation and keep test unused. No CV,
  spectral-theory or statistical-significance chapter. The notebook is edited directly, without a builder;
  ML1's classroom status is unchanged.

- **2026-11-05 (transformer explainer):** Added the author-approved local HTML/CSS/JS block before ML3 section 2
  on `fit/transform/fit_transform`, fitted attributes, saving a fitted Pipeline and five common transformers.
  Added a short preprocessing/feature-engineering lead-in and ColumnTransformer overview with official sources.
  Diagram labels use sklearn attribute names. The notebook remains hand-maintained, its other sections retain
  Markdown/Python, and classroom use is still pending. The preview HTML is not a runtime dependency.

- **2026-11-05:** Recorded ML2's November 4 classroom completion and added the classroom matrix OLS derivation
  to its notebook: intercept column, MSE gradient, normal equations, full rank and solve/lstsq comparison.
  Added explicit percentage MAPE and zero/near-zero limitations. Created `LinModels/03_data_preprocessing.ipynb`
  for review: same Ames observations/split and unused test, median imputation, scaling, Pipeline, OneHot and
  ColumnTransformer, numeric/mixed-feature OLS comparisons and unanswered tasks. ML1 classroom status remains
  unconfirmed; ML3 has not yet been taught. Both applied seminars remain hand-maintained Markdown/Python.

- **2026-11-03:** Added `LinModels/02_linear_regression.ipynb` as a hand-maintained Markdown/Python seminar
  for review. Preserved the original first seminar's three-panel raw and sqrt/log scatterplot style and a
  short sklearn/algorithm introduction. Uses Ames, a fixed train/validation/test split with test unused,
  training-only exploration, mean baseline, one-/three-feature OLS, coefficient interpretation and MAE/RMSE.
  Student tasks remain unanswered; the original root-level seminars and ML1 format are unchanged.
  The provided code and a temporary completed copy executed locally; figures and rendered formulas were
  inspected. Actual Colab UI remains unverified.

- **2026-11-02:** Restored the author-approved Task 1 heading and introductory instructions; all exercise statements remain verbatim.

- **2026-11-02 (practice review):** Replaced ML1's initial task with the author's five applied formulations and
  three bank/car-sharing/marketplace scenarios, preserving all eight texts verbatim except authorized gross
  typo corrections. No added questions, explanations or source notes. Kept the calculation and workflow
  questions as Tasks 3–4; removed only the recorded-experiment task. No task answers.

- **2026-11-02 (author review):** Revised ML1 chart labels, units and legends, including small task illustrations,
  token probabilities, speaker timing and MSE bars. Standardized introductory target-variable wording and
  clarified that model parameters change during training. Replaced process cards with connected SVG diagrams,
  including explicit branches and feedback loops; `intro_ml_diagrams.py` is used only at build time.
  Recorded the axis-label requirement in the protocol.

- **2026-11-02:** Added `LinModels/01_intro_ml.ipynb` for author review: presentation-like HTML/SVG theory,
  three synthetic widgets, short Python examples, modern application diagrams, precise Russian–English
  terminology and a final glossary. Covers features/targets and dataset notation, training/inference,
  train/validation/test, loss versus evaluation metrics, parameters/hyperparameters and generalization.
  Recorded the already completed hand-maintained calculus and MSE seminars and corrected stale statements
  that derivatives or all regression fitting remain untaught. Documented outstanding MSE-seminar audit issues
  without editing that notebook. ML1 classroom use is pending; L9 status is unchanged.

- **2026-10-16:** Recorded that L12 has been completed in class. Added L13 on sample covariance, Pearson and
  Spearman correlation, covariance/correlation matrices and exact/near multicollinearity. Synthetic apartment
  data, four JS/SVG widgets and ordinary NumPy/pandas/SciPy/seaborn examples connect centered feature vectors
  to matrix calculations. Eight tasks add hand calculations and interpretation, with three extensions for
  class/homework; `lesson13_tasks.py` is build-only. Feature transformations are a brief preview, without model
  fitting. Corrected the map's implication that strong correlation means rank deficiency. The discussed next
  order is OLS/linear regression before eigenvectors/PCA; those new lessons are not built. L13 awaits review
  and classroom use; L9 classroom status is unchanged.

- **2026-10-15:** Recorded that L11 has been completed in class. Added L12 on linear systems, inverse matrices
  and 2D determinant geometry, with three JS/SVG widgets and worked NumPy examples. Adapted six tasks from the
  teacher's temporary `linal_lab.ipynb`, including a first weight calculation from a supplied least-squares
  formula and two optional larger-matrix exercises. Image-based statements and all data are embedded as text
  and arrays; the source notebook and existing course notebooks are preserved. The core theory is one meeting,
  while tasks may continue as homework. Correlation is planned next; regression theory and a complete training
  workflow remain pending. L9 classroom status is unchanged.

- **2026-10-14:** Added L11 on linear dependence/independence, rank and square-matrix singularity defined by
  rank. Four widgets connect linear combinations, redundant columns, plane/line/point geometry and duplicate
  measurement units; worked NumPy examples and three short student tasks use small synthetic data.
  No dataset downloads, determinant/inverse or linear-systems chapters, SVD or model fitting. L10 is unchanged.

- **2026-10-09:** Added L10 on matrices and multiplication as the return to linear algebra after L9.
  Reuses L1–L2 ideas, repeats dot-product and linear-combination definitions, and connects each operation
  to NumPy. Five HTML/JS widgets link tables, vector geometry, multiplication and composition; Xw and
  X @ A.T connect these calculations to row-oriented data. The theory occupies one meeting; added §9 practice
  covers rotation, car prices from given weights, multiple weight sets and a small threshold network's forward
  calculation. The instructor's network diagram is embedded unchanged. Clarified the scalar k control;
  the author's separate exercises remain intact. Basis, rank, covariance and the rest of Phase 2 remain pending.

- **2026-10-08:** Added L9 as the final two-hour statistics lesson on delivery comparisons: precise
  definitions of hypotheses, p-value and significance; false-positive simulation; two-sample bootstrap CI and a
  five-minute practical threshold. Uses the established dark HTML theory cells, three self-contained JS/SVG
  widgets and three small coding tasks. Clarified that the Markdown-only format belongs to practicums, not
  theoretical lessons. Existing notebooks and the author’s edited bus assignment were preserved.

- **2026-10-02:** Created the student bus resampling assignment from the author-approved shortened KEY.
  Preserved all preparation and provided plotting code, replaced only A–D with TODO placeholders, removed saved
  outputs and teacher answers, and added spaces for students' own conclusions. The KEY is unchanged.

- **2026-10-02:** Rewrote the bus resampling KEY for beginners at the author's request. Cut new prose by about 59%,
  removed HTML/JS widgets and the optional season/three-window analysis, retained four short coding tasks and four
  standard figures. Teacher notes now give concrete conclusions. Shared preparation is unchanged.

- **2026-10-02:** Added the post-L8 bus resampling KEY for review: unchanged shared preparation, paired daily
  route differences, sign-flip experiments, one-sample bootstrap, SE and two approximate CIs; two embedded widgets,
  standard Python figures and four essential coding tasks. Student version deferred until author review.

- **2026-10-02:** Moved the bus practicum KEY from `math_for_ds/` to `practice/` unchanged and added the student
  notebook alongside it. Updated paths and the repository layout in README, CLAUDE and AGENT_PROTOCOL;
  resolved the question about keeping a student copy in the repo. Teaching order and prerequisites are unchanged.

- **2026-10-01:** Added L8 on confidence intervals and bootstrap, with nine widgets and eight Python figures.
  Deferred formal tests/p-values to L9 by agreement with the course author. Updated the concept inventory,
  sequence, README and contributor navigation. L7 was not rebuilt.

- **2026-10-01:** Map created. Covers L1–L7, Seminar 1, the vector-algebra homework, three practicums (phones, cars,
  bus) and the `DT/` and `unsupervised/` modules. `build_lesson2–7.py` now write next to themselves (the old
  `linear_algebra/` paths are fixed); the `build_lesson4.py` docstring lists all four parts. Added the external
  house.kg seminar project to the sequence (#6) and `kws-project` to §7; the data's origin (the HF and GitHub
  organizations) to §8.
