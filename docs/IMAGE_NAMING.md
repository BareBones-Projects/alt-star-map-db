# CYCLUS Image Naming & Source Tying

## Naming Convention

Format: `{parent}_{body}_{type}_{batch}_{version}.png`

Examples:
- `Sol_Earth_planet_B1_v01.png` - Earth from Batch 1
- `Sol_Luna_moon_B1_v01.png` - Luna
- `Trappist-1_e_planet_B1_CORE_v02.png` - Trappist-1 e CYCLUS CORE
- `Trappist-1_e_Cyclus-Prime-Luna_moon_B1_v01.png` - Moon of Trappist-1 e
- `GJ-5000_b_planet_B2_v01.png` - Procedural planet
- `HD-300001_1_moon_B2_v01.png` - Procedural moon

Rules:
1. Use exact name from CSV but replace spaces with `-` or `_` - keep parent linkage
2. Always include type: star, planet, moon
3. Include batch: B1, B2, B3, B4 etc for traceability
4. Version: v01, v02 for iterations
5. Special tags: CORE, HAB, HOME for important bodies

## Folder Structure

```
images/
  stars/
    Sol_star_B1_v01.png
    Trappist-1_star_B1_CORE_v01.png
    GJ-5000_star_B2_v01.png
  planets/
    Sol_Earth_planet_B1_HOME_v01.png
    Trappist-1_e_planet_B1_CORE_v02.png
    GJ-5000_b_planet_B2_v01.png
  moons/
    Earth_Luna_moon_B1_v01.png
    Trappist-1_e_Cyclus-Prime-Luna_moon_B1_v01.png
```

## Tying Source Image from Other Chat

When you create a planet image in another chat, you need to tie it back to the database entry:

### Method 1: Filename = Database Key

1. In other chat, when you generate planet image, name it using convention above BEFORE uploading
2. Example: You create "Lava world around GJ-5000" in other chat -> name file `GJ-5000_b_planet_B2_v01.png`
3. Upload to this repo's `images/planets/` folder
4. The filename IS the foreign key to CSV: `GJ-5000_b` exists in `cyclus_BATCH2_2500_planets.csv`

### Method 2: Sidecar JSON (recommended for other chat workflow)

Create a sidecar JSON with same name as image:

`GJ-5000_b_planet_B2_v01.json`:
```json
{
  "name": "GJ-5000 b",
  "parent": "GJ-5000",
  "type": "planet",
  "batch": "BATCH2",
  "x_ly_local": 45.2,
  "y_ly_local": -12.1,
  "z_ly_local": 33.4,
  "body_class": "lava",
  "notes": "Created in other chat - lava world",
  "source_chat": "Chat ID or date",
  "source_prompt": "Lava world with 2 moons, tidally locked",
  "image_file": "GJ-5000_b_planet_B2_v01.png",
  "version": "v01",
  "created": "2026-10-27"
}
```

### Method 3: Database Link (for markdown database)

Insert into `images` table in `cyclus_markdowns.db`:

```sql
INSERT INTO images (body_name, file_path, type, batch, source_chat, prompt, version)
VALUES ('GJ-5000 b', 'images/planets/GJ-5000_b_planet_B2_v01.png', 'planet', 'BATCH2', 'Other chat 2026-10-27', 'Lava world prompt', 'v01');
```

### Workflow for Other Chat

1. Other chat: Generate planet image -> Download
2. Rename using convention: `{Parent}_{Body}_{type}_{Batch}_v01.png`
3. Create sidecar JSON with XYZ from CSV
4. Copy both to this repo's images/ folder
5. Run: `python scripts/link_images.py` (will be provided) to auto-update database

### Script to Link Images (save as scripts/link_images.py)

```python
import os, json, sqlite3
# Scans images/ and auto-links to cyclus_milkyway_clone.db based on filename
```

This way, any image created anywhere can be traced back to exact XYZ coordinate in the clone database.

## Git LFS

For large images, use Git LFS:
```
git lfs track "*.png"
git lfs track "*.jpg"
```

## Example: Trappist-1 e (CYCLUS CORE)

Database entry: `Trappist-1 e` in `cyclus_BATCH1_2500_planets.csv`
- XYZ: 18.200029, 30.5, 12.1 ly
- Image: `images/planets/Trappist-1_e_planet_B1_CORE_v01.png`
- Sidecar: `images/planets/Trappist-1_e_planet_B1_CORE_v01.json`
- Viewer will auto-load image if filename matches body name
