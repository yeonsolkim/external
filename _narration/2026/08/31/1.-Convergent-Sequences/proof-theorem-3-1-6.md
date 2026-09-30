---
section: proof-theorem-3-1-6
title: Proof
kind: proof
document: 3.1 Convergent Sequences
url: /2026/08/31/1.-Convergent-Sequences.html
source: 001c578c4ce0e1920c1497872feb503f1b512e17876d8db864fb41ccaee42d27
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-09-30
body: cc4fc3eff029afbb10160d1babee740092bdcc5c0224a8979a4d34607964fbe8
words: 601
---

Proof. Part one. Given epsilon greater than zero, there exist n sub zero x and n sub zero y in the positive integers such that n greater than or equal to n sub zero x implies the absolute value of x n minus x is less than epsilon over two, and n greater than or equal to n sub zero y implies the absolute value of y n minus y is less than epsilon over two.

If n naught equals the maximum of n sub zero x and n sub zero y, then n greater than or equal to n naught implies the absolute value of the quantity x n plus y n, minus the quantity x plus y, is less than or equal to the absolute value of x n minus x, plus the absolute value of y n minus y, which is less than epsilon.

Since epsilon was arbitrary, part one holds.

Part two. Given epsilon greater than zero, there exists n naught in the positive integers such that n greater than or equal to n naught implies the absolute value of x n minus x is less than epsilon over the quantity absolute value of c plus one.

Then, n greater than or equal to n naught implies the absolute value of c x n minus c x equals the absolute value of c times the absolute value of x n minus x, which is less than or equal to the absolute value of c, over the quantity absolute value of c plus one, times epsilon, which is less than epsilon.

Since epsilon was arbitrary, part two holds.

Part three. Given epsilon greater than zero, there exist n sub zero x and n sub zero y in the positive integers such that n greater than or equal to n sub zero x implies the absolute value of x n minus x is less than the square root of epsilon, and n greater than or equal to n sub zero y implies the absolute value of y n minus y is less than the square root of epsilon.

If n naught equals the maximum of n sub zero x and n sub zero y, then n greater than or equal to n naught implies the absolute value of the product of x n minus x and y n minus y equals the absolute value of x n minus x times the absolute value of y n minus y, which is less than epsilon.

Thus we have the limit as n goes to infinity of the quantity x n minus x times the quantity y n minus y equals zero. It follows that the limit as n goes to infinity of the quantity x n y n minus x y equals the limit as n goes to infinity of the quantity the product of x n minus x and y n minus y, plus x times the quantity y n minus y, plus y times the quantity x n minus x, equals zero.

Therefore the limit as n goes to infinity of x n y n equals the limit as n goes to infinity of the quantity x n y n minus x y, plus x y, equals x y.

Part four. Since the absolute value of one over x n, minus one over x, equals the absolute value of x n minus x, over x n x, what we have to show is to ensure that the denominators x n stay uniformly away from zero. To do that, we first prove the following lemma, so-called the reverse triangle inequality.
