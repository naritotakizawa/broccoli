import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, 'broccoli', '__version__.py'), 'r', encoding='utf-8') as f:
    exec(f.read(), about)

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    license=about['__license__'],

    packages=find_packages(),
    install_requires=['pillow'],
    include_package_data=True,
    entry_points={'console_scripts': [
        'mapeditor = broccoli.tool.editor.mapeditor:main',
        'imgeditor = broccoli.tool.editor.imgeditor:main',
    ]},
)
