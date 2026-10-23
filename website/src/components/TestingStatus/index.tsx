import React, { useEffect, useState } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './styles.module.css';

type Status = 'tested' | 'fixed_in_design' | 'issue' | 'untested';

interface Item {
  feature: string;
  status: Status;
  notes?: string;
}

interface Section {
  title: string;
  items: Item[];
}

interface TestingStatusData {
  updated: string;
  prototype_commit?: string;
  sections: Section[];
}

const LABELS: Record<Status, string> = {
  tested: 'Tested',
  fixed_in_design: 'Issue, fixed in design',
  issue: 'Issue',
  untested: 'Not yet tested',
};

// Renders `code` spans in the notes; everything else is plain text.
function renderInline(text: string): React.ReactNode[] {
  return text.split(/(`[^`]+`)/g).map((part, i) =>
    part.startsWith('`') && part.endsWith('`') ? <code key={i}>{part.slice(1, -1)}</code> : part,
  );
}

function isValid(data: unknown): data is TestingStatusData {
  const d = data as TestingStatusData;
  return !!d && typeof d.updated === 'string' && Array.isArray(d.sections);
}

interface Props {
  /** Name of the `customFields` entry that holds the data URL. */
  urlField?: string;
}

type Load =
  | { state: 'loading' }
  | { state: 'error'; message: string }
  | { state: 'ready'; data: TestingStatusData };

export default function TestingStatus({ urlField = 'testingStatusUrl' }: Props): React.ReactElement {
  const { siteConfig } = useDocusaurusContext();
  const url = siteConfig.customFields?.[urlField] as string | undefined;
  const [load, setLoad] = useState<Load>({ state: 'loading' });

  useEffect(() => {
    if (!url) {
      setLoad({ state: 'error', message: 'No data URL is configured for this page.' });
      return;
    }
    let cancelled = false;
    setLoad({ state: 'loading' });
    fetch(url, { cache: 'no-store' })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`The server answered ${r.status}.`))))
      .then((json) => {
        if (cancelled) return;
        if (isValid(json)) {
          setLoad({ state: 'ready', data: json });
        } else {
          setLoad({ state: 'error', message: 'The file is not in the expected format.' });
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setLoad({ state: 'error', message: err instanceof Error ? err.message : String(err) });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [url]);

  if (load.state === 'loading') {
    return <p className={styles.meta}>Loading the status data…</p>;
  }

  if (load.state === 'error') {
    return (
      <div className="alert alert--danger" role="alert">
        <strong>The status data could not be loaded.</strong> {load.message} It is read from{' '}
        {url ? <a href={url}>{url}</a> : 'a URL that is not set'}.
      </div>
    );
  }

  const { data } = load;
  return (
    <div>
      <p className={styles.meta}>
        {data.prototype_commit && /^[0-9a-f]{7,40}$/i.test(data.prototype_commit) && (
          <>
            Prototype tested:{' '}
            <a href={`https://github.com/JohnNeville/SunSprout/commit/${data.prototype_commit}`}>
              <code>{data.prototype_commit}</code>
            </a>
            .{' '}
          </>
        )}
        Last updated {data.updated}
        .
      </p>
      {data.sections.map((section) => (
        <section key={section.title}>
          <h2>{section.title}</h2>
          <table>
            <thead>
              <tr>
                <th>Feature</th>
                <th>Status</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {section.items.map((item) => (
                <tr key={item.feature}>
                  <td>{renderInline(item.feature)}</td>
                  <td>
                    <span className={`${styles.badge} ${styles[item.status] ?? ''}`}>
                      {LABELS[item.status] ?? item.status}
                    </span>
                  </td>
                  <td>{item.notes ? renderInline(item.notes) : null}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ))}
    </div>
  );
}
