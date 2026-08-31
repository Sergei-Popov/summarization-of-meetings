# Editorial Structure Review

This document pair exists to help human UX, architecture, and implementation readers—and their AI tooling—retrieve the approved visual and behavioral contracts quickly and implement the meeting-analysis experience consistently.

**Model:** Reference/Database. The peer contracts appropriately optimize for random access, MECE ownership, stable component IDs, and consistent table schemas; the mandated `DESIGN.md` and `EXPERIENCE.md` section order should remain unchanged.

| Pass | Original Text | Revised Text | Changes |
|---|---|---|---|
| structure | `EXPERIENCE.md` — Component Patterns, Interaction Primitives, Accessibility Floor | **CONDENSE:** assign one authority per rule and use exact component-ID cross-references. | Remove three-way repetition; save ~180 words. |
| structure | `DESIGN.md` — Components | **MOVE:** retain visual tokens/geometry/color/emphasis; move behavioral clauses to EXPERIENCE. | Restore peer-contract boundary; save ~105 words. |
| structure | `EXPERIENCE.md` — Requirement-to-flow mapping | **CONDENSE:** preserve each requirement and mapping; replace repeated prose with exact contract anchors. | Keep traceability; save ~115 words. |
| structure | `EXPERIENCE.md` — Foundation and Open items | **CUT:** stable decisions stay in Foundation; unresolved dependencies appear once in Open items. | Remove duplicated task/audio/library follow-ups; save ~45 words. |
| structure | `DESIGN.md` — Colors + foreground/background matrix | **MERGE:** shorten semantic legend; matrix owns surface permissions and contrast constraints. | Save ~45 words. |
| structure | `DESIGN.md` — Layout & Spacing versus EXPERIENCE reading order/responsive | **MOVE:** DESIGN keeps visual geometry; EXPERIENCE owns DOM/overlay/action/reflow behavior. | Save ~35 words. |
| structure | `DESIGN.md` — Do's and Don'ts | **CONDENSE:** retain visual identity contrasts; cross-reference behavioral rules. | Save ~35 words. |
| structure | `EXPERIENCE.md` preamble | **QUESTION:** add 25–35-word contract map linking IA, component behavior, states, accessibility, flows, traceability. | Add ~30 words; improve random access. |
| structure | `DESIGN.md` YAML preamble | **PRESERVE.** | Machine-readable catalog is justified. |
| structure | `EXPERIENCE.md` Component Patterns | **PRESERVE.** | Primary behavioral lookup surface. |
| structure | `EXPERIENCE.md` State Patterns and Key Flows | **PRESERVE.** | Functional reinforcement for humans. |

Estimated net reduction if accepted: ~530 words (7.9% of the 6,733-word pair).
