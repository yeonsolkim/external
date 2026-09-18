---
section: theorem-3-4-6
title: Theorem 3.4.6
kind: theorem
document: 3.4. Limit Superior and Limit Inferior
url: /2026/09/12/4.-Limit-Superior-and-Limit-Inferior.html
source: 8f51600d9f3e305b5349695c73bf42cf369cf9087eb8d80ecb4e1a66a6ff4adf
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-18
body: 759ee51f4c2e1622ad9dda5f8d93874203e969211e9edc97216412c47b36609c
words: 150
---

Theorem 3.4.6. Let x n be a sequence in R and let x belong to R. Then x n converges to x if and only if the lim sup of x n equals the lim inf of x n equals x.

Proof. Let A be the set of all extended subsequential limits of x n. If x n tends to x, then every subsequential limit of x n is x. Hence A equals the singleton x, so that max A equals min A equals x. Suppose, conversely, that the limit superior and limit inferior of x n are both x. Then for any epsilon greater than zero, eventually x minus epsilon is less than x n, which is less than x plus epsilon, by Theorem 3.4.5. That is, the absolute value of x n minus x is less than epsilon. Hence x n tends to x. This completes the proof.
