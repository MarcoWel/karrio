from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="karrio.server.manager",
    version="2023.4.1",
    description="Multi-carrier shipping API Shipments manager module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/karrioapi/karrio",
    author="karrio",
    author_email="hello@karrio.io",
    license="Apache-2.0",
    packages=find_namespace_packages(exclude=["tests.*", "tests"]),
    install_requires=[
        "karrio.server.core",
        "django-downloadview",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    zip_safe=False,
)
