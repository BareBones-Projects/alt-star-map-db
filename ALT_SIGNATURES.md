# ALT notices, HEX selectors and signing

This package adds reviewable first-party source header/footer notices and a manually triggered GitHub Actions workflow that opens a follow-up PR. The two ALT tags identify copyright notice blocks. They are selection markers, not evidence of a cryptographic signature. No private keys or BareMark certification claims are generated.

## Configure and propose

After merging, run **ALT signed notices** in Actions with the copyright holder and BareMark ID. It updates `.alt-signatures.json`, applies notices and opens a PR in that repository. Repeat for each ALT repository. Actions must be allowed to create PRs in repository settings. See [GitHub workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) for manual inputs and token permissions. PR CI may require maintainer approval for a bot-created PR.

Locally, edit `.alt-signatures.json`, then run:

```sh
python3 tools/alt_signatures.py apply
python3 tools/alt_signatures.py check
python3 -m unittest discover -s tests -p test_alt_signatures.py
```

The explicit file list covers existing first-party source files with supported comment syntax; README is included for repositories with no source. Add new source paths to the list as they are created. Generated files, dependencies, JSON, binary assets and LICENSE/NOTICE files are excluded. Existing licenses still apply; this does not change their terms. Notices are source comments, not visible page widgets. Review the supplied all-rights-reserved wording against repository licensing before merging. Both header and footer use the supplied notice, since no separate footer text was supplied.

## Select code with custom tags

- `@ALT_HEADER_SIGNED`
- `@ALT_FOOT_SIGNED`
- `@HEX_{bareID_INPUT_HERE}_SIDEBAR`
- `@HEX_{bareID_INPUT_HERE}_BODY`
- `@HEX_{bareID_INPUT_HERE}_FRAME`
- `@HEX_{bareID_INPUT_HERE}_HEADER`
- `@HEX_{bareID_INPUT_HERE}_FOOTER`
- `@HEX_{bareID_INPUT_HERE}_SQUARE`
- `@HEX_{bareID_INPUT_HERE}_RECTANGLE`
- `@HEX_{bareID_INPUT_HERE}_VERTICAL`
- `@HEX_{bareID_INPUT_HERE}_BANNER`
- `@HEX_{bareID_INPUT_HERE}_ICON_01` through `@HEX_{bareID_INPUT_HERE}_ICON_07`

Replace `{bareID_INPUT_HERE}` with the configured ID; the initial literal placeholder is `bareID_INPUT_HERE` without braces. IDs allow letters, digits, `_` and `-`. These are project-level selectors, not globally installed editor @ mentions.

Render a selected trusted snippet, optionally adding Shroud boundaries:

```sh
python3 tools/alt_signatures.py render --tag @HEX_ABC_BODY --snippet snippets/body.html --shroud
```

Render without `--snippet` to obtain an empty slot. Place that START/END pair at the intended HTML location, then insert or replace its content:

```sh
python3 tools/alt_signatures.py inject --tag @HEX_ABC_BODY --target index.html --snippet snippets/body.html --shroud
```

Only configured HTML targets containing one matching slot are accepted. Repeating injection replaces that slot. `--shroud` emits `@BAREMARK_SHROUD_START` and `@BAREMARK_SHROUD_END` comments; it is off by default. These boundaries are an integration convention pending actual BareMark Shroud code. They do not hide content, certify it, alter crawler behavior or guarantee SEO outcomes. Only inject reviewed first-party HTML/SEO snippets; code is inserted verbatim. Commit snippets and injected HTML on a review branch and open a PR.

## Actual digital signatures

Use an existing trusted RSA signing identity and OpenSSL. Keep the private key outside the repository. Set a real holder and BareMark ID before signing:

```sh
python3 tools/alt_signatures.py sign --key /secure/location/private.pem
python3 tools/alt_signatures.py verify --key /trusted/location/public.pem
```

Signing writes `.alt-signature-manifest.json` and its detached binary `.sig`. SHA-256 covers the exact bytes of configured files plus configuration. Commit both outputs; publish the trusted public key through an independently trusted channel. Verification rejects changes to content or the covered file list. Files outside that list are not covered. Re-sign after changes, including snippet insertion. CI checks notice consistency; it does not assert certificate verification without a configured trust root. Private-key operations are intentionally local and are not performed on PR code.

`@BAREMARK_VERIFIED_PENDING` remains in notice blocks because the current BareMark backend has no implemented certificate issuer/verification integration. A successful OpenSSL verification proves consistency under the supplied public key; it is not a BareMark Verified certificate. Connect the official certificate verification service and define its trust policy before showing a Verified badge.
