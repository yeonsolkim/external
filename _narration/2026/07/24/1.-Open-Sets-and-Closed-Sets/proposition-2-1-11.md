---
section: proposition-2-1-11
title: Proposition 2.1.11
kind: proposition
document: 2.1. Open Sets and Closed Sets
url: /2026/07/24/1.-Open-Sets-and-Closed-Sets.html
source: 8a083a08888274e8cb9ba962879e1fc9c33d8714af2413ebd62d3c2812a40827
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-15
body: b50bdfe8c21d353083384f75eb456263544d26ac6931665b2dacca6234410f0a
words: 272
---

Proposition 2.1.11. Let M be a metric space and let A be contained in M. Then the following hold.

One: the closure of A equals M set minus the exterior of A.

Two: the closure of A equals A union A prime.

Three: the interior of A is contained in A, which is contained in the closure of A.

Proof. For one, if x belongs to the closure of A, then every ball meets A. Hence no balls lie entirely in A complement, so that x is not in the exterior of A. If x is not in the exterior of A, then every ball meets A so that x belongs to the closure of A. Hence the closure of A equals M set minus the exterior of A.

For two, since the open ball of radius r about x equals the punctured open ball of radius r about x union the singleton x, every ball around x meets A if and only if every punctured ball meets A or the singleton x meets A. Hence the closure of A equals A union A prime.

For three, if x belongs to the interior of A, then the open ball of radius r about x is contained in A for some r greater than zero. Since x belongs to the open ball of radius r about x, x belongs to A, so that the interior of A is contained in A. Two immediately yields A is contained in the closure of A. Therefore the interior of A is contained in A, which is contained in the closure of A. This completes the proof.
