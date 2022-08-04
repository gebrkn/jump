import sys
import os
import re
import io

import livereload
import mistune

DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(DIR + '/..'))

import jump

NL = '\n'


class ReadmeEngine(jump.Engine):
    def mbox_eval(self, text):
        text = trim(dedent(text))
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            exec(text)
        except:
            print('ERROR IN', text, NL)
            raise

        res = sys.stdout.getvalue()
        sys.stdout = old_stdout

        return (
                self.head('example:') +
                self.code(text, 'python') +
                self.head('output:') +
                self.code(trim(res))
        )

    def mbox_example(self, text):
        text = trim(dedent(text))
        parts = [x.strip() for x in text.split('ARGS =')]
        tpl = parts.pop(0)
        args = parts.pop(0) if parts else None

        try:
            res = jump.render(tpl, eval(args) if args else None)
        except:
            print('ERROR IN', text, NL)
            raise

        out = self.head('example:') + self.code(tpl)
        if args:
            out += self.head('arguments:') + self.code(trim(args))
        out += self.head('output:') + self.code(trim(res))

        return out

    def mbox_xmp(self, text, lang=''):
        text = trim(dedent(text))
        return self.code(text, lang)

    def mbox_filter(self, text):
        flt, xmp = text.strip().split('==')
        try:
            res = jump.render(xmp.strip())
        except:
            print('ERROR IN', text, NL)
            raise

        flt = flt.strip()
        xmp = xmp.strip().replace('|', '\\|')
        res = res.strip().replace('|', '\\|')

        return f"`{flt}` | `{xmp}` | `{res}`"

    tok_marker = '__TOC__'

    def def_toc(self):
        return self.tok_marker

    def box_document(self, text):
        indent = '    '
        lines = []

        for ln in text.splitlines():
            m = re.match(r'^(#{2,4})( .+)', ln.strip())
            if m:
                d, t = m.groups()
                lines.append(
                    '%s * [%s](#%s)' % (
                        indent * (len(d) - 2),
                        t.strip(),
                        t.strip().lower().replace(' ', '-')
                    ))

        return text.replace(
            self.tok_marker,
            '## table of contents\n' + NL.join(lines))

    def head(self, s):
        return '#' * 6 + ' ' + s.strip() + NL

    def code(self, s, lang=''):
        q = '`' * 3
        return q + lang + NL + s + NL + q + NL


def lpr(s):
    for n, l in enumerate(s.split(NL), 1):
        print(f'{n:6d}:{l}')


def trim(text):
    lines = text.split(NL)
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return NL.join(lines)


def dedent(text):
    ind = 1e20
    lines = text.split(NL)
    for ln in lines:
        n = len(ln.lstrip())
        if n > 0:
            ind = min(ind, len(ln) - n)
    return NL.join(ln[ind:] for ln in lines)


def update():
    with open(DIR + '/README.jump.md') as fp:
        text = fp.read()

    # lpr(ReadmeEngine().translate(text))

    markdown = ReadmeEngine().render(text)

    with open(DIR + '/../README.md', 'w') as fp:
        fp.write(markdown)

    body = mistune.html(markdown)
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="github-markdown-light.css"/>
        </head>
        <body>
            <div style="max-width: 1280px; padding: 32px">
            <article class="markdown-body">
                {body}
            </article>
            </div>
        </body>
        </html>
    '''
    with open(DIR + '/index.html', 'wt') as fp:
        fp.write(html)


###

if __name__ == '__main__':
    update()

    try:
        port = int(sys.argv[1])
    except IndexError:
        port = None

    if port:
        server = livereload.Server()
        server.watch(DIR + '/*jump.md', update, delay=0)
        server.serve(root=DIR, port=port, live_css=False)
