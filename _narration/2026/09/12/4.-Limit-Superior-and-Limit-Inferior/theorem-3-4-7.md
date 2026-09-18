---
section: theorem-3-4-7
title: Theorem 3.4.7
kind: theorem
document: 3.4. Limit Superior and Limit Inferior
url: /2026/09/12/4.-Limit-Superior-and-Limit-Inferior.html
source: 2ff65f87a74d311b35f196dea985f9eb65c1cb25b8f7bf32ac4cf728a0c07529
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-18
body: 91adad4566c683020e99f1552acb6bff1e2554d6eb1297525d44b86a9b785b3f
words: 334
---

Theorem 3.4.7. Let x n and y n be sequences in R. If x n is less than or equal to y n eventually, then the following hold.

One, lim sup of x n is less than or equal to lim sup of y n.

Two, lim inf of x n is less than or equal to lim inf of y n.

Proof. Suppose n greater than or equal to N implies x n is less than or equal to y n. Let k be greater than or equal to N, and let s k equal the supremum of the k-th tail and s k prime equal the supremum of the k-th tail of y. If n is greater than or equal to k then x n is less than or equal to y n, which is less than or equal to s k prime. Hence s k prime is an upper bound for the k-th tail, so

s k is less than or equal to s k prime.

It follows that the infimum over k greater than or equal to N of s k is less than or equal to s k, which is less than or equal to s k prime. Hence the infimum over k greater than or equal to N of s k is a lower bound for the set of s k prime such that k is greater than or equal to N, so the infimum over k greater than or equal to N of s k is less than or equal to the infimum over k greater than or equal to N of s k prime. By Definition 3.4.2,

lim sup of x n equals the infimum over k greater than or equal to N of s k, which is less than or equal to the infimum over k greater than or equal to N of s k prime, which equals lim sup of y n.

The proof of two is analogous to one. This completes the proof.
