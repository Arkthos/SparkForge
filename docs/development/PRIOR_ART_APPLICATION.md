# Apply prior art selectively

This is a design-use map of the existing dated research, not a new upstream audit or an adoption/license decision. Read the actual repository dossier/source pins before borrowing code. Favor mechanisms that solve a named work-package problem; do not install a framework just because it appears in a video.

| Mechanism to study | Existing reference | Apply to | Adoption boundary |
|---|---|---|---|
| Intent clarification, specifications and artifact dependencies | [Specifications/intake](../../research/prior-art/dossier/SPECIFICATIONS_AND_INTAKE.md) | WP-110, WP-132, WP-134 | Keep behavior, technical plan and execution authority separate |
| Deterministic phases with typed worker exchanges | [Factory patterns](../../research/prior-art/dossier/FACTORY_PATTERNS.md) | WP-111, WP-121, WP-126 | Reuse concepts; qualify native host support, not a different runtime's launcher |
| Independent tests/judging, holdouts and correction | [Quality/evaluation](../../research/prior-art/dossier/QUALITY_AND_EVALUATION.md) | WP-115, WP-135, WP-141 through WP-147 | Protect oracle and evidence; worker success is not acceptance |
| Context provenance, memory, recovery and governed learning | [Knowledge/governance](../../research/prior-art/dossier/KNOWLEDGE_AND_GOVERNANCE.md) | WP-131, WP-150, WP-183, WP-184 | Keep environment-local data and inactive proposals |
| Host portability and source terms | [Compatibility/licensing](../../research/prior-art/dossier/COMPATIBILITY_AND_LICENSING.md) | WP-160 through WP-162 | Pin path-specific evidence and dependencies before adoption |
| Whole lifecycle and worked scenarios | [Factory research](../../research/ai-factory/README.md) | Architecture/evaluation reviews | Research scenarios are not executed product evidence |

The dossier includes Spec Kit/OpenSpec, Superpowers, RSC Harness, factory/loop patterns and other candidates at dated pins. Those observations are bounded, and this reorganization did not refresh every upstream source or run those projects. Exact source provenance remains in the existing catalogs/manifests.

Before adopting an implementation: identify the mechanism and task, read the relevant pinned source and tests, inspect terms/dependency closure/host assumptions, compare against existing SparkForge helpers, and record the smallest justified choice in the decision register. A prompt-only loop does not establish deterministic enforcement.
