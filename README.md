# python-azure-sql-connect

This repository contains `pyazsql` Python module that helps create an ODBC connection to an Azure SQL Database using Azure Active Directory application authentication mechanism with tokens. It also provides a solution to keep Azure App credentials separate from the code by storing and loading them from a configuration file (example included).

### Usage

1. Make sure `ODBC Driver 17 for SQL Server` is installed in the system.

2. Install required packages ([`msal`](https://pypi.org/project/msal/), [`pyodbc`](https://pypi.org/project/pyodbc/)):

`python -m pip install msal pyodbc`

3. Register an [application](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app#register-an-application).

4. Prepare credentials file (you can use `azure_credentials_example.ini` as an example) by populating `client_id`, `tenant_id`, and `client_secret` values obtained through Azure Active Directory application portal. Section can have arbitrary name (`example-app` in the example file), but it may be convenient to name it after the Azure app. Be careful to keep the file private and not commit it to a repository (it may be a good idea to add it to `.gitignore`).

#### To use with `pyodbc`

5. Create a connection:

```python
from pyazsql import connect

conn = connect("server", "database", "azure_credentials.ini")
```

6. Use created Connection object normally:

```python
cur = conn.cursor()
cur.execute("select * from schema.table").fetchone()
```

#### To use with `sqlalchemy`

5. Make sure [`sqlalchemy`](https://pypi.org/project/sqlalchemy/) is installed:

`python -m pip install sqlalchemy`

6. Create an engine:

```python
from pyazsql_sqlalchemy import create_engine

engine = create_engine("server", "database", "azure_credentials.ini")
```

7. Use created Engine object normally:

```python
engine.execute("select * from schema.table").fetchone()
```
