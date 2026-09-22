# Extends the official KiCad CI image (ghcr.io/kicad/kicad) with everything kicad-cli needs
# to fully render/export this project's design (real 3D component bodies, not just board
# outline + copper), plus InteractiveHtmlBom for generating an interactive pinout/BOM viewer.
#
# Two library layers, both required for full 3D fidelity:
#
# 1. kicad-packages3D - KiCad's official 3D model library (standard resistors, capacitors,
#    connectors, etc.), git-cloned directly from KiCad's own GitLab, pinned to the same 10.0.0
#    tag as the base image. Public, no auth needed. Several GB - expect a slow first build;
#    Docker caches the layer after that.
#
# 2. batterypowerboard-kicad-libraries - this project's own private repo of vendor-specific
#    footprint/symbol/3D-model files (Snapeda, EasyEDA, etc.) that carry redistribution
#    restrictions, kept private for that reason. Covers the parts kicad-packages3D doesn't:
#    the MCU module, both 8P8C jacks, the USB-C receptacle, and a handful of ICs. Cloning it
#    needs a GitHub token with read access, passed in as a build secret (never baked into an
#    image layer) - see tools/generate-docs-assets.sh, which supplies it from `gh auth token`.
#    Build without this secret still works; that layer's RUN step is skipped and those specific
#    parts just render bodyless, same as before this repo existed.

FROM ghcr.io/kicad/kicad:10.0.0

USER root

RUN git clone --depth 1 --branch 10.0.0 \
      https://gitlab.com/kicad/libraries/kicad-packages3D.git /usr/share/kicad/3dmodels \
    && rm -rf /usr/share/kicad/3dmodels/.git

# KiCad has renamed this env var across major versions; footprints placed under older KiCad
# releases can still reference the older names, so point all of them at the same directory.
ENV KICAD10_3DMODEL_DIR=/usr/share/kicad/3dmodels
ENV KICAD9_3DMODEL_DIR=/usr/share/kicad/3dmodels
ENV KICAD6_3DMODEL_DIR=/usr/share/kicad/3dmodels

RUN --mount=type=secret,id=github_token \
    if [ -s /run/secrets/github_token ]; then \
      git clone --depth 1 \
        "https://oauth2:$(cat /run/secrets/github_token)@github.com/JohnNeville/batterypowerboard-kicad-libraries.git" \
        /opt/kicad-3rd-party \
      && rm -rf /opt/kicad-3rd-party/.git; \
    else \
      echo "No github_token secret supplied - skipping batterypowerboard-kicad-libraries (Snapeda/EasyEDA parts will render bodyless)"; \
      mkdir -p /opt/kicad-3rd-party; \
    fi

ENV KICAD_3RD_PARTY=/opt/kicad-3rd-party

# ESP32-C5-WROOM-1U 3D model: public (CC BY-SA 4.0, same license already covering the vendored
# symbol/footprint under libraries/vendor/espressif-kicad-libraries/ - see NOTICE.md), it just
# wasn't part of what got vendored locally, only the 2D symbol/footprint were. The footprint's
# embedded 3D-model reference expects KICAD9_3RD_PARTY laid out the way KiCad's Plugin & Content
# Manager would on a real install (a "com_github_<owner>_<repo>" subfolder per installed addon) -
# NOT the same thing as KICAD_3RD_PARTY above, which is this project's own manually-managed
# personal-library convention. Sparse-clones just this one file rather than the full (much
# larger) upstream 3dmodels tree, which has a same-sized STEP file for every other WROOM variant.
RUN mkdir -p /opt/kicad-pcm/3dmodels/com_github_espressif_kicad-libraries \
    && git clone --filter=blob:none --no-checkout --depth 1 \
         https://github.com/espressif/kicad-libraries.git /tmp/espressif-kicad-libraries \
    && cd /tmp/espressif-kicad-libraries \
    && git sparse-checkout set --no-cone 3dmodels/espressif.3dshapes/esp32-c5-wroom-1u.step \
    && git checkout main \
    && mv 3dmodels/espressif.3dshapes /opt/kicad-pcm/3dmodels/com_github_espressif_kicad-libraries/ \
    && rm -rf /tmp/espressif-kicad-libraries

ENV KICAD9_3RD_PARTY=/opt/kicad-pcm
ENV KICAD8_3RD_PARTY=/opt/kicad-pcm
ENV KICAD7_3RD_PARTY=/opt/kicad-pcm

# CDFER/JLCPCB-Kicad-Library 3D models: public, covers the small JLCPCB-basic passive
# footprints (0402/0805 caps etc.) used throughout this board. Same com_github_<owner>_<repo>
# PCM layout and sparse-checkout approach as the Espressif clone above - only the 3dmodels/
# folder is needed, not the repo's own footprints/symbols (this project has its own).
RUN mkdir -p /opt/kicad-pcm/3dmodels/com_github_CDFER_JLCPCB-Kicad-Library \
    && git clone --filter=blob:none --no-checkout --depth 1 \
         https://github.com/CDFER/JLCPCB-Kicad-Library.git /tmp/jlcpcb-kicad-library \
    && cd /tmp/jlcpcb-kicad-library \
    && git sparse-checkout set --no-cone 3dmodels/JLCPCB.3dshapes \
    && git checkout main \
    && mv 3dmodels/JLCPCB.3dshapes /opt/kicad-pcm/3dmodels/com_github_CDFER_JLCPCB-Kicad-Library/ \
    && rm -rf /tmp/jlcpcb-kicad-library

# InteractiveHtmlBom & pinout: interactive hoverable pinout/BOM viewer and graphical pinout
# diagram generation, run headlessly via CLI (see tools/generate-docs-assets.sh). python3-pip
# isn't in the base image.
# xvfb is needed because KiCad's pcbnew Python bindings initialize wxWidgets even for
# non-GUI use, which fails outright without a display to attach to - generate_interactive_bom
# must be run under `xvfb-run`, a bare --no-browser flag isn't enough.
RUN apt-get update -qq \
    && apt-get install -y -qq --no-install-recommends python3-pip xvfb \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --break-system-packages InteractiveHtmlBom pinout pillow

USER kicad
