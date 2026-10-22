---
section: proof-theorem-1-5-5
title: Proof
kind: proof
document: 1.5 Linear Dependence and Linear Independence
url: /2026/08/17/5.-Linear-Dependence-and-Linear-Independence.html
source: ec79a534a23e974b14e6c9702df5c245fb1232ad42227201135c66a2da49c761
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-19
body: f214bf490fe269894cf4df41ab590596bebf8dd0d0caac7cdcc0e09f17cbd227
words: 224
---

Proof. We show that S union the set consisting of v is linearly dependent if and only if v belongs to the span of S. Suppose that S union the set consisting of v is linearly dependent. By Proposition 1.5.3, there exists u in S union the set consisting of v such that u belongs to the span of the set S union the set consisting of v, with u removed.

If u equals v, then v belongs to the span of S. If u belongs to S, then u belongs to the span of the set S with u removed, union the set consisting of v.

Since S is linearly independent, Proposition 1.5.3 gives that u does not belong to the span of S with u removed.

Thus, by the Theorem 1.4.13, part one, v belongs to the span of the set S with u removed, union the set consisting of u, which equals the span of S.

Conversely, suppose that v belongs to the span of S. Then the span of S union the set consisting of v equals the span of S.

Since S equals S union the set consisting of v, with v removed, it follows from Definition 1.5.2 that S union the set consisting of v is linearly dependent. Taking negations yields the desired equivalence. This completes the proof.
