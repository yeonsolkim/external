---
section: proof-theorem-2-1-18
title: Proof
kind: proof
document: 2.1 Open Sets and Closed Sets
url: /2026/07/24/1.-Open-Sets-and-Closed-Sets.html
source: 278603bc0b1c956039ceef3ad75d5d31f60b514d2f5c7eb1a65a863b0cde49fd
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-07
body: 493c66f46db55068c1f030a261f09675418963fb49a3174549167d4e295744f1
words: 365
---

Proof. Suppose A, contained in N, is open in N. Then, every x in A has an open ball, the ball in N of radius r sub x about x, contained in A. Define U to be the union over x in A of the ball in M of radius r sub x about x. Since the ball in N of radius r sub x about x equals the intersection of the ball in M of radius r sub x about x with N, we have U intersect N equals the intersection of the union over x in A of the ball in M of radius r sub x about x with N, which equals the union over x in A of the intersection of the ball in M of radius r sub x about x with N, which equals the union over x in A of the ball in N of radius r sub x about x. We refer to the identity relating the two balls as star. It is clear that A is contained in the union over x in A of the ball in N of radius r sub x about x. Since each ball in N of radius r sub x about x is contained in A, we also have the union over x in A of the ball in N of radius r sub x about x is contained in A. Therefore A equals the union over x in A of the ball in N of radius r sub x about x, which equals U intersect N. Conversely, suppose that A equals U intersect N for some U contained in M, open in M. If x is in A then x is in U. Thus every x in A has an open ball, the ball in M of radius r about x, contained in U. Since the intersection of U with N equals A, the intersection of the ball in M of radius r about x with N is contained in A. Thus, by star, we have the ball in N of radius r about x is contained in A. Therefore A is open in N. This completes the proof.
