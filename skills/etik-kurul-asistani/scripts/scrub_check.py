"""Scan every XML part of an EY.FR.75 copy for leftovers from the previous study.

There is no blank EY.FR.75 template on this machine, so a new application is normally
built by clearing a filled copy. The failure mode that matters is a term from the old
study surviving somewhere the eye does not go: a text box, a comment, a header, the
document properties, a custom XML island. Checking word/document.xml alone is what let
one through before.

    python scrub_check.py FORM.docx --terms sarkopeni,divertikulit,"Ali Osman"
    python scrub_check.py FORM.docx --terms-file eski_terimler.txt
    python scrub_check.py FORM.docx            # identifier + placeholder sweep only

Always runs, regardless of --terms:
  * TC kimlik-shaped 11-digit runs, and protocol/decision numbers like 2026/0316
  * unfilled markers: [ ], [KULLANICI DOLDURACAK], TBD, XXX, <...>
  * author/company metadata in docProps (python-docx leaves its own fingerprint)

Exit code 1 if anything was found, so it can gate a build script.
"""

import argparse
import os
import re
import sys
import zipfile

TEXT_PARTS = re.compile(r"\.(xml|rels)$")

IDENTIFIER_PATTERNS = [
    ("11 haneli TC kimlik gorunumlu sayi", re.compile(r"(?<!\d)[1-9]\d{10}(?!\d)")),
    ("karar/protokol numarasi", re.compile(r"\b20\d{2}\s*/\s*\d{3,5}\b")),
    ("hasta/dosya numarasi gorunumlu etiket",
     re.compile(r"(protokol|dosya|hasta)\s*(no|numaras[ıi])\s*[:=]\s*\S+", re.I)),
]

PLACEHOLDER_PATTERNS = [
    ("doldurulmamis yer tutucu", re.compile(r"\[(?:[^\[\]]{0,80})(DOLDUR|AD SOYAD|TARIH|TBD|XX)"
                                            r"(?:[^\[\]]{0,80})\]", re.I)),
    ("acik kose parantez", re.compile(r"<[A-ZÇĞİÖŞÜ][^<>]{2,40}>")),
    ("TBD / XXX", re.compile(r"\b(TBD|XXX+|LOREM)\b", re.I)),
]

# Word splits a word across runs freely, so match against text with tags stripped.
TAG_RE = re.compile(r"<[^>]+>")


def part_text(raw):
    return TAG_RE.sub("", raw.decode("utf-8", "replace"))


def context(text, m, width=45):
    a = max(0, m.start() - width)
    b = min(len(text), m.end() + width)
    return " ".join(text[a:b].split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--terms", default="", help="comma-separated terms from the old study")
    ap.add_argument("--terms-file", help="one term per line")
    ap.add_argument("--quiet-metadata", action="store_true",
                    help="skip the docProps author/company report")
    args = ap.parse_args()

    terms = [t.strip() for t in args.terms.split(",") if t.strip()]
    if args.terms_file:
        with open(args.terms_file, encoding="utf-8") as fh:
            terms += [l.strip() for l in fh if l.strip() and not l.startswith("#")]

    hits = 0
    with zipfile.ZipFile(args.path) as z:
        names = [n for n in z.namelist() if TEXT_PARTS.search(n)]
        print(f"file : {os.path.basename(args.path)}")
        print(f"parts: {len(names)} XML parts scanned "
              f"({sum(1 for n in names if n.startswith('word/'))} under word/)")
        print()

        for name in names:
            text = part_text(z.read(name))

            for term in terms:
                for m in re.finditer(re.escape(term), text, re.I):
                    hits += 1
                    print(f"[ESKI TERIM] {name}: '{term}' -> ...{context(text, m)}...")

            for label, pat in IDENTIFIER_PATTERNS + PLACEHOLDER_PATTERNS:
                for m in pat.finditer(text):
                    hits += 1
                    print(f"[{label}] {name}: ...{context(text, m)}...")

        if not args.quiet_metadata:
            for prop in ("docProps/core.xml", "docProps/app.xml"):
                if prop in z.namelist():
                    raw = z.read(prop).decode("utf-8", "replace")
                    for tag in ("dc:creator", "cp:lastModifiedBy", "Company", "Manager"):
                        for m in re.finditer(rf"<{tag}>(.*?)</{tag}>", raw, re.S):
                            val = m.group(1).strip()
                            if val:
                                print(f"[METADATA] {prop} {tag} = {val}")

    print()
    if hits:
        print(f"{hits} bulgu. Her birini forma bakarak degerlendir; "
              f"tarih ve merkez adi gibi dogru olanlari birak.")
        sys.exit(1)
    print("Eski terim, kimlik gorunumlu sayi veya yer tutucu bulunamadi.")


if __name__ == "__main__":
    main()
