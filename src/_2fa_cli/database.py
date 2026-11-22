import sqlite3
import pyotp
from _2fa_cli.constants import (
    DATABASE_FOLDER,
    DEFAULT_DATABASE_NAME,
    MINIMUM_SECRET_LENGTH,
    DEFAULT_DIGITS,
    DEFAULT_INTERVAL
)

# default is 112 but we adjust the subclass to 80 because some websites do that
class _TOTP(pyotp.TOTP):
    min_secret_length_bits = MINIMUM_SECRET_LENGTH

class Database:
    def __init__(self, database_name=DEFAULT_DATABASE_NAME):
        DATABASE_FOLDER.mkdir(
            parents=True,
            exist_ok=True
        )
        self.db = sqlite3.connect(DATABASE_FOLDER / database_name)
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS 
                secrets (
                    alias TEXT PRIMARY KEY,
                    secret TEXT NOT NULL
                )     
            """
        )
        self.db.commit()

    def add_secret(self, alias, secret):
        self.db.execute(
            """
            INSERT INTO 
                secrets (alias, secret)
            VALUES
                (?,?)
            """,
            [alias,secret]
        )
        self.db.commit()

    def remove_secret(self, alias):
        self.db.execute(
            """
            DELETE FROM 
                secrets
            WHERE
                alias = ?
            """,
            [alias]
        )
        self.commit()

    def update_alias(self, alias_from, alias_to):
        self.db.execute(
            """
            UPDATE
                secrets
            SET
                alias = ?
            WHERE
                alias = ?
            """,
            [alias_from, alias_to]
        )
        self.db.commit()

    def update_secret(self, alias, secret):
        self.db.execute(
            """
            UPDATE
                secrets
            SET
                secret = ?
            WHERE
                alias = ?
            """,
            [secret, alias]
        )
        self.db.commit()

    def list_aliases(self, show_codes, digits, interval):
        rows = self.db.execute(
            """
            SELECT
                alias, secret
            FROM
                secrets
            ORDER BY
                alias
            """
        ).fetchall()

        for row in rows:
            alias, secret = row
            
            # we construct the string to print so we dont half-print output if get_code throws an exception
            string_to_print = alias

            if show_codes:
                code = self.get_code(
                    secret, 
                    digits=digits, 
                    interval=interval
                )
                string_to_print += " " + code

            print(string_to_print)

    def get_code(self, alias_or_secret, digits=DEFAULT_DIGITS, interval=DEFAULT_INTERVAL):
        row = self.db.execute(
            """
            SELECT
                secret
            FROM
                secrets
            WHERE
                alias = ?
            """,
            [alias_or_secret]
        ).fetchone()

        if row:
            secret = row[0]
        else:
            secret = alias_or_secret

        code = _TOTP(
            s=secret,
            interval=interval,
            digits=digits
        ).now()

        return code