import argparse
import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


BUILD_PATH = Path("build")
PUBLIC_PATH = Path("public")
SRC_PATH = Path("src")


def render():
    BUILD_PATH.mkdir(exist_ok=True)

    with open("data.json", "r") as f:
        data = json.loads(f.read())

    env = Environment(loader=FileSystemLoader(SRC_PATH))
    template = env.get_template("index.html")
    rendered_content = template.render(**data)
    with open(BUILD_PATH / "index.html", "w") as f:
        f.write(rendered_content)

    print("Rendered")


def copy_public():
    BUILD_PATH.mkdir(exist_ok=True)

    for f in PUBLIC_PATH.iterdir():
        shutil.copy(f, BUILD_PATH / f.name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true")

    args = parser.parse_args()

    copy_public()

    if args.watch:
        from watchfiles import watch

        print("Watching for changes. Press Ctrl+C to stop.")

        render()

        paths_to_watch = ["data.json", str(SRC_PATH)]
        for changes in watch(*paths_to_watch):
            print(f"Changes detected: {changes}")
            try:
                render()
            except Exception as e:
                print(f"Error rendering: {e}")
    else:
        render()


if __name__ == "__main__":
    main()
