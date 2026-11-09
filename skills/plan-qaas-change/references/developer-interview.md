# Developer Interview and Provider Policy

Use this protocol after researching codebase facts and before drafting the plan.

## Separate facts from decisions

Research repositories, source, tests, documentation, and graph evidence yourself.
Ask the developer only about choices that materially affect product behavior,
scope, compatibility, architecture, rollout, or risk tolerance.

Invoke the exact Skill `mattpocock-skills:grilling` as the interview engine.
Follow its interview procedure while keeping QaaS responsible for the
facts-versus-decisions boundary and the persisted decision record. Number each
developer-owned question, include a recommendation and tradeoff, wait for the
answer, and record it as `D-n`; do not silently choose on the developer's behalf.

After a successful invocation, emit exactly:

`Provider: mattpocock-skills:grilling — SUCCEEDED`

If the Skill cannot be invoked after QaaS has loaded, emit
`BLOCKED_PROVIDER: mattpocock-skills:grilling — cause` and stop. Do not draft a
plan, invoke a downstream agent, or substitute a QaaS-owned interview algorithm.

Finish by summarizing the outcome, constraints, non-goals, and decisions. Ask the
developer to confirm that shared understanding explicitly. Confirmation of the
interview is not approval of the plan that will be drafted later.

Do not invoke a user-only command wrapper, install a provider, or change provider
settings. The QaaS shared-understanding confirmation and later approval gate
remain mandatory.

## Other developer plugins

Other provider capabilities may strengthen discovery, coding, testing, or
review, but never replace QaaS evidence, repository instructions, independent
review, explicit approval, tests, verification, or release authorization.
