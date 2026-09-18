---
section: theorem-3-4-3
title: Theorem 3.4.3
kind: theorem
document: 3.4. Limit Superior and Limit Inferior
url: /2026/09/12/4.-Limit-Superior-and-Limit-Inferior.html
source: 512038f7000aad41b7bef08cc2ef806c6b3cdee1604a695d47a0cb3ad8fbdeea
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-18
body: 701e780c6115ec6bd6b4aca0a1113f17d090e7987992d4823ce4dec697bfcee9
words: 777
---

Theorem 3.4.3. Let x n be a sequence in R, and let A be the set of all extended subsequential limits of x n. Then lim sup of x n equals the maximum of A, and lim inf of x n equals the minimum of A.

Proof. Let s k equal the supremum of the set of x n such that n is greater than or equal to k, and L equal the lim sup of x n. First suppose L belongs to R. We show that no extended subsequential limit can be greater than L. Suppose x sub n j converges to y and fix k. Since n j tends to infinity, there is j zero such that j greater than or equal to j zero implies n j greater than or equal to k. It follows that x sub n j is less than or equal to s k. If y belongs to R, then for any epsilon greater than zero, there is j zero prime such that j greater than or equal to j zero prime implies the absolute value of x sub n j minus y is less than epsilon. Taking maximum of j zero and j zero prime, eventually y minus epsilon is less than s k. Since y and s k are the supremum and an upper bound for the set of y minus epsilon such that epsilon is greater than zero respectively, so y is less than or equal to s k. If y equals plus infinity, then for any capital N greater than zero, there exists j zero prime such that j greater than or equal to j zero prime implies x sub n j is greater than or equal to capital N. Taking maximum, eventually capital N is less than or equal to x sub n j, which is less than or equal to s k, which implies s k equals plus infinity. Hence y is less than or equal to s k. If y equals minus infinity, then automatically y is less than or equal to s k. Thus y is less than or equal to s k in every case. Since k was arbitrary, y is less than or equal to the infimum over k greater than or equal to one of s k, which equals L. Furthermore, L is itself a subsequential limit. Indeed, put n zero equal to zero. Since s k decreases to L, after n sub j minus one has been chosen, we can choose k j greater than n sub j minus one such that s sub k j is less than L plus one over j. Since s sub k j is the supremum for the k j-th tail, there exists n j greater than or equal to k j such that x sub n j is greater than s sub k j minus one over j. Thus n j is greater than n sub j minus one and L minus one over j is less than or equal to s sub k j minus one over j, which is less than x sub n j, which is less than or equal to s sub k j, which is less than L plus one over j.

Therefore, we obtain x sub n j converges to L. Hence L is an upper bound for A and L belongs to A, we conclude that L equals the maximum of A. We now consider the infinite cases. If L equals plus infinity, then the set of x n such that n is greater than or equal to k is unbounded above for every k. Choose n one such that x sub n one is greater than one. Having chosen n one through n sub j minus one, we can choose n j greater than n sub j minus one so that x sub n j is greater than j. It follows that x sub n j converges to plus infinity, which implies the maximum of A equals plus infinity. Hence L equals the maximum of A. If L equals minus infinity, then s k converges to minus infinity. Given y belongs to R, we have s k is less than y eventually. It follows that x k is less than or equal to s k, which is less than y. Thus eventually x k is less than y, giving x k converges to minus infinity. Therefore A equals the set containing minus infinity and the maximum of A equals minus infinity. Hence L equals the maximum of A. In the case of the limit inferior, the proof is analogous. This completes the proof.
