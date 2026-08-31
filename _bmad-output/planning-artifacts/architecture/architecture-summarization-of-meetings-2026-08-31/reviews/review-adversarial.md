# Final Reviewer Gate — adversarial compatibility lens

**Artifact:** `ARCHITECTURE-SPINE.md` (final candidate, read-only review)  
**Inputs:** final PRD and `addendum.md`  
**Method:** for each boundary, construct two independently-built units that both satisfy the literal spine but disagree at integration. Findings are included only where the disagreement can cause failed integration, lost/corrupt state, privacy/reproducibility drift, or violation of a bound requirement.

## Verdict

**CHANGES REQUIRED.** The paradigm and major boundaries converge well, but eight real compatibility gaps remain: **2 Critical, 5 High, 1 Medium**. The blockers are the DB/filesystem publication protocol and missing fencing for leased stage completion. Both can violate NFR-4 despite every participating unit following the current words.

## Findings

### ADV-1 — CRITICAL — DB and filesystem cannot satisfy the stated atomic publication without an ordered recovery protocol

**Spine:** AD-2 says a file is published by atomic rename; AD-13 says one transaction creates `Meeting`/`MediaArtifact` and rename publishes the file. Neither fixes ordering or crash recovery across SQLite and the filesystem.

**Compliant implementation A:** the intake command commits SQLite first, then asks the filesystem adapter to rename staging to final. It interprets “one transaction creates Meeting/MediaArtifact” literally. A crash or `EXDEV` leaves an authoritative row pointing to a missing file.

**Compliant implementation B:** the filesystem adapter renames first, then the repository commits SQLite so no visible row can point at staging. A DB failure or crash leaves an unreferenced final file. If its staging directory is container `/tmp`, rename to a mounted data volume is not atomic and may fail cross-device.

Both follow AD-2/AD-13 locally; their cleanup/recovery assumptions are opposite. The same ambiguity applies to prepared-audio stage outputs.

**Smallest fix:** add one convention: all file-backed mutations use a single canonical publication saga; staging is inside the managed root on the same filesystem as final; DB records an explicit `pending` artifact before publication; rename is idempotent; a final DB compare-and-set marks `ready`; only `ready` artifacts are visible; startup/maintenance reconciliation deterministically completes or removes every `pending`/orphaned artifact. Deletion uses the inverse journaled saga. State that “output + checkpoint atomically” means the final DB transition, after file publication has reached a recoverable state.

### ADV-2 — CRITICAL — Lease expiry does not fence a stale worker from publishing

**Spine:** AD-3 gives `StageAttempt` a lease and heartbeat, but its commit rule has no lease generation/fencing precondition.

**Compliant implementation A:** worker A checks that it owns the lease when it starts a long provider request. Its heartbeat is delayed; the lease expires, but A accepts the eventual response and commits because the attempt ID still matches.

**Compliant implementation B:** the scheduler treats the expired lease as abandoned, assigns the stage to worker B, and B commits a newer result. Depending on ordering, A can overwrite B, publish a transcript for an older input fingerprint, or trigger summary twice. Each implementation honored lease acquisition and heartbeat as written.

**Smallest fix:** every acquisition increments a persisted monotonic `leaseEpoch` (fencing token). Heartbeat, checkpoint, artifact/domain publication and transition to terminal state must compare-and-set `(attemptId, leaseEpoch, state=running)` in the same SQLite unit of work; stale writes are rejected. Provider dispatch carries a stable `dispatchId` plus epoch, and app↔provider RPC is idempotent for that dispatch. Explicitly designate one owner of automatic provider retries and disable nested SDK retries so the global “no more than two” rule cannot multiply across layers.

### ADV-3 — HIGH — “Stage output” is ambiguous across `processing`, domain publication and FTS

**Spine:** AD-3 says output/checkpoint commit atomically; AD-1 requires module calls through application commands; Mutation gives one transaction per command or checkpoint; AD-9 indexes domain output in its publication transaction.

**Compliant implementation A:** `processing` atomically saves a normalized engine payload and marks `transcribe` succeeded, then invokes a public `meetings.publish_transcript` command in a second transaction. The scheduler may start `summarize` between them.

**Compliant implementation B:** an application service opens one SQLite unit of work, publishes authoritative `Transcript`/`Summary`, updates FTS and marks the attempt succeeded together. B assumes downstream may start immediately after success. Integrating A's producer with B's scheduler yields a succeeded stage without authoritative input.

**Smallest fix:** define successful-stage commit scope: `prepare` publishes a `ready` audio artifact via the AD-2 saga; `transcribe` commits current Transcript/Segments + FTS rows + attempt success; `summarize` commits current Summary/items/evidence + FTS rows + attempt success. All structured writes share one application-owned SQLite unit of work; a stage is not externally `succeeded` before that unit commits. Module public APIs participate in that caller-owned UoW and never start an independent transaction for this path.

### ADV-4 — HIGH — Provider RPC, authentication and secret redemption have no canonical wire contract

**Spine:** AD-4 defines typed engine ports; AD-5 says authenticated internal RPC with an immutable envelope; AD-6 says a single-use grant resolves `secretRef` and that the key reaches `provider-worker` over authenticated RPC. AD-11's OpenAPI source of truth is explicitly the external/UI API, not this internal process boundary.

**Compliant implementation A:** `app` redeems the grant, pushes the raw key inside a camelCase JSON dispatch request, and treats the grant as audit metadata.

**Compliant implementation B:** `provider-worker` expects a snake_case/protobuf envelope, then calls the broker with the opaque grant to redeem the key. It also chooses a different authentication scheme. Both implement “authenticated RPC” and a typed port, but cannot communicate. Under a lost response, one may repeat the provider call while the other assumes `dispatchId`-level deduplication.

**Smallest fix:** name a versioned, generated internal RPC contract as the only wire source of truth, including serialization, framing/streaming, authentication scheme and compatibility policy. Choose exactly one secret flow. A coherent minimal choice is: the dispatch carries the opaque attempt grant; an authenticated `provider-worker` redeems it once through the broker RPC; the key exists only in worker memory for that leased attempt. Require `dispatchId`, `attemptId`, `leaseEpoch`, stage, input fingerprint, profile-snapshot digest, consent proof and typed result/error echoes. State retry/deduplication behavior in this contract.

### ADV-5 — HIGH — Backup consistency and restore replacement are not crash-defined

**Spine:** AD-10 combines “maintenance mode”, SQLite online snapshot, copied media, a manifest, and replacement after validation. It does not define whether maintenance mode is quiescent or how DB and media are switched as one recoverable generation.

**Compliant implementation A:** the UI enters read-only mode, but existing workers continue. It snapshots SQLite and then copies the media referenced by that snapshot while a worker publishes or deletes files.

**Compliant implementation B:** the maintenance CLI stops leasing, waits for workers, copies media first and snapshots SQLite last. The two backups can contain different DB/media sets. During restore A replaces DB then media; B replaces media then DB. A crash between replacements produces a mixed generation in either order.

**Smallest fix:** define an exclusive persisted maintenance lock: reject mutations, stop new leases, drain/cancel active attempts, then snapshot. The manifest is derived from that DB snapshot and only those checksum-addressed artifacts are copied. Restore while all services are stopped into a new validated generation; activation is a single recoverable generation switch, or a persisted restore journal guarantees resume/rollback after every interruption. Migration cannot begin until the pre-upgrade generation is complete and verified.

### ADV-6 — HIGH — Persistent `llama-server` topology conflicts with sequential model residency

**Spine:** AD-5 makes `llama-server` a Compose service; AD-12 requires ASR and LLM to load sequentially so the 16-GB baseline is not exceeded. No component owns model load/unload or proves memory release.

**Compliant implementation A:** deployment starts `llama-server` with Qwen loaded and healthy for the life of Compose. `local-worker` independently loads Whisper for `transcribe`.

**Compliant implementation B:** the local scheduler assumes exclusive model residency and starts ASR because no LLM stage is active. Both satisfy their own rules, yet together hold both models and can fail the 16-GB gate or block the UI.

**Smallest fix:** make `local-worker` (or one named `LocalResourceCoordinator`) the sole owner of a persisted exclusive compute/model-residency lease. `llama-server` must be on-demand or support an explicit load/unload protocol; ASR may start only after LLM unload acknowledgement and observed process exit/released budget, and vice versa. The Compose health check must not require the LLM model to be resident. Cross-OS AD-14 gates exercise these transitions, not merely one stage at a time.

### ADV-7 — HIGH — The immutable job snapshot omits result-affecting profile inputs and resolved engine identity

**Spine:** AD-4 lists engine kind, endpoint, model ID, capability snapshot and optional `secretRef`, then says the job snapshots both stage configurations. The PRD also makes language, summary language/rules and additional instructions part of the saved Profile. AD-12 pins local revisions only in a release manifest.

**Compliant implementation A:** the job producer snapshots only the fields enumerated in AD-4; the summarize worker reads the current profile instructions and resolves a model alias from the current release manifest at dispatch.

**Compliant implementation B:** the worker expects language/instructions/model revision to have been frozen at job creation. Editing a profile or updating model files while a job is queued then changes A's output but not B's, and provenance cannot say which inputs actually produced the Summary.

**Smallest fix:** define one `JobExecutionSnapshot` contract containing both resolved stage configs plus transcription language, summary output language, instructions/template revision, decoding/model parameters, capability manifest version, adapter version and resolved local model revision/checksum (for external engines: requested model ID + endpoint identity, and response model when supplied). The worker consumes only this snapshot; Summary provenance stores its ID/digest. `secretRef` remains a stable non-secret handle and the secret value is deliberately excluded.

### ADV-8 — MEDIUM — SSE resume identifiers have no scope, durability or gap semantics

**Spine:** Events require a monotonic ID and reconnection by `Last-Event-ID`; server state is authoritative. It does not say whether IDs are global, per job or per connection, nor what happens after restart or retention loss.

**Compliant implementation A:** backend emits an in-memory counter starting at 1 for every SSE connection. The frontend treats IDs as a durable per-job cursor and drops “old” IDs after reconnect.

**Compliant implementation B:** backend uses a global persisted sequence while the frontend assumes each job starts at 1. Both satisfy “monotonic” within their chosen scope; integration loses or duplicates progress and terminal events.

**Smallest fix:** define SSE as replaceable state snapshots keyed by a persisted per-job revision. Endpoint scope is one job; every observable persisted state/progress update increments the revision and uses it as event ID. Reconnect emits later retained snapshots, or one current `resync` snapshot when a cursor is absent/pruned; clients ignore revisions not greater than the last applied value. Terminal state remains queryable through REST.

## Boundary coverage

| Boundary tested | Result |
| --- | --- |
| Module APIs | **Gap:** caller-owned UoW and successful-stage publication scope are not explicit (ADV-3). |
| Profile snapshots | **Gap:** immutable snapshot is incomplete for result-affecting inputs and resolved versions (ADV-7). |
| Provider dispatch | **Gap:** no canonical wire/auth/idempotency contract (ADV-4); stale dispatch is not fenced (ADV-2). |
| Secret grants | **Gap:** push-vs-redeem flow and retry behavior permit incompatible implementations (ADV-4). The no-persistence locations themselves are clear. |
| Job transactions | **Gap:** no fencing CAS and ambiguous authoritative output boundary (ADV-2, ADV-3). |
| Artifact publication | **Blocker:** no cross-resource publication/reconciliation saga (ADV-1). |
| Event contracts | **Gap:** resume cursor scope/durability unspecified (ADV-8). |
| FTS/search | **No architecture compatibility finding:** one SQLite FTS5 authority, same-transaction updates, bounded pagination and deterministic rebuild are sufficient at this altitude; tokenizer/schema/query syntax can remain owned together by `search_export` and migrations. |
| Backup/restore | **Gap:** no quiescence or generation-switch semantics (ADV-5). |
| Cross-OS deployment | **Gap:** same-filesystem staging and model lifecycle are not guaranteed (ADV-1, ADV-6). AD-14 otherwise provides the required platform/release convergence gate. |

## Gate recommendation

Do not finalize before ADV-1 and ADV-2 are fixed. ADV-3 through ADV-7 are build-substrate decisions: leaving them open permits independently built modules/processes to compile yet disagree at runtime, so they should also be fixed in the spine rather than deferred to code. ADV-8 is a small convention fix. No new structural diagram, service or broad schema is required beyond the resource coordinator named by ADV-6; each fix can be expressed as one sentence appended to the relevant AD/convention.

## Recheck

**Verdict: PASS — remaining Critical: 0; High: 0. No new blocker introduced.**

- **Artifact saga — closed:** AD-2 fixes same-filesystem staging, persisted `pending`, idempotent rename, CAS to `ready`, read visibility and startup reconciliation; AD-3 requires file output `ready` before stage success.
- **Fencing, dispatch and atomic success — closed:** AD-3 fixes monotonic `leaseEpoch`, CAS for every write and a single authoritative-output/FTS/success transaction; AD-5 and retry convention fix at-most-once `dispatchId` behavior and ambiguous outcomes.
- **Provider wire and secrets — closed:** AD-5 names one versioned generated TLS/workload-auth streaming contract with the required correlation, snapshot, consent and opaque-grant fields; AD-6 fixes single-use runtime-only grant resolution and forbidden persistence paths.
- **Backup/restore generations — closed:** AD-10 fixes exclusive maintenance quiescence, exact snapshot-derived artifact manifest, completed temporary generation and recoverable atomic activation/rollback.
- **Model lifecycle — closed:** AD-12 names `LocalResourceCoordinator` as exclusive residency owner and fixes ASR unload/memory acknowledgement before on-demand `llama-server` startup and teardown.
- **Immutable job snapshot — closed:** AD-4 now freezes all result-affecting stage config, language/instructions, adapter/capability and resolved model identity; AD-7 stores the snapshot digest in Summary provenance.
- **SSE resume — closed:** AD-11 fixes persisted per-job revisions, replaceable snapshots, stale suppression, gap/pruning `resync` and REST terminal-state recovery.
