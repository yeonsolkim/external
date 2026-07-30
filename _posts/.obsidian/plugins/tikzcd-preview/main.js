const { Plugin, loadMathJax } = require("obsidian");
const { execFile } = require("node:child_process");
const crypto = require("node:crypto");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const { promisify } = require("node:util");

const execFileAsync = promisify(execFile);
const CACHE_VERSION = "3";
const SVG_SCALE = 1.2;
const MATHJAX_VERSION = "4.1.3";
const MATHJAX_COMPONENT_URL =
  `https://cdn.jsdelivr.net/npm/mathjax@${MATHJAX_VERSION}/tex-mml-svg.js`;
const MATHJAX_NEWCM_URL =
  "https://cdn.jsdelivr.net/npm/@mathjax/" +
  `mathjax-newcm-font@${MATHJAX_VERSION}`;
const NEWCM_RENDER_ATTRIBUTE = "data-newcm-mathjax";
const NEWCM_SOURCE_PROPERTY = Symbol("newcmMathSource");
const MATHJAX_PREAMBLE = String.raw`
\def\lowparen#1{
  \mathinner{
    \mathopen{\lower .25em {\bigg(}}
    #1
    \mathclose{\lower .25em {\bigg)}}
  }
}
`;

module.exports = class TikzcdPreviewPlugin extends Plugin {
  async onload() {
    this.diagramIndex = 0;
    this.renderPromises = new Map();

    await this.loadMathJaxPreamble();
    this.mathJax4Promise = this.loadMathJax4Renderer().catch((error) => {
      console.warn(
        "TikZ-cd Preview could not start the New Computer Modern renderer.",
        error
      );
      return null;
    });
    this.register(() => this.mathJax4Frame?.remove());

    this.registerMarkdownPostProcessor(
      (el, ctx) => {
        this.renderDisplayMathDiagrams(el, ctx);
        this.captureObsidianMathSources(el);
      },
      -1000
    );

    this.registerMarkdownPostProcessor(
      (el) => this.watchAndRenderObsidianMath(el),
      1000
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

  async loadMathJax4Renderer() {
    const frame = document.createElement("iframe");
    frame.className = "tikzcd-preview__mathjax-frame";
    frame.hidden = true;
    frame.tabIndex = -1;
    frame.setAttribute("aria-hidden", "true");
    frame.srcdoc = [
      "<!doctype html>",
      '<html><head><meta charset="utf-8">',
      "<script>",
      `window.MathJax=${JSON.stringify({
        loader: {
          paths: {
            "mathjax-newcm": MATHJAX_NEWCM_URL,
          },
        },
        tex: {
          macros: {
            lowparen: [
              "\\mathinner{\\mathopen{\\lower .25em {\\bigg(}}" +
                "#1\\mathclose{\\lower .25em {\\bigg)}}}",
              1,
            ],
          },
        },
        startup: {
          typeset: false,
        },
        options: {
          enableMenu: false,
        },
        output: {
          font: "mathjax-newcm",
        },
        svg: {
          blacker: 9,
          fontCache: "none",
          scale: 0.9,
          exFactor: 0.5,
          displayAlign: "center",
        },
      })};`,
      "</script>",
      `<script src="${MATHJAX_COMPONENT_URL}"></script>`,
      "</head><body></body></html>",
    ].join("");

    const loaded = new Promise((resolve, reject) => {
      const timeout = window.setTimeout(
        () => reject(new Error("MathJax 4 took too long to load.")),
        15000
      );
      frame.addEventListener(
        "load",
        () => {
          window.clearTimeout(timeout);
          resolve();
        },
        { once: true }
      );
      frame.addEventListener(
        "error",
        () => {
          window.clearTimeout(timeout);
          reject(new Error("MathJax 4 could not be loaded."));
        },
        { once: true }
      );
    });

    document.body.appendChild(frame);
    this.mathJax4Frame = frame;
    await loaded;

    const mathJax = frame.contentWindow?.MathJax;
    if (!mathJax?.startup?.promise) {
      throw new Error("MathJax 4 did not expose its startup promise.");
    }

    await mathJax.startup.promise;
    if (
      typeof mathJax.tex2svgPromise !== "function" ||
      typeof mathJax.mathml2svgPromise !== "function"
    ) {
      throw new Error("MathJax 4 did not expose its SVG converters.");
    }

    return mathJax;
  }

  watchAndRenderObsidianMath(el) {
    void this.renderObsidianMath(el);

    const view = el.ownerDocument.defaultView;
    if (!view?.MutationObserver) return;

    const observer = new view.MutationObserver(() => {
      void this.renderObsidianMath(el);
    });
    observer.observe(el, { childList: true, subtree: true });
    view.setTimeout(() => observer.disconnect(), 2000);
  }

  captureObsidianMathSources(el) {
    const selector = ".math-inline, .math-block";
    const mathElements = [];

    if (el.matches?.(selector)) mathElements.push(el);
    mathElements.push(...el.querySelectorAll(selector));

    mathElements.forEach((mathElement) => {
      if (
        mathElement[NEWCM_SOURCE_PROPERTY] ||
        mathElement.querySelector("mjx-container") ||
        mathElement.closest(".tikzcd-preview")
      ) {
        return;
      }

      const source =
        mathElement.getAttribute("data-math") || mathElement.textContent || "";
      if (!source.trim() || this.extractTikzcdEnvironment(source)) return;

      mathElement[NEWCM_SOURCE_PROPERTY] = source.trim();
    });
  }

  async renderObsidianMath(el) {
    const containers = this.findObsidianMathContainers(el);
    if (containers.length === 0) return;

    containers.forEach((container) => {
      container.setAttribute(NEWCM_RENDER_ATTRIBUTE, "pending");
    });

    const mathJax = await this.mathJax4Promise;
    if (!mathJax) {
      containers.forEach((container) => {
        if (container.isConnected) {
          container.setAttribute(NEWCM_RENDER_ATTRIBUTE, "unavailable");
        }
      });
      return;
    }

    for (const container of containers) {
      if (!container.isConnected || container.closest(".tikzcd-preview")) {
        continue;
      }

      const input = this.extractMathInput(container);
      if (!input) {
        container.setAttribute(NEWCM_RENDER_ATTRIBUTE, "unavailable");
        continue;
      }

      try {
        const options = { display: input.display };
        const converted =
          input.kind === "tex"
            ? await mathJax.tex2svgPromise(input.source, options)
            : await mathJax.mathml2svgPromise(input.source, options);
        if (!container.isConnected) continue;

        const rendered = container.ownerDocument.importNode(converted, true);
        rendered.classList.add("newcm-mathjax");
        rendered.setAttribute(NEWCM_RENDER_ATTRIBUTE, "complete");

        const label = container.getAttribute("aria-label");
        if (label && !rendered.hasAttribute("aria-label")) {
          rendered.setAttribute("aria-label", label);
        }

        const assistiveMathMl = container.querySelector("mjx-assistive-mml");
        if (
          assistiveMathMl &&
          !rendered.querySelector("mjx-assistive-mml")
        ) {
          rendered.appendChild(
            container.ownerDocument.importNode(assistiveMathMl, true)
          );
        }

        container.replaceWith(rendered);
      } catch (error) {
        container.setAttribute(NEWCM_RENDER_ATTRIBUTE, "failed");
        console.warn(
          "TikZ-cd Preview could not render an equation with MathJax 4.",
          error
        );
      }
    }
  }

  findObsidianMathContainers(el) {
    const selector =
      `mjx-container[jax="CHTML"]:not([${NEWCM_RENDER_ATTRIBUTE}])`;
    const containers = [];

    if (el.matches?.(selector)) containers.push(el);
    containers.push(...el.querySelectorAll(selector));

    return containers.filter(
      (container) => !container.closest(".tikzcd-preview")
    );
  }

  extractMathInput(container) {
    const wrapper = container.closest(".math-inline, .math-block");
    const texSource = wrapper?.[NEWCM_SOURCE_PROPERTY];
    if (texSource) {
      return {
        kind: "tex",
        source: texSource,
        display:
          wrapper.classList.contains("math-block") ||
          container.getAttribute("display") === "true",
      };
    }

    const math = container.querySelector("mjx-assistive-mml math");
    if (math) {
      const Serializer =
        container.ownerDocument.defaultView?.XMLSerializer || XMLSerializer;
      return {
        kind: "mathml",
        source: new Serializer().serializeToString(math),
        display:
          math.getAttribute("display") === "block" ||
          container.getAttribute("display") === "true" ||
          Boolean(container.closest(".math-block")),
      };
    }

    const mathJax = globalThis.MathJax;
    const document = mathJax?.startup?.document;
    const toMml = mathJax?.startup?.toMML;
    if (
      typeof document?.getMathItemsWithin !== "function" ||
      typeof toMml !== "function"
    ) {
      return null;
    }

    const [item] = document.getMathItemsWithin([container]);
    if (!item?.root) return null;

    return {
      kind: "mathml",
      source: toMml(item.root),
      display:
        item.display ||
        container.getAttribute("display") === "true" ||
        Boolean(container.closest(".math-block")),
    };
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
        "dvilualatex",
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
        return await execFileAsync(executable, args, {
          cwd,
          timeout: 30000,
          maxBuffer: 5 * 1024 * 1024,
        });
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
      "\\usepackage[regular]{newcomputermodern}",
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
        "TikZ-cd preview requires dvilualatex, dvisvgm, tikz-cd, " +
        "and New Computer Modern."
      );
    }

    return (
      "TikZ-cd preview failed. " +
      "Check the diagram syntax or the developer console."
    );
  }
};
