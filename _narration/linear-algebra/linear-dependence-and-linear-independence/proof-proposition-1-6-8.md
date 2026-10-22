---
section: proof-proposition-1-6-8
title: Proof
kind: proof
document: 1.6 Linear Dependence and Linear Independence
url: /linear-algebra/linear-dependence-and-linear-independence/
source: 88ae00db8a127bf221e6c73132fa4142b55cb92ea9af9008ce99425b550a5136
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-22
body: a1da28696763a93249f3af35326c5ed2521f3ad4cae2e5d1f1d7db7354c8d07d
words: 286
---

Proof. One. Suppose that the zero vector in V belongs to S and define a from S to F by a of t equals one if t equals the zero vector in V, and zero if t is not equal to the zero vector in V. Then the support of a equals the singleton set containing the zero vector in V, and the sum over t in the support of a of a of t times t equals one times the zero vector in V, which equals the zero vector in V. Since the zero vector in V belongs to the support of a, S is linearly dependent by Theorem 1.6.6.

Two. If v in V has a representation in terms of the empty set, then it is the empty function. Hence, by Corollary 1.6.7, the empty set is linearly independent.

Three. Suppose that S equals the singleton set containing v, with v not equal to the zero vector in V, and let a from S to F be a representation of the zero vector in V. If the support of a is not equal to the empty set, then a of v is not equal to zero. Hence we have the sum over s in the support of a of a of s times s equals the sum over s in the singleton set containing v of a of s times s, which equals a of v times v, which is not equal to the zero vector in V, which contradicts the fact that a is a representation of the zero vector in V. Thus the support of a equals the empty set, so S is linearly independent by Theorem 1.6.6. This completes the proof.
