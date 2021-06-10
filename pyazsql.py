import configparser
import struct
from itertools import chain, repeat
from typing import Dict, Optional, Tuple

import msal
import pyodbc

SQL_COPT_SS_ACCESS_TOKEN = 1256

AZURE_AUTHORITY = "https://login.microsoftonline.com"
AZURE_RESOURCE_SQL_DATABASE = "https://database.windows.net"

MSSQL_DRIVER = "ODBC Driver 17 for SQL Server"


def read_credentials(fp: str, app: Optional[str] = None) -> Dict[str, str]:
    keys = ("tenant_id", "client_id", "client_secret")

    cfg = configparser.ConfigParser()
    cfg.read_file(open(fp))

    if app:
        if app not in cfg.sections():
            raise ValueError(
                "couldn't find '%s' app credentials section" % app
            )
        section = cfg[app]
    else:
        if len(cfg.sections()) > 1:
            raise ValueError(
                "app must be specified if multiple credentials exist"
            )
        section = cfg[cfg.sections()[0]]

    unknown = set(section) - set(keys)
    if unknown:
        raise ValueError(
            "unknown key%s used: %s (use %s)"
            % (
                "s" if len(unknown) > 1 else "",
                ", ".join("'%s'" % c for c in sorted(unknown)),
                ", ".join("'%s'" % c for c in keys),
            )
        )

    missing = set(keys) - set(section)
    if missing:
        raise ValueError(
            "missing required key%s: %s"
            % (
                "s" if len(missing) > 1 else "",
                ", ".join("'%s'" % c for c in sorted(missing)),
            )
        )

    return dict(section)


def get_token(
    authority: str,
    resource: str,
    tenant_id: str,
    client_id: str,
    client_secret: str,
    proxies: Optional[Dict[str, str]],
) -> bytes:
    app = msal.ConfidentialClientApplication(
        client_id,
        client_credential=client_secret,
        authority=authority.rstrip("/") + "/" + tenant_id,
        proxies=proxies,
    )
    resp = app.acquire_token_for_client([resource.rstrip("/") + "//.default"])
    if "access_token" not in resp:
        raise ValueError(
            "%s: %s"
            % (
                resp.get("error", "error"),
                resp.get("error_description", "couldn't obtain token"),
            )
        )
    encoded = bytes(
        chain.from_iterable(zip(resp["access_token"].encode(), repeat(0)))
    )
    return struct.pack("<I", len(encoded)) + encoded


def make_conn_params(
    server: str,
    database: str,
    credentials_file: str,
    app: Optional[str],
    authority: str,
    resource: str,
    proxies: Optional[Dict[str, str]],
    driver: str = MSSQL_DRIVER,
    **kwargs
) -> Tuple[str, bytes]:
    if driver not in pyodbc.drivers():
        raise ValueError("couldn't find driver '%s'" % driver)

    kwargs["Driver"] = "{%s}" % driver
    kwargs["Server"] = server
    kwargs["Database"] = database

    conn_str = ";".join("%s=%s" % args for args in kwargs.items())
    credentials = read_credentials(credentials_file, app)
    token = get_token(
        authority=authority,
        resource=resource,
        tenant_id=credentials["tenant_id"],
        client_id=credentials["client_id"],
        client_secret=credentials["client_secret"],
        proxies=proxies,
    )
    return conn_str, token


def connect(
    server: str,
    database: str,
    credentials_file: str,
    app: Optional[str] = None,
    authority: str = AZURE_AUTHORITY,
    resource: str = AZURE_RESOURCE_SQL_DATABASE,
    proxies: Optional[Dict[str, str]] = None,
    **kwargs
) -> pyodbc.Connection:
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
    return pyodbc.connect(
        conn_str,
        attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token},
    )
