---
section: proof-corollary-1-4-6
title: Proof
kind: proof
document: 1.4 Linear Combinations and Spans
url: /linear-algebra/linear-combinations-and-spans/
source: 1ed9385af956c8266de77312b04400e60b2f80c8d50a38141bc3c0913cbd57ac
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-22
body: 7aefaf2f81e0c4e7557be5d5cbc4260161f597020f1a4438614b7e9f9b537d0b
words: 214
---

Proof. Let I equal the set consisting of zero through n and define f from K to I, the pair i j maps to i.

By Theorem 1.4.4, the sum over k in K of x k equals the sum from i equals zero to n of the sum over k in f inverse of i of x k.

Let J i equal the set consisting of i through n and define varphi i from J i to f inverse of i, j maps to the pair i j.

Since varphi i is bijective, by Corollary 1.4.5, the sum over k in K of x k equals the sum from i equals zero to n of the sum from j equals i to n of x sub i j.

Similarly, we have the sum over k in K of x k equals the sum from j equals zero to n of the sum from i equals zero to j of x sub i j.

Therefore, the sum from i equals zero to n of the sum from j equals i to n of x sub i j equals the sum from j equals zero to n of the sum from i equals zero to j of x sub i j. This completes the proof.
