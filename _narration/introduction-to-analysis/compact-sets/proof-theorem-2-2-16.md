---
section: proof-theorem-2-2-16
title: Proof
kind: proof
document: 2.2 Compact Sets
url: /2026/07/30/2.-Compact-Sets.html
source: 900e94a4aa5a3387d16d54464944588a761b61899655e06e5cf4a10173e84911
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-21
body: 375cfc9e7bf23c2e79d38aa34f72d8c44d17c83744551867a24ac0238afe156c
words: 379
---

Proof. Let I be a k-cell, consisting of all points x, equal to x one through x k, in R k such that x i belongs to the closed interval from a i to b i for i from one to k. Let the point a equal a one through a k and the point b equal b one through b k, and define delta equals the norm of a minus b. Then, we have the norm of x minus y is less than or equal to delta for every x and y in I. Suppose, for contradiction, that there exists an open cover U of I that has no finite subcover of I. Put c i equal to the quantity a i plus b i, over two, then the intervals the closed interval from a i to c i and the closed interval from c i to b i determine two to the k k-cells, whose union is I. At least one of these sub-cells, call it I one, cannot be covered by any finite subcollection of the cover U. If every sub-cell had a finite subcover, the union of these two to the k finite subcovers would be a finite subcover of I. We subdivide I one and continue the process. Then we obtain a sequence I n with the following properties: Property one: I contains I one, which contains I two, and so on. Property two: the cell I n is not covered by any finite subcollection of the cover U. Property three: if x and y belong to I n, then the norm of x minus y is less than or equal to two to the minus n, times delta.

By Theorem 2.2.15, there is a point c which lies in every I n. Then, there exists U zero in the cover U that contains c. Since U zero is open, there exists r greater than zero such that the ball of radius r about c is contained in U zero. If n is so large that two to the minus n, times delta is less than r, then I n is contained in the ball of radius r about c, which is contained in U zero, which contradicts property two. This completes the proof.
