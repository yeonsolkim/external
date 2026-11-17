---
section: proof-theorem-3-2-7
title: Proof
kind: proof
document: 3.2 The Dimension Function
url: /linear-algebra/the-dimension-function/
source: f3d84e0a0d221a1108eb6b486f875851eb56057505ffb63654090c52cd43d1cc
skeleton: 4
prompt: lecture-v5
model: gpt-5.5
generated: 2026-11-17
body: cf87536b6fa6bc7dba51af2babf7a7bfad749f461fb66bce96ee5341fadf4c98
words: 212
---

Proof. Let S belong to the power set of V and W belong to the subspaces of V. Suppose sigma of S is contained in W and let s belong to S. Since s belongs to the span of S, s belongs to sigma of S, which is contained in W. Hence S is contained in iota of W. Conversely, suppose S is contained in iota of W and let v belong to sigma of S. Then there exist a finite set I and indexed families, the family s i, for i in I, in S, and the family a i, for i in I, in F, such that v equals the sum over i in I of a i times s i. Since the set of s i such that i belongs to I is contained in S, which is contained in iota of W, which equals W, and W is a subspace, v equals the sum over i in I of a i times s i, belongs to W. Hence sigma of S is contained in W. By Definition 3.2.4, the pair sigma, iota is a Galois connection. Furthermore, by Theorem 3.2.5, iota composed with sigma is a closure operator on the power set of V. This completes the proof.
