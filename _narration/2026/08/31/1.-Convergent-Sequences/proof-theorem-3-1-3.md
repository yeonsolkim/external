---
section: proof-theorem-3-1-3
title: Proof
kind: proof
document: 3.1 Convergent Sequences
url: /2026/08/31/1.-Convergent-Sequences.html
source: a75cd48f2a3c1faa7a284adfddebd5ed0e7d0a58f0a3a4a3920ec7193f6e021c
skeleton: 4
prompt: lecture-v3
model: gpt-5.5
generated: 2026-09-29
body: f1c6c7adc32ac259b697f95c09ad36620797d160a46f232e376a938db4b0dea0
words: 444
---

Proof. First, suppose x n goes to x and let the ball of radius r about x be an open ball of x. Corresponding to this r, there exists n naught in positive integers such that n is greater than or equal to n naught implies x n belongs to the ball of radius r about x. Conversely, suppose that every open ball of x contains x n for all but finitely many n. Fix r greater than zero and let

n naught be greater than the maximum of the set of n in positive integers such that x n does not belong to the ball of radius r about x.

Then n is greater than or equal to n naught implies x n belongs to the ball of radius r about x. Thus x n goes to x.

Second, given epsilon greater than zero, there exist n sub naught x and n sub naught y in positive integers such that

n is greater than or equal to n sub naught x implies d of x n and x is less than epsilon over two, and n is greater than or equal to n sub naught y implies d of x n and y is less than epsilon over two.

If n naught equals the maximum of the set n sub naught x and n sub naught y, then we have

d of x and y is less than or equal to d of x n and x plus d of x n and y, which is less than epsilon.

Since epsilon was arbitrary, we conclude that d of x and y equals zero; hence x equals y.

Third, suppose x n goes to x. There exists n naught in positive integers such that n is greater than n naught implies x n belongs to the unit ball about x. Put

epsilon equals the maximum of the set d of x one and x, and so on up to d of x sub n naught and x, plus one.

Then we have d of x n and x is less than epsilon for all n in positive integers; hence x n is bounded.

Fourth, for each n in positive integers, there is a point x n in A such that d of x n and x is less than one over n. Given epsilon greater than zero, choose n naught so that one over n naught is less than or equal to epsilon. Then, n is greater than or equal to n naught implies d of x n and x is less than epsilon; hence x n goes to x. This completes the proof.
