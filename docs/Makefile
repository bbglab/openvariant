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
EXAMPLES_TASKS = ../examples/tasks
EXAMPLES_CLI = ../examples/cli
EXAMPLES_PLUGIN_SYS = ../examples/plugin_system

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	cp -r $(EXAMPLES_FINDFILES) $(EXAMPLES_DOCS)
	cp -r $(EXAMPLES_VARIANT) $(EXAMPLES_DOCS)
	cp -r $(EXAMPLES_TASKS) $(EXAMPLES_DOCS)
	cp -r $(EXAMPLES_CLI) $(EXAMPLES_DOCS)
	cp -r $(EXAMPLES_PLUGIN_SYS) $(EXAMPLES_DOCS)

	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

