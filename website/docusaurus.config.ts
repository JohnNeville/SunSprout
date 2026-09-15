import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'SunSprout',
  tagline: 'USB-C, solar, and battery power management for ESP32-C5 projects',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Repo: https://github.com/JohnNeville/SunSprout (currently private, so
  // Pages can't actually serve from it yet on a Free personal plan).
  // GitHub Pages project sites are served from a subpath, so baseUrl must match the
  // repo name. Asset references use useBaseUrl()/relative paths so they survive it.
  url: 'https://johnneville.github.io',
  baseUrl: '/SunSprout/',

  // GitHub pages deployment config.
  organizationName: 'JohnNeville',
  projectName: 'SunSprout',

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: 'docs',
          // TODO: point this at the real repo once it exists, or remove to drop "edit this page" links.
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/board-top.png',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'SunSprout',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'hardwareSidebar',
          position: 'left',
          label: 'Docs',
        },
        // TODO: add a GitHub navbar link once this project has a public repo.
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {label: 'Overview', to: '/docs/overview'},
            {label: 'Pins & Signals', to: '/docs/pinout'},
            {label: 'Connectors', to: '/docs/connectors'},
          ],
        },
        {
          title: 'More',
          items: [
            {label: 'Design Files', to: '/docs/design-files'},
            {label: 'Attribution', to: '/docs/attribution'},
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} John Neville. Licensed under CERN-OHL-S v2.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
