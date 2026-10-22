---
section: proof-theorem-1-6-5
title: Proof
kind: proof
document: 1.6 Linear Dependence and Linear Independence
url: /linear-algebra/linear-dependence-and-linear-independence/
source: 08337801e1d26d3808d1f057d78c0be24edd169b0ae138888e909ce06f01c63e
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-22
body: 55bfb0406c77757e878a39a8e9569f35c5f606ee1d5478f50750eff56dfa985c
words: 207
---

Proof. We show that S union the singleton v is linearly dependent if and only if v belongs to the span of S. Suppose that S union the singleton v is linearly dependent. By Proposition 1.6.3, there exists u in S union the singleton v such that u belongs to the span of the set obtained from S union the singleton v by removing u.

If u equals v, then v belongs to the span of S. If u belongs to S, then u belongs to the span of the set S with u removed, union the singleton v.

Since S is linearly independent, Proposition 1.6.3 gives u does not belong to the span of S with u removed.

Thus, by the Theorem 1.5.13, part one, v belongs to the span of the set S with u removed, union the singleton u, which equals the span of S.

Conversely, suppose that v belongs to the span of S. Then the span of S union the singleton v equals the span of S.

Since S equals S union the singleton v, with v removed, it follows from Definition 1.6.2 that S union the singleton v is linearly dependent. Taking negations yields the desired equivalence. This completes the proof.
