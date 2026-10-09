---
section: example-1-3-5
title: Example 1.3.5
kind: example
document: 1.3 Linear Combinations and Spans
url: /2026/06/21/3.-Linear-Combinations-and-Spans.html
source: 549b9bffc32a15249ee43042bda4c2e281bccaa4360afb9fbbc1f47a1c836e7a
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-09
body: ba1b34fd93a4e616bffa22e66671b8d230ca513f3fac30931e1f3ac8c00085e4
words: 344
---

Example 1.3.5. The matrices the matrix with first row one, zero, and second row zero, zero; the matrix with first row zero, one, and second row zero, zero; the matrix with first row zero, zero, and second row one, zero; and the matrix with first row zero, zero, and second row zero, one, generate R two by two since for any two by two matrix the following holds: the matrix with first row a one one, a one two, and second row a two one, a two two, equals a one one times the matrix with first row one, zero, and second row zero, zero, plus a one two times the matrix with first row zero, one, and second row zero, zero, plus a two one times the matrix with first row zero, zero, and second row one, zero, plus a two two times the matrix with first row zero, zero, and second row zero, one.

On the other hand, consider the matrices the matrix A equals the matrix with first row one, zero, and second row zero, one; the matrix B equals the matrix with first row one, one, and second row zero, one; and the matrix C equals the matrix with first row one, zero, and second row one, one.

Their linear combinations have the form alpha A plus beta B plus gamma C equals the matrix with first row alpha plus beta plus gamma, beta, and second row gamma, alpha plus beta plus gamma.

The two diagonal entries are always equal, so these matrices do not generate R two by two. It follows that span of the set A, B, C equals the set of matrices with first row t, u, and second row v, t, where t, u, and v belong to R.

Thus the same subspace can be described by a condition on its elements or by a set of vectors that generates it. The condition identifies which vectors belong to the subspace; the generating set identifies the vectors from which the elements of the subspace can be built.
