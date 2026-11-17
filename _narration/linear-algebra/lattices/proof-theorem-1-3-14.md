---
section: proof-theorem-1-3-14
title: Proof
kind: proof
document: 1.3 Lattices
url: /linear-algebra/lattices/
source: 90494e5dbffe50be8e789bf1179e5e6a72decd17b4d814b1f21f15c983764fd1
skeleton: 4
prompt: lecture-v5
model: gpt-5.5
generated: 2026-11-17
body: 03bc73428ef50b585351270708c346c50907344a23231bf9c9184fe733dba106
words: 249
---

Proof. Let x and y belong to L and define f from the interval from x meet y to x, to the interval from y to x join y, by s maps to s join y, and g from the interval from y to x join y, to the interval from x meet y to x, by t maps to t meet x.

Since f is monotone, f of s belongs to the interval from y to x join y, for all s in the interval from x meet y to x. Similarly, since g is monotone, g of t belongs to the interval from x meet y to x, for all t in the interval from y to x join y. Hence the functions are well-defined. Furthermore, by modularity of L, we have, g of f of s, equals the meet of s join y with x, which equals s join the meet of y and x, which equals s, and f of g of t, equals the join of t meet x with y, which equals t meet the join of x and y, which equals t, for all s in the interval from x meet y to x and t in the interval from y to x join y. Thus f and g are mutually inverse bijections. Since both maps are monotone, f is an order isomorphism. An order isomorphism between lattices preserves joins and meets, so f is a lattice isomorphism. This completes the proof.
