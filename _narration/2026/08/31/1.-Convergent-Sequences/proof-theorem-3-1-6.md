---
section: proof-theorem-3-1-6
title: Proof
kind: proof
document: 3.1 Convergent Sequences
url: /2026/08/31/1.-Convergent-Sequences.html
source: faabbc56ee90cc6a1901907025486ed55ad8cf8ec344b491985f18acc6e88b84
skeleton: 4
prompt: lecture-v3
model: gpt-5.5
generated: 2026-09-29
body: d3e7710142d992eb8fd9c1cd229f97ce4979047521d45149ac3f128df78a72eb
words: 588
---

Proof. Part one. Given epsilon greater than zero, there exist n naught x and n naught y in the positive integers such that

n greater than or equal to n naught x implies the absolute value of x n minus x is less than epsilon over two, and n greater than or equal to n naught y implies the absolute value of y n minus y is less than epsilon over two.

If n naught equals the maximum of n naught x and n naught y, then n greater than or equal to n naught implies

the absolute value of the quantity x n plus y n, minus the quantity x plus y, is less than or equal to the absolute value of x n minus x plus the absolute value of y n minus y, which is less than epsilon.

Since epsilon was arbitrary, part one holds. Part two. Given epsilon greater than zero, there exists n naught in the positive integers such that

n greater than or equal to n naught implies the absolute value of x n minus x is less than epsilon over the absolute value of c plus one.

Then, n greater than or equal to n naught implies

the absolute value of c x n minus c x equals the absolute value of c times the absolute value of x n minus x, which is less than the absolute value of c over the absolute value of c plus one, times epsilon, which is less than epsilon.

Since epsilon was arbitrary, part two holds. Part three. Given epsilon greater than zero, there exist n naught x and n naught y in the positive integers such that

n greater than or equal to n naught x implies the absolute value of x n minus x is less than the square root of epsilon, and n greater than or equal to n naught y implies the absolute value of y n minus y is less than the square root of epsilon.

If n naught equals the maximum of n naught x and n naught y, then n greater than or equal to n naught implies

the absolute value of the quantity x n minus x times the quantity y n minus y equals the absolute value of x n minus x times the absolute value of y n minus y, which is less than epsilon.

Thus we have the limit as n goes to infinity of the quantity x n minus x times the quantity y n minus y equals zero. It follows that

the limit as n goes to infinity of x n y n minus x y equals the limit as n goes to infinity of the quantity the quantity x n minus x times the quantity y n minus y, plus x times the quantity y n minus y, plus y times the quantity x n minus x, which equals zero.

Therefore

the limit as n goes to infinity of x n y n equals the limit as n goes to infinity of the quantity x n y n minus x y, plus x y, which equals x y.

Part four. Since

the absolute value of one over x n minus one over x equals the absolute value of the quantity x n minus x, over x n x,

what we have to show is to ensure that the denominators x n stay uniformly away from zero. To do that, we first prove the following lemma, so-called the reverse triangle inequality.
