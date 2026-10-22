---
section: example-1-3-5
title: Example 1.3.5
kind: example
document: 1.3 Linear Combinations and Spans
url: /2026/06/21/3.-Linear-Combinations-and-Spans.html
source: bed7d7d333d587eaa330483359944ec4b19d65d07953584054c4e35fb93b8097
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-10
body: 8d14d4dd618938e1a63771b89148e0d5e8865b08bef44afafc7bb32b3f70b3d2
words: 354
---

Example 1.3.5. The matrices the matrix with first row one, zero, and second row zero, zero; the matrix with first row zero, one, and second row zero, zero; the matrix with first row zero, zero, and second row one, zero; and the matrix with first row zero, zero, and second row zero, one, generate Mat two by two of R, since for any two by two matrix the following holds: the matrix with first row a sub one one, a sub one two, and second row a sub two one, a sub two two, equals a sub one one times the matrix with first row one, zero, and second row zero, zero, plus a sub one two times the matrix with first row zero, one, and second row zero, zero, plus a sub two one times the matrix with first row zero, zero, and second row one, zero, plus a sub two two times the matrix with first row zero, zero, and second row zero, one.

On the other hand, consider the matrices A equals the matrix with first row one, zero, and second row zero, one; B equals the matrix with first row one, one, and second row zero, one; and the matrix C equals the matrix with first row one, zero, and second row one, one.

Their linear combinations have the form alpha A plus beta B plus gamma C equals the matrix with first row alpha plus beta plus gamma, beta, and second row gamma, alpha plus beta plus gamma.

The two diagonal entries are always equal, so these matrices do not generate Mat two by two of R. It follows that span of the set A, B, C, equals the set of all matrices with first row t, u, and second row v, t, such that t, u, and v are in R.

Thus the same subspace can be described by a condition on its elements or by a set of vectors that generates it. The condition identifies which vectors belong to the subspace; the generating set identifies the vectors from which the elements of the subspace can be built.
