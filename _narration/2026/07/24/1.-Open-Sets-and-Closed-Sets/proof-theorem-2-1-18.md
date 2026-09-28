---
section: proof-theorem-2-1-18
title: Proof
kind: proof
document: 2.1 Open Sets and Closed Sets
url: /2026/07/24/1.-Open-Sets-and-Closed-Sets.html
source: 278603bc0b1c956039ceef3ad75d5d31f60b514d2f5c7eb1a65a863b0cde49fd
skeleton: 4
prompt: lecture-v3
model: gpt-5.5
generated: 2026-09-28
body: a777cf1b678d6c872acaa5fd9eed960a536980c53c2f73899df35387742bc20d
words: 340
---

Proof. Suppose A is contained in N is open in N. Then, every x in A has an open ball in N of radius r x about x contained in A. Define U equals the union over x in A of the ball in M of radius r x about x. Since the ball in N of radius r x about x equals the ball in M of radius r x about x intersect N, we have U intersect N equals the union over x in A of the ball in M of radius r x about x, intersect N, which equals the union over x in A of the quantity the ball in M of radius r x about x intersect N, which equals the union over x in A of the ball in N of radius r x about x. We refer to the preceding identity as star.

It is clear that A is contained in the union over x in A of the ball in N of radius r x about x. Since each ball in N of radius r x about x is contained in A, we also have the union over x in A of the ball in N of radius r x about x is contained in A. Therefore A equals the union over x in A of the ball in N of radius r x about x, which equals U intersect N. Conversely, suppose that A equals U intersect N for some U contained in M open in M. If x is in A then x is in U. Thus every x in A has an open ball in M of radius r about x contained in U. Since the intersection of U with N equals A, the intersection of the ball in M of radius r about x with N is contained in A. Thus, by star, we have the ball in N of radius r about x is contained in A. Therefore A is open in N. This completes the proof.
