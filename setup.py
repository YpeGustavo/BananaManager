from os import path
from setuptools import setup, find_packages


def get_long_description() -> str:
    this_directory = path.abspath(path.dirname(__file__))
    with open(path.join(this_directory, "README.md"), encoding="utf-8") as file:
        return file.read()


def get_version() -> str:
    with open("banana/__init__.py") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("__version__"):
                return line.split('"')[1]
        raise RuntimeError("Version not found.")


setup(
    name="banana-manager",
    version=get_version(),
    author="Gustavo Furtado",
    author_email="gustavofurtado2@gmail.com",
    description="Ready-to-go web app for end-users to interact with tables in a database.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["dash-ag-grid", "pydantic", "pyyaml", "Flask-SQLAlchemy"],
    url="https://github.com/GusFurtado/BananaManager",
)
