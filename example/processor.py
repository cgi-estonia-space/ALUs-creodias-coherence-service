import os
import typer
from structlog import get_logger
from pathlib import Path
from xml.dom.minidom import parse

from eof.download import find_unique_safes
from eof.download import download_eofs

from demloader_get_from_aoi import get_from_aoi

log = get_logger()
runner_status_offset = 100


def main(
        input_dir: Path = typer.Option(...),
        output_dir: Path = typer.Option(...),
        config_file: Path = typer.Option(None),
):
    log.info("processing", input=str(input_dir), output=str(output_dir), config=config_file)

    safe_files = find_unique_safes(input_dir)
    if len(safe_files) != 2:
        log.error(
            "Expected 2 Sentinel-1 SAFE inputs, but %d were supplied. Coherence is calculated between pairs" % len(
                safe_files))
        raise typer.Exit(runner_status_offset)

    safe_files_list = sorted(safe_files, key=lambda x: x.date)
    orbit_types = ["precise", "restituted"]
    orbits = [None] * len(safe_files_list)
    orbit_slot = 0
    for ds in safe_files_list:
        for ot in orbit_types:
            orbit_file = download_eofs([ds.start_time], [ds.mission], None, output_dir, ot)
            if orbit_file is not None:
                orbits[orbit_slot] = orbit_file
                break
        orbit_slot += 1

    if any(o is None for o in orbits):
        log.error("Could not get the orbit files for all scenes.")
        raise typer.Exit(runner_status_offset + 1)

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
    copdem_location = str(input_dir) + "/../dem/"
    copdem_paths = [copdem_location + x + ".tif" for x in copdems]
    log.info("COPDEMs covered %s" % str(copdem_paths))

    polarization = ["VV"]
    dem_files = ["--dem " + copdem_location + "srtm_37_02.tif",
                 "--dem " + copdem_location + "srtm_37_03.tif",
                 "--dem " + copdem_location + "srtm_38_02.tif",
                 "--dem " + copdem_location + "srtm_38_03.tif"]
    dem_args = " ".join(dem_files)
    command = f"alus-coh -r {safe_files_list[0].filename} -s {safe_files_list[1].filename} --orbit_ref {orbits[0][0]} \
              --orbit_sec {orbits[1][0]} -p {polarization[0]} --no_mask_cor -o {output_dir} \
              {dem_args}"
    res_val = os.system(command)
    if res_val != 0:
        raise typer.Exit(res_val)


if __name__ == "__main__":
    typer.run(main)
