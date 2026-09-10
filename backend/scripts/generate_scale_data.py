#!/usr/bin/env python3
import argparse
from pathlib import Path


DEFAULT_RECORDS = 466_550


def generate_dataset(output: Path, records: int = DEFAULT_RECORDS) -> None:
    if records <= 0:
        raise ValueError("A quantidade de registros deve ser maior que zero.")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as stream:
        for position in range(records):
            stream.write(f"word-{position:06d}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera um TXT reproduzível com uma palavra única por linha."
    )
    parser.add_argument("output", type=Path, help="Caminho do TXT de saída.")
    parser.add_argument("--records", type=int, default=DEFAULT_RECORDS)
    args = parser.parse_args()

    generate_dataset(args.output, args.records)
    print(f"Gerados {args.records:,} registros em {args.output}.")


if __name__ == "__main__":
    main()
