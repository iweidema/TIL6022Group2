"""Afstand tussen schepen en sensoren.

Input : basisdataset.csv        (sensor, lat, lon, flow per 3 min)
        sail_ships_22aug_16-18.csv (timestamp, name, category, length_m, speed_ms, lon, lat)
Output: ship_sensor_distances.csv   -> 1 rij per ping per sensor (afstand in m)
        ship_features_3min.csv      -> 1 rij per 3 min per sensor (+ flow)
"""
import numpy as np
import pandas as pd

PATH_BASIS = "49ee1c74-basisdataset.csv"
PATH_SHIPS = "65865a0a-sail_ships_22aug_16-18.csv"
RADII = (250, 500)   # meters
CAP = 1000           # afstanden afkappen op 1000 m


def haversine(lat1, lon1, lat2, lon2):
    """Afstand in meters tussen twee (arrays van) lat/lon-punten."""
    R = 6371000
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    a = (np.sin((lat2 - lat1) / 2) ** 2
         + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2)
    return 2 * R * np.arcsin(np.sqrt(a))


# --- 1. Laden -------------------------------------------------------------
basis = pd.read_csv(PATH_BASIS)
basis["timestamp"] = pd.to_datetime(basis["timestamp"], utc=True)
sensors = basis[["sensor", "location", "lat", "lon"]].drop_duplicates("sensor").reset_index(drop=True)

ships = pd.read_csv(PATH_SHIPS)
ships["timestamp"] = pd.to_datetime(ships["timestamp"], utc=True)
ships = ships.dropna(subset=["lat", "lon"])
print("Sensoren:\n", sensors.to_string(index=False))
print(f"\n{len(ships)} pings, {ships['name'].nunique()} schepen, "
      f"{ships['timestamp'].min()} t/m {ships['timestamp'].max()}")

# --- 2. Afstand per ping per sensor (long-format) ------------------------
rows = []
for _, s in sensors.iterrows():
    d = haversine(s["lat"], s["lon"], ships["lat"].values, ships["lon"].values)
    rows.append(ships.assign(sensor=s["sensor"], distance_m=d))
pings = pd.concat(rows, ignore_index=True).sort_values(["timestamp", "name", "sensor"])
pings.to_csv("ship_sensor_distances.csv", index=False)

# --- 3. Features per 3 minuten per sensor ---------------------------------
# eerst per schip per bin middelen (zoals in de XGBoost-notebook), dan afstand
ships["bin"] = ships["timestamp"].dt.floor("3min")
binned = (ships.groupby(["bin", "name"], as_index=False)
               .agg(lat=("lat", "mean"), lon=("lon", "mean"), length_m=("length_m", "first")))

feat = []
for _, s in sensors.iterrows():
    b = binned.assign(dist=np.clip(haversine(s["lat"], s["lon"], binned["lat"], binned["lon"]), 0, CAP))
    g = b.groupby("bin")
    f = pd.DataFrame({"nearest_ship_m": g["dist"].min()})
    for R in RADII:
        m = b[b["dist"] <= R].groupby("bin")
        f[f"n_ships_{R}m"] = m.size()
        f[f"sum_length_{R}m"] = m["length_m"].sum()
    f = f.reindex(pd.date_range(binned["bin"].min(), binned["bin"].max(), freq="3min", tz="UTC"))
    f["nearest_ship_m"] = f["nearest_ship_m"].fillna(CAP)   # geen schip in beeld
    f = f.fillna(0)
    f.insert(0, "sensor", s["sensor"])
    feat.append(f.rename_axis("timestamp").reset_index())
feat = pd.concat(feat, ignore_index=True)

# flow (sensor-telling) erbij voor dezelfde tijdstappen
feat = feat.merge(basis[["timestamp", "sensor", "flow", "flow_per_m"]],
                  on=["timestamp", "sensor"], how="left")
feat.to_csv("ship_features_3min.csv", index=False)

# --- 4. Samenvatting ------------------------------------------------------
print("\nDichtstbijzijnde ping per sensor:")
idx = pings.groupby("sensor")["distance_m"].idxmin()
print(pings.loc[idx, ["sensor", "name", "timestamp", "distance_m"]]
      .assign(distance_m=lambda d: d["distance_m"].round(1)).to_string(index=False))
print("\nMediane afstand per sensor (m):")
print(pings.groupby("sensor")["distance_m"].median().round(0).to_string())
