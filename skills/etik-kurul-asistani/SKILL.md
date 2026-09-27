---
name: etik-kurul-asistani
description: Build a complete Göztepe Prof. Dr. Süleyman Yalçın Şehir Hastanesi Girişimsel Olmayan Klinik Araştırmalar ethics committee dossier — başvuru dilekçesi (EY.FR.74), başvuru formu (EY.FR.75), bütçe formu (EY.FR.76), özgeçmiş formu (EY.FR.77), İKU taahhütnamesi (EY.FR.78), taahhütname, consent form or waiver justification, and the contents list — with blank templates included, tick-box handling, internal-consistency audit and a rendered visual check. Use this whenever the user is preparing, editing, revising or checking an ethics committee application or dossier, a re-application after a rejection, or an amendment — even when they only mention one form, one section or one field. Turkish triggers: etik kurul, etik kurul başvurusu, etik kurul formu, başvuru formu doldur, EY.FR.75, girişimsel olmayan klinik araştırma, etik kurul dosyası, etik kurul revizyonu, amendman, kurul düzeltme istedi, başvuruyu yeniden yaz, dahil edilme kriterleri, GOKAEK, gizlilik bölümü. English triggers: ethics committee application, IRB form, non-interventional research application, ethics form fill, ethics resubmission.
---

# Etik Kurul Asistanı — EY.FR.75

The target document is the Göztepe Prof. Dr. Süleyman Yalçın Şehir Hastanesi
**Girişimsel Olmayan Klinik Araştırmalar Etik Kurul Başvuru Formu**, Dok. Kodu
EY.FR.75, Yayın Tarihi 16.05.2025, Revizyon No 00. An intact copy holds **94 legacy
Word tick boxes** and **125 numbered items** across sections A–H plus a GİZLİLİK block
and the H.1 undertaking.

The form is Turkish and so is everything written into it. Write in the impersonal
academic register the house style requires — "bu araştırmada … değerlendirilecektir",
never "yapacağız" — and run `/banned-words` over any prose before it goes in.

## Why this needs tooling rather than hand-editing

Three properties of this template defeat straightforward python-docx code, and each one
has already produced a corrupted submission on this machine:

- The tick boxes are **form fields**, not characters. Typing ☒ next to one leaves the
  real box still rendering beside it, so the form shows two marks.
- `row.cells[i]` is a **grid** mapping, not the physical cells. The row carries narrow
  spacer columns; writing into one squeezes the answer into a vertical ribbon.
- The label paragraph and the body paragraphs of a cell carry **different properties**.
  Copying the label's onto body text makes the answer come out bold.

`scripts/ey_fr_75.py` handles all three and refuses the operations that break them.
Reach for it rather than writing new python-docx code against this form.

## Workflow

### 1. Start from the blank template

`assets/EY-FR-75_basvuru_formu_bos.docx` is the committee's own blank form: 125 items,
94 tick boxes, none of them ticked. Copy it into the new study's folder and fill that.
Earlier versions of this skill cleared a previous study's copy because no blank existed
on the machine; that is no longer necessary and should not be done — scrubbing another
study out of a form is error-prone and it left leftovers behind every time it was used.

If you ever do have to work from a filled copy, check it first:

```bash
python scripts/inspect_form.py "<candidate>.docx"
```

It must report **94 checkboxes and 125 items**. Fewer means an earlier edit destroyed a
field, and a destroyed box cannot be recreated from python-docx. A file whose name
contains EY.FR.75 but which reports 0 boxes is a flattened reproduction, not the form.
Never edit a previous study's file in place.

### 2. Collect the study facts before writing anything

The form asks for specifics that must not be improvised. Ask the user for whatever is
missing rather than filling plausible values:

design and tense (prospective or retrospective), target sample size and how it was
derived, inclusion criteria, exclusion criteria, primary endpoint, secondary endpoints,
start and end dates, centre, funding, investigator list with titles, and the data
retention plan.

Three of the house red lines bite hardest here:

- **Never invent an approval number, protocol ID or trial registration number.** Leave
  a marked placeholder and say it needs filling.
- **Never invent an N, a prevalence or a power calculation.** If the sample-size logic
  is not supplied, ask for it.
- **No patient identifiers** anywhere in the form, including examples.

### 3. Fill the form

`references/form-haritasi.md` is the item-by-item map: what each numbered field
expects, which ones are conditional on a tick box, and the phrasing this committee has
accepted before. Read it before filling, not after.

```python
import sys; sys.path.insert(0, "scripts")
import ey_fr_75 as F

doc = F.load(path)
F.item(doc, "A.1").set_text("Araştırmanın Türkçe adı")
F.item(doc, "B.2").check(True)                    # single box on the row
F.item(doc, "E.6.1").check(answer="evet")         # evet/hayır row
F.item(doc, "D.1.5").set_text("Amaç…\n\nHipotez…")
F.item(doc, "D.1.7").set_block("dahil edilmeme kriterleri", "• …\n• …")
doc.save(path)
```

Things worth knowing about the API:

- `set_text` picks its target cell by **width**, because two layouts of A.1/A.2 are in
  circulation and a fixed index is right in one and destructive in the other. It
  refuses to write into a spacer column.
- `D.1.7` holds **two** printed fields in one cell — dahil edilme and dahil edilmeme
  kriterleri. `set_text` refuses it; use `set_block` twice. Writing it as one field
  silently deletes the exclusion criteria and nothing looks wrong afterwards.
- `check()` flips the real field state. Never type a tick character.
- C.1.8's box shares its cell with its text, so that row is not writable as text; tick
  it with `check()`.
- `item.value()` returns what the applicant wrote with the printed instruction removed,
  which is how you tell "still empty" from "has an answer".

### 4. Scrub the previous study out

The failure that matters is a term from the old study surviving somewhere the eye does
not go — a header, a comment, document properties, a custom XML island. Checking
`word/document.xml` alone is what let one through before.

```bash
python scripts/scrub_check.py FORM.docx --terms "eski konu,eski yazar,eski tarih"
```

Build the term list from the study you cleared: its topic words, investigator names,
student names, dates, sample sizes, instrument names. The script also sweeps for
identifier-shaped numbers and unfilled placeholders regardless of the list.

### 5. Audit internal consistency

```bash
python scripts/consistency_check.py FORM.docx
```

This catches the contradictions the board sends applications back for: retrospektif and
prospektif both ticked, a conditional field left empty after its gate was ticked, "risk
yok" alongside a ticked risk, single-centre and multi-centre both marked, an empty
exclusion list. Errors block; warnings are judgement calls.

### 6. Render it and look at it

```bash
python scripts/to_pdf.py FORM.docx
```

Then actually read the pages. XML-level checks pass on layouts that are visibly broken,
and every layout failure this form has produced was caught here and nowhere else. This
step is not optional on this form.

### 7. Hand back what only the user can complete

H.3 (el yazısıyla adı soyadı), H.4 (tarih) and H.5 (imza) are signed by hand. Telephone
numbers of co-investigators and any student name list are usually the user's to fill.
List these explicitly when you hand the file over rather than inventing values.

## The rest of the dossier

**An application is a set, not one form.** The committee's own checklist is
`assets/EY-YD-05_dosya_kontrol_listesi.docx`; build the folder in the order it gives,
and include a contents list saying what each item is and why anything is absent.

Blank templates for the whole set live in `assets/`:

| Belge | Şablon |
|---|---|
| Başvuru dilekçesi | `EY-FR-74_basvuru_dilekcesi_bos.docx` — two alternative letters, page 1 for a scientific study and page 2 for a thesis; delete the one that does not apply |
| Başvuru formu | `EY-FR-75_basvuru_formu_bos.docx` |
| Bütçe formu | `EY-FR-76_butce_formu_bos.docx` |
| Özgeçmiş formu | `EY-FR-77_ozgecmis_formu_bos.docx` |
| İKU-Helsinki taahhütnamesi | `EY-FR-78_iku_taahhutname_bos.docx` |
| Taahhütname | `taahhutname_bos.docx` |
| BGOF içerik yönergesi | `BGOF_icerik_yonergesi.docx` — guidance, not a fillable form |

Two things about these differ from EY.FR.75 and will catch you out:

- **The budget form's tick boxes are modern content controls (`w:sdt`), not the legacy
  fields EY.FR.75 uses.** Ticking one means setting `w14:checked` *and* swapping the
  displayed character (U+2610 unchecked, U+2612 checked); changing only one leaves Word
  showing a box that disagrees with its own state. Their cell also sits inside the
  `w:sdt`, so `row._tr.findall(w:tc)` does not see it and the row looks short a column.
- A retrospective record study with a consent waiver has no BGOF. Do not leave the slot
  empty and do not invent a consent form: write a **muafiyet gerekçesi** in its place
  covering why consent cannot be obtained, why a consent-limited cohort would not answer
  the question, and what protects the volunteers instead.

Personal history — date of birth, education, employment, GCP certificates — is never
invented for the CV form. Leave marked placeholders and list them when handing over.

## References

- `references/form-haritasi.md` — item-by-item map of sections A–H, which fields are
  conditional, and what this committee expects in each.
- `references/kurul-tercihleri.md` — decisions this board has made before: the
  prospective-tense rule for re-applications, the GİZLİLİK block, retention period,
  how deviations from an approved protocol are handled.
