# rpm
RPM packaging specs for Fedora Copr.

## Automated release updates

The `Update monitored release` workflow accepts a `repository_dispatch` event
named `anitya-release`, or a manual run with `package` and `version` inputs.
It updates RPM versions, resets explicit releases to `1%{?dist}`, adds changelog
entries where needed, commits the change, and calls the existing Copr workflow
with the exact pushed commit. Duplicate and older versions are skipped using RPM
version ordering. Aegisub keeps `%autorelease` and `%autochangelog`.
Updates run one at a time, with up to 100 pending runs queued through
[GitHub's concurrency queue](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency).

| Package | Target branch | Specs updated |
| --- | --- | --- |
| `zotero` | `master` | `zotero/zotero.spec` |
| `xpadneo` | `master` | Both xpadneo and xpadneo-kmod specs |
| `aegisub` | `aegisub-next` | `aegisub/aegisub.spec` |

Versions may have a leading `v`. Zotero and xpadneo accept dotted numeric stable
versions; Aegisub also accepts `-alpha`, `-beta`, and `-rc` suffixes with optional
numbers, converting the hyphen to RPM's `~` prerelease separator.

### Connect Anitya

[Anitya publishes release notifications through Fedora Messaging](https://github.com/fedora-infra/anitya#readme).
A notification consumer must select the intended Anitya project IDs, map them to
the package names above, and send the desired release version to GitHub's
[repository dispatch API](https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event):

```json
{
  "event_type": "anitya-release",
  "client_payload": {
    "package": "zotero",
    "version": "9.0.5"
  }
}
```

For example, with an authenticated GitHub CLI session:

```sh
gh api --method POST repos/OWNER/REPO/dispatches --input - <<'JSON'
{
  "event_type": "anitya-release",
  "client_payload": {"package": "zotero", "version": "9.0.5"}
}
JSON
```

Install these workflow changes and `.github/scripts/update_release.py` on the
repository's default branch before sending events. The sender needs a token with
repository Contents write permission. The workflow uses its own `GITHUB_TOKEN`
to push; repository rules must permit those pushes to the target branches.
Configure the existing `COPR_CLI_CONFIG` secret for builds.

If a push fails due to a concurrent branch update, rerun the workflow.
If a build fails after a successful push, rerun the failed jobs
in that run so they retain the committed SHA; resending the same version skips the
update and build.

### Local validation

With Python's RPM bindings installed (`python3-rpm` on Ubuntu):

```sh
python3 -B -m unittest discover -s .github/scripts -p 'test_*.py' -v
actionlint -ignore 'unexpected key "queue" for "concurrency" section'
```

Actionlint 1.7.12 does not yet recognize GitHub's documented `queue` property;
the command excludes only that diagnostic.
