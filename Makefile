clean:
	find . -name '*.pyc' -delete

test: check_deps
	INI=testing venv/bin/nosetests --nocapture -v -w $(shell pwd)/cwrstatus

install_deps:
	./scripts/install_deps.sh

check_deps:
	./scripts/check_deps.sh

lint:
	venv/bin/flake8 cwrstatus
