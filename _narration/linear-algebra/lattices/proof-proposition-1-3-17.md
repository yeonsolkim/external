---
section: proof-proposition-1-3-17
title: Proof
kind: proof
document: 1.3 Lattices
url: /linear-algebra/lattices/
source: 6bc04e47cbaca2f90ae9e3550e8ee413bc9b3a966a0c0493f64fb7afc2bba630
skeleton: 4
prompt: lecture-v5
model: gpt-5.5
generated: 2026-11-17
body: cede38e671c7ea5ea269da495a1fe9bffb4218918f716688f4c4fc6c3915028a
words: 385
---

Proof. Suppose L is graded and rho from L to the nonnegative integers is a rank function on L. Let I equal the interval from a to b be any interval in L and C be a maximal chain in I. Then a and b are the minimum and maximum of C, respectively. Furthermore, since C has the form, a equals x zero, which is covered by x one, which is covered by, and so on, up to x sub the length of C, which equals b, we have the length of C equals rho of b minus rho of a. It follows that the length of the interval from a to b equals the length of C, which equals rho of b minus rho of a. Hence all maximal chains in the interval I have the same length. Furthermore, we have rho of x equals the length of the interval from zero to x, plus rho of zero, which equals the length of the interval from zero to x, for all x in L, which implies that a rank function is unique. Conversely, suppose that all maximal chains in any interval in L have the same length. Define rho of hat zero equals zero. For each interval from zero to x in L, define rho of x equals the length of the interval from zero to x. Let x and y belong to L such that x is covered by y and let C be a maximal chain in the interval from zero to x. Then, C prime equals C disjoint union the singleton y is a maximal chain in the interval from zero to y. It follows from Proposition 1.3.3 that the length of the interval from zero to y equals the length of C prime, which equals the cardinality of C prime minus one, which equals the cardinality of C, which equals the length of C plus one, which equals the length of the interval from zero to x plus one. Therefore rho of y equals rho of x plus the quantity the length of the interval from zero to y minus the length of the interval from zero to x, which equals rho of x plus one. Hence rho is the rank function and L is graded. This completes the proof.
