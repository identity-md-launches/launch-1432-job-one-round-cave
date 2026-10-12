# Round 22 — Guarded Pebble Trail

The final wall is `artifacts/line-4/wall.png`; the required named output is the
identical `artifacts/line-4/wall-v2.png`. Both are **1254 × 1254, RGB PNG**.
The accompanying `dist/line-4/22.jpg` is **512 × 512, baseline RGB JPEG**,
73,430 bytes. Machine-readable dimensions, format and unmet requirements are
recorded in `image-review.json`.

The new mark is a worn charcoal loop containing three red ochre pebbles on the
empty upper-left rock. It stands for checking each event inside a bounded trail.
The ancestral Pepe, his held stone and the earlier loose pebbles remain intact.

The missing ancestor PNG was recovered from the round-01 content-addressed URL
and verified against SHA-256
`da7df3ed310ce393f0748eaee581cc3b623ab512e7ff1ef6abfe42e1be6760c2`.
Rounds 02–21 are explicitly unpainted placeholders referencing the bare cave;
using them as a replacement would discard the ancestor's painting. No old
record was changed. The count rule makes this new record **22**.

The built-in image generator edited the recovered wall with this prompt:

> Edit this existing 1254 by 1254 square cave painting, adding ONLY a small worn
> charcoal-and-yellow-ochre loop enclosing a short trail of three small red
> ochre pebbles in the EMPTY upper-left wall area above and left of Pepe,
> symbolizing bounded checked transfer evidence. Preserve the entire ancestral
> Pepe figure, both hands, all existing pebbles, every ancestral stroke, rock,
> cracks, torchlight, framing and square dimensions unchanged. No erasing,
> moving, cleaning, or redrawing old marks. This is a Lascaux-style hand-made
> pigment mark on rough warm stone with the stone showing through. Do not add
> another frog or hands: preserve Pepe with wide mouth and heavy-lidded eyes
> and his existing five-digit hands. No text, letters, numbers, logos,
> signatures, watermarks, borders, political symbols, photographs, or 3D.

Generation also introduced small texture differences beyond the new mark.
To preserve the actual ancestor, only the generated rectangle
`[230, 180, 415, 360]` on empty rock was published onto the original image,
with a ten-pixel blend at its edge. All decoded pixels outside that rectangle
were asserted identical before publication. The rectangle contains no ancestral
figure or painted mark. Both finished PNGs contain identical bytes. The reviewed
standard-library helper from `gathering/make_thumbnail.py` converted the finished
wall to the required JPEG; no other image was retained in the workspace.

I inspected the final full PNG and JPEG. The broad mouth and heavy-lidded eyes
read as Pepe. Both ancestral hands retain four fingers and one thumb each; the
new mark adds no hands or handprints. The rough warm rock, cracks, torchlight,
square size and framing are retained. The palette is earth pigments with stone
showing through. No words, numbers, captions, signatures, logos, watermarks,
frames, real people or political/hateful symbols were observed. No visual
requirements are knowingly unmet. This is a local visual review, not an
independent certification.
