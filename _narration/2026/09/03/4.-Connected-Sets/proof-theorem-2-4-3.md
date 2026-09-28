---
section: proof-theorem-2-4-3
title: Proof
kind: proof
document: 2.4 Connected Sets
url: /2026/09/03/4.-Connected-Sets.html
source: 315b9a27765a7f12eed0112265ba0162a0b4403741d1969fee93274035b7c465
skeleton: 4
prompt: lecture-v3
model: gpt-5.5
generated: 2026-09-28
body: 6164590434e495a8effa7e36eafee77df7186866ea5bc1a1d42501eacf4ec07b
words: 339
---

Proof. Suppose first that A is disconnected. Then there exist two nonempty separated sets B and C such that A equals B disjoint union C. Define U equals A minus the closure of C and V equals A minus the closure of B. Since M minus the closure of C and M minus the closure of B are open, Theorem 2.1.18 shows that the sets U and V are open in A. Since B and C are separated, B intersect the closure of C equals the empty set, so B is contained in U. If x belongs to U, then x belongs to A, which equals B union C, and x is not in the closure of C. Thus x is not in C, so x belongs to B. Thus U equals B. Similarly, V equals C. Therefore, A equals U disjoint union V, where U and V are nonempty and open in A.

Conversely, suppose that U and V are nonempty sets open in A such that A equals U disjoint union V. Since U equals A minus V and V equals A minus U, both U and V are also closed in A. Hence the closure of U in A equals U and the closure of V in A equals V. Therefore we have U intersect the closure of V in A equals U intersect V equals the empty set.

Since U is contained in A and the closure of V in A equals the closure of V intersect A by Theorem 2.1.19, it follows that U intersect the closure of V equals the quantity U intersect A, intersect the closure of V, which equals U intersect the quantity A intersect the closure of V, which equals U intersect the closure of V in A, which equals the empty set.

Similarly, the closure of U intersect V equals the empty set. Thus U and V are separated. Since they are nonempty and A equals U disjoint union V, the set A is disconnected. This completes the proof.
