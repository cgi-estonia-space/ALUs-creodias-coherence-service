import json
import os
from pathlib import Path
import structlog
import typer
from xml.dom.minidom import parse

from demloader_get_from_aoi import get_from_aoi
from eof.download import find_unique_safes
from eof.products import Sentinel, SentinelOrbit
import structlog_cloudferro

structlog_cloudferro.setup_logging()
log = structlog.getLogger("app")


def main(
        input_dir: Path = typer.Option(...),
        output_dir: Path = typer.Option(...),
        config_file: Path = typer.Option(None),
):
    log.info("processing")

    safe_files = find_unique_safes(input_dir)
    if len(safe_files) != 2:
        log.error(
            "Expected 2 Sentinel-1 SAFE inputs, but %d were supplied. Coherence is calculated between pairs" % len(
                safe_files))
        raise typer.Exit(1)

    orbit_types = ["poeorb", "resorb"]
    orbits = []
    for ds in safe_files:
        acq_start = ds.start_time
        acq_end = ds.stop_time
        found = False
        for ot in orbit_types:
            if found:
                break
            with open(str(input_dir) + "/" + ot + ".txt") as ofl:
                entries = ofl.readlines()
                for e in entries:
                    e = e.rstrip('\n')
                    fn = os.path.basename(e)
                    so = SentinelOrbit(fn)
                    so_start = so.start_time
                    so_end = so.stop_time
                    if so_start <= acq_start <= so_end and so_start <= acq_end <= so_end:
                        orbits.append(e)
                        found = True
                        break

    safe_files_list = sorted(safe_files, key=lambda x: x.date)
    reference_manifest = parse(safe_files_list[0].filename + "/manifest.safe")
    reference_boundaries = reference_manifest.getElementsByTagName("gml:coordinates")[0].firstChild.data
    boundary_points = reference_boundaries.split(" ")
    lons = []
    lats = []
    for p in boundary_points:
        items = p.split(",")
        lons.append(float(items[1]) + 180)
        lats.append(float(items[0]))

    lons = sorted(lons)
    lons = [x - 180 for x in lons]
    lats = sorted(lats)
    copdems = get_from_aoi([lons[0], lats[0], lons[3], lats[3]], 30)
    copdems = [x + "/" + x + ".tif" for x in copdems]

    conf_out = {"orbit": orbits, "dem": copdems}
    conf_json = json.dumps(conf_out, indent=4)
    with open(str(output_dir) + "/aux.json", 'w')as co:
        co.write(conf_json)


if __name__ == "__main__":
    typer.run(main)
