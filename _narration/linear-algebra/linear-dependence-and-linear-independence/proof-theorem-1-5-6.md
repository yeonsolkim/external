---
section: proof-theorem-1-5-6
title: Proof
kind: proof
document: 1.5 Linear Dependence and Linear Independence
url: /2026/08/17/5.-Linear-Dependence-and-Linear-Independence.html
source: a1c0d91ed21bdb57ea3619f7c9dfcebe9aba7121e7fbb0311293e8f6ea6caf2e
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-19
body: 6ed840d300f3f5fbb5060ded00c3375f9e9d81fb8db3c288fddbca4b03d2f5e3
words: 373
---

Proof. Suppose that S is linearly dependent. Then there exists v in S such that v belongs to the span of S without v. By Proposition 1.3.14, there exists a finite supported function a from S without v to F such that v equals the sum over t in the support of a of a of t times t.

Define a function b from S to F by b of s equals a of s if s belongs to the support of a, minus one if s equals v, and zero otherwise.

Then the support of b equals the support of a union the set containing v is finite, and the sum over s in the support of b of b of s times s equals b of v times v plus the sum over s in the support of a of b of s times s, which equals negative the quantity the sum over t in the support of a of a of t times t, plus the sum over s in the support of a of a of s times s, which equals the zero vector in V.

Hence b is a representation of the zero vector in V in terms of S, and v belongs to the support of b. We now prove the converse. Let a from S to F be a representation of the zero vector in V with nonempty support. Put I equal to the support of a and choose s in I. By Definition 1.3.1, we have a of s times s plus the sum over t in I without s of a of t times t equals the zero vector in V.

Since a of s is not equal to zero, s equals the inverse of the quantity negative a of s, times the sum over t in I without s of a of t times t, which equals the sum over t in I without s of the negative of a of s inverse times a of t, times t.

Therefore s belongs to the span of I without s, so I is linearly dependent by Proposition 1.5.3. It follows from Proposition 1.5.4, part one, that S is linearly dependent. This completes the proof.
