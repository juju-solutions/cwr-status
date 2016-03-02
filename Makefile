clean:
	find . -name '*.pyc' -delete

test: check_deps
	INI=test.ini cwr_venv/bin/nosetests

install_deps:
	./scripts/install_deps.sh

check_deps:
	./scripts/check_deps.sh
