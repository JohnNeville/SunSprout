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
    title: 'Three power sources, one battery',
    description: (
      <>
        Runs from USB-C (5 V), a DC or solar panel input (3.6 V to 24 V), or a
        single lithium cell (Li-ion, LiPo or LiFePO4). The board picks the source and
        charges the battery automatically; both inputs can be connected at once.
      </>
    ),
  },
  {
    title: 'Solar panel tracking',
    description: (
      <>
        Every couple of minutes the charger measures the panel's open-circuit
        voltage and sets its minimum input voltage to a fraction of it, so a
        weak panel in poor light is not dragged down.
      </>
    ),
  },
  {
    title: 'Two separate I2C buses',
    description: (
      <>
        An always-on bus for the charger and fuel gauge, and a switchable sensor
        bus. The sensor bus feeds a STEMMA QT port and two RJ45 (8P8C) jacks that
        carry I2C over an Ethernet cable to remote sensors.
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
