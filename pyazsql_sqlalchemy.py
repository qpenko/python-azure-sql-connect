from typing import Dict, Optional
from urllib import parse

import sqlalchemy

from pyazsql import (
    AZURE_AUTHORITY,
    AZURE_RESOURCE_SQL_DATABASE,
    SQL_COPT_SS_ACCESS_TOKEN,
    make_conn_params,
)


def create_engine(
    server: str,
    database: str,
    credentials_file: str,
    app: Optional[str] = None,
    authority: str = AZURE_AUTHORITY,
    resource: str = AZURE_RESOURCE_SQL_DATABASE,
    proxies: Optional[Dict[str, str]] = None,
    **kwargs
) -> sqlalchemy.engine.base.Engine:
    conn_str, token = make_conn_params(
        server=server,
        database=database,
        credentials_file=credentials_file,
        app=app,
        authority=authority,
        resource=resource,
        proxies=proxies,
        **kwargs
    )
    return sqlalchemy.create_engine(
        "mssql+pyodbc:///?odbc_connect=%s" % parse.quote_plus(conn_str),
        connect_args={"attrs_before": {SQL_COPT_SS_ACCESS_TOKEN: token}},
    )
