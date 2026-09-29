---
section: proof-theorem-3-3-5
title: Proof
kind: proof
document: 3.3 Cauchy Sequences
url: /2026/09/09/3.-Cauchy-Sequences.html
source: 360e3936b13b7ba7b469a59f66776133b202af7bc3efd6f7e805125a50cfe712
skeleton: 4
prompt: lecture-v3
model: gpt-5.5
generated: 2026-09-29
body: c0cff539bc71a3083e380ccb154ef8e6c144a5d393608ee7df31bd1d19bf0db3
words: 336
---

Proof. One. Suppose x n converges to x in M and let epsilon greater than zero be given. Then, there is n naught in the positive integers such that n greater than or equal to n naught implies d of x n and x is less than epsilon over two. By the triangle inequality, it follows that m and n greater than or equal to n naught implies d of x m and x n is less than epsilon.

Hence x n is a Cauchy sequence. Two. Let E k equal the set of x n such that n is greater than or equal to k. Then Theorem 3.3.3 and part one of Lemma 3.3.4 gives the limit as k tends to infinity of the diameter of the closure of E k equals zero.

Since M is compact, by Theorem 2.2.7, closure of E k is compact. Since E k plus one is contained in E k, we also have closure of E k plus one is contained in closure of E k. Part two of Lemma 3.3.4 now shows that there is a unique point y in the intersection from k equals one to infinity of closure of E k. Let epsilon greater than zero be given. Then, there is k naught in the positive integers such that k greater than or equal to k naught implies the diameter of the closure of E k is less than epsilon. Since y belongs to closure of E k, if z belongs to closure of E k then d of z and y is less than epsilon; hence z belongs to E k implies d of z and y is less than epsilon. Since x n belongs to E k if and only if n is greater than or equal to k, it is concluded that n greater than or equal to k naught implies d of x n and y is less than epsilon; this says that x n tends to y. This completes the proof.
