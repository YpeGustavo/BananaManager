import yaml


with open(r"C:\Users\gusta\Repositórios\Cadastro\config.yaml", "r") as file:
    CONFIG = yaml.safe_load(file)
    print(CONFIG)

with open(r"C:\Users\gusta\Repositórios\Cadastro\tables.yaml", "r") as file:
    TABLES = yaml.safe_load(file)
    print(TABLES)
