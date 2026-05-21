#!/usr/bin/python3
"""Draw a clean Vietnam map with tourism city markers using cartopy."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Try cartopy first, fall back to plain matplotlib scatter if not installed
try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    HAS_CARTOPY = True
except ImportError:
    HAS_CARTOPY = False

TOURISM_CITIES = {
    "Hanoi":            (105.85, 21.03),
    "Hue":              (107.59, 16.46),
    "Da Nang":          (108.22, 16.07),
    "Hoi An":           (108.33, 15.88),
    "Nha Trang":        (109.19, 12.24),
    "Ho Chi Minh City": (106.66, 10.82),
    "Phu Quoc":         (103.96, 10.29),
}

VN_LON = (102.0, 110.5)
VN_LAT = (8.0,   23.5)

# Offset labels so they don't overlap the markers
LABEL_OFFSETS = {
    "Hanoi":            (-3.2,  0.2),
    "Hue":              ( 0.2,  0.3),
    "Da Nang":          ( 0.2, -0.6),
    "Hoi An":           ( 0.2, -0.6),
    "Nha Trang":        ( 0.2,  0.3),
    "Ho Chi Minh City": ( 0.2,  0.3),
    "Phu Quoc":         (-3.8,  0.2),
}

if HAS_CARTOPY:
    fig = plt.figure(figsize=(7, 11))
    ax  = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.set_extent([VN_LON[0], VN_LON[1], VN_LAT[0], VN_LAT[1]], crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.LAND,       facecolor='#e8f4e8', edgecolor='none')
    ax.add_feature(cfeature.OCEAN,      facecolor='#cce5f0')
    ax.add_feature(cfeature.COASTLINE,  linewidth=0.8, edgecolor='#555')
    ax.add_feature(cfeature.BORDERS,    linewidth=0.6, edgecolor='#888', linestyle='--')
    ax.add_feature(cfeature.RIVERS,     linewidth=0.4, edgecolor='#7ec8e3', alpha=0.6)

    gl = ax.gridlines(draw_labels=True, linewidth=0.4, color='grey',
                      alpha=0.5, linestyle=':')
    gl.top_labels = False
    gl.right_labels = False

    for city, (lon, lat) in TOURISM_CITIES.items():
        ax.plot(lon, lat, 'o', color='#e63946', markersize=8,
                markeredgecolor='white', markeredgewidth=1.2,
                transform=ccrs.PlateCarree(), zorder=5)
        dx, dy = LABEL_OFFSETS.get(city, (0.2, 0.2))
        ax.text(lon + dx, lat + dy, f"{city}\n({lon}°E, {lat}°N)",
                fontsize=7.5, transform=ccrs.PlateCarree(),
                bbox=dict(boxstyle='round,pad=0.25', fc='white', alpha=0.85, ec='#ccc'),
                zorder=6)

else:
    # Fallback: plain matplotlib, no cartopy needed
    fig, ax = plt.subplots(figsize=(7, 11))
    ax.set_xlim(VN_LON[0], VN_LON[1])
    ax.set_ylim(VN_LAT[0], VN_LAT[1])
    ax.set_facecolor('#cce5f0')
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.grid(True, linewidth=0.4, color='grey', alpha=0.5, linestyle=':')

    # Draw a rough Vietnam land polygon approximation
    vn_coast_lon = [104.8,105.2,106.0,107.5,108.5,109.5,109.2,108.8,
                    108.2,107.5,106.5,105.5,104.5,103.5,102.5,102.1,
                    102.5,103.0,103.5,104.0,104.8]
    vn_coast_lat = [10.4, 10.0, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5,
                    16.0, 16.5, 17.5, 18.5, 19.5, 20.5, 21.5, 22.5,
                    23.0, 23.4, 22.5, 21.0, 10.4]
    ax.fill(vn_coast_lon, vn_coast_lat, color='#e8f4e8', zorder=1)
    ax.plot(vn_coast_lon, vn_coast_lat, color='#555', linewidth=0.8, zorder=2)

    for city, (lon, lat) in TOURISM_CITIES.items():
        ax.plot(lon, lat, 'o', color='#e63946', markersize=9,
                markeredgecolor='white', markeredgewidth=1.2, zorder=5)
        dx, dy = LABEL_OFFSETS.get(city, (0.2, 0.2))
        ax.text(lon + dx, lat + dy, f"{city}\n({lon}°E, {lat}°N)",
                fontsize=7.5,
                bbox=dict(boxstyle='round,pad=0.25', fc='white', alpha=0.85, ec='#ccc'),
                zorder=6)

ax.set_title("Vietnam — Tourism Cities Used in Analysis\n"
             "Bounding box: 102.0–110.5°E, 8.0–23.5°N",
             fontsize=11, pad=12)

plt.tight_layout()
plt.savefig("output_vietnam_map.png", dpi=180, bbox_inches='tight')
print("Saved → output_vietnam_map.png")
plt.show()
