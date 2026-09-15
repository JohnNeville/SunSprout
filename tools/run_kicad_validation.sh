#!/usr/bin/env sh
# Runs this project's KiCad validation suite: ERC (electrical rules + schematic library
# resolution), DRC (design rules + PCB/schematic netlist parity), against
# hardware/hub/SunSproutHub.kicad_sch / .kicad_pcb. Fails (nonzero exit) on any violation that isn't
# a pre-approved known-benign entry in tools/validation/known_exceptions.json - see that file
# for what's currently allowlisted and why. Run from the repo root:
#
#     tools/run_kicad_validation.sh
#
# Only prerequisite is Docker - no local KiCad install needed. Builds a local image
# (tools/kicad-ci.Dockerfile) on top of the official KiCad CI image, layered with this
# project's private vendor-library repo so ERC/DRC's library-resolution checks are accurate
# (see that Dockerfile's header comment). The private-repo clone needs a GitHub token with read
# access, supplied below via `gh auth token` as a Docker build secret. If `gh` isn't
# installed/authenticated, the build still succeeds, but ERC/DRC will additionally report
# Snapeda/EasyEDA library-link noise on top of the known exceptions.
#
# JSON reports are written to tools/validation/erc-report.json and drc-report.json (gitignored
# build artifacts - regenerate, don't hand-edit).

set -eu

IMAGE="sunsprout-kicad-ci:10.0.0"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VALIDATION_DIR="tools/validation"

# On Windows git-bash (MSYS), bash rewrites args that look like absolute Unix paths (e.g. the
# container's /work below) into Windows paths before docker.exe ever sees them - this disables
# that for the `docker run`/`docker build` calls, which need /work and the build context to stay
# literal. No-op on real Linux/Mac/WSL.
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

echo "== Building KiCad CI image (cached after first run) =="
if [ -n "$GITHUB_TOKEN" ]; then
	docker build --secret id=github_token,env=GITHUB_TOKEN \
		-f "$BUILD_CONTEXT/kicad-ci.Dockerfile" -t "$IMAGE" "$BUILD_CONTEXT"
else
	echo "No 'gh auth token' available - building without the private vendor-library repo"
	docker build -f "$BUILD_CONTEXT/kicad-ci.Dockerfile" -t "$IMAGE" "$BUILD_CONTEXT"
fi

mkdir -p "$REPO_ROOT/$VALIDATION_DIR"

run_kicad_cli() {
	docker run --rm -v "$REPO_ROOT:/work" -w /work "$IMAGE" kicad-cli "$@"
}

echo "== ERC (electrical rules + schematic library resolution) =="
run_kicad_cli sch erc --format json --severity-error --severity-warning \
	-o "$VALIDATION_DIR/erc-report.json" hardware/hub/SunSproutHub.kicad_sch

echo "== DRC (design rules + PCB/schematic netlist parity) =="
run_kicad_cli pcb drc --format json --severity-error --severity-warning --schematic-parity \
	-o "$VALIDATION_DIR/drc-report.json" hardware/hub/SunSproutHub.kicad_pcb

run_python() {
	docker run --rm -v "$REPO_ROOT:/work" -w /work "$IMAGE" python3 "$@"
}

echo "== Checking results against tools/validation/known_exceptions.json =="
erc_status=0
drc_status=0
run_python "$VALIDATION_DIR/check_violations.py" erc "$VALIDATION_DIR/erc-report.json" \
	"$VALIDATION_DIR/known_exceptions.json" || erc_status=$?
echo
run_python "$VALIDATION_DIR/check_violations.py" drc "$VALIDATION_DIR/drc-report.json" \
	"$VALIDATION_DIR/known_exceptions.json" || drc_status=$?

echo
if [ "$erc_status" -eq 0 ] && [ "$drc_status" -eq 0 ]; then
	echo "== VALIDATION PASSED =="
	exit 0
else
	echo "== VALIDATION FAILED (erc exit=$erc_status, drc exit=$drc_status) =="
	exit 1
fi
