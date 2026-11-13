# SparkForge repository context

Read `AGENTS.md`, `docs/PROJECT_STATUS.md`, `docs/development/COPILOT_HANDOFF.md`, then the selected section of `docs/IMPLEMENTATION_PLAN.md`. The active CSV backlog owns work states; archived plans do not.

Build a coordinated multi-agent SPARK software factory: platform brain, independent intent controller, scoped coder/test-author/reviewer/diagnostician roles, deterministic test execution, bounded repair/replanning and materially necessary human decisions. The current shipped package is assisted v1; P1 (WP-110..115) foundations are implemented in source, but the coordinated execution loop is not.

Default next task: consult `docs/development/COPILOT_HANDOFF.md` and the active backlog. WP-110 is the implemented foundation described in `docs/development/FIRST_TASK.md`. Preserve the existing v1 APIs/tests and reuse their mechanisms. No speculative empty modules, invented host launch commands or new orchestration framework. Source-neutral fake-host work does not require corp/acro access.

For each task: inspect actual state; implement one complete slice; run meaningful positive/negative tests; fix observed failures; update the four living records and append an engineering cycle; report exact results and next task. Proceed through ordinary in-scope corrections without repeated permission questions. Material decisions follow `docs/design/HUMAN_DECISIONS.md`. Never invent approvals, independent reviews, source coverage, usage or test results.

Use Python 3.12+ and the repo-local research dependencies for the full suite. Run `python -B -m unittest discover -s tests` with PYTHONPATH configured as in README, `python -B scripts/validate_plan.py --base HEAD` before commit (`HEAD~` after commit), and `git diff --check`. Native-only selector: `test_native_*.py`. Node preview tests were retired.

Keep private sources, platform credentials, real profiles, journals and transcripts outside Git. corp and acro remain isolated. Do not change v1 manual approval semantics while merely implementing future policy contracts.
