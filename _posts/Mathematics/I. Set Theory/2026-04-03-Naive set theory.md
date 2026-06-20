---
layout: post
title: Naive set theory
date: 2026-04-03 00:00:00 +0900
category_path:
  - Mathematics
  - I. Set Theory
last_modified_at: 2026-06-20 12:30:58 +0900
created_at: 1984-01-24 17:00:00 +0900
---

**1. Axiom of extension.**

$$\forall x\,(x\in A\leftrightarrow x\in B)\leftrightarrow A=B$$

<br> 

**2. Belonging.** a binary "relation" $\in$.
hierarchical한 느낌이다: [$n$-dimension] $\in$ [($n+1$)-dimension].
<br><br>

**3. Inclusion.**

$$A\subset B \leftrightarrow \forall x\,(x\in A \rightarrow x\in B).$$

여기서 두 set은 same-dimensional로 보여진다. 
$A\subset B\wedge B\subset C \rightarrow A\subset C\ (transitive)$
<br><br>

**4. Axiom of specification.**

$$\forall A\,\forall p\,\exists B \,\forall x\,(x\in B\leftrightarrow x\in A\wedge \varphi (x,p)),$$

denoted by $B=\lbrace x\in A:\varphi(x,p)\rbrace.$
given set이 있어야 carve out하여 new one을 만들 수 있다.<br>
<br>

**5.1. Axiom of pairing.**

$$\forall a\,\forall b\,\exists B\,\forall x\,(x\in B\leftrightarrow \varphi(x,a,b)) \text{ where } \varphi(x,a,b):x=a\lor x=b,$$

denoted by $B=\lbrace a,b\rbrace$; the set is called the *unordered pair*.
We may refer to the axiom as a pseudo-special case of axiom of specification in the sense that if there were a universe, then the axiom would follow as a special case. <br>
<br>

**5.2. Notation.** 앞으로 이런 generating axiom들이 추가될 예정이므로 이쯤에서 새 notation을 도입하자: If $\varphi(x,p)$ is a condition such that $x$s that $\varphi(x,p)$ specifies constitute a set, then we denote that set by $\lbrace x:\varphi(x,p)\rbrace.$
<br><br>

**6.1. Axiom of unions.** $\forall A\,\exists B\,\forall x\,( \exists y\,(y\in A\wedge x\in y)\rightarrow x\in B).$ There exists a comprehensive set. And, applying axiom of specification, we get 

$$\forall A\,\exists B\,\forall x\,( \exists y\,(y\in A\wedge x\in y)\leftrightarrow x\in B),$$

denoted by $B=\bigcup A$; *the union of* $A$.
<br><br>

**6.2. Notation.** We introduce special notation for a pair: $X\cup Y=\bigcup\lbrace X,Y\rbrace$. It follows that $X\cup Y=\lbrace x:x\in X\lor x\in Y\rbrace$ by general definition. 
<br><br>

**6.3. Definition.** Now we can generalize pairs: $\lbrace a,b,c\rbrace =\lbrace a\rbrace \cup \lbrace b\rbrace \cup \lbrace c\rbrace , \text{etc.}$ 

> **Proving strategy**<br>
> Goal: To explicate that a sentence is trivial. <br>
> Strategy 1: If a sentence has disjunction, then split into the cases.


<br>

**7.1. Definition of complement.** *Relative complement* of $B$ in $A$ is the set $A-B$ defined by 

$$A-B=\lbrace x\in A:x\notin B\rbrace.$$

Dealing with sets which are subsets of $E$, we can define *absolute complement*. Often used symbol for absolute complement of $A$ is $A'$. 
<br><br>

**7.2. Theorem (*De Morgan laws*).** Basically, they are about unions and intersections: 

$$(A\cup B)'=A'\cap B',\ (A\cap B)'=A'\cup B'.$$

<br>

**8. Axiom of powers.** $\forall E\, \exists \mathcal{P}\, \forall x\, (x\subset E\rightarrow x\in \mathcal{P})$. And, applying axiom of specification, we get 

$$\forall E\, \exists \mathcal{P}\, \forall x\, (x\subset E\leftrightarrow x\in \mathcal{P}).$$

The set $\mathcal{P}$ is called the *power set* of $E$; the dependence of $\mathcal{P}$ on $E$ is denoted by $\mathcal{P}(E)$. 
