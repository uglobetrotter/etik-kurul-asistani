"""Check an EY.FR.75 copy for the internal contradictions the board sends back.

The form encodes the same fact in several places, and nothing in Word stops the two
copies from disagreeing. A real filled copy on this machine has both B.1 (Retrospektif)
and B.2 (Prospektif) ticked. Rules here are the ones the form's own wording implies:
a conditional field that must be filled once its gate is ticked, a pair that cannot
both be true, a section that becomes mandatory for a given design.

    python consistency_check.py FORM.docx

Exit code 1 if any ERROR is raised. WARNs are judgement calls, not blockers.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ey_fr_75 as F

problems = []


def err(item, msg):
    problems.append(("ERROR", item, msg))


def warn(item, msg):
    problems.append(("WARN", item, msg))


def ticked(items, num, answer=None):
    """True if the box is set. answer='evet'/'hayir' selects the column."""
    it = items.get(num.rstrip('.'))
    if it is None:
        return None
    boxes = it.checkboxes()
    if not boxes:
        return None
    if answer is None:
        return any(st for _, _, st in boxes)
    want = answer.lower()[0]
    for ci, _, st in boxes:
        lab = it.cell_texts()[ci].lower().strip()
        if lab.startswith(want):
            return st
    return None


def body(items, num):
    """What the applicant wrote on the row, instruction text removed."""
    it = items.get(num.rstrip('.'))
    return it.value() if it is not None else ""


def check(path):
    doc = F.load(path)
    items = F.items(doc)

    n_boxes = F.count_checkboxes(doc)
    if n_boxes != 94:
        warn("form", f"{n_boxes} form kutusu var, saglam sablonda 94; "
                     f"bir kutu onceki duzenlemede yok edilmis olabilir")

    # --- B: design ------------------------------------------------------
    retro, pro = ticked(items, "B.1"), ticked(items, "B.2")
    if retro and pro:
        err("B.1/B.2", "Retrospektif ve Prospektif birlikte isaretli; yalnizca biri olmali")
    if not retro and not pro:
        err("B.1/B.2", "Ne retrospektif ne prospektif isaretli")

    if ticked(items, "B.3.1") and not body(items, "B.3.2"):
        err("B.3.2", "Tez isaretli ama tez sahibinin adi soyadi bos")
    if body(items, "B.3.4") and not ticked(items, "B.3.4"):
        warn("B.3.4", "'Diger' aciklamasi yazilmis ama kutusu isaretli degil")

    # --- C: funding -----------------------------------------------------
    sponsor = ticked(items, "C.1", answer="evet")
    named = any(ticked(items, k) for k in ("C.1.3", "C.1.4", "C.1.5")) \
        or bool(body(items, "C.1.6")) or bool(body(items, "C.1.7"))
    self_funded = ticked(items, "C.1.8")
    if sponsor and not named:
        err("C.1", "Destekleyici 'Evet' ama C.1.3-C.1.7 arasinda hicbiri belirtilmemis")
    if sponsor is False and named:
        err("C.1", "Destekleyici 'Hayir' ama bir destekleyici belirtilmis")
    if not sponsor and not self_funded:
        warn("C.1.8", "Destekleyici yok ve 'Arastirmacilar tarafindan karsilanacaktir' "
                      "isaretli degil; giderin kaynagi belirsiz kaliyor")

    # --- D: subject and endpoints ---------------------------------------
    for num, name in (("D.1.1", "Arastirmanin konusu"),
                      ("D.1.2", "Literature katacagi yenilikler"),
                      ("D.1.5", "Amac ve hedefler"),
                      ("D.1.6", "Yaklasim ve yontemler"),
                      ("D.2.1", "Primer sonlanim")):
        if not body(items, num):
            err(num, f"{name} bos")

    # D.1.7 is two fields in one cell; an empty exclusion list is invisible to a
    # whole-cell emptiness test because the inclusion list fills the same cell.
    d17 = items.get("D.1.7")
    if d17 is not None:
        heads = d17.headings()
        paras = [p.text.strip() for p in
                 F._tc_paragraphs(d17.tcs[d17.target_cell()], d17.table)]
        for idx, (start, head) in enumerate(heads):
            end = heads[idx + 1][0] if idx + 1 < len(heads) else len(paras)
            if not any(paras[start + 1:end]):
                err("D.1.7", f"bos: {head.split('(')[0].strip()}")
        if not heads:
            err("D.1.7", "Dahil edilme / edilmeme kriterleri basliklari bulunamadi")

    if ticked(items, "D.1.3", answer="evet") and not body(items, "D.1.4"):
        err("D.1.4", "Nadir hastalik 'Evet' ama aciklama bos")

    # --- E: risks, scope, design ----------------------------------------
    risks = [k for k in [f"E.1.{i}" for i in range(1, 9)] if ticked(items, k)]
    if ticked(items, "E.1.9") and risks:
        err("E.1.9", f"'Risk yok' isaretli ama {', '.join(risks)} de isaretli")
    if not ticked(items, "E.1.9") and not risks:
        err("E.1", "Hicbir risk ve 'Risk yok' da isaretli degil")
    if ticked(items, "E.1.8") and not body(items, "E.1.8"):
        warn("E.1.8", "'Diger riskler' isaretli ama tanimlanmamis")

    if not any(ticked(items, k) for k in ("E.2.2", "E.2.3", "E.2.4", "E.2.5")) \
            and not body(items, "E.2.6"):
        err("E.2", "Arastirmanin kapsami hic isaretlenmemis ve 'Diger' de bos")

    if not any(ticked(items, k) for k in ("E.3.1", "E.3.2", "E.3.3", "E.3.4")) \
            and not body(items, "E.3.5"):
        err("E.3", "Arastirmanin turu bos; girisimsel olmayan calismalarda E.3.5 "
                   "'Diger' alanina tasarim yazilir")

    if not any(ticked(items, k) for k in ("E.4.1", "E.4.2", "E.4.3")) \
            and not body(items, "E.4.4"):
        err("E.4", "Arastirmanin niteligi isaretlenmemis")
    if ticked(items, "E.4.3"):
        warn("E.4.3", "'Deneysel' isaretli; girisimsel olmayan etik kurulun kapsami disinda "
                      "gorunebilir, kasitli degilse kaldir")

    if ticked(items, "E.5.1", answer="evet") and not body(items, "E.5.2"):
        err("E.5.2", "Kontrollu 'Evet' ama karsilastirma urunu belirtilmemis")

    single = ticked(items, "E.6.1", answer="evet")
    multi = ticked(items, "E.6.2", answer="evet")
    if single and multi:
        err("E.6", "Tek merkez ve cok merkez birlikte 'Evet'")
    if not single and not multi:
        err("E.6", "Merkez sayisi isaretlenmemis")
    if not body(items, "E.6.3"):
        err("E.6.3", "Merkez sayisi ve isimleri bos")
    if ticked(items, "E.6.4", answer="evet") and not body(items, "E.6.5"):
        err("E.6.5", "Baska ulkelerde de yurutuluyor 'Evet' ama merkez sayisi bos")

    for num in ("E.7.1", "E.7.2"):
        cells = items[num].cell_texts() if num in items else []
        date_cells = [c for c in cells[2:] if c.strip().strip("_")]
        if not date_cells:
            err(num, "Tarih alanlari bos (gun/ay/yil)")

    # --- F: population --------------------------------------------------
    under18 = ticked(items, "F.1.2", answer="evet")
    over18 = ticked(items, "F.1.4", answer="evet")
    if not under18 and not over18:
        err("F.1", "Yas araligi isaretlenmemis")
    if under18 and not body(items, "F.1.3"):
        err("F.1.3", "18 yas alti 'Evet' ama yas araligi ve gonullu sayisi bos")
    if over18 and not body(items, "F.1.5"):
        err("F.1.5", "18 yas ustu 'Evet' ama yas araligi ve gonullu sayisi bos")

    if not ticked(items, "F.2.1") and not ticked(items, "F.2.2"):
        err("F.2", "Cinsiyet isaretlenmemis")

    if ticked(items, "F.3.10", answer="evet") and not body(items, "F.3.17"):
        warn("F.3.17", "Ozel hassas populasyon 'Evet' ama F.3.17 aciklamasi bos")
    if ticked(items, "F.3.1", answer="evet") and not body(items, "F.3.18"):
        warn("F.3.18", "Saglikli gonullu 'Evet' ama nereden secilecegi yazilmamis")

    # --- G / H: people and undertaking -----------------------------------
    for num, name in (("G.1.1", "Sorumlu arastirmaci adi"),
                      ("G.1.5", "Telefon"),
                      ("G.1.6", "E-posta")):
        if not body(items, num):
            err(num, f"{name} bos")

    # --- Confidentiality block ------------------------------------------
    gizlilik = ""
    for tbl in doc.tables:
        head = tbl.rows[0].cells[0].text.strip().upper()
        if head.startswith("GİZLİLİK") or head.startswith("GIZLILIK"):
            gizlilik = "\n".join(c.text for r in tbl.rows[1:] for c in r.cells).strip()
    if retro and len(gizlilik) < 120:
        err("GIZLILIK", "Retrospektif calismada gizlilik bolumu zorunlu ve bos/cok kisa")
    if gizlilik and "15" not in gizlilik:
        warn("GIZLILIK", "Saklama suresi gorunmuyor; IKU geregi en az 15 yil yazilir")

    return problems


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    path = sys.argv[1]
    found = check(path)
    print(f"file: {os.path.basename(path)}")
    errs = [p for p in found if p[0] == "ERROR"]
    warns = [p for p in found if p[0] == "WARN"]
    for level, item, msg in found:
        print(f"[{level:5s}] {item:10s} {msg}")
    print(f"\n{len(errs)} hata, {len(warns)} uyari")
    if errs:
        sys.exit(1)


if __name__ == "__main__":
    main()
