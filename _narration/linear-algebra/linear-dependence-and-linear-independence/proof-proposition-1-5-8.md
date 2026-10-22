---
section: proof-proposition-1-5-8
title: Proof
kind: proof
document: 1.5 Linear Dependence and Linear Independence
url: /2026/08/17/5.-Linear-Dependence-and-Linear-Independence.html
source: 1fbc8cc3bbd003b686a5c3d87c9a435e3de585c3344b78a1b6d0e96cd6adb943
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-19
body: c798e0bcb62794c96a5592b691fd793462c0cd18ab1097c9dc42c2824abc223c
words: 276
---

Proof. Part one. Suppose that zero vector in V belongs to S and define a from S to F by a of t equals one if t equals zero vector in V, and zero if t is not equal to zero vector in V. Then the support of a equals the set containing zero vector in V and the sum over t in the support of a of a of t times t equals one times zero vector in V, which equals zero vector in V. Since zero vector in V belongs to the support of a, S is linearly dependent by Theorem 1.5.6.

Part two. If v belongs to V has a representation in terms of the empty set, then it is the empty function. Hence, by Corollary 1.5.7, the empty set is linearly independent.

Part three. Suppose that S equals the set containing v with v not equal to zero vector in V, and let a from S to F be a representation of zero vector in V. If the support of a is not equal to the empty set, then a of v is not equal to zero. Hence we have the sum over s in the support of a of a of s times s equals the sum over s in the set containing v of a of s times s, which equals a of v times v, which is not equal to zero vector in V, which contradicts the fact that a is a representation of zero vector in V. Thus the support of a equals the empty set, so S is linearly independent by Theorem 1.5.6. This completes the proof.
