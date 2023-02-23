import glob
import os
import typer
import structlog
from pathlib import Path

from eof.download import find_unique_safes
import structlog_cloudferro


structlog_cloudferro.setup_logging()
log = structlog.getLogger("app")
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

    polarization = ["VV"]
    dem_files = glob.glob(os.path.join(input_dir, "*.tif"))
    dem_args = ["--dem " + x + " " for x in dem_files]
    dem_args = " ".join(dem_args)
    command = f"alus-coh -r {safe_files_list[0].filename} -s {safe_files_list[1].filename} --orbit_dir {input_dir} \
              -p {polarization[0]} --no_mask_cor -o {output_dir} {dem_args} --log_format_creodias"
    log.info(command)
    res_val = os.system(command)
    if res_val != 0:
        raise typer.Exit(res_val)

    log.info("Converting result to COG")
    results = glob.glob(os.path.join(output_dir, "S1*.tif"))
    output_filename = results[0]
    command = f"gdaladdo -r average {output_filename} 2 4 8 16"
    res_val = os.system(command + " > /dev/null 2>&1")
    if res_val != 0:
        raise typer.Exit(res_val)

    cog_filename = output_filename[:-4] + "_cog.tif"
    command = f"gdal_translate {output_filename} {cog_filename} \
                -co COMPRESS=LZW -co TILED=YES -co COPY_SRC_OVERVIEWS=YES"
    res_val = os.system(command + " > /dev/null 2>&1")
    if res_val != 0:
        raise typer.Exit(res_val)
    log.info("Final result - " + cog_filename)


if __name__ == "__main__":
    typer.run(main)
