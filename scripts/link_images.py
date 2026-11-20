import os, json, sqlite3, pathlib
base = pathlib.Path(__file__).parent.parent
db_path = base / "database" / "cyclus_milkyway_clone.db"
md_db_path = base / "database" / "cyclus_markdowns.db"
images_dir = base / "images"

# Link images to clone DB based on filename
# Usage: python scripts/link_images.py

conn = sqlite3.connect(md_db_path)
cur = conn.cursor()

for root, dirs, files in os.walk(images_dir):
    for f in files:
        if not f.lower().endswith(('.png','.jpg','.jpeg')):
            continue
        fp = pathlib.Path(root) / f
        rel = fp.relative_to(base)
        # Parse name: Parent_Body_type_batch_version.ext
        # Simple: body name is first two parts
        parts = f.replace('.png','').replace('.jpg','').split('_')
        body_name = parts[1] if len(parts)>1 else f
        # Try to find XYZ from clone DB
        clone_conn = sqlite3.connect(db_path)
        cc = clone_conn.cursor()
        # search in planets and stars
        cc.execute("SELECT x_ly_local, y_ly_local, z_ly_local, parent_star FROM planets WHERE name LIKE ?", (f"%{body_name}%",))
        row = cc.fetchone()
        if not row:
            cc.execute("SELECT x_ly_local, y_ly_local, z_ly_local, '' FROM stars WHERE name LIKE ?", (f"%{body_name}%",))
            row = cc.fetchone()
        clone_conn.close()
        x,y,z = row[:3] if row else (None,None,None)
        parent = row[3] if row and len(row)>3 else ''
        # Check sidecar JSON
        sidecar = fp.with_suffix('.json')
        prompt = ''
        source_chat = ''
        if sidecar.exists():
            try:
                j = json.loads(sidecar.read_text())
                prompt = j.get('source_prompt','')
                source_chat = j.get('source_chat','')
            except: pass
        cur.execute("INSERT OR REPLACE INTO images (body_name, file_path, type, batch, parent, source_chat, prompt, x_ly_local, y_ly_local, z_ly_local, linked) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (body_name, str(rel), 'unknown', 'unknown', parent, source_chat, prompt, x,y,z, 1 if row else 0))
        print(f"Linked {f} -> {body_name} XYZ={x},{y},{z}")

conn.commit()
conn.close()
print("Done linking images")
