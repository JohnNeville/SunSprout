# Extends the official KiCad CI image (ghcr.io/kicad/kicad) with everything needed to run
# ERC/DRC validation and generate JLCPCB production files headlessly - i.e. everything this
# project's CI-style scripts need except the 3D-model layers.
#
# Deliberately leaner than tools/kicad-assets.Dockerfile: DRC/ERC and the Fabrication Toolkit
# plugin operate on 2D footprint/symbol geometry, which is embedded directly in
# .kicad_sch/.kicad_pcb at placement time - none of that depends on 3D STEP/WRL models
# resolving, so this image skips the multi-GB public kicad-packages3D clone entirely (see
# kicad-assets.Dockerfile's own header comment, which confirms the same thing).
#
# It still needs the one library layer that DOES affect ERC/DRC correctness: this project's own
# private vendor-library repo (batterypowerboard-kicad-libraries), which provides the
# Snapeda/EasyEDA footprint/symbol files that fp-lib-table/sym-lib-table reference via the
# KICAD_3RD_PARTY env var (J201/J202, J2/J3, D5's ESD array). Confirmed by directly running
# `kicad-cli sch erc` against this repo without that layer resolvable: 42 noise violations
# (footprint_link_issues/lib_symbol_issues) instead of the real baseline. Cloning it needs a
# GitHub token with read access, passed in as a build secret (never baked into an image layer) -
# see tools/run_kicad_validation.sh, which supplies it from
# `gh auth token`. Build without this secret still works; that layer's RUN step is skipped and
# ERC will show the library-link noise instead of the real 3-violation baseline.

FROM ghcr.io/kicad/kicad:10.0.0

USER root

RUN --mount=type=secret,id=github_token \
    if [ -s /run/secrets/github_token ]; then \
      git clone --depth 1 \
        "https://oauth2:$(cat /run/secrets/github_token)@github.com/JohnNeville/batterypowerboard-kicad-libraries.git" \
        /opt/kicad-3rd-party \
      && rm -rf /opt/kicad-3rd-party/.git; \
    else \
      echo "No github_token secret supplied - skipping batterypowerboard-kicad-libraries (ERC will show library-link noise for Snapeda/EasyEDA parts)"; \
      mkdir -p /opt/kicad-3rd-party; \
    fi

ENV KICAD_3RD_PARTY=/opt/kicad-3rd-party
ENV KICAD9_3RD_PARTY=/opt/kicad-3rd-party
ENV KICAD8_3RD_PARTY=/opt/kicad-3rd-party
ENV KICAD7_3RD_PARTY=/opt/kicad-3rd-party

# This project's fp-lib-table already points its Snapeda/EasyEDA footprint entries at
# ${KICAD_3RD_PARTY} (project-relative, works as-is once the layer above is cloned) - but
# sym-lib-table has no equivalent entries, project- or global-level, for those same two
# libraries. On a real workstation they come from the user's personal SnapEDA/EasyEDA KiCad
# plugin installs, which register themselves in that machine's *global* sym-lib-table - not
# something this repo can vendor since it's normally machine-specific. In this image
# KICAD_3RD_PARTY IS well-defined, so the same two .kicad_sym files the private repo already
# provides (Snapeda.kicad_sym, EasyEDA.kicad_sym) can be registered as global library-table
# entries here. Confirmed necessary by directly running `kicad-cli sch erc`: without this,
# ERC still reports 21 lib_symbol_issues warnings even with the private repo cloned.
RUN f=/home/kicad/.config/kicad/10.0/sym-lib-table \
    && sed -i '$d' "$f" \
    && printf '\t(lib (name "Snapeda") (type "KiCad") (uri "${KICAD_3RD_PARTY}/Snapeda.kicad_sym") (options "") (descr "Vendored personal SnapEDA plugin library, added for headless CI (see fp-lib-table for the footprint equivalent)"))\n' >> "$f" \
    && printf '\t(lib (name "EasyEDA") (type "KiCad") (uri "${KICAD_3RD_PARTY}/EasyEDA.kicad_sym") (options "") (descr "Vendored personal EasyEDA plugin library, added for headless CI"))\n' >> "$f" \
    && printf ')\n' >> "$f" \
    && chown kicad:kicad "$f"

# xvfb: the Fabrication Toolkit CLI (plugins/cli.py) still imports pcbnew + wx even in
# non-interactive mode (same reason tools/generate-docs-assets.sh needs it for
# generate_interactive_bom) - wxWidgets initializes on import and fails without a display to
# attach to. python3 itself is already present in the base image (pcbnew's own bindings need
# it) - no pip installs needed here; the JLCPCB pricing script (run separately, on the host,
# not in this container) is stdlib-only.
RUN apt-get update -qq \
    && apt-get install -y -qq --no-install-recommends xvfb \
    && rm -rf /var/lib/apt/lists/*

# Fabrication Toolkit (JLCPCB BOM/CPL/gerber generator): pinned to the same release version
# available via KiCad's own Plugin & Content Manager, cloned as a plain public repo (no auth
# needed - unlike the private vendor-library repo above). Its plugins/ package (with its own
# __init__.py) exposes a genuine headless CLI at plugins/cli.py, distinct from the wx GUI dialog
# used inside pcbnew - run as `python3 -m plugins.cli --path <board> ... --nonInteractive` from
# /opt/fabrication-toolkit. The release workflow installs the same pinned version the same
# way; this layer keeps it available for local runs against the same image.
RUN git clone --depth 1 --branch 5.3.1 \
      https://github.com/bennymeg/Fabrication-Toolkit.git /opt/fabrication-toolkit \
    && rm -rf /opt/fabrication-toolkit/.git

USER kicad
