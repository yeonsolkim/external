---
section: proof-theorem-1-3-18
title: Proof
kind: proof
document: 1.3 Linear Combinations and Spans
url: /2026/06/21/3.-Linear-Combinations-and-Spans.html
source: d22ba2616b3b5bb2c9a47a9b0f5a9c4894f79182823c2286389075d37b37a200
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-09
body: e46b18268051eadb521e1a0b5e86b08e6e9e1b3744e199a3e76933f54337fb34
words: 196
---

Proof. Suppose u belongs to span of the union of S with the singleton v, but not to span of S.

By Corollary 1.3.15, there exist s in span of S and a in F such that u equals s plus a times v.

Since u does not belong to span of S, we must have a is not equal to zero. It follows that v equals a to the minus one times u, minus a to the minus one times s, which belongs to span of the union of S with the singleton u.

We now prove the equality. Since u belongs to span of the union of S with the singleton v, we have S union the singleton u is contained in span of the union of S with the singleton v.

Since the right hand side is closed, Theorem 1.3.10 gives the inclusion span of the union of S with the singleton u is contained in span of the union of S with the singleton v.

The reverse inclusion follows similarly from v belongs to span of the union of S with the singleton u. Therefore the equality holds. This completes the proof.
