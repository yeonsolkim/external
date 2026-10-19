---
section: proof-proposition-1-3-7
title: Proof
kind: proof
document: 1.3 Linear Combinations and Spans
url: /2026/06/21/3.-Linear-Combinations-and-Spans.html
source: 3ab1edd6a80a24992fe37bf960071da4ddbf77a5f048d58bd22fe48916189d15
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-19
body: 170c312720ac034f51bf60feeb54f283a03e663941de5b9efb2d1ef3d4d8ded7
words: 552
---

Proof.

First, we proceed by induction on n equals the cardinality of I. If n equals zero, then both sides equal zero in V. Now suppose that the statement holds for n equals k. Let the cardinality of I equal k plus one, and choose i prime in I. Put I prime equals I minus the singleton containing i prime. By Definition 1.3.1, the induction hypothesis, and associativity and commutativity of addition, the sum over i in I of the quantity u i plus v i, equals the quantity u sub i prime plus v sub i prime, plus the sum over i in I prime of the quantity u i plus v i, which equals the quantity u sub i prime plus v sub i prime, plus the quantity the sum over i in I prime of u i, plus the sum over i in I prime of v i, which equals the quantity u sub i prime plus the sum over i in I prime of u i, plus the quantity v sub i prime plus the sum over i in I prime of v i, which equals the sum over i in I of u i, plus the sum over i in I of v i.

Second, we proceed by induction on n equals the cardinality of I. If n equals zero, both sides equal zero in V, since a times zero in V equals zero in V. Now suppose that the statement holds for n equals k. Let the cardinality of I equal k plus one, and choose i prime in I. By Definition 1.3.1, distributivity of scalar multiplication over addition, and the induction hypothesis, a times the sum over i in I of v i, equals a times the quantity v sub i prime plus the sum over i in I minus the singleton containing i prime of v i, which equals a v sub i prime plus a times the sum over i in I minus the singleton containing i prime of v i, which equals a v sub i prime plus the sum over i in I minus the singleton containing i prime of a v i, which equals the sum over i in I of a v i.

Third, we proceed by induction on n equals the cardinality of I. If n equals zero, both sides equal zero in V, since zero times v equals zero in V. Now suppose that the statement holds for n equals k. Let the cardinality of I equal k plus one, and choose i prime in I. By Definition 1.3.1, distributivity with respect to scalar addition, and the induction hypothesis, the quantity the sum over i in I of a i, multiplied by v, equals the quantity a sub i prime plus the sum over i in I minus the singleton containing i prime of a i, multiplied by v, which equals a sub i prime v plus the quantity the sum over i in I minus the singleton containing i prime of a i, multiplied by v, which equals a sub i prime v plus the sum over i in I minus the singleton containing i prime of a i v, which equals the sum over i in I of a i v. This completes the proof.
