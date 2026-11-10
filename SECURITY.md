# Security policy

## Authorized use

`opencode-red` installs offensive-security knowledge and tooling. It is intended
only for systems you own or are explicitly authorized to test, and only within
the scope of a bug-bounty program, signed engagement or lab environment.

The maintainers do not support, condone or take responsibility for unauthorized
testing. You are responsible for complying with the law and with each program's
rules.

## Reporting a vulnerability

This repository is code, not a service. If you find a security issue **in this
repository** (installer, scripts, command templates, CI), please report it
privately:

1. Open a [private security advisory](https://github.com/danielvaldess/opencode-red/security/advisories/new)
   on GitHub.
2. Include the affected file, a minimal reproduction, and the impact.
3. Do not open a public issue before a fix is available.

Please do not report vulnerabilities in third-party targets here. Report those to
the target's program or vendor.

## Scope of this policy

In scope:

- the installer and scripts in this repository;
- the command templates and engine overlay;
- CI configuration;
- documentation that could cause a user to test out of scope.

Out of scope:

- vulnerabilities in upstream skill bundles — report them to the upstream project;
- vulnerabilities in third-party tools installed by `install_tools.sh`;
- findings in targets you tested with the arsenal.

## Secrets

The installer does not collect, transmit or store credentials. Do not commit
`.env` files, API keys, cookies or target data. The repository's `.gitignore`
excludes the common cases; CI does not run against external targets.

## No warranty

The software is provided "as is", without warranty of any kind, under the MIT
license. See [LICENSE](LICENSE).
