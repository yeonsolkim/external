---
layout: post
title: "Naive set theory"
date: 2026-06-23 00:00:00 +0900
category_path:
  - Mathematics
  - IV. Others
created_at: 2026-06-25 12:36:39 +0900
last_modified_at: 2026-06-25 12:36:39 +0900
---

**Belonging.** a binary "relation" $\in.$ hierarchical한 느낌이다: [$n$-dimension] $\in$ [($n+1$)-dimension].<br>
<br>

**Inclusion.**

$$A\subseteq B \iff \forall x\,(x\in A \Rightarrow x\in B).$$

여기서 두 set은 same-dimensional로 보여진다. $A\subseteq B\wedge B\subseteq C \Rightarrow A\subseteq C\ (transitive)$<br>
<br>

**Axiom of Extension.**

$$A=B \iff \forall x\,(x\in A\leftrightarrow x\in B). $$

<br> 

**Axiom of Specification.**

$$\forall A\,\forall p\,\exists B \,\forall x\,[x\in B\Leftrightarrow x\in A\wedge \varphi (x,p)],$$

denoted by $B=\lbrace x\in A:\varphi(x,p)\rbrace.$ given set이 있어야 carve out하여 new one을 만들 수 있다.<br>
<br>

**Axiom of Pairing.**

$$\forall a\,\forall b\,\exists B\,\forall x\ [x\in B\leftrightarrow \varphi(x,a,b)] \text{ where } \varphi(x,a,b):x=a\lor x=b,$$

denoted by $B=\lbrace a,b\rbrace;$ the set is called the *unordered pair*.
We may refer to the axiom as a pseudo-special case of axiom of specification in the sense that if there were a universe, then the axiom would follow as a special case. <br>
&emsp; 앞으로 이런 generating axiom들이 추가될 예정이므로 이쯤에서 새 notation을 도입하자: If $\varphi(x,p)$ is a condition such that $x$s that $\varphi(x,p)$ specifies constitute a set, then we denote that set by $\lbrace x:\varphi(x,p)\rbrace.$<br>
<br>

**Axiom of Unions.** 

$$\forall A\,\exists B\,\forall x\ [ \exists y\ (y\in A\wedge x\in y)\Rightarrow x\in B].$$

There exists a comprehensive set. And, applying axiom of specification, we get 

$$\forall A\,\exists B\,\forall x\ [ \exists y\ (y\in A\wedge x\in y)\Leftrightarrow x\in B],$$

denoted by $B=\bigcup A;$ *the union of* $A.$ We introduce special notation for a pair: 

$$X\cup Y=\bigcup\lbrace X,Y\rbrace.$$ 

It follows that $X\cup Y=\lbrace x:x\in X\lor x\in Y\rbrace$ by general definition. Then we can generalize pairs: $\lbrace a,b,c\rbrace =\lbrace a\rbrace \cup \lbrace b\rbrace \cup \lbrace c\rbrace , \text{etc.}$<br>
<br>

**Definition of Complement.** *Relative complement* of $B$ in $A$ is the set $A-B$ defined by 

$$A-B=\lbrace x\in A:x\notin B\rbrace.$$

Dealing with sets which are subsets of $E,$ we can define *absolute complement*. Often used symbol for absolute complement of $A$ is $A'.$ <br>
<br>

**De Morgan Laws.** Basically, they are about unions and intersections: 

$$(A\cup B)'=A'\cap B',\ (A\cap B)'=A'\cup B'.$$

<br>

**Axiom of powers.** 

$$\forall E\, \exists \mathcal{P}\, \forall x\ (x\subseteq E\Rightarrow x\in \mathcal{P}).$$ 

And, applying axiom of specification, we get 

$$\forall E\, \exists \mathcal{P}\, \forall x\ (x\subseteq E\Leftrightarrow x\in \mathcal{P}).$$

The set $\mathcal{P}$ is called the *power set* of $E;$ the dependence of $\mathcal{P}$ on $E$ is denoted by $\mathcal{P}(E).$ 
