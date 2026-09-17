---
section: theorem-3-4-7
title: Theorem 3.4.7
kind: theorem
document: 3.4. Upper and Lower Limits
url: /2026/09/12/4.-Upper-and-Lower-Limits.html
source: 2ff65f87a74d311b35f196dea985f9eb65c1cb25b8f7bf32ac4cf728a0c07529
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-17
body: d67fa2473487905b3d224cb4573b553d1e28181a8047930a8cac07f976bcb87a
words: 379
---

Theorem 3.4.7. Let x n and y n be sequences in R. If x n is less than or equal to y n eventually, then the following hold.

First, the limit superior of x n is less than or equal to the limit superior of y n. Second, the limit inferior of x n is less than or equal to the limit inferior of y n.

Proof. Suppose n is greater than or equal to N implies x n is less than or equal to y n. Let k be greater than or equal to N, and let s k equal the supremum of the set of x n such that n is greater than or equal to k, and s k prime equal the supremum of the set of y n such that n is greater than or equal to k. If n is greater than or equal to k, then x n is less than or equal to y n, which is less than or equal to s k prime. Hence s k prime is an upper bound for the set of x n such that n is greater than or equal to k, so we have s k is less than or equal to s k prime.

It follows that the infimum over k greater than or equal to N of s k is less than or equal to s k, which is less than or equal to s k prime. Hence the infimum over k greater than or equal to N of s k is a lower bound for the set of s k prime such that k is greater than or equal to N, so the infimum over k greater than or equal to N of s k is less than or equal to the infimum over k greater than or equal to N of s k prime. By Definition 3.4.2, the limit superior of x n equals the infimum over k greater than or equal to N of s k, which is less than or equal to the infimum over k greater than or equal to N of s k prime, which equals the limit superior of y n.

The proof of item two is analogous to item one. This completes the proof.
