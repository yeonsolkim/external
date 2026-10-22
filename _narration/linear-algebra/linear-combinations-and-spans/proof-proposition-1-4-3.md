---
section: proof-proposition-1-4-3
title: Proof
kind: proof
document: 1.4 Linear Combinations and Spans
url: /linear-algebra/linear-combinations-and-spans/
source: ecd930e9aaa0b2c27161ec7503621ad62ebe5b4060f16800d14e9de7e214d4c9
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-22
body: 1e4d4483632094e88db1a9c5390ebb22306d252ae6746133e314648e23a6b105
words: 302
---

Proof. We proceed by induction on n equals the cardinality of B. If n equals zero, then B equals the empty set and I equals A. By Definition 1.4.1, we have the sum over i in I of x i equals the sum over i in A of x i, which equals the sum over i in A of x i plus zero in M, which equals the sum over i in A of x i plus the sum over i in B of x i.

Now suppose that the statement holds for n equals k. Let I equal A disjoint union B, and n equals k plus one. Choose b in B, and define B prime equals B minus the singleton b. Since I minus the singleton b equals A disjoint union B prime and the cardinality of B prime equals k, the induction hypothesis gives the sum over i in I minus the singleton b of x i equals the sum over i in A of x i plus the sum over i in B prime of x i.

Therefore, by Definition 1.4.1, the induction hypothesis, and the associativity and commutativity of addition in M, the sum over i in I of x i equals x b plus the sum over i in I minus the singleton b of x i, which equals x b plus the quantity, the sum over i in A of x i plus the sum over i in B prime of x i, which equals the sum over i in A of x i plus the quantity, x b plus the sum over i in B prime of x i, which equals the sum over i in A of x i plus the sum over i in B of x i. This completes the proof.
