---
section: proof-theorem-2-3-3
title: Proof
kind: proof
document: 2.3 Perfect Sets
url: /2026/08/05/3.-Perfect-Sets.html
source: 3023ec2d09a39544248539f188ac66a4e37c6555b079771b0f3daa68b9cf5b79
skeleton: 4
prompt: lecture-v4
model: gpt-5.5
generated: 2026-10-07
body: 29c6fb46559f1497e858e4d921af9b099253d4514058583f1a287cefd58d7565
words: 364
---

Proof. Let P be a nonempty perfect subset of R k. Since P has limit points, P is infinite by Corollary 2.1.9. Suppose, for contradiction, P is countable, and denote the points of P as p one, p two, p three, and so on. We now construct a sequence V n of open balls. Define V one to be any open ball around p one. Suppose V n has been constructed so that V n has a point of P. Then, we may choose a point y in V n intersect P other than p n. Indeed, even if p n belongs to V n intersect P, since V n is open, there is a ball of radius r about p n contained in V n. Since p n is a limit point of P, the punctured ball of radius r about p n has a point of P, so such a y exists. Let the ball of radius s about y be contained in V n, and let zero be less than t, which is less than the minimum of s and the norm of p n minus y. Then we define V sub n plus one equal to the ball of radius t about y. Since y belongs to V sub n plus one intersect P so that V sub n plus one satisfies our induction hypothesis, the construction can proceed. Put K n equal to the closure of V n intersect P. Then, each K n is nonempty and compact. Moreover, since the closure of V sub n plus one is contained in V n, which is contained in the closure of V n, we have K sub n plus one is contained in K n. Thus Corollary 2.2.12 gives a point x in the intersection from n equals one to infinity of K n. This point has survived every stage of the construction. But since x belongs to P, the assumed enumeration gives x equals p m for some m. This contradicts the fact that the m plus one-th ball was chosen precisely so that p m does not belong to K sub m plus one. This completes the proof.
