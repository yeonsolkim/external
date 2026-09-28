---
section: proof-theorem-3-4-7
title: Proof
kind: proof
document: 3.4 Limit Superior and Limit Inferior
url: /2026/09/12/4.-Limit-Superior-and-Limit-Inferior.html
source: eef5c18f6cf6223462af012eaae3c43e3041693f07d882af62dffc8cbf743bc7
skeleton: 4
prompt: lecture-v3
model: gpt-5.5
generated: 2026-09-28
body: ea87a3e17238908f25094f7dfd423294a2349a947bf39a76e1af3b25e4fefc54
words: 309
---

Proof. Suppose n is greater than or equal to N implies x n is less than or equal to y n. Let k be greater than or equal to N, and let s k equal the supremum of the set of x n such that n is greater than or equal to k, and s k prime equal the supremum of the set of y n such that n is greater than or equal to k. If n is greater than or equal to k, then x n is less than or equal to y n, which is less than or equal to s k prime. Hence s k prime is an upper bound for the set of x n such that n is greater than or equal to k, so

s k is less than or equal to s k prime.

It follows that the infimum over k greater than or equal to N of s k is less than or equal to s k, which is less than or equal to s k prime. Hence the infimum over k greater than or equal to N of s k is a lower bound for the set of s k prime such that k is greater than or equal to N, so the infimum over k greater than or equal to N of s k is less than or equal to the infimum over k greater than or equal to N of s k prime. By Definition 3.4.2,

the lim sup of x n equals the infimum over k greater than or equal to N of s k, which is less than or equal to the infimum over k greater than or equal to N of s k prime, which equals the lim sup of y n.

The proof of two is analogous to one. This completes the proof.
