import sys
from typing import Sequence

from .PacodexionCLI import PacodexionCLI


def main(argv: Sequence[str] | None = None) -> int:
    cli = PacodexionCLI()
    return cli.run(argv if argv is not None else sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
