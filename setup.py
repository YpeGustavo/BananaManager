from setuptools import setup, find_packages

setup(
    name="banana",
    version="0.0.1",
    author="Gustavo Furtado",
    author_email="gustavofurtado2@gmail.com",
    description="Ready-to-go web app for end-users to interact with tables in a database.",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["dash", "pydantic", "pandas", "sqlalchemy", "pyyaml"],
)
