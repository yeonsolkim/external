---
section: theorem-3-3-5
title: Theorem 3.3.5
kind: theorem
document: 3.3 Cauchy Sequences
url: /2026/09/09/3.-Cauchy-Sequences.html
source: e6c1fb8405230bf3c53f27a39b589328167bc2c90af41df9fa7471e1acea29c6
skeleton: 3
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-19
body: 7a5f4141738df61498feec4a59a6105b7855cb470817e8102c4999ef3033e9f1
words: 392
---

Theorem 3.3.5. Let the sequence x n be a sequence in a metric space M.

One. If the sequence x n converges in M, then the sequence x n is a Cauchy sequence.

Two. If M is compact and the sequence x n is a Cauchy sequence, then the sequence x n converges in M.

Proof. One. Suppose the sequence x n converges to x in M and let epsilon greater than zero be given. Then, there is n naught in the positive integers such that n greater than or equal to n naught implies d of x n and x is less than epsilon over two. By the triangle inequality, it follows that m and n greater than or equal to n naught implies d of x m and x n is less than epsilon.

Hence the sequence x n is a Cauchy sequence. Two. Let E k equal the set of x n such that n is greater than or equal to k. Then Theorem 3.3.3 and part one of Lemma 3.3.4 gives the limit as k tends to infinity of the diameter of closure of E k equals zero.

Since M is compact, by Theorem 2.2.7, closure of E k is compact. Since E k plus one is contained in E k, we also have closure of E k plus one is contained in closure of E k. Part two of Lemma 3.3.4 now shows that there is a unique point y in the intersection from k equals one to infinity of closure of E k. Let epsilon greater than zero be given. Then, there is k naught in the positive integers such that k greater than or equal to k naught implies the diameter of closure of E k is less than epsilon. Since y is in closure of E k, if z is in closure of E k then d of z and y is less than epsilon; hence z in E k implies d of z and y is less than epsilon. Since x n is in E k if and only if n is greater than or equal to k, it is concluded that n greater than or equal to k naught implies d of x n and y is less than epsilon; this says that x n tends to y. This completes the proof.
