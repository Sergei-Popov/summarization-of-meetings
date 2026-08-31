# Reconciliation: Architecture Spine ↔ PRD

**Verdict:** **NEEDS CORRECTION** — the spine carries the main product shape and most durable invariants, but five architecture-relevant PRD commitments are either not enforced by a rule or are left ambiguous enough for independent units to implement incompatibly. No direct rejection of the product vision was found.

**Compared:**

- `ARCHITECTURE-SPINE.md` (draft, 2026-08-31)
- `prd.md` (final, 2026-08-31)

## Findings

### R-1 — Critical: provider egress has broad data reach and no enforceable data-minimization/consent contract

**PRD commitment:** FR-7 requires the user to see the mode, provider, and transmitted data type before processing and to confirm the first use of every external profile. The privacy rules require that provider mode transmit only data necessary for the selected stage; FR-9 specifically says video must not be sent when audio is sufficient. No request may run without an explicitly selected profile.

**Spine state:** AD-4 prevents automatic engine fallback and records an engine/capability snapshot. AD-5 gives only `provider-worker` processing egress, but the topology also gives that worker direct access to `DATA` (`provider-worker --> DATA`). Neither AD-4 nor AD-5 limits the worker to a stage-specific payload, records the required first-use consent, or prevents a provider adapter from reading unrelated meeting artifacts. The browser is also outside the container egress boundary, while the spine has no prohibition on remote frontend assets, telemetry, or browser-side outbound calls.

**Divergence risk:** one provider adapter can upload prepared audio, another the source video, and another the full meeting record; a frontend path can initiate network traffic that AD-5 does not control. All can still appear compliant with the current spine.

**Required correction direction:** strengthen the privacy/egress invariant so the provider worker receives an immutable, stage-scoped payload through a narrow port and has no general meeting-volume or unrestricted database access. Define outbound payload allowlists (`transcribe`: prepared audio + language/model; `summarize`: current transcript segments + instructions/model), require a persisted profile/engine snapshot plus consent proof before dispatch, and deny frontend external connections/remote assets by policy. Keep provider responses and diagnostics under the existing no-content logging rule.

### R-2 — High: NFR-2/NFR-3 timing budgets are named as bound but not encoded in the interaction rules

**PRD commitment:** at up to 1,000 meetings, library/navigation must complete within 2 seconds; navigation, saving, and cancel requests during local inference must respond within 1 second at p95; cancellation must reach a safe stop within 10 seconds; progress/activity must update at least every 5 seconds. Import/audio preparation must stream rather than load the whole file.

**Spine state:** AD-3 merely says cancellation is checked at safe points and workers heartbeat. The SSE convention gives event fields but no maximum publication interval. AD-12 serializes compute-heavy work, but sets no responsiveness or memory/backpressure contract. AD-3, AD-11, and AD-12 nevertheless claim to bind NFR-2/NFR-3.

**Divergence risk:** adapters can choose chunk sizes or blocking calls that postpone cancellation well past 10 seconds, workers can emit heartbeats too slowly for the 5-second activity promise, and API/UI work can share resources in a way that fails the p95 responsiveness target.

**Required correction direction:** add an operational invariant that carries the PRD budgets into worker and API contracts: bounded streaming/chunking for media, cooperative cancellation checkpoints no farther than the 10-second budget, persisted heartbeat/activity at no more than 5-second intervals, and isolation/backpressure that reserves API responsiveness during model work. Put the 1,000-meeting/2-second and p95/1-second checks in the release verification gate rather than treating them as implicit effects of the topology.

### R-3 — High: the pre-job media acceptance gate required by FR-1 and SM-2 has no owner or atomic boundary

**PRD commitment:** MP4/MOV/MKV/WebM inputs up to 3 hours or 5 GB must be probed for availability, container validity, and an audio track before a processing job starts. Unsupported and corrupt inputs must be rejected with a reason and must not create a hidden or stuck job. SM-2 makes correct rejection of two bad files a release condition.

**Spine state:** the FR-1–4 map points import to `meetings`, the filesystem adapter, AD-2, and AD-10. Those decisions define storage ownership, deletion, migration, and backup, but none defines a media-probe port, the validation-before-job ordering, or the atomic outcome when managed-file ingestion succeeds and validation/job creation fails. FFmpeg appears only in the stack.

**Divergence risk:** UI, API, media adapter, and processing module can each validate a different subset or create the job at different times; an invalid upload can leave an orphan artifact or a recoverable-looking job that can never start.

**Required correction direction:** define one application-level intake command and media-probe result as the authority for FR-1. It should stream/copy into staging, probe the PRD limits and audio presence, publish the managed artifact and create the meeting/job only under an explicit atomic/compensating boundary, and return a typed rejection without a job on validation failure. Add bad-input corpus cases to the same release gate used by AD-12.

### R-4 — Medium: the search invariant omits meeting-title search required by FR-3

**PRD commitment:** the library must search by meeting title and transcript content; FR-19 additionally requires search over transcripts and summaries.

**Spine state:** AD-9 indexes only current `Segment` and `Summary` content. It does not put meeting titles in FTS or state that title results are merged through the same search query. The capability map nevertheless assigns FR-3 to AD-9.

**Divergence risk:** a compliant-looking `search_export` implementation can satisfy AD-9 and FR-19 yet fail the FR-3 library search path, or frontend and backend can implement incompatible title matching/ranking.

**Required correction direction:** include normalized current meeting titles in the authoritative local search projection, or explicitly require the search query port to merge deterministic title matches with FTS hits. Keep the existing hit contract (meeting, match type, snippet/context).

### R-5 — Medium: retry checkpoints can accidentally create a full summary/version history forbidden by FR-18

**PRD commitment:** MVP retains only the current summary and metadata for the latest run, not full version history. Before replacing a manually edited summary, the user must confirm.

**Spine state:** the ER seed correctly gives a meeting at most one `SUMMARY`, but AD-3 keeps multiple `StageAttempt` records and says their output/checkpoint is committed atomically. It does not state whether old attempt payloads are purged after publication. AD-7 records `manualEdit`, yet no mutation precondition protects a manually edited summary from replacement.

**Divergence risk:** one implementation can preserve every generated summary inside attempt outputs, effectively violating the retention boundary, while another deletes all retry evidence. A background retry can replace a manual edit without an application-level confirmation token/precondition.

**Required correction direction:** define the lifecycle boundary: historical attempts retain operational metadata and fingerprints only; full transcript/summary payloads are removed after current-result publication or failed-attempt cleanup. Make summary replacement conditional on the current revision/manual-edit marker plus explicit user confirmation, with stale-write rejection.

## Coverage that did land

- The local-first, single-owner, loopback deployment shape is represented by AD-2 and AD-5.
- Durable staged execution, stage-specific retry, atomic publication, and no automatic engine fallback are represented by AD-3 and AD-4.
- Runtime-only secrets and log/export exclusion are represented by AD-6 and the logging/data conventions.
- Transcript revisioning, summary staleness, evidence identity, and persistent `unverified` status are represented by AD-7 and AD-8.
- Current-result local search, local export metadata, backups/restores, CPU/16-GB baseline, model version pinning, and corpus-gated model promotion are represented by AD-9, AD-10, AD-12, and conventions.
- The PRD's out-of-scope boundaries (remote exposure/authentication, multi-user ownership, native packages, semantic search, plugin catalog) are explicitly deferred.

## Deliberately not raised as architecture defects

NFR-6 keyboard/accessibility behavior, NFR-9 Apache-2.0 licensing, NFR-10 single-screen UX, detailed export formatting, unsaved-edit undo, and the exact summary section labels remain binding PRD requirements, but they do not require another cross-unit architectural choice at this altitude. They should be preserved in UX/specification, implementation acceptance criteria, and release checks. SM-1 is a post-release product outcome rather than an architecture invariant.

