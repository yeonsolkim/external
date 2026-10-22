---
section: proof-proposition-1-3-3
title: Proof
kind: proof
document: 1.3 Linear Combinations and Spans
url: /2026/06/21/3.-Linear-Combinations-and-Spans.html
source: 6a58382ac78b5ef42b94bd4af304b40e447cb225f0fe62e73be7d1f656757908
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-19
body: fa4b91fcdfb3f3bebb612af15a3baab05a54cb140287638980c1098d2fb1c08c
words: 306
---

Proof. We proceed by induction on n equals the cardinality of B. If n equals zero, then B equals the empty set and I equals A. By Definition 1.3.1, we have the sum over i in I of x i, equals the sum over i in A of x i, which equals the sum over i in A of x i, plus zero in M, which equals the sum over i in A of x i, plus the sum over i in B of x i.

Now suppose that the statement holds for n equals k. Let I equal A disjoint union B, and n equals k plus one. Choose b in B, and define B prime equals B setminus the set containing b. Since I setminus the set containing b equals A disjoint union B prime and the cardinality of B prime equals k, the induction hypothesis gives the sum over i in I setminus the set containing b of x i, equals the sum over i in A of x i, plus the sum over i in B prime of x i.

Therefore, by Definition 1.3.1, the induction hypothesis, and the associativity and commutativity of addition in M, the sum over i in I of x i, equals x b plus the sum over i in I setminus the set containing b of x i, which equals x b plus the quantity the sum over i in A of x i, plus the sum over i in B prime of x i, which equals the sum over i in A of x i, plus the quantity x b plus the sum over i in B prime of x i, which equals the sum over i in A of x i, plus the sum over i in B of x i. This completes the proof.
