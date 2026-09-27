#!/usr/bin/env python3
"""Build the two English papers in the author's reference article style.

Numerical tables are read by the existing registry loader. No analysis is run.
The reference uses US Letter, one-inch side margins, Times-family type,
justified paragraphs, a centered abstract, and unshaded three-rule tables.
"""
import argparse
import csv
import html
import io
import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle,
)

from build_revision import data, register_fonts


WIDTH = 468
JOURNALS = [
    'American Economic Review: Insights', 'American Economic Review',
    'International Journal of Industrial Organization',
    'Review of Industrial Organization',
    'Review of Economic Studies',
]


def rich(text, reference=False):
    text = html.escape(text)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',
                  r'<a href="\2" color="#173a55">\1</a>', text)
    if reference:
        # Longest journal first; avoid inserting nested italic tags.
        pattern = '|'.join(re.escape(x) for x in JOURNALS)
        text = re.sub(pattern, lambda m: '<i>'+m.group()+'</i>', text)
    else:
        text = re.sub(r'\bs_(DL|NW)\b', r'<i>s</i><sub>\1</sub>', text)
        text = re.sub(r'\bdelta_t\b', 'δ<sub>t</sub>', text)
        text = re.sub(r'\bH_single\b', '<i>H</i><sub>single</sub>', text)
        text = re.sub(r'\bn_i\b', '<i>n</i><sub>i</sub>', text)
    return text


def caption_parts(block, kind):
    lines = block.splitlines()[1:]
    text = ' '.join(x.removeprefix('@caption ') for x in lines)
    match = re.match(rf'({kind} [A-Za-z0-9]+)\. ([^.]+)\.(?:\s*(.*))?$', text)
    if match:
        return match.group(1), match.group(2), match.group(3) or ''
    return '', '', text


def equation(number):
    import matplotlib as mpl
    from matplotlib.mathtext import math_to_image
    expressions = {
        1: r'$\overline{p}_{rt}=\frac{\sum_{i\in(r,t)}n_i\overline{p}_i}{\sum_{i\in(r,t)}n_i},\qquad y_{rt}=\log(\overline{p}_{rt}).$',
        2: r'$y_{rt}=\alpha_r+\lambda_t+\beta(\mathrm{Overlap}_r\times\mathrm{Post}_t)+\gamma_{d(r),t}+\eta_{c(r),t}+\epsilon_{rt}.$',
    }
    stream = io.BytesIO()
    with mpl.rc_context({'mathtext.fontset': 'stix', 'font.family': 'STIXGeneral', 'font.size': 11}):
        math_to_image(expressions[number], stream, dpi=400, format='png', color='black')
    stream.seek(0)
    w, h = ImageReader(stream).getSize()
    width = min(w*72/400, WIDTH-40)
    return Image(stream, width=width, height=h*width/w)


def styles():
    body = ParagraphStyle('Body', fontName='Body', fontSize=10.91, leading=14.63,
                          alignment=TA_JUSTIFY, firstLineIndent=13.09, spaceAfter=3.2,
                          allowWidows=0, allowOrphans=0, splitLongWords=True)
    result = {'body': body}
    result['first'] = ParagraphStyle('First', parent=body, firstLineIndent=0)
    result['heading'] = ParagraphStyle('Heading', parent=body, fontName='Body-Bold',
                                      fontSize=14.35, leading=18, firstLineIndent=0,
                                      alignment=TA_LEFT, spaceBefore=13, spaceAfter=7,
                                      keepWithNext=True)
    result['subheading'] = ParagraphStyle('Subheading', parent=result['heading'],
                                         fontSize=11.96, leading=15, spaceBefore=8)
    result['title'] = ParagraphStyle('Title', parent=result['heading'], alignment=TA_CENTER,
                                    leading=24.8, spaceBefore=0, spaceAfter=17)
    result['author'] = ParagraphStyle('Author', parent=body, alignment=TA_CENTER,
                                     firstLineIndent=0, fontSize=11.96, leading=16.5, spaceAfter=1)
    result['affiliation'] = ParagraphStyle('Affiliation', parent=result['author'],
                                          fontSize=9.96, leading=15, spaceAfter=0)
    result['abstract_head'] = ParagraphStyle('AbstractHead', parent=result['affiliation'],
                                             fontName='Body-Bold', spaceBefore=0, spaceAfter=7)
    result['abstract'] = ParagraphStyle('Abstract', parent=body, fontSize=9.96, leading=13,
                                        leftIndent=27.27, rightIndent=27.27, spaceAfter=13)
    result['caption'] = ParagraphStyle('Caption', parent=body, firstLineIndent=0,
                                       alignment=TA_CENTER, fontSize=9.96, leading=12.8,
                                       spaceBefore=5, spaceAfter=9, keepWithNext=True)
    result['note'] = ParagraphStyle('Note', parent=body, firstLineIndent=0,
                                    fontSize=8.97, leading=11.7, spaceAfter=9)
    result['cell'] = ParagraphStyle('Cell', parent=body, fontSize=9.55, leading=11.8,
                                     alignment=TA_LEFT, firstLineIndent=0, spaceAfter=0)
    result['cell_right'] = ParagraphStyle('CellRight', parent=result['cell'], alignment=TA_RIGHT)
    result['reference'] = ParagraphStyle('Reference', parent=body, alignment=TA_LEFT,
                                         leftIndent=10.91, firstLineIndent=-10.91,
                                         fontSize=10.5, leading=13.7, spaceAfter=5)
    return result


def normalize_spacing(text):
    # Whitespace corrections in generated table labels and source annotations.
    for a, b in {
        ',2005': ', 2005', 'meeting2007': 'meeting 2007', 'in2009': 'in 2009',
        'in2006': 'in 2006', 'Exclude2007': 'Exclude 2007', 'Omit2008': 'Omit 2008',
        'per100': 'per 100', 'blankcr2': 'blank cr2', 'coupon;1': 'coupon; 1',
        'D.2007': 'D. 2007', 'and2007': 'and 2007', 'All24': 'All 24',
        'omits2008': 'omits 2008', 'Reference2007': 'Reference 2007',
        'pointwise95': 'pointwise 95', 'NumPy2': 'NumPy 2', 'pandas2': 'pandas 2',
        'SciPy1': 'SciPy 1', 'statsmodels0': 'statsmodels 0', 'matplotlib3': 'matplotlib 3',
        'Review83': 'Review 83',
    }.items():
        text = text.replace(a, b)
    return text


def build(root, out):
    register_fonts(english_only=True)
    source, values, tables = data(root)
    models = json.loads((source/'extended_results.json').read_text())['models']
    primary = [('same_sample_unadjusted','Unadjusted benchmark'),
               ('distance_quarter','Distance by quarter'),
               ('distance_and_composition_quarter','Primary: distance and composition')]
    primary_rows = []
    for key, label in primary:
        c = models[key]['coef']['did']
        primary_rows.append([label, f'{c["pct"]:.2f}', f'[{c["pct_lo"]:.2f}%, {c["pct_hi"]:.2f}%]'])
    tables['primary_core'] = (['Specification','Change %','95% interval'], primary_rows, [265,70,133])
    extra = root/'extensions/carrier_diagnostics/results'
    with (extra/'wn_model_registry.csv').open() as f:
        wn = {r['model']:r for r in csv.DictReader(f)}
    wn_rows = []
    for key,label in [('legacy','Legacy'),('expanded','Expanded')]:
        cells = [label]
        for suffix in ['adjusted','adjusted_wn_present','adjusted_wn_bin']:
            row = wn[key+'_'+suffix]
            cells.append(f'{float(row["pct"]):.2f}%\n[{float(row["pct_lo"]):.2f}%, {float(row["pct_hi"]):.2f}%]')
        wn_rows.append(cells)
    tables['wn_main'] = (['Comparison','Composition\nadjusted','Add WN presence\nby quarter','Add WN-share bin\nby quarter'],wn_rows,[90,126,126,126])
    tables['wn_appendix'] = tables['wn_main']
    with (extra/'carrier_gap_period_contrasts.csv').open() as f:
        gaps = list(csv.DictReader(f))
    gap_labels = {'all_products_baseline_paired':'All products; baseline paired',
                  'all_products_balanced_24q':'All products; complete panel',
                  'two_coupon_only_baseline_paired':'Two coupons; baseline paired',
                  'two_coupon_only_balanced_24q':'Two coupons; complete panel'}
    tables['carrier_gaps'] = (['Sample','Routes / cells','Change %','95% interval'],
        [[gap_labels[r['model']], f'{r["routes"]} / {int(r["N"]):,}',f'{float(r["pct_ratio_change"]):.2f}',
          f'[{float(r["pct_lo"]):.2f}%, {float(r["pct_hi"]):.2f}%]'] for r in gaps],[218,85,55,110])
    with (root/'extensions/honestdid/sensitivity_summary.csv').open() as f:
        honest = list(csv.DictReader(f))
    tables['honest_rm'] = (['M','Log-point interval','Transformed interval','Grid step'],
        [[r['Mbar'],f'[{float(r["accepted_lower"]):.5f}, {float(r["accepted_upper"]):.5f}]',
          f'[{float(r["lower_percent"]):.1f}%, {float(r["upper_percent"]):.1f}%]',
          f'{float(r["grid_step"]):.5f}'] for r in honest],[35,173,170,90])
    out.mkdir(parents=True, exist_ok=True)
    st = styles()
    for stem, supplement in [('writing_sample_v2', False), ('technical_supplement_v2', True)]:
        text = (root/'documents'/f'{stem}.md').read_text()
        for key, value in values.items():
            text = text.replace('{{'+key+'}}', str(value))
        assert '{{' not in text
        assert not re.search(r'[\u3400-\u9fff]', text), 'English-only source required'
        text = normalize_spacing(text.replace('@page\n', '@page\n\n'))
        story = [NextPageTemplate('Body')]
        resolved = []
        after_heading = True
        in_references = False
        eq_number = 0
        for block in re.split(r'\n\s*\n', text.strip()):
            block = block.strip()
            if block.startswith('# '):
                lines = block.splitlines()
                title = lines[0][2:]
                subtitle = next((x[3:] for x in lines if x.startswith('## ')), '')
                story.append(Paragraph(rich(title)+'<br/>'+rich(subtitle), st['title']))
                story.append(Paragraph('Xuange (Adora) Chen', st['author']))
                story.append(Paragraph('The Pennsylvania State University', st['affiliation']))
                story.append(Paragraph('<a href="mailto:xmc5171@psu.edu" color="black">xmc5171@psu.edu</a>', st['affiliation']))
                story.append(Spacer(1, 14))
                story.append(Paragraph('Revised September 27, 2026', st['affiliation']))
                story.append(Spacer(1, 24 if not supplement else 16))
                resolved.append('# '+title+'\n## '+subtitle+'\nXuange (Adora) Chen\nThe Pennsylvania State University\nxmc5171@psu.edu\nRevised September 27, 2026')
            elif block.startswith('@abstract '):
                story.append(Paragraph('Abstract', st['abstract_head']))
                story.append(Paragraph(rich(block[10:]), st['abstract']))
                resolved.append('### Abstract\n\n'+block[10:])
            elif block.startswith('@keywords '):
                story.append(Paragraph('<b>Keywords:</b> '+rich(block[10:]), st['first']))
                story.append(Spacer(1, 5))
                resolved.append('Keywords: '+block[10:])
            elif block.startswith('@table '):
                name = block.splitlines()[0][7:]
                headers, records, widths = tables[name]
                label, title, notes = caption_parts(block, 'Table')
                grid = []
                for row in [headers]+records:
                    grid.append([Paragraph(rich(normalize_spacing(str(value))).replace('\n', '<br/>'),
                                           st['cell'] if i == 0 or name in ('fields', 'files') else st['cell_right'])
                                 for i, value in enumerate(row)])
                scaled = [x*WIDTH/sum(widths) for x in widths]
                table = Table(grid, colWidths=scaled, repeatRows=1, hAlign='CENTER')
                table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LINEABOVE', (0, 0), (-1, 0), .85, colors.black),
                    ('LINEBELOW', (0, 0), (-1, 0), .5, colors.black),
                    ('LINEBELOW', (0, -1), (-1, -1), .65, colors.black),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('TOPPADDING', (0, 0), (-1, -1), 2.3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2.3),
                ]))
                items = [Paragraph(f'<b>{rich(label)}:</b> {rich(title)}', st['caption']), table, Spacer(1, 5)]
                if notes:
                    items.append(Paragraph(rich(notes), st['note']))
                story.append(KeepTogether(items))
                resolved += [f'{label}: {title}', '| '+' | '.join(x.replace('\n', ' ') for x in headers)+' |',
                             '|'+'|'.join([' --- ']*len(headers))+'|',
                             *['| '+' | '.join(normalize_spacing(str(x)).replace('\n',' ') for x in row)+' |' for row in records], notes]
                after_heading = True
            elif block.startswith('@figure '):
                file = block.splitlines()[0][8:]
                label, title, notes = caption_parts(block, 'Figure')
                width, height = ImageReader(str(source/file)).getSize()
                image = Image(str(source/file), width=WIDTH, height=height*WIDTH/width)
                items = [Spacer(1, 5), image,
                         Paragraph(f'<b>{rich(label)}:</b> {rich(title)}', st['caption'])]
                if notes:
                    items.append(Paragraph(rich(notes), st['note']))
                story.append(KeepTogether(items))
                resolved += [f'![{label}: {title}](../results/{file})', notes]
                after_heading = True
            elif block == '@page':
                # Both documents flow naturally; captions and tables stay together.
                pass
            elif block.startswith('@equation '):
                eq_number += 1
                formula = equation(eq_number)
                row = Table([[formula, Paragraph(f'({eq_number})', st['cell_right'])]], colWidths=[WIDTH-30, 30])
                row.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                         ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                                         ('TOPPADDING', (0, 0), (-1, -1), 7),
                                         ('BOTTOMPADDING', (0, 0), (-1, -1), 9)]))
                story.append(row)
                resolved.append(block[10:]+f' ({eq_number})')
                after_heading = True
            elif block.startswith('@mono ') or block.startswith('@caption '):
                value = block.split(' ', 1)[1]
                story.append(Paragraph(rich(value), st['note']))
                resolved.append(value)
            elif block.startswith('### '):
                heading = re.sub(r'^([0-9]+|[A-Z])\. ', r'\1  ', block[4:])
                in_references = heading == 'References'
                story.append(Paragraph(rich(heading), st['heading']))
                resolved.append('### '+heading)
                after_heading = True
            elif block.startswith('#### '):
                story.append(Paragraph(rich(block[5:]), st['subheading']))
                resolved.append(block)
                after_heading = True
            else:
                style = st['reference'] if in_references else st['first'] if after_heading else st['body']
                story.append(Paragraph(rich(block, reference=in_references), style))
                resolved.append(block)
                after_heading = False
            resolved.append('')

        def first_page(canvas, doc):
            pass

        def later_page(canvas, doc):
            canvas.saveState()
            canvas.setFont('Body', 9.96)
            short = 'Delta-Northwest Merger: Technical Supplement' if supplement else 'Delta-Northwest Merger: Route-Level Fares'
            canvas.drawString(72, 749.5, short)
            canvas.drawRightString(540, 749.5, 'Adora Chen')
            canvas.setLineWidth(.4)
            canvas.line(72, 742.7, 540, 742.7)
            canvas.setFont('Body', 10.91)
            canvas.drawCentredString(306, 36, str(doc.page))
            canvas.restoreState()

        doc = BaseDocTemplate(str(out/f'{stem}.pdf'), pagesize=(612, 792),
                               title='Delta-Northwest Merger: Technical Supplement' if supplement else 'Fare Changes After the Delta-Northwest Merger: Market Composition and Competitive Exposure',
                               author='Xuange (Adora) Chen', pageCompression=1,
                               leftMargin=72, rightMargin=72, topMargin=72, bottomMargin=56)
        doc.addPageTemplates([
            PageTemplate(id='First', frames=Frame(72, 56, WIDTH, 654, id='first',
                                                 leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0), onPage=first_page),
            PageTemplate(id='Body', frames=Frame(72, 56, WIDTH, 664, id='body',
                                                leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0), onPage=later_page),
        ])
        doc.build(story)
        (out/f'{stem}.md').write_text('\n'.join(resolved))
        print('Built', out/f'{stem}.pdf')
    (out/'document_values.json').write_text(json.dumps(values, indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    build(args.root, args.out or args.root/'papers')
