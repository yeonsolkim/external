const { Plugin, loadMathJax } = require("obsidian");
const { execFile } = require("node:child_process");
const crypto = require("node:crypto");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const { promisify } = require("node:util");

const execFileAsync = promisify(execFile);
const CACHE_VERSION = "2";
const SVG_SCALE = 1.2;
// One tikzcd environment and nothing else: the body may not end another one.
const TIKZCD_ENVIRONMENT_PATTERN =
  /^\s*(\\begin\s*\{tikzcd\}(?:\[[^\]\r\n]*\])?(?:(?!\\end\s*\{tikzcd\})[\s\S])*\\end\s*\{tikzcd\})\s*$/;
// Obsidian renders math with MathJax 3's CHTML output, which differs from the
// site's SVG output in two ways that matter for \whitestar:
// - it measures the system-font star at full size and sets that width in px,
//   ignoring the font-size scale, so the glyph is boxed with a wide gap after
//   it; \rlap drops that box and \hspace restores the scaled advance width;
// - SVG stroke-width does nothing on HTML text, so -webkit-text-stroke
//   thickens the outline instead (relative to the scaled glyph size).
// 55% matches the TeX font's \circ, whose ring is larger than newcm's.
const MATHJAX_PREAMBLE = String.raw`
\def\whitestar{\mathbin{\rlap{{\unicode{x2606}}}\hspace{0.55em}}}
\def\lowparen#1{
  \mathinner{
    \mathopen{\lower .3em {\bigg(}}
    #1
    \mathclose{\lower .3em {\bigg)}}
  }
}
`;

module.exports = class TikzcdPreviewPlugin extends Plugin {
  async onload() {
    this.diagramIndex = 0;
    this.renderPromises = new Map();

    await this.loadMathJaxPreamble();

    this.registerMarkdownPostProcessor(
      (el, ctx) => this.renderDisplayMathDiagrams(el, ctx),
      -1000
    );

    this.registerMarkdownCodeBlockProcessor(
      "tikzcd",
      (source, el) =>
        this.renderTikz(
          ["\\begin{tikzcd}", source.trim(), "\\end{tikzcd}"].join("\n"),
          el
        ),
      -1000
    );
  }

  async loadMathJaxPreamble() {
    await loadMathJax();

    const mathJax = globalThis.MathJax;
    if (typeof mathJax?.tex2chtml !== "function") {
      console.warn("TikZ-cd Preview could not register MathJax macros.");
      return;
    }

    mathJax.tex2chtml(MATHJAX_PREAMBLE);
  }

  renderDisplayMathDiagrams(el, ctx) {
    const section = ctx.getSectionInfo(el);
    // The section info holds the whole note; only this section's lines pair
    // up with the math elements rendered in el.
    const sectionText = section?.text
      .split("\n")
      .slice(section.lineStart, section.lineEnd + 1)
      .join("\n");
    const sourceHasTikzcd = sectionText?.includes("\\begin{tikzcd}");
    let environments = [];

    if (sourceHasTikzcd) {
      const displayBlocks = this.findDisplayMathBlocks(sectionText);
      environments = displayBlocks
        .map((block) => block.environment)
        .filter(Boolean);
      const mathElements = this.findMathBlockElements(el);

      displayBlocks.forEach((block, index) => {
        if (!block.environment) return;

        const mathEl = mathElements[index];
        if (!mathEl) return;

        this.replaceWithTikz(mathEl, block.environment);
      });
    }

    // Obsidian releases do not all expose display math to post-processors at
    // the same stage. If core MathJax has already produced an error node,
    // recover the original environment from that node and replace it.
    if (
      this.replaceRenderedTikzcdErrors(el, environments) > 0 ||
      !sourceHasTikzcd
    ) {
      return;
    }

    const view = el.ownerDocument.defaultView;
    if (!view?.MutationObserver) return;

    const observer = new view.MutationObserver(() => {
      if (this.replaceRenderedTikzcdErrors(el, environments) > 0) {
        observer.disconnect();
      }
    });

    observer.observe(el, { childList: true, subtree: true });
    view.setTimeout(() => observer.disconnect(), 2000);
  }

  findDisplayMathBlocks(markdown) {
    const blocks = [];
    const displayMathPattern = /\$\$([\s\S]*?)\$\$/g;
    let match;

    while ((match = displayMathPattern.exec(markdown)) !== null) {
      blocks.push({ environment: this.tikzcdSource(match[1]) });
    }

    return blocks;
  }

  // What a display math body is typeset from: its tikzcd environment when that
  // is all it holds, or else one display formula setting the diagrams among
  // the other math, as in
  //   \begin{tikzcd}...\end{tikzcd} \quad \text{or} \quad \begin{tikzcd}...\end{tikzcd}.
  // Blank lines are dropped from a formula: TeX would end it there.
  tikzcdSource(body) {
    const environmentMatch = body.match(TIKZCD_ENVIRONMENT_PATTERN);
    if (environmentMatch) return environmentMatch[1];
    if (!/\\begin\s*\{tikzcd\}/.test(body)) return null;

    return `$\\displaystyle\n${body.trim().replace(/\n\s*\n/g, "\n")}\n$`;
  }

  findMathBlockElements(el) {
    const elements = [];
    const selector = ".math-block, .math.math-block, [data-math]";

    if (el.matches?.(selector)) elements.push(el);
    elements.push(...el.querySelectorAll(selector));

    return [...new Set(elements)];
  }

  replaceRenderedTikzcdErrors(el, sourceEnvironments = []) {
    const selector =
      "mjx-merror, mjx-container, .math-block, .math, [data-math]";
    const candidates = [];

    if (el.matches?.(selector)) candidates.push(el);
    candidates.push(...el.querySelectorAll(selector));

    const matches = candidates.filter(
      (candidate) =>
        !candidate.closest?.(".tikzcd-preview") &&
        this.candidateTikzcdSource(candidate) !== null
    );

    // Keep only the innermost match so one failed equation is replaced once.
    const innermost = matches.filter(
      (candidate) =>
        !matches.some(
          (other) => other !== candidate && candidate.contains(other)
        )
    );

    let replaced = 0;
    innermost.forEach((candidate, index) => {
      const environment =
        sourceEnvironments[index] || this.candidateTikzcdSource(candidate);
      if (!environment) return;

      const target =
        candidate.closest(".math-block") ||
        candidate.closest(".math") ||
        candidate.closest("mjx-container") ||
        candidate;

      if (this.replaceWithTikz(target, environment)) replaced += 1;
    });

    return replaced;
  }

  // A math element holds its TeX as text until MathJax replaces it, and
  // MathJax shows the TeX of a formula it cannot typeset.
  candidateTikzcdSource(candidate) {
    for (const text of [
      candidate.getAttribute?.("data-math"),
      candidate.textContent,
      candidate.getAttribute?.("aria-label"),
    ]) {
      const source = text ? this.tikzcdSource(text) : null;
      if (source) return source;
    }

    return null;
  }

  replaceWithTikz(mathEl, environment) {
    if (
      !mathEl?.isConnected ||
      mathEl.dataset.tikzcdProcessed === "true" ||
      mathEl.closest?.(".tikzcd-preview")
    ) {
      return false;
    }

    const replacement = mathEl.ownerDocument.createElement("div");
    mathEl.dataset.tikzcdProcessed = "true";
    mathEl.replaceWith(replacement);
    this.renderTikz(environment, replacement);
    return true;
  }

  async renderTikz(environment, el) {
    el.addClass("tikzcd-preview");
    const viewport = el.createDiv({ cls: "tikzcd-preview__viewport" });
    const status = viewport.createDiv({
      cls: "tikzcd-preview__status",
      text: "Rendering commutative diagram…",
    });

    try {
      const source = environment.replaceAll("\u00a0", " ").trim();
      const { svg, digest } = await this.cachedSvg(source);

      status.remove();
      viewport.appendChild(this.prepareSvg(svg, digest, el.ownerDocument));
    } catch (error) {
      console.error("TikZ-cd preview failed", error);

      status.remove();
      viewport.createDiv({
        cls: "tikzcd-preview__error",
        text: this.previewErrorMessage(error),
      });
    }
  }

  async cachedSvg(environment) {
    const digest = crypto
      .createHash("sha256")
      .update(`${CACHE_VERSION}\0${environment}`)
      .digest("hex");

    if (!this.renderPromises.has(digest)) {
      const renderPromise = this.loadOrCompileSvg(environment, digest).catch(
        (error) => {
          this.renderPromises.delete(digest);
          throw error;
        }
      );
      this.renderPromises.set(digest, renderPromise);
    }

    return { svg: await this.renderPromises.get(digest), digest };
  }

  async loadOrCompileSvg(environment, digest) {
    const vaultRoot = this.app.vault.adapter.getBasePath();
    const cacheDirectory = path.join(
      vaultRoot,
      this.app.vault.configDir,
      "cache",
      "tikzcd-preview"
    );
    const cachePath = path.join(cacheDirectory, `${digest}.svg`);

    try {
      return await fs.readFile(cachePath, "utf8");
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }

    const svg = await this.compileSvg(environment);
    await fs.mkdir(cacheDirectory, { recursive: true });
    await fs.writeFile(cachePath, svg, "utf8");
    return svg;
  }

  async compileSvg(environment) {
    const directory = await fs.mkdtemp(
      path.join(os.tmpdir(), "obsidian-tikzcd-")
    );

    try {
      const texPath = path.join(directory, "diagram.tex");
      await fs.writeFile(texPath, this.latexDocument(environment), "utf8");

      await this.runTexTool(
        "latex",
        [
          "-interaction=nonstopmode",
          "-halt-on-error",
          "-file-line-error",
          "-no-shell-escape",
          "diagram.tex",
        ],
        directory
      );
      await this.runTexTool(
        "dvisvgm",
        ["--no-fonts", "--exact-bbox", "--output=diagram.svg", "diagram.dvi"],
        directory
      );

      return await fs.readFile(path.join(directory, "diagram.svg"), "utf8");
    } finally {
      await fs.rm(directory, { recursive: true, force: true });
    }
  }

  async runTexTool(name, args, cwd) {
    const candidates =
      process.platform === "darwin"
        ? [`/Library/TeX/texbin/${name}`, name]
        : [name];
    let lastError;

    for (const executable of candidates) {
      try {
        await execFileAsync(executable, args, {
          cwd,
          timeout: 30000,
          maxBuffer: 5 * 1024 * 1024,
        });
        return;
      } catch (error) {
        lastError = error;
        if (error.code !== "ENOENT") throw error;
      }
    }

    throw lastError;
  }

  // A lone diagram is typeset as its own tikzpicture. A display formula has to
  // stay on one page, which the tikz option (a page per tikzpicture) would
  // prevent, and may use amsmath's \text.
  latexDocument(environment) {
    const formula = !TIKZCD_ENVIRONMENT_PATTERN.test(environment);
    return [
      "\\def\\pgfsysdriver{pgfsys-dvisvgm.def}",
      `\\documentclass[${formula ? "" : "tikz,"}border=2pt]{standalone}`,
      ...(formula ? ["\\usepackage{amsmath}"] : []),
      "\\usepackage{tikz-cd}",
      "\\begin{document}",
      environment,
      "\\end{document}",
      "",
    ].join("\n");
  }

  prepareSvg(source, digest, ownerDocument) {
    const Parser = ownerDocument.defaultView.DOMParser;
    const parsed = new Parser().parseFromString(source, "image/svg+xml");
    if (
      parsed.querySelector("parsererror") ||
      parsed.documentElement.nodeName !== "svg"
    ) {
      throw new Error("dvisvgm returned invalid SVG output.");
    }

    const svg = parsed.documentElement;
    const prefix = `tikzcd-${digest.slice(0, 10)}-${++this.diagramIndex}-`;
    this.namespaceSvgIds(svg, prefix);
    this.adaptSvgColors(svg);
    this.scaleSvgDimensions(svg);

    svg.classList.add("tikzcd-preview__svg");
    svg.setAttribute("role", "img");
    const title = parsed.createElementNS("http://www.w3.org/2000/svg", "title");
    title.id = `${prefix}title`;
    title.textContent = "Commutative diagram";
    svg.prepend(title);
    svg.setAttribute("aria-labelledby", title.id);

    return ownerDocument.importNode(svg, true);
  }

  scaleSvgDimensions(svg) {
    for (const attribute of ["width", "height"]) {
      const value = svg.getAttribute(attribute);
      const match = value?.match(/^(\d+(?:\.\d+)?)([a-z%]*)$/i);
      if (!match) continue;

      const scaledValue = (Number.parseFloat(match[1]) * SVG_SCALE)
        .toFixed(6)
        .replace(/\.?0+$/, "");
      svg.setAttribute(attribute, `${scaledValue}${match[2]}`);
    }
  }

  adaptSvgColors(svg) {
    for (const attribute of ["fill", "stroke"]) {
      svg.querySelectorAll(`[${attribute}]`).forEach((element) => {
        const color = element.getAttribute(attribute)?.toLowerCase();
        if (["#000", "#000000", "black"].includes(color)) {
          element.setAttribute(attribute, "currentColor");
        } else if (["#fff", "#ffffff", "white"].includes(color)) {
          // tikz-cd's background colour, painted behind description labels
          // and under crossing-over arrows to hide the lines they cover.
          element.style.setProperty(attribute, "var(--background-primary)");
        }
      });
    }
  }

  namespaceSvgIds(svg, prefix) {
    const idMap = new Map();
    svg.querySelectorAll("[id]").forEach((element) => {
      const oldId = element.id;
      const newId = `${prefix}${oldId}`;
      idMap.set(oldId, newId);
      element.id = newId;
    });

    svg.querySelectorAll("*").forEach((element) => {
      for (const attribute of [...element.attributes]) {
        let value = attribute.value;
        idMap.forEach((newId, oldId) => {
          if (value === `#${oldId}`) value = `#${newId}`;
          value = value.replaceAll(`url(#${oldId})`, `url(#${newId})`);
        });
        if (value !== attribute.value) {
          element.setAttribute(attribute.name, value);
        }
      }
    });
  }

  previewErrorMessage(error) {
    if (error?.code === "ENOENT") {
      return "TikZ-cd preview requires a TeX installation with latex and dvisvgm.";
    }

    return (
      "TikZ-cd preview failed. " +
      "Check the diagram syntax or the developer console."
    );
  }
};
