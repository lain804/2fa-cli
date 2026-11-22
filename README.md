# 2fa-cli

Generate time-based two-factor authentication (TOTP) codes from your terminal.

## Install

Requires Python 3.14 or newer. Run one of these from the repository root.

```sh
python -m pip install .
# or
uv tool install .
```

If your shell can’t find `2fa` after installing with uv, run `uv tool update-shell` and reopen your terminal.

## Use

Replace `BASE32_SECRET` with the setup key from your account.

```sh
2fa add example BASE32_SECRET
2fa get example
2fa list
2fa --help
```

Secrets are NOT encrypted 
They database is stored in `~/.2fa-cli/secrets.db`.
