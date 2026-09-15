---
section: lemma-3-1-7
title: Lemma 3.1.7
kind: lemma
document: 3.1. Convergent Sequences
url: /2026/08/31/1.-Convergent-Sequences.html
source: dd4f65e2cffe9135d34d460384485b57a464c4d2de48cb664544170ec77c19e2
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-15
body: 8804e2bb25cf44df600812aab43bd656c76d19d9238e0497e8f10b904045921a
words: 457
---

Lemma 3.1.7. In a metric space M comma d, the following inequality holds:

d of x and y is greater than or equal to the absolute value of d of x and z minus d of y and z.

Subproof. If d of x and z is greater than or equal to d of y and z, let delta equal d of x and z minus d of y and z. In order that

d of x and y plus d of y and z is greater than or equal to d of x and z, which equals d of y and z plus delta,

d of x and y must be greater than or equal to delta. That is, d of x and y is greater than or equal to d of x and z minus d of y and z. If d of y and z is greater than or equal to d of x and z, in the same way, we have d of x and y is greater than or equal to d of y and z minus d of x and z. Therefore d of x and y is greater than or equal to the absolute value of d of x and z minus d of y and z. This proves the claim.

Since x is not equal to zero, we have d of x and zero is greater than zero. Then, there exists m in positive integers such that n is greater than or equal to m implies d of x n and x is less than one half times d of x and zero. By Lemma 3.1.7, the reverse triangle inequality, we obtain

d of x n and zero is greater than or equal to d of zero and x minus d of x n and x, which is greater than one half times d of zero and x,

whenever n is greater than or equal to m. Equivalently, the absolute value of x n is greater than one half times the absolute value of x. Given epsilon greater than zero, there is n naught greater than m such that n is greater than or equal to n naught implies

the absolute value of x n minus x is less than one half times the absolute value of x squared times epsilon.

Hence, if n is greater than or equal to n naught, then

the absolute value of one over x n minus one over x, equals the absolute value of x n minus x over x n times x, which is less than two over the absolute value of x squared, times the absolute value of x n minus x, which is less than epsilon. This completes the proof.
