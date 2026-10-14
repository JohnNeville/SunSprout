import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';
import Admonition from '@theme/Admonition';

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
          <Link
            className="button button--secondary button--lg"
            to="/docs/fabrication/ordering-jlcpcb">
            Build your own
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
        <div className="container margin-top--lg">
          <Admonition type="warning" title="Prototype hardware: charging works, validation incomplete">
            <p>
              A first hub was built and tested: charging and running from the battery
              worked, and testing found issues. The current design fixes them but has not
              been built yet, and not every feature has been bench-tested. Check{' '}
              <Link to="/docs/testing-status">what has been tested</Link>, set the cell
              chemistry before attaching a battery, and bring up one board before ordering
              a batch.
            </p>
          </Admonition>
          <div className={styles.heroShowcase}>
            <Link
              to="/docs/overview"
              className={styles.boardCard}
              aria-label="SunSprout Hub Documentation">
              <img
                src={useBaseUrl("/img/board-top.png")}
                alt="SunSprout Hub"
                className={styles.boardImageHub}
              />
              <div className={styles.boardCaption}>
                <span className={styles.boardName}>SunSprout Hub</span>
                <span className={styles.boardSpecs}>
                  ESP32-C5 Power Management Controller &bull; 56 &times; 85 mm
                </span>
              </div>
            </Link>

            <Link
              to="/docs/satellite-overview"
              className={styles.boardCard}
              aria-label="SunSprout Satellite Documentation">
              <img
                src={useBaseUrl("/img/satellite-board-top.png")}
                alt="SunSprout Satellite"
                className={styles.boardImageSatellite}
              />
              <div className={styles.boardCaption}>
                <span className={styles.boardName}>SunSprout Satellite</span>
                <span className={styles.boardSpecs}>
                  Differential I2C Sensor Leaf Node &bull; 27 &times; 51 mm
                </span>
              </div>
            </Link>
          </div>
        </div>

        <HomepageFeatures />
      </main>
    </Layout>
  );
}

