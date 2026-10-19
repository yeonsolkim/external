---
section: proof-corollary-1-5-7
title: Proof
kind: proof
document: 1.5 Linear Dependence and Linear Independence
url: /2026/08/17/5.-Linear-Dependence-and-Linear-Independence.html
source: 7f7ab6bab8c1a12c77843827f14b6a7570dd2a1a68575372de456ab4aa9191c7
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-19
body: 68beb2531082e545a9be5dfbd9ab81b200e0dff6db255cc677df18febce03fd5
words: 233
---

Proof. Suppose that S is linearly independent, and let a and b from S to F be representations of the same vector v in V. Put K equal to the support of a union the support of b, and define d from S to F by d of s equals a of s minus b of s. Then the support of d is contained in K is finite. By Proposition 1.3.3, the sum over s in the support of d of d of s times s, equals the sum over s in K of the quantity a of s minus b of s, times s, which equals the sum over s in the support of a of a of s times s, minus the sum over s in the support of b of b of s times s, which equals v minus v, which equals zero vector in V.

Thus d is a representation of zero vector in V in terms of S. Since S is linearly independent, Theorem 1.5.6 implies that the support of d equals the empty set. Hence a equals b. Conversely, suppose that every vector has at most one representation in terms of S. The zero function from S to F is a representation of zero vector in V, so it is the only such representation. Theorem 1.5.6 therefore implies that S is linearly independent. This completes the proof.
