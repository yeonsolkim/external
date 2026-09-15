---
section: theorem-3-1-6
title: Theorem 3.1.6
kind: theorem
document: 3.1. Convergent Sequences
url: /2026/08/31/1.-Convergent-Sequences.html
source: d5d8f607df0f9f273834400e5a61c5b708a32b5437f22465c5ab924fd0f6127b
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-15
body: 28155bd9f9b3a13f0d1851aab5928c8488b3818f68e77dbdfa3fe2791819e13b
words: 729
---

Theorem 3.1.6. Suppose the sequence x n and the sequence y n are sequences in C. If the limit as n tends to infinity of x n equals x and the limit as n tends to infinity of y n equals y, then the following hold:

One, the limit as n tends to infinity of x n plus y n equals x plus y.

Two, the limit as n tends to infinity of c x n equals c x for any c in C.

Three, the limit as n tends to infinity of x n y n equals x y.

Four, if x n is not equal to zero and x is not equal to zero, then the limit as n tends to infinity of one over x n equals one over x.

Proof. One. Given epsilon greater than zero, there exist n sub zero x and n sub zero y in the positive integers such that

n greater than or equal to n sub zero x implies the absolute value of x n minus x is less than epsilon over two, and n greater than or equal to n sub zero y implies the absolute value of y n minus y is less than epsilon over two.

If n naught equals the maximum of n sub zero x and n sub zero y, then n greater than or equal to n naught implies

the absolute value of the quantity x n plus y n, minus the quantity x plus y, is less than or equal to the absolute value of x n minus x plus the absolute value of y n minus y, which is less than epsilon.

Since epsilon was arbitrary, one holds. Two. Given epsilon greater than zero, there exists n naught in the positive integers such that

n greater than or equal to n naught implies the absolute value of x n minus x is less than epsilon over the quantity the absolute value of c plus one.

Then, n greater than or equal to n naught implies

the absolute value of c x n minus c x equals the absolute value of c times the absolute value of x n minus x, which is less than the absolute value of c over the quantity the absolute value of c plus one, times epsilon, which is less than epsilon.

Since epsilon was arbitrary, two holds. Three. Given epsilon greater than zero, there exist n sub zero x and n sub zero y in the positive integers such that

n greater than or equal to n sub zero x implies the absolute value of x n minus x is less than the square root of epsilon, and n greater than or equal to n sub zero y implies the absolute value of y n minus y is less than the square root of epsilon.

If n naught equals the maximum of n sub zero x and n sub zero y, then n greater than or equal to n naught implies

the absolute value of the quantity x n minus x times the quantity y n minus y equals the absolute value of x n minus x times the absolute value of y n minus y, which is less than epsilon.

Thus we have the limit as n tends to infinity of the quantity x n minus x times the quantity y n minus y equals zero. It follows that

the limit as n tends to infinity of the quantity x n y n minus x y equals the limit as n tends to infinity of the quantity the quantity x n minus x times the quantity y n minus y, plus x times the quantity y n minus y, plus y times the quantity x n minus x, equals zero.

Therefore

the limit as n tends to infinity of x n y n equals the limit as n tends to infinity of the quantity x n y n minus x y, plus x y, equals x y.

Four. Since

the absolute value of one over x n minus one over x equals the absolute value of x n minus x over x n x,

what we have to show is to ensure that the denominators x n stay uniformly away from zero. To do that, we first prove the following lemma, so-called the reverse triangle inequality.
