# Developer Interview and Optional Plugin Policy

Use this protocol after researching codebase facts and before drafting the plan.

## Separate facts from decisions

Research repositories, source, tests, documentation, and graph evidence yourself.
Ask the developer only about choices that materially affect product behavior,
scope, compatibility, architecture, rollout, or risk tolerance.

For each decision round:

1. Map unresolved decisions as a dependency tree.
2. Ask only the current decision frontier; do not ask downstream questions whose
   options depend on an unanswered parent decision.
3. Number every question and include a recommended answer plus its tradeoff.
4. Wait for the developer's answers. Do not silently choose on their behalf.
5. Record each answer as `D-n`, then recompute the next frontier.

Finish by summarizing the outcome, constraints, non-goals, and decisions. Ask the
developer to confirm that shared understanding explicitly. Confirmation of the
interview is not approval of the plan that will be drafted later.

## Grill Me

When Matt Pocock's model-invoked `grilling` skill is already available, use it as
the interview engine. Do not invoke a user-only command wrapper, install the
plugin, or change its settings. The QaaS facts-versus-decisions boundary,
numbered decision record, shared-understanding confirmation, and later approval
gate still apply.

## Ponytail

Use Ponytail only when a Ponytail-provided skill or tool is visible in the current
session and exposes its active minimality level. Do not infer an opaque plugin's
state or change its global mode. If the level cannot be read, use the built-in
minimality sequence and record that fallback:

1. Is a code change required?
2. Can existing QaaS code solve the problem?
3. Can an existing platform capability solve it?
4. Can an already installed dependency solve it?
5. What is the smallest complete diff?

Record rejected alternatives and scope. Minimality must never remove requested
behavior, validation, error handling, security, compatibility, tests,
observability, or required release work.

## Other developer plugins

An already active developer plugin may strengthen discovery, coding, testing, or
review. It is an optional collaborator, not a workflow authority. Never install,
configure, or mutate another plugin, and never allow it to replace QaaS evidence,
repository instructions, independent review, explicit approval, tests,
verification, or release authorization.
