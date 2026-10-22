---
section: proof-theorem-1-6-6
title: Proof
kind: proof
document: 1.6 Linear Dependence and Linear Independence
url: /linear-algebra/linear-dependence-and-linear-independence/
source: d696b34dec154b0c29c6712a3827344aab74972bf3ec94b7d1577483d6afbca7
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-22
body: 650f8d58ede750185d02ee6ab88a8758267fabe8963fc9e8c119c703f2f49381
words: 368
---

Proof. Suppose that S is linearly dependent. Then there exists v belonging to S such that v belongs to the span of S without v. By Proposition 1.4.14, there exists a finite supported function a from S without v to F such that v equals the sum over t in the support of a of a of t times t.

Define a function b from S to F by b of s equals a of s if s belongs to the support of a; equals negative one if s equals v; and equals zero otherwise.

Then the support of b equals the support of a union the singleton v is finite and the sum over s in the support of b of b of s times s equals b of v times v plus the sum over s in the support of a of b of s times s, which equals negative the quantity the sum over t in the support of a of a of t times t, plus the sum over s in the support of a of a of s times s, which equals zero vector in V.

Hence b is a representation of zero vector in V in terms of S, and v belongs to the support of b. We now prove the converse. Let a from S to F be a representation of zero vector in V with nonempty support. Put I equal to the support of a and choose s belonging to I. By Definition 1.4.1, we have a of s times s plus the sum over t in I without s of a of t times t equals zero vector in V.

Since a of s is not equal to zero, s equals the inverse of negative a of s times the sum over t in I without s of a of t times t, which equals the sum over t in I without s of negative a of s inverse times a of t, times t.

Therefore s belongs to the span of I without s, so I is linearly dependent by Proposition 1.6.3. It follows from Proposition 1.6.4, part one, that S is linearly dependent. This completes the proof.
