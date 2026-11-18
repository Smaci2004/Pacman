set -euo pipefail

VENV=".venv"
PY="${VENV}/bin/python"
PIP="${VENV}/bin/pip"
RELEASE="release"

if [ ! -d "${VENV}" ]; then
    python3 -m venv "${VENV}"
fi

"${PIP}" install --upgrade pip
"${PIP}" install utils/mazegenerator-00001-py3-none-any.whl
"${PIP}" install -r requirements.txt
"${PIP}" install pyinstaller

# Build the standalone executable.
"${VENV}/bin/pyinstaller" --clean --noconfirm pacman.spec

# Stage release contents.
rm -rf "${RELEASE}"
mkdir -p "${RELEASE}"
cp dist/pacman "${RELEASE}/" 2>/dev/null || cp -r dist/pacman "${RELEASE}/"
cp config.json "${RELEASE}/"
cat > "${RELEASE}/README.txt" <<'INFO'
Pac-Man
=======
Run the 'pacman' executable to play.

Controls
  Move ........ Arrow keys or W A S D
  Pause ....... P
  Back/Quit ... ESC

Menu
  SPACE start, I instructions, H highscores, ESC exit

Cheats (in game, for reviewers)
  C invincible   F freeze ghosts   N skip level   L extra life

Configuration
  Edit config.json next to the executable to change levels, lives,
  maze size, timing and scoring. Lines starting with # or // are
  comments. Invalid values fall back to safe defaults.
INFO

# Zip for upload.
( cd "${RELEASE}" && zip -r "../pacman-release.zip" . >/dev/null )
echo "Built: pacman-release.zip (upload this as an unlisted Itch.io build)"
