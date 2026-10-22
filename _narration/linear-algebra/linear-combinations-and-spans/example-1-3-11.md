---
section: example-1-3-11
title: Example 1.3.11
kind: example
document: 1.3 Linear Combinations and Spans
url: /2026/06/21/3.-Linear-Combinations-and-Spans.html
source: 38bc0bd49b999f360ed62a064aa2972181d5d00607b86fca183d950547755fda
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-19
body: b084d7d17b9bbd1d6513c16a5aadb32d124a0c96e16f16d215e5432af8ca4fad
words: 352
---

Example 1.3.11. The matrices the matrix with first row one, zero, and second row zero, zero; the matrix with first row zero, one, and second row zero, zero; the matrix with first row zero, zero, and second row one, zero; and the matrix with first row zero, zero, and second row zero, one, generate Mat two by two of R since for any two by two matrix the following holds: the matrix with first row a sub one one, a sub one two, and second row a sub two one, a sub two two, equals a sub one one times the matrix with first row one, zero, and second row zero, zero, plus a sub one two times the matrix with first row zero, one, and second row zero, zero, plus a sub two one times the matrix with first row zero, zero, and second row one, zero, plus a sub two two times the matrix with first row zero, zero, and second row zero, one.

On the other hand, consider the matrices A equals the matrix with first row one, zero, and second row zero, one; B equals the matrix with first row one, one, and second row zero, one; and C equals the matrix with first row one, zero, and second row one, one.

Their linear combinations have the form alpha A plus beta B plus gamma C equals the matrix with first row alpha plus beta plus gamma, beta, and second row gamma, alpha plus beta plus gamma.

The two diagonal entries are always equal, so these matrices do not generate Mat two by two of R. It follows that span of the set A, B, C equals the set of all matrices with first row t, u, and second row v, t, such that t, u, and v are in R.

Thus the same subspace can be described by a condition on its elements or by a set of vectors that generates it. The condition identifies which vectors belong to the subspace; the generating set identifies the vectors from which the elements of the subspace can be built.
