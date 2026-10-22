---
section: proof-proposition-1-4-7
title: Proof
kind: proof
document: 1.4 Linear Combinations and Spans
url: /linear-algebra/linear-combinations-and-spans/
source: c4d882da2005e30aadf828e4cfe02021c69691786daab7975f1c264f40d8c3a2
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-22
body: 2fa6eca13cea113656d9125dc270db5434791999042d26a76e2a843b63ac1087
words: 564
---

Proof. First, we proceed by induction on n equals the cardinality of I. If n equals zero, then both sides equal zero in V. Now suppose that the statement holds for n equals k. Let the cardinality of I equal k plus one, and choose i prime in I. Put I prime equal to I set minus the singleton i prime. By Definition 1.4.1, the induction hypothesis, and associativity and commutativity of addition, we have the sum over i in I of the quantity u i plus v i equals the quantity u sub i prime plus v sub i prime, plus the sum over i in I prime of the quantity u i plus v i, which equals the quantity u sub i prime plus v sub i prime, plus the quantity the sum over i in I prime of u i plus the sum over i in I prime of v i, which equals the quantity u sub i prime plus the sum over i in I prime of u i, plus the quantity v sub i prime plus the sum over i in I prime of v i, which equals the sum over i in I of u i plus the sum over i in I of v i.

Second, we proceed by induction on n equals the cardinality of I. If n equals zero, both sides equal zero in V, since a times zero in V equals zero in V. Now suppose that the statement holds for n equals k. Let the cardinality of I equal k plus one, and choose i prime in I. By Definition 1.4.1, distributivity of scalar multiplication over addition, and the induction hypothesis, we have a times the sum over i in I of v i equals a times the quantity v sub i prime plus the sum over i in I set minus the singleton i prime of v i, which equals a times v sub i prime plus a times the sum over i in I set minus the singleton i prime of v i, which equals a times v sub i prime plus the sum over i in I set minus the singleton i prime of a times v i, which equals the sum over i in I of a times v i.

Third, we proceed by induction on n equals the cardinality of I. If n equals zero, both sides equal zero in V, since zero times v equals zero in V. Now suppose that the statement holds for n equals k. Let the cardinality of I equal k plus one, and choose i prime in I. By Definition 1.4.1, distributivity with respect to scalar addition, and the induction hypothesis, we have the quantity the sum over i in I of a i, times v, equals the quantity a sub i prime plus the sum over i in I set minus the singleton i prime of a i, times v, which equals a sub i prime times v plus the quantity the sum over i in I set minus the singleton i prime of a i, times v, which equals a sub i prime times v plus the sum over i in I set minus the singleton i prime of a i times v, which equals the sum over i in I of a i times v. This completes the proof.
