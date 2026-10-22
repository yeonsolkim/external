---
section: proof-theorem-3-3-5
title: Proof
kind: proof
document: 3.3 Cauchy Sequences
url: /2026/09/09/3.-Cauchy-Sequences.html
source: 7e2026b21cc38301e0173bcdcf912f2a3b9d27fbc7d87d9d1120b3836cf0a2d6
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-08
body: f10e57e6b0d5df246352a1eb846e529154205028c8e35b86b1de138bcc8408fc
words: 337
---

Proof. One. Suppose x n converges to x in M and let epsilon greater than zero be given. Then, there is n naught in the positive integers such that n greater than or equal to n naught implies d of x n and x is less than epsilon over two. By the triangle inequality, it follows that m and n greater than or equal to n naught implies d of x m and x n is less than epsilon. Hence x n is a Cauchy sequence.

Two. Let E k equal the set of x n such that n is greater than or equal to k. Then Theorem 3.3.3 and Lemma 3.3.4 part one give the limit as k tends to infinity of the diameter of the closure of E k equals zero. Since M is compact, by Theorem 2.2.7, the closure of E k is compact. Since E sub k plus one is contained in E k, we also have the closure of E sub k plus one is contained in the closure of E k. Lemma 3.3.4 part two now shows that there is a unique point y in the intersection over k from one to infinity of the closure of E k. Let epsilon greater than zero be given. Then, there is k naught in the positive integers such that k greater than or equal to k naught implies the diameter of the closure of E k is less than epsilon. Since y is in the closure of E k, if z is in the closure of E k then d of z and y is less than epsilon; hence z in E k implies d of z and y is less than epsilon. Since n greater than or equal to k implies x n is in E k, it is concluded that n greater than or equal to k naught implies d of x n and y is less than epsilon; this says that x n tends to y. This completes the proof.
