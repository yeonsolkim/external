---
section: proof-proposition-1-3-2
title: Proof
kind: proof
document: 1.3 Linear Combinations and Spans
url: /2026/06/21/3.-Linear-Combinations-and-Spans.html
source: 3385fccc04c7c32ac5cd9f67a433d65c6e639cfa78ab42567f912a76fb50f262
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-19
body: 3d73186eb4e8aab8fad4d9ba1609930f3007950f1b915a4ef84973e2c303abca
words: 274
---

Proof. We proceed by strong induction on n equals the cardinality of I. If n equals zero, then I equals the empty set, and the recursive rules uniquely determine the sum to be zero in M. Now let n be greater than or equal to one, and suppose that the recursive rules determine a unique element of M for every family indexed by a set of cardinality less than n. Let the cardinality of I equal n. For any j in I, the induction hypothesis and closedness under addition guarantees that x j plus the sum over i in I set minus the singleton j of x i is a well-defined element of M. It remains to show that this element is independent of the choice of j. Let j and k belong to I. If j equals k, there is nothing to prove. Otherwise, define R equals I set minus the set containing j and k. Since R, I set minus the singleton j, and I set minus the singleton k all have cardinality less than n, their sums are uniquely determined by the induction hypothesis. Hence, by Definition 1.3.1 and associativity and commutativity of addition, x j plus the sum over i in I set minus the singleton j of x i, equals x j plus the quantity x k plus the sum over i in R of x i, which equals x k plus the quantity x j plus the sum over i in R of x i, which equals x k plus the sum over i in I set minus the singleton k of x i. This completes the proof.
