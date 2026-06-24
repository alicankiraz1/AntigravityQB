.PHONY: check export-sanitized

check:
	bash scripts/validate.sh

export-sanitized:
	python3 scripts/export_sanitized.py
