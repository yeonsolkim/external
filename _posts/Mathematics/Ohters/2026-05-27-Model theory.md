---
layout: post
title: Model theory
date: 2026-05-27 10:37:14 +0900
category_path:
  - Mathematics
  - Ohters
---

**1. Definition.** A $language\,\mathcal{L}$ is given by the following data: 
1. a set of function symbols $\mathcal{F}$ and positive integer $n_f$ for each $f\in {\mathcal{F}}$;
2. a set of relation symbols $\mathcal{R}$ and positive integer $n_R$ for each $R\in {\mathcal{R}}$;
3. a set of constant symbols $\mathcal{C}$.<br>
<br>

**2. Definition.** An $\mathcal{L}$-$structure\,\mathcal{M}$ is given by the following data:
1. a nonempty set $M$ called the $underlying\,set$ of $\mathcal{M}$;
2. a function $f^{\mathcal{M}}:M^{n_f}\to M$ for each $f\in {\mathcal{F}}$;
3. a set $R^{\mathcal{M}}\subseteq M^{n_R}$ for each $R\in {\mathcal{R}}$;
4. an element $c^{\mathcal{M}}\in M$ for each $c\in \mathcal{C}$.

We refer to $f^{\mathcal{M}}, R^{\mathcal{M}}$, and $c^{\mathcal{M}}$ as the $interpretations$ of the symbols $f,R$, and $c$.<br>
For example, $(\mathbb R,\cdot, 1)$ is an $\mathcal L_g$-structure, where $\mathcal L_g$ is the language of groups.<br>
<br>

**3. Definition.** Suppose that $\mathcal{M}$ and $\mathcal{N}$ are $\mathcal{L}$-structures with underlying sets $M$ and $N$, respectively. An $\mathcal{L}$-$embedding\ \eta: \mathcal{M}\to\mathcal{N}$ is a one-to-one map $\eta:M\to N$ that preserves the interpretation of all of the symbols of $\mathcal{L}$. And, a bijective $\mathcal{L}$-embedding is called an $\mathcal{L}$-$isomorphism$. <br>
For example, if $\eta : \mathbb Z \to \mathbb R$ is the function $\eta(x)=e^x$, then $\eta$ is an $\mathcal L_g$-embedding of $(\mathbb Z,+,0)$ into $(\mathbb R, \cdot, 1)$.<br>
<br>

**4. Definition.** The set of $\mathcal L$-$terms$ is the smallest set $\mathcal T$ such that
1. $c\in \mathcal T$ for each constant symbol $c\in \mathcal C$,
2. each variable symbol $v_i\in \mathcal T$ for $i=1,2,\dots,$ and
3. if $t_1,\dots,t_{n_f}\in \mathcal T$ and $f\in \mathcal F$, then $f(t_1,\dots,t_{n_f})\in \mathcal T$.

For example, $\cdot(v_1, -(v_3,1))$ and $+1(1, +(1, 1))$ are $\mathcal L_r$-terms.<br>
<br>

**5. Definition.** We say that $\phi$ is an $atomic\,\mathcal L$-$formula$ if $\phi$ is either 
1. $t_1=t_2$, where $t_1$ and $t_2$ are terms, or
2. $R(t_1,\dots, t_{n_R})$, where $R\in \mathcal R$ and $t_1,\dots,t_{n_R}$ are terms.

We call a formula a $sentence$ if it has no free variables.<br>
The set of $\mathcal L$-$formulas$ is the smallest set $\mathcal W$ containing the atomic formulas such that
1. if $\phi$ is in $\mathcal W$, then $\neg \phi$ is in $\mathcal W$,
2. if $\phi$ and $\psi$ are in $\mathcal W$, then $(\phi \wedge \psi)$ and $(\phi \lor \psi)$ are in $\mathcal W$, and 
3. if $\phi$ is in $\mathcal W$, then $\exists v_i\ \phi$ and $\forall v_i\ \phi$ in $\mathcal W$.<br>
<br>

**6. Definition.** Let $\phi$ be a formula with free variables from $\bar v=(v_{i_1},\dots,v_{i_m})$, and let $\bar a=(a_{i_1},\dots,a_{i_m})\in M^m$. We can inductively define $\mathcal M \vDash \phi (\bar a)$. If $\mathcal M \vDash \phi (\bar a)$ we say that $\phi (\bar a)$ is $true$ in $\mathcal M$.<br>
<br>

**7. Definition.** We say that two $\mathcal L$-structures $\mathcal M$ and $\mathcal N$ are $elementarily\ equivalent$ and write $\mathcal M \equiv \mathcal N$ if 

$$\mathcal M \vDash \phi \text{ if and only if } \mathcal N \vDash \phi$$

for all $\mathcal L$-sentences $\phi$.<br>
We let $\text{Th}(\mathcal M)$, the $full\ theory\ of\ \mathcal M$, be the set of $\mathcal L$-sentences $\phi$ such that $\mathcal M \vDash \phi$.<br>
<br>

**8. Definition.** An $\mathcal L$-$theory\ T$ is simply a set of $\mathcal L$-sentences. We say that $\mathcal M$ is a $model$ of $T$ and write $\mathcal M \vDash T$ if $\mathcal M \vDash \phi$ for all sentences $\phi \in T$. And, we say that a theory is $satisfiable$ if it has a model.<br>
<br>

**9. Definition.** We say that a class of $\mathcal L$ structures $\mathcal K$ is an $elementary\ class$ if there is an $\mathcal L$-theory such that $\mathcal K=\lbrace \mathcal M: \mathcal M\vDash T\rbrace$. The elementary class of models of $\text{Th}(\mathcal M)$ is exactly the class of $\mathcal L$-structures elementarily equivalent to $\mathcal M$.