"""Print the item map and tick-box state of an EY.FR.75 copy.

Run this first on whatever copy you are starting from. Circulating copies differ:
some have lost a checkbox, some have the label overwritten by the previous study's
value, some carry leftover text. Seeing the real state beats assuming the template.

    python inspect_form.py FORM.docx              # item map + box audit
    python inspect_form.py FORM.docx --boxes      # ticked boxes only
    python inspect_form.py FORM.docx --text       # every item with body text
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ey_fr_75 as F


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--boxes", action="store_true", help="only ticked boxes")
    ap.add_argument("--text", action="store_true", help="dump body text per item")
    args = ap.parse_args()

    doc = F.load(args.path)
    items = F.items(doc)
    total = F.count_checkboxes(doc)

    print(f"file      : {os.path.basename(args.path)}")
    print(f"items     : {len(items)}")
    print(f"checkboxes: {total}   (the intact template has 94; fewer means a box was "
          f"destroyed by an earlier edit)")

    ticked = [(n, lab) for n, lab, st in F.checkbox_audit(doc) if st]
    print(f"ticked    : {len(ticked)}")
    print()

    if args.boxes:
        for n, lab in ticked:
            print(f"  [x] {n:9s} {lab}")
        return

    for num, it in items.items():
        boxes = it.checkboxes()
        marks = ""
        if boxes:
            marks = " " + " ".join(
                ("[x]" if st else "[ ]") + (it.cell_texts()[ci][:5] or "")
                for ci, _, st in boxes)
        label = it.label.split("\n")[0]
        print(f"{num:9s} cells={len(it.tcs)}{marks}  {label[:80]}")
        if args.text:
            body = "\n".join(it.label.split("\n")[1:]).strip()
            if body:
                for line in body.split("\n"):
                    print(f"          | {line[:110]}")


if __name__ == "__main__":
    main()
