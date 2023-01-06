import os
import typer
from structlog import get_logger
from pathlib import Path

from eof.download import find_unique_safes
from eof.download import download_eofs

log = get_logger()
runner_status_offset = 100


def main(
        input_dir: Path = typer.Option(...),
        output_dir: Path = typer.Option(...),
        config_file: Path = typer.Option(...),
):
    log.info("processing", input=str(input_dir), output=str(output_dir), config=config_file)

    safe_files = find_unique_safes(input_dir)
    if len(safe_files) != 2:
        log.error(
            "Expected 2 Sentinel-1 SAFE inputs, but %d were supplied. Coherence is calculated between pairs" % len(
                safe_files))
        return runner_status_offset

    safe_files_list = sorted(safe_files, key=lambda x: (x.date))
    orbit_types = ["precise", "restituted"]
    orbits = [None] * len(safe_files_list)
    # reference_orbit = download_eofs(reference_scene.start_time, reference_scene.mission, )
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
        return runner_status_offset + 1

    polarization = ["VV"]
    dem_files = ["--dem /mnt/vol/dem/srtm_37_02.tif",
                 "--dem /mnt/vol/dem/srtm_37_03.tif",
                 "--dem /mnt/vol/dem/srtm_38_02.tif",
                 "--dem /mnt/vol/dem/srtm_38_03.tif"]
    dem_args = " ".join(dem_files)
    command = f"alus-coh -r {safe_files_list[0].filename} -s {safe_files_list[1].filename} --orbit_ref {orbits[0][0]} \
              --orbit_sec {orbits[1][0]} -p {polarization[0]} --no_mask_cor --log_format_creodias -o {output_dir} \
              {dem_args}"
    os.system(command)
    # os.system(f"mkdir {output_dir}/my_new_product_name")
    # os.system(f"touch {output_dir}/my_new_product_name/result.data")
    # os.system(f"ls -R {input_dir}")
    # os.system(f"ls -R {output_dir}")


if __name__ == "__main__":
    typer.run(main)
