# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#conda
import os
import sys

import openvariant
from pybtex.plugin import register_plugin
from pybtex.style.formatting.unsrt import Style as UnsrtStyle
from pybtex.style.labels.alpha import BaseLabelStyle

sys.path.insert(0, os.path.abspath('../'))

# -- Project information -----------------------------------------------------

project = 'OpenVariant'
copyright = '2022, BBGLab - Barcelona Biomedical Genomics Lab'
author = 'BBGLab - Barcelona Biomedical Genomics Lab'

# The full version, including alpha/beta/rc tags

release = openvariant.__version__

html_last_updated_fmt = "%d %b %Y"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'sphinx.ext.coverage', 'sphinx.ext.napoleon',
              'sphinx_copybutton', 'sphinxcontrib.autoyaml', 'sphinx.ext.autosectionlabel', 'sphinx_panels', 'nbsphinx',
              'sphinx_gallery.load_style', 'sphinxcontrib.bibtex']


numpydoc_show_class_members = False
autosectionlabel_prefix_document = True
panels_add_bootstrap_css = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '_templates', 
                    '**.ipynb_checkpoints']

# -- Bibtex configuration ---------------------------------------------------

bibtex_bibfiles = ["refs.bib"]

class MyLabelStyle(BaseLabelStyle):
    def format_labels(self, sorted_entries):
        for entry in sorted_entries:
            yield entry.key

class MyStyle(UnsrtStyle):
    default_label_style = MyLabelStyle


register_plugin("pybtex.style.formatting", "mystyle", MyStyle)

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pydata_sphinx_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_css_files = [
    'openvariant.css',
]

html_context = {
    "github_user": "bbglab",
    "github_repo": "https://github.com/bbglab/openvariant",
    "github_version": "",
    "doc_path": "",
    "default_mode": "light"
}

html_theme_options = {
    'use_edit_page_button': True,
    "show_nav_level": 4,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/bbglab/openvariant",
            "icon": "fab fa-github",
        },
        {
            "name": "Twitter",
            "url": "https://twitter.com/bbglab",
            "icon": "fab fa-twitter",
        }
    ],
}

nbsphinx_thumbnails = {
    'examples/find_files/find_files_with_directory_path': './_static/examples_thumbnails/find_files_folder.png',
    'examples/find_files/find_files_with_file_path': './_static/examples_thumbnails/find_files_file.png',
    'examples/variant/read': './_static/examples_thumbnails/read.png',
    'examples/variant/save': './_static/examples_thumbnails/save.png',
    'examples/tasks/cat': './_static/examples_thumbnails/cat_task.png',
    'examples/tasks/count': './_static/examples_thumbnails/count_task.png',
    'examples/tasks/group_by': './_static/examples_thumbnails/group_by_task.png',
    'examples/cli/introduction_cli': './_static/examples_thumbnails/introduction_cli.png',
    'examples/cli/main_cli': './_static/examples_thumbnails/main_cli.png',
    'examples/plugin_system/plugin_system': './_static/examples_thumbnails/plugin_example.png',
}

nbsphinx_input_prompt = '[%s] - '

html_title = 'OpenVariant'
html_favicon = './_static/favicon_openvariant.ico'

html_use_opensearch = 'False'

html_logo = "./_static/title.png"

language = "en"


