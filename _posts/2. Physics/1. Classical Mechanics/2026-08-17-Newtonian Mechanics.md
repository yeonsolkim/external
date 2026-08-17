---
layout: post
title: "Newtonian Mechanics"
date: 2026-08-17 00:00:00 +0900
category_path:
  - 2. Physics
  - 1. Classical Mechanics
created_at: 2026-08-17 13:05:49 +0900
last_modified_at: 2026-08-17 14:35:28 +0900
---

**Definition 1.** We consider a system of $k$ particles with fixed masses $m_1,\dots, m_k$, located at positions $\mathbf x_1,\dots,\mathbf x_k\in \mathbb R^3$ at time $t\in \mathbb R$. The $i$th particle is acted upon by a force $\mathbf F_i$ that depends on the positions $\mathbf x_1,\dots,\mathbf x_k$ and the time $t$. We then concatenate the positions and forces into $3k$-vectors

$$ F = (\mathbf F_1,\dots,\mathbf F_k)\in \mathbb R^{3k}\quad \text{and} \quad x = (\mathbf x_1,\dots,\mathbf x_k)\in \mathbb R^{3k},$$

and the masses into a $3k\times 3k$ matrix

$$ m = 
\begin{pmatrix} m_1I_3 & 0 & \dots & 0 \\ 0 & m_2I_3 & \dots & 0 \\ \vdots & \vdots & & \vdots \\ 0 & 0 & \dots & m_kI_3 \end{pmatrix}
$$

where $I_3$ is the $3\times 3$ identity matrix. And set 

$$ v = \frac {dx}{dt}\quad \text{and} \quad a = \frac{dv}{dt}.$$

<br>

**Principle 2** (Newton's law). Newton's law is a foundational physical law of dynamics of classical mechanics, which is a second-order ordinary differential equation for $x$ when $F$ is known:

$$ F = ma.$$

<br>

**Definition 3.** We shall consider only autonomous and conservative forces, that is, those $F$ that depend only on $x$ and for which the line integral $\int_C F\cdot dx$ vanishes for every closed curve $C$ in $\mathbb R^{3k}$. 