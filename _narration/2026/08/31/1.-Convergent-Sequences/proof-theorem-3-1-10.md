---
section: proof-theorem-3-1-10
title: Proof
kind: proof
document: 3.1 Convergent Sequences
url: /2026/08/31/1.-Convergent-Sequences.html
source: cdcae40402c1862507122e19e2f58c004fe295124d0d8cf160ebe7504e38e666
skeleton: 4
prompt: lecture-v3
model: gpt-5.5
generated: 2026-09-28
body: 8bfd54f715c8881488e81828278f03fa707a3b3eb55a5efe2eadb61a4ecdac90
words: 635
---

Proof. Part one. Let epsilon greater than zero be given. The Archimedean property of R guarantees the existence of n naught in the positive integers such that n naught is greater than the quantity one over epsilon, to the one over x. Then, n greater than or equal to n naught implies one over n to the x is less than epsilon. Since epsilon greater than zero was arbitrary, one over n to the x tends to zero.

Part two. If x equals one then it is trivial. Suppose x is greater than one and let the n-th root of x equal one plus delta n. Then we have the quantity one plus delta n, to the n, equals x. Since one plus n delta n is less than the quantity one plus delta n, to the n, by the binomial theorem, it follows that one plus n delta n is less than x. Therefore delta n is less than x minus one over n, and thus delta n tends to zero by Lemma 3.1.9. This proves the limit as n goes to infinity of the n-th root of x equals one. Since the n-th root of x times the n-th root of one over x equals one, we have the limit as n goes to infinity of the n-th root of one over x equals the limit as n goes to infinity of one over the n-th root of x, which equals one over the limit as n goes to infinity of the n-th root of x, which equals one. This shows that part two holds as well when x is less than one.

Part three. Let the n-th root of n equal one plus delta n, where delta n is greater than zero. Then we have the quantity one plus delta n, to the n, equals n. If n is greater than or equal to two, then n times the quantity n minus one, over two, times delta n squared is less than the quantity one plus delta, to the n, by the binomial theorem. It follows that n times the quantity n minus one, over two, times delta n squared is less than n. Thus we have zero is less than delta n, which is less than the square root of two over n minus one. Hence delta n tends to zero, by Lemma 3.1.9. Consequently, the n-th root of n tends to one.

Part four. Let k be an integer such that k is greater than y and k is greater than zero. If n is greater than two k, then, by the binomial theorem, the quantity one plus x, to the n, is greater than n choose k times x to the k, which equals n times n minus one times and so on up to n minus k plus one, over k factorial, times x to the k, which is greater than n to the k over two to the k times k factorial, times x to the k. It follows that zero is less than n to the y over the quantity one plus x, to the n, which is less than two to the k times k factorial, over x to the k times n to the k minus y. Since we have two to the k times k factorial, over x to the k times n to the k minus y, tends to zero by part one, Lemma 3.1.9 now gives n to the y over the quantity one plus x, to the n, tends to zero.

Part five. If x equals zero it is trivial. If zero is less than the absolute value of x, which is less than one, then taking y equals zero in part four shows part five. This completes the proof.
