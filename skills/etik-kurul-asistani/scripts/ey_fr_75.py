"""EY.FR.75 (Girisimsel Olmayan Klinik Arastirmalar Etik Kurul Basvuru Formu) helper.

Addresses every field by its printed item number (A.1, D.1.5, F.3.15, ...) rather than
by table/row index, because the item numbers are stable across the filled copies that
circulate on this machine while row indices are not.

Three things in this template break naive python-docx code; each has a guard here:

1. The tick boxes are legacy Word FORMCHECKBOX fields, not typed characters. Their
   state lives in <w:ffData><w:checkBox><w:default w:val="0|1"/>. Typing a checked-box
   character into the label produces a double mark, because the real field still
   renders next to it.
2. row.cells[i] is a *grid* mapping. Merged cells repeat, and this template has narrow
   spacer columns. Writing through row.cells duplicates text into the spacer and blows
   the row up vertically. Everything here goes through the physical <w:tc> elements.
3. Paragraph properties differ between the label paragraph and the body paragraphs of
   the same cell. Copying the label's pPr onto body text bolds the paragraph marks and
   breaks alignment, so body paragraphs are built from a body-side template (usually
   None) instead of from paragraph 0.

Element.iter() descends into nested tables, so anything meaning "this cell only" has to
filter by ancestry. The E.1 risk list is a nested table inside the risks/benefits header
cell and is invisible to doc.tables.
"""

import copy
import re

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.table import Table, _Cell

W_TC = qn('w:tc')
W_TBL = qn('w:tbl')
W_PPR = qn('w:pPr')
W_R = qn('w:r')
W_RPR = qn('w:rPr')
W_VAL = qn('w:val')

ITEM_RE = re.compile(r'^([A-H])\.(\d+)(?:\.(\d+))?\.?$')

# Rows whose printed instruction does not end in a colon and whose answer therefore
# always starts in a new paragraph. Everywhere else the answer follows the colon on the
# same line, so the two cases need different rules for "what did the applicant write".
LONG_TEXT_ITEMS = {"D.1.1", "D.1.2", "D.1.5", "D.1.6", "D.1.7", "D.2.1", "D.2.2"}

# Rows where the template itself prints more than one field into a single cell, so the
# cell must be written one sub-field at a time. Verified against every EY.FR.75 copy on
# this machine: D.1.7 is the only one.
TEMPLATE_MULTI_FIELD_ITEMS = {"D.1.7"}


def _tc_paragraphs(tc, table):
    """Paragraphs belonging to this cell only, excluding any nested table."""
    return [p for p in _Cell(tc, table).paragraphs if p._p.getparent() is tc]


def _tc_text(tc, table):
    return "\n".join(p.text for p in _tc_paragraphs(tc, table)).strip()


def _own_checkboxes(tc):
    """checkBox elements physically inside this cell, nested tables excluded."""
    out = []
    for ff in tc.iter(qn('w:ffData')):
        anc = ff.getparent()
        while anc is not None and anc.tag != W_TC:
            anc = anc.getparent()
        if anc is not tc:
            continue
        cb = ff.find(qn('w:checkBox'))
        if cb is not None:
            out.append(cb)
    return out


def _tc_width(tc):
    """Cell width in twips, or -1 when the cell does not declare one."""
    tcpr = tc.find(qn('w:tcPr'))
    if tcpr is None:
        return -1
    w = tcpr.find(qn('w:tcW'))
    if w is None:
        return -1
    try:
        return int(w.get(qn('w:w')))
    except (TypeError, ValueError):
        return -1


# 700 twips is about 1.2 cm: wide enough for a word, far below any real answer column.
# The spacer columns in this template measure 288-343 twips.
MIN_WRITABLE_TWIPS = 700


def _cb_state(cb):
    ck = cb.find(qn('w:checked'))
    if ck is not None:
        return ck.get(W_VAL, '1') not in ('0', 'false')
    d = cb.find(qn('w:default'))
    if d is not None:
        return d.get(W_VAL, '0') not in ('0', 'false')
    return False


def _cb_set(cb, on):
    val = '1' if on else '0'
    ck = cb.find(qn('w:checked'))
    if ck is not None:
        ck.set(W_VAL, val)
    d = cb.find(qn('w:default'))
    if d is None:
        d = OxmlElement('w:default')
        cb.append(d)
    d.set(W_VAL, val)


def _first_body_rpr(paras, start=1):
    """Run properties the new body text should copy.

    Two subtleties, both of which produced bold answers before they were handled.
    `start` skips the printed instruction, which is bold on full-width rows. And the
    answer is taken from the *first* run of the first non-empty body paragraph even
    when that run carries no rPr at all — returning None there is correct, because it
    means "inherit the style". Scanning forward for the first run that happens to have
    an rPr lands on whatever fragment the previous applicant emphasised mid-sentence.
    """
    for p in paras[start:]:
        if not p.text.strip():
            continue
        runs = p._p.findall(W_R)
        return runs[0].find(W_RPR) if runs else None
    return None


def _answer_rpr(rpr):
    """Run properties for an answer, copied from the surrounding text minus the bold.

    Inheriting formatting keeps the answer looking like the rest of the form — the
    italic of A.1/A.2 comes from the template and is worth keeping. Bold does not:
    on this form it is always either the printed instruction or emphasis the previous
    applicant added to their own answer, and carrying it over makes a whole section
    come out bold. Answers on EY.FR.75 are never bold.
    """
    if rpr is None:
        rpr = OxmlElement('w:rPr')
        sz = OxmlElement('w:sz')
        sz.set(W_VAL, '22')  # template body runs carry only w:sz 22; Normal is already Times
        rpr.append(sz)
        return rpr
    rpr = copy.deepcopy(rpr)
    for tag in ('w:b', 'w:bCs'):
        for el in rpr.findall(qn(tag)):
            rpr.remove(el)
    return rpr


def _append_run(p, text, rpr=None):
    r = OxmlElement('w:r')
    rpr = _answer_rpr(rpr)
    r.append(rpr)
    t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = text
    r.append(t)
    p.append(r)
    return r


def _run_text(r):
    return "".join(t.text or "" for t in r.findall(qn('w:t')))


def _set_run_text(r, text):
    for t in r.findall(qn('w:t')):
        r.remove(t)
    t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = text
    r.append(t)


def _field_kind(p):
    """'checkbox', 'text' or None for the legacy form field in a paragraph.

    The distinction decides everything. A checkBox field must never have its runs
    touched — C.1.8 keeps its box and its label in one cell and the box cannot be
    rebuilt from python-docx. A textInput field is the opposite: it is the slot the
    answer is supposed to go into, and every "Diger ise belirtiniz:" row in an unused
    template has one sitting after the colon.
    """
    for ff in p.iter(qn('w:ffData')):
        if ff.find(qn('w:checkBox')) is not None:
            return 'checkbox'
        if ff.find(qn('w:textInput')) is not None:
            return 'text'
    for r in p.findall(W_R):
        instr = r.find(qn('w:instrText'))
        if instr is not None and 'FORMTEXT' in (instr.text or ''):
            return 'text'
        if instr is not None and 'FORMCHECKBOX' in (instr.text or ''):
            return 'checkbox'
    return None


def _fill_formtext(p, text):
    """Put the answer inside the paragraph's FORMTEXT field, where Word expects it.

    The field's displayed value is whatever sits between the 'separate' and 'end'
    fldChar runs. Replacing that keeps the field intact, so the form still behaves as
    a form; writing beside it would leave the empty field showing next to the answer.
    """
    runs = p.findall(W_R)
    sep = end = None
    for i, r in enumerate(runs):
        fc = r.find(qn('w:fldChar'))
        if fc is None:
            continue
        kind = fc.get(qn('w:fldCharType'))
        if kind == 'separate':
            sep = i
        elif kind == 'end' and end is None:
            end = i
    if end is None:
        return False

    start = sep + 1 if sep is not None else end
    for r in runs[start:end]:
        p.remove(r)

    holder = OxmlElement('w:r')
    rpr = runs[start].find(W_RPR) if (sep is not None and runs[start:end]) else None
    holder.append(_answer_rpr(rpr))
    t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = text if text else "     "
    holder.append(t)
    runs[end].addprevious(holder)
    return True


def _rewrite_after_label(p, text, has_label=True):
    """Replace what follows the label's colon inside a single paragraph."""
    kind = _field_kind(p)
    if kind == 'checkbox':
        raise ValueError("this paragraph carries a Word tick box; editing its runs would "
                         "destroy the field, and it cannot be rebuilt. Use check() if you "
                         "meant to tick it.")
    if kind == 'text' and _fill_formtext(p, text):
        return

    runs = p.findall(W_R)
    cut, keep_upto = 0, -1
    if has_label:
        for i, r in enumerate(runs):
            txt = _run_text(r)
            if ":" in txt:
                _set_run_text(r, txt[:txt.index(":") + 1])
                keep_upto, cut = i, i + 1
                break
        else:
            cut = 0
    if keep_upto < 0:
        cut = 0

    doomed = runs[cut:]
    rpr = None
    for r in doomed:
        if rpr is None:
            rpr = r.find(W_RPR)
        p.remove(r)
    if rpr is None and keep_upto >= 0:
        rpr = runs[keep_upto].find(W_RPR)

    _append_run(p, (" " if keep_upto >= 0 else "") + text, rpr)


def _make_paragraph(text, ppr, fallback_rpr=None):
    p = OxmlElement('w:p')
    if ppr is not None:
        p.append(copy.deepcopy(ppr))
    if text:
        _append_run(p, text, fallback_rpr)
    return p


class Item:
    """One numbered row of the form."""

    def __init__(self, number, table, row, tcs):
        self.number = number
        self.table = table
        self.row = row
        self.tcs = tcs

    def __repr__(self):
        return f"<Item {self.number} cells={len(self.tcs)} boxes={len(self.checkboxes())}>"

    # ---- reading -------------------------------------------------------
    @property
    def label(self):
        return _tc_text(self.tcs[1], self.table) if len(self.tcs) > 1 else ""

    def text(self, cell=1):
        return _tc_text(self.tcs[cell], self.table)

    def cell_texts(self):
        return [_tc_text(tc, self.table) for tc in self.tcs]

    def value(self):
        """What the applicant wrote on this row, with the printed instruction removed.

        Deciding "is this field still empty" cannot be done by asking whether the cell
        has text, because the cell always has text: the instruction is printed in it.
        Two shapes exist in this template and both appear below. Cells holding a tick
        box are skipped, since 'Evet'/'Hayir' is a label, not an answer.
        """
        if len(self.tcs) > 1:
            chunks = [_tc_text(tc, self.table) for tc in self.tcs[1:]
                      if not _own_checkboxes(tc)]
            joined = "\n".join(c for c in chunks if c.strip())
        else:
            joined = "\n".join(_tc_text(self.tcs[0], self.table).split("\n")[1:])

        lines = [l.strip() for l in joined.split("\n") if l.strip()]
        if not lines:
            return ""
        if len(lines) > 1 or self.number in LONG_TEXT_ITEMS:
            return "\n".join(lines[1:]).strip()
        head = lines[0]
        # A lone line still carrying its colon means the answer was never typed; a lone
        # line without one means an earlier edit overwrote the label with the answer.
        return head.split(":", 1)[1].strip() if ":" in head else head

    def checkboxes(self):
        """[(cell_index, checkbox_element, state)] over the physical cells."""
        found = []
        for ci, tc in enumerate(self.tcs):
            for cb in _own_checkboxes(tc):
                found.append((ci, cb, _cb_state(cb)))
        return found

    # ---- writing -------------------------------------------------------
    def widths(self):
        return [_tc_width(tc) for tc in self.tcs]

    def target_cell(self):
        """Index of the cell an answer belongs in: the widest one that is not the item
        number and does not hold a tick box.

        A fixed index is wrong here. Two layouts of A.1/A.2 circulate on this machine:
        [415, 4297, 288] puts label and answer together in cell 1 with cell 2 a 0.5 cm
        spacer, while [343, 1222, 3435] splits label into cell 1 and answer into cell 2.
        Writing to the spacer squeezes the text into a vertical ribbon and blows the row
        up; picking by width is stable across both.
        """
        best, best_w = None, -1
        for ci, tc in enumerate(self.tcs):
            if ci == 0 and len(self.tcs) > 1:
                continue
            if _own_checkboxes(tc):
                continue
            w = _tc_width(tc)
            if w > best_w:
                best, best_w = ci, w
        if best is None:
            raise ValueError(f"{self.number}: no writable cell on this row")
        return best

    def set_text(self, text, cell=None, keep_label=True, force=False):
        """Replace the body of a cell, keeping the printed label line.

        cell defaults to target_cell(); pass an index only when you have checked the
        widths yourself. keep_label matters because several circulating copies
        overwrote 'Adi Soyadi:' with the bare value, which makes the form harder to
        read against the blank template.
        """
        if cell is None:
            cell = self.target_cell()
        width = _tc_width(self.tcs[cell])
        if not force and 0 <= width < MIN_WRITABLE_TWIPS:
            raise ValueError(
                f"{self.number}: cell {cell} is {width} twips wide, a spacer column. "
                f"Widths on this row are {self.widths()}; the answer belongs in cell "
                f"{self.target_cell()}. Pass force=True only if you are sure.")
        tc = self.tcs[cell]
        paras = _tc_paragraphs(tc, self.table)
        if not paras:
            raise ValueError(f"{self.number}: cell {cell} has no paragraph to write into")

        blocks = self.blocks(cell)
        if len(blocks) > 1 and not force:
            names = "; ".join(repr(h[:45]) for _, h in blocks)
            raise ValueError(
                f"{self.number}: this cell holds {len(blocks)} separate fields — {names}. "
                f"Writing the whole cell would delete the others. Use "
                f"set_block('<part of the heading>', text) for each.")

        keep = self._label_paragraphs(cell) if keep_label else 0

        if keep and len(paras) <= keep:
            # Instruction and answer share the last paragraph, which is how the
            # "Diger ise belirtiniz:" rows and the whole of section G are built.
            # Replacing after the colon is what makes refilling a used copy work;
            # appending would leave the previous study's answer sitting in front.
            _rewrite_after_label(paras[-1]._p, text, has_label=self._has_inline_label(cell))
            return

        # A one-line answer on a row whose label carries a FORMTEXT field belongs inside
        # that field, even when the cell has spare paragraphs below it. Otherwise the
        # empty field keeps showing next to the answer.
        if keep and "\n" not in str(text) and _field_kind(paras[keep - 1]._p) == 'text':
            if _fill_formtext(paras[keep - 1]._p, str(text)):
                for p in paras[keep:]:
                    if p.text.strip():
                        p._p.getparent().remove(p._p)
                return

        body_ppr = None
        for p in paras[keep:]:
            if p.text.strip():
                body_ppr = p._p.find(W_PPR)
                break
        fallback_rpr = _first_body_rpr(paras, keep or 1)

        # The template puts an empty paragraph between a block instruction and its
        # answer. Keeping it preserves the printed look of the form.
        if keep and len(paras) > keep and not paras[keep].text.strip():
            keep += 1

        for p in paras[keep:]:
            p._p.getparent().remove(p._p)

        anchor = paras[keep - 1]._p if keep else None
        for line in str(text).split("\n"):
            new_p = _make_paragraph(line, body_ppr, fallback_rpr)
            if anchor is None:
                tc.insert(0, new_p)
            else:
                anchor.addnext(new_p)
            anchor = new_p

    def headings(self, cell=None):
        """[(paragraph_index, heading)] for every bold paragraph ending in a colon.

        Catches both kinds: the instructions the template prints, and the sub-headings
        a previous applicant typed into a free-text field. Only the former are
        structure worth protecting, so `blocks()` filters this down.
        """
        if cell is None:
            cell = self.target_cell()
        found = []
        for i, p in enumerate(_tc_paragraphs(self.tcs[cell], self.table)):
            txt = p.text.strip()
            if not txt.endswith(":"):
                continue
            for r in p._p.findall(W_R):
                rpr = r.find(W_RPR)
                if rpr is not None and rpr.find(qn('w:b')) is not None:
                    found.append((i, txt))
                    break
        return found

    def blocks(self, cell=None):
        """The printed sub-fields of a row that holds more than one.

        D.1.7 carries both 'dahil edilme kriterleri' and 'dahil edilmeme kriterleri'
        in the same full-width cell, one under the other; rewriting the cell as a
        single text area silently deletes the exclusion criteria, and nothing in the
        XML looks wrong afterwards. It is the only row in this template built that way,
        so the check is a lookup rather than a guess — bold sub-headings in D.1.5,
        D.1.6 and D.2.1 are the previous applicant's own prose and are meant to be
        replaced wholesale when the form is refilled.
        """
        if self.number not in TEMPLATE_MULTI_FIELD_ITEMS:
            return []
        return self.headings(cell)

    def set_block(self, heading, text, cell=None):
        """Replace the answer under one heading of a multi-field cell.

        heading is any distinctive part of the printed instruction, matched
        case-insensitively: set_block('dahil edilmeme', '...') for the exclusion list.
        """
        if cell is None:
            cell = self.target_cell()
        paras = _tc_paragraphs(self.tcs[cell], self.table)
        blocks = self.headings(cell)
        if not blocks:
            raise ValueError(f"{self.number}: no headed blocks in cell {cell}; "
                             f"use set_text()")

        needle = heading.casefold()
        # Match on the field name, i.e. what comes before the parenthetical gloss.
        # D.1.7's exclusion heading quotes the inclusion heading inside its own
        # parentheses ("...dahil edilme kriterlerinde sayilan..."), so matching the
        # full string makes the obvious key ambiguous against the wrong field.
        matches = [b for b in blocks if needle in b[1].split("(")[0].casefold()]
        if not matches:
            matches = [b for b in blocks if needle in b[1].casefold()]
        if len(matches) != 1:
            names = "; ".join(repr(h[:60]) for _, h in blocks)
            raise ValueError(f"{self.number}: {heading!r} matched {len(matches)} of "
                             f"the headings — {names}")

        start = matches[0][0]
        following = [i for i, _ in blocks if i > start]
        end = following[0] if following else len(paras)

        body_ppr, fallback_rpr = None, None
        for p in paras[start + 1:end]:
            if p.text.strip():
                body_ppr = p._p.find(W_PPR)
                for r in p._p.findall(W_R):
                    if fallback_rpr is None:
                        fallback_rpr = r.find(W_RPR)
                break

        first = start + 1
        if first < end and not paras[first].text.strip():
            first += 1          # keep the blank line the template prints under a heading

        # ...and the blank ones that separate this answer from the next heading, so the
        # two fields do not end up butted against each other.
        last = end
        while last > first and not paras[last - 1].text.strip():
            last -= 1

        for p in paras[first:last]:
            p._p.getparent().remove(p._p)

        anchor = paras[first - 1]._p
        for line in str(text).split("\n"):
            new_p = _make_paragraph(line, body_ppr, fallback_rpr)
            anchor.addnext(new_p)
            anchor = new_p

    def _label_paragraphs(self, cell):
        """How many leading paragraphs are printed form text rather than an answer.

        A full-width row keeps its item number in its own paragraph above the
        instruction (D.1.7 is the one that matters), so two paragraphs are form text
        there and one everywhere else. Deleting from paragraph 1 in that case wipes
        the instruction and leaves a bare 'D.1.7.' on the page.
        """
        return 2 if len(self.tcs) == 1 and cell == 0 else 1

    def _has_inline_label(self, cell):
        """Whether this cell's own text starts with the printed instruction.

        When the instruction sits in an earlier cell (the [343, 1222, 3435] layout of
        A.1), the target cell is pure answer and any colon inside it belongs to the
        title, not to a label. Treating it as a label would keep half the old title.
        """
        if cell > 1 and len(self.tcs) > 1:
            neighbour = _tc_text(self.tcs[1], self.table).rstrip()
            if neighbour.endswith(":"):
                return False
        return True

    def check(self, value=True, cell=None, answer=None):
        """Set a tick box.

        answer='evet'/'hayir' picks the column on the two-column yes/no rows, which is
        what most of sections E and F use. cell= addresses a physical cell directly.
        With neither, the row must hold exactly one box.
        """
        boxes = self.checkboxes()
        if not boxes:
            raise ValueError(f"{self.number}: no form checkbox in this row")

        if answer is not None:
            labelled = [b for b in boxes
                        if _tc_text(self.tcs[b[0]], self.table).lower().strip()
                        in ("evet", "hayır", "hayir")]
            if len(labelled) != 2:
                raise ValueError(f"{self.number}: not an evet/hayir row "
                                 f"({len(labelled)} labelled boxes)")
            want_yes = answer.lower().startswith("e")
            for ci, cb, _ in labelled:
                is_yes = _tc_text(self.tcs[ci], self.table).lower().startswith("e")
                _cb_set(cb, value if is_yes == want_yes else not value)
            return

        if cell is not None:
            targets = [b for b in boxes if b[0] == cell]
            if not targets:
                raise ValueError(f"{self.number}: no checkbox in cell {cell}")
        elif len(boxes) == 1:
            targets = boxes
        else:
            raise ValueError(f"{self.number}: {len(boxes)} boxes here; pass cell= or answer=")

        for _, cb, _ in targets:
            _cb_set(cb, value)


def _walk_tables(container, parent):
    """Every table under container, nested ones included, in document order."""
    for tbl_el in container.findall(W_TBL):
        table = Table(tbl_el, parent)
        yield table
        for row in table.rows:
            for tc in row._tr.findall(W_TC):
                yield from _walk_tables(tc, table)


def load(path):
    return Document(path)


def items(doc):
    """dict of item number -> Item, in document order. First occurrence wins."""
    out = {}
    for table in _walk_tables(doc.element.body, doc):
        for row in table.rows:
            tcs = row._tr.findall(W_TC)
            if not tcs:
                continue
            first = _tc_text(tcs[0], table).split("\n")[0].strip()
            if ITEM_RE.match(first):
                key = first.rstrip('.')
                out.setdefault(key, Item(key, table, row, tcs))
    return out


def item(doc, number):
    key = number.rstrip('.')
    found = items(doc).get(key)
    if found is None:
        raise KeyError(f"item {number} not found in this document")
    return found


def checkbox_audit(doc):
    """[(item, box_label, state)] for every tick box, for pre-submission review."""
    rows = []
    for num, it in items(doc).items():
        for ci, cb, state in it.checkboxes():
            lab = _tc_text(it.tcs[ci], it.table) or it.label
            rows.append((num, lab.split("\n")[0][:60], state))
    return rows


def count_checkboxes(doc):
    n = 0
    for table in _walk_tables(doc.element.body, doc):
        for row in table.rows:
            for tc in row._tr.findall(W_TC):
                n += len(_own_checkboxes(tc))
    return n
