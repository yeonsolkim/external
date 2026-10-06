---
section: example-1-3-5
title: Example 1.3.5
kind: example
document: 1.3 Linear Combinations and Spans
url: /2026/06/21/3.-Linear-Combinations-and-Spans.html
source: abf9ef4b0660e95f6d25d8b918186094fcd0b01694fc1222e9c6ad0dde4e342f
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-06
body: d48e32a7dc5306b05b6b38bd002decdfb5e284e7bd7f552b9cd09bcecf3e1678
words: 388
---

Example 1.3.5. The matrices, the two by two matrix with first row 1, 0 and second row 0, 0; the two by two matrix with first row 0, 1 and second row 0, 0; the two by two matrix with first row 0, 0 and second row 1, 0; and the two by two matrix with first row 0, 0 and second row 0, 1, generate R two by two, since for any two by two matrix the following holds: the two by two matrix with first row a one one, a one two and second row a two one, a two two, equals a one one times the two by two matrix with first row 1, 0 and second row 0, 0, plus a one two times the two by two matrix with first row 0, 1 and second row 0, 0, plus a two one times the two by two matrix with first row 0, 0 and second row 1, 0, plus a two two times the two by two matrix with first row 0, 0 and second row 0, 1.

On the other hand, consider the matrices A equals the two by two matrix with first row 1, 0 and second row 0, 1; B equals the two by two matrix with first row 1, 1 and second row 0, 1; and C equals the two by two matrix with first row 1, 0 and second row 1, 1. Their linear combinations have the form alpha times A plus beta times B plus gamma times C equals the two by two matrix with first row alpha plus beta plus gamma, beta and second row gamma, alpha plus beta plus gamma.

The two diagonal entries are always equal, so these matrices do not generate R two by two. It follows that the span of the set containing A, B, and C equals the set of all two by two matrices with first row t, u and second row v, t, such that t, u, and v are in R. Thus the same subspace can be described by a condition on its elements or by a set of vectors that generates it. The condition identifies which vectors belong to the subspace; the generating set identifies the vectors from which the elements of the subspace can be built.
