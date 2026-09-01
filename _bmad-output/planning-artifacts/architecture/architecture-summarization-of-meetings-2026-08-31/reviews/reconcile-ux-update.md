# UX reconciliation — architecture update

**Verdict: conditional pass.** Direct audio intake/storage and structured `taskNumber` exact/prefix search are now materially aligned with the final UX. The spine should not be finalized unchanged because AD-16 contradicts the final implementation policy, and the playable-media boundary remains implicit.

## Findings

1. **BLOCKER — AD-16 permits CSS that final `DESIGN.md` forbids.** The spine allows custom CSS for “layout/product-specific delta”. Final UX explicitly prohibits CSS, CSS Modules, styled wrappers, internal selector overrides, and `styles`/`classNames` customization; if tokens, props, and composition cannot express a requirement, implementation must pause for a separate design decision. Amend AD-16 to inherit that exact no-custom-styling rule. The rest of the Ant Design invariant is aligned: `antd` is pinned in Stack; one `ConfigProvider`/`App` composition root owns Russian locale, system light/dark theme selection, and design/component tokens; product components remain compositions over Ant Design.

2. **MAJOR — native player exception and media-delivery contract are not explicit.** Final UX makes browser-native `<video controls>`/`<audio controls>` the sole documented exception to the Ant Design-only base and requires a working embedded player for retained source audio/video. AD-16 does not name the exception, while AD-2/AD-13 guarantee original-byte retention and prepared audio but not browser delivery/playability. Add an invariant that explicitly permits native media controls and assigns the backend/frontend boundary for a playable source (at minimum content type, byte-range/seek behavior, captions/VTT route, missing-media response, and whether unsupported source containers use a derived playback artifact). Otherwise an FFmpeg-decodable import can satisfy intake while failing the approved player journey.

3. **PASS — direct audio import and durable retention are coherently covered.** AD-13 accepts exactly one audio or video source, streams and validates it before creating a Meeting/job, preserves the source, and derives canonical `preparedAudio` without mutating it. AD-2 distinguishes source/prepared artifacts, retains original bytes without TTL until explicit deletion, uses staged atomic publication, and preserves text on media-only deletion. OQ-1 correctly defers only supported audio formats and size/duration limits, not the audio/video contract itself.

4. **PASS — `taskNumber` exact/prefix contract is implementation-ready.** AD-9 adds display and normalized Meeting fields, a non-unique partial B-tree outside FTS5, identical write/query normalization, equality/prefix range semantics, and bans fuzzy/contains/FTS/semantic fallback. AD-11 exposes `GET /api/v1/meetings?taskNumber=…&taskNumberMatch=exact|prefix`, AND-composes facets, returns typed match metadata, and preserves an empty-page/echo-query no-match contract. This matches the approved UX search/filter behavior. The now-stale `EXPERIENCE.md` open item claiming AD-9 does not cover this field should be removed or marked resolved so the source set does not contradict the spine.

5. **PASS WITH GATE CLARIFICATION — theme/accessibility ownership is sound but the release wording is narrower than UX.** AD-16 makes final UX accessibility contracts and tests mandatory over Ant Design defaults, and AD-14 covers Chromium/Firefox keyboard, labels, and non-color checks. For unambiguous acceptance, AD-14 should name the inherited WCAG 2.2 AA floor and final UX outcomes: automated theme contrast, visible focus, 44×44 product controls, reduced motion, 200%/320 px reflow, stable live-region behavior, and equivalent audio/video/evidence navigation. This is a gate clarification, not a competing UI design.

## Reconciliation summary

| UX contract | Spine coverage | Result |
|---|---|---|
| Ant Design stack and centralized theming | AD-16, Stack, Structural Seed | Pass |
| No custom styling | AD-16 | Conflict |
| Native accessible audio/video player | AD-16, AD-2, AD-13 | Partial |
| Direct audio import and storage | AD-2, AD-13, Deferred OQ-1 | Pass |
| `taskNumber` indexed exact/prefix API | AD-9, AD-11, conventions | Pass |
| WCAG 2.2 AA behavioral floor | AD-14, AD-16 | Inherited; gate should be explicit |
