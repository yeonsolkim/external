---
section: proof-theorem-1-3-18
title: Proof
kind: proof
document: 1.3 Linear Combinations and Spans
url: /2026/06/21/3.-Linear-Combinations-and-Spans.html
source: 5a11e5c7942b8528b9eb0d6dba23a84f8c3e7a393671bc9c71d732d62e9a73a0
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-11
body: f5e9aed585ba7fe0317b0ef968ec79240aabe589da648641ce9c754682217746
words: 209
---

Proof. First, suppose u belongs to span of S union the set containing v, but not to span of S.

By Corollary 1.3.15, there exist s in span of S and a in F such that u equals s plus a v.

Since span of S is a subspace and u does not belong to span of S, we must have a is not equal to zero and v does not belong to span of S. It follows that v equals a inverse times u minus a inverse times s, which belongs to span of S union the set containing u, which proves the forward implication. Since u and v were arbitrary, the same argument with their roles interchanged proves the backward implication.

Second, since u belongs to span of S union the set containing v, S union the set containing u is contained in span of S union the set containing v.

Since the right hand side is closed, Theorem 1.3.10 gives the inclusion span of S union the set containing u is contained in span of S union the set containing v.

The reverse inclusion follows similarly from v belongs to span of S union the set containing u. Therefore the equality holds. This completes the proof.
