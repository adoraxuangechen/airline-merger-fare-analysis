#!/usr/bin/env python3
"""Build review PDFs and resolved Markdown from the saved analysis registry.

No estimates are generated or adjusted by this document builder. Dependencies:
reportlab. Optional matplotlib locates portable DejaVu font files.
"""
import argparse,csv,json,re,html
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT,TA_CENTER
from reportlab.lib.colors import HexColor,black
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether

def register_fonts(english_only=False):
    candidates=[Path('/System/Library/Fonts/Supplemental')]
    try:
        import matplotlib
        candidates.append(Path(matplotlib.get_data_path())/'fonts/ttf')
    except ImportError:pass
    candidates.extend([Path('/usr/share/fonts/truetype/dejavu')])
    for folder in candidates:
        if (folder/'Times New Roman.ttf').exists():
            files=['Times New Roman.ttf','Times New Roman Bold.ttf','Times New Roman Italic.ttf','Times New Roman Bold Italic.ttf'];break
        if (folder/'DejaVuSerif.ttf').exists():
            files=['DejaVuSerif.ttf','DejaVuSerif-Bold.ttf','DejaVuSerif-Italic.ttf','DejaVuSerif-BoldItalic.ttf'];break
    else:raise FileNotFoundError('Install DejaVu fonts or matplotlib to build the PDFs.')
    for name,file in zip(['Body','Body-Bold','Body-Italic','Body-BoldItalic'],files):pdfmetrics.registerFont(TTFont(name,str(folder/file)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='Body-Bold',italic='Body-Italic',boldItalic='Body-BoldItalic')
    if english_only:return
    chinese=Path('/System/Library/Fonts/STHeiti Light.ttc')
    if chinese.exists():pdfmetrics.registerFont(TTFont('ChineseEmbedded',str(chinese),subfontIndex=0))
    else:
        import os
        chinese=Path(os.environ.get('CHINESE_FONT_FILE',''))
        if not chinese.is_file():raise FileNotFoundError('Set CHINESE_FONT_FILE to a CJK TrueType font for the Chinese note.')
        pdfmetrics.registerFont(TTFont('ChineseEmbedded',str(chinese),subfontIndex=0))

def rows(path):
    with path.open() as f:return list(csv.DictReader(f))

def rich(text):
    text=html.escape(text)
    text=re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',r'<a href="\2" color="#28576a">\1</a>',text)
    return text

def pct(x):return f'{x:.2f}'
def ci(c):return f'[{c["pct_lo"]:.2f}%, {c["pct_hi"]:.2f}%]'

def data(root):
    source=root/'results_v2'
    if not source.exists():source=root/'results'
    reg=json.loads((source/'extended_results.json').read_text());m=reg['models'];meta=reg['metadata']
    b={ (v['sample'],v['treated']):v for v in meta['balance']}
    def c(name,term='did'):return m[name]['coef'][term]
    val={}
    for label,model in [('baseline','published_baseline'),('valid','same_sample_unadjusted'),('distance','distance_quarter'),('adjusted','distance_and_composition_quarter'),('support','common_support_cell_quarter'),('expanded','all_controls_adjusted'),('expanded_support','all_controls_support')]:
        val[label+'_pct']=pct(c(model)['pct']);val[label+'_ci']=ci(c(model))
    val.update(support_treated=m['common_support_cell_quarter']['treated'],support_controls=m['common_support_cell_quarter']['controls'],expanded_controls=m['all_controls_adjusted']['controls'],
               dose_median=f'{meta["concentration_median_split"]:.2f}',dose_mean=f'{b["legacy",1]["delta_proxy"]:.2f}',dose_pct=pct(c('concentration_dose','per100')['pct']),dose_ci=ci(c('concentration_dose','per100')),
               dose_difference_p=f'{m["concentration_groups"]["high_minus_low"]["p"]:.3f}',
               coverage_treated=f'{100*b["legacy",1]["single_coverage"]:.1f}',coverage_controls=f'{100*b["legacy",0]["single_coverage"]:.1f}',hhi_treated=f'{b["legacy",1]["hhi_single"]:,.0f}',hhi_controls=f'{b["legacy",0]["hhi_single"]:,.0f}',
               pre_base_f=f'{m["event_base"]["pre_2005_2007"]["F"]:.2f}',pre_adj_f=f'{m["event_adjusted"]["pre_2005_2007"]["F"]:.2f}',pre_support_p=f'{m["event_support"]["pre_2005_2007"]["p"]:.5f}')
    tables={}
    tables['sample']=(['Stage','Count'],[
        ['NBER aggregate records,2005-2010','4,175,354'],['Records after cleaning','4,175,350'],['Observed airport-pair quarters','609,396'],['Routes meeting2007 eligibility','5,535'],['Initial overlap / comparison routes','156 / 105'],['Initial route-quarter observations','6,259'],['Distance-adjusted routes / observations','260 / 6,235']], [360,148])
    balance=[]
    for col,label,fmt in [('routes','Routes',lambda x:f'{x:,}'),('distance','Distance (miles)',lambda x:f'{x:,.0f}'),('one_share','One-coupon share',lambda x:f'{100*x:.1f}%'),('fare_pre','Mean fare ($)',lambda x:f'{x:.2f}'),('pax_pre','Quarterly sample passengers',lambda x:f'{x:,.0f}')]:
        balance.append([label,*[fmt(b[s,t][col]) for s,t in [('legacy',1),('legacy',0),('common_support',1),('common_support',0)]]])
    tables['balance_main']=(['Characteristic','Initial\noverlap','Initial\ncomparison','Support\noverlap','Support\ncomparison'],balance,[170,80,86,86,86])
    labels=[('published_baseline','Initial comparison'),('same_sample_unadjusted','Same sample; valid distance'),('distance_quarter','Distance × quarter'),('distance_and_composition_quarter','Distance + composition × quarter'),('common_support_cell_quarter','Common support; joint-cell × quarter'),('all_controls_adjusted','Broader controls; adjusted'),('all_controls_support','Broader controls; common support')]
    tables['core']=(['Specification','Change %','95% interval','T / C'],[[label,pct(c(key)['pct']),ci(c(key)),f'{m[key]["treated"]} / {m[key]["controls"]}'] for key,label in labels],[256,65,115,72])
    dl=[('concentration_groups','low','Lower exposure'),('concentration_groups','high','Higher exposure'),('concentration_dose','per100','Continuous: per100 proxy points')]
    tables['dose_groups']=(['Exposure measure','Change %','95% interval'],[[label,pct(c(key,term)['pct']),ci(c(key,term))] for key,term,label in dl],[300,75,133])
    robust=[('end_2009','End in2009'),('start_2006','Start in2006'),('exclude_UA_CO','Exclude2007 UA/CO presence'),('route_trends','Add route-specific linear trends'),('omit_transition','Omit2008Q2-2008Q4')]
    tables['robustness']=(['Specification','Change %','95% interval','T / C'],[[label,pct(c(key)['pct']),ci(c(key)),f'{m[key]["treated"]} / {m[key]["controls"]}'] for key,label in robust],[256,65,115,72])
    tables['fields']=(['Field','Meaning'],[
        ['yr, qtr','Calendar year and quarter.'],['ap1, ap2','Alphabetically ordered airport pair; directions combined.'],['cr1, cr2','Alphabetically ordered operating-carrier set; blankcr2 on one-coupon records.'],['cop','0: one coupon;1: two coupons.'],['pax','Sampled journeys represented by the cell.'],['avprc','Cell average one-way-equivalent fare, nominal dollars.'],['nsdst','Airport-pair distance; zero treated as a sentinel.'],['avdst','Mean routing distance; not a baseline control.']],[100,408])
    tables['support_counts']=(['Population','Treated','Comparison','Quarters'],[[label,m[key]['treated'],m[key]['controls'],f'{m[key]["N"]:,}'] for key,label in [('same_sample_unadjusted','Legacy; valid distance'),('common_support_cell_quarter','Legacy common support'),('all_controls_adjusted','All unexposed; valid distance'),('all_controls_support','All unexposed common support')]],[290,70,78,70])
    tables['dose_full']=(['Model / term','β','SE','Change % [95% interval]'],[[label,f'{c(k,t)["b"]:.5f}',f'{c(k,t)["se"]:.5f}',pct(c(k,t)['pct'])+' '+ci(c(k,t))] for k,t,label in dl+[('concentration_within_overlap','overlap','Binary overlap; centered dose'),('concentration_within_overlap','per100_within','Within-overlap: per100')]], [215,65,65,163])
    allkeys=labels[:5]+[('all_controls_unadjusted','All controls; unadjusted')]+labels[5:]+robust
    tables['all_pooled']=(['Specification','β (SE)','Change % [95% interval]','N'],[[label,f'{c(k)["b"]:.4f}\n({c(k)["se"]:.4f})',pct(c(k)['pct'])+' '+ci(c(k)),f'{m[k]["N"]:,}'] for k,label in allkeys],[218,78,156,56])
    event=[]
    for t in range(1,25):
        label=f'{2005+(t-1)//4}Q{(t-1)%4+1}'
        if t==12:event.append([label,'0 (reference)','-','-'])
        else:
            z=c('event_adjusted',f'q{t}');event.append([label,f'{z["b"]:+.4f}',f'{z["se"]:.4f}',f'[{z["lo"]:+.4f}, {z["hi"]:+.4f}]'])
    tables['event_full']=(['Quarter','Coefficient','SE','95% interval'],event,[108,110,100,190])
    tables['pretests']=(['Model','F(11,G-1)','p'],[[label,f'{m[k]["pre_2005_2007"]["F"]:.3f}',f'{m[k]["pre_2005_2007"]["p"]:.3g}'] for k,label in [('event_base','Unadjusted'),('event_adjusted','Composition adjusted'),('event_support','Legacy support'),('event_expanded_support','Expanded support')]],[290,110,108])
    old=root/'archive/v1/results/specification_bridge.csv'
    if not old.exists():old=root/'results/specification_bridge.csv'
    oldrows=rows(old)
    tables['old_bridge']=(['Sequential change','Change %','Treated','Comparison'],[[lab,f'{float(z["percent"]):+.2f}',f'{int(z["treated_routes"]):,}',f'{int(z["control_routes"]):,}'] for lab,z in zip(['A. Original implementation','B. Correct fixed effects only','C. Passenger-weighted fare','D.2007 eligibility','E. Empirical overlap','F. Legacy comparison restriction'],oldrows)],[275,75,78,80])
    tables['files']=(['Location','Purpose'],[['analysis/extend_analysis.py','Canonical-source preparation, fixed design sequence, all estimates and plots.'],['analysis/independent_check.py','Independent raw-dummy regression validation.'],['scripts/download_nber.py','Download/check source and extract six years preserving NA.'],['results/model_registry.csv','All pooled and event coefficients, intervals, sample counts.'],['results/route_features.csv','All route classifications and2007 concentration measures.'],['results/panel_*.csv','Saved analysis panels for each comparison.'],['provenance/','Source manifests, archive audit, research notes.'],['documents/','Source text and PDF builder.'],['archive/v1/','Prior paper, outputs, code and documentation.']],[218,290])
    return source,val,tables

def build(root,out,english_only=False):
    register_fonts(english_only);source,val,tables=data(root);out.mkdir(parents=True,exist_ok=True)
    body=ParagraphStyle('Body',fontName='Body',fontSize=11.05,leading=14.25,spaceAfter=8.0,allowWidows=0,allowOrphans=0)
    for stem,title,cn in [('writing_sample_v2','Fare Changes After the Delta-Northwest Merger',False),('technical_supplement_v2','Technical Supplement',False)]:
        if english_only and cn:continue
        normal=ParagraphStyle('Normal',parent=body,fontName='ChineseEmbedded' if cn else 'Body',fontSize=10.6 if cn else 11.05,leading=16.2 if cn else 14.25,wordWrap='CJK' if cn else None)
        heading=ParagraphStyle('Heading',parent=normal,fontName='ChineseEmbedded' if cn else 'Body-Bold',fontSize=12.7,leading=16.2,spaceBefore=6,spaceAfter=9,keepWithNext=True)
        title_style=ParagraphStyle('Title',parent=heading,fontSize=19,leading=22.5,spaceBefore=0,spaceAfter=7)
        sub=ParagraphStyle('Sub',parent=normal,fontSize=12,leading=15,spaceAfter=9,textColor=HexColor('#384952'))
        cap=ParagraphStyle('Caption',parent=normal,fontSize=8.7 if not cn else 9.2,leading=11.2 if not cn else 13.5,spaceAfter=9,textColor=HexColor('#3d454a'))
        cell=ParagraphStyle('Cell',parent=normal,fontSize=9.0 if not cn else 9.5,leading=11.2 if not cn else 13,spaceAfter=0)
        headcell=ParagraphStyle('HeadCell',parent=cell,fontName='ChineseEmbedded' if cn else 'Body-Bold')
        story=[];resolved=[]
        text=(root/'documents'/f'{stem}.md').read_text()
        for key,value in val.items():text=text.replace('{{'+key+'}}',str(value))
        text=text.replace('@page\n','@page\n\n')
        assert '{{' not in text,stem
        for block in re.split(r'\n\s*\n',text.strip()):
            block=block.strip()
            if block.startswith('@table '):
                name=block.splitlines()[0][7:];headers,records,widths=tables[name]
                grid=[[Paragraph(rich(str(v)).replace('\n','<br/>'),headcell) for v in headers]]
                grid.extend([[Paragraph(rich(str(v)).replace('\n','<br/>'),cell) for v in row] for row in records])
                table=Table(grid,colWidths=widths,repeatRows=1,hAlign='LEFT')
                table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEABOVE',(0,0),(-1,0),.8,black),('LINEBELOW',(0,0),(-1,0),.55,black),('LINEBELOW',(0,-1),(-1,-1),.6,black),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),('ROWBACKGROUNDS',(0,1),(-1,-1),[HexColor('#ffffff'),HexColor('#f4f6f7')])]))
                story.append(table);story.append(Spacer(1,7))
                resolved.extend(['| '+' | '.join(h.replace('\n',' ') for h in headers)+' |','|'+'|'.join([' --- ']*len(headers))+'|',*['| '+' | '.join(str(v).replace('\n',' ') for v in row)+' |' for row in records]])
                for line in block.splitlines()[1:]:
                    story.append(Paragraph(rich(line.removeprefix('@caption ')),cap));resolved.append(line.removeprefix('@caption '))
            elif block.startswith('@figure '):
                file=block.splitlines()[0][8:];story.append(Image(str(source/file),width=508,height=348.34));story.append(Spacer(1,6));resolved.append(f'![Event-study comparison](../results/{file})')
                for line in block.splitlines()[1:]:
                    story.append(Paragraph(rich(line.removeprefix('@caption ')),cap));resolved.append(line.removeprefix('@caption '))
            elif block=='@page':story.append(PageBreak());resolved.append('\n<!-- page break -->')
            elif block.startswith('@equation '):
                eq=ParagraphStyle('Equation',parent=normal,fontSize=10.1,leading=14,alignment=TA_CENTER,spaceAfter=11)
                formula=rich(block[10:]).replace('γ_distance(r),t','γ<sub>d(r),t</sub>').replace('η_share(r),t','η<sub>c(r),t</sub>')
                formula=re.sub(r'([A-Za-z]+|[αβγηλε])_([A-Za-z]+)',r'\1<sub>\2</sub>',formula)
                story.append(Paragraph(formula,eq));resolved.append(block[10:])
            elif block.startswith('@mono '):
                story.append(Paragraph(rich(block[6:]),cap));resolved.append(block[6:])
            elif block.startswith('@caption '):story.append(Paragraph(rich(block[9:]),cap));resolved.append(block[9:])
            elif block.startswith('# '):
                # Title, subtitle and byline can be contiguous source lines.
                for line in block.splitlines():
                    if line.startswith('# '):story.append(Paragraph(rich(line[2:]),title_style))
                    elif line.startswith('## '):story.append(Paragraph(rich(line[3:]),sub))
                    elif line.startswith('@byline '):story.append(Paragraph(rich(line[8:]),cap));story.append(Spacer(1,6))
                    else:story.append(Paragraph(rich(line),normal))
                resolved.append(block.replace('@byline ',''))
            elif block.startswith('### '):story.append(Paragraph(rich(block[4:]),heading));resolved.append(block)
            else:story.append(Paragraph(rich(block),normal));resolved.append(block)
            resolved.append('')
        def page(canvas,doc):
            canvas.saveState();canvas.setFont('Body',8.2);canvas.setFillColor(HexColor('#657078'))
            canvas.drawString(52,letter[1]-31,'Adora Chen | Delta-Northwest fare analysis | Review draft')
            canvas.drawRightString(letter[0]-52,31,str(doc.page));canvas.restoreState()
        doc=SimpleDocTemplate(str(out/(stem+'.pdf')),pagesize=letter,rightMargin=52,leftMargin=52,topMargin=48,bottomMargin=47,title=title,author='Xuange (Adora) Chen',pageCompression=1)
        doc.build(story,onFirstPage=page,onLaterPages=page)
        (out/(stem+'.md')).write_text('\n'.join(resolved))
        print('Built',out/(stem+'.pdf'))
    (out/'document_values.json').write_text(json.dumps(val,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--out',type=Path);ap.add_argument('--english-only',action='store_true',help='Build the main paper and supplement without requiring a Chinese font');args=ap.parse_args()
    build(args.root,args.out or args.root/'papers',args.english_only)
