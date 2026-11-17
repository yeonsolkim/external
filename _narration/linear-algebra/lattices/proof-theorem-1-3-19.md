---
section: proof-theorem-1-3-19
title: Proof
kind: proof
document: 1.3 Lattices
url: /linear-algebra/lattices/
source: 46406eb420591a4db57959335abaeb5c0b74011152c02beb726e84b81d9e16fe
skeleton: 4
prompt: lecture-v5
model: gpt-5.5
generated: 2026-11-17
body: 9f4f8098786424b9a576f185dd6214fdf2c2fdb71dfe80ce4fb00db81e6299d2
words: 861
---

Proof. Suppose that L is upper semimodular. We first prove that L is graded. Let I, equal to the interval from a to b, be an interval in L. We show, by induction on the length of I, that all maximal chains in I have the same length. The assertion is immediate if the length of I is less than or equal to one. Suppose that the length of I is greater than or equal to two and that the assertion holds for every interval of smaller length. Let C and D be maximal chains in I, and let u and v be their respective immediate successors of a. Thus a is covered by u and a is covered by v. If u equals v, the induction hypothesis applied to the interval from u to b gives the length of C equals the length of D. Suppose instead that u is not equal to v. Since both u and v cover a, we have u meet v equals a. By upper semimodularity, u is covered by u join v and v is covered by u join v. Put w equals u join v. Since w is less than or equal to b, the intervals from u to b, from v to b, and from w to b all have length smaller than the length of I. By the induction hypothesis, all maximal chains in each of these intervals have the same length. Consequently, the length of C equals one plus the length of the interval from u to b, which equals two plus the length of the interval from w to b, and, similarly, the length of D equals one plus the length of the interval from v to b, which equals two plus the length of the interval from w to b.

Hence the length of C equals the length of D. By induction, all maximal chains in every interval of L have the same length. It follows from Proposition 1.3.17 that L is graded. We now prove that its rank function rho is submodular. First, observe that if u is covered by v, then, for any z in L, u join z equals v join z, or u join z is covered by v join z. Indeed, since u is less than or equal to v meet the quantity u join z, which is less than or equal to v, we have either v meet the quantity u join z, equals v, or v meet the quantity u join z, equals u. In the first case, v is less than or equal to u join z, so that u join z equals v join z. In the second case, upper semimodularity gives u join z is covered by v join the quantity u join z, which equals v join z.

Now let x and y belong to L, and choose a maximal chain in the interval from x meet y to x, say x meet y equals x zero, which is covered by x one, and so on, up to x k, which equals x. Since L is graded, we have k equals rho of x, minus rho of the quantity x meet y. For each i equals zero through k, put y i equals x i join y. The preceding observation shows that, for every i equals one through k, either y sub the quantity i minus one, equals y i, or y sub the quantity i minus one is covered by y i. Consequently, rho of y i, minus rho of y sub the quantity i minus one, is less than or equal to one. Since y zero equals y and y k equals x join y, it follows that rho of the quantity x join y, minus rho of y, equals the sum from i equals one to k of the quantity rho of y i, minus rho of y sub the quantity i minus one, which is at most k, which equals rho of x, minus rho of the quantity x meet y.

Therefore rho is submodular. Conversely, suppose that L is graded and its rank function rho is submodular. Let x and y belong to L satisfy x meet y is covered by x. Then, by submodularity, rho of the quantity x join y, minus rho of y, is less than or equal to rho of x, minus rho of the quantity x meet y, which equals one. Furthermore, x is not less than or equal to y, since otherwise x meet y equals x, contradicting x meet y is covered by x. Thus y is less than x join y, and Proposition 1.3.17 gives zero is less than rho of the quantity x join y, minus rho of y, which is less than or equal to one. Since the rank function takes integer values, we conclude that rho of the quantity x join y, minus rho of y, equals one. By Proposition 1.3.17, the length of the interval from y to x join y, equals one, so y is covered by x join y. Hence L is upper semimodular. This completes the proof.
