# Final Reviewer Gate — adversarial update lens

**Artifact:** `ARCHITECTURE-SPINE.md` (`updated: 2026-09-01`, read-only review)

**Focus:** direct audio/source storage, `preparedAudio`, media deletion and delivery, `taskNumber` exact/prefix contract, Summary/auto-tag publication, Ant Design composition policy

**Method:** for each seam, construct independently-built units that obey every applicable AD literally but can still disagree at integration.

## Verdict

**CHANGES REQUIRED — Critical 0 / High 5 / Medium 3 / Low 1.** The requested product decisions are present and point in the right direction, but the update still permits five build-breaking divergences: imported media can be valid for FFmpeg yet unplayable in the required browser player; `preparedAudio` has no durable identity/retention contract; deletion is not fenced against readers and new processing; Unicode prefix bounds are not canonical; and a late summarization result can overwrite newer transcript/Summary/tag edits.

## High

### ADV-U1 — HIGH — A valid retained `source` is not necessarily a browser-playable representation

**Spine:** AD-13 accepts an audio/video source when `ffprobe` finds it readable and decodable. AD-11 serves the original `source` bytes to native `<video>`/`<audio>`. AD-14 checks controls and evidence seek, but neither AD selects a representation strategy for sources that FFmpeg decodes while Chromium/Firefox do not.

**Compliant unit A:** intake accepts the PRD-mandated MKV/MOV container with any codec present in the pinned FFmpeg build and retains the original bytes as `source`.

**Compliant unit B:** the frontend binds the URL from AD-11 directly to native `<video controls>` and assumes correct `Content-Type` plus ranges makes it playable. Chromium or Firefox can still reject the codec/container, so evidence seek and fullscreen fail although both units implemented their literal contract.

**Why it matters:** `ffprobe`/FFmpeg decodability and browser media support are different capability sets. A release gate can detect the mismatch, but the spine gives builders no convergent remediation.

**Action:** **discuss, then autofix.** Choose one invariant before media implementation: either (a) publish a separate versioned `playbackMedia` derivative in a browser-safe baseline, preserving time mapping to `source`; or (b) bind import acceptance to an explicit Chromium+Firefox container/codec allowlist. Because the PRD already admits MP4/MOV/MKV/WebM, the derivative/alias strategy is the safer fit: the player endpoint resolves `source` only when browser-compatible and otherwise resolves `playbackMedia`; original bytes remain the retained source. Add the playback derivative to AD-2 deletion/reconciliation and AD-14 corpus gates.

### ADV-U2 — HIGH — `preparedAudio` is named, but its format, identity and retention are not an invariant

**Spine:** AD-13 creates “отдельный canonical `preparedAudio`” for both media kinds and hands it to every transcription port. AD-2 gives only `source` an explicit no-TTL promise; AD-3 resumes the first unfinished stage and skips successful stages.

**Compliant unit A:** a cleanup unit removes derived `preparedAudio` after successful transcription or summary because only `source` is explicitly retained without TTL. On retry/recovery, it expects `prepare` to be invalidated and recomputed.

**Compliant unit B:** the job state machine sees `prepare=succeeded`, resumes `transcribe`, and expects the authoritative ready artifact still to exist. A provider adapter assumes FLAC while a local adapter independently interprets “canonical” as PCM WAV. Each reading fits the current words; together they yield a missing or incompatible stage input.

**Why it matters:** this can make restart/retry non-deterministic and makes the claim that one prepared artifact feeds all engines unenforceable.

**Action:** **autofix.** Define one `PreparedAudioSpec` (container, codec/sample format, sample rate, channels, time base) or explicitly make the spec part of the immutable stage snapshot. Give the artifact a canonical identity such as `(meetingId, sourceChecksum, preparedAudioSpecDigest)` and one current/ready uniqueness rule. Retain it while a succeeded `prepare` can be reused or any attempt/read lease references it; cleanup must first invalidate the stage under CAS, and recovery must atomically re-run `prepare` if the artifact is absent or its spec/fingerprint differs.

### ADV-U3 — HIGH — Destructive media operations are not fenced against active jobs or ranged readers, and full deletion has no aggregate tombstone

**Spine:** AD-2 allows source-only deletion after a successfully completed job, moves artifacts through `deleting`, and relies on startup reconciliation. AD-11 streams ready media. No rule excludes a later active retry/job, a provider upload, or an already-open media response. Full Meeting deletion is bound by FR-4 but has no explicit aggregate protocol.

**Compliant unit A:** the deletion command finds an earlier completed job, CASes source/derived artifacts to `deleting`, and unlinks them. It assumes the state change is enough to block future reads.

**Compliant unit B:** a worker started a new attempt just before that CAS, or the media endpoint already opened the file and is streaming a byte range. On Linux an unlink can succeed while the open stream continues; on Windows the same unlink can fail. For full deletion, another implementation can cascade DB rows first and leave filesystem orphans for reconciliation, making it impossible to show the PRD-required partial-delete state.

**Why it matters:** all implementations obey `ready` visibility and `deleting`, yet cross-OS outcomes, provider input and the visible deletion result diverge. The source-only precondition is also satisfied by a historical success even when new processing is active.

**Action:** **autofix.** Add a persisted Meeting-scoped destructive-operation gate. Source-only deletion requires current published Transcript/Summary **and no active job**; its CAS prevents new jobs and new media/read grants. Track stage/upload/range readers with leases or opened-artifact references, then choose and state whether deletion waits for them or cancels/revokes them. Full Meeting deletion retains a tombstone with the exact DB/file cleanup set and remaining-material/error status until every file and row is reconciled; only then is the aggregate hidden/removed. Require identical semantics on Linux/macOS/Windows.

### ADV-U4 — HIGH — “lexicographic upper bound” permits incompatible and incorrect Unicode prefix algorithms

**Spine:** AD-9 fixes `NFKC → trim → Unicode casefold`, SQLite `BINARY`, and says the application layer computes a lexicographic upper bound. It does not define that function or bind it to one shared implementation/Unicode version.

**Compliant unit A:** the query builder uses `normalizedPrefix + U+FFFF` (or `U+10FFFF`) as the exclusive upper sentinel.

**Compliant unit B:** a repository computes the successor by incrementing the rightmost scalar and truncating the suffix. Both call their value a lexicographic upper bound, but A excludes valid prefixed strings containing code points above its sentinel, and even `prefix + U+10FFFF + suffix` lies above the supposed maximum. A separate writer/query process can also inherit a different Unicode casefold table after a runtime upgrade.

**Why it matters:** exact/prefix lookup can produce false negatives for stored values even though the index and both sides use the named normalization stages.

**Action:** **autofix.** Make a single versioned domain helper the only owner of `normalizeTaskNumber` and `prefixInterval`, used by write, query, repair and tests. Specify the interval algorithm against SQLite `BINARY` (including no-finite-upper-bound handling), pin the Unicode data/runtime version through migrations, and add conformance vectors for compatibility characters, casefold expansion, astral characters, trailing whitespace and maximum scalars. Schema/index migrations must rebuild `taskNumberNorm` if the normalization version changes.

### ADV-U5 — HIGH — Summarization completion is fenced by the attempt lease, not by the current Transcript/Summary/tag revisions it replaces

**Spine:** AD-3 CASes stage completion on `(attemptId, leaseEpoch, running)`. AD-7 requires a revision precondition for manual replacement. AD-8 atomically publishes Summary and auto tags and preserves tags whose origin is manual.

**Compliant unit A:** a worker snapshots Transcript revision 7 and starts summarization. While it runs, the meeting editor publishes Transcript revision 8, manually edits the current Summary, and converts/deletes tags.

**Compliant unit B:** the worker still owns the attempt lease, so its validator atomically replaces Summary and auto tags from revision 7. The editor assumes its revisioned writes cannot be overwritten without a new confirmation. Both follow the named CAS rules, but the later stage commit can publish an immediately stale Summary, silently replace a newer manual Summary, and resurrect/change tags without reconfirmation.

**Why it matters:** the update correctly makes Summary+autoTags one crash-atomic output, but does not protect that output from concurrent authoritative user mutation.

**Action:** **autofix.** Stage completion must additionally CAS the current `Transcript.revision`, expected current `Summary.revision` (including the revision that was confirmed for replacement), and a Meeting tag-set revision captured at dispatch/confirmation. Any mismatch rejects publication without changing Summary or tags and transitions to a stable `input_changed`/`confirmation_required` outcome. If product policy chooses to publish an old-revision Summary as stale instead, state that explicitly and still forbid replacement of newer manual content without a fresh precondition.

## Medium

### ADV-U6 — MEDIUM — `matchKind` location/meaning and pagination order remain ambiguous

**Spine:** AD-11 returns query metadata with `matchedField=taskNumber`/`matchKind`; AD-9 says results are bounded/paginated. Neither says whether metadata is page-level or per hit, whether an equality row under a `prefix` request is reported as `exact` or `prefix`, nor what total order/cursor makes pages stable.

**Compliant unit A:** API echoes `matchKind=prefix` once for the whole page and paginates by mutable `lastModified` with offsets.

**Compliant unit B:** frontend/search hits expect per-item `matchKind`, label an equal value as `exact`, and resume by `(taskNumberNorm,id)`. Integration loses the required typed hit or skips/duplicates meetings when metadata changes between pages.

**Action:** **autofix.** Put `matchedField` and a precisely defined `matchKind` on every structured hit (separately echo the requested operator in query metadata), fix the exact-within-prefix rule, and define one deterministic order with an `id` tie-break plus offset/keyset semantics. Include the order/cursor and normalized query in the OpenAPI contract and repair/benchmark fixtures.

### ADV-U7 — MEDIUM — Auto and manual tags do not share a canonical identity/collision rule

**Spine:** AD-8 normalizes/deduplicates auto tags, preserves manual tags, and converts an edited auto tag to manual. It does not define normalization for manual tags or what happens when generated and manual display values collide.

**Compliant unit A:** the summary validator casefold-deduplicates only auto candidates, so generated `Security` coexists with manual `security`.

**Compliant unit B:** the meeting editor treats display text as unique, converts the auto row in place, and expects regeneration to preserve its stable ID. Atomic replacement can then either create a duplicate, discard a manual value, or change origin differently depending on which module wins.

**Action:** **autofix.** Define a meeting-local `tagNorm` for **all** origins, a uniqueness constraint `(meetingId, tagNorm)`, stable display/ID behavior, and collision precedence (`manual` wins; generation may attach provenance but never replace manual display/value). Use the same helper for manual edit, auto publication, search and export.

### ADV-U8 — MEDIUM — The Ant Design exception is too narrow for the required native media subtree

**Spine:** AD-16 names only `<video controls>` and `<audio controls>` as exceptions to the Ant Design-only component rule; visual `styles`/`classNames` and custom CSS are correctly prohibited. Final UX also requires a current VTT as `<track kind="captions">` when available.

**Compliant unit A:** the media feature treats native `<source>`/`<track>` children as implicitly inside the player exception and renders captions.

**Compliant unit B:** a strict composition reviewer permits exactly the two named native elements and rejects `<track>` as a non-Ant component, so captions are omitted despite an available VTT. Both can defend literal AD-16 readings.

**Action:** **autofix.** Define the exception as the semantic native media subtree (`video|audio` plus required `source`/`track` and accessibility attributes), not only two tags; it still grants no custom CSS or styled control library. Keep the existing pause-and-record-a-design-decision rule for any visual requirement not expressible through Ant props/composition/tokens, and make the frontend composition root the sole owner of approving/recording such an exception.

## Low

### ADV-U9 — LOW — Empty stored task numbers are not canonicalized with empty query handling

**Spine:** AD-9 rejects an empty normalized query and indexes every non-null `taskNumberNorm`, but does not say whether a display value normalizing to empty is rejected or converted to null.

**Compliant unit A:** the write path stores `taskNumber="   "`, `taskNumberNorm=""`, producing an indexed value no valid query can retrieve.

**Compliant unit B:** URL extraction/manual editing maps the same input to null and removes it from the partial index.

**Action:** **autofix.** State that normalization-to-empty is canonical null/removal (or a validation error, choose one) on every write/import/repair path; never persist/index an empty normalized value.

## Stress tests that held

- Direct audio and video now share one streaming, crash-consistent intake path, while original bytes remain a distinct immutable `source`; this closes the earlier video-only divergence.
- Summary and generated tags have one atomic publication owner, and failed/cancelled summarization does not mutate tags; the remaining issue is optimistic concurrency, not crash atomicity.
- `taskNumber` is correctly separated from FTS5 and has an explicit partial B-tree plus no-fuzzy/no-semantic fallback.
- Ant Design 6, one `ConfigProvider`/`App` composition root, centralized locale/theme tokens and the no-custom-CSS rule strongly prevent parallel component systems. Apart from the native media-subtree wording, the no-CSS policy itself is convergent because an unmet requirement must stop for a recorded design decision.

## Gate close conditions

1. Decide browser-playable representation ownership and bind it to import, artifact deletion and the cross-browser corpus gate.
2. Make `preparedAudio` a versioned, fingerprinted, retained stage artifact with a single recovery/cleanup rule.
3. Fence source/full deletion against new jobs, provider/media readers and cross-OS unlink behavior; retain an aggregate tombstone through partial cleanup.
4. Centralize and version `taskNumber` normalization/prefix interval logic; define per-hit match metadata and deterministic pagination.
5. Add Transcript/Summary/tag-set optimistic preconditions to atomic Summary+autoTag publication and unify tag identity across origins.
6. Expand the native Ant Design exception to the required semantic media subtree.

## Recheck — updated spine

**Final verdict: CHANGES REQUIRED — Critical 0 / High 3.** The update closes the original browser-representation, prepared-audio contract, canonical-prefix, and stale-Summary publication findings. Deletion is materially stronger but not fully closed. Two new seams introduced by the fixes — globally ambiguous derived identity and an unfenced provider commit handshake — still allow incompatible implementations.

### Previous High findings

| Finding | Recheck | Evidence in updated spine |
| --- | --- | --- |
| ADV-U1 — browser-playable representation | **Closed** | AD-13 selects source only through a Chromium+Firefox codec allowlist and otherwise publishes WebM/Opus or WebM/VP9+Opus; AD-11 exposes only `playbackArtifactId`; AD-14 exercises every supported corpus source in both browsers. |
| ADV-U2 — `preparedAudio` contract/lifecycle | **Closed, subject to RH-1** | AD-13 fixes WAV/PCM s16le/mono/16 kHz, profile `asr-audio-v1`, deterministic tuple identity and engine ownership; AD-2 retains published derivatives until explicit deletion. The remaining issue is cross-Meeting identity scope, not format or TTL. |
| ADV-U3 — delete versus jobs/readers/provider | **Partially closed; RH-2 remains High** | `lifecycleEpoch`, `DeleteIntent`, no-active-job precondition, new-lease/grant prohibition, cancellation/revocation and lease wait close most of the race. Media-only completion and long response lease semantics are still ambiguous. |
| ADV-U4 — canonical task prefix | **Closed** | AD-9 indexes normalized UTF-8 as BLOB and fixes `upper=p+0xFF`; no valid UTF-8 byte is `0xFF`, so every valid extension is inside `[p,pFF)`. Backend-only normalization also prevents client drift. |
| ADV-U5 — late summarization | **Closed** | AD-3 requires completion CAS against lifecycle/input plus current Transcript, Summary and Tag-set revisions, and supersedes without publication on mismatch. Summary+autoTags remain one transaction. |

### RH-1 — HIGH — Derived identity is not scoped to its owning Meeting

**Spine:** AD-2 says a Meeting owns artifact slots; the ER seed says `MEETING ||--o{ MEDIA_ARTIFACT`. AD-13 defines derived identity only as `SHA-256(sourceChecksum, role, profileVersion)` and says a unique constraint excludes duplicates.

**Compliant unit A:** the artifact repository treats that digest as globally unique. Two Meetings importing identical source bytes collide, so the second reuses the first Meeting's `MediaArtifact` row/file or cannot publish its own slot. Media/full deletion of either Meeting can then remove a derivative still referenced by the other.

**Compliant unit B:** the meetings repository interprets ownership literally and scopes uniqueness to `(meetingId, derivedIdentity)`, storing one derivative per Meeting. Its schema conflicts with A's global uniqueness and with any globally content-addressed filesystem adapter.

**Why it remains High:** the spine deliberately chooses Meeting ownership and delete cascades, but the new tuple accidentally admits shared storage without reference counting. This can break the other Meeting after an otherwise valid deletion.

**Required correction:** choose one model. For the current ownership/deletion rules, include `meetingId` in the canonical tuple and make uniqueness explicit as `(meetingId, sourceChecksum, role, profileVersion)`; CAS the corresponding slot in the successful prepare transaction. The alternative — global content-addressed blobs — requires a separate blob entity, persisted reference counts and delete-after-last-reference semantics, which is unnecessary for MVP.

### RH-2 — HIGH — `DeleteIntent` does not distinguish media-only completion, and a bounded read lease can expire before a streaming response closes

**Spine:** `Meeting.lifecycleState` has only `active|deleting`; media-only and full delete both bump the epoch, hide the Meeting, wait bounded leases, delete files and “лишь затем очищает authoritative rows/indexes”. AD-11 also allows an unbounded-in-size `GET` without Range for sources up to 5 GB.

**Compliant unit A:** a media-only delete follows the shared terminal wording, clears Meeting rows/indexes after files, or leaves the Meeting in `deleting` because no return transition is defined. It treats the same terminal behavior as full delete.

**Compliant unit B:** the route acquires a fixed-TTL artifact read lease, opens the file and streams until the client closes. If the 5-GB response outlives that bounded lease, deletion proceeds after expiry: Unix keeps serving the unlinked inode while Windows can fail the unlink. Another route implementation heartbeats the lease and can make delete wait indefinitely. Both obey “bounded artifact read lease”.

**Why it remains High:** source-only deletion can still either erase preserved text/index state or produce cross-OS partial deletion, exactly what FR-4/NFR-4 prohibit.

**Required correction:** persist `DeleteIntent.kind=mediaOnly|full` and its exact target set. `mediaOnly` completion nulls media slots, preserves Meeting/Transcript/Summary/tags/FTS, records unavailable playback, advances the epoch and returns the Meeting to `active`; `full` alone removes authoritative rows/indexes after file cleanup and retains a tombstone on partial failure. A media GET must acquire `(artifactId,lifecycleEpoch)` under the same readiness check, heartbeat until response close, and release in `finally`; after bounded drain expiry the server aborts remaining responses before unlink rather than treating expired TTL as proof that no handle exists.

### RH-3 — HIGH — Provider `commit` is not bound to current epochs or to the worker that ACKed

**Spine:** AD-5 adds a `prepared → inFlight` ledger and ACK/commit split. The envelope carries attempt/lease/lifecycle epochs, but no transition explicitly CASes them against a currently running attempt/active Meeting, and no ACK token binds commit to the same stateless worker. AD-2 revokes attempts/grants on delete; AD-3 prevents stale result publication only after the external call.

**Compliant unit A:** a worker ACKs and redeems the single-use grant while preparing its client. The app persists `inFlight`; then cancel/delete bumps `lifecycleEpoch` and revokes the attempt. A delayed commit still reaches that worker, whose already-redeemed secret allows provider egress. AD-3 rejects the eventual result, but privacy/cost was already incurred.

**Compliant unit B:** the app or load balancer routes a retried commit to another stateless worker. It interprets `dispatchId` as sufficient authorization, while the first worker interprets its ACK as reservation. The call can be lost, rejected inconsistently, or duplicated if both accept the commit.

**Why it remains High:** the handshake protects an ambiguous outcome from automatic replay, but it does not yet prove that the one provider call was authorized by the current Meeting/attempt at the instant of egress.

**Required correction:** ACK returns a single-use `commitNonce` bound to `(dispatchId, workerInstance/session, attemptId, leaseEpoch, lifecycleEpoch)`. The app transaction moving `prepared → inFlight` must CAS those epochs plus `Meeting=active` and `Attempt=running`; the signed/opaque commit carries that nonce. Only the ACKing worker may consume it, and it redeems the secret grant **after** commit validation immediately before egress. Cancel/delete/revoke invalidates an unconsumed nonce; result persistence and stage completion repeat the epoch CAS. Loss after nonce consumption remains `outcomeUnknown` and is never auto-replayed.

### Additional non-High observations

- **Derived timeline:** AD-13 fixes encodings but not the shared media clock. `preparedAudio` and transcoded playback can independently reset start PTS or add encoder delay, shifting evidence seeks. Bind both profiles to a zero-based Meeting timeline and a tested drift tolerance, or persist an explicit time mapping. AD-14's evidence fixture should verify alignment, not merely that seeking is possible.
- **Conditional ranges:** the strong ETag is useful, but `If-Range` behavior is not named when a playback slot changes after re-prepare/profile migration. Define matching ETag → `206`, stale/nonmatching validator → full `200`, and keep the read lease for the selected immutable representation.
- **AutoTags:** late publication is now fenced. ADV-U7 remains Medium: manual and automatic tags still lack one `tagNorm`/collision precedence and a stated requirement that every manual/auto mutation increments the Tag-set revision checked by AD-3.
- **Task-number response:** ADV-U6 remains Medium: `(task_number_norm,id)` ordering is fixed, but page-level versus per-hit `matchKind` semantics and cursor/offset behavior are still not in AD-11.
- **Ant Design:** ADV-U8 remains Medium: the feasibility spike is a sound no-CSS gate, but the sole native exception still names only `<video>`/`<audio>`, not the required semantic `<track>` child.

## Final recheck — three High corrections

**FINAL VERDICT: PASS — Critical 0 / High 0.** The three remaining High seams are closed without weakening the earlier fixes.

- **RH-1 closed — Meeting-scoped derivatives.** AD-13 now includes both `meetingId` and `sourceArtifactId` in the canonical derivative tuple and makes uniqueness explicitly Meeting-scoped. AD-2 assigns every `MediaArtifact` to exactly one Meeting, so identical recordings in separate Meetings neither collide nor share a file that one Meeting can delete from under the other.
- **RH-2 closed — scope-specific deletion and live read fencing.** AD-2 distinguishes `mediaDeleting` from full `deleting`, persists `DeleteIntent(scope=media|meeting)`, and gives each scope a different final transaction. Media-only cleanup nulls only media slots/artifact rows and returns the Meeting to `active` with text/metadata preserved; full cleanup alone removes dependent rows/FTS/tombstone. Streams and workers hold persisted `(artifactId, ownerId, lifecycleEpoch, expiresAt)` leases, heartbeat them, recheck epoch before each chunk, and cannot renew after the intent closes app streams. Unlink occurs only after release/expiry, eliminating the previous fixed-TTL/open-handle divergence across operating systems.
- **RH-3 closed — provider egress authorization.** AD-5 binds the authenticated worker-session nonce to the complete envelope, CASes `Attempt=running` plus current lease/lifecycle epochs before `inFlight`, and issues a single-use commit token only over that same authenticated RPC session. Only the ACK-ing worker with the matching nonce/token may perform the one provider call; restart loses the right. AD-2's intent prohibition/revocation and the epoch CAS prevent a stale or different worker from obtaining new authorization, while any post-commit ambiguous outcome remains non-replayable under the existing ledger rule.

The additional Medium/Low observations recorded above remain non-blocking follow-ups; no Critical or High adversarial compatibility finding remains in this update scope.
