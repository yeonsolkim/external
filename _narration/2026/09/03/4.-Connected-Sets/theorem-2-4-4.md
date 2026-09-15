---
section: theorem-2-4-4
title: Theorem 2.4.4
kind: theorem
document: 2.4. Connected Sets
url: /2026/09/03/4.-Connected-Sets.html
source: 47f92c7f5c8222c9c78c5b07793a4761179227e6d7230f22123f5ec949b04570
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-15
body: 4f724d33e8a2f41088c68cbf15781d59fa6567a3c8b260f9085cf81dfb84d6e5
words: 436
---

Theorem 2.4.4. A subset A of R is connected if and only if it has the following property: x and y belong to A, and x is less than z, which is less than y, implies that z belongs to A.

Proof. Suppose x and y belong to A, x is less than z, which is less than y, and z does not belong to A. Define U equals the open interval from negative infinity to z, intersected with A, and V equals the open interval from z to infinity, intersected with A.

Then, A equals U disjoint union V. Since x belongs to U and y belongs to V, U and V are nonempty. By Theorem 2.1.18, U and V are open in A. Theorem 2.4.3 now shows that A is disconnected.

We now prove the converse. Suppose, for contradiction, that A is disconnected and has the stated property. Then there are nonempty separated sets A one and A two such that A equals A one union A two. Let a one belong to A one and a two belong to A two, and assume, without loss of generality, that a one is less than a two. By the property, we have the closed interval from a one to a two is contained in A.

As we move from a one to a two, there must be a boundary between the two sets. To locate this boundary, define alpha equals the supremum of A one intersected with the closed interval from a one to a two.

For all x in A, we have x in A one or x in A two. Thus alpha belongs to the closed interval from x to y, which is contained in A, implies that alpha belongs to A one or alpha belongs to A two. If alpha does not belong to A one, then alpha belongs to A two. Since alpha belongs to the closure of A one, it follows that the closure of A one intersected with A two is not empty. This contradicts the separatedness. If alpha belongs to A one, then alpha is less than a two because a two belongs to A two. Since alpha is the supremum, the half-open interval from alpha to a two is not contained in A one, so that the half-open interval from alpha to a two is contained in A two. Therefore alpha belongs to the closure of A two, so that A one intersected with the closure of A two is not empty. The result is a contradiction once again. Therefore A is connected. This completes the proof.
