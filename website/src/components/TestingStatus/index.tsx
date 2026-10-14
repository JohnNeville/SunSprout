import React, { useEffect, useState } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import bundled from '@site/src/data/testing-status.json';
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

export default function TestingStatus(): React.ReactElement {
  const { siteConfig } = useDocusaurusContext();
  const url = siteConfig.customFields?.testingStatusUrl as string | undefined;
  const [data, setData] = useState<TestingStatusData>(bundled as TestingStatusData);
  const [source, setSource] = useState<'bundled' | 'live'>('bundled');

  useEffect(() => {
    if (!url) return;
    let cancelled = false;
    fetch(url, { cache: 'no-store' })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((json) => {
        if (!cancelled && isValid(json)) {
          setData(json);
          setSource('live');
        }
      })
      .catch(() => {
        // Keep the copy bundled with the site.
      });
    return () => {
      cancelled = true;
    };
  }, [url]);

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
        {source === 'bundled' ? ' (copy bundled with the site)' : ''}.
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
