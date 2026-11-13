"""Generar el memo PDF del Desafío 4 desde el Markdown en la raíz."""
from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
styles = getSampleStyleSheet()
styles["BodyText"].fontSize = 10.5
styles["BodyText"].leading = 14.5
styles["BodyText"].spaceBefore = 7
styles["Heading2"].textColor = colors.HexColor("#173b57")


def tabla(block):
    rows = [[col.strip() for col in line.strip("|").split("|")]
            for line in block.splitlines() if not line.startswith("|---")]
    cells = [[Paragraph(escape(col), styles["BodyText"]) for col in row] for row in rows]
    widths = [132, 93, 63, 100, 99] if len(rows[0]) == 5 else [153, 110, 108, 116]
    t = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dce8f0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f5f8")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def main():
    items = []
    for block in (ROOT / "memo_desafio4.md").read_text().strip().split("\n\n"):
        if block == "<!-- PAGINA -->":
            items.append(PageBreak())
        elif block.startswith("|"):
            items.append(tabla(block))
        else:
            style = "Title" if block.startswith("# ") else "Heading2" if block.startswith("## ") else "BodyText"
            t = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", escape(block.lstrip("# ").replace("×", "x")))
            items.append(Paragraph(t, styles[style]))
    path = ROOT / "entrega_desafio4" / "memo_riesgo.pdf"
    path.parent.mkdir(exist_ok=True)
    SimpleDocTemplate(str(path), title="Riesgo diario de la cartera regional",
                      author="Diego Martinez", leftMargin=55, rightMargin=55,
                      topMargin=40, bottomMargin=40).build(items)


if __name__ == "__main__":
    main()
