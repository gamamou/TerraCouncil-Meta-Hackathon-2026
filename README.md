# TerraCouncil AI — Meta Global AI Developer Hackathon 2026

**Track:** Startups  
**Theme:** Build for Your World  
**Project:** SustainAfrica / FAITH / FSDC  
**Official build period (per participant guide):** October 27 – November 4, 2026  
**Submission deadline:** November 4, 2026 at 9:00 PM Eastern Time

## Vision

**A Meta-powered multi-stakeholder decision intelligence council for the FAITH/FSDC ecosystem.**

TerraCouncil is designed as a cross-sector decision council connecting perspectives in mining, agriculture, energy, environment, Simandou, critical minerals and digital twins. Its first hackathon pilot is mining in Boké, Guinea. Agents simulate stakeholder *perspectives*, not actual organizational endorsements.

This is a **dedicated public hackathon repository**. It is separate from SustainAfrica's existing FAITH/FSDC systems.

## Clear contribution boundary

### Existing foundation — before the hackathon (not new competition work)

- FAITH/FSDC scientific datasets, geospatial pipelines, indicators, methodology, provenance and QA.
- Early exploratory TerraCouncil architecture and prototypes in development.
- Feasibility **tests** of Meta Muse Spark and Muse Wonder. These were not a completed, deployed integrated scientific council.
- Early French audio-dialogue and visual interface prototypes, including ElevenLabs output.

### Hackathon build — progress recorded by commit

- **HACK-001 (registry implementation committed Oct 27):** A sector/agent registry, local validator and preliminary Boké scenario definition. This is **not** yet a live scientific council or integrated FSDC retrieval.
- **HACK-002 (prototype code committed Oct 27):** Evidence-gated Spark/Wonder API orchestration with direct HTTP client, independent critique and revision. No real Meta call, live FSDC connection, or scientific accuracy validation has yet been demonstrated.
- **HACK-003 (verification prototype committed Oct 27):** Independent pre/post evidence checks, exact finding/citation matching, exploratory-only Boké tier and fail-closed Spark/Wonder pipeline. Code and synthetic tests are committed; real FSDC ingestion, scientific validation and live model runs remain pending.
- **HACK-004 (in progress):** Implement an integrated multimedia council experience and evaluate Muse Image for illustrative visual output; transparently reuse existing ElevenLabs audio where helpful.

Beyond the HACK-001 registry, these are **planned contributions, not completed features**. Only code and capabilities actually built during the event will be described as hackathon-built.

SAM 3.1 and speech transcription are not core dependencies unless a demonstrable use case justifies them.

## Science and publication policy

Evidence must retain provenance, dates, versions, licence, geographic limits, methods and validation status. The preliminary Boké case is **NOT_FIELD_VALIDATED**. AI-generated imagery is illustrative, never scientific evidence. Missing evidence is grounds for an abstention, not a fabricated conclusion.

No API credentials, private data, restricted-source datasets, proprietary FAITH/FSDC components, or unlicensed assets should be committed.

## Documentation

- [Pre-hackathon foundation](docs/PRE_HACKATHON_FOUNDATION.md)
- [Contribution register](docs/HACKATHON_CONTRIBUTIONS.md)
- [Scientific evidence policy](docs/SCIENTIFIC_EVIDENCE_POLICY.md)
- [Roadmap](docs/ROADMAP.md)
- [HACK-001 registry architecture](docs/HACK-001-ARCHITECTURE.md)
- [HACK-002 runtime and local test instructions](docs/HACK-002-RUNTIME.md)
- [HACK-003 independent scientific verification](docs/HACK-003-INDEPENDENT-VERIFICATION.md)
- [HACK-004 real Boké screened-data bridge](docs/HACK-004-REAL-BOKE-DATA.md)
- [HACK-005 one-call Meta Spark live pilot](docs/HACK-005-LIVE-PILOT.md)
- [HACK-006 verified Wonder critique / Spark revision](docs/HACK-006-CONTINUE-DEBATE.md)
- [HACK-007 Interactive Scientific Council](docs/HACK-007-INTERACTIVE-COUNCIL.md)
- [HACK-008 Local interactive Meta Council](docs/HACK-008-INTERACTIVE-LOCAL-COUNCIL.md)
- [HACK-009 Chamber, source visualization, audio and scientific PDF](docs/HACK-009-CHAMBER-PDF-AUDIO.md)
- [HACK-010 Executive PDF & natural French audio](docs/HACK-010-EXECUTIVE-PDF-NATURAL-VOICE.md)
- [HACK-011 Reviewed oral narration & synchronized chamber](docs/HACK-011-AUDIO-REVIEW-CHAMBER.md)
- [HACK-012 visibly redesigned Executive Brief V3](docs/HACK-012-EXECUTIVE-V3.md)
- [HACK-013 Immersive scientific chamber](docs/HACK-013-IMMERSIVE-CHAMBER.md)
- [HACK-014 French Oral Studio and source-bound review](docs/HACK-014-ORAL-STUDIO.md)
- [HACK-015 approved one-click ElevenLabs dialogue](docs/HACK-015-ONE-CLICK-AUDIO.md)

## Submission transparency

Our submission will explicitly call out prior foundations and focus the three-minute demo on the functions implemented within the hackathon window, evidenced by dated commits, model execution records and tests.

**As of October 27, 2026:** HACK-001 registry, HACK-002 runtime, HACK-003 independent verification, and HACK-004 source-aware Boké screening adapter have been committed; no live Meta council execution, production FSDC integration or field-validated result is claimed. Development uses Python, VS Code, GitHub and direct Meta Model API (later milestones), **not Muse Code**.

## Licensing

No public code license has yet been selected. All rights reserved pending an explicit licensing decision. FAITH/FSDC assets are **not automatically licensed for redistribution**.

## HACK-004 data integration status

The new `src/import_boke_010hi.py` bridges pre-existing TerraCouncil 010HI/010HJ scientific screening into locally generated, **not field validated**, source-derived evidence records with strict hash consistency checks. Source inputs are not published in this repository. The code and isolated tests are committed; an actual model run with the local Boké input has **not** yet been completed or validated. See [HACK-004](docs/HACK-004-REAL-BOKE-DATA.md).

## HACK-005 live-readiness checkpoint

The new `src/live_pilot.py` supports one **explicitly authorized** real Meta Spark 1.3 API request with independent structural verification, private audit file and no automatic retry. The source/tests are committed; **a live Meta API call has not yet been performed here**. Preserve data-sharing and scientific review boundaries. Full Spark/Wonder deliberation remains pending successful first live validation.

## HACK-006 continuation status

The participant's first live Spark call passed HACK-003 structural gates. HACK-006 code now supports separate, explicitly authorized Wonder critique and Spark revision stages, with re-verification of saved local traces. **Neither the Wonder nor revised Spark call has yet been executed live.** Science remains exploratory and human review is required.

## HACK-007 interface checkpoint

The participant has completed three live Meta calls (Spark first position, Wonder critique and Spark revision) with structural citation checks. `src/build_council_ui.py` now builds a **local interactive HTML replay** from these three saved private traces and the same FSDC evidence, rechecking fingerprints and source findings. The new UI and tests are committed; **the final HTML has not yet been built or inspected on the participant's Windows computer**. The new-question input is intentionally not connected to Meta and does not pretend to answer. Human scientific review is still required.

## HACK-008 local interactive council (source committed; live browser validation pending)

New `src/local_council_server.py` and `ui/hack008.html` provide a localhost-only question interface and an explicitly authorized **maximum 4-call** Meta debate (2 simulated stakeholder perspectives via Spark, Wonder critic, Spark revised synthesis). Every stage must pass independent FSDC structural checks. Local private checkpoints, zero default calls, no automatic retries. The first HACK-008 browser/API run is **not yet verified**, and no full 8-agent council is claimed.

## HACK-009 — session-bound scientific PDF and audiovisual chamber (source committed)

The local interactive Council now supports reopening previously completed HACK-008 sessions at zero additional Meta cost, downloading a source-verified Scientific Decision Brief PDF (requires local ReportLab), visualizing preliminary WorldCover 2021 shares, and manually playing locally selected archival MP3s. Pre-hackathon ElevenLabs audio is **not** claimed as the audio of new HACK-008 model responses. New session-specific French TTS and synchronization are planned, not yet implemented. User-side PDF/Edge validation pending.

## HACK-010 — executive French brief and session-bound natural voice

The localhost app can now generate a refined French executive PDF with scientific audit annex, download a four-turn spoken French editorial script for mandatory human review, and play session-matched ElevenLabs v4 audio with synchronized active-speaker indicators when an authorized, separately generated MP3/timing JSON is loaded. Automatic TTS is **not** performed on page load or PDF export. Real HACK-008 audio generation and user-side PDF QA remain pending. All source provenance, data-status and human-review disclaimers remain mandatory.

## HACK-011 — Source-bound oral editorial approval

A new review gate keeps the actual verified HACK-008 model messages immutable and requires an explicitly approved, session-fingerprint-matched French oral manuscript before ElevenLabs speech synthesis. The new UI provides editable JSON drafts and verifies audio SHA-256 before synchronized playback. No new Meta calls are required. Source and mock tests committed; user-side end-to-end execution and paid speech generation remain pending. A short editorial reconstruction is **not** a verbatim model transcript or scientific endorsement.

## HACK-012 PDF export correction

Verified that the user's October 28 PDF still had the previous five-page visual treatment. The new `src/executive_brief_v3.py` introduces a substantially distinct navy cover, an executive decision page, prioritization matrix and audit appendix. `/api/pdf` now uses a new V3 server-side path and distinct response filename; the interface identifies the export as **V3**, avoiding silent V2 file reuse. No further model calls needed. User-side Windows PDF visual validation is pending.

## HACK-013 — grounded audiovisual chamber

The live local TerraCouncil app now has four manually browsable visual scenes derived from a completed and structurally verified HACK-008 session. During future approved session-specific ElevenLabs playback, the timestamped MP3 selects the corresponding scene and highlights the active scientific role. `src/chamber_visuals.py` derives figures and warnings only from original checked WorldPop/WorldCover evidence; `src/prepare_chamber.py` creates reviewable audio text **offline**. No new Meta or ElevenLabs calls were made during HACK-013. Edge playback with new audio and user-side tests remain pending. Audio remains a reviewed editorial reconstruction, never a verbatim original model recording.

## HACK-014 — review natural French speech directly in Edge

A new French Oral Studio permits review/editing of all four session-specific speaker interventions inside the local TerraCouncil Chamber. A protected localhost endpoint validates the original HACK-008 evidence and saves an immutable, session-fingerprint-bound oral manuscript only after explicit manual approval. It never triggers Meta or ElevenLabs. The existing separately authorized ElevenLabs synthesis and matched audio player remain available for a future reviewed session. User-side Windows validation is pending.

## HACK-015 — explicit one-click voice production

The local Edge Chamber now exposes a separate, consent-gated ElevenLabs voice generation action for a **source-bound and already human-approved** four-turn French script. The server creates a durable no-retry claim before one potentially paid TTS call, retains the MP3 and timing manifest privately, and serves them to a SHA-256-checking synchronized browser player. No new Meta debate is required. **HACK-015 source and offline tests are committed; paid synthesis and listening have not yet been user-validated.** The audio is a faithful-intent editorial reconstruction, not a verbatim scientific recording or field validation.
