#!/usr/bin/env python3
"""Compare an ERC report against the accepted baseline.

kicad-cli does not apply the project's ERC exclusions: running `sch erc` with
--severity-exclusions returns the same violations as --severity-error, so excluding a
violation in the KiCad GUI has no effect on a headless run. This script provides the
equivalent for CI.

The baseline lists violations that have been reviewed and accepted, each with the reason.
CI fails only on violations that are not in the baseline, so a new problem breaks the build
while the known ones stay visible rather than hidden.

Violations are matched on (rule type, symbol reference) -- deliberately NOT on the pin or its
uuid.

The reason: for a rule like power_pin_not_driven, ERC emits one violation per net and names an
arbitrary representative pin. U3's BAT, CE and REGIN pins all sit on VBAT, so an unrelated edit
elsewhere in the schematic flipped the reported pin from BAT to REGIN and the run failed against
a baseline that had recorded the uuid of the other pin. Same net, same root cause, no design
change. Coordinates are ignored for the same reason.

The tradeoff is real and worth stating: a genuinely different violation of the same rule on the
same symbol would be absorbed by an existing entry rather than flagged. That is acceptable here
because these entries are symbol-declaration artifacts and nets ERC cannot trace a driver
through -- one root cause per symbol. A new rule type, or the same rule on a different symbol,
still fails the build.
"""
import argparse
import json
import re
import sys


def symbol_ref(description):
    """Pull the reference designator out of 'Symbol U3 Pin 6 [REGIN, ...]'."""
    m = re.match(r'Symbol\s+(\S+)', description or '')
    return m.group(1) if m else (description or '')


def load_violations(path):
    with open(path, encoding='utf-8') as fh:
        report = json.load(fh)
    out = {}
    for sheet in report.get('sheets', []):
        for v in sheet.get('violations', []):
            item = (v.get('items') or [{}])[0]
            desc = item.get('description', v.get('description', ''))
            out[(v['type'], symbol_ref(desc))] = {
                'type': v['type'],
                'symbol': symbol_ref(desc),
                'sheet': sheet.get('path', ''),
                'description': desc,
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
        accepted = {(e['type'], e.get('symbol') or symbol_ref(e.get('description', ''))): e
                    for e in json.load(fh)['accepted']}

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
