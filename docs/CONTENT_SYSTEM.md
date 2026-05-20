# Content System

TechScript Video Pipeline is a semiconductor explainer pipeline, not a Micro LED-only demo.

Micro LED is the seed domain because it provides good examples for both rendering lines:

- HyperFrames: industry maps, market data, company comparisons, equipment/material flows.
- Manim: mass transfer, alignment, defect/yield mechanics, optical structures.

The same structure should work for broader semiconductor topics.

## Supported Topic Families

| Family | Core question | Typical topics | Renderer |
| --- | --- | --- | --- |
| Technology principle | How does it work physically? | hybrid bonding, TSV, lithography, Micro LED transfer | Manim |
| Process sequence | What happens step by step? | clean, CMP, align, bond, anneal, inspect | Manim |
| Equipment/material map | What tools and materials are needed? | bonders, metrology, carriers, adhesives, substrates | HyperFrames |
| Industry/value chain | Who does what? | suppliers, foundries, OSATs, equipment vendors | HyperFrames |
| Market/data story | Why now, how big, how fast? | TAM, adoption curve, cost trend, roadmap | HyperFrames |
| System architecture | How do subsystems connect? | CPO, optical engines, chiplets, display backplanes | HyperFrames with Manim inserts |

## Renderer Selection Rules

Use Manim when the explanation depends on:

- motion, force, contact, deformation, alignment, transfer, diffusion, or stacking;
- geometric precision;
- formulas, vectors, coordinates, arrays, particles, or step-by-step physical mechanisms.

Use HyperFrames when the explanation depends on:

- categories, relationships, markets, timelines, value chains, tables, charts, or comparisons;
- strong visual layout and information hierarchy;
- fast iteration on cards, labels, diagrams, SVG icons, and data graphics.

Do not add Remotion yet. It is a possible future replacement for the browser-rendered HyperFrames line, not a replacement for Manim.

## Recommended First Non-MicroLED Episodes

1. `demo-hybrid-bonding-principle`
   - Renderer: Manim
   - Goal: explain oxide/copper hybrid bonding from surface preparation to post-bond anneal.

2. `demo-hybrid-bonding-supply-chain`
   - Renderer: HyperFrames
   - Goal: show the equipment/material/value-chain map behind hybrid bonding.

3. `demo-3d-packaging`
   - Renderer: Mixed
   - Goal: combine a Manim stack/interconnect explanation with a HyperFrames market/system map.

These should become the next reference demos if the project is going to prove that it generalizes beyond Micro LED.
