# Final Reviewer Gate — Technology and Version Fit (2026-09-01 update)

**Review date:** 2026-09-01

**Artifact:** `ARCHITECTURE-SPINE.md`

**Scope:** affected decisions only — Ant Design/React/theme fit, no-custom-CSS feasibility, direct audio/source-media playback, and SQLite `taskNumber` exact/prefix lookup

**Initial verdict:** **NEEDS CORRECTION**

**Initial findings:** Critical 0 / High 2 / Medium 3 / Low 0

**Final recheck verdict:** **PASS WITH MEDIUM FOLLOW-UP**

**Remaining findings after recheck:** Critical 0 / High 0 / Medium 1 / Low 0

The selected frontend version is real and current: Ant Design 6.6.2 is the official release marked **Latest** on 2026-09-01, and its package declares `react`/`react-dom >=18`. Ant Design v6 supports React 19 without the old compatibility patch. `ConfigProvider` design/component tokens, preset default/dark algorithms, Russian locale, and the paired `ConfigProvider > App` root are all supported upstream APIs. The update remains gated because (1) serving only retained original bytes cannot guarantee the required Chromium/Firefox native player for every accepted MP4/MOV/MKV/WebM input, and (2) the SQLite index rule does not bind `task_number_norm` to TEXT affinity, so a compliant schema can silently turn number-like task identifiers into numeric values and break prefix behavior.

## Findings

### VFU-1 — High — Range delivery of original bytes does not guarantee a playable native media representation

**Affected rules:** AD-2, AD-11, AD-13, AD-14.

**Evidence**

- AD-2/AD-13 retain the original source and derive only `preparedAudio`. AD-11 exposes `/media/source`, i.e. the original representation. The PRD accepts video in MP4, MOV, MKV, and WebM and requires a video player for video sources; the UX gate requires parity in Chromium and Firefox.
- The HTML Standard explicitly treats an unsupported container or unsupported codecs as a media-resource error. Its capability API returns only `""`, `maybe`, or `probably`; the standard does not make an arbitrary FFmpeg-decodable source playable by every browser. [WHATWG media resource processing and byte-range fetching](https://html.spec.whatwg.org/multipage/media.html), [WHATWG author-facing media format selection](https://html.spec.whatwg.org/dev/media.html).
- The new HTTP contract is directionally correct: the HTML fetch algorithm can request the entire resource or a byte range, and RFC 9110 defines `206`, `Content-Range`, and `Accept-Ranges: bytes`. These transport semantics cannot add a browser decoder for the retained container/codec. [RFC 9110 §14 Range Requests](https://www.rfc-editor.org/rfc/rfc9110.html#name-range-requests).

**Why it breaks a decision:** an intake adapter can correctly accept a source because `ffprobe`/FFmpeg can decode its audio track, persist the original bytes, and serve correct `206` responses, while the native `<video controls>` fails in one or both release browsers. Such an implementation follows the current spine but violates FR-10 and the AD-14 player/evidence gate. This is especially material because `preparedAudio` is not an equivalent substitute for the required video/fullscreen path.

**Required correction:** choose and bind one of these strategies before import implementation:

1. add a derived `playbackMedia` artifact and define the cross-browser release container/codec profile, publication/deletion saga, source-to-playback provenance, and URL-selection rule; or
2. make browser-decodability in both supported browser families an intake acceptance capability and reject otherwise-decodable sources that cannot satisfy the player contract.

The first strategy preserves the broadest interpretation of the four required video containers. In both strategies, original source bytes remain retained unchanged under AD-2 and `preparedAudio` remains separately owned by transcription.

### VFU-2 — High — The task-number B-tree is sound only if the normalized column and bounds are guaranteed to be TEXT/BINARY

**Affected rules:** AD-9, AD-11, Data convention.

**Evidence**

- The partial composite index shape is valid. SQLite documents `WHERE c IS NOT NULL` as usable for queries that compare `c` with `=`, `<`, `>`, `<=`, or `>=`; therefore equality and a two-sided prefix range can use the proposed partial index. [SQLite partial-index planner rules](https://www.sqlite.org/partialindex.html#queries_using_partial_indexes).
- A multi-column B-tree is ordered first by its left-most column and then by the next column, so `(task_number_norm, id)` is a correct search key plus deterministic tie-breaker. [SQLite multi-column indexes](https://www.sqlite.org/queryplanner.html#_multi_column_indices).
- SQLite affinity is not merely documentation: a column with NUMERIC affinity converts well-formed numeric text to INTEGER/REAL on insertion, while a TEXT-affinity column preserves text. Collation applies to TEXT comparisons; `BINARY` compares string data bytewise. [SQLite storage classes, affinity, comparison, and collations](https://www.sqlite.org/datatype3.html).

**Why it breaks a decision:** the spine defers detailed schema and names the index but does not require `task_number_norm` to have TEXT affinity. A compliant builder can declare it with NUMERIC affinity. Then normalized values such as `00123` are stored as integer `123`; exact values can collapse and the prefix range for `00` returns the wrong result. A BINARY index name alone does not repair storage-class conversion. The application-computed upper bound also has no bound postcondition or defined behavior when the normalized prefix has no finite successor in the permitted alphabet.

**Required correction:** bind `task_number_norm` as nullable **TEXT with `COLLATE BINARY`** (preferably in a STRICT table, or with an equivalent `typeof(...)='text'` constraint for non-null values), bind lower/upper query parameters as TEXT, and require the index DDL to use the same collation. Define the prefix-bound postcondition (`x` is in `[lower, upper)` iff normalized `x` starts with `lower`) plus the no-successor case, or constrain the accepted normalized alphabet so a successor always exists. Add migration/API tests for leading-zero numeric identifiers, non-ASCII casefold expansions, duplicates, the maximum permitted character, exact/no-hit, and prefix pagination; assert index use with `EXPLAIN QUERY PLAN` in the release benchmark.

### VFU-3 — Medium — The strict no-custom-CSS policy is a valid governance choice but is not yet proven capable of rendering the complete final UX

**Affected rules:** AD-14, AD-16, Structural Seed.

**Evidence**

- Ant Design officially supports global design tokens, component tokens, preset default/dark algorithms, and motion disablement via `ConfigProvider`; these are a good fit for the shared palette, radius, component states, dark mode, and reduced-motion baseline. [Ant Design theme API](https://ant.design/docs/react/customize-theme/).
- The official `Flex` API exposes direction, wrapping, alignment, flex shorthand, and gap; its documented tokens are padding tokens. It has no prop or token for an absolute `max-width`. [Ant Design Flex API](https://ant.design/components/flex/).
- The official Grid API exposes proportional spans, offsets/order, gutters, and responsive breakpoints. It likewise has no absolute `max-width` contract. [Ant Design Grid API](https://ant.design/components/grid/).
- Final `DESIGN.md` normatively fixes `content-max: 1200px`. With CSS, inline `style`, and visual `styles`/`classNames` hooks all forbidden, neither the listed Ant layout props nor theme tokens can express that exact maximum on an arbitrarily wide viewport. Similar risks remain for surface-local player theming and any required visual delta that is not a published component token.

**Why it matters:** AD-16 correctly says an unexpressible requirement must stop and receive a separate design decision, so the policy is not internally dishonest. However, AD-14 simultaneously treats the whole final UX as a release contract. Discovering the first unavoidable delta during feature implementation would block the frontend after the architecture has already committed both sides.

**Required correction:** keep the no-custom-CSS policy, but add an early frontend foundation proof before feature work: render the final shell and meeting page at all four UX width bands in both themes using only approved APIs, including exact 1200px content cap, 44×44 controls, canonical DOM/visual order, sticky player, focus treatment, and 320-CSS-px reflow. Every failure must resolve through the already-required design-decision path; it must not silently introduce `style`, CSS, or semantic-DOM visual hooks. If exact `content-max` remains normative, the likely design decision is a narrowly named layout primitive/exception rather than a general styling escape hatch.

### VFU-4 — Medium — The media range contract needs RFC-exact edge semantics before independent HTTP adapters implement it

**Affected rule:** AD-11.

**Evidence**

- RFC 9110 defines range handling for GET, not HEAD. HEAD sends no content and normally mirrors GET representation headers. [RFC 9110 HEAD](https://www.rfc-editor.org/rfc/rfc9110.html#name-head), [RFC 9110 Range](https://www.rfc-editor.org/rfc/rfc9110.html#name-range).
- A single byte range can be bounded (`bytes=0-499`), open-ended (`bytes=500-`), or a suffix (`bytes=-500`). Byte positions are inclusive. A single-part `206` must carry `Content-Range`, and `416` should carry `Content-Range: bytes */<complete-length>`. [RFC 9110 byte ranges](https://www.rfc-editor.org/rfc/rfc9110.html#name-byte-ranges), [RFC 9110 Content-Range](https://www.rfc-editor.org/rfc/rfc9110.html#name-content-range), [RFC 9110 206](https://www.rfc-editor.org/rfc/rfc9110.html#name-206-partial-content), [RFC 9110 416](https://www.rfc-editor.org/rfc/rfc9110.html#name-416-range-not-satisfiable).
- RFC 9110 allows invalid or multi-range input to be ignored or rejected under defined conditions; a valid but unsatisfiable range has distinct `416` semantics.

**Why it matters:** “streaming GET/HEAD”, “single byte-range”, and “invalid range 416” leave separate adapters free to disagree on Range-with-HEAD, suffix/open-ended requests, multi-range input, content length, and `416` headers. Native browser seek behavior commonly exercises open-ended ranges even when the happy-path bounded-range test passes.

**Required correction:** make the route matrix explicit: `HEAD 200` with no body and the same selected-representation metadata as full GET (Range ignored); full `GET 200`; all three satisfiable single-byte forms return `206` with inclusive `Content-Range`, range `Content-Length`, unchanged media `Content-Type`, and `Accept-Ranges: bytes`; valid unsatisfiable input returns `416` plus `Content-Range: bytes */total`; choose one RFC-permitted policy for invalid/multi-range input. Serve the stored representation without content coding/transformation so byte offsets remain source-byte offsets. Exercise the matrix in Chromium and Firefox seek tests.

### VFU-5 — Medium — `ConfigProvider`/`App` is correct, but contextless static feedback APIs remain an allowed divergence

**Affected rule:** AD-16.

**Evidence**

- The official composition order is `<ConfigProvider theme={...}><App>...</App></ConfigProvider>`. `App.useApp()` must execute below `App`. [Ant Design App component](https://ant.design/components/app/).
- Ant Design explicitly warns that static `message.xxx`, `Modal.xxx`, and `notification.xxx` do not inherit `ConfigProvider` context; it recommends hooks or `App`. [Ant Design theme context warning](https://ant.design/docs/react/customize-theme/#basic-usage).
- Russian locale exists in the 6.6.2 source, so locale availability itself is not a gap. [Ant Design 6.6.2 Russian locale](https://github.com/ant-design/ant-design/blob/6.6.2/components/locale/ru_RU.ts).

**Why it matters:** one feature can use `App.useApp()` while another imports a static modal/message method; both use official Ant APIs, but only the first reliably receives the central locale/theme context. That is exactly the divergence AD-16 intends to prevent.

**Required correction:** state the root order and require feedback/modal/notification instances from `App.useApp()` or the corresponding hook/context-holder APIs; forbid contextless static imports in product features. Add a lint/import rule and a Russian-locale + dark-theme modal smoke test.

## Verified fit matrix

| Affected item | Reality/currentness at 2026-09-01 | Fit verdict |
| --- | --- | --- |
| Ant Design 6.6.2 | Real official release from 2026-08-28 and marked Latest. [Release](https://github.com/ant-design/ant-design/releases/tag/6.6.2), [tagged package](https://github.com/ant-design/ant-design/blob/6.6.2/package.json) | **Pass.** Correct production UI dependency. Pin `antd`, matching `@ant-design/icons@6`, and transitives in the frontend lockfile. |
| React 19.2.7 + Ant Design 6.6.2 | The tagged package declares `react` and `react-dom >=18`; v6 removes the React-19 compatibility patch. [Package peer dependencies](https://github.com/ant-design/ant-design/blob/6.6.2/package.json#L109-L112), [v6 migration](https://ant.design/docs/react/migration-v6/#react-version-support) | **Pass.** Native fit; do not install `@ant-design/v5-patch-for-react-19`. |
| `ConfigProvider` tokens/algorithms | Global/component tokens and default/dark algorithms are official supported APIs. [Theme API](https://ant.design/docs/react/customize-theme/) | **Pass with VFU-3/VFU-5.** The shared theme is supported; context consumers and unexpressible layout deltas need explicit gates. |
| Russian locale | `ru_RU` is present in the exact 6.6.2 source. [Source](https://github.com/ant-design/ant-design/blob/6.6.2/components/locale/ru_RU.ts) | **Pass.** Use it on the root `ConfigProvider`; product strings remain application-owned. |
| SQLite partial `(task_number_norm, id)` B-tree | Partial-index and left-most composite-index behavior support equality and range scans. [Partial indexes](https://www.sqlite.org/partialindex.html), [query planner](https://www.sqlite.org/queryplanner.html) | **Conditional pass.** Bind TEXT/BINARY storage and successor semantics per VFU-2. |
| Native media HTTP range | RFC 9110 supports the intended 200/206/416 model; WHATWG media fetching can request byte ranges. | **Conditional pass.** Complete the response matrix per VFU-4; provide a browser-playable representation per VFU-1. |
| Direct audio import and retention | The updated source/prepared roles, streaming intake, original-byte retention, explicit deletion, and shared crash-consistent publication path do not conflict with the verified FFmpeg/PyAV/SQLite stack. | **Pass.** Audio format/limit selection remains a legitimate OQ-1 release-corpus gate, but it must also close the player representation question. |

## Gate close conditions

1. Add a browser-playable representation decision or make browser-decodability an explicit intake capability; test every accepted release container/codec in Chromium and Firefox.
2. Bind `task_number_norm` and both prefix bounds to TEXT/BINARY, define successor/no-successor semantics, and add the index/correctness test vectors from VFU-2.
3. Run the no-custom-CSS foundation proof and resolve every unexpressible normative UX delta through a narrow design decision.
4. Specify and test the full GET/HEAD/Range response matrix.
5. Require `ConfigProvider > App` and context-bound `App.useApp()`/hook APIs for modal/message/notification use.

## Recheck — updated spine after reviewer fixes

**Recheck verdict:** **PASS WITH MEDIUM FOLLOW-UP** — both High findings and two of three Medium findings are closed. The remaining Medium is a narrow HTTP representation constraint; there is no remaining critical/high technology or version-fit blocker.

### Finding disposition

| Finding | Status | Recheck evidence |
| --- | --- | --- |
| VFU-1 — playable media representation | **Closed** | AD-2 now owns a `playbackArtifactId`; AD-13 reuses source only for a pinned Chromium+Firefox container/codec allowlist and otherwise derives audio WebM/Opus or video WebM/VP9+Opus under a versioned profile. AD-14 verifies every supported corpus source through prepare, playback, and seek in both browsers on all three OSes and asserts the required FFmpeg encoders. Chromium source lists WebM with Opus and VP9 as supported, Firefox's WebM demuxer maps VP9 and Opus explicitly, and FFmpeg documents the selected `libvpx-vp9` and `libopus` encoders. [Chromium supported media formats](https://chromium.googlesource.com/chromium/src/+/master/media/base/mime_util_internal.cc), [Firefox WebM demuxer](https://searchfox.org/mozilla-central/source/dom/media/webm/WebMDemuxer.cpp), [FFmpeg codec documentation](https://ffmpeg.org/ffmpeg-codecs.html). The choice is therefore technically coherent and protected from browser/version drift by the release gate. |
| VFU-2 — task-number index storage/bounds | **Closed** | AD-9 deliberately selects the alternative robust representation: normalized valid UTF-8 bytes are stored and bound as SQLite BLOB, and prefix upper is `p || 0xFF`. SQLite BLOB affinity does not coerce numeric-looking task numbers, and BLOB comparison is bytewise `memcmp`; valid UTF-8 never contains byte `FF`, so every byte string with prefix `p` lies in `[p, p||FF)` and no non-prefix byte string does. Backend-only normalization, rejection of empty/control queries, ordered `(task_number_norm,id)` pagination, and release vectors close the earlier leading-zero, client-divergence, and no-successor gaps. [SQLite affinity and BLOB ordering](https://www.sqlite.org/datatype3.html), [SQLite partial indexes](https://www.sqlite.org/partialindex.html), [SQLite multi-column query planning](https://www.sqlite.org/queryplanner.html#_multi_column_indices). |
| VFU-3 — strict no-custom-CSS feasibility | **Closed as an early decision gate** | AD-16 keeps the final UX policy intact and now requires a pre-feature-merge spike for normative content-max, sticky, reflow, 44×44, and focus patterns using only approved Ant APIs. Failure blocks merge and requires the narrow design decision requested by the original finding. This is the correct architectural treatment because Ant Flex/Grid provide substantial layout props but no general arbitrary visual-expression guarantee. [Ant Design Flex API](https://ant.design/components/flex/), [Ant Design Grid API](https://ant.design/components/grid/). |
| VFU-4 — media Range response matrix | **Partially closed; one Medium remains** | AD-11 now fixes full GET `200`, all satisfiable single bytes ranges `206`, unsatisfiable `416` with `bytes */N`, malformed/multi-range `400`, Range-ignoring HEAD `200` without body, representation metadata, strong ETag, and browser gates. This closes the prior independent-adapter ambiguity. It still does not prohibit `Content-Encoding` or another transformation on this route. RFC 9110 defines ranges over the encoded byte sequence when content coding is present, so global gzip middleware can make offsets cease to be offsets into the stored playback artifact and can defeat random seek. [RFC 9110 byte-range representation semantics](https://www.rfc-editor.org/rfc/rfc9110.html#name-byte-ranges). **Remaining correction:** state `Content-Encoding: identity`/no transformation for playback responses (and bypass compression middleware), with Range and ETag computed over the stored ready artifact bytes. |
| VFU-5 — ConfigProvider/App context | **Closed** | AD-16 now binds the exact root order `ConfigProvider → App → product routes`, requires context-bound hooks/`App.useApp()`, and forbids static APIs. That matches the official Ant composition/context contract. [Ant Design App sequence](https://ant.design/components/app/#sequence-with-configprovider), [theme context warning](https://ant.design/docs/react/customize-theme/#basic-usage). |

### Final tiered verdict

- **Critical:** 0.
- **High:** 0. Playback derivation/codec fit and BLOB exact/prefix index semantics are now build-convergent.
- **Medium:** 1. Explicitly force identity/no-transform media delivery so Range offsets and the checksum ETag describe the same stored representation.
- **Low:** 0.

The affected stack remains compatible: Ant Design 6.6.2 + React 19.2.7, `ConfigProvider`/tokens/algorithms/locale, SQLite partial composite BLOB indexing, FFmpeg WebM/VP9/Opus derivation, and native media delivery all fit the existing verified stack after the recorded fixes. The architecture may proceed once the remaining media-response line is amended or carried as an implementation-mandatory HTTP test.
