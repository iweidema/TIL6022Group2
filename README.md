# TIL6022 Group 2 – Pedestrian flows during SAIL Amsterdam 2025

Project for TIL6022 Programming (TU Delft). We analyse pedestrian flow data from crowd sensors in Amsterdam during SAIL 2025 (20–24 August 2025).

*Research question: to be added.*

## Repository structure

```
├── README.md
├── requirements.txt
├── project_report_group_2.ipynb    # main report (proposal + final report)
├── exports/                        # PDF/HTML export of the report
├── notebooks/
│   └── data_cleaning.ipynb         # cleaning, sensor selection and data integration
├── data/
│   ├── raw/                        # original data, not changed
│   │   ├── sensordata_SAIL2025.csv
│   │   ├── sensor_locations.csv
│   │   └── SAIL_Amsterdam_Weather_Data.csv
│   └── processed/
│       └── basisdataset.csv        # made by notebooks/data_cleaning.ipynb
└── figures/                        # figures saved by the notebooks
```

## Data

| File | Description |
|---|---|
| `sensordata_SAIL2025.csv` | Number of people passing per sensor per 3 minutes, for each walking direction (20–24 Aug 2025) |
| `sensor_locations.csv` | Name, coordinates and (effective) width of each sensor location |
| `SAIL_Amsterdam_Weather_Data.csv` | Temperature, humidity and rain per 10 minutes |

## How to run

1. Install Python 3 and the packages:
   ```
   pip install -r requirements.txt
   ```
2. Run `notebooks/data_cleaning.ipynb` from top to bottom. This creates `data/processed/basisdataset.csv` and `figures/flow_3_sensors.png`.
3. Run `project_report_group_2.ipynb` for the analysis and the report.

## Data cleaning (short)

- Checked for empty values, duplicate timestamps and gaps in time: none found.
- Selected 3 sensors: **GASA-03** (Oosterdoksbrug) and **GASA-04** (CS towards Oosterdokskade) as busy places on the event route, and **CMSA-GAWW-17** (Oudezijds Voorburgwal 206) as a quiet place in the city centre.
- Added both walking directions together into one flow per sensor.
- The GASA sensors were only switched on at 20 Aug 08:12. The zeros before that are set to empty (NaN).
- Added location and effective width, and calculated `flow_per_m` (people per metre of width).
- Added weather per 10-minute block. The weather file only covers 20 Aug 02:00 – 22 Aug 18:30, so weather is empty after that. We assume the weather times are local time.

## Authors

| Name | Student number | Main tasks |
|---|---|---|
| Ivo Weidema | | |
| Fabian | | GitHub setup, data cleaning, sensor selection, base dataset, data integration |
| | | |
