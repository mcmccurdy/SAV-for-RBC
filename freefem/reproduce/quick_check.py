"""quick_check.py WORK REFDIR: compare the logs of the quick runs with the logs behind the paper.
Data rows are compared on the columns both logs have (older logs lack a few later-added columns); tagged lines
(# MMS, # MMS2, # REF, RAC, EIG) are compared number by number. Relative tolerance 1e-6."""
import os, re, sys

TOL = 1e-6


def numbers(s):
    out = []
    for x in re.split(r'[\s,]+', s):
        try:
            out.append(float(x))
        except ValueError:
            pass
    return out


def parse(path):
    rows, tags = [], {}
    for l in open(path):
        if l[:1].isdigit():
            rows.append(numbers(l))
        else:
            m = re.match(r'(# MMS2|# MMS|# REF|RAC|EIG)\b(.*)', l)
            if m:
                key = m.group(1) + (' ' + ' '.join(l.split()[1:5]) if m.group(1) in ('RAC', 'EIG') else '')
                tags[key] = numbers(m.group(2).split(':', 1)[-1] if ':' in m.group(2) else m.group(2))
    return rows, tags


def rel(a, b):
    return abs(a - b) / max(abs(b), 1e-12)


def main(work, ref):
    ok = True
    for root, _, files in os.walk(ref):
        for f in sorted(files):
            r = os.path.join(root, f); name = os.path.relpath(r, ref); w = os.path.join(work, name)
            if not os.path.exists(w):
                print(f'FAIL  {name}: not produced'); ok = False; continue
            rr, rt = parse(r); wr, wt = parse(w)
            worst, n = 0.0, 0
            if len(rr) != len(wr):
                print(f'FAIL  {name}: {len(wr)} data rows, expected {len(rr)}'); ok = False; continue
            for a, b in zip(wr, rr):
                for x, y in zip(a, b):
                    worst = max(worst, rel(x, y)); n += 1
            for k, v in rt.items():
                if k not in wt:
                    print(f'FAIL  {name}: line "{k}" missing'); ok = False; continue
                for x, y in zip(wt[k], v):
                    worst = max(worst, rel(x, y)); n += 1
            good = worst <= TOL
            ok &= good
            print(f'{"ok  " if good else "FAIL"}  {name}: {n} numbers, largest relative difference {worst:.1e}')
    print('\nQUICK CHECK PASSED: this installation reproduces the paper\'s runs.' if ok else
          '\nQUICK CHECK FAILED: see the lines above.')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
