import argparse
import json
import pathlib

parser = argparse.ArgumentParser()
parser.add_argument("name", type=str, help="Name of the platform.")


def main(name):
    with open(pathlib.Path(__file__).parent.parent / "queues.json") as file:
        data = json.load(file)
    print(data[name])


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.name)
