---
section: proof-theorem-3-4-7
title: Proof
kind: proof
document: 3.4 Limit Superior and Limit Inferior
url: /2026/09/12/4.-Limit-Superior-and-Limit-Inferior.html
source: eef5c18f6cf6223462af012eaae3c43e3041693f07d882af62dffc8cbf743bc7
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-09-29
body: 67be73777915cfeee9d34ef312f1b7af26a120269f9fa653bd823ed583663b1f
words: 277
---

Proof. Suppose n is greater than or equal to N implies x n is less than or equal to y n. Let k be greater than or equal to N, and let s k equal the supremum of the k-th tail and s k prime equal the supremum of the k-th tail of y. If n is greater than or equal to k, then x n is less than or equal to y n, which is less than or equal to s k prime. Hence s k prime is an upper bound for the k-th tail, so s k is less than or equal to s k prime.

It follows that the infimum over k greater than or equal to N of s k is less than or equal to s k, which is less than or equal to s k prime. Hence the infimum over k greater than or equal to N of s k is a lower bound for the set of s k prime such that k is greater than or equal to N, so the infimum over k greater than or equal to N of s k is less than or equal to the infimum over k greater than or equal to N of s k prime. By Definition 3.4.2, the lim sup of x n equals the infimum over k greater than or equal to N of s k, which is less than or equal to the infimum over k greater than or equal to N of s k prime, which equals the lim sup of y n.

The proof of part two is analogous to part one. This completes the proof.
