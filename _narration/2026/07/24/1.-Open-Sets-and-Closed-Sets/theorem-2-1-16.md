---
section: theorem-2-1-16
title: Theorem 2.1.16
kind: theorem
document: 2.1. Open Sets and Closed Sets
url: /2026/07/24/1.-Open-Sets-and-Closed-Sets.html
source: aa697637c89d162728731b52aaaf5226be361bc682cec715ec174d22dc61a4f6
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-15
body: b63723b93894f1b1ee152d9afad6e4e398d4155031ddddf31f81647c4c0a06b7
words: 358
---

Theorem 2.1.16. Let M be a metric space and let A be a subset of M. Then,

First, the interior of A is the union of all subsets of A open in M.

Second, the closure of A is the intersection of all supersets of A closed in M.

Proof. First, let U be the union of all subsets of A open in M. If x belongs to the interior of A, then the open ball of radius r about x is contained in A for some r greater than zero. Since the open ball of radius r about x is open in M, we have x belongs to the open ball of radius r about x, which is contained in U. Conversely, if x belongs to U, then there is a subset U i of A open in M. Then x has an open ball, the open ball of radius r about x, contained in U i. It follows that the open ball of radius r about x is contained in A, so x belongs to the interior of A. Consequently, the interior of A equals U.

Second, let F be the intersection of all supersets of A closed in M. If x belongs to the closure of A, then every open ball of x meets A. Since A is contained in F, x is a closure point of F. Since F is closed, x belongs to F. Conversely, if x is not a closure point of A, then the open ball of radius r about x intersect A equals the empty set for some r greater than zero. It follows that A is contained in M minus the open ball of radius r about x. Thus the set M minus the open ball of radius r about x is a superset of A closed in M. Since F is contained in M minus the open ball of radius r about x and x does not belong to M minus the open ball of radius r about x, we have x does not belong to F. Consequently, the closure of A equals F. This completes the proof.
