---
section: proof-corollary-1-6-7
title: Proof
kind: proof
document: 1.6 Linear Dependence and Linear Independence
url: /linear-algebra/linear-dependence-and-linear-independence/
source: a1f09c575b58130e0de32c0625df71cde493838e9ebad523ebca5313f2dba4f8
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-22
body: 4a0fa60bd6a614286fd22986a1974132993f2c6ff542a78c7815fb4c3dc279d8
words: 228
---

Proof. Suppose that S is linearly independent, and let a and b from S to F be representations of the same vector v in V. Put K equals support of a union support of b and define d from S to F by d of s equals a of s minus b of s. Then support of d is contained in K is finite. By Proposition 1.4.3, the sum over s in support of d of d of s times s equals the sum over s in K of the quantity a of s minus b of s, times s, which equals the sum over s in support of a of a of s times s, minus the sum over s in support of b of b of s times s, which equals v minus v, which equals the zero vector in V.

Thus d is a representation of the zero vector in V in terms of S. Since S is linearly independent, Theorem 1.6.6 implies that support of d equals the empty set. Hence a equals b. Conversely, suppose that every vector has at most one representation in terms of S. The zero function from S to F is a representation of the zero vector in V, so it is the only such representation. Theorem 1.6.6 therefore implies that S is linearly independent. This completes the proof.
