---
section: theorem-2-1-15
title: Theorem 2.1.15
kind: theorem
document: 2.1. Open Sets and Closed Sets
url: /2026/07/24/1.-Open-Sets-and-Closed-Sets.html
source: 964d8adf9929ee8e647511147ce2e047aedf8f68f8962f0f380dcb5beeec12bd
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-15
body: 16611f2ddbb3de81256c73188d123637f70a09597db20382c1d061cc32e41132
words: 474
---

Theorem 2.1.15. Let M be a metric space.

One. If the family U i, for i in I, is a collection of open sets, then the union over i in I of U i is open.

Two. If the family F i, for i in I, is a collection of closed sets, then the intersection over i in I of F i is closed.

Three. If the family U i, for i in I, is a finite collection of open sets, then the intersection over i in I of U i is open.

Four. If the family F i, for i in I, is a finite collection of closed sets, then the union over i in I of F i is closed.

Proof. For one, let x belong to the union over i in I of U i. Then we may let x belong to U i for some i in I. Since x is an interior point of U i, x is also an interior point of the union over i in I of U i. Therefore the union over i in I of U i is open.

For two, by Theorem 2.1.14, F i complement is open for every i in I. Then the union over i in I of F i complement is open by one. Since the union over i in I of F i complement equals the complement of the intersection over i in I of F i, the intersection over i in I of F i is closed by Theorem 2.1.14.

For three, with the standard convention the empty intersection of the U i equals M, if I equals the empty set then the empty intersection of the U i is open. Suppose I is not equal to the empty set and x belongs to the intersection over i in I of U i. Then we have x belongs to U i for every i in I. Since U i is open, there exists r i greater than zero such that the open ball of radius r i about x is contained in U i. Since I is finite, we may let r equal the minimum over i in I of r i. Then the open ball of radius r about x is contained in the intersection over i in I of U i. Hence the intersection over i in I of U i is open.

For four, by Theorem 2.1.14, F i complement is open for every i in I. Then the intersection over i in I of F i complement is open by three. Since the intersection over i in I of F i complement equals the complement of the union over i in I of F i, the union over i in I of F i is closed by Theorem 2.1.14. This completes the proof.
