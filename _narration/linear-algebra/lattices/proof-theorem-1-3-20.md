---
section: proof-theorem-1-3-20
title: Proof
kind: proof
document: 1.3 Lattices
url: /linear-algebra/lattices/
source: c2e5cb700c385c5b2fd5a90cedb2e75bfc60c415805af5c9535c52a40620d112
skeleton: 4
prompt: lecture-v5
model: gpt-5.5
generated: 2026-11-17
body: 4c174fce7bcc6717542b9df8d6968c37a55507e4e5dec1d2ec8e7fa824e65df8
words: 390
---

Proof. Suppose that L is modular. Since modularity implies upper semimodularity, L is graded by Theorem 1.3.19. Let x and y be in L, and let rho be the rank function on L. Then we have, the interval from x meet y to x is isomorphic to the interval from y to x join y, by Theorem 1.3.14.

Since order isomorphisms preserve covering relations, the lengths of the two intervals are the same. Hence, by Proposition 1.3.17, rho of x minus rho of x meet y, equals the length of the interval from x meet y to x, which equals the length of the interval from y to x join y, which equals rho of x join y minus rho of y, proving that rho is modular.

Conversely, suppose that L is graded and its rank function rho is modular. Let x, y, and z be in L with x less than or equal to z, and let u be x join the quantity y meet z, and v be the meet of the quantity x join y and z. Since x is less than or equal to z and rho is modular, we have, rho of u equals rho of x plus the quantity rho of y meet z minus rho of x meet y, and rho of v equals rho of z minus the quantity rho of y join z minus rho of x join y, and, rho of x equals rho of x meet y plus the quantity rho of x join y minus rho of y.

Therefore rho of u equals rho of x plus the quantity rho of y meet z minus rho of x meet y, which equals rho of x join y plus the quantity rho of y join z minus rho of y, which equals rho of x join y plus the quantity rho of z minus rho of y meet z, which equals rho of v.

If u is less than v, then the length of the interval from u to v is greater than or equal to one, contradicting rho of u equals rho of v. Hence u equals v, so that x join the quantity y meet z, equals the meet of the quantity x join y and z. By Definition 1.3.13, L is modular. This completes the proof.
