.PHONY: help install tools verify catalog lint clean

help:
	@echo "Targets:"
	@echo "  install   install skills, commands, engine and workspace"
	@echo "  tools     install the external toolchain (Go + pipx)"
	@echo "  verify    check the installed environment"
	@echo "  catalog   regenerate docs/ARSENAL.md"
	@echo "  lint      shellcheck + python compile"

install:
	./install.sh

tools:
	./install.sh --tools

verify:
	./scripts/verify.sh

catalog:
	python3 scripts/generate_arsenal.py

lint:
	shellcheck install.sh scripts/*.sh
	python3 -m py_compile scripts/*.py config/*.py
	bash -n install.sh scripts/*.sh

clean:
	rm -rf __pycache__ scripts/__pycache__ config/__pycache__
