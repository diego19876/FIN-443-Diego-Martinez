"""Convierte el informe Markdown en PDF de dos páginas con ReportLab."""
from pathlib import Path
import re
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4

root = Path(__file__).resolve().parents[1]
destination = root / 'entrega_desafio3' / 'informe_desafio3.pdf'
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyReport',fontName='Helvetica',fontSize=9.6,leading=12.3,spaceAfter=6.5,alignment=TA_LEFT))
styles.add(ParagraphStyle(name='ReportTitle',fontName='Helvetica-Bold',fontSize=15,leading=18,spaceAfter=6))
styles.add(ParagraphStyle(name='ReportHeading',fontName='Helvetica-Bold',fontSize=10.4,leading=13,spaceBefore=8,spaceAfter=5))
styles.add(ParagraphStyle(name='ReportReference',fontName='Helvetica',fontSize=8.5,leading=11,spaceAfter=6,leftIndent=12,firstLineIndent=-12))
styles.add(ParagraphStyle(name='TableText',fontName='Helvetica',fontSize=8.3,leading=10.5))

def inline(text):
    text=escape(text)
    return re.sub(r'\*([^*]+)\*',r'<i>\1</i>',text)

lines=(root/'informe_desafio3.md').read_text().splitlines()
story=[]
i=0
reference=False
while i<len(lines):
    line=lines[i]
    if not line.strip(): i+=1; continue
    if line.startswith('# '):
        story.append(Paragraph(inline(line[2:]),styles['ReportTitle']))
    elif line.startswith('## '):
        if line.startswith('## Riesgo,'):
            story.append(PageBreak())
        reference=line=='## Referencias'
        story.append(Paragraph(inline(line[3:]),styles['ReportHeading']))
    elif line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].startswith('|'):
            if not re.match(r'^\|\s*:?-',lines[i]):
                rows.append([Paragraph(inline(cell.strip()),styles['TableText']) for cell in lines[i].strip('|').split('|')])
            i+=1
        table=Table(rows,colWidths=[94,58,55,56,75,66,66],repeatRows=1,hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E9EEF3')),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F7F8FA')]),
            ('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#AAB8C5')),
        ]))
        story.extend([table,Spacer(1,7)])
        continue
    else:
        story.append(Paragraph(inline(line),styles['ReportReference' if reference else 'BodyReport']))
    i+=1

def page_number(canvas,doc):
    canvas.setFont('Helvetica',8)
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.drawRightString(A4[0]-35,23,str(doc.page))

doc=SimpleDocTemplate(str(destination),pagesize=A4,rightMargin=31,leftMargin=31,topMargin=30,bottomMargin=34,
                     title='Desafío 3 - FIN443',author='Diego Martinez')
doc.build(story,onFirstPage=page_number,onLaterPages=page_number)
print(destination)
