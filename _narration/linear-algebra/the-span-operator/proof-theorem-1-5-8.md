---
section: proof-theorem-1-5-8
title: Proof
kind: proof
document: 1.5 The Span Operator
url: /linear-algebra/the-span-operator/
source: d12bc1c81d7c6a765c4e63742ade73c2e21213dab5f3ee2aff6e8d043345ca50
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-22
body: d6186fe225813c245150273427bdbc216f2e35a9dc37a763b0f530f55f5289fa
words: 343
---

Proof. Suppose first that S is closed. First, choosing I equals the empty set, we have zero V belongs to the span of S, which equals S. Next, let u and v be in S, and let a be in F. Since both u plus v and a times u are linear combinations of vectors in S, we have u plus v belongs to the span of S, which equals S, and a times u belongs to the span of S, which equals S.

By Theorem 1.3.2, S is a subspace of V. Conversely, suppose that S is a subspace of V. Since span is extensive, we have S is contained in the span of S. It remains to show that the span of S is contained in S. Let v belong to the span of S. By Definitions 1.4.8 and 1.4.9, there exist a finite index set I, the family u i, for i in I, in S, and the family a i, for i in I, in F, such that v equals the sum over i in I of a i times u i.

We show by mathematical induction on the cardinality of I that v belongs to S. For the base case the cardinality of I equals zero, we have I equals the empty set, so v equals zero V, which belongs to S. Now suppose that every linear combination indexed by a set of cardinality n belongs to S. Let the cardinality of I equal n plus one, and choose j in I. Then v equals a j times u j plus the sum over i in I with j removed of a i times u i.

Since S is a subspace, the first summand belongs to S. Since the cardinality of I with j removed equals n, the second summand belongs to S by the induction hypothesis. Hence v belongs to S. It follows that the span of S is contained in S. Consequently S equals the span of S and S is closed. This completes the proof.
