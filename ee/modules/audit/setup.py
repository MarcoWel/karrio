from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="karrio.server.audit",
    version="2023.1",
    description="Multi-carrier shipping API audit log module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/karrioapi/karrio",
    author="karrio",
    author_email="hello@karrio.io",
    license="Karrio Enterprise License",
    packages=find_namespace_packages(exclude=["tests.*", "tests"]),
    install_requires=[
        "django-auditlog",
        "karrio.server.core",
        "karrio.server.graph",
        "karrio.server.cloud",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    zip_safe=False,
    include_package_data=True,
)
