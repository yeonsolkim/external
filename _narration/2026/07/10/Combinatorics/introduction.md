---
section: introduction
title: Introduction
kind: introduction
document: Combinatorics
url: /2026/07/10/Combinatorics.html
source: 7772d0c25808445d0857b9c3b6f8ef447ad0cb1a1264f544d5a91a0997f2c15e
skeleton: 2
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-18
body: c712db6465ef3bab0e3225f1a6d1d6e8e5dc76a4c0e553f7a9988605710a2dbb
words: 1844
---

One. Trials and outcomes. An outcome is one particular possible result of the trial. The sample space, usually denoted by omega, is the set of all possible outcomes. An event is a subset of the sample space. For example, if one die is rolled, the event that an even number appears is A equals the set two, four, six, and is contained in omega.

The statement “event A occurs” means that the actual outcome of the trial belongs to A. Thus, if the actual outcome is four, then A occurs; if the actual outcome is five, then A does not occur. Accordingly, the statement “event A can occur in m ways” means that A contains m possible outcomes: the size of A equals m.

For instance, the number of ways event A equals the set two, four, six can occur is three because there are three outcomes that make A occur.

Two. Addition rule. Two events A and B are disjoint, when they cannot occur in the same trial, which is denoted by A intersection B equals the empty set.

If the size of A equals m, the size of B equals n, and A intersection B equals the empty set, then the event “A or B occurs” is denoted by A union B. We can easily see that the size of A union B equals the size of A plus the size of B, which equals m plus n.

This formula is called the addition rule.

Three. Multiplication rule. A process is a trial that is completed in successive stages, whose outcome is called the complete outcome. We let A be the event of the first stage and B the event of the second stage, with the size of A equals m and the size of B equals n.

The event “A occurs and then B occurs” is denoted by A then B. Suppose that x records the first-stage outcome and y records the second-stage outcome. Since each of the m possible values of x can be paired with each of the n possible values of y, the size of A then B equals the size of A times the size of B, which equals m n.

This formula is called the multiplication rule. The multiplication rule extends to any finite number of stages. If a process consists of k successive stages, and each event A i of the i-th stage has n i possible outcomes, then the event A one through A k can occur in n one times n two times and so on times n k ways.

Four. Factorial. For a positive integer n, the factorial of n is defined by n factorial equals n times n minus one times and so on down to two times one.

We also define zero factorial equals one. To arrange n distinct objects in a row, we have n choices for the first position, n minus one choices for the second position, and so on. By the multiplication rule, the number of ways the process of arrangements can be completed is n times n minus one times and so on down to two times one, which equals n factorial.

Five. Permutations. Let zero be less than or equal to r, which is less than or equal to n. An r-permutation of n distinct objects is a complete outcome of a process of selecting r objects in order without repetition. The first object can be chosen in n ways, the second in n minus one ways, and the r-th in n minus r plus one ways. Hence the number of r-permutations is n P r equals n times n minus one times and so on times n minus r plus one, which equals n factorial over n minus r factorial.

In particular, n P n equals n factorial and n P zero equals one.

Six. Combinations. Let zero be less than or equal to r, which is less than or equal to n. An r-combination of n distinct objects is a complete outcome of a process of selecting r objects without repetition in which the order of selection is irrelevant. The number of r-combinations is denoted by n choose r, or n choose r.

Each r-combination gives rise to r factorial different r-permutations by arranging its selected objects in every possible order. Therefore, n P r equals n choose r times r factorial, and consequently n choose r equals n P r over r factorial, which equals n factorial over r factorial times n minus r factorial.

Since choosing r objects to include is equivalent to choosing the remaining n minus r objects to exclude, we also have n choose r equals n choose n minus r.

Seven. Pascal’s identity. Let n and r be positive integers with r less than n. Then n choose r equals n minus one choose r minus one, plus n minus one choose r.

Proof. Let S be a set of n elements and fix an element a in S. The r-combinations can be divided into two disjoint classes: those containing a and those not containing a. An r-combination containing a is obtained by choosing r minus one elements from the remaining n minus one elements, while an r-combination not containing a is obtained by choosing r elements from them. Applying the addition rule, we get the Pascal’s identity. This completes the proof.

Eight. Binomial theorem. Let n be a nonnegative integer. For any real numbers x and y, the quantity x plus y to the n equals the sum from r equals zero to n of n choose r, x to the n minus r, y to the r.

Proof. Consider the raw expansion of the quantity x plus y, times the quantity x plus y, and so on, with n factors.

From the point of view of the act of expansion, the two n occurrences of x and y in the original expression can be distinguished from one another: each occurrence belongs to a particular original factor. Thus, if necessary, we may mentally label them as the quantity x one plus y one, times the quantity x two plus y two, and so on times the quantity x n plus y n, where the subscripts merely record provenance. Now consider one raw term in the fully expanded expression. By the heuristic that multiplication preserves degree, the raw term consists of exactly n letters. First, every factor of this raw term must be one of the summands already present in the original expression. Otherwise, some letter not present in the original expression would somehow have been created during expansion, which makes no sense. Second, two different factors of the raw term cannot both have come from the same original factor. If, for example, both x i and y i occurred in the same raw term as contributions from x i plus y i, then at some point in the expansion those two summands would have had to be multiplied by each other. But distributive expansion never multiplies the summands within a single factor against one another. Hence, every raw term receives at most one summand from each original factor. Since the raw term contains n letters and there are exactly n original factors, it follows that it receives exactly one summand from each original factor. We may therefore classify raw terms according to the number of occurrences of x they contain. There are n plus one possible types, corresponding to zero, one, and so on up to n occurrences of x. For example, consider raw terms containing exactly one x. That x must have come from one of the n original factors. Suppose it came from the i-th factor. Since every original factor contributes exactly one summand, the i-th factor must contribute x i. Moreover, because the raw term contains no other x, every other factor must contribute its y-summand. Thus any such raw term must have the provenance x i times the product over j not equal to i of y j.

At this point, however, we have shown only that there is a single possible composition for a raw term whose unique x comes from the i-th factor. We have not yet shown that this composition cannot occur twice in the raw expansion. In principle, our previous heuristics alone do not rule out two distinct occurrences of exactly the same raw term. This reveals a further primitive heuristic about the act of distributive expansion: Expansion does not spontaneously duplicate a term occurrence. A given multiplication of two existing term occurrences produces its product occurrence once. Now suppose, for contradiction, that two raw terms with exactly the same provenance x i times the product over j not equal to i of y j occurred in the final raw expansion. Trace the two occurrences backward through the expansion. At the last multiplication step, either they came from two distinct identical partial terms, or a single multiplication event somehow produced the same product twice. The latter is ruled out by the no-spontaneous-duplication heuristic. Hence the corresponding partial term must already have occurred twice one stage earlier. Applying the same reasoning repeatedly, we are forced to trace the duplication all the way back to the original expression. Eventually, this would require the same summand occurrence in one of the original factors to have been present twice from the beginning. But each such occurrence appears only once in the original expression. Therefore, a fixed provenance can produce exactly one raw term occurrence. Consequently, for each i, there is exactly one raw term containing a single x whose x comes from the i-th original factor. Hence there are exactly n raw terms of type x y to the n minus one. The same reasoning extends immediately. If a raw term is required to contain exactly r occurrences of x, then once we specify which r original factors contribute their x-summands, every remaining factor is forced to contribute its y-summand. That specification determines one possible provenance, and the no-spontaneous-duplication heuristic guarantees that this provenance occurs exactly once. Thus, counting raw terms with exactly r occurrences of x reduces to counting the ways to specify which r of the n original factors contribute x. That is, the number of the raw terms of type x to the r, y to the n minus r, is exactly the number of r-combinations of n distinct objects, n choose r. This proves the binomial theorem. This completes the proof.

Nine. Corollaries. Setting x equals y equals one in the binomial theorem gives the sum from r equals zero to n of n choose r equals two to the n.

Since every subset of an n-element set has a unique cardinality r, the sum on the left counts all subsets of the set. Thus an n-element set has two to the n subsets. If n is positive, setting x equals one and y equals minus one gives the sum from r equals zero to n of minus one to the r, times n choose r, equals zero.
