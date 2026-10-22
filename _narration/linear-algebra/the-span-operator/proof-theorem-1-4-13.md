---
section: proof-theorem-1-4-13
title: Proof
kind: proof
document: 1.4 The Span Operator
url: /2026/10/14/4.-The-Span-Operator.html
source: fe1edde43dec0b587aad8cc961afa27bc2a1ee18d3ab353bcc863827b95faaf8
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-19
body: 5fb0ad2fde48975c1bb386659d29c708f7f2130ef93b81f3055bdf1d84847a79
words: 221
---

Proof. First, suppose u belongs to span of S union the set containing v, and u does not belong to span of S. By Corollary 1.4.10, there exist s belonging to span of S and a belonging to F such that u equals s plus a times v. Since span of S is a subspace and u does not belong to span of S, we must have a is not equal to zero and v does not belong to span of S. It follows that v equals a to the minus one times u, minus a to the minus one times s, which belongs to span of S union the set containing u, which proves the forward implication. Since u and v were arbitrary, the same argument with their roles interchanged proves the backward implication.

Second, since u belongs to span of S union the set containing v, S union the set containing u is contained in span of S union the set containing v. Since the right hand side is closed, Theorem 1.4.4 gives the inclusion span of S union the set containing u is contained in span of S union the set containing v. The reverse inclusion follows similarly from v belongs to span of S union the set containing u. Therefore the equality holds. This completes the proof.
