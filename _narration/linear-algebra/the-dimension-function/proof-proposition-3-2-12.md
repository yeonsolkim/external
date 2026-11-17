---
section: proof-proposition-3-2-12
title: Proof
kind: proof
document: 3.2 The Dimension Function
url: /linear-algebra/the-dimension-function/
source: 01b10d4fbaae504de96c7481acc2f95dc4e6bf5daef0a32b7f9c6307e3d8e7dd
skeleton: 4
prompt: lecture-v5
model: gpt-5.5
generated: 2026-11-17
body: 42847ca853f8a0f900cafa17ce977f41379143c46e7454d263062ccb0597a8c6
words: 240
---

Proof.

First, since sigma of the empty set equals the zero subspace and rho of the zero subspace equals zero, r of the empty set equals zero.

Second, by Theorem 3.2.5, sigma is monotone. Since rho is also monotone, the composite r is monotone.

Third, since sigma preserves joins and rho is monotone, r of the join of S and T, minus r of S, equals rho of sigma of the join of S and T, minus rho of sigma of S, which equals rho of the join of sigma of S and sigma of T, minus rho of sigma of S, which equals rho of sigma of T, minus rho of the meet of sigma of S and sigma of T.

Moreover, since sigma is monotone, we have, sigma of the meet of S and T, is less than or equal to the meet of sigma of S and sigma of T, by Theorem 1.3.11. It therefore follows from monotonicity of rho that r of the join of S and T, minus r of S, equals rho of sigma of T, minus rho of the meet of sigma of S and sigma of T, which is less than or equal to rho of sigma of T, minus rho of sigma of the meet of S and T, which equals r of T, minus r of the meet of S and T.

Hence r is submodular. This completes the proof.
