---
section: proof-theorem-1-4-8
title: Proof
kind: proof
document: 1.4 The Span Operator
url: /2026/10/14/4.-The-Span-Operator.html
source: 89b5af70bbd4fc56d7b54c148fca3821aef92ec804ff0af76586cd4c5306e279
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-19
body: d02226c8b53557dce34d95fd09c1dc5da060a7d232a41d4e7bf9234f8ce445aa
words: 334
---

Proof. Suppose first that S is closed. First, choosing I equals the empty set, we have zero in V belongs to span of S, which equals S. Next, let u and v belong to S and a belong to F. Since both u plus v and a times u are linear combinations of vectors in S, we have u plus v belongs to span of S, which equals S, and a times u belongs to span of S, which equals S. By Theorem 1.2.2, S is a subspace of V. Conversely, suppose that S is a subspace of V. Since span is extensive, we have S is contained in span of S. It remains to show that span of S is contained in S. Let v belong to span of S. By Definitions 1.3.8 and 1.3.9, there exist a finite index set I, the family u i, for i in I, in S, and the family a i, for i in I, in F such that v equals the sum over i in I of a i times u i. We show by mathematical induction on the cardinality of I that v belongs to S. For the base case the cardinality of I equals zero, we have I equals the empty set, so v equals zero in V, which belongs to S. Now suppose that every linear combination indexed by a set of cardinality n belongs to S. Let the cardinality of I equal n plus one, and choose j in I. Then v equals a j times u j, plus the sum over i in I without j of a i times u i. Since S is a subspace, the first summand belongs to S. Since the cardinality of I without j equals n, the second summand belongs to S by the induction hypothesis. Hence v belongs to S. It follows that span of S is contained in S. Consequently S equals span of S and S is closed. This completes the proof.
