import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bbox", type=str, help="minx,miny,maxx,maxy (EPSG:4326)")
    parser.add_argument("--crs", type=str, default="EPSG:4326")
    parser.add_argument("--start", type=str)
    parser.add_argument("--end", type=str)
    args = parser.parse_args()

    # Stub: apenas grava um arquivo de log para demonstrar execução
    out = Path("outputs")
    out.mkdir(parents=True, exist_ok=True)
    (out / "run_stub.txt").write_text(
        f"bbox={args.bbox}\ncrs={args.crs}\nstart={args.start}\nend={args.end}\n",
        encoding="utf-8",
    )
    print("Prototype stub OK -> outputs/run_stub.txt")


if __name__ == "__main__":
    main()
