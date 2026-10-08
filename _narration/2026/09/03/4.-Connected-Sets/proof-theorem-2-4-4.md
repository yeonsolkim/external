---
section: proof-theorem-2-4-4
title: Proof
kind: proof
document: 2.4 Connected Sets
url: /2026/09/03/4.-Connected-Sets.html
source: 5ecc215b1d50abbdc87e33f7689fc0a8dae2070d256968577488119f1d51d9fc
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-07
body: df1ea0a066c8a1e29702db6c68f9ffb3cfd5e83cb105d58489748ba8c10890a0
words: 419
---

Proof. Suppose x and y are in A, x is less than z, which is less than y, and z is not in A. Define U equals the open interval from minus infinity to z, intersect A, and V equals the open interval from z to infinity, intersect A. Then, A equals the disjoint union of U and V. Since x belongs to U and y belongs to V, U and V are nonempty. By Theorem 2.1.18, U and V are open in A. Theorem 2.4.3 now shows that A is disconnected. We now prove the converse. Suppose, for contradiction, that A is disconnected and has the stated property. Then there are nonempty separated sets A one and A two such that A equals A one union A two. Let a one belong to A one and a two belong to A two, and assume, without loss of generality, that a one is less than a two. By the property, we have the closed interval from a one to a two is contained in A. As we move from a one to a two, there must be a boundary between the two sets. To locate this boundary, define alpha equals the supremum of A one intersect the closed interval from a one to a two. For all x in A, we have x belongs to A one or x belongs to A two. Thus alpha belongs to the closed interval from a one to a two, which is contained in A, implies that alpha belongs to A one or alpha belongs to A two. If alpha does not belong to A one, then alpha belongs to A two. Since alpha belongs to the closure of A one, it follows that the closure of A one intersect A two is not equal to the empty set. This contradicts the separatedness. If alpha belongs to A one, then alpha is less than a two because a two belongs to A two. Since alpha is the supremum, the interval from alpha to a two, open at alpha and closed at a two, intersect A one, equals the empty set, so that the interval from alpha to a two, open at alpha and closed at a two, is contained in A two. Therefore alpha belongs to the closure of A two, so that A one intersect the closure of A two is not equal to the empty set. The result is a contradiction once again. Therefore A is connected. This completes the proof.
