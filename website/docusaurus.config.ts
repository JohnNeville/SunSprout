import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import fs from 'node:fs';
import path from 'node:path';
import sidebars from './sidebars';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

// Served from root on Cloudflare Pages (https://sunsprout.pages.dev), with env fallback.
const baseUrl = process.env.BASE_URL || '/';
const url = process.env.URL || 'https://sunsprout.pages.dev';

// Main menu: one dropdown per sidebar group (Hub, Satellite, Build your own) listing every page, so the navbar and the
// mobile menu show the same pages as the sidebar and the home page. Built from sidebars.ts; each label is the doc's
// sidebar_label or title, read from its front matter, with a leading "Satellite " dropped inside the Satellite menu.
type SidebarCategory = {type: 'category'; label: string; items: string[]};
function docLabel(id: string, dropPrefix?: string): string {
  const text = fs.readFileSync(path.join(__dirname, 'docs', `${id}.md`), 'utf8');
  const front = text.match(/^---\n([\s\S]*?)\n---/)?.[1] ?? '';
  const field = (name: string) => front.match(new RegExp(`^${name}:\\s*(.+)$`, 'm'))?.[1].trim().replace(/^['"]|['"]$/g, '');
  const label = field('sidebar_label') ?? field('title') ?? id;
  if (!dropPrefix || !label.startsWith(dropPrefix)) return label;
  const rest = label.slice(dropPrefix.length);
  return rest.charAt(0).toUpperCase() + rest.slice(1);
}
const menuLabels: Record<string, string> = {'SunSprout Hub': 'Hub', 'SunSprout Satellite': 'Satellite'};
// Same order as the home page buttons: Hub, Satellite, Build your own.
const menuOrder = ['SunSprout Hub', 'SunSprout Satellite', 'Build your own'];
const docMenus = [...(sidebars.hardwareSidebar as SidebarCategory[])]
  .sort((a, b) => menuOrder.indexOf(a.label) - menuOrder.indexOf(b.label))
  .map((category) => {
    const dropPrefix = category.label === 'SunSprout Satellite' ? 'Satellite ' : undefined;
    return {
      type: 'dropdown' as const,
      label: menuLabels[category.label] ?? category.label,
      position: 'left' as const,
      items: category.items.map((id) => ({type: 'doc' as const, docId: id, label: docLabel(id, dropPrefix)})),
    };
  });

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

  customFields: {
    // Live testing-status data, fetched in the browser so it can be updated without a
    // release. There is no bundled copy: the page shows an error if this is empty or the
    // fetch fails.
    testingStatusUrl:
      process.env.TESTING_STATUS_URL ||
      'https://gist.githubusercontent.com/JohnNeville/31635451e342c20357f21a530f6bacda/raw/testing-status.json',
    // The same for the firmware features page, from another file in the same Gist.
    firmwareStatusUrl:
      process.env.FIRMWARE_STATUS_URL ||
      'https://gist.githubusercontent.com/JohnNeville/31635451e342c20357f21a530f6bacda/raw/firmware-status.json',
    // The same for the satellite testing page, from another file in the same Gist.
    satelliteTestingStatusUrl:
      process.env.SATELLITE_TESTING_STATUS_URL ||
      'https://gist.githubusercontent.com/JohnNeville/31635451e342c20357f21a530f6bacda/raw/satellite-testing-status.json',
  },

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

  // Offline search index built at deploy time: no account or external service, and it works on
  // Cloudflare Pages. The docs are the site root's only content, so serve them from /docs.
  themes: [
    [
      '@easyops-cn/docusaurus-search-local',
      {
        hashed: true,
        indexBlog: false,
        docsRouteBasePath: '/docs',
        highlightSearchTermsOnTargetPage: true,
        explicitSearchResultPath: true,
      },
    ],
  ],

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
        ...docMenus,
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
