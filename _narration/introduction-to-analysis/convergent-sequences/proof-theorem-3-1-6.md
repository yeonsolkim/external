---
section: proof-theorem-3-1-6
title: Proof
kind: proof
document: 3.1 Convergent Sequences
url: /2026/08/31/1.-Convergent-Sequences.html
source: 2799f794970d911087e860207259bcf7470b62c8bf33f7470bad57bea17ecae3
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-07
body: edfd6378e4c27090ab83a98a1bd93b35e6e44d6b76d800f9f475312914cc8358
words: 588
---

Proof. One. Given epsilon greater than zero, there exist n naught x and n naught y in positive integers such that n greater than or equal to n naught x implies the absolute value of x n minus x is less than epsilon over two, and n greater than or equal to n naught y implies the absolute value of y n minus y is less than epsilon over two. If n naught equals the maximum of n naught x and n naught y, then n greater than or equal to n naught implies the absolute value of the difference between x n plus y n and x plus y is less than or equal to the absolute value of x n minus x, plus the absolute value of y n minus y, which is less than epsilon. Since epsilon was arbitrary, one holds.

Two. Given epsilon greater than zero, there exists n naught in positive integers such that n greater than or equal to n naught implies the absolute value of x n minus x is less than epsilon over the quantity the absolute value of c plus one. Then, n greater than or equal to n naught implies the absolute value of the quantity c x n minus c x equals the absolute value of c, times the absolute value of x n minus x, which is less than or equal to the absolute value of c over the quantity the absolute value of c plus one, times epsilon, which is less than epsilon. Since epsilon was arbitrary, two holds.

Three. Given epsilon greater than zero, there exist n naught x and n naught y in positive integers such that n greater than or equal to n naught x implies the absolute value of x n minus x is less than the square root of epsilon, and n greater than or equal to n naught y implies the absolute value of y n minus y is less than the square root of epsilon. If n naught equals the maximum of n naught x and n naught y, then n greater than or equal to n naught implies the absolute value of the product of x n minus x and y n minus y equals the absolute value of x n minus x, times the absolute value of y n minus y, which is less than epsilon. Thus we have the limit as n tends to infinity of the product of x n minus x and y n minus y equals zero. It follows that the limit as n tends to infinity of x n y n minus x y equals the limit as n tends to infinity of the quantity the product of x n minus x and y n minus y, plus x times the quantity y n minus y, plus y times the quantity x n minus x, equals zero. Therefore the limit as n tends to infinity of x n y n equals the limit as n tends to infinity of the quantity x n y n minus x y, plus x y, equals x y.

Four. Since the absolute value of the quantity one over x n minus one over x equals the absolute value of the fraction with numerator x n minus x and denominator x n times x, what we have to show is to ensure that the denominators x n stay uniformly away from zero. To do that, we first prove the following lemma, so-called the reverse triangle inequality.
