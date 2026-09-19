---
section: lemma-3-3-4
title: Lemma 3.3.4
kind: lemma
document: 3.3 Cauchy Sequences
url: /2026/09/09/3.-Cauchy-Sequences.html
source: 5ef3b3df551aa18832b13304bb13fea7a8f840a6dd92ddaad2042ead35add406
skeleton: 3
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-19
body: db5a535287cc1684063c16f22809af6df8d4881d08208a0e12782b8a5d5c1b86
words: 376
---

Lemma 3.3.4. Let M be a metric space. Then the following hold.

First, let A be a subset of M. Then, the diameter of closure of A equals the diameter of A.

Second, let the sequence K n be a sequence of nonempty compact sets in M such that K n plus one is contained in K n for n equals one, two, three, and so on. If the limit as n tends to infinity of the diameter of K n equals zero, then the intersection of the K n consists of one point.

Proof. For part one, let epsilon be greater than zero be given, and let x and y belong to closure of A. Then there exist points x prime and y prime in A such that d of x comma x prime is less than epsilon and d of y comma y prime is less than epsilon. Hence, we have d of x comma y is less than or equal to d of x comma x prime plus d of x prime comma y prime plus d of y prime comma y, which is less than d of x prime comma y prime plus two epsilon, which is less than or equal to the diameter of A plus two epsilon.

It follows that d of x comma y is less than the diameter of A. Therefore the diameter of closure of A is less than or equal to the diameter of A. Since A is contained in closure of A, it is clear that the diameter of A is less than or equal to the diameter of closure of A. Consequently, the diameter of closure of A equals the diameter of A. For part two, by Corollary 2.2.12, the intersection of the K n is nonempty. If x and y belong to the intersection of the K n with x not equal to y, then the diameter of K n is greater than d of x comma y, which is greater than zero, for every n in the positive integers. This contradicts the limit as n tends to infinity of the diameter of K n equals zero. Therefore the intersection of the K n consists of exactly one point. This completes the proof.
