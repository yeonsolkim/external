---
section: proof-theorem-1-2-17
title: Proof
kind: proof
document: 1.2 Subspaces
url: /2026/06/18/2.-Subspaces.html
source: e0a78c76354d125ab2ec391361812f4b635322e3594be82b9c1a81c557f0966f
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-01
body: 8fe14db1b341994c03f4f39e54a00deb192c6819c929bda36f5822d7b1e89250
words: 695
---

Proof. Suppose u one plus W equals u two plus W and v one plus W equals v two plus W. Then the equality, the sum of the coset u one plus W and the coset v one plus W equals the sum of the coset u two plus W and the coset v two plus W, holds.

Indeed, we have u one minus u two belongs to W and v one minus v two belongs to W. It follows that the quantity u one plus v one, minus the quantity u two plus v two, belongs to W. Since the sum of the coset u one plus W and the coset v one plus W equals the coset represented by u one plus v one, and the sum of the coset u two plus W and the coset v two plus W equals the coset represented by u two plus v two, the two cosets, the sum of the coset u one plus W and the coset v one plus W, and the sum of the coset u two plus W and the coset v two plus W, are equal. We now show that for any a in F, a times the coset u one plus W equals a times the coset u two plus W.

Since u one plus W equals u two plus W, we have u one minus u two belongs to W. Thus a u one minus a u two belongs to W, and this implies a times the coset u one plus W equals a times the coset u two plus W. Thus both operations are well-defined. We now verify the vector space axioms. The operations are closed on V modulo W by Definition 1.2.16. For u, v, z in V, associativity and commutativity of addition follow from those in V: the sum of the sum of the coset u plus W and the coset v plus W, with the coset z plus W, equals the coset represented by the quantity u plus v, plus z, which equals the coset represented by u plus the quantity v plus z, which equals the sum of the coset u plus W and the sum of the coset v plus W and the coset z plus W; and the sum of the coset u plus W and the coset v plus W equals the coset represented by u plus v, which equals the coset represented by v plus u, which equals the sum of the coset v plus W and the coset u plus W.

The coset W is the additive identity, and negative v plus W is the additive inverse of v plus W: the sum of the coset v plus W and the coset W equals v plus W, and the sum of the coset v plus W and the coset negative v plus W equals the coset represented by v minus v, which equals W.

Finally, for a, b in F, the scalar multiplication axioms follow from the corresponding axioms in V: one times the coset v plus W equals the coset represented by one v, which equals v plus W; the quantity a b, times the coset v plus W, equals the coset represented by the quantity a b, times v, which equals the coset represented by a times the quantity b v, which equals a times the quantity b times the coset v plus W; a times the sum of the coset u plus W and the coset v plus W equals the coset represented by a times the quantity u plus v, which equals the coset represented by a u plus a v, which equals a times the coset u plus W plus a times the coset v plus W; and the quantity a plus b, times the coset v plus W, equals the coset represented by the quantity a plus b, times v, which equals the coset represented by a v plus b v, which equals a times the coset v plus W plus b times the coset v plus W.

Therefore V modulo W is a vector space over F. This completes the proof.
