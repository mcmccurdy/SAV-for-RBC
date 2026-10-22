"""Final form of the generated LaTeX tables"""
import re


def _group(t, k):
    """the argument of a macro starting at t[k]: a braced group, a control sequence or one character"""
    while t[k] in ' \t\n':
        k += 1
    if t[k] == '{':
        d = 0
        for m in range(k, len(t)):
            d += (t[m] == '{') - (t[m] == '}')
            if d == 0:
                return t[k:m + 1], m + 1
    if t[k] == '\\':
        m = k + 1
        if t[m].isalpha():
            while m < len(t) and t[m].isalpha():
                m += 1
        else:
            m += 1
        return '{' + t[k:m] + '}', m
    return '{' + t[k] + '}', k + 1


def braced_fracs(t):
    out, k = [], 0
    for m in re.finditer(r'\\[dt]?frac(?![a-zA-Z])', t):
        if m.start() < k:
            continue
        a, p = _group(t, m.end())
        b, p = _group(t, p)
        out += [t[k:m.start()], m.group(0) + a + b]
        k = p
    return ''.join(out) + t[k:]


def caption_below(t):
    i = t.find('\\caption{')
    if i < 0:
        return t
    _, j = _group(t, i + len('\\caption'))
    cap = t[i:j]
    lab = re.search(r'\\label\{[^}]*\}', t[j:j + 200])
    rest = t[:i] + t[j:]
    if lab:
        rest = rest.replace(lab.group(0), '', 1)
        cap += '\n' + lab.group(0)
    rest = re.sub(r'\n(?:[ \t]*\n)+', '\n', rest)
    e = rest.rfind('\\end{table}')
    return rest[:e].rstrip('\n') + '\n' + cap + '\n' + rest[e:]


def finalize(t):
    return caption_below(braced_fracs(t))
