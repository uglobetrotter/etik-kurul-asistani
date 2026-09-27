"""Convert a DOCX to PDF through Word so the result can actually be looked at.

XML-level checks pass on layouts that are visibly broken: a row grown to half a page
because text landed in a spacer column, a doubled tick mark, a heading whose paragraph
marks turned bold. Rendering through Word and reading the pages is the only check that
catches those, and on this form it has caught all three.

    python to_pdf.py FORM.docx                 # -> FORM.pdf next to it
    python to_pdf.py FORM.docx out/preview.pdf

Needs Word installed. On Windows it drives Word through COM (pywin32); on macOS it
drives Microsoft Word through AppleScript (osascript). Falls back with a clear message
if neither is available.
"""

import os
import subprocess
import sys

# Word for Mac: open the document, save it as PDF, count the pages, close without
# saving. Paths arrive as arguments so no quoting is spliced into the script.
MAC_SCRIPT = """
on run argv
    set srcPath to item 1 of argv
    set dstPath to item 2 of argv
    tell application "Microsoft Word"
        open (POSIX file srcPath)
        set theDoc to active document
        try
            save as theDoc file name dstPath file format format PDF
        on error errMsg number errNum
            close theDoc saving no
            error errMsg number errNum
        end try
        set pageCount to "?"
        try
            set pageCount to compute statistics theDoc statistic statistic pages
        end try
        close theDoc saving no
    end tell
    return pageCount as text
end run
"""

MAC_TIMEOUT = 300  # seconds; a cold Word start plus a 10-page export fits well inside


def _convert_windows(src, dst):
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
    return pages


def _convert_macos(src, dst):
    # `open -Ra` only looks the application up; it never launches it and never shows
    # the "Where is Microsoft Word?" dialog that a bare `tell application` would.
    found = subprocess.run(["open", "-Ra", "Microsoft Word"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if found.returncode != 0:
        raise SystemExit("Microsoft Word bulunamadi. Word for Mac'i kur ya da PDF'i Word'de elle uret.")

    try:
        result = subprocess.run(["osascript", "-", src, dst], input=MAC_SCRIPT,
                                capture_output=True, text=True, timeout=MAC_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise SystemExit(
            f"Word {MAC_TIMEOUT} sn icinde yanit vermedi. Word'de acik bir iletisim kutusu "
            "(ilk calistirma, dosya erisim izni) olabilir; kapatip yeniden dene.")
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        hint = ""
        if "-1743" in detail or "Not authorized" in detail:
            hint = (" Terminal'in Word'u denetlemesine izin ver: Sistem Ayarlari > "
                    "Gizlilik ve Guvenlik > Otomasyon.")
        raise SystemExit(f"Word PDF'e cevirmedi: {detail}{hint}")
    if not os.path.isfile(dst):
        raise SystemExit(
            f"Word hata vermedi ama {dst} olusmadi. Word dosya erisim izni istemis olabilir; "
            "izni verip yeniden dene.")
    try:
        return int(result.stdout.strip())
    except ValueError:
        return "?"


def convert(src, dst=None):
    src = os.path.abspath(src)
    if dst is None:
        dst = os.path.splitext(src)[0] + ".pdf"
    dst = os.path.abspath(dst)
    os.makedirs(os.path.dirname(dst), exist_ok=True)

    if sys.platform == "darwin":
        pages = _convert_macos(src, dst)
    elif sys.platform == "win32":
        pages = _convert_windows(src, dst)
    else:
        raise SystemExit(f"Bu platformda ({sys.platform}) Word yok. PDF'i Windows ya da "
                         "macOS'ta Word ile uret.")

    print(f"{dst}  ({pages} sayfa)")
    return dst, pages


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    convert(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
