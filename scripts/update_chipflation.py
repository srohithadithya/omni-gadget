#!/usr/bin/env python3
"""
AIDE-OS Chipflation Updater
Upload spot price data to the chipflation_index table.

Usage:
  # Single update
  python scripts/update_chipflation.py --component LPDDR5X --price 3.85 --mom 4.2 --yoy 18.5

  # From CSV file (columns: component_type,spot_price_usd,mom_growth_pct,yoy_growth_pct,source)
  python scripts/update_chipflation.py --csv data/chipflation_sep2026.csv

  # Print current state
  python scripts/update_chipflation.py --show
"""
import argparse
import csv
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.db import get_connection, update_chipflation_index, get_latest_chipflation_all


def show_current():
    rows = get_latest_chipflation_all()
    if not rows:
        print("No chipflation data found. Seed with schema.sql or --csv.")
        return
    print(f"\n{'Component':<20} {'Spot $/GB':>10} {'MoM%':>8} {'YoY%':>8} {'Source':<15} {'Recorded'}")
    print("-" * 85)
    for r in rows:
        print(f"{r['component_type']:<20} {float(r['spot_price_usd']):>10.4f} "
              f"{float(r['mom_growth_pct']):>+7.2f} {float(r['yoy_growth_pct']):>+7.2f} "
              f"{r['source']:<15} {r['recorded_at'].strftime('%Y-%m-%d %H:%M') if r['recorded_at'] else 'N/A'}")


def update_single(component, price, mom, yoy, source="cli"):
    update_chipflation_index(component, price, mom, yoy, source)
    print(f"Updated {component}: ${price}/GB, MoM {mom}%, YoY {yoy}% (source: {source})")


def update_from_csv(path):
    with open(path) as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            update_chipflation_index(
                row["component_type"],
                float(row["spot_price_usd"]),
                float(row["mom_growth_pct"]),
                float(row["yoy_growth_pct"]),
                row.get("source", "csv_import"),
            )
            count += 1
    print(f"Imported {count} chipflation records from {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AIDE-OS Chipflation Updater")
    parser.add_argument("--show", action="store_true", help="Show current chipflation data")
    parser.add_argument("--component", help="Component type (LPDDR5X, DDR5_SODIMM, NAND_3D_TLC, etc.)")
    parser.add_argument("--price", type=float, help="Spot price USD/GB")
    parser.add_argument("--mom", type=float, help="Month-over-month growth %")
    parser.add_argument("--yoy", type=float, help="Year-over-year growth %")
    parser.add_argument("--source", default="cli", help="Data source (default: cli)")
    parser.add_argument("--csv", help="Path to CSV file for bulk import")
    args = parser.parse_args()

    if args.show:
        show_current()
    elif args.csv:
        update_from_csv(args.csv)
    elif args.component and args.price is not None and args.mom is not None and args.yoy is not None:
        update_single(args.component, args.price, args.mom, args.yoy, args.source)
    else:
        parser.print_help()
