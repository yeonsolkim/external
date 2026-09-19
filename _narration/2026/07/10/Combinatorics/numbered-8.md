---
section: numbered-8
title: 8. Binomial theorem
kind: numbered
document: Combinatorics
url: /2026/07/10/Combinatorics.html
source: 207d0229514901447943365a4f0aa19a0d2c11ffab2d6554ae2f5c6d55485011
skeleton: 3
prompt: lecture-v2
model: gpt-5.5
generated: 2026-09-19
body: 48245a535baed99048c653caca07f22589e5972c338c74fc3f73414477298b45
words: 846
---

8. Binomial theorem. Let n be a nonnegative integer. For any real numbers x and y, we have

x plus y, to the n, equals the sum from r equals zero to n of n choose r, x to the quantity n minus r, y to the r.

Proof. Consider the raw expansion of

x plus y, times x plus y, times and so on, times x plus y, with n factors.

From the point of view of the act of expansion, the two n occurrences of x and y in the original expression can be distinguished from one another: each occurrence belongs to a particular original factor. Thus, if necessary, we may mentally label them as

x one plus y one, times x two plus y two, times and so on, times x n plus y n,

where the subscripts merely record provenance. Now consider one raw term in the fully expanded expression. By the heuristic that multiplication preserves degree, the raw term consists of exactly n letters. First, every factor of this raw term must be one of the summands already present in the original expression. Otherwise, some letter not present in the original expression would somehow have been created during expansion, which makes no sense. Second, two different factors of the raw term cannot both have come from the same original factor. If, for example, both x i and y i occurred in the same raw term as contributions from x i plus y i, then at some point in the expansion those two summands would have had to be multiplied by each other. But distributive expansion never multiplies the summands within a single factor against one another. Hence, every raw term receives at most one summand from each original factor. Since the raw term contains n letters and there are exactly n original factors, it follows that it receives exactly one summand from each original factor. We may therefore classify raw terms according to the number of occurrences of x they contain. There are n plus one possible types, corresponding to zero, one, and so on up to n occurrences of x. For example, consider raw terms containing exactly one x. That x must have come from one of the n original factors. Suppose it came from the i-th factor. Since every original factor contributes exactly one summand, the i-th factor must contribute x i. Moreover, because the raw term contains no other x, every other factor must contribute its y-summand. Thus any such raw term must have the provenance

x i times the product over j not equal to i of y j.

At this point, however, we have shown only that there is a single possible composition for a raw term whose unique x comes from the i-th factor. We have not yet shown that this composition cannot occur twice in the raw expansion. In principle, our previous heuristics alone do not rule out two distinct occurrences of exactly the same raw term. This reveals a further primitive heuristic about the act of distributive expansion: Expansion does not spontaneously duplicate a term occurrence. A given multiplication of two existing term occurrences produces its product occurrence once. Now suppose, for contradiction, that two raw terms with exactly the same provenance

x i times the product over j not equal to i of y j

occurred in the final raw expansion. Trace the two occurrences backward through the expansion. At the last multiplication step, either they came from two distinct identical partial terms, or a single multiplication event somehow produced the same product twice. The latter is ruled out by the no-spontaneous-duplication heuristic. Hence the corresponding partial term must already have occurred twice one stage earlier. Applying the same reasoning repeatedly, we are forced to trace the duplication all the way back to the original expression. Eventually, this would require the same summand occurrence in one of the original factors to have been present twice from the beginning. But each such occurrence appears only once in the original expression. Therefore, a fixed provenance can produce exactly one raw term occurrence. Consequently, for each i, there is exactly one raw term containing a single x whose x comes from the i-th original factor. Hence there are exactly n raw terms of type x y to the n minus one. The same reasoning extends immediately. If a raw term is required to contain exactly r occurrences of x, then once we specify which r original factors contribute their x-summands, every remaining factor is forced to contribute its y-summand. That specification determines one possible provenance, and the no-spontaneous-duplication heuristic guarantees that this provenance occurs exactly once. Thus, counting raw terms with exactly r occurrences of x reduces to counting the ways to specify which r of the n original factors contribute x. That is, the number of the raw terms of type x to the r, y to the quantity n minus r, is exactly the number of r-combinations of n distinct objects, n choose r. This proves the binomial theorem. This completes the proof.
