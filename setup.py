import pathlib
from setuptools import setup
from setuptools import find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="orthogonal",
    version="1.1.6",
    description="Orthogonal Graph Layout for Python 3",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/hasii2011/OrthogonalDrawing",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['networkx']
)
