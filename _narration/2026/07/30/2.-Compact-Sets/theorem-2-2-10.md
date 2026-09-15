---
section: theorem-2-2-10
title: Theorem 2.2.10
kind: theorem
document: 2.2. Compact Sets
url: /2026/07/30/2.-Compact-Sets.html
source: 8a6442d7fb6373e2f7b0664c5dc1b3367c025fa3bb3e9271e441acd5b90be454
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-15
body: 3499f027ecd7ffe9792c4ebd04ce207c73b62bf50ecc59a963862fa134402fea
words: 327
---

Theorem 2.2.10. A metric space M is compact if and only if, for every collection the family F i, for i in I, of closed subsets of M, the family F i, for i in I, has the F I P implies the intersection over i in I of F i is not equal to the empty set.

Proof. Suppose that M is compact, and let the family F i, for i in I, be a collection of closed subsets of M satisfying the F I P. Let U i equal M set minus F i. If the intersection over i in I of F i equals the empty set, then the family U i, for i in I, is an open cover of M. Since M is compact, M equals the union from k equals one to n of U sub i k, for some finitely many indices i one through i n. It follows that the intersection from k equals one to n of F sub i k equals the empty set, which contradicts the F I P. Hence the intersection over i in I of F i is not equal to the empty set.

Conversely, suppose that every collection of closed subsets of M satisfying the F I P has nonempty intersection. Let the family U i, for i in I, be an open cover of M, and put F i equal M set minus U i. Then every F i is closed in M, and the intersection over i in I of F i equals the empty set. Consequently, the family F i, for i in I, cannot have the finite intersection property. Hence there exists a finite subcollection the family F sub i k, for k equals one to n, whose intersection is empty. Taking complements yields M is contained in the union from k equals one to n of U sub i k. Therefore M is compact. This completes the proof.
