---
section: proof-theorem-3-2-3
title: Proof
kind: proof
document: 3.2 The Dimension Function
url: /linear-algebra/the-dimension-function/
source: 0a6b10a4014af00d4edb828e3f9b1d04526162e82aefafe137a0e148889caf24
skeleton: 4
prompt: lecture-v5
model: gpt-5.5
generated: 2026-11-17
body: 65e967cc9995273b44f5d74e25042a1eb22879c5127d61fb5645af2293041449
words: 341
---

Proof. First, by the definitions of union and intersection, union is distributive over intersection and vice versa. Hence the power set of V is distributive.

Second, let W one, W two, and W three belong to the subspaces of V and W one be contained in W three. Suppose w belongs to W one plus the intersection of W two and W three. Then there exist w one in W one and w two in the intersection of W two and W three such that w equals w one plus w two. Hence w equals w one plus w two, which belongs to W one plus W two. Furthermore, since W one is contained in W three, we have w one in W three and w two in W three. Since W three belongs to the subspaces of V, w equals w one plus w two, which belongs to W three. Thus W one plus the intersection of W two and W three, is contained in the intersection of W one plus W two and W three.

We now suppose w belongs to the intersection of W one plus W two and W three. Then there exist w one in W one and w two in W two such that w equals w one plus w two. Since W one is contained in W three and W three belongs to the subspaces of V, w one belongs to W three so that w two equals w minus w one, which belongs to W three. Thus w equals w one plus w two, which belongs to W one plus the intersection of W two and W three, so W one plus the intersection of W two and W three, contains the intersection of W one plus W two and W three. It is concluded that W one plus the intersection of W two and W three, equals the intersection of W one plus W two and W three, and, by Definition 1.3.13, the subspaces of V is modular. This completes the proof.
