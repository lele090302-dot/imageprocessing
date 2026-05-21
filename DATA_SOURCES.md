# Data Sources

All datasets used in this project are open-access and freely available from the Copernicus Climate Change Service (C3S) and related European Commission services.

---

## 1. Agricultural Drought Risk (RDRIA)

| Field | Detail |
|-------|--------|
| **Name** | Risk of Drought Impact for Agriculture (RDRIA) |
| **Provider** | Copernicus Global Drought Observatory (GDO), Joint Research Centre |
| **URL** | https://edo.jrc.ec.europa.eu/gdo/php/index.php |
| **Format** | NetCDF (.nc) |
| **Resolution** | 1° global grid (180 × 360 pixels) |
| **Temporal** | Dekadal (10-day intervals), 36 time steps per year |
| **Period used** | 2010–2026 (17 files) |
| **Values** | 1 = Low risk, 2 = Medium risk, 3 = High risk, NaN = no data/ocean |
| **License** | Creative Commons Attribution 4.0 International |
| **Citation** | Sepulcre-Canto, G. et al. (2012) 'Development of a Combined Drought Indicator to detect agricultural drought in Europe', *Natural Hazards and Earth System Sciences*, 12(11), pp. 3519–3531. |

### Download Instructions
1. Go to https://edo.jrc.ec.europa.eu/gdo/php/index.php
2. Navigate to "Download" → "Drought-related indicators worldwide"
3. Filter: Indicator = "Risk of Drought Impact for Agriculture"
4. Select years 2010–2026, format = NetCDF
5. Place downloaded files in `data/drought/`

---

## 2. Global Sea Level Change — Historical (1990–2014)

| Field | Detail |
|-------|--------|
| **Name** | Global sea level change time series from 1950 to 2050 |
| **Provider** | Deltares / Copernicus Climate Change Service |
| **URL** | https://cds.climate.copernicus.eu/datasets/sis-water-level-change-timeseries-cmip6 |
| **Format** | NetCDF (.nc) |
| **Type** | Station-based (43,119 coastal stations globally) |
| **Temporal** | Annual mean sea level |
| **Period used** | 1990–2014 (25 files) |
| **Variable** | mean_sea_level (metres) |
| **Experiment** | Historical (ERA5 reanalysis) |
| **Model** | HadGEM3-GC31-HM |
| **License** | Copernicus License (free, attribution required) |
| **Citation** | Dullaart, J. et al. (2021) Global Sea Level Change Time Series. Copernicus Climate Change Service, ECMWF. |

### Download Instructions
1. Go to https://cds.climate.copernicus.eu
2. Search "Global sea level change time series"
3. Select: Variable = Mean sea level, Experiment = Historical, Model = HadGEM3-GC31-HM
4. Temporal aggregation = Annual, Years = 1990–2014
5. Place downloaded files in `data/sea_level_historical/`

---

## 3. Global Sea Level Change — Future Projection (2015–2050)

| Field | Detail |
|-------|--------|
| **Name** | Same dataset as above |
| **Period used** | 2015–2050 (36 files) |
| **Experiment** | Future (SSP5-8.5) |
| **Model** | HadGEM3-GC31-HM |
| **Scenario** | SSP5-8.5 (high emissions, high mitigation/adaptation challenges) |

### Download Instructions
1. Same URL as above
2. Select: Variable = Mean sea level, Experiment = Future, Model = HadGEM3-GC31-HM
3. Temporal aggregation = Annual, Years = 2015–2050
4. Place downloaded files in `data/sea_level_future/`

---

## 4. Validation Data (planned)

| Field | Detail |
|-------|--------|
| **Name** | EM-DAT: The Emergency Events Database |
| **Provider** | Centre for Research on the Epidemiology of Disasters (CRED), Université catholique de Louvain |
| **URL** | https://www.emdat.be |
| **Format** | CSV |
| **Usage** | Cross-reference RDRIA drought risk peaks with historically declared drought events in Vietnam |
| **License** | Free for academic use (registration required) |
| **Citation** | Guha-Sapir, D. et al. (2024) EM-DAT: The Emergency Events Database. Université catholique de Louvain, Brussels. |

---

## File Naming Conventions

### Drought (RDRIA)
```
rdria_m_gdo_YYYYMMDD_YYYYMMDD_t.nc
         │       │         │
         │       │         └── end date of coverage
         │       └── start date of coverage
         └── monthly/dekadal product from GDO
```

### Sea Level
```
historical_msl_YYYY_01_v1.nc    (historical, one per year)
future_msl_YYYY_01_v1.nc        (future projection, one per year)
```

---

## Notes

- Raw .nc files are excluded from this repository via .gitignore due to file size (~500MB total)
- All data is reproducible by following the download instructions above
- Copernicus data requires a free CDS account for download
