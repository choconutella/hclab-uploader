from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '3.1.0'
DESCRIPTION = 'HCLAB Uploader'

# Setting up
setup(
    name="hclab-python",
    version=VERSION,
    author="ANO (Adhil Novandri)",
    author_email="<adhil.nvndr@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['cx_Oracle', 'PyPDF2', 'sqlalchemy', 'requests', 'pystray'],
    keywords=['python', 'hclab', 'uploader', 'email'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)