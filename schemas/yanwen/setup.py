"""Warning: This setup.py is only there for git install until poetry support git subdirectory"""

from setuptools import setup, find_packages

setup(
    name="carrier.yanwen",
    version="0.0.0-dev",
    license="Apache-2.0",
    packages=find_packages(),
    install_requires=["jstruct"],
    zip_safe=False,
)
