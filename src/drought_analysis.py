#!/usr/bin/python3
"""
Global Drought Risk Analysis — 2010 to 2026
Copernicus GDO RDRIA dataset (NetCDF, dekadal, 1° global grid)

Values: 1=Low, 2=Medium, 3=High drought impact risk for agriculture
NaN = no data / ocean

Pipeline:
  1. Load all years → (time, lat, lon) cube
  2. Crop to Vietnam + extract city time series
  3. Seasonal heatmap: month vs year, mean risk level
  4. Trend map: is drought getting worse over time?
  5. Global hotspot map: mean risk 2010-2026
  6. Vietnam city risk profiles across all dekads
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.ticker as mticker
import pandas as pd
import glob, os
from scipy import stats

# ── Vietnam bounding box ──────────────────────────────────────────────────────
VN_LON = (102.0, 110.5)
VN_LAT = (8.0,   23.5)

TOURISM_CITIES = {
    "Hanoi":            (105.85, 21.03),
    "Da Nang":          (108.22, 16.07),
    "Hoi An":           (108.33, 15.88),
    "Nha Trang":        (109.19, 12.24),
    "Ho Chi Minh City": (106.66, 10.82),
    "Hue":              (107.59, 16.46),
    "Phu Quoc":         (103.96, 10.29),
}

RISK_CMAP = mcolors.LinearSegmentedColormap.from_list(
    "drought", ["#ffffff", "#ffffcc", "#fd8d3c", "#bd0026"], N=256)


# ── Step 1: Load all NetCDF files into one xarray DataArray ──────────────────
def load_drought_cube(folder):
    """
    Load all rdria_m_gdo_YYYY*.nc files and concatenate along time.
    Returns an xarray DataArray with dims (time, lat, lon).
    """
    files = sorted(glob.glob(os.path.join(folder, "rdria_m_gdo_*.nc")))
    if not files:
        raise FileNotFoundError(f"No RDRIA .nc files found in: {folder}")

    print(f"Loading {len(files)} files...")
    datasets = []
    for f in files:
        ds = xr.open_dataset(f)
        # squeeze out the 'band' dimension → (time, lat, lon)
        da = ds["rdria"].squeeze("band", drop=True)
        datasets.append(da)
        ds.close()

    cube = xr.concat(datasets, dim="time").sortby("time")
    # Replace 0 and negative with NaN (ocean / no data)
    cube = cube.where(cube >= 1)

    print(f"Cube shape : {cube.shape}  (time × lat × lon)")
    print(f"Time range : {str(cube.time.values[0])[:10]} → {str(cube.time.values[-1])[:10]}")
    print(f"Total dekads: {len(cube.time)}")
    return cube


# ── Helper: nearest grid cell to a lon/lat point ─────────────────────────────
def nearest_cell(cube, lon, lat):
    """Return the DataArray time series at the nearest grid cell."""
    return cube.sel(lon=lon, lat=lat, method="nearest")


# ── Step 2: Vietnam crop ──────────────────────────────────────────────────────
def crop_vietnam(cube):
    return cube.sel(
        lon=slice(VN_LON[0], VN_LON[1]),
        lat=slice(VN_LAT[1], VN_LAT[0])   # lat is descending
    )


# ── Step 3: Seasonal heatmap (year × month) ───────────────────────────────────
def plot_seasonal_heatmap(cube):
    """
    For Vietnam: mean risk level per calendar month per year.
    Rows = years, columns = months. Reveals seasonal drought patterns.
    """
    vn = crop_vietnam(cube)
    # Spatial mean over Vietnam for each dekad
    vn_mean = vn.mean(dim=["lat", "lon"], skipna=True)

    times  = pd.DatetimeIndex(vn_mean.time.values)
    values = vn_mean.values

    years  = sorted(set(times.year))
    months = range(1, 13)
    grid   = np.full((len(years), 12), np.nan)

    for i, yr in enumerate(years):
        for j, mo in enumerate(months):
            mask = (times.year == yr) & (times.month == mo)
            if mask.any():
                grid[i, j] = np.nanmean(values[mask])

    fig, ax = plt.subplots(figsize=(14, 7))
    im = ax.imshow(grid, aspect='auto', cmap=RISK_CMAP, vmin=1, vmax=3,
                   interpolation='nearest')
    plt.colorbar(im, ax=ax, label="Mean drought risk (1=Low, 2=Medium, 3=High)",
                 shrink=0.8)
    ax.set_xticks(range(12))
    ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun",
                         "Jul","Aug","Sep","Oct","Nov","Dec"])
    ax.set_yticks(range(len(years)))
    ax.set_yticklabels(years)
    ax.set_title("Vietnam Agricultural Drought Risk — Seasonal Heatmap 2010–2026\n"
                 "Darker = higher risk", fontsize=13)
    ax.set_xlabel("Month")
    ax.set_ylabel("Year")
    plt.tight_layout()
    plt.savefig("output_drought_seasonal_heatmap.png", dpi=150, bbox_inches='tight')
    print("Saved → output_drought_seasonal_heatmap.png")
    plt.show()
    return grid, years


# ── Step 4: Annual trend map for Vietnam ──────────────────────────────────────
def plot_trend_map(cube):
    """
    Per-pixel linear trend in risk level (units/year) across 2010–2026.
    Positive = drought getting worse, negative = improving.
    """
    vn   = crop_vietnam(cube)
    times = pd.DatetimeIndex(vn.time.values)
    # Use decimal year as x-axis
    x = times.year + (times.month - 1) / 12

    lats = vn.lat.values
    lons = vn.lon.values
    data = vn.values   # (time, lat, lon)

    trend_map = np.full((len(lats), len(lons)), np.nan)
    for i in range(len(lats)):
        for j in range(len(lons)):
            ts    = data[:, i, j]
            valid = ~np.isnan(ts)
            if valid.sum() < 10:
                continue
            slope, *_ = stats.linregress(x[valid], ts[valid])
            trend_map[i, j] = slope

    fig, ax = plt.subplots(figsize=(9, 10))
    norm = mcolors.TwoSlopeNorm(vmin=-0.1, vcenter=0, vmax=0.1)
    im = ax.imshow(trend_map, extent=[VN_LON[0], VN_LON[1], VN_LAT[0], VN_LAT[1]],
                   origin='upper', cmap='RdBu_r', norm=norm, interpolation='nearest')
    plt.colorbar(im, ax=ax, label="Trend (risk units/year)", shrink=0.7)

    for city, (lon, lat) in TOURISM_CITIES.items():
        ax.plot(lon, lat, 'k*', markersize=10)
        ax.annotate(city, (lon, lat), textcoords="offset points",
                    xytext=(5, 3), fontsize=7,
                    bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.8))

    ax.set_title("Vietnam Drought Risk Trend 2010–2026\nRed = worsening, Blue = improving")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    plt.tight_layout()
    plt.savefig("output_drought_trend_map.png", dpi=150, bbox_inches='tight')
    print("Saved → output_drought_trend_map.png")
    plt.show()


# ── Step 5: Global mean risk map ──────────────────────────────────────────────
def plot_global_mean(cube):
    """Mean risk level across all dekads — shows chronic drought hotspots globally."""
    mean_map = cube.mean(dim="time", skipna=True)

    fig, ax = plt.subplots(figsize=(16, 8))
    im = ax.imshow(mean_map.values,
                   extent=[-180, 180, -90, 90],
                   origin='upper', cmap=RISK_CMAP, vmin=1, vmax=3,
                   interpolation='nearest', aspect='auto')
    plt.colorbar(im, ax=ax, label="Mean drought risk 2010–2026 (1=Low, 3=High)",
                 shrink=0.6)

    # Vietnam box
    from matplotlib.patches import Rectangle
    rect = Rectangle((VN_LON[0], VN_LAT[0]),
                      VN_LON[1]-VN_LON[0], VN_LAT[1]-VN_LAT[0],
                      linewidth=2, edgecolor='cyan', facecolor='none', zorder=5)
    ax.add_patch(rect)
    ax.text(VN_LON[0], VN_LAT[1]+1, "Vietnam", color='cyan', fontsize=9, fontweight='bold')

    ax.set_title("Global Agricultural Drought Risk — Mean 2010–2026\n"
                 "Copernicus GDO RDRIA Indicator", fontsize=13)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    plt.tight_layout()
    plt.savefig("output_drought_global_mean.png", dpi=150, bbox_inches='tight')
    print("Saved → output_drought_global_mean.png")
    plt.show()


# ── Step 6: City risk time series ─────────────────────────────────────────────
def plot_city_timeseries(cube):
    """Annual mean risk level for each tourism city, 2010–2026."""
    times = pd.DatetimeIndex(cube.time.values)
    years = sorted(set(times.year))
    colors = plt.cm.tab10.colors

    fig, ax = plt.subplots(figsize=(13, 6))

    for i, (city, (lon, lat)) in enumerate(TOURISM_CITIES.items()):
        ts = nearest_cell(cube, lon, lat).values
        # Annual mean
        annual = [np.nanmean(ts[times.year == yr]) for yr in years]
        ax.plot(years, annual, marker='o', markersize=5,
                color=colors[i % 10], linewidth=1.8, label=city)

    ax.set_xlabel("Year")
    ax.set_ylabel("Mean drought risk level (1=Low, 2=Medium, 3=High)")
    ax.set_title("Annual Agricultural Drought Risk — Vietnam Tourism Cities 2010–2026")
    ax.set_ylim(0.8, 3.2)
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(["Low", "Medium", "High"])
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("output_drought_city_timeseries.png", dpi=150, bbox_inches='tight')
    print("Saved → output_drought_city_timeseries.png")
    plt.show()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Analyse Copernicus GDO RDRIA drought NetCDF files")
    parser.add_argument("folder", help="Folder containing rdria_m_gdo_*.nc files")
    args = parser.parse_args()

    cube = load_drought_cube(args.folder)
    plot_global_mean(cube)
    plot_seasonal_heatmap(cube)
    plot_trend_map(cube)
    plot_city_timeseries(cube)
