---
section: proof-theorem-1-3-7
title: Proof
kind: proof
document: 1.3 Linear Combinations and Spans
url: /2026/06/21/3.-Linear-Combinations-and-Spans.html
source: 5e2792f0a94d797ef48644287fd407122a90f87199ba046f808bcc9c50a0d0e8
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-06
body: 07b7051dc1cbac377df9e7f776f63f5f77d873f83baa9a1c8c35680c466a8aa2
words: 349
---

Proof. One. If S equals the empty set, then the span of S equals the set containing the zero vector is a subspace containing S and is contained in every subspace of V, so both assertions hold. Assume S is not equal to the empty set. Since v equals one times v belongs to the span of S for every v in S, we have S is contained in the span of S. Let v belong to S. Then the zero vector equals zero times v belongs to the span of S. If s and t belong to the span of S, then there exist m and n in the positive integers, u i and v j in S, and a i and b j in F such that s equals the sum from i equals one to m of a i u i, and t equals the sum from j equals one to n of b j v j.

For any c in F, we have s plus t equals the sum from i equals one to m of a i u i, plus the sum from j equals one to n of b j v j, and c s equals the sum from i equals one to m of the quantity c a i times u i.

Both expressions are finite linear combinations of vectors in S, so s plus t and c s belong to the span of S. Therefore the span of S is a subspace of V by Theorem 1.2.2.

Two. Let W be a subspace of V containing S. If v belongs to the span of S, then there exist a finite number of a one through a n in F and u one through u n in S such that v equals a one u one plus, and so on, up to a n u n. Since u one through u n belong to W and W is closed, v equals a one u one plus, and so on, up to a n u n, belongs to W. This completes the proof.
