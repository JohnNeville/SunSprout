import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Power management',
    description: (
      <>
        USB-C, DC/solar, and battery inputs, arbitrated and charged automatically,
        with true open-circuit-voltage MPPT on the solar input.
      </>
    ),
  },
  {
    title: 'Two independent I2C buses',
    description: (
      <>
        An always-on internal bus for the board's own power-management ICs, and a
        switched user bus with a differential buffer for remote sensors.
      </>
    ),
  },
  {
    title: 'Datasheet-driven design',
    description: (
      <>
        Every IC's required external components are drawn directly into the
        schematic and hand-routed — nothing is a black-box breakout module.
      </>
    ),
  },
];

function Feature({title, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
