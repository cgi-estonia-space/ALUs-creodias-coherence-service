import os
import typer
from structlog import get_logger
from pathlib import Path


log = get_logger()


def main(
    input: Path = typer.Option(...),
    output: Path = typer.Option(...),
    config_file: Path = typer.Option(None),
):
    log.info("processing", input=str(input), output=str(output), config=config_file)

    os.system(f"mkdir {output}")
    os.system(f"mkdir {output}/my_new_product_name")
    os.system(f"touch {output}/my_new_product_name/result.data")
    os.system(f"ls -R {input}")
    os.system(f"ls -R {output}")



if __name__ == "__main__":
    typer.run(main)
