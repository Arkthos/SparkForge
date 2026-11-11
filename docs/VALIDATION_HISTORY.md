# Validation history

Only actual checks of the clean publication candidate are recorded here.
Private historical source/read/reviewer receipts are not imported as a new pass.
The acceptance matrix remains a planned inventory, not a result ledger.

## 2026-11-11: clean publication preparation

Project-owned executable/test/fixture/static-asset files were copied into an
independent repository without the original Git database or restricted docs.
Source-neutral documentation and reviewed public research are being integrated.
The original private working tree and history are retained unchanged.

| Actual operation | Result | Evidence boundary |
|---|---|---|
| Private GitHub repository identity/branch read | PASS | Correct requested private destination; empty before this publication |
| Project-owned software copy | PASS | 30 selected executable/test/fixture/static-asset/ignore files; no private Git objects or captured source collections |
| `python -B -m unittest discover -s tests -p test_native_factory.py` | PASS: 54 cases in 6.895 seconds | Actual unchanged core in the independent publication checkout |
| Runtime-documentation worker package/integration/dogfood selectors | PASS: 39 / 5 / 7 cases, no skips | Initial missing `validate-spec` wording failed its existing assertion, was corrected and passed on rerun; no executable/test changes |
| Public-research worker checks | PASS within recorded scope | 35 content hashes, 213 local links, 125 source citations and two JSON examples; historical upstream inspection is not new network/framework execution |
| `python -B -m unittest discover -s tests` | PASS: 310 collected, 308 passed, two skips in 73.848 seconds | Complete suite against this standalone checkout; Windows symlink-creation privilege unavailable for two cases |
| `node --test --test-reporter=spec tests\test_preview_model.cjs tests\test_preview_assets.cjs` | PASS: 40 cases, no skips | Current model and static-asset behavior |
| `preview\browser-checks.html` in its own local-file browser frame | PASS: 51 synthetic cases | Actual 1280x900, 490x828 and 390x844 frame viewports; no other preview touched, real user acceptance NOT_ASSESSED |
| `build_package` for `corp` and `acro` into fresh owned outputs | PASS: 9 / 8 owned resources | Structural inventories only; generated outputs remain ignored |
| Native CLI `--no-auto-update --plugin-dir <profile> plugin list --json` and `skill list --json` | PASS for both profiles | CLI 1.0.106-2; exact skill paths checked, no model session or installation |
| Complete outgoing content/link preflight | PASS: 99 files before the new receipt, 58 Markdown files, 278 local links | Positive file/type scope; no selected credential/private-source indicators or link errors; not a universal secret/security audit |
| Initial staged whitespace check | FAIL | Preserved CRLF was classified as trailing whitespace; repository attributes now recognize CR-at-EOL while retaining the normal whitespace rules |
| CRLF-aware staged whitespace recheck | FAIL on 45 Markdown hard-break lines | Required whitespace-clean equivalent layout and refreshed research inventories, without changing meaning or executable code |
| Research formatting correction and hash/link recheck | PASS | 45 hard breaks across 10 files changed to explicit line breaks; reverse-hash checks preserved wording/other bytes; 35 hashes and 213 links rechecked |
| Final staged whitespace and base-free project-state validation | PASS | 100 staged files; 23 project Markdown files, 68 project links, 31 requirements, 44 work packages, 96 scenarios, 16 contracts, 25 decisions and one initial cycle |
| Complete staged byte/content/link gate | PASS | All 100 staged files match working bytes; 58 Markdown files and 280 local links; no selected credential/private-source indicators, no imported history |
| Outgoing file/history review and push | PENDING | No publication pass is inferred from preparation |

The included self-check example uses explicitly synthetic source references
and decisions. It is not an approved real task or evidence of live source
coverage. An actual independent reviewer must inspect its exact current context;
an earlier private verdict is not relabeled.

No hosted CI, real provider/model task, installed-host lifecycle, private-source
export, security certification or Corp/Acro acceptance is implied by these checks.

The fresh [validation receipt](engineering/evidence/CLEAN_PUBLICATION_VALIDATION_20261111.json)
keeps scopes, profile digests, skips and the corrected documentation assertion.
The first indicator/structure checks do not replace the final staged/history
review and exact remote verification.

The two skipped methods in `test_native_knowledge.py` require independently
authorized synthetic symlink creation. Metadata fixtures do not replace actual
link coverage, and no privilege workaround was attempted.

Repository `.gitattributes` preserves authored bytes, so reviewed source/research
hashes do not silently change through checkout newline conversion. No global
Git configuration or credentials were changed.
