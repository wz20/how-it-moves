# Security

This repository contains executable Python, JavaScript and HTML. Review any new scene or contributed script before running it. The renderer is not a security sandbox for untrusted code.

- Keep API keys, access tokens, private project data and personal photos outside this repository.
- The included example does not need an API key and makes no model API calls.
- Dependency installation accesses package registries; inspect normal supply-chain risks.
- Run untrusted contributions in an isolated environment without credentials.
- The optional GitHub publication helper uses your local `gh` login. It does not ask for or print tokens. It requires explicit `--public`, checks your login, stages only manifest-listed files and refuses an existing repository. It does not force-push or convert private repositories to public.
- GitHub Pages publishes its configured source to the public web. Verify the contents of `docs/` before enabling it.

Do not paste tokens or exploitable private data into a public issue. Use the maintainer's explicitly available private reporting channel (or GitHub private vulnerability reporting if enabled); public issues should contain sanitized reproduction information only.
