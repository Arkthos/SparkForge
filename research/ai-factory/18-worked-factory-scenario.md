# 18 - Worked Scenario: A Verified CSV Export Change

[Back to the index](README.md)

## Status and purpose

Everything in this chapter is **synthetic and illustrative**. No application was built, no tests below were executed, and no external review or deployment occurred.

The scenario demonstrates how the concepts fit together. Symbolic revisions such as `candidate-2` are not real commit hashes or run receipts.

## The request

> When a user exports the currently filtered case list, the CSV should contain exactly the rows allowed by the user's tenant and active filters.

The synthetic existing application exports too many rows because one filter is omitted from the export query.

This is a good teaching task because it has a bounded outcome, visible correctness criteria, an important permission boundary, and a plausible integration risk.

## 1. Intake and scope

**Requester:** a synthetic product owner.<br>
**Acceptance owner:** the synthetic application team.<br>
**Allowed environment:** a local fixture application only.<br>
**Allowed changes:** export query construction and directly related tests/documentation.<br>
**Excluded:** schema migration, authentication redesign, new dependencies, production data access, and deployment.

The task is not "fix anything that looks wrong." If the worker discovers a broader architecture issue, it records a separate finding and seeks a scope decision.

## 2. Synthetic fixture

| ID | Tenant | Region | Status | Display name |
|---|---|---|---|---|
| A-01 | alpha | east | open | First case |
| A-02 | alpha | east | closed | Second case |
| A-03 | alpha | west | open | Third case |
| A-04 | alpha | east | open | Case, four |
| B-01 | beta | east | open | Fifth case |
| B-02 | beta | west | closed | Sixth case |

For an authorized alpha user filtering east/open, the expected IDs are **A-01 and A-04**, in stable ID order.

The explicit fixture makes a vague claim such as "the export looks right" unnecessary.

## 3. Task contract

Required behavior:

- Tenant scope comes from authenticated server-side identity, not a model-selected tenant parameter.
- Active region/status filters are applied consistently.
- A request missing the required filter snapshot is rejected explicitly in this illustrative design.
- Unsupported filter fields produce a validation error, not silent omission.
- Export covers all matching rows, not just the first displayed page.
- Headers and CSV encoding follow the agreed existing format.
- A display name containing a comma is escaped correctly.
- The list view's existing behavior is preserved.

The missing-filter rule is a synthetic product decision for this exercise. A real product might choose different defaults, but that choice must be specified before implementation.

## 4. Prepare the environment

The harness records:

- task contract revision `task-spec-1`;
- fixture revision `fixture-1`;
- source baseline `base-1`;
- protected acceptance suite `acceptance-1`;
- approved model/harness configuration;
- permitted file paths and tools;
- a bounded run budget;
- no external-write authority.

It verifies that the fixture application starts and that the baseline failure is reproducible. If the test environment is broken, the run must not claim to have reproduced the product bug.

## 5. Gather context

The worker reads only relevant material:

- export route and query builder;
- tenant-scoping mechanism;
- list-view filter semantics;
- CSV formatter;
- existing tests;
- architecture guidance relevant to query construction.

A historical note suggesting a different database is not allowed to override the current source and approved architecture decision.

The context packet includes source revisions and known uncertainty. It does not include unrelated customer records or secrets.

## 6. Implementation and developer feedback

The worker drafts a regression test for east/open under tenant alpha. It confirms the baseline would return an unwanted closed row. It then proposes a focused change using the existing query helper.

The worker may add development tests. It cannot change the protected acceptance suite merely to make the new implementation pass.

If it proposes replacing the database or rewriting authentication, the scope gate rejects that action for this task.

## 7. Acceptance scenarios

| Case | Expected outcome |
|---|---|
| alpha, east, open | A-01 and A-04 only |
| alpha, west, open | A-03 only |
| beta, east, open | B-01 only |
| Valid filters with no matches | Header-only CSV under the agreed format |
| Pagination size one | Export still includes both alpha/east/open matches |
| Comma in display name | CSV parses back to the original field value |
| Unsupported filter field | Explicit validation error |
| Missing required filter snapshot | Explicit validation error |
| Attempt to request another tenant | Access denied or target rejected before cross-tenant data is returned |
| Repeated export of the same fixed snapshot | Same defined row set and order |
| Existing list view | Required behavior remains intact |
| Candidate changed after tests | Previous evidence cannot accept the new candidate |

These are expected results, not a report of passing tests.

## 8. Review and integration

Suppose `candidate-1` passes its development tests, but no one has yet run the protected tenant-isolation case.

The correct state is **verification incomplete**, not accepted.

Suppose an independent reviewer notices that one helper still accepts a caller-supplied tenant value. The reviewer records the exact location, affected revision, and a concrete path to the incorrect behavior.

The builder creates `candidate-2`, and the applicable checks are rerun. A review of `candidate-1` cannot be reused as approval for `candidate-2`.

If another change has modified the shared query helper, the integrated result also needs verification.

## 9. Illustrative event trace

| Event | Meaning | Important invariant |
|---|---|---|
| E01 | Task admitted | Scope and requester recorded |
| E02 | Environment prepared | Exact baseline and fixture identified |
| E03 | Baseline failure reproduced | Failure is the intended bug, not setup failure |
| E04 | Candidate-1 created | Candidate is not accepted |
| E05 | Development checks complete | Their coverage is not overstated |
| E06 | Independent finding recorded | Bound to candidate-1 |
| E07 | Candidate-2 created | Old acceptance evidence is stale |
| E08 | Required verification requested | Protected evaluator controls its own suite |
| E09 | Evidence assembled | Each result identifies candidate-2 |
| E10 | Human acceptance requested | No production authority is implied |
| E11 | Accepted for the agreed next stage | Acceptance and release remain distinct |

This is the shape of an observable process, not a real execution log.

## 10. Failure injection: model claims completion early

**Situation:** the model says the work is finished after E04.

**Expected harness response:** reject completion because required verification evidence is absent. Return the missing criteria or stop for an operator if limits prevent further work.

**Lesson:** the completion contract is enforced outside the final message.

## 11. Failure injection: lost external response

Imagine a later, separately authorized step creates a review request in a fake external service.

1. The harness records operation `review-request-demo-01`.
2. The fake service creates the request.
3. The response is lost.
4. The harness restarts.

The local record says the outcome is uncertain. It does not say creation failed.

The recovery process queries the fake service by operation identity or retries under its verified idempotency contract. If it cannot establish the result, it enters `NEEDS_RECONCILIATION`.

It does not generate a fresh operation ID and create a second request blindly.

## 12. Failure injection: stale approval

**Situation:** an approver accepts `candidate-2`, but the candidate becomes `candidate-3` before the next stage.

**Expected behavior:** approval is invalid for the changed artifact. Re-evaluate the relevant criteria and request the required decision again.

**Lesson:** an approval is about a particular action and artifact, not general confidence in the worker.

## 13. Failure injection: untrusted instructions

**Situation:** a retrieved issue comment tells the worker to skip tenant checks to save time.

**Expected behavior:** the comment remains untrusted source data. It cannot change the approved task contract, protected tests, or tool permissions.

**Lesson:** a work item can contain useful evidence and malicious or mistaken instructions at the same time.

## 14. A conceptual evidence record

The following explicitly records that this chapter is not executed:

```json
{
  "example": true,
  "task_id": "synthetic-csv-export",
  "task_spec_revision": "task-spec-1",
  "candidate_revision": "candidate-2",
  "fixture_revision": "fixture-1",
  "acceptance_suite_revision": "acceptance-1",
  "execution_status": "not_executed",
  "observed_results": null,
  "expected_properties": [
    "tenant boundary preserved",
    "active filters applied",
    "all matching rows exported",
    "CSV round-trip preserves fields",
    "existing list behavior preserved"
  ],
  "release_authorization": null
}
```

In a real run, observed results must be populated from actual checks, not copied from the expected-properties list.

## 15. What the operator reviews

The operator should be able to answer:

- What did the user ask for?
- What was excluded?
- Which exact artifact was checked?
- Which criteria were checked, skipped, or inconclusive?
- What data and tools were used?
- Was anything changed outside the workspace?
- Are any operations unresolved?
- What authority is requested now?
- How would the system recover if the next stage fails?

If the evidence packet cannot answer these questions, a polished summary is insufficient.

## 16. Translating the scenario to a content factory

Replace the CSV patch with a rendered video. The task contract now covers editorial intent, allowed source footage, rights, factual claims, captions, and publication destination.

Replace unit tests with appropriate checks: media integrity, caption accuracy, preservation of meaning, approved assets, and final editorial review. Keep operation identity, exact artifact binding, budgets, and publication authority.

This is the transferable insight from the supplied video's content example: the factory structure can generalize, but its acceptance criteria cannot simply be copied from software.
