---
section: theorem-3-1-8
title: Theorem 3.1.8
kind: theorem
document: 3.1. Convergent Sequences
url: /2026/08/31/1.-Convergent-Sequences.html
source: f8e4c9c70892ac9ccbfc6f510e4789140a9bf10cc71e8a2b6f97162a51479ed5
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-15
body: 6a628ebba09c05ecad8933e7f661cb97a54e605eab53e71c1c74a2e9436a9e43
words: 346
---

Theorem 3.1.8. Suppose x n is a sequence in R k and x n equals x one n through x k n. Then, x n converges to x equals x one through x k if and only if the limit as n tends to infinity of x i n equals x i, for i equals one, two, and so on up to k.

Proof. Suppose x n tends to x. From the definition of the norm in R k, we have the absolute value of x i n minus x i is less than or equal to the norm of x n minus x, for each i equals one, two, and so on up to k and n in the positive integers. Hence, given epsilon greater than zero, there exists n naught in the positive integers such that n is greater than or equal to n naught implies the absolute value of x i n minus x i is less than epsilon. Therefore x i n tends to x i for each i equals one, two, and so on up to k. Conversely, suppose x i n tends to x i for each i equals one, two, and so on up to k. Given epsilon greater than zero, there exists n naught sub i in the positive integers such that n is greater than or equal to n naught sub i implies the absolute value of x i n minus x i is less than epsilon over the square root of k, for each i equals one, two, and so on up to k. Put n naught equal to the maximum of the set n naught sub one through n naught sub k. Then n is greater than or equal to n naught implies the norm of x n minus x equals the quantity the sum from i equals one to k of the absolute value of x i n minus x i squared, to the one half, which is less than epsilon. Since epsilon was arbitrary, x n tends to x. This completes the proof.
