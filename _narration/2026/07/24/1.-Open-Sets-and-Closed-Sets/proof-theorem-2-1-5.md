---
section: proof-theorem-2-1-5
title: Proof
kind: proof
document: 2.1 Open Sets and Closed Sets
url: /2026/07/24/1.-Open-Sets-and-Closed-Sets.html
source: a1d78d5edd63775ecaafbf6a3c3dc53e841fdd3600bb1a1147e06de036365cf9
skeleton: 4
prompt: lecture-v3
model: gpt-5.5
generated: 2026-09-28
body: 817bebaa9878aa131d37ee368ac816275983faaa8a5588570496b4466dcc6aa8
words: 416
---

Proof. If x belongs to the interior of A, then the open ball of radius r about x is contained in A for some r greater than zero. Since x belongs to the interior of A implies x belongs to A, the open ball of radius r about x does not meet A complement. Hence the interior of A intersect the boundary of A equals the empty set. If zero is less than s, which is less than r, then the open ball of radius s about x is contained in the open ball of radius r about x, which is contained in A. If s is greater than r, then the open ball of radius r about x is contained in the open ball of radius s about x, so that the open ball of radius s about x intersect A is not equal to the empty set. Hence the interior of A intersect the exterior of A equals the empty set. Lastly, since x belongs to the boundary of A implies x does not belong to the exterior of A, the boundary of A intersect the exterior of A equals the empty set. Therefore the interior of A, the boundary of A, and the exterior of A are mutually disjoint.

We claim that the boundary of A union the exterior of A equals the complement of the interior of A. Indeed, if x belongs to the boundary of A or x belongs to the exterior of A, then x does not belong to the interior of A, because the interior of A, the boundary of A, and the exterior of A are mutually disjoint. Therefore the boundary of A union the exterior of A is contained in the complement of the interior of A. Conversely, suppose x does not belong to the interior of A, which means that every ball around x meets A complement. There may exist some r greater than zero such that the open ball of radius r about x is contained in A complement, which means x belongs to the exterior of A. Otherwise, no such r exists, which means that every ball around x meets A. Thus x belongs to the boundary of A. Therefore the complement of the interior of A is contained in the boundary of A union the exterior of A. It is concluded that the boundary of A union the exterior of A equals the complement of the interior of A. This completes the proof.
