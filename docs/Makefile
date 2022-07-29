# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build


EXAMPLES_FINDFILES_DR = ./examples/find_files
EXAMPLES_FINDFILES = ../examples/find_files/*.ipynb

EXAMPLES_VARIANT_DR = ./examples/variant
EXAMPLES_VARIANT = ../examples/variant/*.ipynb

EXAMPLES_TASKS_DR = ./examples/tasks
EXAMPLES_TASKS = ../examples/tasks/*.ipynb

EXAMPLES_CLI_DR = ./examples/cli
EXAMPLES_CLI = ../examples/cli/*.ipynb

EXAMPLES_PLUGIN_SYS_DR = ./examples/plugin_system
EXAMPLES_PLUGIN_SYS = ../examples/plugin_system/*.ipynb

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	mkdir -p $(EXAMPLES_FINDFILES_DR)
	cp -r $(EXAMPLES_FINDFILES) $(EXAMPLES_FINDFILES_DR)
	mkdir -p $(EXAMPLES_VARIANT_DR)
	cp -r $(EXAMPLES_VARIANT) $(EXAMPLES_VARIANT_DR)
	mkdir -p $(EXAMPLES_TASKS_DR)
	cp -r $(EXAMPLES_TASKS) $(EXAMPLES_TASKS_DR)
	mkdir -p $(EXAMPLES_CLI_DR)
	cp -r $(EXAMPLES_CLI) $(EXAMPLES_CLI_DR)
	mkdir -p $(EXAMPLES_PLUGIN_SYS_DR)
	cp -r $(EXAMPLES_PLUGIN_SYS) $(EXAMPLES_PLUGIN_SYS_DR)

	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

