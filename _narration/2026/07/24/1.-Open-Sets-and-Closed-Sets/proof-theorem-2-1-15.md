---
section: proof-theorem-2-1-15
title: Proof
kind: proof
document: 2.1 Open Sets and Closed Sets
url: /2026/07/24/1.-Open-Sets-and-Closed-Sets.html
source: 1dc90ad7e2080e626bd425d75fcdcbce43fbac2639898b0e77545f73aeab097b
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-09-29
body: a431b4a19fbcb95dabb27aa056770f4652fc6ab2de766f2881d397d04b1a2478
words: 350
---

Proof. One. Let x belong to the union over i in I of U i. Then we may let x belong to U i for some i in I. Since x is an interior point of U i, x is also an interior point of the union over i in I of U i. Therefore the union over i in I of U i is open.

Two. By Theorem 2.1.14, F i complement is open for every i in I. Then the union over i in I of F i complement is open by part one. Since the union over i in I of F i complement equals the complement of the intersection over i in I of F i, the intersection over i in I of F i is closed by Theorem 2.1.14.

Three. With the standard convention the empty intersection of the U i equals M, if I equals the empty set then the empty intersection of the U i is open. Suppose I is not equal to the empty set and x belongs to the intersection over i in I of U i. Then we have x belongs to U i for every i in I. Since U i is open, there exists r i greater than zero such that the open ball of radius r i about x is contained in U i. Since I is finite, we may let r equal the minimum over i in I of r i. Then the open ball of radius r about x is contained in the intersection over i in I of U i. Hence the intersection over i in I of U i is open.

Four. By Theorem 2.1.14, F i complement is open for every i in I. Then the intersection over i in I of F i complement is open by part three. Since the intersection over i in I of F i complement equals the complement of the union over i in I of F i, the union over i in I of F i is closed by Theorem 2.1.14. This completes the proof.
