---
section: proof-theorem-1-3-13
title: Proof
kind: proof
document: 1.3 Linear Combinations and Spans
url: /2026/06/21/3.-Linear-Combinations-and-Spans.html
source: 429d319fd0f0d0ae378009336708ecdc5391cb099a6b3a64099ff42030badec4
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-08
body: 959f9b4b271b31e3e33309e91f72b71dc6469edf11a40c8e1155229a8cac46e3
words: 550
---

Proof. Since Definition 1.3.2 guarantees that the span of S belongs to the power set of V for all S belonging to the power set of V, the operation is well-defined. Firstly, if S equals the empty set, then S is contained in the span of S, which equals the singleton set containing zero in V. Suppose S is not equal to the empty set. Since v equals one times v, which belongs to the span of S, for every v in S, we have S is contained in the span of S. Hence span is extensive. Secondly, suppose S and T belong to the power set of V and S is contained in T. If S equals T, which equals the empty set, then the span of S equals the singleton set containing zero in V, which equals the span of T. If S equals the empty set and T is not equal to the empty set, then there exists v in T and zero in V equals zero times v, which belongs to the span of T. Hence the span of S is contained in the span of T. If S is not equal to the empty set and v belongs to the span of S, then there exist v one through v n in S and a one through a n in F such that v equals a one times v one plus a two times v two, and so on, up to a n times v n. Since S is contained in T, we have v one through v n in T. So v belongs to the span of T. Hence span is monotone. Lastly, we check idempotence. If S equals the empty set, then the span of S equals the singleton set containing zero in V is the zero subspace, so the span of the span of S equals the span of S by Proposition 1.3.3. Now assume S is not equal to the empty set. If v belongs to the span of the span of S, then there exist a positive integer n, vectors v one through v n in the span of S, and scalars a one through a n in F such that v equals the sum from i equals one to n of a i times v i. For each i, there exist a positive integer m i, vectors u sub i j in S, and scalars b sub i j in F such that v i equals the sum from j equals one to m i of b sub i j times u sub i j. Thus v equals the sum from i equals one to n of the sum from j equals one to m i of the quantity a i times b sub i j, times u sub i j.

This is a finite linear combination of vectors in S, so v belongs to the span of S. Therefore the span of the span of S is contained in the span of S. Extensivity gives the reverse inclusion, so the span of the span of S equals the span of S; span is idempotent. By Proposition 1.3.3, a subset S of V is closed if and only if S is a subspace of V. This completes the proof.
