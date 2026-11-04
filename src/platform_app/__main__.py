import argparse
import json
import sys

from .core import run
from .sources import authorize_gmail
from .core import paths


def main():
    parser = argparse.ArgumentParser(description="Atualiza o painel privado de vagas")
    parser.add_argument("command", choices=["run", "auth-gmail"])
    parser.add_argument("--person", default="glaucojunior")
    args = parser.parse_args()
    try:
        if args.command == "run":
            result = run(args.person)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            if result["errors"]:
                sys.exit(2)
        else:
            private, _ = paths(args.person)
            print(f"Autorização salva em {authorize_gmail(private)}")
    except Exception as exc:
        parser.exit(1, f"Falha: {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    main()
