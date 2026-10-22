---
section: proof-theorem-1-4-7
title: Proof
kind: proof
document: 1.4 The Span Operator
url: /2026/10/14/4.-The-Span-Operator.html
source: ae6c84ed7708b212f135cc64230bebc53d3aa7a0960b19454d95942b099f13d6
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-19
body: 93c5769b93540a5d28c3407905b12bf476541ac20cc1b281ab2e73ab7c624bda
words: 461
---

Proof. Since Definition 1.3.9 guarantees that span of S belongs to P of V for all S in P of V, the operation is well-defined. Firstly, if v belongs to S, then v equals the sum from i equals one to one of one times v, which belongs to span of S.

Hence S is contained in span of S and span is extensive. Secondly, suppose S and T belong to P of V and S is contained in T. If v belongs to span of S, then there exist a finite index set I, an indexed family u i, for i in I, in S, and an indexed family a i, for i in I, in F such that v equals the sum over i in I of a i times u i.

Since S is contained in T, the family u i, for i in I, is in T. By existential introduction, v belongs to span of T. Hence, span is monotone. Lastly, we check idempotence. If v belongs to span of span of S, then there exist a finite index set I, an indexed family u i, for i in I, in span of S, and an indexed family a i, for i in I, in F such that v equals the sum over i in I of a i times u i.

Since u i belongs to span of S, there exist a finite index set J i, an indexed family w i j, for j in J i, in S, and an indexed family b i j, for j in J i, in F such that u i equals the sum over j in J i of b i j times w i j for each i in I. Put K equal to the set of pairs i j such that i belongs to I and j belongs to J i. By Proposition 1.3.7, part 2, and Theorem 1.3.4, v equals the sum over i in I of a i times the quantity the sum over j in J i of b i j times w i j, which equals the sum over i in I of the sum over j in J i of a i times the quantity b i j times w i j, which equals the sum over pairs i j in K of the quantity a i times b i j, times w i j.

Therefore, by existential introduction, v is a linear combination of vectors in S, so v belongs to span of S. Hence span of span of S is contained in span of S. Extensivity gives the reverse inclusion, so span of span of S equals span of S; the span operator is idempotent. This completes the proof.
