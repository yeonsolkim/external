(() => {
  const ROOT_ID = "__root__";
  const ROOT_LABEL = "Subjects";

  const graphEl = document.getElementById("km-graph");

  if (!graphEl) {
    return;
  }

  boot();

  function boot() {
    if (typeof window.ForceGraph !== "function") {
      showError("ForceGraph library was not loaded. Check the CDN script tag or network blocking.");
      return;
    }

    let parents;
    let posts;
    let graphData;

    try {
      parents = readJson("km-parent-categories", []);
      posts = readJson("km-posts", []);
      graphData = buildGraphData(posts, parents);
    } catch (error) {
      console.error("[Knowledge Map] Failed to build graph data:", error);
      showError("Knowledge Map data could not be parsed. Check km-posts JSON in the page source.");
      return;
    }

    if (!graphData.nodes.length) {
      showError("No graph nodes were generated.");
      return;
    }

    console.info("[Knowledge Map] nodes:", graphData.nodes.length);
    console.info("[Knowledge Map] links:", graphData.links.length);

    initGraph(graphData);
  }

  function initGraph(graphData) {
    const linkedNodeIds = new Set();
    const linkedEdgeKeys = new Set();
    const neighborMap = buildNeighborMap(graphData.links);

    let hoverNode = null;
    let focusNode = null;

    const Graph = window.ForceGraph()(graphEl)
      .width(graphEl.clientWidth || 900)
      .height(graphEl.clientHeight || 720)
      .graphData({
        nodes: graphData.nodes,
        links: graphData.links
      })
      .nodeId("id")
      .nodeLabel(node => node.label)
      .backgroundColor("#ffffff")
      .enableNodeDrag(false)
      .enablePanInteraction(true)
      .enableZoomInteraction(true)
      .nodeRelSize(4)
      .cooldownTicks(160)
      .d3AlphaDecay(0.03)
      .d3VelocityDecay(0.35)
      .linkWidth(link => {
        if (!hoverNode && !focusNode) return 0.7;
        return linkedEdgeKeys.has(edgeKey(getNodeId(link.source), getNodeId(link.target))) ? 1.6 : 0.35;
      })
      .linkColor(link => {
        if (!hoverNode && !focusNode) {
          return "rgba(17, 17, 17, 0.16)";
        }

        return linkedEdgeKeys.has(edgeKey(getNodeId(link.source), getNodeId(link.target)))
          ? "rgba(17, 17, 17, 0.72)"
          : "rgba(17, 17, 17, 0.045)";
      })
      .nodeCanvasObjectMode(() => "replace")
      .nodeCanvasObject((node, ctx, globalScale) => {
        drawNode(node, ctx, globalScale, {
          hoverNode,
          focusNode,
          linkedNodeIds
        });
      })
      .onNodeHover(node => {
        hoverNode = node || null;
        updateHighlightState(hoverNode || focusNode);
        graphEl.style.cursor = node
          ? node.kind === "post"
            ? "pointer"
            : "zoom-in"
          : "default";
      })
      .onNodeClick(node => {
        if (!node) return;

        if (node.kind === "post" && node.url) {
          window.location.href = node.url;
          return;
        }

        focusNode = node;
        updateHighlightState(node);

        Graph.centerAt(node.x || 0, node.y || 0, 900);
        Graph.zoom(getZoomForNode(node), 1200);
      })
      .onBackgroundClick(() => {
        hoverNode = null;
        focusNode = null;
        updateHighlightState(null);
        Graph.centerAt(0, 0, 900);
        Graph.zoom(1.15, 1200);
      });

    const chargeForce = Graph.d3Force("charge");
    if (chargeForce && typeof chargeForce.strength === "function") {
      chargeForce.strength(-130);
    }

    const linkForce = Graph.d3Force("link");
    if (linkForce && typeof linkForce.distance === "function") {
      linkForce.distance(link => {
        const source = getNodeId(link.source);
        const target = getNodeId(link.target);
        const sourceNode = graphData.nodeById.get(source);
        const targetNode = graphData.nodeById.get(target);
        const maxDepth = Math.max(sourceNode?.depth || 0, targetNode?.depth || 0);

        if (maxDepth <= 1) return 115;
        if (maxDepth === 2) return 92;
        if (maxDepth === 3) return 74;
        return 58;
      });
    }

    Graph.zoom(1.15, 0);

    window.addEventListener("resize", () => {
      Graph.width(graphEl.clientWidth || 900);
      Graph.height(graphEl.clientHeight || 720);
    });

    document.addEventListener("keydown", event => {
      if (event.key === "Escape") {
        hoverNode = null;
        focusNode = null;
        updateHighlightState(null);
        Graph.centerAt(0, 0, 900);
        Graph.zoom(1.15, 1200);
      }
    });

    function updateHighlightState(node) {
      linkedNodeIds.clear();
      linkedEdgeKeys.clear();

      if (!node) return;

      linkedNodeIds.add(node.id);

      const neighbors = neighborMap.get(node.id) || [];
      neighbors.forEach(item => {
        linkedNodeIds.add(item.nodeId);
        linkedEdgeKeys.add(item.edgeKey);
      });

      const ancestors = getAncestors(node.id, graphData.nodeById);
      ancestors.forEach(ancestorId => {
        linkedNodeIds.add(ancestorId);

        const child = getChildToward(node.id, ancestorId, graphData.nodeById);
        if (child) {
          linkedEdgeKeys.add(edgeKey(ancestorId, child.id));
        }
      });
    }
  }

  function drawNode(node, ctx, globalScale, state) {
    const activeNode = state.hoverNode || state.focusNode;
    const hasActiveState = Boolean(activeNode);
    const isActive = hasActiveState && activeNode.id === node.id;
    const isLinked = state.linkedNodeIds.has(node.id);

    const radius = getNodeRadius(node, isActive, isLinked);
    const alpha = !hasActiveState ? 1 : isActive || isLinked ? 1 : 0.14;

    ctx.save();
    ctx.globalAlpha = alpha;

    ctx.beginPath();
    ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
    ctx.fillStyle = "#ffffff";
    ctx.fill();

    ctx.lineWidth = isActive ? 1.7 : isLinked ? 1.25 : 0.95;
    ctx.strokeStyle = getNodeStroke(node, isActive, isLinked, hasActiveState);
    ctx.stroke();

    if (shouldDrawLabel(node, isActive, isLinked, hasActiveState, globalScale)) {
      drawLabel(node, ctx, radius, globalScale, isActive);
    }

    ctx.restore();
  }

  function drawLabel(node, ctx, radius, globalScale, isActive) {
    const label = node.label || "";
    const fontSize = Math.max(10, Math.min(13, 13 / globalScale));
    const fontWeight = isActive ? 500 : 400;

    ctx.font = `${fontWeight} ${fontSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "top";

    const paddingX = 5 / globalScale;
    const paddingY = 3 / globalScale;
    const textWidth = ctx.measureText(label).width;
    const boxWidth = textWidth + paddingX * 2;
    const boxHeight = fontSize + paddingY * 2;

    const x = node.x;
    const y = node.y + radius + 6 / globalScale;

    ctx.fillStyle = "rgba(255, 255, 255, 0.88)";
    roundRect(ctx, x - boxWidth / 2, y - paddingY, boxWidth, boxHeight, 5 / globalScale);
    ctx.fill();

    ctx.fillStyle = isActive ? "#111111" : "#333333";
    ctx.fillText(label, x, y);
  }

  function getNodeRadius(node, isActive, isLinked) {
    if (isActive) return 7.5;
    if (isLinked) return node.kind === "post" ? 4.5 : 5.3;

    if (node.kind === "root") return 6;
    if (node.kind === "category" && node.depth <= 1) return 5.4;
    if (node.kind === "category") return 4.5;
    return 3.6;
  }

  function getNodeStroke(node, isActive, isLinked, hasActiveState) {
    if (isActive) return "#111111";
    if (isLinked) return "#333333";
    if (hasActiveState) return "#d9d9d9";

    if (node.kind === "root") return "#222222";
    if (node.kind === "category") return "#777777";
    return "#aaaaaa";
  }

  function shouldDrawLabel(node, isActive, isLinked, hasActiveState, globalScale) {
    if (isActive || isLinked) return true;
    if (node.kind === "root") return true;
    if (!hasActiveState && node.depth <= 1) return true;
    return globalScale > 1.8 && node.depth <= 2;
  }

  function getZoomForNode(node) {
    if (node.kind === "root") return 1.2;
    if (node.depth <= 1) return 1.9;
    if (node.depth === 2) return 2.5;
    return 3;
  }

  function buildGraphData(posts, parents) {
    const nodes = new Map();
    const links = [];

    const parentLookup = new Map(
      parents.map(parent => [normalizeKey(parent), parent])
    );

    createNode({
      id: ROOT_ID,
      label: ROOT_LABEL,
      rawLabel: ROOT_LABEL,
      kind: "root",
      depth: 0,
      parent: null
    });

    parents.forEach(parent => {
      ensureCategoryPath([parent]);
    });

    posts.forEach((post, index) => {
      const path = normalizeCategoryPath(post.category_path, post.categories, parentLookup);
      if (!path || path.length === 0) return;

      const categoryNode = ensureCategoryPath(path);
      const title = post.title || "Untitled";
      const postId = `${categoryNode.id}/__post__-${slugify(title)}-${index}`;

      if (!nodes.has(postId)) {
        createNode({
          id: postId,
          label: title,
          rawLabel: title,
          url: post.url,
          kind: "post",
          depth: path.length + 1,
          parent: categoryNode.id
        });

        createLink(categoryNode.id, postId);
      }
    });

    return {
      nodes: [...nodes.values()],
      links,
      nodeById: nodes
    };

    function ensureCategoryPath(path) {
      let parentId = ROOT_ID;
      let current = nodes.get(ROOT_ID);

      path.forEach((label, index) => {
        const cleanLabel = String(label || "").trim();
        if (!cleanLabel) return;

        const id = `${parentId}/${slugify(cleanLabel)}`;

        if (!nodes.has(id)) {
          createNode({
            id,
            label: stripLeadingIndex(cleanLabel),
            rawLabel: cleanLabel,
            kind: "category",
            depth: index + 1,
            parent: parentId
          });

          createLink(parentId, id);
        }

        current = nodes.get(id);
        parentId = id;
      });

      return current;
    }

    function createNode(node) {
      nodes.set(node.id, node);
      return node;
    }

    function createLink(source, target) {
      const key = edgeKey(source, target);

      if (links.some(link => link.key === key)) {
        return;
      }

      links.push({
        source,
        target,
        key
      });
    }
  }

  function buildNeighborMap(links) {
    const map = new Map();

    links.forEach(link => {
      const source = getNodeId(link.source);
      const target = getNodeId(link.target);
      const key = edgeKey(source, target);

      if (!map.has(source)) map.set(source, []);
      if (!map.has(target)) map.set(target, []);

      map.get(source).push({ nodeId: target, edgeKey: key });
      map.get(target).push({ nodeId: source, edgeKey: key });
    });

    return map;
  }

  function normalizeCategoryPath(categoryPath, categories, parentLookup) {
    let pieces = [];

    if (categoryPath) {
      pieces = toPathPieces(categoryPath);
    }

    if (pieces.length === 0 && categories) {
      pieces = toPathPieces(categories);
    }

    if (pieces.length === 0) {
      return null;
    }

    const parentIndex = pieces.findIndex(piece => {
      return parentLookup.has(normalizeKey(piece));
    });

    if (parentIndex === -1) {
      return null;
    }

    const matchedParent = parentLookup.get(normalizeKey(pieces[parentIndex]));
    return [matchedParent, ...pieces.slice(parentIndex + 1)];
  }

  function toPathPieces(value) {
    const asArray = Array.isArray(value) ? value : [value];

    return asArray
      .flatMap(item => String(item).split("|"))
      .flatMap(item => String(item).split("/"))
      .map(item => item.trim())
      .filter(Boolean);
  }

  function getAncestors(id, nodeById) {
    const result = [];
    let current = nodeById.get(id)?.parent;

    while (current) {
      result.push(current);
      current = nodeById.get(current)?.parent;
    }

    return result;
  }

  function getChildToward(targetId, ancestorId, nodeById) {
    let current = nodeById.get(targetId);
    let previous = null;

    while (current && current.id !== ancestorId) {
      previous = current;
      current = nodeById.get(current.parent);
    }

    return previous;
  }

  function readJson(id, fallback) {
    const el = document.getElementById(id);

    if (!el) {
      return fallback;
    }

    try {
      return JSON.parse(el.textContent);
    } catch (error) {
      console.warn(`[Knowledge Map] Invalid JSON in #${id}`, error);
      return fallback;
    }
  }

  function getNodeId(value) {
    return typeof value === "object" && value !== null ? value.id : value;
  }

  function edgeKey(source, target) {
    return `${source}→${target}`;
  }

  function slugify(value) {
    const normalized = String(value)
      .trim()
      .toLowerCase()
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/&/g, "and")
      .replace(/[^a-z0-9가-힣]+/gi, "-")
      .replace(/^-+|-+$/g, "");

    return normalized || "item";
  }

  function normalizeKey(value) {
    return stripLeadingIndex(String(value)).trim().toLowerCase();
  }

  function stripLeadingIndex(value) {
    return String(value)
      .trim()
      .replace(/^[0-9\s.)_:-]+/, "")
      .trim();
  }

  function roundRect(ctx, x, y, width, height, radius) {
    const r = Math.min(radius, width / 2, height / 2);

    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + width, y, x + width, y + height, r);
    ctx.arcTo(x + width, y + height, x, y + height, r);
    ctx.arcTo(x, y + height, x, y, r);
    ctx.arcTo(x, y, x + width, y, r);
    ctx.closePath();
  }

  function showError(message) {
    const el = document.createElement("div");
    el.className = "km-error";
    el.textContent = message;
    graphEl.appendChild(el);
  }
})();