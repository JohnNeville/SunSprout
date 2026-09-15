#!/usr/bin/env python3
"""Compare an ERC report against the accepted baseline.

kicad-cli does not apply the project's ERC exclusions: running `sch erc` with
--severity-exclusions returns the same violations as --severity-error, so excluding a
violation in the KiCad GUI has no effect on a headless run. This script provides the
equivalent for CI.

The baseline lists violations that have been reviewed and accepted, each with the reason.
CI fails only on violations that are not in the baseline, so a new problem breaks the build
while the known ones stay visible rather than hidden.

Violations are matched on (type, item uuid). Coordinates are deliberately ignored, so moving
a symbol on the sheet does not invalidate its baseline entry.
"""
import argparse
import json
import sys


def load_violations(path):
    with open(path, encoding='utf-8') as fh:
        report = json.load(fh)
    out = {}
    for sheet in report.get('sheets', []):
        for v in sheet.get('violations', []):
            item = (v.get('items') or [{}])[0]
            uuid = item.get('uuid', '')
            out[(v['type'], uuid)] = {
                'type': v['type'],
                'uuid': uuid,
                'sheet': sheet.get('path', ''),
                'description': item.get('description', v.get('description', '')),
                'severity': v.get('severity', ''),
            }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('report', help='ERC report JSON from kicad-cli sch erc --format json')
    ap.add_argument('baseline', help='accepted-violation baseline JSON')
    ap.add_argument('--write-baseline', action='store_true',
                    help='rewrite the baseline from this report instead of checking it')
    args = ap.parse_args()

    found = load_violations(args.report)

    if args.write_baseline:
        entries = [dict(v, reason='TODO: explain why this is accepted')
                   for v in found.values()]
        with open(args.baseline, 'w', encoding='utf-8') as fh:
            json.dump({'accepted': entries}, fh, indent=2)
            fh.write('\n')
        print(f'Wrote {len(entries)} entries to {args.baseline}. Fill in each reason.')
        return 0

    with open(args.baseline, encoding='utf-8') as fh:
        accepted = {(e['type'], e['uuid']): e for e in json.load(fh)['accepted']}

    new = [v for k, v in found.items() if k not in accepted]
    gone = [e for k, e in accepted.items() if k not in found]

    for e in gone:
        print(f"RESOLVED  {e['type']}: {e['description']}")
    if gone:
        print(f"\n{len(gone)} baseline entries no longer occur. Remove them from the baseline.\n")

    if new:
        print(f'NEW ERC VIOLATIONS ({len(new)}):\n')
        for v in new:
            print(f"  [{v['severity']}] {v['type']}")
            print(f"      {v['sheet']}  {v['description']}")
        print('\nFix these, or add them to the baseline with a reason if they are expected.')
        return 1

    print(f'ERC clean: {len(found)} violations, all in the accepted baseline.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
