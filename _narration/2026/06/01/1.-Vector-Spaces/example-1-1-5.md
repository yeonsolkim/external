---
section: example-1-1-5
title: Example 1.1.5
kind: example
document: 1.1 Vector Spaces
url: /2026/06/01/1.-Vector-Spaces.html
source: 18eca061f5f42cef5cd33fe7cfc623092b06122c2ddd05aaeb30004ee947cedc
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-07
body: f70463d5831b5ee539c3d3850bb37eee821da6d6ad72308f9f304b2877a01bca
words: 463
---

Example 1.1.5. A polynomial from a field F is an expression of the form a n times x to the n plus a sub n minus one times x to the power n minus one, and so on, down to a one times x plus a zero, where n is in the nonnegative integers and each a k, called the coefficient of x to the k, is in F. If a n, a sub n minus one, and so on, down to a zero, are all equal to zero, then the polynomial is called the zero polynomial and, its degree is defined to be negative infinity; otherwise, the degree of a polynomial is defined to be the largest exponent of x that appears in the expression with a nonzero coefficient.

Two polynomials, p of x equals a n times x to the n plus a sub n minus one times x to the power n minus one, and so on, down to a one times x plus a zero, and q of x equals b m times x to the m plus b sub m minus one times x to the power m minus one, and so on, down to b one times x plus b zero, are equal if and only if their corresponding coefficients agree after padding with zero coefficients to the same length.

The set of all polynomials from F is denoted by F adjoin x. If m is less than or equal to n, then q of x can be written as q of x equals b n times x to the n plus b sub n minus one times x to the power n minus one, and so on, down to b one times x plus b zero, where b sub m plus one, b sub m plus two, and so on, up to b n, are all equal to zero.

And we give F adjoin x the following operations of addition and scalar multiplication: p of x plus q of x equals the quantity a n plus b n, times x to the n plus the quantity a sub n minus one plus b sub n minus one, times x to the power n minus one, and so on, down to the quantity a one plus b one, times x plus the quantity a zero plus b zero, and for c in F, c p of x equals the quantity c times a n, times x to the n plus the quantity c times a sub n minus one, times x to the power n minus one, and so on, down to the quantity c times a one, times x plus the quantity c times a zero.

Then F adjoin x is a vector space over F.
