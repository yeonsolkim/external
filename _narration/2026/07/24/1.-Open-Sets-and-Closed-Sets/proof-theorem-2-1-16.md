---
section: proof-theorem-2-1-16
title: Proof
kind: proof
document: 2.1 Open Sets and Closed Sets
url: /2026/07/24/1.-Open-Sets-and-Closed-Sets.html
source: b54d8cccf55b7dee59ced42334be2804911a39d5f1182f948ab0b753586e9fd5
skeleton: 4
prompt: lecture-v3
model: gpt-5.5
generated: 2026-09-28
body: 3a47cb15ef32543e44bfbab6faa0665d9093e06f8c71121063e0eb49c9dba587
words: 309
---

Proof.

One. Let U be the union of all subsets of A open in M. If x belongs to the interior of A, then the open ball of radius r about x is contained in A for some r greater than zero. Since the open ball of radius r about x is open in M, we have x belongs to the open ball of radius r about x, which is contained in U. Conversely, if x belongs to U, then there is a subset U i of A open in M. Then x has an open ball, the open ball of radius r about x, contained in U i. It follows that the open ball of radius r about x is contained in A, so x belongs to the interior of A. Consequently, the interior of A equals U.

Two. Let F be the intersection of all supersets of A closed in M. If x belongs to the closure of A, then every open ball of x meets A. Since A is contained in F, x is a closure point of F. Since F is closed, x belongs to F. Conversely, if x is not a closure point of A, then the open ball of radius r about x intersect A equals the empty set for some r greater than zero. It follows that A is contained in M minus the open ball of radius r about x. Thus the set M minus the open ball of radius r about x is a superset of A closed in M. Since F is contained in M minus the open ball of radius r about x and x does not belong to M minus the open ball of radius r about x, we have x does not belong to F. Consequently, the closure of A equals F. This completes the proof.
