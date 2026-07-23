OFFICE = $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
outdir ?= $(OFFICE)/.packages

.PHONY: deb
deb: $(OFFICE)/openvpn3-indicator.control.py
	git log -n 1
	git tag --list
	git describe --tags
	../scripts/semver
	rm -rf $(outdir)
	python3 $< --scriptdir $(OFFICE) --outdir $(outdir)
	find $(outdir) -name "*_source.changes" -exec debsign --no-conf "-mGrzegorz Gutowski Github Actions <grzegorz.gutowski@uj.edu.pl>" --re-sign -S {} ";"
	find $(outdir) -name "*_source.changes" -exec dput -c dput.cf publish {} ";"
