---
section: proof-theorem-1-2-18
title: Proof
kind: proof
document: 1.2 Subspaces
url: /2026/06/18/2.-Subspaces.html
source: cdd3369021a9da9487e7f0106f9e9d400535e3bffd5756101de5ba3335ce3cda
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-06
body: 6f9c470b0a5adf3f9713e47aa0dd67c8a2902f8ac6eec881e522dc7141be244e
words: 642
---

Proof. Suppose u one plus W equals u two plus W and v one plus W equals v two plus W. Then the equality the coset u one plus W, plus the coset v one plus W, equals the coset u two plus W, plus the coset v two plus W, holds. Indeed, we have u one minus u two belongs to W and v one minus v two belongs to W. It follows that the quantity u one plus v one, minus the quantity u two plus v two, belongs to W. Since the coset u one plus W, plus the coset v one plus W, equals the quantity u one plus v one, plus W, and the coset u two plus W, plus the coset v two plus W, equals the quantity u two plus v two, plus W, the two cosets, the coset u one plus W, plus the coset v one plus W, and the coset u two plus W, plus the coset v two plus W, are equal. We now show that for any a in F, a times the coset u one plus W equals a times the coset u two plus W. Since u one plus W equals u two plus W, we have u one minus u two belongs to W. Thus a u one minus a u two belongs to W, and this implies a times the coset u one plus W equals a times the coset u two plus W. Thus both operations are well-defined. We now verify the vector space axioms. The operations are closed on V modulo W by Definition 1.2.17. For u, v, and z in V, associativity and commutativity of addition follow from those in V: the quantity the coset u plus W plus the coset v plus W, plus the coset z plus W, equals the quantity u plus v, plus z, plus W, which equals the quantity u plus the quantity v plus z, plus W, which equals the coset u plus W, plus the quantity the coset v plus W plus the coset z plus W; and the coset u plus W, plus the coset v plus W, equals the quantity u plus v, plus W, which equals the quantity v plus u, plus W, which equals the coset v plus W, plus the coset u plus W.

The coset W is the additive identity, and negative v plus W is the additive inverse of v plus W: the coset v plus W, plus W, equals v plus W, and the coset v plus W, plus the coset negative v plus W, equals the quantity v minus v, plus W, which equals W.

Finally, for a and b in F, the scalar multiplication axioms follow from the corresponding axioms in V: one times the coset v plus W equals one v plus W, which equals v plus W; the product a b times the coset v plus W equals the product a b times v, plus W, which equals a times b v, plus W, which equals a times the quantity b times the coset v plus W; a times the quantity the coset u plus W plus the coset v plus W, equals a times the quantity u plus v, plus W, which equals the quantity a u plus a v, plus W, which equals a times the coset u plus W, plus a times the coset v plus W; and the quantity a plus b times the coset v plus W, equals the quantity a plus b times v, plus W, which equals the quantity a v plus b v, plus W, which equals a times the coset v plus W, plus b times the coset v plus W.

Therefore V modulo W is a vector space over F. This completes the proof.
