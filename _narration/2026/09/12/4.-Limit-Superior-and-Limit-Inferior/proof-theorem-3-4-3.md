---
section: proof-theorem-3-4-3
title: Proof
kind: proof
document: 3.4 Limit Superior and Limit Inferior
url: /2026/09/12/4.-Limit-Superior-and-Limit-Inferior.html
source: d200489f8df76f09749c629bc641e9c16a8d578acdd1710bdf0990fb0d6f38c7
skeleton: 4
prompt: lecture-v3
model: gpt-5.5
generated: 2026-09-28
body: a8a5fd4f325d544877812ec28d3d6c0176e874018549db6e76f66bc126b643e0
words: 705
---

Proof. Let s k equal the supremum of the k-th tail and L equal the lim sup of x n. First suppose L belongs to R. We show that no extended subsequential limit can be greater than L. Suppose x sub n j tends to y and fix k. Since n j tends to infinity, there is j zero such that j is greater than or equal to j zero implies n j is greater than or equal to k. It follows that x sub n j is less than or equal to s k. If y belongs to R, then for any epsilon greater than zero, there is j zero prime such that j is greater than or equal to j zero prime implies the absolute value of x sub n j minus y is less than epsilon. Taking maximum of j zero and j zero prime, eventually y minus epsilon is less than s k. Since y and s k are the supremum and an upper bound for the set of y minus epsilon such that epsilon is greater than zero respectively, so y is less than or equal to s k. If y equals plus infinity, then for any N greater than zero, there exists j zero prime such that j is greater than or equal to j zero prime implies x sub n j is greater than or equal to N. Taking maximum, eventually N is less than or equal to x sub n j, which is less than or equal to s k, which implies s k equals plus infinity. Hence y is less than or equal to s k. If y equals minus infinity, then automatically y is less than or equal to s k. Thus y is less than or equal to s k in every case. Since k was arbitrary, y is less than or equal to the infimum over k greater than or equal to one of s k, which equals L. Furthermore, L is itself a subsequential limit. Indeed, put n zero equal to zero. Since s k decreases to L, after n j minus one has been chosen, we can choose k j greater than n j minus one such that s sub k j is less than L plus one over j. Since s sub k j is the supremum for the k j-th tail, there exists n j greater than or equal to k j such that x sub n j is greater than s sub k j minus one over j. Thus n j is greater than n j minus one and we have L minus one over j is less than or equal to s sub k j minus one over j, which is less than x sub n j, which is less than or equal to s sub k j, which is less than L plus one over j.

Therefore, we obtain x sub n j tends to L. Hence L is an upper bound for A and L belongs to A, we conclude that L equals the maximum of A. We now consider the infinite cases. If L equals plus infinity, then the k-th tail is unbounded above for every k. Choose n one such that x sub n one is greater than one. Having chosen n one through n j minus one, we can choose n j greater than n j minus one so that x sub n j is greater than j. It follows that x sub n j tends to plus infinity, which implies the maximum of A equals plus infinity. Hence L equals the maximum of A. If L equals minus infinity, then s k tends to minus infinity. Given y belongs to R, we have s k is less than y eventually. It follows that x k is less than or equal to s k, which is less than y. Thus eventually x k is less than y, giving x k tends to minus infinity. Therefore A equals the set containing minus infinity and the maximum of A equals minus infinity. Hence L equals the maximum of A. In the case of the limit inferior, the proof is analogous. This completes the proof.
