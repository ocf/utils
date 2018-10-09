.PHONY: test
test: venv
	venv/bin/pre-commit install
	venv/bin/pre-commit run --all-files

.PHONY: builddeb
builddeb: autoversion
	dpkg-buildpackage -us -uc

.PHONY: autoversion
autoversion:
	date +%Y.%m.%d.%H.%M-git`git rev-list -n1 HEAD | cut -b1-8` > .version
	rm -f debian/changelog
	DEBFULLNAME="Open Computing Facility" DEBEMAIL="help@ocf.berkeley.edu" VISUAL=true \
		dch -v `sed s/-/+/g .version` -D stable --no-force-save-on-release \
		--create --package "ocf-utils" "Package for Debian."

venv: Makefile
	vendor/venv-update \
		venv= venv -ppython3.7 \
		install= -r requirements-dev.txt

.PHONY: clean
clean:
	rm -rf venv
	rm -rf debian/*.debhelper debian/*.log dist dist_*


