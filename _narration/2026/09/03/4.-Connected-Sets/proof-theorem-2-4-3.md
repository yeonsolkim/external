---
section: proof-theorem-2-4-3
title: Proof
kind: proof
document: 2.4 Connected Sets
url: /2026/09/03/4.-Connected-Sets.html
source: 315b9a27765a7f12eed0112265ba0162a0b4403741d1969fee93274035b7c465
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-07
body: 5b9ae31a9f6e47537b7b245564f8f5d195c98cf064f4c6e0278ece9e2c78d6b4
words: 359
---

Proof. Suppose first that A is disconnected. Then there exist two nonempty separated sets B and C such that A equals the disjoint union of B and C. Define U equals A minus the closure of C and V equals A minus the closure of B. Since M minus the closure of C and M minus the closure of B are open, Theorem 2.1.18 shows that the sets U and V are open in A. Since B and C are separated, B intersection the closure of C equals the empty set, so B is contained in U. If x belongs to U, then x belongs to A, which equals B union C, and x does not belong to the closure of C. Thus x does not belong to C, so x belongs to B. Thus U equals B. Similarly, V equals C. Therefore, A equals the disjoint union of U and V, where U and V are nonempty and open in A. Conversely, suppose that U and V are nonempty sets open in A such that A equals the disjoint union of U and V. Since U equals A minus V and V equals A minus U, both U and V are also closed in A. Hence the closure of U in A equals U and the closure of V in A equals V. Therefore we have U intersection the closure of V in A equals U intersection V, which equals the empty set.

Since U is contained in A and the closure of V in A equals the intersection of the closure of V with A by Theorem 2.1.19, it follows that U intersection the closure of V equals the quantity U intersection A, intersected with the closure of V, which equals U intersected with the quantity A intersection the closure of V, which equals U intersection the closure of V in A, which equals the empty set.

Similarly, the closure of U intersection V equals the empty set. Thus U and V are separated. Since they are nonempty and A equals the disjoint union of U and V, the set A is disconnected. This completes the proof.
