---
section: theorem-3-1-6
title: Theorem 3.1.6
kind: theorem
document: 3.1 Convergent Sequences
url: /2026/08/31/1.-Convergent-Sequences.html
source: 579c2b5b809007aaba1e98cdd61f30e226ad75adadd37deb989c9c2ecaa8a0b9
skeleton: 3
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-19
body: 8913dcdb347db08eb86d9bda6299937d3592b370f39cc13232af1eefc037e89e
words: 723
---

Theorem 3.1.6. Suppose x n and y n are sequences in the complex numbers. If the limit as n tends to infinity of x n equals x and the limit as n tends to infinity of y n equals y, then the following hold:

First, the limit as n tends to infinity of x n plus y n equals x plus y.

Second, the limit as n tends to infinity of c x n equals c x for any c in the complex numbers.

Third, the limit as n tends to infinity of x n y n equals x y.

Fourth, if x n is not equal to zero and x is not equal to zero, then the limit as n tends to infinity of one over x n equals one over x.

Proof. For one, given epsilon greater than zero, there exist n naught x and n naught y in the positive integers such that n greater than or equal to n naught x implies the absolute value of x n minus x is less than epsilon over two, and n greater than or equal to n naught y implies the absolute value of y n minus y is less than epsilon over two.

If n naught equals the maximum of n naught x and n naught y, then n greater than or equal to n naught implies the absolute value of the quantity x n plus y n, minus the quantity x plus y, is less than or equal to the absolute value of x n minus x plus the absolute value of y n minus y, which is less than epsilon.

Since epsilon was arbitrary, one holds. For two, given epsilon greater than zero, there exists n naught in the positive integers such that n greater than or equal to n naught implies the absolute value of x n minus x is less than epsilon over the quantity the absolute value of c plus one.

Then, n greater than or equal to n naught implies the absolute value of c x n minus c x equals the absolute value of c times the absolute value of x n minus x, which is less than the absolute value of c over the quantity the absolute value of c plus one, times epsilon, which is less than epsilon.

Since epsilon was arbitrary, two holds. For three, given epsilon greater than zero, there exist n naught x and n naught y in the positive integers such that n greater than or equal to n naught x implies the absolute value of x n minus x is less than the square root of epsilon, and n greater than or equal to n naught y implies the absolute value of y n minus y is less than the square root of epsilon.

If n naught equals the maximum of n naught x and n naught y, then n greater than or equal to n naught implies the absolute value of the quantity x n minus x times the quantity y n minus y equals the absolute value of x n minus x times the absolute value of y n minus y, which is less than epsilon.

Thus we have the limit as n tends to infinity of the quantity x n minus x times the quantity y n minus y equals zero. It follows that the limit as n tends to infinity of x n y n minus x y equals the limit as n tends to infinity of the quantity the quantity x n minus x times the quantity y n minus y, plus x times the quantity y n minus y, plus y times the quantity x n minus x, which equals zero.

Therefore the limit as n tends to infinity of x n y n equals the limit as n tends to infinity of the quantity x n y n minus x y, plus x y, which equals x y.

For four, since the absolute value of one over x n minus one over x equals the absolute value of the fraction x n minus x, over x n x,

what we have to show is to ensure that the denominators x n stay uniformly away from zero. To do that, we first prove the following lemma, so-called the reverse triangle inequality.
