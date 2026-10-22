---
section: proof-theorem-1-3-18
title: Proof
kind: proof
document: 1.3 Subspaces
url: /linear-algebra/subspaces/
source: 0a74981f0af76ef79a4e78204f3301582ae22c2bf72e1915b4bcb3f696f021f4
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-22
body: 882bd479a8780250316059db6d0f06a12ef5c1ae62d3ded37a766a2f89f76ae6
words: 666
---

Proof. Suppose the coset u one plus W equals the coset u two plus W, and the coset v one plus W equals the coset v two plus W. Then the equality the quantity u one plus W, plus the quantity v one plus W, equals the quantity u two plus W, plus the quantity v two plus W, holds. Indeed, we have u one minus u two belongs to W and v one minus v two belongs to W. It follows that the quantity u one plus v one, minus the quantity u two plus v two, belongs to W. Since the quantity u one plus W, plus the quantity v one plus W, equals the quantity u one plus v one, plus W, and the quantity u two plus W, plus the quantity v two plus W, equals the quantity u two plus v two, plus W, the two cosets the quantity u one plus W, plus the quantity v one plus W, and the quantity u two plus W, plus the quantity v two plus W, are equal. We now show that for any a in F, a times the quantity u one plus W equals a times the quantity u two plus W. Since the coset u one plus W equals the coset u two plus W, we have u one minus u two belongs to W. Thus a u one minus a u two belongs to W, and this implies a times the quantity u one plus W equals a times the quantity u two plus W. Thus both operations are well-defined.

We now verify the vector space axioms. The operations are closed on V modulo W by Definition 1.3.17. For u, v, z in V, associativity and commutativity of addition follow from those in V: the quantity, the quantity u plus W, plus the quantity v plus W, then plus the quantity z plus W, equals the quantity, the quantity u plus v, then plus z, plus W, which equals the quantity, u plus the quantity v plus z, plus W, which equals the quantity u plus W, plus the quantity, the quantity v plus W, plus the quantity z plus W; and the quantity u plus W, plus the quantity v plus W, equals the quantity u plus v, plus W, which equals the quantity v plus u, plus W, which equals the quantity v plus W, plus the quantity u plus W.

The coset W is the additive identity, and minus v plus W is the additive inverse of the coset v plus W: the quantity v plus W, plus W, equals v plus W, and the quantity v plus W, plus the quantity minus v plus W, equals the quantity v minus v, plus W, which equals W.

Finally, for a, b in F, the scalar multiplication axioms follow from the corresponding axioms in V: one times the quantity v plus W equals the quantity one v, plus W, which equals v plus W; the scalar a b times the quantity v plus W equals the quantity, a b times v, plus W, which equals the quantity a times b v, plus W, which equals a times the quantity b times the quantity v plus W; a times the quantity, the quantity u plus W, plus the quantity v plus W, equals the quantity a times the quantity u plus v, plus W, which equals the quantity a u plus a v, plus W, which equals a times the quantity u plus W, plus a times the quantity v plus W; and the quantity a plus b, times the quantity v plus W, equals the quantity, the quantity a plus b times v, plus W, which equals the quantity a v plus b v, plus W, which equals a times the quantity v plus W, plus b times the quantity v plus W. Therefore V modulo W is a vector space over F. This completes the proof.
