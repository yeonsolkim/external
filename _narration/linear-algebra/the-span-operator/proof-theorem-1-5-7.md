---
section: proof-theorem-1-5-7
title: Proof
kind: proof
document: 1.5 The Span Operator
url: /linear-algebra/the-span-operator/
source: f7c0a199234b9499b8354ce91b1c5c339bfee17c950ace51d1c60e0a6068567e
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-22
body: e9aa77a072e9cacb79c2bb56bb7d15199029682e97405fa4a5036a8c9e4433ee
words: 497
---

Proof. Since Definition 1.4.9 guarantees that the span of S belongs to the power set of V for all S in the power set of V, the operation is well-defined. Firstly, if v belongs to S, then we have v equals the sum from i equals one to one of one times v, which belongs to the span of S.

Hence S is contained in the span of S and span is extensive. Secondly, suppose S and T belong to the power set of V and S is contained in T. If v belongs to the span of S, then there exist a finite index set I, an indexed family u i, for i in I, in S, and an indexed family a i, for i in I, in F such that v equals the sum over i in I of a i times u i.

Since S is contained in T, the family u i, for i in I, is in T. By existential introduction, v belongs to the span of T. Hence, span is monotone. Lastly, we check idempotence. If v belongs to the span of the span of S, then there exist a finite index set I, an indexed family u i, for i in I, in the span of S, and an indexed family a i, for i in I, in F such that v equals the sum over i in I of a i times u i.

Since u i belongs to the span of S, there exist a finite index set J i, an indexed family w sub i j, for j in J i, in S, and an indexed family b sub i j, for j in J i, in F such that u i equals the sum over j in J i of b sub i j times w sub i j, for each i in I.

Put K equal to the set of pairs i and j such that i belongs to I and j belongs to J i. By Proposition 1.4.7 part 2 and Theorem 1.4.4, v equals the sum over i in I of a i times the quantity the sum over j in J i of b sub i j times w sub i j, which equals the sum over i in I of the sum over j in J i of a i times the quantity b sub i j times w sub i j, which equals the sum over pairs i and j in K of the quantity a i times b sub i j, times w sub i j.

Therefore, by existential introduction, v is a linear combination of vectors in S, so v belongs to the span of S. Hence the span of the span of S is contained in the span of S. Extensivity gives the reverse inclusion, so the span of the span of S equals the span of S; the span operator is idempotent. This completes the proof.
