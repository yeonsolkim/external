---
section: proof-theorem-1-5-13
title: Proof
kind: proof
document: 1.5 The Span Operator
url: /linear-algebra/the-span-operator/
source: b4d3247a7a6570a3399e20686c6cfd19224acb119a79ec6ec19e75d2edd585d3
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-22
body: fea964f3a519ad321a3bf37a345dce5a9f8fa06f9e89ef741bd1c569b73af1f3
words: 213
---

Proof. First, suppose u belongs to the span of S union the singleton v, set minus the span of S.

By Corollary 1.5.10, there exist s in the span of S and a in F such that u equals s plus a times v.

Since the span of S is a subspace and u does not belong to the span of S, we must have a is not equal to zero and v does not belong to the span of S. It follows that v equals a inverse times u minus a inverse times s, which belongs to the span of S union the singleton u, which proves the forward implication. Since u and v were arbitrary, the same argument with their roles interchanged proves the backward implication.

Second, since u belongs to the span of S union the singleton v, S union the singleton u is contained in the span of S union the singleton v.

Since the right hand side is closed, Theorem 1.5.4 gives the inclusion the span of S union the singleton u is contained in the span of S union the singleton v.

The reverse inclusion follows similarly from v belongs to the span of S union the singleton u. Therefore the equality holds. This completes the proof.
