---
section: proof-theorem-1-3-4
title: Proof
kind: proof
document: 1.3 Linear Combinations and Spans
url: /2026/06/21/3.-Linear-Combinations-and-Spans.html
source: 180d395836ad151cf0fd8f3e742a1d680f9d81063fa6aad202d1f707fc4e4d5a
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-19
body: 22ca906a8119a46277c7aca2564eb30de19b3e4f3f1474a65afcb640f282f8a3
words: 220
---

Proof. We proceed by induction on n equals the cardinality of J. If n equals zero, then I equals J equals the empty set, so both sides equal zero in M. Now suppose that the statement holds for n equals k. Let the cardinality of J equal k plus one and choose j prime in J. Define I prime equals I setminus f inverse of the singleton j prime and J prime equals J setminus the singleton j prime, and let g from I prime to J prime be the restriction of f to I prime. Then, by Proposition 1.3.3, the sum over i in I of x i equals the sum over i in f inverse of j prime of x i, plus the sum over i in I prime of x i.

Since the cardinality of J prime equals k, by the induction hypothesis and Definition 1.3.1, the sum over i in I of x i equals the sum over i in f inverse of j prime of x i, plus the sum over j in J prime of the sum over i in g inverse of the singleton j of x i, which equals the sum over j in J of the sum over i in f inverse of j of x i. This completes the proof.
