.PHONY: check export-sanitized

check:
	bash scripts/validate.sh

export-sanitized:
	git diff --quiet
	git diff --cached --quiet
	git archive --format=zip --prefix=AntigravityQB/ --output AntigravityQB-sanitized.zip HEAD
