---
section: theorem-3-1-3
title: Theorem 3.1.3
kind: theorem
document: 3.1. Convergent Sequences
url: /2026/08/31/1.-Convergent-Sequences.html
source: 59d0312dc2d648a5e6c6c4b9feaa14334a905ffc1b601826706bfeb1570488dd
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-15
body: a32d96fe93b6a32d83157cdf212f5fe0ed19f50375c11ac3a63121094f0fd145
words: 566
---

Theorem 3.1.3. Let the sequence x n be a sequence in a metric space M.

Property one: the sequence x n converges to x in M if and only if every open ball centered at x contains x n for all but finitely many n.

Property two: for x and y in M, if the sequence x n converges to x and to y, then x equals y.

Property three: if the sequence x n converges in M, then the sequence x n is bounded.

Property four: if x in M is a limit point of A contained in M, then there exists a sequence x n in A that converges to x.

Proof. For property one, suppose the sequence x n tends to x and let the ball of radius r about x be an open ball of x. Corresponding to this r, there exists n naught in the positive integers such that n is greater than or equal to n naught implies x n belongs to the ball of radius r about x. Conversely, suppose that every open ball of x contains x n for all but finitely many n. Fix r greater than zero and let n naught be greater than the maximum of the set of n in the positive integers such that x n does not belong to the ball of radius r about x.

Then n is greater than or equal to n naught implies x n belongs to the ball of radius r about x. Thus x n tends to x.

For property two, given epsilon greater than zero, there exist n sub zero x and n sub zero y in the positive integers such that n is greater than or equal to n sub zero x implies d of x n, x is less than epsilon over two, and n is greater than or equal to n sub zero y implies d of x n, y is less than epsilon over two.

If n naught equals the maximum of the set containing n sub zero x and n sub zero y, then we have d of x, y is less than or equal to d of x n, x plus d of x n, y, which is less than epsilon.

Since epsilon was arbitrary, we conclude that d of x, y equals zero; hence x equals y.

For property three, suppose x n tends to x. There exists n naught in the positive integers such that n is greater than n naught implies x n belongs to the unit ball about x. Put epsilon equal to the maximum of the set containing d of x one, x, and so on up to d of x n naught, x, plus one.

Then we have d of x n, x is less than epsilon for all n in the positive integers; hence the sequence x n is bounded.

For property four, for each n in the positive integers, there is a point x n in A such that d of x n, x is less than one over n. Given epsilon greater than zero, choose n naught so that one over n naught is less than or equal to epsilon. Then, n is greater than or equal to n naught implies d of x n, x is less than epsilon; hence x n tends to x. This completes the proof.
