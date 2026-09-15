---
section: theorem-3-3-4
title: Theorem 3.3.4
kind: theorem
document: 3.3. Cauchy Sequences
url: /2026/09/09/3.-Cauchy-Sequences.html
source: f3e26eabb3692ce0e3a84eded74bd21d1e76ee251cb6aaad3379b3ef0d497acc
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-15
body: 2f5ad85fdae40750ad83b6b113fccf6087b1f9e740d4863a087fec77fb548ea3
words: 370
---

Theorem 3.3.4. Let M be a metric space. Then the following hold.

First, let A be a subset of M. Then, the diameter of closure of A equals the diameter of A.

Second, let K n be a sequence of nonempty compact sets in M such that K n plus one is contained in K n for n equals one, two, three, and so on. If the limit as n tends to infinity of the diameter of K n equals zero, then the intersection of the K n consists of one point.

Proof. First, let epsilon be greater than zero be given, and let x and y be in closure of A. Then there exist points x prime and y prime in A such that d of x comma x prime is less than epsilon and d of y comma y prime is less than epsilon. Hence, we have d of x comma y is less than or equal to d of x comma x prime plus d of x prime comma y prime plus d of y prime comma y, which is less than d of x prime comma y prime plus two epsilon, which is less than or equal to the diameter of A plus two epsilon.

It follows that d of x comma y is less than the diameter of A. Therefore the diameter of closure of A is less than or equal to the diameter of A. Since A is contained in closure of A, it is clear that the diameter of A is less than or equal to the diameter of closure of A. Consequently, the diameter of closure of A equals the diameter of A.

Second, by Corollary 2.2.12, the intersection of the K n is nonempty. If x and y are in the intersection of the K n with x not equal to y, then the diameter of K n is greater than d of x comma y, which is greater than zero, for every n in the positive integers. This contradicts the limit as n tends to infinity of the diameter of K n equals zero. Therefore the intersection of the K n consists of exactly one point. This completes the proof.
