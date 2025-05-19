import argparse
import json
import shutil
import hashlib
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


BUILD_PATH = Path("build")
PUBLIC_PATH = Path("public")
SRC_PATH = Path("src")


def calculate_file_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:8]


def render():
    BUILD_PATH.mkdir(exist_ok=True)

    with open("data.json", "r") as f:
        data = json.loads(f.read())

    style_css_path = BUILD_PATH / "style.css"
    if not style_css_path.exists():
        raise FileNotFoundError(f"style.css not found: {style_css_path}")

    style_hash = calculate_file_hash(style_css_path)

    env = Environment(loader=FileSystemLoader(SRC_PATH))
    template = env.get_template("index.html")
    rendered_content = template.render(style_hash=style_hash, **data)
    with open(BUILD_PATH / "index.html", "w") as f:
        f.write(rendered_content)

    print("Rendered")


def copy_public():
    BUILD_PATH.mkdir(exist_ok=True)

    shutil.copytree(PUBLIC_PATH, BUILD_PATH, dirs_exist_ok=True)


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
