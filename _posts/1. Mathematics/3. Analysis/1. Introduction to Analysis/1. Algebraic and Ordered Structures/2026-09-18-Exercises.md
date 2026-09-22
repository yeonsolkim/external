---
layout: post
title: "Exercises"
date: 2026-09-18 00:00:00 +0900
category_path:
  - 1. Mathematics
  - 3. Analysis
  - 1. Introduction to Analysis
  - 1. Algebraic and Ordered Structures
created_at: 2026-09-18 12:16:08 +0900
last_modified_at: 2026-09-22 10:06:46 +0900

publish: false
---

**Exercise 1.1** Prove that for all $x\in \mathbb R$ and $n\in \mathbb N^{+},$

$$ nx = n\cdot x.$$

*Proof.* By Definition 1.1.2 and Definition 1.1.5,

$$ \begin{align}
nx 
&= \underbrace{x + \cdots + x}_{n\ \text{times}} = 1\cdot x + \cdots + 1\cdot x \\
&= (\underbrace{1 + \cdots + 1}_{n\ \text{times}})\cdot x\\
&= n\cdot x.\tag*{\(\square\)}
\end{align}
$$

**Exercise 1.2.** Prove that for all $x,y\in \mathbb R,$

1. $0<1$;
2. if $x<y$ then $-y<-x$;
3. if $0<x$ and $0<xy$ then $0<y$;
4. if $0<x<y$ then $1/y<1/x$;
5. if $x<y$ then $x<(x+y)/2<y$.

*Proof.* (1) We have $0\le 1^2.$ Since $1^2 = 1\cdot 1= 1$ and $0\ne 1,$ $0<1.$
(2) Suppose, for contradiction, that $-x\le -y.$ Since $x<y,$ it follows that $x+(-x)<y+(-y),$ which contradicts $x+(-x)=y+(-y).$ Hence $-y<-x.$
(3) Suppose, for contradiction, that $y\le 0.$ If $y=0,$ then $x\cdot y = 0,$ which contradicts $0<x\cdot y.$ If $y<0,$ then $0<-y,$ by (1). Thus $0<x\cdot (-y).$ It yields $0<-(x\cdot y),$ since $x\cdot(-y)= -(x\cdot y).$ Therefore $x\cdot y<0,$ which contradicts $0<x\cdot y.$ Consequently, it is concluded that $0<y.$
(4) If $1/x\le 1/y$ then $x\cdot(1/x)<y\cdot(1/x)\le y\cdot(1/y).$ If follows that $x\cdot(1/x)<y\cdot (1/y),$ which contradicts $x\cdot(1/x)=1=y\cdot(1/y).$ Therefore it is concluded that $1/y< 1/x.$
(5) Since $(1/2)\cdot (1+1) = 1,$ we have $((x+y)/2)\cdot(1+1) = x+y.$ We also have $x\cdot (1+1)= x + x$ and $y\cdot (1+1)  =y+y.$ Since $x<y$ implies $x+x<x+y<y+y,$ we finally get $x<(x+y)/2<y.$ <span class="qed">$\square$</span>

**Exercise 1.3.** Let $r\in \mathbb Q,r\ne 0,$ and $x\notin \mathbb Q.$ Prove that $r+x\notin \mathbb Q$ and $r\cdot x\notin \mathbb Q.$

**Exercise 1.4.** Fix $a>1$.
1. Prove that if $m,n,p,q\in \mathbb Z$, $n,q>0$, and $r=m/n=p/q$, then $(a^m)^{1/n} = (a^p)^{1/q}$.
2. Prove that $a^{r+s} = a^r a^s$ for all $r,s\in \mathbb Q$.
3. Let $x\in \mathbb R$ and define $A(x)$ to be the set of all numbers $a^r$ where $r\in \mathbb Q$ and $r\le x$. Prove that if $s\in \mathbb Q$, then $a^s = \sup {A(s)}$.


**Exercise 1.5.** For $a,x\in \mathbb R$ with $a>1$, define $a^x = \sup {A(x)}$. Prove that $a^{x+y} = a^xa^y$ for all $x,y\in \mathbb R$.



**Exercise 1.6.** If $z_1,\dots,z_n$ are complex, prove that

$$ |z_1+z_2+\cdots +z_n| \le |z_1| + |z_2| + \cdots + |z_n|.$$

*Proof.* The case $n=1$ is immediate, since $\vert{}z_1\vert{} \le \vert{}z_1\vert{}.$ The case $n=2$ holds by Theorem 1.3.11.
Now we suppose that for some $n\ge 3,$

$$\vert{}z_1+\cdots+z_n\vert{} \le \vert{}z_1\vert{}+\cdots+\vert{}z_n\vert{}.$$

Then, applying Theorem 1.3.11, we obtain

$$\begin{aligned} \vert{}z_1+\cdots+z_n+z_{n+1}\vert{} &= \vert{}(z_1+\cdots+z_n)+z_{n+1}\vert{}\\ &\le \vert{}z_1+\cdots+z_n\vert{}+\vert{}z_{n+1}\vert{}\\ &\le \vert{}z_1\vert{}+\cdots+\vert{}z_n\vert{}+\vert{}z_{n+1}\vert{}. \end{aligned}$$

Therefore, by mathematical induction,

$$\vert{}z_1+\cdots+z_n\vert{} \le \vert{}z_1\vert{}+\cdots+\vert{}z_n\vert{}$$

for every positive integer $n.$ <span class="qed">$\square$</span>

**Exercise 7.** If $x$ and $y$ are complex, prove that

$$ \big\vert|x|-|y|\big\vert\le |x-y|.$$

*Proof.* Let $|x|=a,|y|=b,$ and $|x-y|=c.$ Since $|x\overline y| = \left( (x\overline y)(\overline x y)\right)^{1/2} = ab,$ $\operatorname{Re} (x\overline y)\le ab,$ by Proposition 1.3.10. Then we have

$$ a^2+b^2-2ab\le a^2+b^2-2\operatorname{Re} (x\overline y).$$

Since

$$
\begin{align}
a^2+b^2-2\operatorname{Re} (x\overline y) 
&= x\overline x + y\overline y -x\overline y -\overline x y\\
&= (x-y)(\overline x -\overline y)\\
&=(x-y)\overline {(x-y)} \\
&= c^2,
\end{align}
$$

we have $(a-b)^2\le c^2.$ Taking square roots yields $\big\vert|x|-|y|\big\vert\le |x-y|.$ <span class="qed">$\square$</span>