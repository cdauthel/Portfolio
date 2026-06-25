from __future__ import annotations

import argparse
from pathlib import Path

import qrcode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate QR code for deployed portfolio URL.")
    parser.add_argument("--url", type=str, required=True, help="Public URL to encode")
    parser.add_argument("--output", type=str, default="docs/assets/portfolio_qr.png")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    img = qrcode.make(args.url)
    img.save(output)
    print(f"QR code saved to {output}")


if __name__ == "__main__":
    main()
