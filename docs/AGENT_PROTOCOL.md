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
   [COURSE_MAP §6](COURSE_MAP.md#6-what-students-know-so-far). As of L8, correlation, covariance, Poisson,
   tests and p-values, regression and every ML model are **not taught**.
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
3. **The newest build script** (`math_for_ds/build_lesson8.py`): this is the current pattern to copy.
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
3. **Implement** `math_for_ds/build_lessonN.py`, starting from `build_lesson8.py` (§5).
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

### 2.3 Editing existing material

1. Find the source of truth in §4. If the material is built by a script, edit the script.
2. **Rebuild safely:** build into a scratch copy, compare cell sources with the committed notebook, and only then
   replace it. Scripts 2–8 write next to themselves, so copy the folder and run the copy:

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
| `seminar_1.ipynb` | The notebook | No script |
| `practice/practicum_mossovet_asia_mall.ipynb` | The notebook (student tasks, without answers or outputs) | No script |
| `practice/practicum_mossovet_asia_mall_KEY.ipynb` | The notebook (KEY, with outputs) | No script |
| `practice/<topic>/<topic>_practice.ipynb` | `practice/<topic>/build_<topic>.py` | Yes, run from inside the folder |
| `DT/*.ipynb`, `unsupervised/*.ipynb` | The notebooks | No scripts |
| `DT/theory/*.html` | The HTML files (shared `assets/style.css`, `assets/common.js`) | — |
| `math_for_ds/theory/` | Legacy prototype. Do not extend it | — |

---

## 5. Lesson implementation spec

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

**Widgets (L6–L8 pattern).** A Python `widget(kind, title, instruction, charts, controls, question, optional=False)`
emits a cell with a fixed anatomy: title → instruction → controls (`slider`, `select`) → SVG charts → a live
`readout` (`aria-live`) → a «Проверь себя» question → a footnote saying it is a simulation. The JS renderer lives in
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
- Synthetic data are welcome where a known law makes results checkable (L6, L7, L8). Say clearly in the text that the
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
