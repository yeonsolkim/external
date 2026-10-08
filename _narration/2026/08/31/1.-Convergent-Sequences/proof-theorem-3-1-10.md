---
section: proof-theorem-3-1-10
title: Proof
kind: proof
document: 3.1 Convergent Sequences
url: /2026/08/31/1.-Convergent-Sequences.html
source: 86d0814105f67b46e2c9674a9500437bb812c39fd446db9781a737b352602959
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-07
body: 08921f7b490bb08db7579db920f14894c7f08aea1f6967e976c006740546196a
words: 692
---

Proof. One. Let epsilon greater than zero be given. The Archimedean property of R guarantees the existence of n naught in the positive integers such that n naught is greater than the quantity one over epsilon, to the power one over x. Then, n greater than or equal to n naught implies one over n to the x is less than epsilon. Since epsilon greater than zero was arbitrary, one over n to the x tends to zero.

Two. If x equals one then it is trivial. Suppose x is greater than one and let the n-th root of x equal one plus delta n, so that delta n is greater than zero. Then we have the quantity one plus delta n, raised to the n, equals x. Since one plus n delta n is less than or equal to the quantity one plus delta n, raised to the n by the binomial theorem, it follows that one plus n delta n is less than or equal to x. Therefore delta n is less than or equal to x minus one over n, and thus delta n tends to zero by Lemma 3.1.9. This proves the limit as n tends to infinity of the n-th root of x equals one. Since the n-th root of x times the n-th root of one over x equals one, we have the limit as n tends to infinity of the n-th root of the quantity one over x equals the limit as n tends to infinity of one over the n-th root of x, which equals one over the limit as n tends to infinity of the n-th root of x, which equals one. This shows that part two holds as well when x is less than one.

Three. Let the n-th root of n equal one plus delta n, so that delta n is greater than zero for n greater than or equal to two. Then we have the quantity one plus delta n, raised to the n, equals n. If n is greater than or equal to two, then n times the quantity n minus one, all over two, times delta n squared, is less than the quantity one plus delta n, raised to the n by the binomial theorem. It follows that n times the quantity n minus one, all over two, times delta n squared, is less than n. Thus we have zero is less than delta n, which is less than the square root of the quantity two over n minus one. Hence delta n tends to zero, by Lemma 3.1.9. Consequently, the n-th root of n tends to one.

Four. Let k be an integer such that k is greater than y and k is greater than zero. If n is greater than two k, then, by the binomial theorem, the quantity one plus x, raised to the n, is greater than n choose k times x to the k, which equals n times the quantity n minus one, and so on, down to the quantity n minus k plus one, all over k factorial, times x to the k, which is greater than n to the k, over the product of two to the k and k factorial, times x to the k. It follows that zero is less than n to the y over the quantity one plus x, raised to the n, which is less than the product of two to the k and k factorial, over the product of x to the k and n to the power k minus y. Since we have the product of two to the k and k factorial, over the product of x to the k and n to the power k minus y, tends to zero by part one, Lemma 3.1.9 now gives n to the y over the quantity one plus x, raised to the n, tends to zero.

Five. If x equals zero it is trivial. If zero is less than the absolute value of x, which is less than one, then taking y equals zero in part four shows part five. This completes the proof.
