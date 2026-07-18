---
layout: post
title: "Combinatorics"
date: 2026-07-11 00:00:00 +0900
category_path:
  - Mathematics
  - VI. Others
created_at: 2026-07-11 12:19:36 +0900
last_modified_at: 2026-07-11 12:19:36 +0900
---

**Definition 1.** An *outcome* is one particular possible result of the trial. When a die is rolled, the outcomes are $1,2,3,4,5,6.$ The *sample space*, usually denoted by $\Omega$, is the set of all possible outcomes:

$$\Omega=\lbrace 1,2,3,4,5,6\rbrace. $$

&emsp; An *event* is a collection of outcomes, so mathematically an event is a subset of the sample space. For example, if one die is rolled, the event that an even number appears is

$$A=\lbrace 2,4,6\rbrace \subseteq \Omega.$$

The statement “*event* $A$ *occurs*” means that the actual outcome of the trial belongs to $A$. Thus, if the actual outcome is $4$, then $A$ occurs; if the actual outcome is $5$, then $A$ does not occur. Accordingly, the statement “*event* $A$ *can occur in* $m$ *ways*” means that $A$ contains $m$ possible outcomes:

$$|A|=m.$$

For instance, the event $A=\lbrace 2,4,6\rbrace$ can occur in three ways because there are three outcomes that make $A$ occur.<br>
<br>

**Definition 2.** Two events $A$ and $B$ are *mutually exclusive*, or *disjoint*, when they cannot occur in the same trial, which is denoted by

$$A\cap B=\varnothing.$$

If $|A|=m$, $|B|=n$, and $A\cap B=\varnothing$, then the event “$A$ *or* $B$ *occurs*” is denoted by $A\cup B$, and

$$|A\cup B|=|A|+|B|=m+n.$$

This formula is often called the *addition rule.*

<br>

**Definition 3.** The *multiplication rule* concerns a process that is completed in successive stages. We let $A$ be the set of possible results of the first stage and $B$ the set of possible results of the second stage, with

$$
|A|=m,\qquad |B|=n.  
$$

A *complete outcome* is then an ordered pair

$$
(a,b)\in A\times B,  
$$

where $a$ records the first-stage result and $b$ records the second-stage result. Since each of the $m$ possible values of $a$ can be paired with each of the $n$ possible values of $b$,

$$
|A\times B|=mn.  
$$
