---
section: proof-theorem-2-4-4
title: Proof
kind: proof
document: 2.4 Connected Sets
url: /2026/09/03/4.-Connected-Sets.html
source: eb1bdbb8c234b4d29ad900b01486f5fd8fc1e42cc6e54e15b2260b4b173640ed
skeleton: 4
prompt: lecture-v3
model: gpt-5.5
generated: 2026-09-28
body: be902a9a626338c6ba2f4e06d94d10a0ff1a9fa60a17092962b5c0adc4b5f1d1
words: 393
---

Proof. Suppose x and y are in A, x is less than z, which is less than y, and z is not in A. Define U equals the open interval from minus infinity to z intersect A, and V equals the open interval from z to infinity intersect A.

Then, A equals U disjoint union V. Since x is in U and y is in V, U and V are nonempty. By Theorem 2.1.18, U and V are open in A. Theorem 2.4.3 now shows that A is disconnected. We now prove the converse. Suppose, for contradiction, that A is disconnected and has the stated property. Then there are nonempty separated sets A one and A two such that A equals A one union A two. Let a one be in A one and a two be in A two, and assume, without loss of generality, that a one is less than a two. By the property, we have the closed interval from a one to a two is contained in A.

As we move from a one to a two, there must be a boundary between the two sets. To locate this boundary, define alpha equals the supremum of A one intersect the closed interval from a one to a two.

For all x in A, we have x in A one or x in A two. Thus alpha in the closed interval from x to y contained in A implies that alpha is in A one or alpha is in A two. If alpha is not in A one, then alpha is in A two. Since alpha is in the closure of A one, it follows that the closure of A one intersect A two is not equal to the empty set. This contradicts the separatedness. If alpha is in A one, then alpha is less than a two because a two is in A two. Since alpha is the supremum, the half-open interval from alpha to a two is not contained in A one, so that the half-open interval from alpha to a two is contained in A two. Therefore alpha is in the closure of A two, so that A one intersect the closure of A two is not equal to the empty set. The result is a contradiction once again. Therefore A is connected. This completes the proof.
