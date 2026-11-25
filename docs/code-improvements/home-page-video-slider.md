## Available Agents

None

## Available Skills

None

## Available Rules

None

## Available Documents

- README.md
- docs/frontend/components.md

# Home Page Video Slider — Code Improvements

## 1. Scope

Reviewed on 2026-10-07 against HEAD `a41f51b7578d1facbafb93e1923b554913e862f8` **plus the existing working-tree changes**, including untracked `AnimationTimeline.js` and its test. Only this review document was created; implementation, tests, configuration, and existing documentation were not modified.

The scope is `prototypes/components/sliders/home-page-video-slider/`: all eight runtime classes, `SliderConfig.js`, `HomePageVideoSlider.vue`, `slider.css`, and `README.md`. Direct supporting evidence includes `docs/frontend/components.md`, the two slider test files, `prototypes/package.json`, installed GSAP 3.15.0/PixiJS 8.22.0 implementation, and the historical Canvas predecessor. The available Codex workflows concern infrastructure, so none applies to this frontend-only review. No backend, infrastructure, or unrelated frontend review was performed.

**Assessment:** extracting real GSAP segment animation and isolating coaching/panel UI are useful improvements. The current implementation is not a finished clean architecture: renderer lifetime protection was lost, error handling leaves coaching active, the canvas CSS selector no longer matches, and resize redraws disappear after segment animation finishes. Fix these before additional abstraction or cosmetic renaming.

Evidence conventions: file/method references below refer to the working tree unless qualified by a commit. Historical snapshots are reproducible with `git show <commit>:<path>`; changes with `git diff <before> <after> -- <path>`. The component path is abbreviated as **slider/** in tables.

History limits: `git log --all` failed because of a bad object under `refs/codex/turn-diffs/checkpoints/`. `git log HEAD` and named snapshots worked. This report reconstructs the reachable committed sequence and the current diff, not inaccessible checkpoint history or the exact order of uncommitted edits. The adjacent ZIP is not treated as an authoritative historical baseline. No claim is made that each historical commit was working in a browser.

## 2. Original Architecture

There are two useful baselines, rather than a single ambiguous “original.”

| Snapshot | Files and structure | Timing/rendering flow |
| --- | --- | --- |
| `467b53a^` (`35aeeb5`), before the reusable Vue component | `prototypes/design/components/home_page_slider/video-demo.js`, associated HTML/styles and assets | An IIFE uses DOM IDs and Canvas 2D. `holdElapsed()`, a hold timeout, RAF, media events, geometry, line progress, labels, and coaching all live together. No GSAP or slider classes. |
| `467b53a`, 2026-10-05: first component at the reviewed path | `HomePageVideoSlider.vue`, `slider.js`, `slider.css`, `README.md`, local WebM asset | Vue passes a root element to `createHomePageVideoSlider(root)`. Its closure owns a Pixi Application, Graphics/Text, DOM queries, configuration, video, hold timing, coaching, observers, listeners, and teardown. No GSAP. |
| `df0667a`, 2026-10-05: first responsibility split | Adds `sliderConfig.js`, `pixiRenderer.js`, `videoController.js`, `coachingDisplay.js`, `sliderLifecycle.js`; retains coordinating `slider.js` | Factories and state objects, not the current classes. Video controller supplies elapsed hold time; renderer draws it; coaching uses the same hold clock; lifecycle runs RAF and browser/media coordination. |
| `973f8fa`, 2026-10-06: classes and GSAP | `SliderController`, `VideoController`, `PixiRenderer`, `SliderLifecycle`, `SliderConfig` replace the factory arrangement | A 24-second main GSAP timeline includes playback waits and analysis holds, tweening `cue.elapsed`. Renderer still calculates segment progress manually. A separate audio GSAP clock and audio DOM rendering live inside `VideoController`. |
| `a41f51b`, 2026-10-06: immediate committed baseline | Introduces `VideoTimelineController`, `PlayerAnalysisTimeline`, `AudioTimeline`, `AIMotionTrackingPanel`; simplifies lifecycle | Main video clock becomes 15 seconds with explicit pauses; each hold has a separate analysis clock. Renderer still receives elapsed time and owns segment timing. `AnimationTimeline` does not exist yet. |

In the initial Vue/Pixi closure, playback advances at 0.3×. RAF plus `timeupdate` detect authored positions 2.9 and 3.7 seconds. The video pauses and seeks; `seeked` marks the frame settled. A timeout holds it for 5.5 or 3.5 seconds. `performance.now()`, `remaining`, and `timerStarted` derive elapsed hold time. `drawAnnotations()` measures bounds, sizes Pixi, maps source pixels, calculates each line's progress from `(elapsed - index * 350) / 300`, draws lines/labels, and renders. Coaching types sentences during that same hold. Visibility/intersection/page/media events suspend or resume work. Disposed/initialized guards handle teardown, including pending Pixi initialization.

The originally requested class interaction did **not** exist at that point: no `PlayerAnalysisTimeline`, `AnimationTimeline`, or class-based `PixiRenderer`. At `973f8fa`, `VideoController → PixiRenderer` passes `cue.elapsed`. At `a41f51b`, the chain becomes `VideoTimelineController → PlayerAnalysisTimeline.render(item) → PixiRenderer.showPlayerParameters(item, elapsed)`. The uncommitted work is what inserts `AnimationTimeline`.

## 3. Current Architecture

```text
HomePageVideoSlider.vue
└── SliderController
    ├── PixiRenderer                         (resource ownership)
    ├── VideoTimelineController
    │   ├── AudioTimeline                    (currently owned here)
    │   └── PlayerAnalysisTimeline
    │       └── AnimationTimeline
    │           └── injected PixiRenderer    (drawing calls)
    ├── SliderLifecycle ──→ VideoTimelineController.pause()
    └── AIMotionTrackingPanel
```

Vue supplies explicit refs, awaits initialization, starts playback, and destroys on unmount. `SliderController` validates elements, creates the renderer/controller/lifecycle, awaits Pixi, then initializes clocks, error handling, and the motion panel.

The repeating main clock pauses at `2.9 / 0.3` and `3.7 / 0.3` seconds of playback time. It pauses/seeks the video and starts a parent analysis timeline. That parent embeds a segment animation at zero and a callback at the configured hold duration. Segment tweens update progress/alpha; animation converts progress into source-space endpoints and calls Pixi's prepare/draw/render methods. Completion clears the overlay and resumes video/main clock.

The independent repeating audio clock spans `15 + 5.5 + 3.5 = 24` seconds. It is a coaching-text/microphone-indicator demo, not audio playback or recording. A separate 2.5-second interval cycles illustrative motion statuses. The main and audio clocks repeat indefinitely; analysis and segment timelines are created per hold and do not repeat.

## 4. Changes Made So Far

| Change/evidence | Before | Now | Reason / architectural effect |
| --- | --- | --- | --- |
| Canvas predecessor → component, `467b53a` | Canvas 2D, DOM IDs, IIFE | Vue wrapper, local Pixi resources, instance cleanup, local asset | Makes the demo reusable; still one large imperative helper. |
| Explicit refs, `df0667a` | Helper queries descendants of root | Vue supplies every required element | DOM ownership is clearer and easier to substitute in tests. |
| Factory extraction, `df0667a` | Configuration, drawing, timing, UI, events in `slider.js` | Separate config/renderer/video/coaching/lifecycle factory files | Better boundaries, but mutable video state and elapsed time still leak into consumers. |
| Class/API conversion, `973f8fa` | Factory with `ready` promise and automatic startup | PascalCase classes, explicit `init()`, `play()`, `destroy()`; Vue catches initialization errors | Clarifies construction/startup. Class syntax itself does not establish better ownership. |
| GSAP adoption, `973f8fa` | RAF, timeout, `performance.now()`, remaining hold time | GSAP main sequence tweens `cue.elapsed`; no application RAF/hold timeout | Removes competing application scheduling, but initially leaves manual segment scheduling in Pixi. |
| Coaching independence, `973f8fa` | Sentences available only inside their associated holds | Five equal slots across a separate 24-second clock, with 1.5-second ellipsis gaps | Intentional visible behavior change: sentences no longer describe the currently frozen pose by timing association. Static Canvas fallback was updated separately too. |
| Main/analysis split, `a41f51b` | Main timeline includes nine seconds of holds | 15-second main timeline with `addPause`; separate per-hold analysis timeline | Clearer analysis ownership and exact GSAP pause boundaries; more lifecycle coordination to get right. |
| Audio extraction, `a41f51b` | `VideoController` builds audio clock and renders/hides UI | `AudioTimeline` owns clock/typing/indicator | Good UI isolation, but `hideAudioUI()` behavior and global audio pause were lost rather than transferred. |
| Motion extraction, `a41f51b` | Playback/hold/seek paths write READY/ANALYZING | Panel independently cycles six demo statuses | Removes video/UI coupling; adds one justified timer for the requested independent demo. |
| Lifecycle reduction, `a41f51b` | Visibility, page, intersection, readiness, buffering, seek, resize handling | Only a once-only video error listener | Meets intended removal of automatic playback policy. Also removes resize observation and media synchronization; those consequences must be acknowledged. |
| Renderer lifetime regression, `a41f51b` | `disposed` guard, one-time destruction, pending-init cleanup | Guard removed; committed `init()` unconditionally destroys the app before stage setup | A bad change, not simplification: it invalidates initialization and cancellation contracts. |
| Current renderer init fix | HEAD destroys app in `init()` | Working tree removes that call; app destruction lives in `destroy()` | Correct placement now, but lost lifetime guards remain unfixed. |
| Current GSAP animation extraction | Analysis forwards elapsed; Pixi derives starts/progress/alpha | New `AnimationTimeline` tweens `{ progress, labelAlpha }` per segment and supplies `{ end, labelAlpha }` | Real transfer of animation timing out of rendering. Parent analysis no longer duplicates segment progression. |
| Current renderer API split | `showPlayerParameters()` measures, gates video state, loops segments, animates, renders | `preparePlayerParameters()`, `drawSegment()`, `drawLabel()`, `render()`, `clearPlayerParameters()` | Removes video-state knowledge and timing. However, exposes a fragile prepare/draw/render protocol and leaves unused annotation state. |
| Current resize extraction | Bounds/conditional resize inline in the full draw | `updateRendererSize()` returns bounds; geometry stored on `this.geometry` | Better named boundary, but still performs measurements each animated update; no independent redraw during the static hold. |
| Current clear ownership | Video directly asks Pixi to clear | Video asks analysis to clear; analysis asks animation to clear | Dependency direction improves, but completion now clears through multiple paths. |
| CSS/template, `973f8fa` and `a41f51b` | Canvas class `freeze-points`; panel at original right offset | Canvas class `frally-videos` while CSS still targets `freeze-points`; panel gains `translateX(-50%)` | Actual changes beyond the expected refactor. Selector mismatch is a defect; panel shift is a separate visual change. Earlier CSS reformatting is not itself an architecture change. |
| Current docs/tests | Test spies on analysis `render()`; no isolated segment tween test | Spy moved to renderer prepare; new animation test verifies endpoints, alpha, restart, cleanup; docs describe the new split | Useful segment coverage. Existing teardown/error tests still fail; documentation's idempotence claims are not evidence of correctness. |

Authored coordinates, label values, configured hold durations, 0.3× playback, and 350ms/300ms segment timing remain unchanged across the reviewed component sequence. The renderer's seek/frame guards were removed in the working tree without introducing a replacement readiness boundary. This is distinct from preserving timing constants.

## 5. Responsibility Review

| Class | Current responsibility | Verdict |
| --- | --- | --- |
| `SliderController` | Resource composition, initialization, startup, teardown | Correct top-level role; missing authoritative lifetime state. Should own global error policy and independent audio. |
| `VideoTimelineController` | Video/main clock/analysis coordination, plus audio construction/start/destruction | Mostly focused. Move supporting audio ownership upward, remove stale renderer/element references, define cancellation versus suspension. |
| `PlayerAnalysisTimeline` | Parent phase duration and completion, nested animation lifetime | A legitimate boundary because drawing duration differs from total hold; not just a wrapper if it enforces that contract. |
| `AnimationTimeline` | Segment GSAP tweens, endpoint projection, frame submission | Genuine animation responsibility. Does too much low-level frame orchestration, but no DOM/Pixi-internals knowledge. |
| `PixiRenderer` | Pixi resource lifetime, bounds, geometry, frame clearing, lines and label layout | Correct domain after timing removal. Needs coherent frame API, resize invalidation, lifetime repair. |
| `AudioTimeline` | Coaching clock, typing, indicator DOM | Useful isolation; still consults video error and imports full analysis configuration. Missing explicit reset/error UI behavior. |
| `AIMotionTrackingPanel` | One status index and interval | Small but coherent. Retain it; a new service or GSAP replacement offers little benefit. |
| `SliderLifecycle` | One event registration, error visibility, controller pause | No longer warrants a separate class. Merge into `SliderController`. |

One owner per behavior matters more than one class per verb. Do not split label placement, sentence slicing, or cover arithmetic into new classes merely to shorten methods.

## 6. VideoTimelineController Review

`createVideoTimeline()` expresses pause positions clearly, and `addPause` is covered by an overshoot test. Analysis pauses leave audio running as intended. Video UI rendering has been removed. Main timeline time is **playback seconds at the configured rate**, not source-video time and not full-cycle wall time; this distinction should remain explicit.

Problems in `init()`, `playTimeline()`, `pause()`, and `onVideoResume()`:

- `createVideoTimeline()` overwrites the previous timeline without killing it. Repeated direct initialization can leak a live clock; repeated top-level initialization replaces resources too.
- `currentTimelineData` is used only as a truthy active-analysis marker in production. On video error, `pause()` clears the analysis but leaves that marker set. Subsequent `play()` takes the resume-analysis branch with a null analysis timeline, rather than restarting video. Completion clears it normally; cancellation does not.
- `onVideoResume()` clears analysis even when analysis completion has already cleared animation, then resumes the main clock before the `video.play()` promise settles. Rejection pauses only video/analysis, leaving audio active and no explicit playback-rejection message.
- The main GSAP clock advances independently of actual decoding/buffering. `onVideoPause()` seeks and immediately begins analysis; it does not wait for a displayed target frame. Exact clock pause placement is not proof of video-frame synchronization. This is a code-derived browser risk, not a reproduced visual result.
- `elements` and `pixiRenderer` are stored but no longer read by production methods after construction. The test's renderer spy is not a reason to retain an otherwise redundant runtime dependency.

Keep `videoTimeline`: it distinguishes the main clock well. Replace `currentTimelineData` with a single explicit analysis-active state, or a public phase status query, rather than retaining the entire item only for truthiness. `onVideoPause`/`onVideoResume` are imperative commands, not event handlers; `startAnalysis(item)` and `resumePlayback(time?)` would materially clarify their role during a future API change. `playTimeline()` need not become another class.

Preserve the requested absence of generic visibility/seek playback automation. If guaranteed frame alignment is required, put a narrowly scoped internal seek/readiness contract in this controller, with cancellation/error handling, rather than bringing back the old broad lifecycle observer system.

## 7. PlayerAnalysisTimeline Review

The current phase starts `AnimationTimeline`, nests its timeline at zero, pauses/resumes through the parent, and reports completion through a callback. It does not calculate segment progress, placement, or label opacity. This is the right dependency direction.

For current configuration, six segments finish in `5 × 0.35 + 0.3 = 2.05s`, leaving 3.45s of the first hold; eight finish in `7 × 0.35 + 0.3 = 2.75s`, leaving 0.75s of the second. The parent makes the final overlay persist until 5.5s/3.5s.

However, a callback at the requested duration does not cap a longer child. A read-only probe using the installed GSAP and current class requested a 0.1-second phase with two segments: parent duration was **0.65 seconds**, and completion had not fired at 0.1 seconds. The child was paused at that point. Thus the phase owns duration only under an unstated condition: drawing must fit inside the hold. Add a configuration invariant or define clipping explicitly; preserving current visuals favors validation over automatic speed changes.

`AnimationTimeline.play()` starts independently and then returns a running timeline to be reparented. Current tests pass, so this is not evidence of a present scheduling failure. Still, composition should build a non-running child and let only the phase start its clock. Avoid changing the child to remain GSAP-paused inside the parent accidentally; the parent must actually be able to drive it.

Completion calls `animationTimeline.clear()`, then the video completion callback calls `playerAnalysisTimeline.clear()`, which destroys/clears again. `play()` also destroys a child before child `play()` clears it again. Establish one finish/cancel path: kill clocks and clear output once, report completion only for successful finish. Retain separate pause/resume for suspension that preserves progress.

## 8. AnimationTimeline Review

**It is now a real GSAP-driven segment animation.** Each segment has one tween beginning at `index * lineStepMs / 1000`, lasting `lineDrawMs / 1000`, with `ease: "none"`. GSAP owns progression and sequencing and interpolates both `progress` and `labelAlpha`. There is no `elapsed`, `analysisTime`, wall-clock delta, interval scheduler, or manual clamp of elapsed progress in this class.

Multiplying an index by a configured step when building a timeline is declarative scheduling, not a second running clock. Likewise `start + (end - start) * progress` projects a GSAP value into coordinates; it does not duplicate timekeeping. Label fade currently starts and ends with line drawing, matching the previous linear fade. Separate alpha state permits later independence without requiring it now.

Remaining improvements:

- Build rather than autonomously start the child when composing it into analysis; public child `resume()` is currently unused by production callers because the phase resumes its parent.
- Keep mutable per-segment tween targets local and stable for that sequence. They are necessary GSAP state, not redundant global fields.
- Replace prepare/draw/render orchestration with one renderer frame submission when changing the API. Iterating segments to create tweens belongs here; iterating submitted primitives to draw them can legitimately belong to the renderer. These are different responsibilities, not duplicate timing.
- `if (drawing.labelAlpha === 0) return` uses label opacity to decide whether a line exists. Current positive-alpha config works, including segments with null labels, but line visibility should depend on progress/explicit visibility if invisible labels become configurable.
- Stop exposing unused controls solely for symmetry. Keep `clear` distinct from resource-only destruction only if callers require that distinction.

Recommendation on state representation: retain `{ progress, labelAlpha }` **inside** animation and submit `{ end, labelAlpha }` in source coordinates to Pixi, as the current code does. Animation calculates the endpoint; Pixi maps it to canvas space and draws. A renderer receiving normalized progress could still be timing-free, but endpoint state makes its contract more explicit and supports frozen-frame redraw without consulting a timeline. No need for a dedicated drawing-state class.

## 9. AudioTimeline Review

Audio has its own repeating GSAP clock and continues through both analysis holds. It contains all coaching DOM writes; video control contains no audio rendering. These are improvements.

This clock is not a declarative sentence-tween sequence: `render()` still derives `elapsed`, sentence index, slot elapsed, typing interval, and letter count from `timeline.time()`. That is isolated manual presentation scheduling, not a second independently advancing clock. It is acceptable for five fixed sentences; replacing it with many callbacks/tweens is optional, not necessary to complete the segment refactor.

The arithmetic is clear: 24 seconds / five sentences = 4.8-second slots, 3.3 seconds of sentence display plus 1.5 seconds of `...`; typing normally advances every 55ms and accelerates only when needed to fit. No separate typing timer exists. Text writes are conditional; `aria-label` and visibility/indicator assignments are repeated each update. Cache only if measurement justifies it.

The failures are lifecycle-related. `render()` returns on `video.error` without hiding already-visible text or deactivating the indicator. `pause()` preserves UI, and `destroy()` only kills the clock. `VideoTimelineController.pause()` never pauses audio. Therefore analysis independence has unintentionally become independence from fatal error/teardown policy. Existing error and rejection tests expose this regression from `973f8fa`.

Move audio ownership to `SliderController`. Give audio its own explicit reset/stop UI behavior; a global failure invokes that behavior, while an analysis hold does not. Supply sentences and cycle duration through configuration at composition time instead of making audio import all analysis items and inspect `elements.video.error`. This keeps support UI independent in both timing and dependency direction. No new typing class is warranted.

## 10. AIMotionTrackingPanel Review

The panel is independent of video analysis: a single interval calls `update()` every 2500ms; `currentIndex` cycles READY, TRACKING PLAYER, ANALYZING MOTION, DETECTING POSE, TRACKING JOINTS, MOTION ANALYSIS. It changes only Phase. Mode/Overlay remain static, and comments/accessible labeling identify a demo.

`play()` prevents duplicate intervals and shows the first value immediately. `destroy()` clears the interval and is idempotent. Both index and interval handle are useful. Calling this class's `play()` after `destroy()` currently restarts it from its retained index; terminal component disposal must be enforced by its owner. The interrupted-init test failure comes from that owner, not interval duplication inside the panel.

A closure with start/stop could do the same job, but converting it buys little in this class-based component. Keep this small class and optionally inject just the Phase element instead of the entire elements bag. Do not move it back into video control or add a general status scheduler. Decide global error stop behavior in `SliderController`; normal analysis pauses must leave it running.

## 11. SliderLifecycle Review

All requested automatic visibility, pagehide/pageshow, seek, intersection, readiness, and buffering playback handlers are gone. There is no application RAF. The remaining `AbortController` owns a once-only `video.error` listener; the handler shows the error element and invokes video-controller `pause()`. Destruction aborts registration correctly, as the focused tests confirm.

This class is now too small to justify a separate lifecycle abstraction. Merge registration/error routing/abort into `SliderController`, which already controls resource lifetime and should handle coordinated failures. Repeated current `init()` calls can register fresh callbacks on the same non-aborted signal; it is not an initialization guard.

Removing automatic playback policies is consistent with the stated direction. Removing all resize notifications is a separate rendering decision and was not a sound consequence of that simplification. Restore rendering invalidation under Pixi ownership without reintroducing visibility-based playback control. Reduced-motion CSS still disables indicator animations, while JavaScript no longer prevents video/annotation animation; document that actual behavior rather than claiming the old policy remains.

## 12. PixiRenderer Review

Pixi now contains no GSAP import, analysis duration, segment start time, elapsed-time arithmetic, or video playback-state checks. Its video reference is used for geometry only. `app.destroy(false, { children: true })` is correctly located in `destroy()` in the working tree; its unconditional historical placement in `init()` was incorrect.

The API still carries too much context and hidden ordering:

| Method / argument | Why it is currently needed | Recommendation |
| --- | --- | --- |
| Historical `showPlayerParameters(activeFreeze, elapsed)` | Whole frame plus manual animation time | Correctly removed; do not restore elapsed-time rendering. |
| `preparePlayerParameters(currentPositionParameters)` | Stores the supplied item, measures geometry, clears Graphics, hides labels | The item is only written to a never-read property. Remove this argument/state unless introducing a real retained frame. `beginFrame()` would describe the present behavior more accurately. |
| `drawSegment(currentPositionParameters, segment, index, drawing)` | Item supplies label text and total segment count; segment supplies line start and complete endpoints for label layout; index selects pooled Text and placement; drawing supplies animated endpoint and alpha | Whole timeline item includes irrelevant `time`, `duration`, and `feedback`. A narrower frame annotation contract is preferable. |
| `drawLabel(label, currentPositionParameters, geometry, segment, index, alpha)` | `label`: pooled Pixi Text; item: text/count; geometry: source-to-canvas mapping and compact width; segment: full midpoint/direction; index: layout rules/text selection; alpha: already animated opacity | Private rendering helper is justified. Pass required label text/layout metadata directly if simplifying the contract. |
| `geometry` | `scale`, `left`, `top` map source pixels; `width` selects compact placement | Rendering state belongs here. Name width `canvasWidth` if exposed beyond this helper. |

**Index is not only a label lookup.** It selects `this.labels[index]`, retrieves `item.labels[index]`, identifies lower-body position using total segment count, selects alternating sides/compact offsets, and distinguishes the first two upper-body labels. Replacing index with label text alone would lose those rules. A future label descriptor can carry text and placement role, or retain index/count internally until such metadata is warranted.

`drawLabel()` is the longest rendering method but remains cohesive: midpoint, side, offset, rotation clamp, font sizing, anchor, text, opacity. Keep layout together. Extract only a pure placement calculation if useful to test compact/wide rules; avoid a helper per assignment.

Prefer an atomic `renderFrame(annotation, segmentStates)` API that measures or reuses valid geometry, clears, draws, and renders. Renderer iteration over primitives is appropriate. It should retain the latest submitted frame only if needed for resize redraw. This is more robust than requiring every caller to remember prepare → draw → render, and avoids `drawSegment()` accessing undefined geometry when called first.

The fixed eight-Text pool fits today's six/eight segments. More than eight labeled segments would address a missing Text object. Validate the fixed configuration or size the pool from the supported data; do not build a generic renderer framework for hypothetical inputs.

## 13. Geometry and Resize Review

For source dimensions `Ws = 1280`, `Hs = 720`, video bounds `V`, and canvas bounds `C`, the current mapping is:

```text
scale = max(V.width / Ws, V.height / Hs)
left  = V.left - C.left + (V.width  - Ws * scale) / 2
top   = V.top  - C.top  + (V.height - Hs * scale) / 2
canvasX = left + sourceX * scale
canvasY = top  + sourceY * scale
```

This is correct for centered `object-fit: cover` with the current uniform `scale(1.07)` video transform: bounding rects already include the transform, so multiplying by 1.07 again would be wrong. `width` means canvas CSS width for the 600px compact breakpoint; it is not source width or DPR-adjusted width. There is no geometry duplication elsewhere in current runtime classes.

For example, with coincident untransformed 800×450 bounds, scale is 0.625 with zero crop offsets. For 400×450, scale remains 0.625 and horizontal crop offset is −200. The actual video transform expands its bounds around the center; the same formula accounts for that expansion. This assumes the annotation reference matches the media, centered object positioning, and no separate transform scaling the canvas/whole coordinate system. Arbitrary rotated/skewed/nonuniformly scaled ancestors are not covered by this formula.

**Concrete layout defect:** Vue uses `class="frally-videos"`, but `slider.css:31` targets `.freeze-points`. Repository search found no alternative `.frally-videos` rule. Pixi's inline 100% width/height do not restore absolute positioning, inset, stacking, or pointer-event rules. The canvas remains in normal flow after the full-height video instead of receiving the intended overlay placement; clipping/misalignment is likely. Correct arithmetic cannot compensate for that missing layout contract. The mismatch originates in `973f8fa`; a browser screenshot was not taken in this review.

`updateRendererSize()` separates conditional resize from line drawing, but also measures both elements. `preparePlayerParameters()` calls it for every segment timeline update. **It does not resize the renderer unconditionally:** dimensions and DPR are compared first. `autoDensity`, logical CSS dimensions, and the DPR argument are consistent with the installed Pixi `ViewSystem.resize(width, height, resolution)` implementation. Restoring CSS percentages after a resize is intentional; avoid multiplying logical coordinates by DPR again. Fractional bounds/renderer rounding deserve a browser check before claiming every equality comparison is stable.

The more significant issue is missed updates. No resize observer remains, and rendering is driven only by the child animation's `onUpdate`. An in-memory probe advancing the first phase from 2.05s to 4s recorded **zero redraws**. During the final 3.45s/0.75s of a hold, or while paused, CSS dimensions can change with no backing-store resize, geometry recomputation, or label repositioning. Previously the phase's `onUpdate` redrew throughout the hold; even earlier a resize observer covered paused output.

Recommendation: keep geometry calculation in `PixiRenderer`, cache a small plain mapping object, and invalidate it for dimensions/DPR/relative video-canvas position changes. Recompute on initialization/first valid layout and rendering resize notifications; retain the last submitted visual frame so a resize redraw does not advance animation. Observe dimensions without controlling video playback. A `ResizeObserver` alone does not detect every transform/position/DPR change, so include an explicit invalidation path for those supported changes. Start with simple measurements at frame submission plus event-driven static redraw; optimize measurement caching only after correctness and profiling. A small pure `computeCoverGeometry()` helper is useful for tests; a geometry class is not.

## 14. State and Lifecycle Review

| State | Keep / Remove / Move | Reason |
| --- | --- | --- |
| Video `videoTimeline` | Keep | Owns main playback schedule. Kill before replacement and clear on terminal destruction. |
| Video `currentTimelineData` | Replace/remove full-item storage | Production only needs phase status. Maintain one authoritative active state and reset it on cancellation/errors. |
| Video `elements`, `pixiRenderer` | Remove stored fields | Constructor can pass required dependencies; methods no longer use these fields. Tests should not dictate a redundant production API. |
| Analysis `timeline` | Keep | Distinct hold clock; supports duration, suspension, completion. |
| Animation `timeline` | Keep | Owns segment tweens and cancellation. |
| Local `drawings`, `progress`, `labelAlpha` | Keep | GSAP tween targets; no independent elapsed clock. |
| Renderer `currentPositionParameters` | Remove as currently implemented | Written/reset, never read. A future retained frame is different and must actually power redraw. |
| Renderer `geometry` | Keep and initialize/invalidate clearly | Useful mapping, currently recalculated each update despite being stored. |
| Renderer `app`, `graphics`, `labels`, `canvas`, `video` | Keep | Resource handles and geometry sources. Narrow video use to measurement. |
| Renderer `initialized` and missing disposed state | Repair, not blindly remove | Resource readiness and a request to cancel/destroy during pending initialization describe different facts. Use coherent explicit states rather than duplicated unrelated flags. |
| Top-level lifecycle state / pending init promise | Add deliberately | Necessary to reject/reuse repeated init, prevent late startup, and make destruction terminal. Do not infer owner lifetime from a child's undocumented field. |
| Audio `timeline`, sentences | Keep | Independent UI schedule/content. Null the clock when destroyed; reset UI explicitly. |
| Audio local `elapsed`, `slotElapsed`, typing interval | Keep unless replacing its presentation scheduler | Derived locals, not redundant persisted state or extra timers. |
| Panel `interval`, `currentIndex` | Keep | Prevent duplicate timers and rotate statuses. |
| Lifecycle `events` | Move | Abort handle belongs with merged error registration in `SliderController`. |
| Required `root` ref | Remove runtime requirement if unused | Current runtime validates it but no longer observes/reads it; Vue may still retain a root ref for its own needs. |
| `freezeTolerance` config export | Remove if frame-alignment contract does not use it | No current slider consumer. Do not restore renderer playback checks just to justify it. |
| Historical `cue.elapsed`, `analysisTime`, `held`, `settled`, remaining timeout state | Remain removed from animation/rendering | GSAP replaced application hold/segment clocks. Audio's derived elapsed local serves a different purpose. |

Lifecycle contract status:

- **Init:** required refs are validated before resources. Failure propagates to Vue. Repeated or concurrent `SliderController.init()` overwrites resource references without releasing old resources. There is no pending-init guard.
- **Destroy during init:** `PixiRenderer.destroy()` does nothing while uninitialized and records no cancellation. Awaited `init()` then completes; `SliderController` checks a `disposed` field that no longer exists and proceeds. Vue's `slider = null` prevents its own late `play()` but does not prevent late resource allocation/listener setup. Direct controller callers can also start the leaked instance.
- **Play:** repeating play in a live initialized instance does not recreate timelines/intervals, which tests cover. After destruction, `initialized` remains true and `disposed` is undefined, so the top-level guard permits playback again. The test demonstrates video resumption.
- **Pause/resume:** parent analysis pause preserves child progress; audio continues, as desired for analysis. Error cancellation leaves stale active-analysis state. A generic global pause/error policy is not implemented coherently.
- **Clear:** kills phase/segment clocks and clears Pixi, but multiple completion paths perform the same clear. Clearing is not equivalent to pausing.
- **Destroy:** event abort/panel stop work. Phase/animation timeline replacement kills prior clocks. Renderer destruction is not idempotent; audio destruction leaves visual state active. Video/audio retain references to killed clocks. Main clock replacement lacks a kill.

Keep all actual Pixi app destruction inside `PixiRenderer.destroy()`. Pending initialization can call that method after settling if disposal was requested, with a resource-destroyed guard so an early cancellation request does not suppress the later actual release. `SliderController` must independently prevent startup after cancellation. Avoid one disposed boolean that returns early before newly initialized GPU resources can be released.

## 15. Dependency Review

There are no circular imports among the current classes. The drawing chain follows the intended direction, and the completion closure is a narrow callback rather than a reverse class dependency. `AnimationTimeline` does not inspect DOM bounds, DPR, Pixi Application, or label objects. `PixiRenderer` no longer knows about analysis clocks or playback state.

Deviations and duplicated knowledge:

- Audio is a child of video rather than a top-level peer; it imports analysis items to derive cycle duration and reads video error state. Move configuration and global policy to composition.
- `SliderController` still relies on renderer internals (`initialized`, missing `disposed`) to decide its own lifetime. A removed child flag broke the owner contract silently.
- Phase/animation/video all participate in clearing the same analysis output. Normal finish should have one clear owner; video only transitions playback afterward.
- Analysis owns hold duration; animation owns drawing duration. This distinction is good, but their fit must be validated rather than assumed. Audio needs a derived full-cycle duration, not authority over holds.
- Video and analysis both know whether a hold is active; the video's marker can disagree with a destroyed analysis. Use one status contract.
- Animation loops once to build tween targets and again to project a frame. This is not duplicate scheduling. Renderer label resets and per-frame primitive drawing are rendering work, not segment-time ownership.
- Multiple classes having `destroy()` is appropriate when each releases its own resources. Multiple callers destroying/clearing the same resource without guards is the problem.

## 16. Problems Found

| Priority | Finding and evidence | Practical impact / confidence |
| --- | --- | --- |
| High | Lost disposed/idempotence/pending-init guards in `PixiRenderer.destroy()/init()` and stale guard in `SliderController.init()/play()` | Repeated destruction, resource survival after unmount, and playback after destruction. Confirmed by four focused test failures covering these paths, including the late panel interval. Origin: `a41f51b`. |
| High | Canvas class mismatch, `HomePageVideoSlider.vue:60` vs `slider.css:31` | Overlay positioning styles do not apply. Source-confirmed; exact browser appearance unverified. Origin: `973f8fa`. |
| High | Error/rejection no longer stops/resets coaching: video `pause()`, audio `render()/destroy()` | Stale active cue/indicator and audio clock continuing after playback failure. Confirmed by two focused failures. Origin: audio extraction in `a41f51b`. |
| Medium | No redraw during static holds or explicit pause; only child animation updates submit frames | Resize/DPR/layout changes can leave stale geometry/backing size. Static-hold absence of updates confirmed by probe; browser effect still needs visual test. Latest extraction worsens loss of resize handling. |
| Medium | Error clears analysis but leaves `currentTimelineData` | Later play attempts to resume a nonexistent analysis. Direct code path; missing dedicated recovery test. |
| Medium | Repeated init leaks/replaces live resources; main clock not killed on replacement | Contract is unsafe outside the single normal Vue mount path. Direct code evidence. |
| Medium | Main clock not tied to media progress; analysis starts immediately after seek | Buffering, delayed play, or seek decode can diverge from annotations. Architectural risk, not a measured browser failure. |
| Medium | Phase duration does not cap longer child | Unsupported config silently changes duration. Confirmed 0.1s request → 0.65s parent probe; current two items fit. |
| Low | Redundant clearing, unused fields/export, exposed draw protocol, overly small lifecycle class | Maintenance cost and ambiguous ownership; simplify after correctness fixes. |
| Low | Fixed label pool, index-dependent placement, no narrow annotation contract | Current config is supported; future configuration can break assumptions without validation. |

Validation performed from `prototypes/`:

```sh
node --test tests/home-page-video-slider.test.js tests/animation-timeline.test.js
```

Result: **21 tests, 15 passed, 6 failed**, exit code 1. Exact failing tests:

1. `destroy during a hold releases timers, animation frames and media listeners`: two renderer destroys instead of one.
2. `unmount during async Pixi initialization destroys the renderer without starting a loop`: zero renderer destroys instead of one.
3. `video errors clear an active hold, overlay and coaching state`: coaching remains visible.
4. `play only starts the initialized slider without reinitializing it`: video resumes after destruction.
5. `playback rejection suspends both clocks and hides audio UI`: audio timeline remains unpaused.
6. `motion panel does not start before playback or after interrupted initialization`: an interval starts after cancelled initialization.

Passing tests cover current segment endpoints/alpha/order, configured holds, independent coaching, loop reuse, pause overshoot, panel independence, error-listener removal, required refs, and initialization rejection. Two additional read-only in-memory probes checked short parent duration and static-hold update counts, as described above. No tests were edited or disabled.

Limits: tests use real GSAP with mocked Pixi/media/DOM. They cannot prove CSS alignment, WebGL destruction safety, actual media readiness, device-pixel rendering, or frame latency. No browser visual QA, build, unrelated full suite, historical-checkout test run, or performance benchmark was performed. A build would not establish these runtime contracts. No security-sensitive backend behavior is involved; text uses `textContent`/Pixi Text, the asset is local, and there is no microphone capture. Demo values remain authored examples, not inferred observations.

The README currently asserts idempotent destruction including pending initialization, contradicted by tests. `components.md` also links to a nonexistent slider `index.html` and uses broader microphone/analysis wording than this demo implements. Record these discrepancies now; update those files only in a later authorized implementation/documentation task.

## 17. Recommended Improvements

Prioritize observed correctness defects: lifetime guards, canvas styling contract, and coordinated failure/UI reset. Preserve 0.3× playback, authored coordinates, hold durations, line ordering/fades, sentence slots, and normal-analysis audio independence while fixing those defects.

Then make ownership explicit: top-level controller owns global lifecycle/error policy and supporting UI; video owns playback and starting/stopping the analysis phase; phase owns completion/cancellation; animation owns segment tweens; renderer owns frame submission/geometry/redraw/resources. Collapse `SliderLifecycle` into the owner, but retain the phase/animation split because their durations and cancellation semantics differ.

Use a small immutable annotation description and per-frame endpoint/alpha state at the rendering boundary. Submit a complete frame instead of exposing a multi-call rendering transaction. Cache only what a real redraw path consumes. Do not replace every class with a composable, add a geometry service, create a global event bus, or rewrite audio timing just to make all classes use identical APIs.

Naming changes should follow these boundaries: `currentTimelineData` → explicit active-phase state; `onVideoPause`/`onVideoResume` → command names; `AnimationTimeline` → optionally `PlayerParametersAnimation` if a more specific name helps navigation. `PlayerAnalysisTimeline`, `VideoTimelineController`, and `PixiRenderer` already communicate useful roles. `drawing` is acceptable locally; `segmentState` is clearer at a public frame boundary. No renaming is needed solely for style.

## 18. Recommended Final Architecture

```text
HomePageVideoSlider.vue
└── SliderController
    ├── lifecycle state + error registration/policy
    ├── PixiRenderer                         (created/destroyed here)
    ├── VideoTimelineController
    │   └── PlayerAnalysisTimeline
    │       └── AnimationTimeline
    │           └── PixiRenderer             (injected frame-rendering API)
    ├── AudioTimeline
    └── AIMotionTrackingPanel

SliderConfig → authored annotations + timing + derived cycle duration
PixiRenderer → private cover geometry helper + resize invalidation
```

Exact responsibilities:

- **Vue:** template/styles/refs; one controller instance; await init; start; unmount; initialization error presentation.
- **SliderController:** validate/inject dependencies, guard repeated/cancelled init and terminal destroy, start peers, route global failure/suspension, register/abort error listener, destroy each owned resource once. This absorbs `SliderLifecycle`.
- **VideoTimelineController:** video playback and main schedule, configured analysis points, active-phase transition, cancellation/recovery, completion-triggered playback resume. No audio DOM or panel knowledge. Report playback failures upward.
- **PlayerAnalysisTimeline:** start the segment sequence, hold final output until configured duration, enforce duration-fit contract, pause/resume, finish/cancel and clear once. Invoke completion only on success.
- **AnimationTimeline:** create GSAP segment starts/durations/progress/alpha, derive source endpoints, submit frames. Parent phase controls playback of the nested sequence.
- **PixiRenderer:** own Application/Graphics/Text, render submitted frame data, compute/cache source-to-canvas geometry, handle sizing/DPR/static redraw, and destroy GPU resources. No clock or playback-state knowledge.
- **AudioTimeline:** independently schedule and render coaching/typing/indicator; expose explicit pause and reset/stop semantics. Receive content/duration without depending on analysis objects or video errors.
- **AIMotionTrackingPanel:** one independent illustrative status cycle, start/stop cleanup. No perception claims or playback coupling.
- **SliderConfig:** authored demo data and shared constants; derive full-cycle duration once without introducing another class.

Preferred interaction flow:

1. Vue awaits controller initialization; cancelled/unmounted instances cannot become runnable.
2. Top-level play starts video control, audio, and panel through their public APIs.
3. The main timeline reaches an authored analysis point.
4. Video control pauses the main clock/video and selects the target frame under the documented media-readiness contract.
5. Video control starts the analysis phase with annotation data and completion callback.
6. Analysis builds/nests the segment animation and starts the parent phase.
7. GSAP advances each segment; animation projects source endpoints and alpha into a frame submission.
8. Pixi maps geometry and draws; once drawing finishes, the final frame remains visible.
9. Rendering invalidation redraws the retained frame when size/DPR/layout changes, without advancing any clock.
10. Analysis finishes at its configured duration, clears once, and reports completion.
11. Video control clears its active-phase status and resumes video/main clock.
12. Audio and panel continue independently through steps 3–11. Global error/destruction follows a separate top-level path that stops resources and resets UI.

## 19. Proposed Refactoring Steps

These are future changes only; none was performed in this review.

1. **Repair lifetime contracts.** What: make top-level init repeat-safe, track pending cancellation, prevent play after destroy, and guarantee exactly-once Pixi release after pending init settles; kill old main clocks before replacement. Why: fixes leaked resources and four failing lifecycle cases before changing APIs. Affected: `SliderController`, `PixiRenderer`, `VideoTimelineController`, focused lifecycle tests. **Risk: High** because async cancellation and resource order must be preserved. Validate double destroy, concurrent/repeated init, unmount during init, init failure, late playback rejection, and no post-destroy startup; keep app destruction in renderer `destroy()`.

2. **Restore the canvas layout contract.** What: align the Vue canvas class with its scoped overlay selector; retain intended CSS geometry. Why: source-to-canvas math requires a correctly positioned canvas. Affected: `HomePageVideoSlider.vue`, `slider.css`, browser layout checks. **Risk: Low.** Verify actual overlay bounds and both authored poses at desktop/compact sizes and multiple DPRs; do not accidentally remove the separately committed panel translation without a design decision.

3. **Repair coordinated failure handling and stale phase state.** What: distinguish normal analysis suspension from global playback error/stop; give audio explicit UI reset, reset phase activity on cancellation, and handle rejected play promises without reviving disposed instances. Why: fixes the two audio failures and makes recovery coherent. Affected: `VideoTimelineController`, `PlayerAnalysisTimeline`, `AudioTimeline`, `SliderController`, tests. **Risk: Medium.** Verify audio advances through ordinary analysis but stops/resets on global failure, and cancellation does not call successful completion.

4. **Move independent UI ownership to the top level and merge lifecycle.** What: make `AudioTimeline` a `SliderController` peer, inject sentences/cycle duration, merge the single error listener/abort handle from `SliderLifecycle`; narrow panel dependencies. Why: one global policy owner without video/UI coupling or a one-listener class. Affected: `SliderController`, `SliderLifecycle`, `VideoTimelineController`, `AudioTimeline`, `AIMotionTrackingPanel`, `SliderConfig`, tests. **Risk: Medium.** Preserve startup order, independent clocks, once-only error behavior, and listener teardown.

5. **Make analysis composition and completion ownership explicit.** What: construct the child for parent-driven execution, eliminate redundant clears, validate drawing fits each hold, and remove unused child controls if no longer needed. Why: one clock owner per phase and one finish/cancel path. Affected: `PlayerAnalysisTimeline`, `AnimationTimeline`, `VideoTimelineController`, configuration validation/tests. **Risk: Medium.** Verify exact 5.5s/3.5s holds, pause/resume mid-stroke, final-frame persistence, replacement cancellation, and invalid shorter-hold behavior.

6. **Consolidate frame submission and add static resize redraw.** What: give Pixi one frame-rendering API using annotation data plus endpoint/alpha states; retain the last visual frame; handle resize/DPR/relative-position invalidation; optionally extract a pure cover helper. Why: removes ordering hazards and restores responsive output after animation stops. Affected: `PixiRenderer`, `AnimationTimeline`, geometry/render tests. **Risk: Medium.** Validate centered crop, transformed video bounds, compact labels, paused/static holds, empty clear, DPR changes, and observer teardown; measure before aggressive caching.

7. **Document and test media synchronization limits.** What: exercise delayed play, seeking, slow decoding, and buffering in a browser; if precise target-frame display is required, add a narrow internal frame-ready boundary in video control with cancellation. Why: GSAP-clock correctness alone cannot guarantee media-frame correctness. Affected: `VideoTimelineController`, media integration checks, component README. **Risk: High** if changing the synchronization behavior. Preserve the intended removal of broad visibility/intersection/external-seek automation and independent coaching timing.

8. **Remove proven dead state and clarify public names.** What: remove renderer's unread annotation field, stale controller references, unused root requirement/export as applicable; narrow label/frame data and rename only ambiguous command/state APIs. Why: align surface area with actual owners after functional repairs. Affected: relevant runtime classes, `SliderConfig`, Vue refs only if unnecessary, focused tests. **Risk: Low.** Do not replace meaningful GSAP targets or lifetime state with implicit guesses.

9. **Update documentation and complete validation.** What: reconcile README/component docs with actual lifetime, timing, supported media behavior, demo semantics, and real paths; run slider tests and prototype build, then browser checks for mounting/unmounting, failure states, both holds, compact layouts, DPR, and resize during static output. Why: current documentation overstates reliability and mocked tests miss CSS/media/WebGL defects. Affected: component README, `docs/frontend/components.md`, relevant tests, this review's status if desired. **Risk: Low.** Preserve all existing tests; fix root causes rather than weakening assertions to accept failures.
