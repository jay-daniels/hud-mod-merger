import os
import shutil
import zipfile
from pathlib import Path

# Conflict definitions
CONFLICTS = {
    "sleekmodularhud_noPBIndicators": "sleekmodularhud_noCompassBorders",
    "sleekmodularhud_noCrimeRabbit": "sleekmodularhud_noCrimeStealth",
    "sleekmodularhud_noCursor": "sleekmodularhud_noNormalCursor",
    "sleekmodularhud_noLetterbox": "sleekmodularhud_noLetterbox4k",
}

# Priority replacement
IGNORE_IF_PRESENT = {"sleekmodularhud_ultrawide": "sleekmodularhud_noLetterbox4k"}

# Base directories
directory = Path.cwd()
merged_mod = directory / "sleekmodularhudMerged"
merged_cfg_path = merged_mod / "mod.cfg"
merged_pak_path = merged_mod / "Data" / "smhudmerged.pak"

# Remove existing merged mod folder
shutil.rmtree(merged_mod, ignore_errors=True)

# Find valid mods, ignoring the merged folder itself
valid_mods = {
    folder.name: folder
    for folder in directory.iterdir()
    if folder.is_dir() and folder.name != "sleekmodularhudMerged"
    and (folder / "mod.cfg").exists() or any((folder / "Data").glob("*.pak"))
}

# Detect conflicts
conflict_found = {(c1, c2) for c1, c2 in CONFLICTS.items() if c1 in valid_mods and c2 in valid_mods}

# Resolve conflicts
mods_to_merge = set(valid_mods.keys())
for c1, c2 in conflict_found:
    while (choice := input(f"Conflict detected: {c1} vs {c2}. Choose (1={c1}, 2={c2}, 3=Neither): ")) not in ["1", "2", "3"]:
        pass
    if choice == "1":
        mods_to_merge.discard(c2)
    elif choice == "2":
        mods_to_merge.discard(c1)
    else:
        mods_to_merge.discard(c1)
        mods_to_merge.discard(c2)

# Apply ignore rule
for mod, replacement in IGNORE_IF_PRESENT.items():
    if mod in mods_to_merge and replacement in mods_to_merge:
        mods_to_merge.remove(mod)

# Create merged mod directory
(merged_mod / "Data").mkdir(parents=True, exist_ok=True)

# Merge mod.cfg files
merged_cfg = {
    line.strip() for mod in mods_to_merge if (cfg_path := valid_mods[mod] / "mod.cfg").exists()
    for line in cfg_path.read_text(encoding="utf-8").splitlines() if line.strip()
}

merged_cfg_path.write_text("\n".join(sorted(merged_cfg)), encoding="utf-8")

# Extract and merge .pak files
def unpack_and_merge(pak_files, output_pak):
    temp_unpack_dir = directory / "temp_unpack"
    shutil.rmtree(temp_unpack_dir, ignore_errors=True)
    temp_unpack_dir.mkdir(exist_ok=True)

    for pak in pak_files:
        with zipfile.ZipFile(pak, 'r') as zip_ref:
            zip_ref.extractall(temp_unpack_dir)

    with zipfile.ZipFile(output_pak, 'w', zipfile.ZIP_DEFLATED) as zip_out:
        for file_path in temp_unpack_dir.rglob("*"):
            if file_path.is_file():
                zip_out.write(file_path, file_path.relative_to(temp_unpack_dir))

    shutil.rmtree(temp_unpack_dir)

unpack_and_merge([p for mod in mods_to_merge for p in (valid_mods[mod] / "Data").glob("*.pak")], merged_pak_path)

print("Merging completed successfully!")
