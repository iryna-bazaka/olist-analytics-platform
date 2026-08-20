from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from olist_analytics.local_pipeline import build_local_warehouse


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the local Olist semantic warehouse preview")
    parser.add_argument("--raw-dir", default=os.getenv("OLIST_RAW_DIR", str(ROOT / "data" / "raw")))
    parser.add_argument("--db-path", default=os.getenv("OLIST_DB_PATH", str(ROOT / "data" / "warehouse" / "olist.sqlite")))
    args = parser.parse_args()

    result = build_local_warehouse(args.raw_dir, args.db_path)
    print(json.dumps(result, indent=2, default=str))

    if not result["quality"]["passed"]:
        raise SystemExit("Pipeline completed with failed quality checks; see reports/quality_report.json")


if __name__ == "__main__":
    main()
