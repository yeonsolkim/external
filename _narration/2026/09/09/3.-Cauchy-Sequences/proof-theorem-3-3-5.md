---
section: proof-theorem-3-3-5
title: Proof
kind: proof
document: 3.3 Cauchy Sequences
url: /2026/09/09/3.-Cauchy-Sequences.html
source: 3497431e543fc0f86a9ee845395812a3d525c017cdcd3001eb7db951bd5cd2f0
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-06
body: 3a92c9795e2bda111759794290497f20ed92efd63afe3c8854f08c1ba3b4f9c8
words: 341
---

Proof. One. Suppose the sequence x n converges to x in M and let epsilon greater than zero be given. Then, there is n naught in the positive integers such that n greater than or equal to n naught implies d of x n and x is less than epsilon over two. By the triangle inequality, it follows that m and n greater than or equal to n naught implies d of x m and x n is less than epsilon. Hence the sequence x n is a Cauchy sequence.

Two. Let E k equal the set of x n such that n is greater than or equal to k. Then Theorem 3.3.3 and Lemma 3.3.4 part one gives the limit as k tends to infinity of the diameter of the closure of E k equals zero. Since M is compact, by Theorem 2.2.7, the closure of E k is compact. Since E sub k plus one is contained in E k, we also have the closure of E sub k plus one is contained in the closure of E k. Lemma 3.3.4 part two now shows that there is a unique point y in the intersection from k equals one to infinity of the closure of E k. Let epsilon greater than zero be given. Then, there is k naught in the positive integers such that k greater than or equal to k naught implies the diameter of the closure of E k is less than epsilon. Since y is in the closure of E k, if z is in the closure of E k then d of z and y is less than epsilon; hence z in E k implies d of z and y is less than epsilon. Since n greater than or equal to k implies x n is in E k, it is concluded that n greater than or equal to k naught implies d of x n and y is less than epsilon; this says that x n tends to y. This completes the proof.
