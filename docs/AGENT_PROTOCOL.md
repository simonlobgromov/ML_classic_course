# Agent Protocol

**How AI coding agents (and the people supervising them) work in this repository.**

This protocol applies to any agent: Claude Code, Codex, Cursor and the like. Instructions from the course author in
the conversation take precedence over this file. This file takes precedence over an agent's default habits.
What exists and in what order is described in [COURSE_MAP.md](COURSE_MAP.md). Keep both files in sync with reality.

---

## 0. Golden rules

1. **Agree on the plan before building.** For any new lesson, practicum or substantial rewrite: first write down
   your understanding (where it sits in the sequence, its prerequisites, the data, its length, the format). Ask the
   questions that would change the result, and wait for an explicit "ok". Materials built without agreement get
   rejected and redone.
2. **Use only concepts already taught.** Before you use a method in a task, check it against
   [COURSE_MAP §6](COURSE_MAP.md#6-what-students-know-so-far). L9 adds hypotheses, permutation p-values and significance.
   Poisson, t-tests, regression theory, eigenvectors/PCA and a full model-training workflow are still
   **not taught**. L10 uses given weights and a small threshold network's forward calculation only.
   L12 adds a first least-squares weight calculation using a supplied formula, without deriving it or teaching
   the full ML workflow. L11–L12 have been completed in class. L13 introduces covariance, Pearson/Spearman
   correlation and multicollinearity; it awaits review and classroom use. Check that status before using its
   new concepts as prerequisites.
3. **Never regenerate a notebook that is edited by hand** (see §4). In particular, never run `build_lesson1.py`.
4. **Never download heavy data:** the `images` configs of the Lalafo datasets (5–78 GB), the raw `bishkek-transport`
   feed (GBs), the speaker audio (2.65 GB). Use extracts and column subsets.
5. **No ready answers in student materials.** Hints are given in words. Answers go into KEY versions only.
6. **Language:** lesson prose is in Russian; code comments and docstrings are in English; strings students see
   (plot titles, labels, widget text, printed messages) are in Russian.
7. **Do not commit or push unless asked.** Never commit data, `venv/`, caches or executed lesson notebooks.
8. **Update the docs when you finish:** [COURSE_MAP.md](COURSE_MAP.md) (§3, §4, §5, §6, §11), and `README.md` if the
   layout changed.

---

## 1. Orient yourself first

Read in this order:

1. `CLAUDE.md`: the repo map and commands.
2. [COURSE_MAP.md](COURSE_MAP.md): §3 (sequence), §6 (what students know), §10 (open questions).
3. **The newest build script** (`math_for_ds/build_lesson13.py`), together with `build_lesson12.py`: the shared
   dark HTML theory cells and self-contained JS/SVG widgets used by theoretical lessons.
   L13's task definitions live in the build-only `lesson13_tasks.py` module.
4. The lesson before the one you are working on: its last sections usually set up the next topic ("bridges").
5. `syllabus.docx`, as a compass for intent. It is not a contract. To read it without extra packages:

   ```bash
   unzip -p syllabus.docx word/document.xml | python3 -c "import re,sys; x=sys.stdin.read(); [print(t) for t in (''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>', p)) for p in re.findall(r'<w:p[ >].*?</w:p>', x, re.S)) if t.strip()]"
   ```

---

## 2. Workflows

### 2.1 A new lesson (`math_for_ds/`)

1. **Brief, for agreement:** the topic and its number in the sequence; prerequisites, from COURSE_MAP §6; what is
   new; the dataset; one meeting or two; the bridge into the next topic; which syllabus week it serves or why it
   departs from the syllabus.
2. **Outline, for agreement:** the sections, every widget (what the student moves and what they should see), the
   tasks and the interpretation questions.
3. **Implement** `math_for_ds/build_lessonN.py`, following the HTML/JS theoretical-lesson pattern in
   `build_lesson8.py` through `build_lesson13.py` (§5). A practicum’s Markdown-only format does not apply to theory lessons.
4. **Build:** `venv/bin/python math_for_ds/build_lessonN.py`. It writes `math_for_ds/NN_<slug>.ipynb`.
5. **Validate** with the checklist in §7.
6. **Document** in COURSE_MAP: a row in §3, a note in §4, an update to §5, the new concepts in §6, a line in §11.

### 2.2 A new practicum

**Lalafo pattern** (one folder per dataset under `practice/<topic>/`):

1. **Study the dataset first.** Download only the small parquets (`listings`, `users`, `cities`), using the
   datasets-server URL `https://huggingface.co/datasets/aiacademy-kg/lalafo-kg-<topic>/resolve/refs%2Fconvert%2Fparquet/<config>/train/0000.parquet`.
   **Never download `images`.** Write `recon.py` (nulls, distributions, signal via medians only) and a teacher-facing
   `RECON.md`. The datasets-server `/statistics` endpoint tends to fail on these datasets, so compute statistics
   yourself.
2. **Build** `build_<topic>.py` → `<topic>_practice.ipynb`. **Markdown and code only, no HTML.** Cell order:
   introduction and rules → setup → loading (`load_dataset(REPO, "listings")`, `"users"`) → rough feature engineering
   done in advance (parse string columns to numbers, convert currency to KGS at USD × ≈89, **leave outliers and
   garbage in**) → a data dictionary with known traps → a warm-up → five cases T1–T5 → a guide for the defence.
3. **Each case:** a layperson-vs-researcher twist and "recommended math, tied to necessity". Across the five, cover
   all the taught topics.
4. **Before shipping:** execute the feature-engineering cell on the local parquet and confirm that **each case has a
   real signal** (in medians, not correlation). Known traps: a feature present only in a subgroup; IQR degenerating
   on counts (use a high percentile instead); mixed currencies.
5. Run the build script from inside its folder: it writes to the current directory.

**Research pattern** (bus practicum): one real question; a Part 0 pipeline prepared in advance and explained step by
step; tasks with «Ваш вывод» cells; memos. **Pin the dataset revision** and ship a small prepared extract with a
fallback rebuild from the raw data. Keep a KEY version with «Для преподавателя» notes and a student version without
them. The bus notebooks are maintained by hand in `practice/`: `practicum_mossovet_asia_mall.ipynb`
(student tasks) and `practicum_mossovet_asia_mall_KEY.ipynb` (answers and saved outputs).
The follow-up after L8 has two versions: `practicum_mossovet_asia_mall_bootstrap.ipynb` (student tasks) and
`practicum_mossovet_asia_mall_bootstrap_KEY.ipynb` (teacher answers, approved by the author).
Dependencies and the entire Part 0 are copied from the original KEY: cell sources and metadata are identical
in both versions; the KEY retains saved outputs, while the student version clears outputs and execution counts.
Keep that shared preparation intact; student coding begins in the new tasks, in the four short cells tagged
`student-core`. These contain TODO placeholders in the assignment and solutions in the KEY.
Grouping and plotting are provided code. The follow-up uses **Markdown and Python only**:
no custom HTML, CSS, JavaScript or widgets. Keep it short, introduce each method through a concrete action,
and put actual numerical conclusions in the teacher notes rather than lengthy methodological instructions.
Both versions are maintained by hand. Student interpretation cells ask for conclusions without supplying answers.

### 2.3 Editing existing material

1. Find the source of truth in §4. If the material is built by a script, edit the script.
2. **Rebuild safely:** build into a scratch copy, compare cell sources with the committed notebook, and only then
   replace it. Scripts 2–13 write next to themselves, so copy the folder and run the copy:

   ```bash
   cp -R math_for_ds /tmp/mfd && rm /tmp/mfd/*.ipynb && venv/bin/python /tmp/mfd/build_lesson5.py
   # then diff the cell sources of /tmp/mfd/05_stat_normal.ipynb and math_for_ds/05_stat_normal.ipynb
   ```

   Differences in cell ids alone are harmless; lessons 2–5 get fresh random ids on each build.
3. When the change touches what students learn, update COURSE_MAP §4 and §6.

### 2.4 Documentation-only changes

Keep `CLAUDE.md` short: navigation and rules only. Course content belongs in COURSE_MAP, process belongs here. When
you find an inconsistency, record it in COURSE_MAP §10. Do not fix it silently in course content.

---

## 3. Who decides what

| Decision | Who |
|---|---|
| Topic order, scope of a lesson, adding or dropping a topic | Course author (agree first) |
| The dataset for a lesson or practicum | Course author (propose options and check the signal first) |
| Wording of definitions, tone | Follow COURSE_MAP §9.2. Flag doubts; do not improvise new conventions |
| Widget mechanics, code structure, validation | Agent, following §5 |
| Anything listed under "Decisions needed" in COURSE_MAP §10 | Course author |

---

## 4. Source of truth and rebuild rules

| Material | Edit here | Rebuild with the script? |
|---|---|---|
| L1 `01_vectors.ipynb` | **The notebook, by hand** | **Never.** `build_lesson1.py` is historical; its output path `linear_algebra/` is stale on purpose |
| L2 `02_dot_product.ipynb` | `build_lesson2.py` | Yes. The rebuild also refreshes SETUP from the current `theme.py` |
| L3 `03_stat_intro.ipynb` | `build_lesson3.py` | Yes. The content matches the script |
| L4 `04_stat_boxplot.ipynb` | `build_lesson4.py` | **Ask first.** The notebook has 17 in-class cells (20–36) that the script does not have |
| L5 `05_stat_normal.ipynb` | `build_lesson5.py` (+ `images/`) | Yes |
| L6 `06_stat_distribution.ipynb` | `build_lesson6.py` + `lesson6_widgets.js` | Yes. Byte-identical rebuilds |
| L7 `07_stat_sampling_clt.ipynb` | `build_lesson7.py` + `lesson7_widgets.js` | Yes. Byte-identical rebuilds |
| L8 `08_stat_ci_bootstrap.ipynb` | `build_lesson8.py` + `lesson8_widgets.js` | Yes. Byte-identical rebuilds |
| L9 `09_stat_hypotheses.ipynb` | `build_lesson9.py` + `lesson9_widgets.js` + `lesson9_helpers.py` | Yes. JS widgets and Python helpers are embedded; preserve unexecuted output |
| L10 `10_matrices.ipynb` | `build_lesson10.py` + `lesson10_widgets.js` + `images/lesson10_threshold_network.png` | Yes. JS widgets, Davis extract and image attachment are embedded; preserve unexecuted output |
| L11 `11_linear_dependence_rank.ipynb` | `build_lesson11.py` + `lesson11_widgets.js` | Yes. JS widgets and synthetic data are embedded; preserve unexecuted output |
| L12 `12_linear_systems_inverse.ipynb` | `build_lesson12.py` + `lesson12_widgets.js` | Yes. JS widgets, transcribed exercises and seeded synthetic data are embedded; no dependency on the temporary source notebook |
| L13 `13_covariance_correlation.ipynb` | `build_lesson13.py` + `lesson13_widgets.js` + `lesson13_tasks.py` + shared `theme.py` | Yes. Task definitions are build-only; widgets, data and task cells are embedded in the standalone unexecuted notebook |
| `seminar_1.ipynb` | The notebook | No script |
| `practice/practicum_mossovet_asia_mall.ipynb` | The notebook (student tasks, without answers or outputs) | No script |
| `practice/practicum_mossovet_asia_mall_KEY.ipynb` | The notebook (KEY, with outputs) | No script |
| `practice/practicum_mossovet_asia_mall_bootstrap.ipynb` | The notebook (student tasks; preserve copied Part 0, clear outputs) | No script |
| `practice/practicum_mossovet_asia_mall_bootstrap_KEY.ipynb` | The notebook (teacher answers and outputs; preserve copied Part 0) | No script |
| `practice/<topic>/<topic>_practice.ipynb` | `practice/<topic>/build_<topic>.py` | Yes, run from inside the folder |
| `DT/*.ipynb`, `unsupervised/*.ipynb` | The notebooks | No scripts |
| `DT/theory/*.html` | The HTML files (shared `assets/style.css`, `assets/common.js`) | — |
| `math_for_ds/theory/` | Legacy prototype. Do not extend it | — |

---

## 5. Lesson implementation spec

**Theoretical lessons use the shared HTML/JS format below, including L9–L13.** The Markdown/Python-only rule
for practicums applies to those practicums. Keep the author’s process instructions out of student prose: title
definition boxes with the mathematical concept, and state the definition itself.

**L9 scope.** One two-hour meeting (110 minutes of work plus a break), three JS/SVG widgets and three short
`student-core` tasks. Embed `lesson9_widgets.js` and `lesson9_helpers.py` into the setup cell so students need
only the notebook. Python examples and ordinary plots accompany the interactive theory. Validate the ready
code and a temporary completed copy.

**L10 scope.** One beginner two-hour theory meeting, returning to L1–L2: matrix operations, multiplication and
its geometric meaning. Five self-contained JS/SVG widgets accompany worked NumPy examples. Repeat the definitions
of the dot product and linear combination before using them. Explicitly distinguish `*`, `@`, `np.dot` and
`np.matmul`, and column-vector formulas from observations stored in rows. The six-row Davis extract is embedded;
no runtime data download is needed. Section 9 adds four short student tasks for class or homework: rotation,
car-price calculations with given weights, multiple weight sets as matrix columns, and the forward calculation
of a three-input/two-hidden-unit/one-output threshold network. Introduce weight, weighted sum, threshold
activation and hidden layer before the network task. Preserve the instructor's diagram bytes in
`images/lesson10_threshold_network.png`, embedded as a Markdown attachment. Task cells have unanswered TODOs;
guarded plotting and result tables are provided. No KEY was requested. Existing separate exercises remain intact.
All three neurons use the author-confirmed rule: output 1 when the weighted sum is at least 0.5, otherwise 0;
there are no bias terms. Include the boundary value in the student check.
Do not assume all the added practice fits the theory meeting. The standard 2D basis is briefly defined to
explain matrix columns. General basis theory, rank, determinants, inverses and model training are outside this lesson.

**L11 scope.** Continue L10 with linear dependence/independence, rank and singularity of a square matrix
defined through rank. Use small synthetic examples without data downloads: two-vector combinations,
morning/evening/total columns, a plane mapped to a plane/line/point, and volume in litres/millilitres as
duplicate features with nonunique given weights. Four self-contained JS/SVG widgets, NumPy examples,
standard Python figures and three short student tasks. Keep tasks unanswered; validate a temporary completed
copy. Briefly define span, state row/column rank equality and full rank for rectangular as well as square
matrices; keep the numerical-tolerance caveat optional. Do not add chapters on determinants, inverses,
linear systems, general basis theory, SVD or model fitting.

**L12 scope.** Continue the completed L11 with linear systems, matrix equations, inverse matrices and a short
2D geometric introduction to the determinant. Three self-contained widgets show one/no/infinitely many solutions,
a transformation followed by its inverse, and area scaling/orientation. Teach the mathematical expression
`x = A⁻¹b`, then use `np.linalg.solve(A, b)` as the practical method for a nonsingular square system; explicitly
define the inverse and its existence condition. Include only the 2×2 hand formula for the determinant.
No minors, Cramer's rule, LU decomposition, cross products, MNIST or Gradio. The core theory fits one two-hour
meeting; do not promise that all exercises fit it. Keep six adapted student tasks unanswered, with the last two
optional: 2×2 determinant/inverse (source task 5), `2AX − B = C` (12), a 4×4 system (15), a supplied least-squares
weight formula on seeded 10×7 synthetic data (14), `SXQ = B` with 5×5 matrices (13), and a 5×5 system (16).
The teacher supplied these in the temporary `linal_lab.ipynb`. Transcribe the two image-based statements into
LaTeX and NumPy, and embed all required data: neither building nor running L12 may read that temporary file.
Preserve the source notebook and existing course notebooks. The weight task introduces calculation by a given
formula, its full-column-rank condition and prediction; do not silently extend it into a least-squares derivation
or a complete ML training/evaluation lesson. Validate the ready cells and a temporary completed task copy.
Correlation follows in L13; it is not a prerequisite for L12.

**L13 scope.** Continue the completed L12 with sample covariance, standard deviation and Pearson correlation
using synthetic apartment area, room count and price. Define centered feature vectors and explain Pearson
as their cosine; distinguish these vectors across observations from individual observation vectors.
Introduce covariance/correlation matrices, a brief rank-based Spearman comparison, and exact versus near
multicollinearity. Pairwise correlation can miss dependence involving several columns; high correlation does
not by itself imply rank deficiency. Discuss nonlinear and monotonic relationships with scatterplots, then
show `x²`, `x³` and `sin(x)` as a short feature-transformation preview. No mutual information, eigenvalues/PCA
or regression fitting. Use four standalone JS/SVG widgets and visible NumPy, pandas, SciPy and seaborn examples.
Use sample normalization consistently (`n − 1`, `ddof=1`), explain units and constant-feature cases, and do not
introduce correlation significance tests through SciPy's returned p-values. Eight student tasks include the
author-requested hand calculations: five core tasks and three extensions for class/homework. The theory is
one meeting; do not promise that all practice fits two hours. `lesson13_tasks.py` supplies task cells at build
time only. Embed them so students need only the notebook. Keep task answers blank and validate a temporary
completed copy. The agreed next direction is OLS/linear regression, then eigenvectors/PCA; those lessons are
not built by this change. The author has already approved L13's structure and extended practice in conversation.

**Skeleton** (copy it from `build_lesson8.py`):

```python
import nbformat as nbf
from theme import SETUP, META          # works because Python puts the script's folder on sys.path

def md(source):   cells.append(nbf.v4.new_markdown_cell(source.strip()))
def code(source): cells.append(nbf.v4.new_code_cell(source.strip()))
def eq(formula, meanings): ...          # raises if the symbol glossary is empty
# ... cells ...
nb = nbf.v4.new_notebook(cells=cells, metadata=json.loads(json.dumps(META)))
nb.metadata["colab"]["name"] = "NN_slug.ipynb"
for i, cell in enumerate(nb.cells):     # deterministic ids give reproducible diffs
    cell.id = hashlib.sha256(f"lessonN-{i}-{cell.source}".encode()).hexdigest()[:12]
nbf.validate(nb)
nbf.write(nb, HERE / "NN_slug.ipynb")   # always next to the script, never relative to the CWD
```

**Cell order.** A Markdown title (the question of the lesson, how to work, one meeting or two) → **one** SETUP code
cell. In L6+ this cell is `theme.SETUP`, followed by the embedded `lessonN_widgets.js` source and the lesson's
`EXTRA_SETUP`, which defines `lessonN_viz()` and the lesson CSS:
`code(SETUP + '\n\nD8_WIDGET_JS = ' + repr(WIDGET_JS) + '\n' + EXTRA_SETUP)`. Then come sections that alternate
theory cells, widgets, short numpy experiments and tasks → a check of understanding → sources.

**The theme (`theme.py`).**

- `SETUP` defines `viz(body, script="", wide=False)`. It wraps HTML in the dark `.vec-root` block, with CSS, JS
  helpers and MathJax inline, so every output is self-contained.
- CSS classes: `.box.def` (definition), `.box.idea`, `.box.warn`, `.box.take` (takeaway), `.where` (symbol glossary),
  `.en` (English gloss), `.widget` / `.widget-title` / `.widget-sub`, `.controls`, `.readout`, `<details>`/`<summary>`.
- JS helpers: `el`, `arrow`, `onDrag`, `handle`, `freshFrame`, `drawFrame`, `label`, `scale`, `clamp`, and
  `plane(half)` for a square plane (equal pixels per unit), which honest angles and circles need.
- `META`: the Colab notebook metadata shared by every lesson.

**Theory cells.** Each is a `#@title <Russian title> { display-mode: "form" }` code cell that displays HTML, so it
appears collapsed in Colab. Use `$…$` and `$$…$$` only. Every displayed formula is followed by a «Где: …» /
«Обозначения.» glossary. Depth goes into `<details>`.

**Widgets (L6–L13 pattern).** A Python `widget(kind, title, instruction, charts, controls, question, optional=False)`
emits a cell with a fixed anatomy: title → instruction → controls (`slider`, `select`) → SVG charts → a live
`readout` (`aria-live`) → a «Проверь себя» question → a footnote identifying the data or simulation. The JS renderer lives in
`lessonN_widgets.js` (`window.<Name>.mount(root, kind)`) and is embedded at build time. Students need only the
`.ipynb`. Every widget must render without a Python kernel, and the charts must work offline (MathJax is the only
network dependency).

**Student code cells.** Short, runnable numpy/pandas experiments. Task cells contain `# TODO:` hints written in words.
Never put the finished line of code in a student cell.

---

## 6. Data rules

- Datasets live on Hugging Face under `aiacademy-kg/*` (the registry is in COURSE_MAP §8). Prefer
  `hf_hub_download` of a specific file, or `load_dataset(repo, config)` with an explicit small config.
- For datasets that keep changing, **pin a revision** (as the bus practicum does with `REVISION = '4aa20aab…'`).
- Local copies go into a `data/` folder, which is gitignored. Caches (`*.npz`, for example `speaker_emb.npz`) are
  gitignored too.
- Lesson notebooks load data at runtime in Colab. Do not embed large data. Small derived summaries may be embedded
  (L7 embeds rounded bus statistics).
- Synthetic data are welcome where a known law makes results checkable (L6–L9). Say clearly in the text that the
  data are synthetic.

---

## 7. Validation checklist (before handover)

**Build and structure**
- [ ] The build script runs from any working directory and writes next to itself; `nbformat.validate` passes.
- [ ] The lesson notebook is committed **un-executed** (KEY versions excepted).
- [ ] The rebuild diff against the previous version shows only the intended changes.

**Rendering**
- [ ] HTML outputs are self-contained; widgets mount; sliders and drags update the readout. At minimum, open the
      generated HTML in a browser. If you could not check it in Colab, say so.
- [ ] Execute the ready Python cells and a temporary completed copy of student tasks; inspect the ordinary
      plot outputs. Distinguish local/browser checks from actual Colab UI validation.
- [ ] MathJax uses `$` / `$$` only. Each formula has its glossary. No raw `<`, `>` or `&` break the HTML.
- [ ] Angles and circles are drawn on a square plane.

**Content**
- [ ] Only taught concepts are used (COURSE_MAP §6), or the new ones are introduced in this very lesson.
- [ ] No ready answers in student cells; hints are in words.
- [ ] At least one interpretation question that cannot be answered by pasting an LLM's output.
- [ ] Tone: academic Russian prose, no conversational metaphors or GPT jargon, properties as lists.
- [ ] Language: prose and UI in Russian; comments and docstrings in English.

**Data**
- [ ] Data cells run; downloads are small; no `images` or raw feeds.
- [ ] For practicums: every case shows a real signal on the actual data.

**Docs**
- [ ] COURSE_MAP updated (§3, §4, §5, §6, §11); README if the layout changed.

---

## 8. Handover report

End every task with a short report to the course author:

- **What changed:** files created or modified, and which notebooks were rebuilt.
- **What was verified and how:** the build ran, the diff, rendering checked in a browser or in Colab, data cells run.
- **What was not verified**, stated plainly (for example "the widgets were not opened in Colab").
- **Open questions** you found, also added to COURSE_MAP §10.

Commit style, when asked to commit: short lowercase subjects as in the history (`hierarh`, `bagging`,
`clustering -> dbscan`); one topic per commit.
