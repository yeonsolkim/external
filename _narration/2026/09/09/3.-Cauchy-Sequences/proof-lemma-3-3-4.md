---
section: proof-lemma-3-3-4
title: Proof
kind: proof
document: 3.3 Cauchy Sequences
url: /2026/09/09/3.-Cauchy-Sequences.html
source: 16c11fcca8622cf56e833f91aa937a8369d164e92233e23488340a3de30a1b94
skeleton: 4
prompt: lecture-v3
model: gpt-5.5
generated: 2026-09-28
body: 817383c660bf76583982cae7f2034b747789a6b9646143b4a8016d94c3598f2a
words: 258
---

Proof. One. Let epsilon greater than zero be given, and let x and y belong to closure of A. Then there exist points x prime and y prime in A such that d of x, x prime is less than epsilon and d of y, y prime is less than epsilon. Hence, we have d of x, y is less than or equal to d of x, x prime plus d of x prime, y prime plus d of y prime, y, which is less than d of x prime, y prime plus two epsilon, which is less than or equal to diameter of A plus two epsilon.

It follows that d of x, y is less than diameter of A. Therefore diameter of closure of A is less than or equal to diameter of A. Since A is contained in closure of A, it is clear that diameter of A is less than or equal to diameter of closure of A. Consequently, diameter of closure of A equals diameter of A. Two. By Corollary 2.2.12, the intersection of the K n is nonempty. If x and y belong to the intersection of the K n with x not equal to y, then diameter of K n is greater than d of x, y, which is greater than zero, for every n in the positive integers. This contradicts the limit as n goes to infinity of diameter of K n equals zero. Therefore the intersection of the K n consists of exactly one point. This completes the proof.
