const { Plugin } = require("obsidian");
const { execFile } = require("node:child_process");
const crypto = require("node:crypto");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const { promisify } = require("node:util");

const execFileAsync = promisify(execFile);
const CACHE_VERSION = "2";
const SVG_SCALE = 1.2;

module.exports = class TikzcdPreviewPlugin extends Plugin {
  async onload() {
    this.diagramIndex = 0;
    this.renderPromises = new Map();

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

  renderDisplayMathDiagrams(el, ctx) {
    const section = ctx.getSectionInfo(el);
    const sourceHasTikzcd = section?.text.includes("\\begin{tikzcd}");
    let environments = [];

    if (sourceHasTikzcd) {
      const displayBlocks = this.findDisplayMathBlocks(section.text);
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
      const body = match[1];
      const environmentMatch = body.match(
        /^\s*(\\begin\s*\{tikzcd\}(?:\[[^\]\r\n]*\])?[\s\S]*?\\end\s*\{tikzcd\})\s*$/
      );

      blocks.push({
        environment: environmentMatch ? environmentMatch[1] : null,
      });
    }

    return blocks;
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

    const matches = candidates.filter((candidate) => {
      if (candidate.closest?.(".tikzcd-preview")) return false;

      const source = [
        candidate.getAttribute?.("data-math") || "",
        candidate.textContent || "",
        candidate.getAttribute?.("aria-label") || "",
      ].join("\n");

      return this.extractTikzcdEnvironment(source) !== null;
    });

    // Keep only the innermost match so one failed equation is replaced once.
    const innermost = matches.filter(
      (candidate) =>
        !matches.some(
          (other) => other !== candidate && candidate.contains(other)
        )
    );

    let replaced = 0;
    innermost.forEach((candidate, index) => {
      const source = [
        candidate.getAttribute?.("data-math") || "",
        candidate.textContent || "",
        candidate.getAttribute?.("aria-label") || "",
      ].join("\n");
      const environment =
        sourceEnvironments[index] || this.extractTikzcdEnvironment(source);
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

  extractTikzcdEnvironment(source) {
    const match = source.match(
      /\\begin\s*\{tikzcd\}(?:\[[^\]\r\n]*\])?[\s\S]*?\\end\s*\{tikzcd\}/
    );

    return match ? match[0] : null;
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

  latexDocument(environment) {
    return [
      "\\def\\pgfsysdriver{pgfsys-dvisvgm.def}",
      "\\documentclass[tikz,border=2pt]{standalone}",
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
      return (
        "TikZ-cd preview requires a TeX installation with latex and dvisvgm."
      );
    }

    return (
      "TikZ-cd preview failed. " +
      "Check the diagram syntax or the developer console."
    );
  }
};
