# Jenkins configuration evidence

The screenshots in this folder document the multibranch pipeline setup:

- [GitHub repository source](the-multibranch-GitHub-repository-source.png)
  shows the private repository URL, masked Jenkins credential, discovery of all
  branches, discovery of pull requests from the repository, and discovery of
  pull requests from forks.
- [Jenkinsfile configuration](the-Jenkinsfile-script-path.png) shows that each
  discovered branch or pull request is built from the repository's
  `Jenkinsfile`.
- [Periodic repository scan](periodic-repository-scan.png) shows the five-minute
  fallback scan. This allows Jenkins to discover repository changes if a
  webhook event is delayed or unavailable.
- [Multibranch overview](the-branch-overview-containing-the-five-relevant-branches.png)
  shows the five relevant branches and their expected green or red outcomes.
- [Archived artifact overview](assignment-work-artifacts-overview.png) shows
  that Jenkins exposes the saved static-analysis, dependency-analysis, and
  test reports for a successful branch build.

No access token is visible. Jenkins displays only the masked credential name.
The separate build console evidence records automatic branch indexing and
GitHub build-status notification.
