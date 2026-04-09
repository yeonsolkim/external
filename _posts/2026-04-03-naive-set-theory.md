---
layout: post
title: "Naive Set Theory"
date: 2026-04-03 00:00:00 +0900
categories: ["Mathematics", "1. Set Theory"]
---

수학적으로 set이 어떤 개념인지 파악해보자. 

**1. Axiom of Extension.**

$$\forall x\,(x\in A\leftrightarrow x\in B)\leftrightarrow A=B$$

<br>

**2. Belonging.** a binary "relation" $\in$.
hierarchical한 느낌이다: e.g., $(\text{(n)-dimensional)}\in(\text{(n+1)-dimensional})$.
<br>

**3. Inclusion.**

$$A\subset B \leftrightarrow \forall x\,(x\in A \rightarrow x\in B).$$

여기서 두 set은 same-dimensional로 보여진다. 
$A\subset B\wedge B\subset C \rightarrow A\subset C\ (transitive)$
<br>

**4. Axiom of Specification.**

$$\forall A\,\forall p\,\exists B \,\forall x\,(x\in B\leftrightarrow x\in A\wedge \varphi (x,p)),$$

denoted by $B=\{x\in A:\varphi(x,p)\}.$
given set이 있어야 carve out하여 new one을 만들 수 있다.
<br>

**5.1. Axiom of Pairing.**

$$\forall a\,\forall b\,\exists B\,\forall x\,(x\in B\leftrightarrow \varphi(x,a,b)) \text{ where } \varphi(x,a,b):x=a\lor x=b,$$

denoted by $B=\{a,b\}$; the set is called the *unordered pair*.
We may refer to the axiom as a pseudo-special cases of axiom of specification in the sense that if there were a universe, then the axiom would follow as a special case. 
<br>

**5.2. Notation.** 앞으로 이런 generating axiom들이 추가될 예정이므로 이쯤에서 새 notation을 도입하자: If $\varphi(x,p)$ is a condition such that $x$'s that $\varphi(x,p)$ specifies constitute a set, then we denote that set by $\{x:\varphi(x,p)\}.$
<br>

**6.1. Axiom of Unions.** $\forall A\,\exists B\,\forall x\,(x\in B\rightarrow \exists y\,(y\in A\wedge x\in y)).$ There exists a comprehensive set. And, applying axiom of specification, we get 

$$\forall A\,\exists B\,\forall x\,(x\in B\leftrightarrow \exists y\,(y\in A\wedge x\in y)),$$

denoted by $B=\bigcup A$; *the union of* $A$.
<br>

**6.2. Notation.** We introduce special notation for a pair: $X\cup Y=\bigcup\{X,Y\}$. It follows that $X\cup Y=\{x:x\in X\lor x\in Y\}$ by general definition. 
<br>

**6.3. Definition.** Now we can generalize pairs: $\{a,b,c\}=\{a\}\cup \{b\}\cup \{c\}, \text{etc.}$ 

> Proving Strategy<br>
> Goal: To explicate that a sentence is trivial. <br>
> Strategy 1: If a sentence has disjunction, then split into the cases.

<br>

**7.1. Definition of Complement.** *Relative complement* of $B$ in $A$ is the set $A-B$ defined by 

$$A-B=\{x\in A:x\notin B\}.$$

Dealing with sets which are subsets of $E$, we can define *absolute complement*. Often used symbol for absolute complement of $A$ is $A'$. 
<br>

**7.2. Theorem(*De Morgan Laws*).** Basically, they are about unions and intersections: 

$$(A\cup B)'=A'\cap B',\ (A\cap B)'=A'\cup B'.$$