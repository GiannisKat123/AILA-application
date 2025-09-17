# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os, sys, inspect, pathlib, posixpath

project = 'AILA'
copyright = '2025, Ioannis Katoikos'
author = 'Ioannis Katoikos'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",          # Markdown support
    "sphinx.ext.autodoc",   # Pull docstrings from Python
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",  # Google/NumPy docstrings
    "sphinx.ext.viewcode",  # Source links
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "sphinx.ext.linkcode",   # <-- add this,
]

GITHUB_ORG_REPO = os.environ.get("GITHUB_REPOSITORY", "ORG/REPO")  # e.g., "my-org/my-repo"
GIT_REF = os.environ.get("GITHUB_SHA", "main")
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))              # repo root on sys.path
sys.path.insert(0, str(REPO_ROOT / "backend"))  
# autosummary_generate = True

def _get_source_info(obj):
    try:
        fn = inspect.getsourcefile(obj) or inspect.getfile(obj)
        fn = pathlib.Path(fn).resolve()
        if not str(fn).startswith(str(REPO_ROOT)):
            return None, None, None
        rel = fn.relative_to(REPO_ROOT).as_posix()

        source, start = inspect.getsourcelines(obj)
        end = start + len(source) - 1
        return rel, start, end
    except Exception:
        return None, None, None

def linkcode_resolve(domain, info):
    """
    Map Python API docs to GitHub source:
    https://github.com/<org>/<repo>/blob/<ref>/<path>#L<start>-L<end>
    """
    if domain != "py" or not info.get("module"):
        return None
    modname = info["module"]
    fullname = info.get("fullname")
    subobj = None

    try:
        mod = __import__(modname, fromlist=["dummy"])
        obj = mod
        for part in (fullname or "").split("."):
            subobj = getattr(obj, part)
            obj = subobj
    except Exception:
        subobj = None

    if subobj is None:
        return None

    rel, start, end = _get_source_info(subobj)
    if not rel:
        return None

    lines = f"#L{start}-L{end}" if start and end else ""
    return f"https://github.com/{GITHUB_ORG_REPO}/blob/{GIT_REF}/{rel}{lines}"

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}


# --- Mock imports that are optional/heavy ---
autodoc_mock_imports = [
    "sentence_transformers",
    "openai",
    "jose",
    # add any other runtime-only deps you see errors for:
    # "sqlalchemy", "psycopg2", "alembic", "pinecone", "uvicorn", etc.
]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}


myst_enable_extensions = [
    "colon_fence",          # ::: fenced blocks
    "deflist",              # definition lists
    "linkify",              # auto link URLs
    "substitution",         # substitutions
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    # TypeDoc dumps can be large; keep only what you need
]

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
}

html_static_path = ["_static"]

autodoc_mock_imports = [
    "fastapi", "uvicorn", "sqlalchemy", "pydantic", "redis", "pymongo",
    # add any others your backend imports but you don't want to install in CI
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

