# Retry-attempt implementation plan

## Goal and scope

Change only the observable default retry attempt count from 3 to 4 in the fixture
repository. Do not change other behavior and do not release or publish anything.

## Evidence and design

`QaaS.Framework/src/RetryPolicy.cs` defines `RetryPolicy.Attempts` as `3`.
`QaaS.Framework/tests/test_retry_policy.sh` is the focused repository check and
currently asserts the same value. The smallest change is to update the behavioral
test first, observe its failure, then update the property.

## Test-first steps

1. Change `tests/test_retry_policy.sh` to require `Attempts => 4;` and run it to
   observe the expected failure.
2. Change `src/RetryPolicy.cs` so `RetryPolicy.Attempts` returns `4`.
3. Run `bash tests/test_retry_policy.sh` again and require success.
4. Give the plan, final diff, and raw test output to `qaas-verifier`.

## Release impact

No release, tag, package publication, or remote mutation is authorized.
