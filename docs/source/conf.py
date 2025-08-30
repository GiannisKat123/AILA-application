import os
import sys
import inspect
from importlib import import_module
from pathlib import Path
import importlib as il
import inspect
import pathlib as pl

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'AILA-Application'
copyright = '2025, Ioannis Katoikos'
author = 'Ioannis Katoikos'
release = 'v0.1'

# ---- Paths ----
# repo_root = docs/source/../../
REPO_ROOT = Path(__file__).resolve().parents[2]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "autoapi.extension",          # <<< the star
    "sphinx.ext.napoleon",        # Google/NumPy docstrings
    "sphinx.ext.viewcode",        # source links
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx.ext.autosummary",
    "sphinx.ext.linkcode",
]

extensions += [ "myst_parser"]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "linkify",
]

templates_path = ['_templates']
exclude_patterns = []

language = 'English'

html_show_sourcelink = True

# ── AutoAPI (Python backend) ────────────────────────────────────────────────
autoapi_type = "python"
autoapi_dirs = ["../../backend"]
autoapi_add_toctree_entry = True
add_module_names = False
autoapi_keep_files = True
autoapi_python_use_implicit_namespaces = True
autoapi_root = "backend"
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "imported-members",
    "show-source",
]
autoapi_member_order = "bysource"
autoapi_python_class_content = "class"
autoapi_generate_api_docs = True
autoapi_keep_module_path = False
autoapi_ignore = [
    "*__pycache__*",
    "*aila_indices*",
    "*vector_indexes*",
    "*files",
]

# ---- Theme ----
html_theme = "sphinx_rtd_theme"
html_title = project
html_static_path = ["_static"]
html_theme_options = {
    "light_logo": "logo.png",  # if you add one to _static
    "dark_logo": "logo-dark.png",
}

# Allow both .rst and .md sources


# Napoleon (Google/NumPy docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True

def linkcode_resolve(domain, info):
    if domain != 'py':
        return None
    if not info['module']:
        return None
    filename = info['module'].replace('.', '/')
    return f"https://github.com/GiannisKat123/AILA-application/blob/main/{filename}.py"
