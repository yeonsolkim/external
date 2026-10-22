---
section: proof-proposition-1-4-14
title: Proof
kind: proof
document: 1.4 Linear Combinations and Spans
url: /linear-algebra/linear-combinations-and-spans/
source: aab76818ef9a1cb9af973cb62a9c0aded1d795aa6ddede80108a1fe6938141ee
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-22
body: b1c180a7d26c7248c0fa4e3cc3b1f4f2cbdc523299dbd9f44955152c2f5d1594
words: 232
---

Proof. If v belongs to span of S, Definition 1.4.8 gives a finite set I and indexed families s i, for i in I, in S, and a i, for i in I, in F, such that v equals the sum over i in I of a i times s i.

Put J equal to the set of s i such that i belongs to I, and define a from S to F by a of s equals the sum over all i in I such that s i equals s, of a i.

If s does not belong to J, the defining sum is empty, so a of s equals zero. Hence the support of a is contained in J and is finite. By Theorem 1.4.4 applied to i maps to s i, Proposition 1.4.7, part three, and Proposition 1.4.3, v equals the sum over i in I of a i times s i, which equals the sum over s in J of the sum over all i in I such that s i equals s, of a i times s, which equals the sum over s in J of a of s times s, which equals the sum over s in the support of a of a of s times s.

Thus a is a representation of v in terms of S. The converse is trivial. This completes the proof.
