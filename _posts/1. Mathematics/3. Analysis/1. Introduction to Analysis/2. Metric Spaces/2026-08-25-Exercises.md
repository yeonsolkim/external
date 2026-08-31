---
layout: post
title: "Exercises"
date: 2026-08-25 00:00:00 +0900
category_path:
  - 1. Mathematics
  - 3. Analysis
  - 1. Introduction to Analysis
  - 2. Metric Spaces
created_at: 2026-08-31 15:32:11 +0900
last_modified_at: 2026-08-31 15:32:11 +0900
---
$A$ is *perfect* if it contains all of its limit points, and every point of $A$ itself is a limit point, that is, $A=A'$. In other words, a perfect set is closed, and none of its own points is locally isolated from the rest of the set. Density answers how widely $A$ spreads throughout the ambient space $M$. If any point of $M$ cannot locally avoid $A$, then $A$ is said to be *dense* in $M$. Equivalently, $A$ is dense in $M$ if $M = \overline A$.

**Exercise 1.** Let $(M,d)$ be a metric space, and let $A\subseteq M$. 
1. Prove that $A'$ is closed.
2. Prove that $A$ and $\overline A$ have the same limit points.
3. Prove or disprove that $A$ and $A'$ have the same limit points.

**Exercise 2.** Let $(M,d)$ be a metric space and let $A\subseteq M$. Prove that

1. $A$ is open if and only if $A\cap\partial A=\varnothing$,
2. $A$ is closed if and only if $\partial A\subseteq A$,
3. $A$ is dense in $M$ if and only if $\operatorname{ext} A = \varnothing$,
4. $A$ is bounded if and only if $\overline A$ is bounded.

*Solution.* (1) Suppose $A$ is open. Since $\operatorname{int} A$ and $\partial A$ is disjoint, $A\subseteq \operatorname{int} A$ implies $A\cap \partial A = \varnothing.$ Conversely, suppose $A\cap \partial A = \varnothing.$ Then $x\in A$ implies $x\notin \partial A,$ so that $x\in \operatorname{int} A$ or $x\in \operatorname{ext} A.$ Since $A$ and $\operatorname{ext} A$ are disjoint, $x\in \operatorname{int} A.$ Hence $A\subseteq \operatorname{int} A,$ so $A$ is open.
(2) If $\partial A\subseteq A,$ then $\operatorname{int} A \cup \partial A \subseteq A.$ Hence $A'\subseteq \overline A \subseteq A.$ Thus $A$ is closed. Conversely, if $A'\subseteq A$ then $\overline A\subseteq A.$ Hence $\partial A \subseteq \overline A \subseteq A.$
(3) Since $M\subseteq M\setminus \operatorname{ext} A$ is equivalent to $\operatorname{ext} A=\varnothing,$ if $A$ is dense in $M$ then $\operatorname{ext} A=\varnothing,$ and vice versa.
(4) Suppose that $A$ is bounded, and choose $r>0$ and $a\in M$ such that $A\subseteq B_r(a).$ If $x\in A'$ then $B_1^{\ast}(x)$ contains some point $y\in A.$ Then $d(x,y)<1,$ while $d(y,a)<r,$ so the triangle inequality gives $d(x,a)<r+1.$ This proves that $A'\subseteq B_{r+1}(a),$ which is enough for boundedness. Conversely, if $\overline A$ is bounded, then $\overline A = A \cup A' \subseteq B_r(a)$ for some $a\in M$ and $r>0.$ Thus $A\subseteq B_r(a),$ so $A$ is bounded.<span class="qed">$\square$</span>

**Exercise 3.** Let $(M,d)$ be a metric space and let $A\subseteq M$. Then the following hold.

1. If $A$ is both closed and dense in $M$, then $A=M.$
2. If $A$ is bounded, then $\operatorname{int} A, \partial A,$ and $A'$ are bounded.
3. If $A$ is both bounded and dense in $M$, then $M$ is bounded. Consequently, if $M$ is unbounded, every dense subset of $M$ is unbounded.

*Solution.* (1) Since $A$ is closed, $\overline A = A.$ Thus, $A$'s being dense in $M$ implies $M\subseteq A.$ Therefore $A=M.$
(2) Since $A$ is bounded, $\overline A$ is also bounded by (4) of Exercise 2. Hence $\overline A\subseteq B_r(a)$ for some $r>0$ and $a\in M.$ Since $\operatorname{int} A, \partial A,$ and $A'$ are subsets of $\overline A,$ the sets are also subsets of $B_r(a).$ Therefore $\operatorname{int} A, \partial A,$ and $A'$ are bounded.
(3) If $A$ is bounded, then $\overline A$ is also bounded, so that $\overline A\subseteq B_r(a)$ for some $r>0$ and $a\in M.$ Since $A$ is dense in $M,$ it follows that $M\subseteq \overline A \subseteq B_r(a).$ Hence $M$ is bounded.<span class="qed">$\square$</span>