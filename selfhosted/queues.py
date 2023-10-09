import pathlib

import click
import yaml

CONFIG = pathlib.Path(__file__).parent / "queues.yml"


@click.command()
@click.argument("name", type=str)
def main(name):
    data = yaml.safe_load(CONFIG.read_text())
    print(data[name])


if __name__ == "__main__":
    main()
