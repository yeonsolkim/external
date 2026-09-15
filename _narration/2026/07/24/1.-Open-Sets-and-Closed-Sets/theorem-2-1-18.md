---
section: theorem-2-1-18
title: Theorem 2.1.18
kind: theorem
document: 2.1. Open Sets and Closed Sets
url: /2026/07/24/1.-Open-Sets-and-Closed-Sets.html
source: ebd946869f43f320af65caefefc36a157c562e177c1d4bff5cfa86095fdd5523
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-15
body: dff5b482c08573f0824261062b46e0ae3d8660af35626b7ef4a04cfef59f5caa
words: 390
---

Theorem 2.1.18. Let M be a metric space, and regard N contained in M as a metric space with the restricted metric. Then a subset A of N is open in N if and only if A equals U intersect N for some U open in M.

Proof. Suppose A contained in N is open in N. Then, every x in A has an open ball, the ball in N of radius r x about x, contained in A. Define U equal to the union over x in A of the ball in M of radius r x about x. Since the ball in N of radius r x about x equals the ball in M of radius r x about x intersect N, we have U intersect N equals the union over x in A of the ball in M of radius r x about x, intersect N, which equals the union over x in A of the quantity the ball in M of radius r x about x intersect N, which equals the union over x in A of the ball in N of radius r x about x. We refer to the preceding identity as star.

It is clear that A is contained in the union over x in A of the ball in N of radius r x about x. Since each ball in N of radius r x about x is contained in A, we also have the union over x in A of the ball in N of radius r x about x is contained in A. Therefore A equals the union over x in A of the ball in N of radius r x about x, which equals U intersect N. Conversely, suppose that A equals U intersect N for some U contained in M open in M. If x belongs to A then x belongs to U. Thus every x in A has an open ball, the ball in M of radius r about x, contained in U. Since the intersection of U with N equals A, the intersection of the ball in M of radius r about x with N is contained in A. Thus, by star, we have the ball in N of radius r about x contained in A. Therefore A is open in N. This completes the proof.
