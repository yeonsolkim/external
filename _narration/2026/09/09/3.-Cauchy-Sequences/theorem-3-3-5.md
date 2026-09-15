---
section: theorem-3-3-5
title: Theorem 3.3.5
kind: theorem
document: 3.3. Cauchy Sequences
url: /2026/09/09/3.-Cauchy-Sequences.html
source: 21ebe0f7d6dc44108087ac5798d3a6e85d1af74f8e21cdebf835e83272405352
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-15
body: 547115844df1a795d3b1c8fd9f32b78718793070235dc54c93b8416db7f220a5
words: 375
---

Theorem 3.3.5. Let x n be a sequence in a metric space M.

First, if x n converges in M, then x n is a Cauchy sequence. Second, if M is compact and x n is a Cauchy sequence, then x n converges in M.

Proof. First, suppose x n converges to x in M and let epsilon greater than zero be given. Then, there is n naught in the positive integers such that n greater than or equal to n naught implies d of x n, x is less than epsilon over two. By the triangle inequality, it follows that m and n greater than or equal to n naught implies d of x m, x n is less than epsilon.

Hence x n is a Cauchy sequence. Second, let E k equal the set of x n such that n is greater than or equal to k. Then Theorem 3.3.3 and part one of Theorem 3.3.4 gives the limit as k tends to infinity of the diameter of the closure of E k equals zero.

Since M is compact, by Theorem 2.2.7, closure of E k is compact. Since E k plus one is contained in E k, we also have closure of E k plus one is contained in closure of E k. Part two of Theorem 3.3.4 now shows that there is a unique point y in the intersection from k equals one to infinity of closure of E k. Let epsilon greater than zero be given. Then, there is k naught in the positive integers such that k greater than or equal to k naught implies the diameter of the closure of E k is less than epsilon. Since y is in closure of E k, if z is in closure of E k then d of z, y is less than epsilon; hence z in E k implies d of z, y is less than epsilon. Since x n is in E k if and only if n is greater than or equal to k, it is concluded that n greater than or equal to k naught implies d of x n, y is less than epsilon; this says that x n tends to y. This completes the proof.
