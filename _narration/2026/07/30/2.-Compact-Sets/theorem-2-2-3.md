---
section: theorem-2-2-3
title: Theorem 2.2.3
kind: theorem
document: 2.2. Compact Sets
url: /2026/07/30/2.-Compact-Sets.html
source: 61386823ca3342dc22411d348ce623ca80870c5ade0c45cfb9d5f71bb8e6a919
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-15
body: 71dc1406803fa33278e70a6c309bc2528bd06a91bbc62d32564d79f18cc3de62
words: 284
---

Theorem 2.2.3. Let M be a metric space and let A be a subset of N, and N a subset of M. Then, A is compact in M if and only if A is compact in N.

Proof. Suppose that A is compact in M. Let the family U i, for i in I, be a cover of A whose elements are open in N. By Theorem 2.1.18, there is an open set V i such that V i intersect N equals U i for each i in I; and since A is compact in M, we have A is contained in the union from k equals one to n of V sub i k, for some finitely many indices i one through i n in I. We refer to this inclusion as star.

Since A is contained in N, star implies A is contained in the union from k equals one to n of U sub i k. We refer to this inclusion as double star.

Therefore A is compact in N. Conversely, suppose that A is compact in N. Let the family V i, for i in I, be a collection of open sets which covers A, and let U i equal V i intersect N for each i in I. Then U i is open in N for each i in I, and the family U i, for i in I, covers A. Since A is compact in N, double star holds for some finitely many indices i one through i n in I. Since U i is contained in V i for each i in I, double star implies star. Therefore A is compact in M. This completes the proof.
