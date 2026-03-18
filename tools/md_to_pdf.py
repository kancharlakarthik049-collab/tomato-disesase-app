from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import textwrap
import os

INPUT = 'project_work_summary.md'
OUTPUT = 'project_work_summary.pdf'

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 50
TOP_MARGIN = 50
RIGHT_MARGIN = 50
LINE_HEIGHT = 12
FONT_NAME = 'Helvetica'
FONT_SIZE = 10

wrap_width = 90

def md_to_text(md):
    # Very small preprocessing: strip triple-backtick blocks markers
    out_lines = []
    in_code = False
    for line in md.splitlines():
        if line.strip().startswith('```'):
            in_code = not in_code
            continue
        out_lines.append(line.rstrip())
    return '\n'.join(out_lines)


def main():
    if not os.path.exists(INPUT):
        print(f'Missing input file: {INPUT}')
        return

    with open(INPUT, 'r', encoding='utf-8') as f:
        md = f.read()

    text = md_to_text(md)

    c = canvas.Canvas(OUTPUT, pagesize=A4)
    c.setFont(FONT_NAME, FONT_SIZE)

    x = LEFT_MARGIN
    y = PAGE_HEIGHT - TOP_MARGIN

    for paragraph in text.split('\n\n'):
        lines = []
        for raw_line in paragraph.split('\n'):
            if raw_line.strip() == '':
                lines.append('')
                continue
            wrapped = textwrap.wrap(raw_line, width=wrap_width)
            if not wrapped:
                lines.append('')
            else:
                lines.extend(wrapped)

        for ln in lines:
            if y < 60:
                c.showPage()
                c.setFont(FONT_NAME, FONT_SIZE)
                y = PAGE_HEIGHT - TOP_MARGIN
            c.drawString(x, y, ln)
            y -= LINE_HEIGHT

        # extra spacing between paragraphs
        y -= LINE_HEIGHT/2

    c.save()
    print(f'Wrote {OUTPUT}')

if __name__ == '__main__':
    main()
