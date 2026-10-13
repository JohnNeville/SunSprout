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

## Testing status data

The [Testing status](docs/testing-status.md) page is rendered from JSON, not written by hand.

- **Live data:** the page fetches
  [this Gist](https://gist.github.com/JohnNeville/31635451e342c20357f21a530f6bacda) in the
  browser. Edit `testing-status.json` there to update the page without a commit or release.
  GitHub caches the raw file for about five minutes.
- **Fallback:** `src/data/testing-status.json` is bundled with the site and shown if the fetch
  fails. Copy the Gist's contents into it now and then so the two don't drift too far apart.
- **Override:** set `TESTING_STATUS_URL` at build time to point the page at a different file.

Each item has a `feature`, a `status` (`tested`, `fixed_in_design`, `issue` or `untested`) and
optional `notes`. Wrap part names in backticks to show them as code. Update the top-level
`updated` date when you change anything.
