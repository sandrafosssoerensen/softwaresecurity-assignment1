# Pull-request pipeline evidence

Pull request #1 proposes the documentation and evidence branch
`final-evidence-and-docs` for merge into `main`. Jenkins discovered the pull
request and ran the repository pipeline successfully.

[PR-1 build #1](pr-1-build-1/) contains:

- the complete Jenkins console output
- all seven generated analysis and test artifacts
- a GitHub screenshot showing separate `branch` and `pr-head` checks
- a Jenkins screenshot showing **Pull Requests (1)** and successful PR build #1
- a concise record of the source, target, revision, trigger, and result

The console is direct evidence that Jenkins fetched `refs/pull/1/head`, used a
workspace ending in `_PR-1`, checked out commit `434f5df`, archived the reports,
notified GitHub, and finished with `SUCCESS`.
