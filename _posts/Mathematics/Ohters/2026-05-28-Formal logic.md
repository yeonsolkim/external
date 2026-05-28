---
layout: post
title: Formal logic
date: 2026-05-28 09:19:08 +0900
category_path:
  - Mathematics
  - Ohters
last_modified_at: 2026-05-28 16:35:56 +0900
---

**1. Formal logic.** formal system은 다음 4가지로 구성된다:
1. alphabet: a set of symbols
2. a set of formulas
3. a set of axioms
4. rules of inference.<br>
<br>

**2.1 Propositional logic.** propositional logic의 formal system은 다음 4가지로 구성된다:
1. alphabet: propositional variables, connectives
2. a set of formulas
3. a set of axioms
4. the rule of inference: Modus Ponens, $\phi$와 $(\phi\rightarrow \psi)$로부터 $\psi$를 추론할 수 있다.

$\sum$이 a set of formulas이고 $\phi$가 $\sum$의 theorem일 때 

$$\sum \vdash \phi$$

로 적는다.<br>
<br>

**2.2 Semantics of propositional logic.** 어떤 propositional variable들에 대해 truth value를 알고 있다면 그것들을 결합하여 만든 formula들의 truth value를 알 수 있다. 임의의 valuation $v$에 대하여 $v(\phi)=\mathrm T$일 때 $\phi$를 tautology라 하고, 임의의 valuation $v$에 대하여 $v(\phi)=\mathrm F$일 때 $\phi$를 contradiction이라 한다.<br>
Let $\sum$ be a set of formulas. We say that a formula $\phi$ is a logical consequence of $\sum$ and write 

$$\sum \vDash \phi$$ 

if $v(\phi)=\mathrm T$ for all valuation $v$ such that $v(\sigma)=\mathrm T$ for all $\sigma\in \sum$.<br>
<br>

**3.1 First-order logic.** 
1. language $\mathcal L$
   * unique symbols: function symbols, relation symbols, constant symbols, 
   * common symbols: variables, connectives, equality, quantifiers, parentheses, comma
1. $\mathcal L$-terms, atomic $\mathcal L$-formulas, $\mathcal L$-formulas
2. 9 axioms
3. rules of inference


> 1. Conjunction introduction
>
>    $$
>    \frac{A \qquad B}{A \land B} 
>    $$
>
> 2. Conjunction elimination
>
>    $$
>    \frac{A \land B}{A}
>    $$
>
>    $$
>    \frac{A \land B}{B} 
>    $$
>
> 3. Disjunction introduction
>
>    $$
>    \frac{A}{A \lor B} 
>    $$
>
>    $$
>    \frac{B}{A \lor B} 
>    $$
>
> 4. Disjunction elimination
>
>    $$
>    \frac{A \lor B \qquad [A] \vdots C \qquad [B] \vdots C}{C} 
>    $$
>
> 5. Implication introduction
>
>    $$
>    \frac{[A] \vdots B}{A \to B} 
>    $$
>
> 6. Implication elimination
>
>    $$
>    \frac{A \to B \qquad A}{B} 
>    $$
>
> 7. Negation introduction
>
>    $$
>    \frac{[A] \vdots \bot}{\neg A} 
>    $$
>
> 8. Negation elimination
>
>    $$
>    \frac{A \qquad \neg A}{\bot}
>    $$
>
> 9. Bottom elimination
>
>    $$
>    \frac{\bot}{A}
>    $$
>
> 10. Biconditional introduction
>
>     $$
>     \frac{A \to B \qquad B \to A}{A \leftrightarrow B} 
>     $$
>
> 11. Biconditional elimination
>
>     $$
>     \frac{A \leftrightarrow B}{A \to B} 
>     $$
>
>     $$
>     \frac{A \leftrightarrow B}{B \to A} 
>     $$
>
> 12. Universal introduction
>
>     $$
>     \frac{A(a)}{\forall x A(x)} 
>     $$
>
>     단, \($a$\)는 arbitrary variable이어야 한다.
>
> 13. Universal elimination
>
>     $$
>     \frac{\forall x A(x)}{A(t)} 
>     $$
>
> 14. Existential introduction
>
>     $$
>     \frac{A(t)}{\exists x A(x)} 
>     $$
>
> 15. Existential elimination
>
>     $$
>     \frac{\exists x A(x) \qquad [A(a)] \vdots B}{B} 
>     $$
>
>     단, \($a$\)는 fresh variable이어야 하며, \($B$\)에 자유변수로 남으면 안 된다.
>
> 16. Equality introduction
>
>     $$
>     \frac{}{t = t} 
>     $$
>
> 17. Equality elimination
>
>     $$
>     \frac{s = t \qquad A(s)}{A(t)}
>     $$
>
> 18. Double negation elimination
>
>     $$
>     \frac{\neg \neg A}{A} 
>     $$
>
> 19. Law of excluded middle
>
>     $$
>     A \lor \neg A 
>     $$
>
> 20. Proof by contradiction
>
>     $$
>     \frac{[\neg A] \vdots \bot}{A} 
>     $$

<br>

**3.2 Semantics of first-order logic**
