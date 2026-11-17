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

// Renders `code` spans and test-hardware references in the notes; everything else is plain text. A reference is written
// [^LFP] in the data and shown as a superscript link to the row with id "hw-lfp" in the page's Test hardware table.
export function hardwareId(ref: string): string {
  return `hw-${ref.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
}

function renderInline(text: string): React.ReactNode[] {
  return text.split(/(`[^`]+`|\[\^[^\]\s]+\])/g).map((part, i) => {
    if (part.startsWith('`') && part.endsWith('`')) return <code key={i}>{part.slice(1, -1)}</code>;
    const ref = part.match(/^\[\^([^\]\s]+)\]$/);
    if (ref) {
      const id = hardwareId(ref[1]);
      return (
        <sup key={i} className={styles.ref}>
          <a href={`#${id}`} aria-label={`Test hardware: ${ref[1]}`}>
            {ref[1]}
          </a>
        </sup>
      );
    }
    return part;
  });
}

function isValid(data: unknown): data is TestingStatusData {
  const d = data as TestingStatusData;
  return !!d && typeof d.updated === 'string' && Array.isArray(d.sections);
}

interface Props {
  /** Name of the `customFields` entry that holds the data URL. */
  urlField?: string;
}

type Load<T> =
  | { state: 'loading' }
  | { state: 'error'; message: string }
  | { state: 'ready'; data: T };

// Fetches a JSON file named by a `customFields` entry, in the browser, so the data can be updated without a release.
function useLiveJson<T>(urlField: string, valid: (data: unknown) => data is T): { url?: string; load: Load<T> } {
  const { siteConfig } = useDocusaurusContext();
  const url = siteConfig.customFields?.[urlField] as string | undefined;
  const [load, setLoad] = useState<Load<T>>({ state: 'loading' });

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
        if (valid(json)) {
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

  return { url, load };
}

function LoadError({ url, message }: { url?: string; message: string }): React.ReactElement {
  return (
    <div className="alert alert--danger" role="alert">
      <strong>The status data could not be loaded.</strong> {message} It is read from{' '}
      {url ? <a href={url}>{url}</a> : 'a URL that is not set'}.
    </div>
  );
}

export default function TestingStatus({ urlField = 'testingStatusUrl' }: Props): React.ReactElement {
  const { url, load } = useLiveJson(urlField, isValid);

  if (load.state === 'loading') {
    return <p className={styles.meta}>Loading the status data…</p>;
  }

  if (load.state === 'error') {
    return <LoadError url={url} message={load.message} />;
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

interface HardwareItem {
  ref: string;
  item: string;
  details: string;
}

interface TestHardwareData {
  items: HardwareItem[];
}

function isHardware(data: unknown): data is TestHardwareData {
  const d = data as TestHardwareData;
  return !!d && Array.isArray(d.items) && d.items.every((i) => typeof i?.ref === 'string');
}

// The Test hardware table that [^REF] references in the status notes link to. Each row gets the id hardwareId(ref).
export function TestHardware({ urlField = 'testHardwareUrl' }: Props): React.ReactElement {
  const { url, load } = useLiveJson(urlField, isHardware);

  // The rows only exist once the data has loaded, so a link that opens the page at #hw-... scrolls once they do.
  useEffect(() => {
    if (load.state !== 'ready' || !window.location.hash.startsWith('#hw-')) return;
    document.getElementById(decodeURIComponent(window.location.hash.slice(1)))?.scrollIntoView();
  }, [load.state]);

  if (load.state === 'loading') {
    return <p className={styles.meta}>Loading the test hardware…</p>;
  }
  if (load.state === 'error') {
    return <LoadError url={url} message={load.message} />;
  }
  return (
    <table>
      <thead>
        <tr>
          <th>Ref</th>
          <th>Item</th>
          <th>Details</th>
        </tr>
      </thead>
      <tbody>
        {load.data.items.map((h) => (
          <tr key={h.ref} id={hardwareId(h.ref)} className={styles.hardwareRow}>
            <td>
              <strong>{h.ref}</strong>
            </td>
            <td>{renderInline(h.item)}</td>
            <td>{renderInline(h.details)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
