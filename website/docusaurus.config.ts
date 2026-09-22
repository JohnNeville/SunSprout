import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

// Served from root on Cloudflare Pages (https://sunsprout.pages.dev), with env fallback.
const baseUrl = process.env.BASE_URL || '/';
const url = process.env.URL || 'https://sunsprout.pages.dev';

const config: Config = {
  title: 'SunSprout',
  tagline: 'USB-C, solar, and battery power management for ESP32-C5 projects',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  url,
  baseUrl,

  // The .ico carries 16/32/48/64 raster sizes for broad compatibility; the SVG is
  // offered alongside it so browsers that support it render the mark crisply at any
  // size instead of upscaling a 64px bitmap.
  headTags: [
    {
      tagName: 'link',
      attributes: {rel: 'icon', type: 'image/svg+xml', href: `${baseUrl}img/favicon.svg`},
    },
  ],

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
      // srcDark swaps in a light-ink copy: the navy mark is near-invisible on the dark
      // navbar, and Docusaurus renders the logo as an <img>, so it can't inherit colour.
      logo: {
        alt: 'SunSprout logo: a potted seedling on a solar panel',
        src: 'img/logo_color.svg',
        srcDark: 'img/logo_lines_dark.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'hardwareSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          href: 'https://github.com/JohnNeville/SunSprout',
          label: 'GitHub',
          position: 'right',
        },
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
            {
              label: 'GitHub',
              href: 'https://github.com/JohnNeville/SunSprout',
            },
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
