# Source inputs are staged by sources/stage-release.py before RPM parsing.
Source900: ../zotero.spec#/zotero-common.inc
# The submission selects the target; Fedora-review initially parses on its host.
%include %{SOURCE900}
