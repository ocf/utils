.PHONY: test
test: venv
	venv/bin/pre-commit install
	venv/bin/pre-commit run --all-files

.PHONY: package_%
package_%: autoversion
	docker run -e "DIST_UID=$(shell id -u)" -e "DIST_GID=$(shell id -g)" -v $(CURDIR):/mnt:rw "docker.ocf.berkeley.edu/theocf/debian:$*" /mnt/build-in-docker "$*"

dist:
	mkdir -p "$@"

.PHONY: builddeb
builddeb:
	dpkg-buildpackage -us -uc

.PHONY: autoversion
autoversion:
	date +%Y.%m.%d.%H.%M-git`git rev-list -n1 HEAD | cut -b1-8` > .version
	rm -f debian/changelog
	DEBFULLNAME="Open Computing Facility" DEBEMAIL="sm+packages@ocf.berkeley.edu" VISUAL=true \
		dch -v `sed s/-/+/g .version` -D stable --no-force-save-on-release \
		--create --package "ocf-utils" "Package for Debian."

venv: Makefile
	vendor/venv-update \
		venv= venv -ppython3.7 \
		install= -r requirements-dev.txt

.PHONY: clean
clean:
	rm -rf venv debian/*.debhelper debian/*.log dist dist_*
