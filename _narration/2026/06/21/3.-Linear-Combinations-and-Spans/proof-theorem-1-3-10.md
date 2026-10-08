---
section: proof-theorem-1-3-10
title: Proof
kind: proof
document: 1.3 Linear Combinations and Spans
url: /2026/06/21/3.-Linear-Combinations-and-Spans.html
source: 486c70a000e94332771c8686768563cbd0c6a3c034c0a765525d0a3846be195b
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-08
body: c3d4be6b62b828d2797edd7637fe08daf23b15212610b04ecea13a5e04e93602
words: 209
---

Proof. Suppose closure is a closure operator on X. Since closure is monotone and idempotent, if S is contained in the closure of T, then the closure of S is contained in the closure of the closure of T, which equals the closure of T. Since closure is extensive, if the closure of S is contained in the closure of T, then S is contained in the closure of S, which is contained in the closure of T. Conversely, suppose star holds for any S and T subsets of X. Since the closure of S is contained in the closure of S, we have S is contained in the closure of S; hence closure is extensive. Since closure is extensive, if S is contained in T, then S is contained in the closure of T. Then the closure of S is contained in the closure of T follows from star; closure is monotone. The inclusion the closure of the closure of S is contained in the closure of S follows from the closure of S is contained in the closure of S by star. Since extensivity gives the reverse inclusion, the closure of the closure of S equals the closure of S; closure is idempotent. This completes the proof.
