---
layout: post
title: "Exercises"
date: 2026-08-31 00:00:00 +0900
category_path:
  - 1. Mathematics
  - 3. Mathematical Analysis
  - 1. Introduction to Analysis
  - 2. Metric Spaces
created_at: 2026-08-31 15:32:11 +0900
last_modified_at: 2026-10-21 18:01:13 +0900

publish: false
source_note: The presentation in this section draws in part on Rudin, *Principles of Mathematical Analysis*, 3rd ed. (1976).
description: "Exercises on metric spaces: limit points and closures, closures of unions, and a direct proof that the set of 0 and the numbers 1/n is compact."
---
**1.** Let $(M,d)$ be a metric space, and let $A\subseteq M$.
1. Prove that $A'$ is closed.
2. Prove that $A$ and $\overline A$ have the same limit points.
3. Prove or disprove that $A$ and $A'$ have the same limit points.

**2.** Let $(M,d)$ be a metric space and let $A\subseteq M$. Prove that

1. the set $A$ is open if and only if $A\cap\partial A=\varnothing$;
2. the set $A$ is closed if and only if $\partial A\subseteq A$;
3. the set $A$ is dense in $M$ if and only if $\operatorname{ext} A = \varnothing$.

*Solution.* (1) Suppose $A$ is open. Since $\operatorname{int} A$ and $\partial A$ is disjoint, $A\subseteq \operatorname{int} A$ implies $A\cap \partial A = \varnothing.$ Conversely, suppose $A\cap \partial A = \varnothing.$ Then $x\in A$ implies $x\notin \partial A,$ so that $x\in \operatorname{int} A$ or $x\in \operatorname{ext} A.$ Since $A$ and $\operatorname{ext} A$ are disjoint, $x\in \operatorname{int} A.$ Hence $A\subseteq \operatorname{int} A,$ so $A$ is open.
(2) If $\partial A\subseteq A,$ then $\operatorname{int} A \cup \partial A \subseteq A.$ Hence $A'\subseteq \overline A \subseteq A.$ Thus $A$ is closed. Conversely, if $A'\subseteq A$ then $\overline A\subseteq A.$ Hence $\partial A \subseteq \overline A \subseteq A.$
(3) Since $M\subseteq M\setminus \operatorname{ext} A$ is equivalent to $\operatorname{ext} A=\varnothing,$ if $A$ is dense in $M$ then $\operatorname{ext} A=\varnothing,$ and vice versa.<span class="qed">$\square$</span>

**3.** Let $M$ be a metric space, and let $A_1,A_2,\ldots\subseteq M$. Prove that
1. if $B_n = \bigcup_{i=1}^n A_i$, then $\overline {B_n} = \bigcup_{i=1}^n \overline {A_i}$;
2. if $B = \bigcup_{i=1}^{\infty} A_i$, then $\bigcup_{i=1}^{\infty}\overline {A_i}\subseteq \overline B$.

**4.** Let $K\subseteq \mathbb R$ consist of $0$ and the numbers $1,1/2,1/3,\ldots.$ Prove that $K$ is compact without using the Heine–Borel theorem.
