---
layout: post
title: "Combinatorics"
date: 2026-07-11 00:00:00 +0900
category_path:
  - 1. Mathematics
  - 6. Others
created_at: 2026-08-06 13:53:49 +0900
last_modified_at: 2026-09-17 18:26:32 +0900

publish: false
---

**1. Trials and outcomes.** An *outcome* is one particular possible result of the *trial*. The *sample space*, usually denoted by $\Omega$, is the set of all possible outcomes. An *event* is a subset of the sample space. For example, if one die is rolled, the event that an even number appears is

$$A=\lbrace 2,4,6\rbrace \subseteq \Omega.$$

The statement “event $A$ occurs” means that the actual outcome of the trial belongs to $A$. Thus, if the actual outcome is $4$, then $A$ occurs; if the actual outcome is $5$, then $A$ does not occur. Accordingly, the statement “event $A$ can occur in $m$ ways” means that $A$ contains $m$ possible outcomes:

$$|A|=m.$$

For instance, the number of ways event $A=\lbrace 2,4,6\rbrace$ can occur is $3$ because there are three outcomes that make $A$ occur.


**2. Addition rule.** Two events $A$ and $B$ are *disjoint*, when they cannot occur in the same trial, which is denoted by

$$A\cap B=\varnothing.$$

If $|A|=m$, $|B|=n$, and $A\cap B=\varnothing$, then the event “$A$ or $B$ occurs” is denoted by $A\cup B$. We can easily see that

$$|A\cup B|=|A|+|B|=m+n.$$

This formula is called the *addition rule*.


**3. Multiplication rule.** A *process* is a trial that is completed in successive *stages*, whose outcome is called the *complete outcome*. We let $A$ be the event of the first stage and $B$ the event of the second stage, with

$$
|A|=m \quad \text{and} \quad |B|=n.  
$$

The event "$A$ occurs and then $B$ occurs" is denoted by $A\times B$.
Suppose that $x$ records the first-stage outcome and $y$ records the second-stage outcome. Since each of the $m$ possible values of $x$ can be paired with each of the $n$ possible values of $y$, 

$$
|A\times B|=|A||B|=mn.
$$

This formula is called the *multiplication rule*.
The multiplication rule extends to any finite number of stages. If a process consists of $k$ successive stages, and each event $A_i$ of the $i$th stage has $n_i$ possible outcomes, then the event $A_1\times\cdots\times A_k$ can occur in $n_1n_2\cdots n_k$ ways.


**4. Factorial.** For a positive integer $n$, the *factorial* of $n$ is defined by

$$
n!=n(n-1)\cdots 2\cdot 1.
$$

We also define $0!=1$. To arrange $n$ distinct objects in a row, we have $n$ choices for the first position, $n-1$ choices for the second position, and so on. By the multiplication rule, the number of ways the process of arrangements can be completed is

$$
n(n-1)\cdots 2\cdot 1=n!.
$$


**5. Permutations.** Let $0\leq r\leq n$. An *$r$-permutation* of $n$ distinct objects is a complete outcome of a process of selecting $r$ objects in order without repetition. The first object can be chosen in $n$ ways, the second in $n-1$ ways, and the $r$th in $n-r+1$ ways. Hence the number of $r$-permutations is

$$
{}_nP_r=n(n-1)\cdots(n-r+1)=\frac{n!}{(n-r)!}.
$$

In particular, ${}_nP_n=n!$ and ${}_nP_0=1$.


**6. Combinations.** Let $0\leq r\leq n$. An *$r$-combination* of $n$ distinct objects a complete outcome of a process of selecting $r$ objects without repetition in which the order of selection is irrelevant. The number of $r$-combinations is denoted by

$$
{}_nC_r \qquad\text{or}\qquad \binom nr.
$$

Each $r$-combination gives rise to $r!$ different $r$-permutations by arranging its selected objects in every possible order. Therefore,

$$
{}_nP_r={}_nC_r\,r!,
$$

and consequently

$$
{}_nC_r=\frac{ {}_nP_r}{r!}=\frac{n!}{r!(n-r)!}.
$$

Since choosing $r$ objects to include is equivalent to choosing the remaining $n-r$ objects to exclude, we also have

$$
{}_nC_r={}_nC_{n-r}.
$$


**7. Pascal's identity.** Let $n$ and $r$ be positive integers with $r<n$. Then

$$
\binom nr=\binom{n-1}{r-1}+\binom{n-1}r.
$$

*Proof.* Let $S$ be a set of $n$ elements and fix an element $a\in S$. The $r$-combinations can be divided into two disjoint classes: those containing $a$ and those not containing $a$. An $r$-combination containing $a$ is obtained by choosing $r-1$ elements from the remaining $n-1$ elements, while an $r$-combination not containing $a$ is obtained by choosing $r$ elements from them. Applying the addition rule, we get the Pascal's identity.<span class="qed">$\square$</span>


**8. Binomial theorem.** Let $n$ be a nonnegative integer. For any real numbers $x$ and $y$,

$$
(x+y)^n=\sum_{r=0}^n\binom nr x^{n-r}y^r.
$$

*Proof.* Consider the raw expansion of

$$
\underbrace{(x+y)(x+y)\cdots(x+y)}_{n\text{ factors}}.
$$

From the point of view of the act of expansion, the $2n$ occurrences of $x$ and $y$ in the original expression can be distinguished from one another: each occurrence belongs to a particular original factor. Thus, if necessary, we may mentally label them as

$$
(x_1+y_1)(x_2+y_2)\cdots(x_n+y_n),
$$

where the subscripts merely record provenance and do not represent different algebraic values.
Now consider one raw term in the fully expanded expression. By the heuristic that multiplication preserves degree, the raw term consists of exactly $n$ letters.
First, every factor of this raw term must be one of the summands already present in the original expression. Otherwise, some letter not present in the original expression would somehow have been created during expansion, which makes no sense.
Second, two different factors of the raw term cannot both have come from the same original factor. If, for example, both $x_i$ and $y_i$ occurred in the same raw term as contributions from $(x_i+y_i)$, then at some point in the expansion those two summands would have had to be multiplied by each other. But distributive expansion never multiplies the summands within a single factor against one another.
Hence, every raw term receives at most one summand from each original factor. Since the raw term contains $n$ letters and there are exactly $n$ original factors, it follows that it receives exactly one summand from each original factor.
We may therefore classify raw terms according to the number of occurrences of $x$ they contain. There are $n+1$ possible types, corresponding to $0,1,\ldots,n$ occurrences of $x$.
For example, consider raw terms containing exactly one $x$. That $x$ must have come from one of the $n$ original factors. Suppose it came from the $i$th factor. Since every original factor contributes exactly one summand, the $i$th factor must contribute $x_i$. Moreover, because the raw term contains no other $x$, every other factor must contribute its $y$-summand. Thus any such raw term must have the provenance

$$
x_i\prod_{j\ne i}y_j.
$$

At this point, however, we have shown only that there is a single possible *composition* for a raw term whose unique $x$ comes from the $i$th factor. We have not yet shown that this composition cannot occur twice in the raw expansion. In principle, our previous heuristics alone do not rule out two distinct occurrences of exactly the same raw term.
This reveals a further primitive heuristic about the act of distributive expansion: Expansion does not spontaneously duplicate a term occurrence. A given multiplication of two existing term occurrences produces its product occurrence once.
For example, expanding

$$
A(x+y)
$$

produces

$$
Ax+Ay,
$$

not

$$
Ax+Ax+Ay.
$$

There would have to be some distinct source for a second occurrence of $Ax$.
Now suppose, for contradiction, that two raw terms with exactly the same provenance

$$
x_i\prod_{j\ne i}y_j
$$

occurred in the final raw expansion. Trace the two occurrences backward through the expansion. At the last multiplication step, either they came from two distinct identical partial terms, or a single multiplication event somehow produced the same product twice. The latter is ruled out by the no-spontaneous-duplication heuristic. Hence the corresponding partial term must already have occurred twice one stage earlier.
Applying the same reasoning repeatedly, we are forced to trace the duplication all the way back to the original expression. Eventually, this would require the same summand occurrence in one of the original factors to have been present twice from the beginning. But each such occurrence appears only once in the original expression.
Therefore, a fixed provenance can produce exactly one raw term occurrence.
Consequently, for each $i$, there is exactly one raw term containing a single $x$ whose $x$ comes from the $i$th original factor. Hence there are exactly $n$ raw terms of type

$$
xy^{n-1}.
$$

The same reasoning extends immediately. If a raw term is required to contain exactly $r$ occurrences of $x$, then once we specify which $r$ original factors contribute their $x$-summands, every remaining factor is forced to contribute its $y$-summand. That specification determines one possible provenance, and the no-spontaneous-duplication heuristic guarantees that this provenance occurs exactly once.
Thus, counting raw terms with exactly $r$ occurrences of $x$ reduces to counting the ways to specify which $r$ of the $n$ original factors contribute $x$.<span class="qed">$\square$</span>


**9. Corollaries.** Setting $x=y=1$ in the binomial theorem gives

$$
\sum_{r=0}^n\binom nr=2^n.
$$

Since every subset of an $n$-element set has a unique cardinality $r$, the sum on the left counts all subsets of the set. Thus an $n$-element set has $2^n$ subsets. If $n$ is positive, setting $x=1$ and $y=-1$ gives

$$
\sum_{r=0}^n(-1)^r\binom nr=0.
$$
