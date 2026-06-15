# AntigravityQB Assessment and Budget Notes

AntigravityQB should assess more than calendar effort.

## Assessment Dimensions

During Step 1 intake and planning, capture or infer:

- planning horizon and urgency;
- desired autonomy level;
- human review cadence;
- repository maturity;
- live dependency readiness;
- security/compliance strictness;
- validation strength;
- expected Antigravity task run size;
- rough token/context pressure;
- whether helper agents are useful or overkill.

## Token and Usage Estimates

AntigravityQB may provide rough token/context estimates, but must not pretend they are exact.

Use qualitative bands unless the user provides a concrete budget:

- Low: small repo, few phases, little generated text, limited helper agent use.
- Medium: moderate repo, many sub-plans, Step 3 audit, limited Step 4 work.
- High: large repo, Autopsy + ontology + many phases + helper agents + implementation queue.

If the user provides a weekly/monthly token or usage budget, estimate whether the planned run is likely to consume a small, moderate, or large share of that budget. Do not invent percentages without a user-provided budget baseline.

## Antigravity task Estimate

For each Antigravity task handoff, include:

- expected work shape;
- validation checkpoints;
- stop gates;
- token/context risk;
- whether helper agents are recommended.
