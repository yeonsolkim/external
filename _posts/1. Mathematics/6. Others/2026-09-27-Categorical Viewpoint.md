---
layout: post
title: "Sets: Categorical Viewpoint"
date: 2026-09-27 00:00:00 +0900
category_path:
  - 1. Mathematics
  - 6. Others
created_at: 2026-09-27 16:02:08 +0900
last_modified_at: 2026-09-27 17:07:42 +0900
publish: false
---
**1. Set-functions.** Let $X$ and $Y$ be sets. If $f$ is a function from $X$ to $Y$, we draw 

$$
\begin{tikzcd}
X \ar[r, "f"] & Y
\end{tikzcd}
\mathpunct{.}
$$


**2. Composition of functions.** Let $f:X\to Y$ and $g:Y\to Z$ be given. If $g \circ f : X\to Z$ is the composite of $f$ and $g$, we may draw diagrams such as 

$$
\begin{tikzcd}
X \ar[r, "f"] \ar[rr, bend right, "g\circ f", swap] & Y \ar[r, "g"] & Z
\end{tikzcd}

\quad \text{or} \quad

\begin{tikzcd}
X \ar[r, "f"] \ar[rd, "g\circ f", swap] & Y \ar[d, "g"] \\
& Z
\end{tikzcd}
$$

and say that the diagrams *commute*.
Generally, saying that a diagram commutes means that whenever two directed paths share the same source and target, the composition of the functions along both paths yields the same result.
It is evident from the definition of composition that composition is *associative*. That is, if $f:X\to Y, g:Y\to Z$, and $h: Z\to W$ are functions, then $h\circ(g\circ f) = (h\circ g)\circ f$; the diagram 

$$
\begin{tikzcd}
X \ar[r, "f"] \ar[rr, bend right, "g\circ f", swap] 
& Y \ar[r, "g"] \ar[rr, bend left, "h\circ g"]
& Z \ar[r, "h"] 
& W
\end{tikzcd}
$$

commutes.
The identity function is very special with respect to compositions. For any function $f:X\to Y$, the diagrams 

$$
\begin{tikzcd}
X \ar[r, "f"] \ar[rr, bend right, "f", swap] 
& Y \ar[r, "\mathrm{id}_Y"] 
& Y
\end{tikzcd}

\quad \text{and} \quad

\begin{tikzcd}
X \ar[r, "\mathrm{id}_X"] \ar[rr, bend right, "f", swap] 
& X \ar[r, "f"] 
& Y
\end{tikzcd}
$$

commute.



**3.  Surjectivity and injectivity.** Let $f:X\to Y$ be a function. A function $g:Y\to X$ is called a *left-inverse* of $f$ if $g\circ f = \mathrm{id}_X$; the following diagram commutes:

$$
\begin{tikzcd}
X \ar[r, "f"] \ar[rr, bend right, "\mathrm{id}_X", swap] & Y \ar[r, "g"] & X
\end{tikzcd}
\mathpunct{.}
$$

A function $h:Y\to X$ is called a *right-inverse* of $f$ if $f\circ h = \mathrm{id}_Y$; the following diagram commutes:

$$
\begin{tikzcd}
Y \ar[r, "h"] \ar[rr, bend right, "\mathrm{id}_Y", swap] & X \ar[r, "f"] & Y
\end{tikzcd}
\mathpunct{.} 
$$

If a function from $Y$ to $X$ is both a left-inverse and right-inverse of $f$, then it is called the *inverse* of $f$.

**Proposition 1.** Let $X\ne \varnothing$, and let $f:X\to Y$ be a function.
1. $f$ is injective if and only if it has a left-inverse.
2. $f$ is surjective if and only if it has a right-inverse.


**4. Cartesian product.**

$$
\begin{tikzcd}[row sep=large, column sep=huge]
A
&
P
  \arrow[l, "\pi_A"']
  \arrow[r, "\pi_B"]
&
B
\\
&
X
  \arrow[ul, "f_A"]
  \arrow[u, dashed, "\exists ! f" description]
  \arrow[ur, "f_B"']
&
\end{tikzcd}
$$


## References
1. Aluffi, P. (2009). *Algebra: Chapter 0.* American Mathematical Society, Providence, RI. [https://doi.org/10.1090/gsm/104](https://doi.org/10.1090/gsm/104)
{:reference}