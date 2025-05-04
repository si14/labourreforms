tailwind-watch:
    npx @tailwindcss/cli -i ./src/style.css -o ./build/style.css --watch

build:
    rm -rf build
    uv run python render.py
    npx @tailwindcss/cli -i ./src/style.css -o ./build/style.css --minify

refresh-data:
    uv run python data_pull.py
    uv run python data_process.py
