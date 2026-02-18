import sys
from .cli import build_parser, dispatch


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    dispatch(args)


if __name__ == "__main__":
    main()
