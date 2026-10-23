# Website

This website is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

## Installation

```bash
npm install
```

**Note**: feel free to use the package manager of your choice.

## Local Development

```bash
npm run start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
npm run build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

Using SSH:

```bash
USE_SSH=true npm run deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> npm run deploy
```

If you are using GitHub Pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.

## Status data

The [Testing status](docs/testing-status.md), [Firmware status](docs/firmware-status.md) and
[Satellite testing status](docs/satellite-testing-status.md) pages are rendered from JSON, not written by hand.
All three files live in [one Gist](https://gist.github.com/JohnNeville/31635451e342c20357f21a530f6bacda) and the pages fetch them in the
browser, so editing a file there updates its page without a commit or release. GitHub caches the raw file for
about five minutes.

| Page | File in the Gist | Override at build time |
|---|---|---|
| Testing status | `testing-status.json` | `TESTING_STATUS_URL` |
| Firmware status | `firmware-status.json` | `FIRMWARE_STATUS_URL` |
| Satellite testing status | `satellite-testing-status.json` | `SATELLITE_TESTING_STATUS_URL` |

There is no copy bundled with the site. If the fetch fails, or the file is not in the expected format, the page
shows an error that names the URL instead of showing out-of-date data.

Each item has a `feature`, a `status` and optional `notes`. The `status` values are `tested`, `fixed_in_design`,
`issue` and `untested`, except on the firmware page, which uses `tested`, `issue` and `untested`. Wrap part names in
backticks to show them as code. Update the top-level `updated` date when you change anything.
