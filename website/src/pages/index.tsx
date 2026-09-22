import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/overview">
            Hub Overview
          </Link>
          <Link
            className="button button--secondary button--lg"
            to="/docs/satellite-overview">
            Satellite Overview
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={siteConfig.title}
      description="Hardware documentation for SunSprout Hub and SunSprout Satellite: an ESP32-C5 power-management controller and remote differential sensor node.">
      <HomepageHeader />
      <main>
        <div className="container">
          <div className={styles.heroImageContainer}>
            <img
              src={useBaseUrl("/img/hub-and-satellite.png")}
              alt="SunSprout Hub and SunSprout Satellite"
              className={styles.heroImage}
            />
            <div className={styles.heroLabels}>
              <span className={styles.heroLabelHub}>SunSprout Hub (56 x 85 mm)</span>
              <span className={styles.heroLabelSat}>SunSprout Satellite (27 x 51 mm)</span>
            </div>
          </div>
        </div>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}

