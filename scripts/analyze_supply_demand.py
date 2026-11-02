"""Classe les communes selon les passages programmes pour 1 000 habitants."""

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def main():
    communes = pd.read_csv(ROOT / "data/reference/communes.csv")
    stops = pd.read_csv(
        ROOT / "data/gtfs_static/stops_frequency.csv", dtype={"stop_id": str}
    )
    if len(communes) != 20 or communes["commune"].duplicated().any():
        raise ValueError("Le referentiel doit contenir 20 communes distinctes.")
    communes["population"] = pd.to_numeric(communes["population"], errors="raise")
    stops["daily_trip_count"] = pd.to_numeric(stops["daily_trip_count"], errors="raise")
    if communes["population"].isna().any() or (communes["population"] <= 0).any():
        raise ValueError("Les populations doivent etre renseignees et positives.")
    counts = stops["daily_trip_count"]
    if counts.isna().any() or (counts < 0).any() or (counts % 1 != 0).any():
        raise ValueError("Les passages doivent etre des entiers positifs ou nuls.")
    if not stops["nearest_commune"].isin(communes["commune"]).all():
        raise ValueError("Un arret est sans commune ou associe a une commune inconnue.")

    # Un passage est une visite programmee a un arret, pas un voyageur.
    supply = stops.groupby("nearest_commune", as_index=False).agg(
        total_daily_stop_visits=("daily_trip_count", "sum"),
        n_assigned_stops=("stop_id", "size"),
    )
    # La jointure gauche part des 20 communes et conserve celles sans arret.
    result = communes.merge(
        supply, left_on="commune", right_on="nearest_commune", how="left",
        validate="one_to_one",
    ).drop(columns="nearest_commune")
    for column in ["total_daily_stop_visits", "n_assigned_stops"]:
        result[column] = result[column].fillna(0).astype(int)
    result["stop_visits_per_1000_residents"] = (
        result["total_daily_stop_visits"] / result["population"] * 1000
    )
    # Classement decroissant ; les ex aequo ont le meme rang.
    result["rank"] = result["stop_visits_per_1000_residents"].rank(
        method="min", ascending=False
    ).astype(int)
    result = result.sort_values(
        ["stop_visits_per_1000_residents", "commune"], ascending=[False, True]
    ).reset_index(drop=True)
    result = result[[
        "rank", "commune", "lat", "lon", "population", "n_assigned_stops",
        "total_daily_stop_visits", "stop_visits_per_1000_residents",
    ]]

    if len(result) != 20 or result["total_daily_stop_visits"].sum() != counts.sum():
        raise ValueError("Le regroupement a perdu des communes ou des passages.")
    if result["n_assigned_stops"].sum() != len(stops):
        raise ValueError("Le regroupement a perdu des arrets.")

    csv_path = ROOT / "data/gtfs_static/supply_by_commune.csv"
    json_path = ROOT / "docs/data/supply_by_commune.json"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(csv_path, index=False, encoding="utf-8")
    payload = {
        "metric": "Scheduled stop-visits per representative weekday per 1,000 residents",
        "formula": "total_daily_stop_visits / population * 1000",
        "sources": ["data/gtfs_static/stops_frequency.csv", "data/reference/communes.csv"],
        "limitations": [
            "Population is a proxy for demand, not observed ridership.",
            "Stops are assigned to the nearest commune centre, not administrative boundaries.",
            "Supply reflects only the representative Tuesday service selected upstream.",
            "Stop-visits do not measure capacity, spatial accessibility or unique trips.",
        ],
        "communes": json.loads(result.to_json(orient="records", double_precision=15)),
    }
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(result.to_string(index=False, float_format=lambda value: f"{value:.3f}"))
    print(f"\nValidation : {len(result)} communes, {len(stops)} arrets, {int(counts.sum())} passages.")
    print(f"CSV : {csv_path}\nJSON : {json_path}")


if __name__ == "__main__":
    main()
