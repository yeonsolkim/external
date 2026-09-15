---
section: theorem-2-1-14
title: Theorem 2.1.14
kind: theorem
document: 2.1. Open Sets and Closed Sets
url: /2026/07/24/1.-Open-Sets-and-Closed-Sets.html
source: 0fbb89822a618e8ab2fd39299ad6b945bdb0dc666989af2efd318d86cd62b82c
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-15
body: ae685f00e89b1bf48dba1aeda7d1d79373c14f658fe273d6e92bf10a96815969
words: 179
---

Theorem 2.1.14. Let M be a metric space, and let A be contained in M. A is open if and only if A complement is closed.

Proof. Suppose that A is open and x belongs to A. Then we can choose r greater than zero so that the open ball of radius r about x is contained in A. It follows that the punctured open ball of radius r about x intersect A complement equals the empty set, so x is not a limit point of A complement. Hence every limit point of A complement is a member of A complement, and thus A complement is closed. Conversely, suppose that A complement is closed and let x belong to A. Then x is not a limit point of A complement. Hence we can choose r greater than zero so that the punctured open ball of radius r about x intersect A complement equals the empty set. It follows that the open ball of radius r about x is contained in A. Therefore A is open. This completes the proof.
