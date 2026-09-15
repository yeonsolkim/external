---
section: theorem-2-1-5
title: Theorem 2.1.5
kind: theorem
document: 2.1. Open Sets and Closed Sets
url: /2026/07/24/1.-Open-Sets-and-Closed-Sets.html
source: 2122d0487cb7957c98d8d1da2fa6edf1ae80cb7e3ff67b5467916740054a68b4
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-15
body: cae310183ce3e7ecca264fe7f07f45d30bce3acdea075811d8df781930ee8ea1
words: 485
---

Theorem 2.1.5. Let M be a metric space and let A be contained in M. Every point of M is either an interior point of A, an exterior point of A, or a boundary point of A, and hence M equals the interior of A, disjoint union the boundary of A, disjoint union the exterior of A.

Proof. If x belongs to the interior of A, then the open ball of radius r about x is contained in A for some r greater than zero. Since x belongs to the interior of A implies x belongs to A, the open ball of radius r about x does not meet A complement. Hence the intersection of the interior of A and the boundary of A is the empty set. If zero is less than s, which is less than r, then the open ball of radius s about x is contained in the open ball of radius r about x, which is contained in A. If s is greater than r, then the open ball of radius r about x is contained in the open ball of radius s about x, so that the intersection of the open ball of radius s about x and A is not equal to the empty set. Hence the intersection of the interior of A and the exterior of A is the empty set. Lastly, since x belongs to the boundary of A implies x does not belong to the exterior of A, the intersection of the boundary of A and the exterior of A is the empty set. Therefore the interior of A, the boundary of A, and the exterior of A are mutually disjoint. We claim that the boundary of A union the exterior of A equals the complement of the interior of A. Indeed, if x belongs to the boundary of A or x belongs to the exterior of A, then x does not belong to the interior of A, because the interior of A, the boundary of A, and the exterior of A are mutually disjoint. Therefore the boundary of A union the exterior of A is contained in the complement of the interior of A. Conversely, suppose x does not belong to the interior of A, which means that every ball around x meets A complement. There may exist some r greater than zero such that the open ball of radius r about x is contained in A complement, which means x belongs to the exterior of A. Otherwise, no such r exists, which means that every ball around x meets A. Thus x belongs to the boundary of A. Therefore the complement of the interior of A is contained in the boundary of A union the exterior of A. It is concluded that the boundary of A union the exterior of A equals the complement of the interior of A. This completes the proof.
