# 🍌 Banana Manager

Welcome to **Banana Manager**! Banana Manager is a Python package designed to connect to a database and create a simple web app that displays and allows updates to selected tables. This tool is perfect for non-technical end-users who need to interact with database tables without using complex DBA tools.


## Powered by

- **[Dash](https://dash.plotly.com/) and [AG Grid](https://www.ag-grid.com/)**: User-friendly, intuitive, and interactive web interface with powerful table displays and editing capabilities.
- **[Pydantic](https://pydantic-docs.helpmanual.io/) and [YAML](https://yaml.org/)**: Fast and accurate data handling and configuration.
- **[SQLAlchemy](https://www.sqlalchemy.org/)**: Secure, efficient, and flexible database operations for multiple database backends.


## Installation

To install Banana Manager, simply use pip:

```bash
pip install banana-manager
```

Also, remember to install the appropriate database connector for your project, like `pyodbc` or `psycopg2`. If you’re unsure, SQLAlchemy will inform you when you load your application.

Additionally, consider installing a production server like `waitress`:

```bash
pip install waitress
```

## Getting started

At the end of this tutorial, you’ll have a folder structure similar to the following:

```
my_manager
    └─ app.py
    └─ config.yaml
    └─ my_tables
            └─ my_group_of_tables.yaml
            └─ another_group_of_tables.yaml
```

### Configuring the Manager

Create a `config.yaml` file in the root folder of your project with the following structure:

```yaml
connection:
  drivername: <optional str>
  username: <optional str>
  password: <optional str>
  host: <optional str>
  port: <optional str>
  database: <optional str>
dataPath: "data"
tablePaths: ["tables"]
title: "Banana Database Manager"
theme: <optional str>
defaultColDef: <optional dict>
defaultGridOptions: <optional dict>
```

- **connection** *(dict)* : This will create a [SQLAlchemy URL](https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.engine.URL) object. See the section [Dialets](https://docs.sqlalchemy.org/en/20/dialects/) for more information about the appropriate driver.
- **dataPath** *(str, default="data")* : The folder where the app data files will be stored.
- **tablePaths** *(list[str], default=["tables"])* : List of folder where the table models YAML files are stored.
- **title** *(str, default="Banana Database Manager")* : HTML header title attribute.
- **theme** *(str, default="cyan")* : One of the [default Mantine colors](https://mantine.dev/theming/colors/#default-colors).
- **defaultColDef** *(dict[str, Any])* : [AG Grid column properties](https://www.ag-grid.com/angular-data-grid/column-properties/).
- **defaultGridOptions** *(dict[str, Any])* : [AG Grid options](https://www.ag-grid.com/react-data-grid/grid-options/).

### Defining the tables

The tables can be defined using YAML files located in the folders specified in the `config.yaml`. If no folder is specified, create a new folder named "tables" in the root folder.

Each YAML file represents a group containing a list of tables. Here’s the structure:

```yaml
group_name: <optional string>
display_order: <optional integer>
tables:
  - name: <string>
    schema_name: <optional string>
    display_name: <optional string>
    primary_key:
      name: <string>
      display_name: <optional string>
      columnDef: <optional dict>
    columns:
      - name: <string>
        display_name: <optional string>
        foreign_key: (optional)
          table_name: <string>
          schema_name: <optional string>
          column_name: <string>
          column_display: <string>
          order_by: (optional)
            - column: <string>
              desc: <optional bool>
        columnDef: <optional dict>
      - <other columns>
    order_by: (optional)
      - column: <string>
        desc: <optional bool>
      - <other columns>
    limit: <optional int>
    defaultColDef: <optional dict>
    gridOptions: <optional dict>

  - <other tables>
```

#### Group configuration

- **group_name** *(str, optional)* : Name of the group that will be displayed in the side menu.
- **display_order** *(int, optional)* : Order which the groups will be stacked in the side menu.
- **tables** *(list)* : List of table configurations.

#### Table configuration

- **name** *(str)* : Name of the table in the database.
- **schema_name** *(str, optional)* : Schema where the table is located in the database.
- **display_name** : *(str, optional)* : Name that will be displayed at the side menu.
- **primary_key** *(dict)* : Primary key configuration.
- **columns** *(list)* : List of column configurations.
- **order_by** *(list[dict])* : Default ordering of the table rows.
- **limit** *(int)* : Maximum of rows returned after order by.
- **defaultColDef** *(dict[str, Any])* : [AG Grid column properties](https://www.ag-grid.com/angular-data-grid/column-properties/).
- **gridOptions** *(dict[str, Any])* : [AG Grid options](https://www.ag-grid.com/react-data-grid/grid-options/).

#### Primary key configuration

- **name** *(str)* : Name of the column in the database that will be used as primary key.
- **display_name** *(str, optional)* : Name that will be displayed in the table.
- **columnDef** *(dict[str, Any])* : [AG Grid column properties](https://www.ag-grid.com/angular-data-grid/column-properties/).

#### Order by configuration

- **column** *(str)* : Name of the column
- **desc** *(bool, optional)* : If True, order table by column in descending order.

#### Column configuration

- **name** *(str)* : Name of the column in the database.
- **display_name** *(str, optional)* : Name that will be displayed in the table.
- **foreign_key** *(dict, optional)* : Foreign key configuration.
- **columnDef** *(dict[str, Any])* : [AG Grid column properties](https://www.ag-grid.com/angular-data-grid/column-properties/).

#### Foreign key configuration

- **table_name** *(str)* : Name of the foreign table in the database.
- **schema_name** *(str, optional)* : Schema where the foreign table is located in the database.
- **column_name** *(str)* : Name of the referenced column in the database.
- **column_display** *(str)* : Values that will be displayed in the app.
- **order_by** *(list[dict])* : Ordering of the dropdown options.

### About column definitions

You can set the `columnDef` property in the `Column` and `PrimaryKey` models and set the `defaultColDef` property in the `Config` and `Table` models.

The column definitions set in the `Config` model are applied to every table and column in the application, but they will be overwritten by the definitions set in the `Table`, and lastly overwritten by the definitions set in `Column` and `PrimaryKey`.

BananaManager does not offer support to every single definition of the original AG Grid, specially the Enterprise-only properties, but are some highlights that were fully tested:

- **editable** *(bool)* : Set to `true` if this column is editable, otherwise `false`.
- **hide** *(bool)* : Set to `true` for this column to be hidden.
- **sortable** *(bool)* : Set to `false` to disable sorting which is enabled by default.
- **filter** *(bool)* : Set to `true` to use the default filter component.

### Load the application

Create an app.py file in the root folder:

```python
from banana import Banana

app = Banana()
MY_PORT = 4000 

if __name__ == "__main__":
    app.run_server(port=MY_PORT)
```

This will load a development server in the selected port. Consider running a production server with `waitress`:

```python
from banana import Banana
from waitress import serve

app = Banana()
MY_PORT = 4000

if __name__ == "__main__":
    serve(app.server, port=MY_PORT)
```


## Roadmap

| Version  | Description                  | Release date               |
|----------|------------------------------|----------------------------|
| **v0.1** | Load table and update cells  | First half of July 2024    |
| **v0.2** | Table groups                 | Second half of July 2024   |
| **v0.3** | Logging and configurations   | First half of August 2024  |
| **v0.4** | Insert rows and color themes | Second half of August 2024 |
| **v0.5** | Change history               | September 2024             |
| **v0.6** | Delete rows                  | November 2024              |
| **v0.7** | Special data types           | December 2024              |
| **v0.8** | User authentication          | First quarter of 2025      |
| **v0.9** | Advanced user authorization  | Second quarter of 2025     |

## License

Banana Manager is released under the MIT License. See the [LICENSE](LICENSE) file for more details.