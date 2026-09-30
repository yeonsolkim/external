---
section: proof-lemma-3-3-4
title: Proof
kind: proof
document: 3.3 Cauchy Sequences
url: /2026/09/09/3.-Cauchy-Sequences.html
source: 3cce40f33ca137f34eb5e844ab2eb7022db0968ec7aee29f7990af7bbb102456
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-09-30
body: 83db1999f2e0f91f839ea0148110b6dea07c5cb3b61a0774a6968eb25e136e67
words: 275
---

Proof. Part one. Let epsilon greater than zero be given, and let x and y be in closure of A. Then there exist points x prime and y prime in A such that d of x and x prime is less than epsilon and d of y and y prime is less than epsilon. Hence, we have d of x and y is less than or equal to d of x and x prime plus d of x prime and y prime plus d of y prime and y, which is less than d of x prime and y prime plus two epsilon, which is less than or equal to diameter of A plus two epsilon.

It follows that d of x and y is less than or equal to diameter of A. Therefore diameter of closure of A is less than or equal to diameter of A. Since A is contained in closure of A, it is clear that diameter of A is less than or equal to diameter of closure of A. Consequently, diameter of closure of A equals diameter of A.

Part two. By Corollary 2.2.12, the intersection of the K n is nonempty. If x and y are in the intersection of the K n with x not equal to y, then diameter of K n is greater than or equal to d of x and y, which is greater than zero, for every n in the positive integers. This contradicts the limit as n tends to infinity of diameter of K n equals zero. Therefore the intersection of the K n consists of exactly one point. This completes the proof.
