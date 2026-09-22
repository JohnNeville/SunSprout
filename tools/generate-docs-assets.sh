#!/usr/bin/env sh
# Regenerates the docs-site assets that are derived from the KiCad source files, so they never
# go stale relative to hardware/hub/SunSproutHub.kicad_sch / .kicad_pcb. Run from the repo root after
# any schematic or layout change you want reflected on the docs site:
#
#     tools/generate-docs-assets.sh
#
# Only prerequisite is Docker - no local KiCad install needed. Builds a local image on top of
# the official KiCad CI image (ghcr.io/kicad/kicad:10.0.0, pinned to match the version this
# project is developed against) that also bundles: KiCad's official 3D model library
# (kicad-packages3D), this project's private vendor-library repo
# (batterypowerboard-kicad-libraries, for the parts kicad-packages3D doesn't cover - the MCU
# module, both 8P8C jacks, the USB-C receptacle), and InteractiveHtmlBom. See
# tools/kicad-assets.Dockerfile for details - first build pulls several GB and is slow; cached
# by Docker after that.
#
# The private-repo clone needs a GitHub token with read access to that repo, supplied below via
# `gh auth token` as a Docker build secret (never baked into an image layer). If `gh` isn't
# installed/authenticated, the build still succeeds - that one layer is skipped and the parts it
# would've covered just render bodyless, same as before that repo existed.
#
# None of this is needed just to get correct (if partially bodyless) exports in the first place:
# KiCad embeds full symbol/footprint geometry directly in .kicad_sch/.kicad_pcb at placement
# time, so exporting/rendering an already-placed design never depended on any of these libraries
# resolving - only on their 3D *visual* models, which is what these layers restore.
#
# Everything this script produces is a build artifact of the .kicad_sch/.kicad_pcb - regenerate
# it, don't hand-edit the outputs.

set -eu

IMAGE="sunsprout-kicad-assets:10.0.0"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMG_DIR="website/static/img"
STATIC_DIR="website/static"
HUB_DIR="hardware/hub"
SAT_DIR="hardware/satellite"

# On Windows git-bash (MSYS), bash rewrites args that look like absolute Unix paths (e.g. the
# container's /work below) into Windows paths before docker.exe ever sees them - this disables
# that for the `docker run` calls, which need /work to stay literal. `docker build`'s context
# argument is the opposite: it needs an actual Windows-style path even with conversion
# disabled, unlike -v/-w, which Docker's CLI accepts fine in POSIX form. Both are no-ops on
# real Linux/Mac/WSL.
BUILD_CONTEXT="$REPO_ROOT/tools"
case "$(uname -s 2>/dev/null)" in
	MINGW*|MSYS*)
		export MSYS_NO_PATHCONV=1
		BUILD_CONTEXT="$(cd "$REPO_ROOT/tools" && pwd -W)"
		;;
esac

GITHUB_TOKEN="$(gh auth token 2>/dev/null || true)"
export GITHUB_TOKEN
export DOCKER_BUILDKIT=1

echo "== Building KiCad+3D-models+IBOM image (cached after first run) =="
if [ -n "$GITHUB_TOKEN" ]; then
	docker build --secret id=github_token,env=GITHUB_TOKEN \
		-f "$BUILD_CONTEXT/kicad-assets.Dockerfile" -t "$IMAGE" "$BUILD_CONTEXT"
else
	echo "No 'gh auth token' available - building without batterypowerboard-kicad-libraries"
	docker build -f "$BUILD_CONTEXT/kicad-assets.Dockerfile" -t "$IMAGE" "$BUILD_CONTEXT"
fi

mkdir -p "$REPO_ROOT/$IMG_DIR"

run_kicad_cli() {
	docker run --rm -v "$REPO_ROOT:/work" -w /work "$IMAGE" kicad-cli "$@"
}

echo "== Hub Board render (top - orthographic for pinout & docs) =="
run_kicad_cli pcb render "$HUB_DIR/SunSproutHub.kicad_pcb" \
	--side top --quality high --background transparent \
	-w 1200 -h 1800 -o "$IMG_DIR/board-top.png"

echo "== Hub Board render (isometric 3D hero) =="
run_kicad_cli pcb render "$HUB_DIR/SunSproutHub.kicad_pcb" \
	--side top --quality high --floor --background opaque --rotate "-30,0,30" \
	-w 1600 -h 1200 -o "$IMG_DIR/board-isometric.png"

echo "== Hub Board render (bottom) =="
run_kicad_cli pcb render "$HUB_DIR/SunSproutHub.kicad_pcb" \
	--side bottom --quality high --background transparent \
	-w 1200 -h 1800 -o "$IMG_DIR/board-bottom.png"

echo "== Hub Schematic PDF (all sheets) =="
run_kicad_cli sch export pdf "$HUB_DIR/SunSproutHub.kicad_sch" \
	-o "$STATIC_DIR/SunSproutHub-schematic.pdf"

echo "== Hub PCB STEP model =="
run_kicad_cli pcb export step "$HUB_DIR/SunSproutHub.kicad_pcb" \
	--subst-models -f -o "$STATIC_DIR/SunSproutHub.step"

echo "== Hub Pinout diagram draft (top silkscreen + edge cuts, board-only crop) =="
run_kicad_cli pcb export svg "$HUB_DIR/SunSproutHub.kicad_pcb" \
	--layers "F.Silkscreen,Edge.Cuts" --mode-single --page-size-mode 2 --fit-page-to-board \
	--exclude-drawing-sheet \
	-o "$IMG_DIR/pinout-top-draft.svg"

echo "== Hub Graphical Pinout diagram (SVG with color-coded callouts) =="
docker run --rm -v "$REPO_ROOT:/work" -w /work "$IMAGE" \
	python3 tools/pinout/generate_hub_pinout.py \
		--board-image "$IMG_DIR/board-top.png" \
		--output "$IMG_DIR/pinout-top.svg" \
		--css "tools/pinout/styles.css"

echo "== Hub Interactive HTML BOM =="
# xvfb-run manages a background Xvfb process via shell job control (backgrounds it, then
# `wait`s) - that breaks if xvfb-run itself is the container's PID 1, which is what happens if
# it's docker's direct argv command. Routing it through `sh -c` gives it a real parent shell
# instead, which is what it needs.
# generate_interactive_bom resolves --dest-dir relative to the BOARD FILE, not the working
# directory, so a repo-relative path here lands under hardware/hub/. Pass the absolute
# container path instead.
docker run --rm -v "$REPO_ROOT:/work" -w /work -e STATIC_DIR="/work/$STATIC_DIR" -e HUB_DIR="$HUB_DIR" "$IMAGE" \
	sh -c 'xvfb-run -a -s "-screen 0 1024x768x24" generate_interactive_bom --no-browser --dest-dir "$STATIC_DIR/ibom" --name-format "index" "$HUB_DIR/SunSproutHub.kicad_pcb"'

echo "== Satellite Board render (top - orthographic for pinout & docs) =="
run_kicad_cli pcb render "$SAT_DIR/SunSproutSatellite.kicad_pcb" \
	--side top --quality high --background transparent \
	-w 1200 -h 1800 -o "$IMG_DIR/satellite-board-top.png"

echo "== Satellite Board render (isometric 3D hero) =="
run_kicad_cli pcb render "$SAT_DIR/SunSproutSatellite.kicad_pcb" \
	--side top --quality high --floor --background opaque --rotate "-30,0,30" \
	-w 1600 -h 1200 -o "$IMG_DIR/satellite-board-isometric.png"

echo "== Satellite Board render (bottom) =="
run_kicad_cli pcb render "$SAT_DIR/SunSproutSatellite.kicad_pcb" \
	--side bottom --quality high --background transparent \
	-w 1200 -h 1800 -o "$IMG_DIR/satellite-board-bottom.png"

echo "== Satellite Schematic PDF =="
run_kicad_cli sch export pdf "$SAT_DIR/SunSproutSatellite.kicad_sch" \
	-o "$STATIC_DIR/SunSproutSatellite-schematic.pdf"

echo "== Satellite PCB STEP model =="
run_kicad_cli pcb export step "$SAT_DIR/SunSproutSatellite.kicad_pcb" \
	--subst-models -f -o "$STATIC_DIR/SunSproutSatellite.step"

echo "== Satellite Pinout diagram draft =="
run_kicad_cli pcb export svg "$SAT_DIR/SunSproutSatellite.kicad_pcb" \
	--layers "F.Silkscreen,Edge.Cuts" --mode-single --page-size-mode 2 --fit-page-to-board \
	--exclude-drawing-sheet \
	-o "$IMG_DIR/satellite-pinout-top-draft.svg"

echo "== Satellite Graphical Pinout & Jumper diagrams (Top & Bottom SVGs) =="
docker run --rm -v "$REPO_ROOT:/work" -w /work "$IMAGE" \
	python3 tools/pinout/generate_satellite_pinout.py \
		--top-image "$IMG_DIR/satellite-board-top.png" \
		--bottom-image "$IMG_DIR/satellite-board-bottom.png" \
		--top-output "$IMG_DIR/satellite-pinout-top.svg" \
		--bottom-output "$IMG_DIR/satellite-pinout-bottom.svg" \
		--css "tools/pinout/styles.css"

echo "== Satellite Interactive HTML BOM =="
docker run --rm -v "$REPO_ROOT:/work" -w /work -e STATIC_DIR="/work/$STATIC_DIR" -e SAT_DIR="$SAT_DIR" "$IMAGE" \
	sh -c 'xvfb-run -a -s "-screen 0 1024x768x24" generate_interactive_bom --no-browser --dest-dir "$STATIC_DIR/ibom-satellite" --name-format "index" "$SAT_DIR/SunSproutSatellite.kicad_pcb"'

echo "Done. Outputs under $STATIC_DIR/ and $IMG_DIR/."
