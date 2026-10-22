---
section: example-1-4-11
title: Example 1.4.11
kind: example
document: 1.4 Linear Combinations and Spans
url: /linear-algebra/linear-combinations-and-spans/
source: b61b60c8905a6abd13c808401ef1112aa634e339604cff9fe172cd630727c6c4
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-22
body: 9f8151486e5f01f928eb5b15373e783b8a0b1d8957c6525262182c4f9743a5a3
words: 386
---

Example 1.4.11. The matrices the two by two matrix with first row one, zero, and second row zero, zero; the two by two matrix with first row zero, one, and second row zero, zero; the two by two matrix with first row zero, zero, and second row one, zero; and the two by two matrix with first row zero, zero, and second row zero, one, generate Mat two by two of R since for any two by two matrix the following holds: the two by two matrix with first row a one one, a one two, and second row a two one, a two two, equals a one one times the two by two matrix with first row one, zero, and second row zero, zero, plus a one two times the two by two matrix with first row zero, one, and second row zero, zero, plus a two one times the two by two matrix with first row zero, zero, and second row one, zero, plus a two two times the two by two matrix with first row zero, zero, and second row zero, one.

On the other hand, consider the matrices A equals the two by two matrix with first row one, zero, and second row zero, one, B equals the two by two matrix with first row one, one, and second row zero, one, and C equals the two by two matrix with first row one, zero, and second row one, one.

Their linear combinations have the form alpha A plus beta B plus gamma C equals the two by two matrix with first row alpha plus beta plus gamma, beta, and second row gamma, alpha plus beta plus gamma.

The two diagonal entries are always equal, so these matrices do not generate Mat two by two of R. It follows that span of the set A, B, C equals the set of all two by two matrices with first row t, u, and second row v, t, such that t, u, and v are in R.

Thus the same subspace can be described by a condition on its elements or by a set of vectors that generates it. The condition identifies which vectors belong to the subspace; the generating set identifies the vectors from which the elements of the subspace can be built.
