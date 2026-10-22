---
section: example-1-6-9
title: Example 1.6.9
kind: example
document: 1.6 Linear Dependence and Linear Independence
url: /linear-algebra/linear-dependence-and-linear-independence/
source: b9428d9ab84cd5773f6eba8379a1a1d75aa73299b16a8f33e9b6575976d5242b
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-22
body: 63fe9b138a091328ce95af0b3c57ec44def5c3514dba63be23c78dd85c099bb8
words: 255
---

Example 1.6.9. Let n be a nonnegative integer and define p k of x equals the sum from i equals k to n of x to the i, for zero less than or equal to k less than or equal to n.

Then the set S equals the set of p k of x such that zero is less than or equal to k, which is less than or equal to n, is linearly independent in F n of x. Indeed, by Proposition 1.4.7, part two, and Corollary 1.4.6, the sum from k equals zero to n of a k p k of x equals the sum from k equals zero to n of a k times the quantity the sum from i equals k to n of x to the i, which equals the sum from k equals zero to n of the sum from i equals k to n of a k times x to the i, which equals the sum from i equals zero to n of the sum from k equals zero to i of a k times x to the i, which equals the sum from i equals zero to n of the quantity the sum from k equals zero to i of a k, times x to the i, for any scalars a zero through a n in F. Therefore, if a from S to F is a representation of the zero polynomial, then the support of a equals the empty set. By Theorem 1.6.6, S is linearly independent.
