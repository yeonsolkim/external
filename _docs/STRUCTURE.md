# Document structure — the contract

How a post's Markdown becomes structured HTML, and what every consumer (CSS, `main.js`,
`_narrator/`) may rely on. **This file is the contract**: the Jekyll plugin
`_plugins/document_structure.rb` produces it, everything else reads it.

The model mirrors a LaTeX document. Sectioning commands nest; theorem-like environments
are numbered units inside a section; a proof is a *sibling* of the statement it proves,
as `\begin{proof}` is in LaTeX, and carries a pointer back to it.

## 1. Mapping

| LaTeX | Markdown you write | HTML |
|---|---|---|
| `\section{T}` | `## T` | `<section class="doc-section" data-doc="section">` + `<h2>` |
| `\subsection{T}` | `### T` | `<section class="doc-section" data-doc="subsection">` + `<h3>` |
| `\subsection{T}` (run-in, numbered) | `**3. T.**` | `<section class="doc-section" data-doc="subsection" data-number="3">`, label `role="heading"` |
| `\subsubsection{T}` | `**3.1. T.**` | same, nested under `3.` |
| `\begin{theorem}` … | `**Theorem 1.3.3.** …` | `<section class="math-environment math-environment--theorem" data-doc="theorem">` |
| `\begin{proof}` … `\qed` | `*Proof.* … $\square$` | `<section class="math-environment math-environment--proof" data-proves="…">` |
| `\begin{enumerate}` | `1. …` | `<ol>` (unchanged) |
| `\begin{figure}` + `\caption` | tikzcd block | `<figure class="commutative-diagram">` (unchanged) |
| `\begin{equation}` + `\tag` | `$$…\tag{…}$$` | display math (unchanged) |
| `\ref{…}` | `Theorem 1.3.3` in prose | `<a class="math-ref-link">` (unchanged, `main.js`) |
| `\bibliography` | `## References` | `<ol class="reference">` (unchanged) |

Everything in the "unchanged" rows keeps working exactly as before; the plugin only adds
wrappers around them.

## 2. Recognising units

Only in the **mathematics** and **physics** domains (`.post-body[data-post-domain]`);
elsewhere (English, dictionary posts) bold text is ordinary emphasis and no unit is made.

| unit | opener, as the first thing in a paragraph | pattern |
|---|---|---|
| numbered section | `**3. Surjectivity and injectivity.**` | `\d+(\.\d+)*\.` then an optional title |
| environment | `**Theorem 1.3.3.**`, `**Definition 2.2.1.**`, `**Remark.**` | one of the kinds below, an optional number |
| proof | `*Proof.*`, `*Subproof.*`, `*Solution.*` | italic, optional trailing number |

Kinds (as counted in the corpus): Definition 103, Theorem 66, Exercise 30, Example 15,
Proposition 13, Corollary 8, Remark 7, Axiom 7, Lemma 6, Principle 2, Notation 1, Rule 1.
An environment may carry a name in parentheses: `**Theorem 2.2.20** (Heine–Borel theorem).`

**Numbers are read, never generated.** You write `Theorem 1.3.3.`; the plugin takes that
string verbatim for the id and the narration. It only *checks* — a number that does not
continue its neighbours produces a build warning, never a renumbering. Cross-references in
prose therefore always match what is printed.

## 3. Where a unit ends

- A **section** ends at the next section of the same or a shallower level, at the next
  `h2`–`h6`, or at the end of the post. Environments, prose, figures and lists in between
  belong to it.
- An **environment** ends at the QED marker when it has one (`data-environment-end`, from
  `$\square$` / `$\blacksquare$` / `\tag*{\(\square\)}`), otherwise at the next opener or
  at a paragraph that is not a continuation. Continuations are the existing blank-line
  markers `post-structural-continuation` (two blank lines) and `post-explicit-entry-break`
  (three or more), emitted by `_plugins/post_entry_breaks.rb`.
- A **proof** ends at its QED marker, else like an environment.

## 4. Identifiers — stable, and never renamed silently

| unit | id | on which element |
|---|---|---|
| environment | `theorem-1-3-3` — kind, lowercased, plus the number with `.`→`-` | the **label** (`<strong class="math-label-anchor">`), exactly as `main.js` does today |
| proof | `proof-theorem-1-3-3`, else `proof-N` | the label (`<em class="math-proof-marker">`) |
| numbered section | `sec-3`, `sec-3-1` | the label |
| heading section | the heading's kramdown id (`references`) | the `<h2>` |
| section wrapper | `unit-<id of its label/heading>` | the `<section>` |

The label keeps the id it has today, so every existing permalink, cross-reference and
podcast chapter link keeps resolving. The wrapper gets a derived id so both "jump to the
statement" and "select the whole unit" are addressable.

## 5. Headings without changing how the page looks

A run-in numbered title stays inside its paragraph — moving it out would change the layout
— and gets heading semantics through ARIA, which is what ARIA is for:

```html
<p class="math-environment__paragraph">
  <strong class="math-label-anchor doc-heading" id="sec-3"
          role="heading" aria-level="3">3. Surjectivity and injectivity.</strong>
  Let <span class="math-inline">\(f:X\to Y\)</span> be a function. …
</p>
```

Screen readers and the outline see a level-3 heading; the page looks exactly as before.
Switching later to a block heading is then a CSS-only decision.

## 6. The shape produced

```html
<div class="post-body" data-post-domain="mathematics" data-semantic-units="true">
  <section class="doc-section" data-doc="subsection" data-number="3" id="unit-sec-3">
    <p class="semantic-paragraph math-environment__paragraph">
      <strong class="math-label-anchor doc-heading" id="sec-3" role="heading" aria-level="3">3. …</strong> …
    </p>
    <figure class="commutative-diagram">…</figure>

    <section class="semantic-unit math-environment math-environment--proposition math-statement-italic"
             data-doc="proposition" data-environment-kind="Proposition" data-number="1"
             id="unit-proposition-1" aria-labelledby="proposition-1">
      <p class="math-environment__paragraph">
        <strong class="math-label-anchor" id="proposition-1">Proposition 1.</strong> …
      </p>
      <ol>…</ol>
    </section>

    <section class="semantic-unit math-environment math-environment--proof"
             data-doc="proof" data-proves="proposition-1" id="unit-proof-proposition-1">
      <p class="math-environment__paragraph">
        <em class="math-proof-marker" id="proof-proposition-1">Proof.</em> …
        <span class="qed" data-environment-end="proof">…</span>
      </p>
    </section>
  </section>
</div>
```

## 7. Who does what, after the change

- **`_plugins/document_structure.rb`** (new, `:post_convert`): all of the above.
- **`assets/js/main.js`**: keeps every presentational pass — soft line breaks, display-math
  continuations, section-opening paragraphs, label gaps, reference links, scrollable
  tables. Its `groupMathEnvironments` pass is deleted: the wrappers now arrive from the
  server. `addAnchorTargets` becomes a no-op guard (ids already exist).
- **`assets/css/post.css`**: selectors written as `.post-body > X` must also match inside
  a section wrapper. The file already uses `:is(.post-body, .math-environment) > …` in
  places; the rest follow that pattern.
- **`_narrator/skeleton.py`**: walks the tree instead of matching bold text. Its regexes
  (`ENV_RE`, `NUMBERED_RE`), the domain gate and the prose-splitting heuristics go away.

## 8. What the narrator gets

Each unit becomes a section with `parent`, `kind`, `number`, `title` and, for a proof,
`proves`. Because the page's audio is one timeline, a parent's range is exactly the span
of its children — so a subsection heading, a statement and a proof are all separately
playable with no extra synthesis. A statement and the proof that follows it form one
**play group**: clicking the statement plays both, clicking `Proof.` plays only the proof.
