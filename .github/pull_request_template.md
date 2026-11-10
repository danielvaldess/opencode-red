## What does this change?

<!-- One or two sentences. Link the issue if there is one. -->

## Type

- [ ] Bug fix
- [ ] Compatibility fix (OpenCode)
- [ ] New command
- [ ] Installer / toolchain
- [ ] Documentation / template
- [ ] Other

## How was it tested?

<!-- Commands you ran, OpenCode version, OS. Redact anything sensitive. -->

```text
$ ./scripts/verify.sh
```

## Checklist

- [ ] `bash -n install.sh scripts/*.sh` passes
- [ ] `python3 -m py_compile scripts/*.py config/*.py` passes
- [ ] `./scripts/verify.sh` passes
- [ ] `./install.sh --dry-run` works
- [ ] New commands have valid frontmatter and a description
- [ ] `docs/ARSENAL.md` regenerated if skills changed
- [ ] Attribution and licenses are intact
- [ ] No secrets, real targets or personal data
