# Course Map

**What has been built, where it lives, in what order it is taught, and why it looks the way it does.**

> **This document is kept up to date as the course grows.** Last updated: **2026-10-01**, after Lesson 8.
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
7. [Classic-ML modules (Phase 4)](#7-classic-ml-modules-phase-4)
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

| Phase | Weeks | Theme (syllabus) | Status (2026-10-01) |
|---|---|---|---|
| **1. Data as vectors** | 1–4 | Descriptive statistics, distributions; vector, norm, dot product; rank; covariance | **In progress.** L1–L8 built. The statistics track is ahead of the plan; the linear-algebra track has stopped after week 1. |
| **2. Matrices as operators** | 5–8 | Operators, determinant and inverse, eigenvectors, PCA (+ SVD overview) | Not started. `unsupervised/01` already covers SVD/PCA as an ML lesson. |
| **3. Estimation and first models** | 9–12 | Projections and least squares, linear regression, MLE, logistic regression | Not started. L7–L8 bring sampling and estimation forward; tests are planned for L9. |
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
| 11 | P | **Bus practicum "Моссовет → Азия Молл"** · `math_for_ds/practicum_mossovet_asia_mall_KEY.ipynb` | real GPS feed; trips via vectors and dot product; ECDF, normal model vs. data, waiting-time paradox, Monte Carlo | L1–L6 | integrative | Sep 28 |
| 12 | L | **L7 — Sampling, standard error, CLT** · `math_for_ds/07_stat_sampling_clt.ipynb` | sampling distribution, SE, LLN, CLT, difference of two means; reuses the bus data | L6, bus practicum | beyond plan (prepares W12) | Sep 30 |
| 13 | L | **L8 — Confidence intervals and bootstrap** · `math_for_ds/08_stat_ci_bootstrap.ipynb` | known-σ intervals, coverage, bootstrap SE and percentile intervals, resampling schemes | L7 | estimation brought forward | Oct 1 |
| 14 | L | **L9 — Statistical tests and significance** | bridge from L8 §9; tests and p-values remain untaught | L7–L8 | W12 brought forward | *not built* |
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
  and is formalised in L5–L6. **S4 Task 8 asks for a correlation coefficient**, although correlation is officially
  not taught yet (§10).
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

- **File.** `math_for_ds/practicum_mossovet_asia_mall_KEY.ipynb`, the **teacher's KEY version**: saved outputs and
  a «Для преподавателя» note after every task. There is no build script, and the student copy is not in the repo.
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
  confidence intervals and bootstrap; formal tests are now planned for L9. The original L7 bridge is unchanged.


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

## 5. Syllabus vs. what was built

| Syllabus | Planned | Built | Comment |
|---|---|---|---|
| W1 | Random variable, mean, variance, SD; vector, norm, dot product; z | L1, L2, L3, Seminar 1, H, house.kg seminar project | **Done.** The random variable is kept intuitive and formalised in L5–L6. |
| W2 | Normal, three sigma, Bernoulli, binomial; LA: linear combinations | L5, L6 | Statistics done and extended (PDF/CDF in L6). Linear combinations were only introduced in L1, not developed. |
| W3 | Poisson; basis, rank, multicollinearity | — | **Not built.** |
| W4 | Covariance, correlation, covariance matrix; milestone presentation 1 | — | **Not built.** Students still do not know correlation, which constrains every practice task. |
| — | *(not in the syllabus)* | L4 | Robust, non-parametric tools, needed because the real data are dirty. |
| — | *(not in the syllabus)* | Bus practicum, L7–L8, planned L9 | Sampling, SE, CLT, confidence intervals and bootstrap; tests next. The syllabus only says tests "return" in W12; we prepare them earlier. |
| W8 | PCA, SVD overview | `unsupervised/01` | Exists as an ML lesson, without the covariance and eigenvector groundwork the syllabus intends. |
| W13 | Trees, ensembles, metrics, cross-validation | `DT/` | Exists. It predates the math block. Metrics and cross-validation have no dedicated lesson. |

**The overall pattern:** the statistics track is ahead of the plan, and the linear-algebra track stopped after
week 1. The main debt to the syllabus is resuming linear algebra (linear combinations → basis and rank →
covariance), which is the road into Phase 2.

---

## 6. What students know so far

*As of L8.* Practice tasks must stay inside this list. Anything outside it has to be taught first.

**Linear algebra.** Vector as an observation; feature space ℝⁿ; addition, scaling, linear combination (introduced
only); L2 norm, distance; centroid as the mean vector; dot product, projection, angle; cosine similarity and
distance; L2 normalization; nearest neighbour by Euclidean vs. cosine distance; embeddings and attention (as ideas).

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

**Tools.** numpy, pandas (`describe`, `groupby`, `quantile`), seaborn (histograms, KDE, boxplots),
`scipy.stats.norm` (`cdf`, `sf`, `ppf`), `scipy.stats.bootstrap`, NumPy resampling (`Generator.choice`), sklearn scalers and `NearestNeighbors`.

**Not taught yet. Do not use without teaching it first:** correlation (Pearson r, `df.corr()`) and covariance; the
covariance matrix; Poisson; hypothesis tests, p-values; matrices as operators, rank,
determinant, inverse, eigenvectors; PCA/SVD; least squares and linear regression; MLE; logistic regression; any ML
model, train/test split, metrics.

---

## 7. Classic-ML modules (Phase 4)

Both modules were built in **June 2026, before the math block**, as standalone ML lessons. In the syllabus they become
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
come in Phase 3, and metrics and cross-validation in W13. Gradient descent is not in the syllabus at all. The
handbook's chapter 1 partly fills the gap: probability, expectation, logarithm, derivative and gradient, convexity,
Jensen.

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
| Davis (height and weight, 200 people) | HF `aiacademy-kg/davis_dataset` | L1–L5 | Measured and self-reported values; small enough to compute by hand |
| house.kg listings (Bishkek) | HF `aiacademy-kg/house_kg_full_dataset`, file `data/listings.parquet` | house.kg seminar project, L4, L5 | Filter `deal == "sale"`, `type == "apartment"`, `city == "Бишкек"`; `price_usd` is strongly skewed |
| Lalafo phones | HF `aiacademy-kg/lalafo-kg-phones` | `practice/phones` | Load `listings` and `users`; never `images` (~5 GB) |
| Lalafo cars | HF `aiacademy-kg/lalafo-kg-cars` | `practice/cars` | Never `images` (78 GB); ≈40% of prices are in USD |
| Bishkek public-transport feed | HF `aiacademy-kg/bishkek-transport` (pinned revision) | Bus practicum; L7 (embedded summaries) | 372 M rows; use the 21 MB practicum extract |
| Speaker audio + WavLM embeddings | HF `aiacademy-kg/audio-3-speaker-dataset-v2` / `aiacademy-kg/audio-3-speaker-dataset` | Seminar 1 / `unsupervised/` | Load only the embedding columns where possible |
| Iris; Rice (zip on Dropbox) | seaborn; Dropbox link in the notebook | `dt_demo` | |
| Telecom churn | CSV from the mlcourse.ai GitHub repo | `bagging_rf` | |
| sklearn toy sets, 20 Newsgroups | sklearn | `DT/`, `unsupervised/` | |
| Keyword-spotting audio features | HF `aiacademy-kg/kws-dataset` | `kws-project` (external) | Features already extracted |
| Synthetic data | generated in the notebook | L6, L7, L8, `bias_variance_demo`, `gradient_boosting` | The law is known, so every result can be checked |

**Where the data come from.** All `aiacademy-kg/*` datasets are published on the school's Hugging Face organization,
[huggingface.co/aiacademy-kg](https://huggingface.co/aiacademy-kg). The scrapers that build the house.kg and Lalafo
datasets live in the school's GitHub organization,
[ai-academy-bish](https://github.com/orgs/ai-academy-bish/repositories) (`house_kg_parser`, `lalafo_parser`). Their
docs describe every field and the known pitfalls, so read them before designing a task on these data.

**Anchor datasets.** The syllabus asks that the group's anchor datasets together cover: a nearly normal feature, a
count of events (for Poisson), strongly correlated features (rank < number of columns), structure for PCA, and a
binary target. The list of students' anchor datasets is not recorded in the repo.

---

## 9. Methodological conventions

### 9.1 Teaching

- **Experience first, then the name, then the formula.** L5–L8 use this "genetic" order explicitly: an experiment or
  widget → «что мы увидели» → a precise definition.
- **Predict, act, explain.** Before moving a slider, the student predicts the result; afterwards, they explain it in
  words.
- **A «Где: …» block under every displayed formula**, explaining every symbol (CSS class `.where`; in L6–L8 enforced
  by the `eq()` helper).
- **Optional depth** goes into `<details>` blocks («для тех, кто хочет глубже»), so the main line stays short.
- **English terminology is introduced gradually:** an English gloss next to the Russian term (class `.en`).
- **By hand in numpy first, then the library.**
- **Interpretation over derivation.** Each assignment includes at least one question from the syllabus's
  interpretation bank, or one written in its spirit. Such a question cannot be answered by pasting an LLM's output:
  it requires linking a mathematical fact to *these* data.
- **No ready answers in student materials.** TODO hints are given in words, never as the finished line of code.
  Teacher answers live in KEY versions («Для преподавателя»).
- **Only concepts already taught** (§6). The usual temptation is correlation: express "a relationship between X and
  Y" with group medians, a scatter or 2D KDE, and centroids instead.
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

### 9.3 Lesson format (`math_for_ds/`)

- Google Colab `.ipynb`, **committed un-executed**, generated by `build_lessonN.py` with nbformat. Change the script,
  not the notebook, except for the hand-maintained files (see AGENT_PROTOCOL §4).
- The first code cell is **SETUP** from `theme.py`: dark-theme CSS, SVG/JS helpers and `viz(body, script, wide)`.
- Theory is HTML in collapsed `#@title … { display-mode: "form" }` cells. **Each output is self-contained** (CSS +
  JS + MathJax inline), because Colab isolates cell outputs.
- Theory visualisations are **live JS/SVG** (draggable points, sliders), not matplotlib. Matplotlib/seaborn appear in
  the code students write. Angles and circles need the square plane `plane(half)`.
- MathJax with `$…$` and `$$…$$` delimiters only.
- Current pattern (L6–L8): widgets in `lessonN_widgets.js` embedded at build time; deterministic cell ids; the `eq()`
  glossary guard; references to authoritative sources (NIST, SciPy, Penn State, OpenStax).

### 9.4 Practicum format

- **Lalafo pattern:** study the dataset first (`recon.py` → teacher-facing `RECON.md`), then `build_<topic>.py`,
  Markdown only, feature engineering done in advance, five cases. Before shipping, run the feature-engineering cell on
  the local parquet and confirm that each case has a real signal (in medians).
- **Bus pattern:** one research question; Part 0 is a pipeline built in advance and explained step by step; tasks
  have a «Ваш вывод» cell and a teacher note; two memos; a pinned data revision and a small prepared extract.

---

## 10. Open questions and next steps

**Next to build**

1. **L9: statistical tests and significance**, prepared by L7 and the new L8. CI and bootstrap come first,
   following the author’s agreed sequence; t-tests and p-values are not part of L8.
2. **Resume the linear-algebra track:** linear combinations → basis, rank, multicollinearity (W3) →
   covariance and correlation, covariance matrix (W4). This is the road into Phase 2.
3. **Poisson** (W3; foreshadowed in L5).
4. **Milestone presentation 1** (W4): not designed yet.

**Decisions needed**

- **L3, S4 Task 8** asks for a correlation coefficient before correlation is taught. Reword it, or treat it as a
  deliberate spoiler?
- **Language of task statements:** English (L2) or Russian (L3 onwards) from now on?
- **Bus practicum:** only the KEY version is in the repo and it has no build script. Should the student copy live here
  too, or a script that strips the teacher notes and outputs?
- **`04_stat_boxplot.ipynb`:** keep the 17 in-class cells in the canonical version, or move them to the build script
  or to a separate class log? A rebuild currently drops them.
- **`vektornaya-algebra-hw`:** credit the source textbook.
- **`math_for_ds/theory/`** (Aug 24, L1 only; L2 marked «готовится») has been replaced by the Colab format. Archive or
  delete it?
- **`DT/*.pdf`** are third-party (HSE). Check redistribution rights before the repo is made public.

**Technical debt**

- L7 §7 still announces tests for “the next lesson”. The author-approved sequence now inserts L8 (CI/bootstrap)
  before tests in L9. L8 explains the detour; update that historical bridge when L7 is next revised.

- `build_lesson1.py` still writes to the old folder `linear_algebra/`. This is left as is on purpose: the L1 notebook
  is edited by hand, and a rebuild would overwrite those edits.
- `practice/*/build_*.py` write to the current directory, so run them from inside their folder.

---

## 11. Changelog

- **2026-10-01:** Added L8 on confidence intervals and bootstrap, with nine widgets and eight Python figures.
  Deferred formal tests/p-values to L9 by agreement with the course author. Updated the concept inventory,
  sequence, README and contributor navigation. L7 was not rebuilt.

- **2026-10-01:** Map created. Covers L1–L7, Seminar 1, the vector-algebra homework, three practicums (phones, cars,
  bus) and the `DT/` and `unsupervised/` modules. `build_lesson2–7.py` now write next to themselves (the old
  `linear_algebra/` paths are fixed); the `build_lesson4.py` docstring lists all four parts. Added the external
  house.kg seminar project to the sequence (#6) and `kws-project` to §7; the data's origin (the HF and GitHub
  organizations) to §8.
