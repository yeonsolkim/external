---
layout: post
title: Tenses and aspects
date: 2026-04-03 16:35:00 +0900
categories:
  - English
  - 2. Grammatical Meaning
---

## 1. Klein's three-time model
1. $UT$ (utterance time): 말하는 시간
2. $TT$ (topic time): 이야기하는 대상 시간 (화제가 되는 시간)
3. $ET$ (event time): 사건이 일어나는 시간


## 2. Definitions
 1. precedence: $I < J \iff \forall t \in I\ \forall t' \in J\ t < t'$
 2. inclusion: $I\subset J \iff \forall t\,(t\in I \rightarrow t\in J)$


## 3. Tenses

| **Category** | **Relation** |
| ------------ | ------------ |
| past     | **$TT < UT$**  |
| present  | **$UT \subset TT$** |
| future   | **$UT < TT$**       |


## 4. Aspects

| **Category**    | **Relation**             | Expression |
| --------------- | ------------------------ | ----- |
| perfective  | **$ET \subset TT$** |
| progressive | **$TT \subset ET$**      | progressive auxiliary be |
| perfect     | **$ET < TT$**            | perfect auxiliary have |


## 5. 주요 조합

| **Category**                 | **Relation**                            | Expression             |
| ---------------------------- | --------------------------------------- | ---------------------- |
| past perfective          | $(TT < UT) \land (ET \subset TT)$       | preterite            |
| present progressive | $(UT \subset TT) \land (TT \subset ET)$ | progressive auxiliary be (plain form)    |
| present perfect          | $(UT \subset TT) \land (ET < TT)$       | perfect auxiliary have (plain form) |
| future perfective        | $(UT < TT) \land (ET \subset TT)$       | modal auxiliary will  |


## 6. Non-finite clauses
Non-finite clauses는 matrix clause의 $TT$를 물려받는다.
>Example.<br>
>Having discovered that elliptical orbits fit the observations, he could not reconcile them with his idea.
>* tense: $TT_{non-finite} = TT_{matrix}<UT$
>* aspect: $ET < TT$ 