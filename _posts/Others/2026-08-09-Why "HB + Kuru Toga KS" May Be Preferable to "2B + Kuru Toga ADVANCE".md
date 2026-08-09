---
layout: post
title: "Why \"HB + Kuru Toga KS\" May Be Preferable to \"2B + Kuru Toga ADVANCE\""
date: 2026-08-09 00:00:00 +0900
category_path:
  - Others
created_at: 2026-08-09 14:04:09 +0900
last_modified_at: 2026-08-09 14:24:36 +0900
---

The comparison can be understood as a trade-off between two different strategies for controlling stroke width. The Kuru Toga ADVANCE uses the W Speed Engine, which rotates the lead approximately once every 20 strokes, whereas the 2023 Kuru Toga KS uses a lower-stroke mechanism with a slower rotation rate of roughly one revolution per 40 strokes. Thus, ADVANCE compensates aggressively for asymmetric lead wear through rapid rotation, while KS prioritizes tip stability and reduced axial play. For a user who is sensitive to the slight looseness or vertical movement of the ADVANCE mechanism, the KS architecture therefore provides a substantial mechanical advantage even though its rotational correction is slower.

 Lead hardness can partly compensate for this slower rotation. Let $w$ denote stroke width, $F$ pencil pressure, and $t$ cumulative writing time since the lead tip last had an approximately symmetric shape. A useful conceptual model is

$$  
w = w(F, t, H, \theta),  
$$

where $H$ represents lead hardness and $\theta$ represents the instantaneous orientation and geometry of the worn tip. Softer 2B lead wears relatively rapidly, so asymmetric wear can produce a comparatively large

$$  
\left|\frac{\partial w}{\partial t}\right|.  
$$

ADVANCE suppresses this effect by changing $\theta$ more frequently through its 20-stroke rotation cycle. HB lead, by contrast, wears more slowly, so even with the KS engine's slower rotation we would expect a smaller rate of tip-shape evolution. Qualitatively,

$$  
\left|\frac{\partial w}{\partial t}\right|_{\mathrm{HB}}  
< 
\left|\frac{\partial w}{\partial t}\right|_{\mathrm{2B}}.  
$$

Consequently, "HB + KS" and "2B + ADVANCE" solve essentially the same problem by different means: the former reduces the rate at which uneven wear develops, while the latter corrects uneven wear more frequently after it develops.

 A second possible advantage of HB is reduced sensitivity of stroke width to variations in writing pressure. Since HB is harder and less readily abraded than 2B, fluctuations in $F$ should cause smaller changes in the geometry of the contacting lead surface. In conceptual terms, one may expect

$$  
\left|\frac{\partial w}{\partial F}\right|_{\mathrm{HB}}  
<  
\left|\frac{\partial w}{\partial F}\right|_{\mathrm{2B}},  
$$

although this particular inequality should be regarded as a physically plausible hypothesis rather than a precisely established quantitative result for these specific leads. A similar argument applies to darkness $D$: 2B generally responds more strongly to pressure because additional pressure deposits more graphite and binder material onto the paper, whereas HB should exhibit a smaller variation in darkness. Thus HB may reduce not only the mean stroke width but also the variance

$$  
\operatorname{Var}(w),  
$$

arising from ordinary fluctuations in pressure, wear state, and tip orientation during actual handwriting.

 The overall system-level trade-off can therefore be summarized as

$$  
\text{soft, dark lead}  
+  
\text{rapid rotational correction}  
$$

versus

$$  
\text{hard, slowly wearing lead}  
+  
\text{mechanically stable tip}.  
$$

The first combination favors darkness, smoothness, and aggressive maintenance of a sharp tip. The second sacrifices some darkness and softness in exchange for lower lead consumption, lower clicking frequency, reduced tip play, slower development of asymmetric wear, and potentially lower sensitivity of stroke width to writing pressure. If the primary objective is not maximum darkness but rather predictable, fine, mechanically stable strokes for mathematical notation, subscripts, symbols, and dense technical writing, "HB + KS" is therefore a particularly coherent combination.