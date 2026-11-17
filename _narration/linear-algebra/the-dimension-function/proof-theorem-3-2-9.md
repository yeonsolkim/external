---
section: proof-theorem-3-2-9
title: Proof
kind: proof
document: 3.2 The Dimension Function
url: /linear-algebra/the-dimension-function/
source: 3eaab63b01fba4fbb217d97d3b44b89eae4f93e59cc98745dc5cf2fca02c1557
skeleton: 4
prompt: lecture-v5
model: gpt-5.5
generated: 2026-11-17
body: 22a34dd9bf0670bed2545d262504200df49a4a19a09eb70034178c730adcba1c
words: 207
---

Proof. The empty set is a basis for the zero subspace, so rho of the zero subspace equals dimension of the zero subspace equals zero. Now suppose U and W belong to the subspaces of V and U is covered by W. Let B be a basis for U. Since B is a linearly independent subset of W, there exists a basis C for W such that B is contained in C by Theorem 3.1.13. Moreover, we have B is properly contained in C, since otherwise B equals C so that U equals W. Suppose, for the sake of contradiction, that the size of C is greater than the size of B plus one. Then, there exist c in C minus B, so that W prime equals the span of B union the singleton c becomes a subspace satisfying U is properly contained in W prime, which is properly contained in W. This contradicts to our assumption that W is the immediate successor of U. It therefore follows that the size of C equals the size of B plus one, proving rho of W equals rho of U plus one. By Definition 1.3.16, rho is the rank function on the subspaces of V. This completes the proof.
