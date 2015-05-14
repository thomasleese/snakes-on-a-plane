import os
import sys

sys.path.insert(0, os.path.abspath('..'))

from xplane import __version__


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon'
]

source_suffix = '.rst'
master_doc = 'index'

project = 'snakes-on-a-plane'
copyright = '2015, Tom Leese'

release = __version__
version = __version__

html_theme = 'alabaster'

intersphinx_mapping = {'http://docs.python.org/': None}
