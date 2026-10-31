#!/usr/bin/env python3
# Extract and repack omni jars. One copy, both patch scripts use it.
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


def require_paths():
    if len(sys.argv) < 3:
        raise SystemExit("Usage: {} ROOT BUILD".format(Path(sys.argv[0]).name))
    return Path(sys.argv[1]), Path(sys.argv[2])


def extract(jar, work, label="theme"):
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    # unzip warns on the omni layout. Files still extract.
    subprocess.run(["unzip", "-q", "-o", str(jar), "-d", str(work)])
    if not (work / "chrome").exists():
        raise SystemExit(f"{label}: extract failed for {jar.name}")


def replace(jar, work):
    new_jar = work.with_name(jar.name + ".new")
    if new_jar.exists():
        new_jar.unlink()
    with zipfile.ZipFile(new_jar, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, dirnames, filenames in os.walk(work):
            dirnames.sort()
            for fn in sorted(filenames):
                full = Path(dirpath) / fn
                z.write(full, full.relative_to(work).as_posix())
    os.replace(new_jar, jar)
    shutil.rmtree(work)
