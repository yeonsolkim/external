---
section: theorem-3-4-5
title: Theorem 3.4.5
kind: theorem
document: 3.4. Upper and Lower Limits
url: /2026/09/12/4.-Upper-and-Lower-Limits.html
source: a3874aa5561595ea2e53ede07574522c80250c1c239103903caab7fcd32c574c
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-17
body: f80148eb3b92a0d6dc1f6a7c15daa595f65cd376e246db1874fa774e8c74076c
words: 243
---

Theorem 3.4.5. Let x n be a sequence in R and let y belong to R.

First, if y is greater than the limit superior of x n, then eventually x n is less than y.

Second, if y is less than the limit inferior of x n, then eventually x n is greater than y.

Proof. First, let S be the set of every supremum s k for the set of x n such that n is greater than or equal to k. Since y is greater than the infimum of S, y is not a lower bound for S. So there exists k zero such that s sub k zero is less than y. Then y is an upper bound for the k zero-th tail. Since s k is monotonically decreasing, n greater than or equal to k zero implies x n is less than y.

Second, let T be the set of every infimum t k for the set of x n such that n is greater than or equal to k. Since y is less than the supremum of T, y is not an upper bound for T. So there exists k zero such that t sub k zero is greater than y. Then y is a lower bound for the k zero-th tail. Since t k is monotonically increasing, n greater than or equal to k zero implies x n is greater than y. This completes the proof.
