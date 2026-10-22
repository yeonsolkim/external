---
section: proof-proposition-1-3-14
title: Proof
kind: proof
document: 1.3 Linear Combinations and Spans
url: /2026/06/21/3.-Linear-Combinations-and-Spans.html
source: 973328f829b6821dc44d37772917137b3a631173ba777af8ef5649549fd1cbad
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-19
body: a8246ceeccb879ddcda269cf1db8ff5c3a21dc10795dc7f9c4d88050d474d0f0
words: 231
---

Proof. If v belongs to span of S, Definition 1.3.8 gives a finite set I and indexed families s i for i in I, in S, and a i for i in I, in F, such that v equals the sum over i in I of a i times s i.

Put J equal to the set of s i such that i belongs to I, and define a from S to F by a of s equals the sum over all i in I such that s i equals s of a i.

If s is not in J, the defining sum is empty, so a of s equals zero. Hence the support of a is contained in J, and is finite. By Theorem 1.3.4 applied to i maps to s i, Proposition 1.3.7 part 3, and Proposition 1.3.3, v equals the sum over i in I of a i times s i, which equals the sum over s in J of the sum over all i in I such that s i equals s of a i times s, which equals the sum over s in J of a of s times s, which equals the sum over s in the support of a of a of s times s.

Thus a is a representation of v in terms of S. The converse is trivial. This completes the proof.
