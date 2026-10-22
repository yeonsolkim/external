---
section: proof-theorem-1-4-4
title: Proof
kind: proof
document: 1.4 Linear Combinations and Spans
url: /linear-algebra/linear-combinations-and-spans/
source: 9bbcb9f11b32deaeaf0fd51790113d65fed383f323e380c3a915d50a1bebb3e5
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-22
body: 9fc41c72cc940466b860535d9fd39547f547c44ca442e996d8ef882009409cf8
words: 222
---

Proof. We proceed by induction on n equals the cardinality of J. If n equals zero, then I equals J equals the empty set, so both sides equal zero in M. Now suppose that the statement holds for n equals k. Let the cardinality of J equal k plus one and choose j prime in J. Define I prime equals I set minus f inverse of the singleton j prime and J prime equals J set minus the singleton j prime, and let g from I prime to J prime be the restriction of f to I prime. Then, by Proposition 1.4.3, the sum over i in I of x i equals the sum over i in f inverse of j prime of x i plus the sum over i in I prime of x i.

Since the cardinality of J prime equals k, by the induction hypothesis and Definition 1.4.1, the sum over i in I of x i equals the sum over i in f inverse of j prime of x i plus the sum over j in J prime of the sum over i in g inverse of the singleton j of x i, which equals the sum over j in J of the sum over i in f inverse of j of x i. This completes the proof.
