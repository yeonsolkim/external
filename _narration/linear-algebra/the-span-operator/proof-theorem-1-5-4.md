---
section: proof-theorem-1-5-4
title: Proof
kind: proof
document: 1.5 The Span Operator
url: /linear-algebra/the-span-operator/
source: 486c70a000e94332771c8686768563cbd0c6a3c034c0a765525d0a3846be195b
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-22
body: 4d891cc5ac98ffcb0d77809038caffd698c31688afd55df5ce3f9e82c76237fe
words: 216
---

Proof. Suppose c l is a closure operator on X. Since c l is monotone and idempotent, if S is contained in the closure of T, then the closure of S is contained in the closure of the closure of T, which equals the closure of T. Since c l is extensive, if the closure of S is contained in the closure of T, then S is contained in the closure of S, which is contained in the closure of T. Conversely, suppose star holds for any S and T contained in X. Since the closure of S is contained in the closure of S, we have S is contained in the closure of S; hence c l is extensive. Since c l is extensive, if S is contained in T, then S is contained in the closure of T. Then the closure of S is contained in the closure of T follows from star; c l is monotone. The inclusion, the closure of the closure of S is contained in the closure of S, follows from the closure of S is contained in the closure of S by star. Since extensivity gives the reverse inclusion, the closure of the closure of S equals the closure of S; c l is idempotent. This completes the proof.
