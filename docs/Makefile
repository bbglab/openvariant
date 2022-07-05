# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build


EXAMPLES_DOCS = ./examples

EXAMPLES_FINDFILES = ../examples/find_files
EXAMPLES_VARIANT = ../examples/variant
EXAMPLES_CAT = ../examples/cat
EXAMPLES_GROUP_BY = ../examples/group_by
EXAMPLES_COUNT = ../examples/count


# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	cp -r $(EXAMPLES_FINDFILES) $(EXAMPLES_DOCS)
	cp -r $(EXAMPLES_VARIANT) $(EXAMPLES_DOCS)
	cp -r $(EXAMPLES_CAT) $(EXAMPLES_DOCS)
	cp -r $(EXAMPLES_GROUP_BY) $(EXAMPLES_DOCS)
	cp -r $(EXAMPLES_COUNT) $(EXAMPLES_DOCS)

	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

