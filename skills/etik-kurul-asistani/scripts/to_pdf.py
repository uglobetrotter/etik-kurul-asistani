"""Convert a DOCX to PDF through Word so the result can actually be looked at.

XML-level checks pass on layouts that are visibly broken: a row grown to half a page
because text landed in a spacer column, a doubled tick mark, a heading whose paragraph
marks turned bold. Rendering through Word and reading the pages is the only check that
catches those, and on this form it has caught all three.

    python to_pdf.py FORM.docx                 # -> FORM.pdf next to it
    python to_pdf.py FORM.docx out/preview.pdf

Needs Word installed (pywin32). Falls back with a clear message if it is not.
"""

import os
import sys


def convert(src, dst=None):
    src = os.path.abspath(src)
    if dst is None:
        dst = os.path.splitext(src)[0] + ".pdf"
    dst = os.path.abspath(dst)
    os.makedirs(os.path.dirname(dst), exist_ok=True)

    try:
        import win32com.client
    except ImportError:
        raise SystemExit("pywin32 yok. 'pip install pywin32' ya da PDF'i Word'de elle uret.")

    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        doc = word.Documents.Open(src, ReadOnly=True, AddToRecentFiles=False)
        try:
            doc.SaveAs(dst, FileFormat=17)   # wdFormatPDF
            pages = doc.ComputeStatistics(2)  # wdStatisticPages
        finally:
            doc.Close(False)
    finally:
        word.Quit()

    print(f"{dst}  ({pages} sayfa)")
    return dst, pages


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    convert(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
