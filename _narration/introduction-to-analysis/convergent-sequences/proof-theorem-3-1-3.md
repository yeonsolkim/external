---
section: proof-theorem-3-1-3
title: Proof
kind: proof
document: 3.1 Convergent Sequences
url: /2026/08/31/1.-Convergent-Sequences.html
source: 775dcfe57ccef75b45ed69cfe6a9ca64f346d399ddba728ac1e2bd6c34336cb6
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-07
body: 8d4f6f5dac85b17aa37cdfaaf6da33df0754a3afdc650d428b202e4ad49fff6d
words: 459
---

Proof.

One. Suppose x n tends to x and let the ball of radius r about x be an open ball of x. Corresponding to this r, there exists n naught in the positive integers such that n is greater than or equal to n naught implies x n belongs to the ball of radius r about x. Conversely, suppose that every open ball of x contains x n for all but finitely many n. Fix r greater than zero and let n naught be greater than the maximum of the union of the singleton set zero and the set of n in the positive integers such that x n does not belong to the ball of radius r about x. Then n is greater than or equal to n naught implies x n belongs to the ball of radius r about x. Thus x n tends to x.

Two. Given epsilon greater than zero, there exist n naught x and n naught y in the positive integers such that n is greater than or equal to n naught x implies d of x n and x is less than epsilon over two, and n is greater than or equal to n naught y implies d of x n and y is less than epsilon over two. If n naught equals the maximum of the set n naught x and n naught y, then we have d of x and y is less than or equal to d of x n and x plus d of x n and y, which is less than epsilon. Since epsilon was arbitrary, we conclude that d of x and y equals zero; hence x equals y.

Three. Suppose x n tends to x. There exists n naught in the positive integers such that n is greater than n naught implies x n belongs to the ball of radius one about x. Put epsilon equal to the maximum of the set consisting of d of x one and x, and so on, up to d of x sub n naught and x, and then plus one. Then we have d of x n and x is less than epsilon for all n in the positive integers; hence x n is bounded.

Four. For each n in the positive integers, there is a point x n in A such that d of x n and x is less than one over n. Given epsilon greater than zero, choose n naught so that one over n naught is less than or equal to epsilon. Then, n is greater than or equal to n naught implies d of x n and x is less than epsilon; hence x n tends to x. This completes the proof.
