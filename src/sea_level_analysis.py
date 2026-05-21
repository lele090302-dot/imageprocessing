#!/usr/bin/python3
"""
Global Sea Level Change Analysis — 1990 to 2014
Copernicus / Deltares annual mean sea level dataset (station-based)

Each .nc file = one year, 43,119 coastal stations worldwide.
Pipeline:
  1. Load all years → build a (stations × years) time series
  2. Compute per-station trend (mm/year) via linear regression
  3. Global map: colour stations by trend magnitude
  4. Highlight Vietnam coastal tourism cities
  5. Regional time series: Vietnam vs global mean
  6. Hotspot ranking: fastest-rising coastal zones
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from scipy import stats
import glob
import os

# ── Vietnam coastal tourism cities (lon, lat) ─────────────────────────────────
TOURISM_CITIES = {
    "Hanoi":            (105.85, 21.03),
    "Da Nang":          (108.22, 16.07),
    "Hoi An":           (108.33, 15.88),
    "Nha Trang":        (109.19, 12.24),
    "Ho Chi Minh City": (106.66, 10.82),
    "Hue":              (107.59, 16.46),
    "Phu Quoc":         (103.96, 10.29),
}

# Vietnam bounding box
VN_LON = (102.0, 110.5)
VN_LAT = (8.0, 23.5)


# ── Step 1: Load all annual files from a folder ───────────────────────────────
def load_folder(folder, prefix):
    """Load all YYYY files matching prefix from folder, return (lons, lats, years, data)."""
    pattern = os.path.join(folder, f"{prefix}_msl_*_01_v1.nc")
    files   = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files matching '{prefix}_msl_*' in: {folder}")

    print(f"Found {len(files)} files [{prefix}]: {os.path.basename(files[0])} → {os.path.basename(files[-1])}")
    yearly, years = [], []
    lons = lats = None

    for f in files:
        ds  = xr.open_dataset(f)
        yr  = int(str(ds.coords["time"].values[0])[:4])
        msl = ds["mean_sea_level"].values[:, 0]
        if lons is None:
            lons = ds["station_x_coordinate"].values
            lats = ds["station_y_coordinate"].values
        yearly.append(msl)
        years.append(yr)
        ds.close()

    return lons, lats, np.array(years), np.column_stack(yearly)


def load_all_years(hist_folder, future_folder=None):
    """
    Load historical and optionally future folders, join on time axis.
    Returns: lons, lats, years, data, split_year (where historical ends)
    """
    lons, lats, h_years, h_data = load_folder(hist_folder, "historical")
    split_year = h_years[-1]

    if future_folder:
        _, _, f_years, f_data = load_folder(future_folder, "future")
        years = np.concatenate([h_years, f_years])
        data  = np.column_stack([h_data, f_data])
        print(f"\nCombined: {years[0]}–{years[-1]}  ({data.shape[1]} years total)")
    else:
        years, data = h_years, h_data

    print(f"Stations: {data.shape[0]:,}  |  Split year (hist→future): {split_year}")
    return lons, lats, years, data, split_year


# ── Step 2: Linear trend per station ─────────────────────────────────────────
def compute_trends(data, years):
    """
    Fit a linear regression to each station's time series.
    Returns trend in mm/year (converted from metres).
    Stations with too many NaN values are masked.
    """
    n_stations = data.shape[0]
    trends     = np.full(n_stations, np.nan)
    r2_vals    = np.full(n_stations, np.nan)

    for i in range(n_stations):
        ts = data[i, :]
        valid = ~np.isnan(ts)
        if valid.sum() < 5:   # need at least 5 years for a meaningful trend
            continue
        slope, _, r, _, _ = stats.linregress(years[valid], ts[valid])
        trends[i]  = slope * 1000   # convert m/yr → mm/yr
        r2_vals[i] = r ** 2

    valid_count = np.sum(~np.isnan(trends))
    print(f"\nTrend computed for {valid_count:,} / {n_stations:,} stations")
    print(f"Global trend range: {np.nanmin(trends):.2f} → {np.nanmax(trends):.2f} mm/yr")
    print(f"Global median trend: {np.nanmedian(trends):.2f} mm/yr")
    return trends, r2_vals


# ── Step 3: Find nearest station to a lon/lat point ──────────────────────────
def nearest_station(lon, lat, lons, lats):
    """Euclidean nearest-neighbour in degree space."""
    dist = np.sqrt((lons - lon)**2 + (lats - lat)**2)
    return np.argmin(dist)


# ── Step 4: Global trend map ──────────────────────────────────────────────────
def plot_global_map(lons, lats, trends, years):
    fig, ax = plt.subplots(figsize=(16, 8))

    # Clip colour scale to ±10 mm/yr so outliers don't dominate
    vmin, vmax = -10, 10
    cmap = plt.cm.RdBu_r
    norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)

    valid = ~np.isnan(trends)
    sc = ax.scatter(lons[valid], lats[valid], c=trends[valid],
                    cmap=cmap, norm=norm, s=1.5, linewidths=0, alpha=0.7)

    plt.colorbar(sc, ax=ax, label="Sea level trend (mm/year)", shrink=0.6, pad=0.02)

    # Vietnam bounding box
    from matplotlib.patches import Rectangle
    rect = Rectangle((VN_LON[0], VN_LAT[0]),
                      VN_LON[1]-VN_LON[0], VN_LAT[1]-VN_LAT[0],
                      linewidth=2, edgecolor='yellow', facecolor='none', zorder=5)
    ax.add_patch(rect)
    ax.text(VN_LON[0], VN_LAT[1]+0.5, "Vietnam", color='yellow', fontsize=9, fontweight='bold')

    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(f"Global Mean Sea Level Trend {years[0]}–{years[-1]}\n"
                 f"Red = rising, Blue = falling (mm/year)", fontsize=13)
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#0f0f1a')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')

    plt.tight_layout()
    plt.savefig("output_global_trend_map.png", dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    print("Saved → output_global_trend_map.png")
    plt.show()


# ── Step 5: Vietnam regional time series ─────────────────────────────────────
def plot_vietnam_timeseries(lons, lats, data, years, split_year=None):
    """
    Extract time series for each tourism city (nearest station)
    and plot against the global mean. Marks the historical/future boundary.
    """
    fig, ax = plt.subplots(figsize=(13, 6))

    # Global mean per year → anomaly relative to first year
    global_mean = np.nanmean(data, axis=0) * 1000
    global_mean -= global_mean[0]
    ax.plot(years, global_mean, 'k--', linewidth=2, label='Global mean', zorder=10)

    colors = plt.cm.tab10.colors
    for i, (city, (lon, lat)) in enumerate(TOURISM_CITIES.items()):
        idx = nearest_station(lon, lat, lons, lats)
        ts  = data[idx, :] * 1000
        if np.sum(~np.isnan(ts)) < 5:
            continue
        ts_anom = ts - np.nanmean(ts[:3])
        dist = np.sqrt((lons[idx]-lon)**2 + (lats[idx]-lat)**2)
        ax.plot(years, ts_anom, marker='o', markersize=3,
                color=colors[i % 10], linewidth=1.5,
                label=f"{city} ({dist:.1f}° from coast)")

    # Mark historical → future boundary
    if split_year and split_year in years:
        ax.axvline(split_year, color='red', linewidth=1.5, linestyle='--', alpha=0.7)
        ax.text(split_year + 0.3, ax.get_ylim()[0] + 5,
                '← Historical | Projected →', color='red', fontsize=8)

    ax.axhline(0, color='grey', linewidth=0.5, linestyle=':')
    ax.set_xlabel("Year")
    ax.set_ylabel("Sea level anomaly (mm, relative to baseline)")
    ax.set_title(f"Mean Sea Level Change — Vietnam Tourism Cities vs Global Mean\n"
                 f"{years[0]}–{years[-1]}  |  SSP5-8.5 future scenario")
    ax.legend(fontsize=8, loc='upper left')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("output_vietnam_timeseries.png", dpi=150, bbox_inches='tight')
    print("Saved → output_vietnam_timeseries.png")
    plt.show()


# ── Step 6: Vietnam zoom map with city trends ─────────────────────────────────
def plot_vietnam_zoom(lons, lats, trends, years):
    """Zoom into Vietnam, show station trends, annotate tourism cities."""
    # Filter to Vietnam region
    mask = ((lons >= VN_LON[0]) & (lons <= VN_LON[1]) &
            (lats >= VN_LAT[0]) & (lats <= VN_LAT[1]) &
            ~np.isnan(trends))

    fig, ax = plt.subplots(figsize=(8, 10))
    vmin, vmax = -10, 10
    norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
    cmap = plt.cm.RdBu_r

    sc = ax.scatter(lons[mask], lats[mask], c=trends[mask],
                    cmap=cmap, norm=norm, s=20, linewidths=0.3,
                    edgecolors='grey', alpha=0.85)
    plt.colorbar(sc, ax=ax, label="Sea level trend (mm/year)", shrink=0.7)

    # Tourism city markers
    city_colors = {'No data': 'grey'}
    for city, (lon, lat) in TOURISM_CITIES.items():
        idx   = nearest_station(lon, lat, lons, lats)
        trend = trends[idx]
        label = f"{city}\n{trend:.1f} mm/yr" if not np.isnan(trend) else f"{city}\nNo data"
        color = cmap(norm(trend)) if not np.isnan(trend) else 'grey'
        ax.plot(lon, lat, '*', markersize=14, color=color,
                markeredgecolor='black', markeredgewidth=0.8, zorder=10)
        ax.annotate(label, (lon, lat), textcoords="offset points",
                    xytext=(8, 4), fontsize=8,
                    bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.8))

    ax.set_xlim(VN_LON[0]-1, VN_LON[1]+1)
    ax.set_ylim(VN_LAT[0]-1, VN_LAT[1]+1)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(f"Sea Level Trend — Vietnam Coastal Region\n{years[0]}–{years[-1]}")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("output_vietnam_zoom.png", dpi=150, bbox_inches='tight')
    print("Saved → output_vietnam_zoom.png")
    plt.show()


# ── Step 7: Top rising/falling hotspots globally ──────────────────────────────
def print_hotspots(lons, lats, trends, top_n=10):
    valid = ~np.isnan(trends)
    idx_sorted = np.argsort(trends[valid])
    valid_idx  = np.where(valid)[0]

    print(f"\n── Top {top_n} fastest RISING coastal zones ──")
    for i in valid_idx[idx_sorted[-top_n:][::-1]]:
        print(f"  lon={lons[i]:7.2f}  lat={lats[i]:6.2f}  trend={trends[i]:+.2f} mm/yr")

    print(f"\n── Top {top_n} fastest FALLING coastal zones ──")
    for i in valid_idx[idx_sorted[:top_n]]:
        print(f"  lon={lons[i]:7.2f}  lat={lats[i]:6.2f}  trend={trends[i]:+.2f} mm/yr")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("hist_folder",   help="Folder with historical_msl_*.nc files")
    parser.add_argument("future_folder", nargs="?", default=None,
                        help="Optional folder with future_msl_*.nc files")
    args = parser.parse_args()

    lons, lats, years, data, split_year = load_all_years(args.hist_folder, args.future_folder)
    trends, r2 = compute_trends(data, years)

    plot_global_map(lons, lats, trends, years)
    plot_vietnam_timeseries(lons, lats, data, years, split_year)
    plot_vietnam_zoom(lons, lats, trends, years)
    print_hotspots(lons, lats, trends)
