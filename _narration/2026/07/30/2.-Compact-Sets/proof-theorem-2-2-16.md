---
section: proof-theorem-2-2-16
title: Proof
kind: proof
document: 2.2 Compact Sets
url: /2026/07/30/2.-Compact-Sets.html
source: 20d7b27582f1b5407c7e96432636bc8b24c444592f2f5bf27dce11583a78445c
skeleton: 4
prompt: lecture-v3
model: gpt-5.5
generated: 2026-09-28
body: 6fba5091dcef7c497f03770550fcee5d86e63da27617faa49d1f0bb6881820e8
words: 377
---

Proof. Let I be a k cell, consisting of all points x, equal to x one through x k, in R k, such that x i belongs to the closed interval from a i to b i for i from one to k. Let a equal a one through a k and b equal b one through b k, and define delta equals the norm of a minus b. Then, we have the norm of x minus y is less than or equal to delta for every points x and y in I. Suppose, for contradiction, that there exists an open cover U of I that has no finite subcover of I. Put c i equals the quantity a i plus b i, over two, then the intervals the closed interval from a i to c i and the closed interval from c i to b i determine two to the k k cells, whose union is I. At least one of these sub-cells, call it I one, cannot be covered by any finite subcollection of the cover U. If every sub-cell had a finite subcover, the union of these two to the k finite subcovers would be a finite subcover of I. We subdivide I one and continue the process. Then we obtain the sequence I n with the following properties:

Property one: I contains I one, which contains I two, and so on.

Property two: I n is not covered by any finite subcollection of the cover U.

Property three: if points x and y belong to I n, then the norm of x minus y is less than or equal to two to the minus n, times delta.

By Theorem 2.2.15, there is a point c which lies in every I n. Then, there exists U zero belonging to the cover U that contains c. Since U zero is open, there exists r greater than zero such that the ball of radius r about c is contained in U zero. If n is so large that two to the minus n, times delta is less than r, then I n is contained in the ball of radius r about c, which is contained in U zero, which contradicts property two. This completes the proof.
