#!/usr/bin/env sh
# Regenerates the JLCPCB production files (BOM, pick-and-place, gerbers) directly from a
# <board>.kicad_pcb, using the actual Fabrication Toolkit plugin
# (github.com/bennymeg/Fabrication-Toolkit - the same plugin KiCad's own Plugin & Content
# Manager distributes, run here via its documented headless CLI instead of the GUI dialog) run
# non-interactively. This replaces the old workflow of clicking the plugin's toolbar button
# inside a local KiCad install. Run from the repo root after any layout change:
#
#     tools/generate_jlcpcb_bom.sh [board-name]
#
# board-name defaults to "SunSproutHub" (the main board). Pass an alternate board's
# base filename to generate its production files instead - output goes to jlcpcb<suffix>/
# where <suffix> is whatever follows "SunSproutHub" in the name, keeping each board's
# production files separate rather than overwriting one with another's.
#
# Only prerequisite is Docker - no local KiCad install needed. Reuses the same
# tools/kicad-ci.Dockerfile image as tools/run_kicad_validation.sh (see that Dockerfile for why
# it needs this project's private vendor-library repo, supplied the same way via `gh auth
# token`).
#
# Refreshes <prod_dir>/ and <gerber_dir>/ in place:
#   - <prod_dir>/BOM-<board-name>.csv   (the plugin's native bom.csv, as-is - columns/header
#     come straight from Fabrication Toolkit 5.3.1, which uses "LCSC Part #", matching JLCPCB's
#     actual required upload header more closely than this repo's old file)
#   - <prod_dir>/CPL-<board-name>.csv   (the plugin's native positions.csv)
#   - <prod_dir>/IPC-<board-name>.ipc   (IPC netlist, new - wasn't previously kept, useful for
#     assembly verification)
#   - <prod_dir>/GERBER-<board-name>.zip
#   - <gerber_dir>/*                    (unzipped from the above)
#
# Note: for the main board, jlcpcb/gerber/ file names change from this run on. The old files
# used a "-CuBottom.gbr"-style ad-hoc naming (from a one-off manual KiCad Plot export); the
# plugin's native output uses the standard Protel/Extended-Gerber extensions JLCPCB itself
# recommends (.gtl/.gbl/.gts/.gbs/.gto/.gbo/.gtp/.gbp/.gm1/.g1-.g4, .drl) - kept as-is here
# rather than fought into the old convention, since it's the more standard/correct naming.
#
# After this runs, tools/validation/check_jlcpcb_pricing.py runs automatically against the
# fresh BOM - it can also be re-run standalone later (no Docker/KiCad needed) to re-check
# pricing without regenerating the BOM, or used via tools/validation/compare_bom_pricing.py to
# diff two boards' BOMs.

set -eu

BOARD_NAME="${1:-SunSproutHub}"
HUB_DIR="hardware/hub"
IMAGE="sunsprout-kicad-ci:10.0.0"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# jlcpcb/ is the established convention for the main board; any other board gets its own
# jlcpcb<suffix>/ so runs for different boards never clobber each other.
SUFFIX="${BOARD_NAME#SunSproutHub}"
PROD_DIR="jlcpcb${SUFFIX}/production_files"
GERBER_DIR="jlcpcb${SUFFIX}/gerber"
# Fabrication Toolkit's own fixed output-folder name, written under the board's project
# directory - i.e. the repo root when /work is the mount point. Gitignored, so a failed run
# never shows up as repo noise; cleaned up at the end either way.
SCRATCH_OUT="$REPO_ROOT/production"

BUILD_CONTEXT="$REPO_ROOT/tools"
case "$(uname -s 2>/dev/null)" in
	MINGW*|MSYS*)
		export MSYS_NO_PATHCONV=1
		BUILD_CONTEXT="$(cd "$REPO_ROOT/tools" && pwd -W)"
		;;
esac

if [ ! -f "$REPO_ROOT/$HUB_DIR/$BOARD_NAME.kicad_pcb" ]; then
	echo "No such board: $REPO_ROOT/$HUB_DIR/$BOARD_NAME.kicad_pcb" >&2
	exit 1
fi

GITHUB_TOKEN="$(gh auth token 2>/dev/null || true)"
export GITHUB_TOKEN
export DOCKER_BUILDKIT=1

echo "== Building KiCad CI image (cached after first run) =="
if [ -n "$GITHUB_TOKEN" ]; then
	docker build --secret id=github_token,env=GITHUB_TOKEN \
		-f "$BUILD_CONTEXT/kicad-ci.Dockerfile" -t "$IMAGE" "$BUILD_CONTEXT"
else
	echo "No 'gh auth token' available - building without the private vendor-library repo"
	docker build -f "$BUILD_CONTEXT/kicad-ci.Dockerfile" -t "$IMAGE" "$BUILD_CONTEXT"
fi

rm -rf "$SCRATCH_OUT"

echo "== Running Fabrication Toolkit (headless CLI, non-interactive) on $BOARD_NAME.kicad_pcb =="
docker run --rm -v "$REPO_ROOT:/work" -w /opt/fabrication-toolkit "$IMAGE" sh -c \
	"xvfb-run -a -s '-screen 0 1024x768x24' python3 -m plugins.cli --path /work/$HUB_DIR/$BOARD_NAME.kicad_pcb --autoTranslate --autoFill --excludeDNP --nonInteractive"

if [ ! -d "$SCRATCH_OUT" ]; then
	echo "Fabrication Toolkit did not produce a production/ output - aborting, $PROD_DIR left untouched" >&2
	exit 1
fi

echo "== Normalizing output into $PROD_DIR/ and $GERBER_DIR/ =="
mkdir -p "$REPO_ROOT/$PROD_DIR"
cp "$SCRATCH_OUT/bom.csv" "$REPO_ROOT/$PROD_DIR/BOM-$BOARD_NAME.csv"
cp "$SCRATCH_OUT/positions.csv" "$REPO_ROOT/$PROD_DIR/CPL-$BOARD_NAME.csv"
[ -f "$SCRATCH_OUT/netlist.ipc" ] && \
	cp "$SCRATCH_OUT/netlist.ipc" "$REPO_ROOT/$PROD_DIR/IPC-$BOARD_NAME.ipc"

GERBER_ZIP="$(find "$SCRATCH_OUT" -maxdepth 1 -name '*.zip' | head -n1)"
if [ -z "$GERBER_ZIP" ]; then
	echo "No gerber archive found in Fabrication Toolkit output - aborting" >&2
	rm -rf "$SCRATCH_OUT"
	exit 1
fi
cp "$GERBER_ZIP" "$REPO_ROOT/$PROD_DIR/GERBER-$BOARD_NAME.zip"

rm -rf "$REPO_ROOT/$GERBER_DIR"
mkdir -p "$REPO_ROOT/$GERBER_DIR"
unzip -o -q "$GERBER_ZIP" -d "$REPO_ROOT/$GERBER_DIR"

rm -rf "$SCRATCH_OUT"

echo "== Done. Refreshed: =="
echo "  $PROD_DIR/BOM-$BOARD_NAME.csv"
echo "  $PROD_DIR/CPL-$BOARD_NAME.csv"
echo "  $PROD_DIR/IPC-$BOARD_NAME.ipc"
echo "  $PROD_DIR/GERBER-$BOARD_NAME.zip"
echo "  $GERBER_DIR/*"

echo
echo "== Checking current JLCPCB pricing for the fresh BOM =="
# cd + relative paths here rather than passing $REPO_ROOT's POSIX-style path straight to
# python3: that's fine for `docker run -v` above (Docker's CLI accepts it) but python3 itself
# is a native Windows exe on MSYS/git-bash and can't resolve a bare /c/... path argument.
(cd "$REPO_ROOT" && python3 "tools/validation/check_jlcpcb_pricing.py" \
	"$PROD_DIR/BOM-$BOARD_NAME.csv")
