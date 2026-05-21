#!/bin/bash
# Run this ONCE to clean up the root folder before git init
# It removes old/duplicate files that are now in src/ and outputs/

# Remove root-level scripts (now in src/)
rm -f drought_analysis.py sea_level_analysis.py draw_vietnam_map.py
rm -f vietnam_risk_analysis.py inspect_nc.py
rm -f readinimage.py display_image.py

# Remove root-level outputs (now in outputs/)
rm -f output_*.png

# Remove old files
rm -f coffee.jpg drought_map.png Screenshot*.jpg
rm -f *.code-workspace

# Remove old GeoTIFF files (data is in drought_data/ as NetCDF now)
rm -f rdria_m_gdo_*.tif

echo "Done. Ready for: git init && git add . && git commit -m 'Initial commit'"
