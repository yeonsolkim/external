---
section: proof-proposition-1-3-7
title: Proof
kind: proof
document: 1.3 Lattices
url: /linear-algebra/lattices/
source: 2ee24103564e6f403017c2cf5b5f89b88616d6146f93f201bfc7926e56bb8f32
skeleton: 4
prompt: lecture-v5
model: gpt-5.5
generated: 2026-11-17
body: befcee7a06242150f0689344b21760999db39af921cec2bd7859e8aaf617a4cd
words: 272
---

Proof. We define a relation less than or equal to on S by, x is less than or equal to y if and only if y equals x join y, for all x and y in S. Then less than or equal to is an order on S and makes x join y the supremum for the set x and y for all x and y in S. Conversely, suppose that S is partially ordered by less than or equal to and any pair of two elements x and y of S has a supremum x join y. Let the quantity x join y, joined with z, equal alpha. Then x join y is less than or equal to alpha and z is less than or equal to alpha, so alpha is an upper bound for the set x, y, and z. Suppose beta is an upper bound for the set x, y, and z. It follows that x join y is less than or equal to beta and z is less than or equal to beta. Since the quantity x join y, joined with z, equals alpha, we have alpha is less than or equal to beta. Therefore alpha is the supremum for the set x, y, and z. Similarly, x join the quantity y join z is the supremum for the set x, y, and z, so that x join the quantity y join z, equals alpha. Hence join is associative. By definition, join is commutative. Furthermore, since x is the supremum for the set x, join is idempotent. Therefore S with join is a semilattice. This completes the proof.
