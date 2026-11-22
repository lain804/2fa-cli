from argparse import (
    ArgumentParser,
    SUPPRESS
)

import copykitten
from loguru import logger

from _2fa_cli.database import (
    Database
)
from _2fa_cli.constants import (
    DEFAULT_DIGITS,
    DEFAULT_INTERVAL,
    EXIT_FAILURE,
    EXIT_SUCCESS
)

def main():
    parser = ArgumentParser()

    base = ArgumentParser(
        add_help=False, 
        argument_default=SUPPRESS
    )

    for current_parser in [parser, base]:
        current_parser.add_argument("--interval", "-i", type=float)
        current_parser.add_argument("--digits", "-d", type=int)
        current_parser.add_argument("--copy", "-c", action="store_true")

    parser.set_defaults(
        interval=DEFAULT_INTERVAL,
        digits=DEFAULT_DIGITS,
        copy=False
    )

    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add")
    add.add_argument("alias", type=str)
    add.add_argument("secret", type=str)

    remove = commands.add_parser("remove",aliases=["rm"])
    remove.add_argument("alias", type=str)

    rename = commands.add_parser("rename",aliases=["ren","mv"])
    rename.set_defaults(command="rename")
    rename.add_argument("alias_from",type=str)
    rename.add_argument("alias_to", type=str)

    update = commands.add_parser("update",aliases=["upd"])
    update.add_argument("alias",type=str)
    update.add_argument("secret", type=str)

    code = commands.add_parser("get",aliases=["code"], parents=[base])
    code.add_argument("alias_or_secret", type=str)

    list_codes = commands.add_parser("list",aliases=["ls"], parents=[base])
    list_codes.set_defaults(command="list")

    list_codes.add_argument("--show-codes", action="store_true", default=False)

    db = Database()

    args = parser.parse_args()
    match args.command:
        case "add":
            db.add_secret(args.alias, args.secret)
        case "remove":
            db.remove_secret(args.alias)
        case "rename":
            db.update_alias(args.alias_from, args.alias_to)
        case "update":
            db.update_secret(args.alias, args.secret)
        case "get":
            try:
                code = db.get_code(
                    args.alias_or_secret,
                    digits=args.digits,
                    interval=args.interval
                )
            except Exception as e:
                logger.error(f"failed to generate code: {e}")
                exit(EXIT_FAILURE)

            if args.copy:
                copykitten.copy(code)
            else:
                print(code)
        case "list":
            try:
                db.list_aliases(
                    show_codes=args.show_codes,
                    digits=args.digits,
                    interval=args.interval
                )
            except Exception as e:
                logger.error(f"failed to list aliases: {e}")
                exit(EXIT_FAILURE)
        case _:
            logger.error("unknown command")
        
    return EXIT_SUCCESS
