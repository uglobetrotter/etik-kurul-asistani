# etik-kurul-asistani

Göztepe Prof. Dr. Süleyman Yalçın Şehir Hastanesi Girişimsel Olmayan Klinik Araştırmalar Etik Kurulu başvuru dosyasını hazırlar: dilekçe (EY.FR.74), başvuru formu (EY.FR.75), bütçe (EY.FR.76), özgeçmiş (EY.FR.77), İKU taahhütnamesi (EY.FR.78), taahhütname, onam ya da feragat gerekçesi ve içerik listesi. Claude skill'i; macOS ve Windows'ta kurulur.

> Bu repo **gizli** tutulmalıdır.

## İçindekiler

- `skills/etik-kurul-asistani/SKILL.md`: skill'in kendisi.
- `assets/`: boş form şablonları (DOCX). Hastanenin belgeleridir.
- `scripts/ey_fr_75.py`: formu madde numarasıyla (A.1, D.1.5 …) dolduran yardımcı; eski Word
  onay kutularını ve birleşik hücreleri doğru ele alır.
- `scripts/inspect_form.py`, `consistency_check.py`, `scrub_check.py`: form haritası,
  iç tutarlılık denetimi ve önceki çalışmadan kalıntı taraması.
- `scripts/to_pdf.py`: formu Word üzerinden PDF'e çevirip görsel kontrol sağlar.

Betikler `python-docx` ister: `pip install -r requirements.txt`.

> **Platform notu:** `to_pdf.py` Word ister. Windows'ta Word'ü COM üzerinden
> (`pip install pywin32`), macOS'ta Microsoft Word for Mac'i AppleScript (`osascript`)
> üzerinden çağırır. macOS'ta ilk çalıştırmada iki izin istenebilir: Terminal'in Word'ü
> denetlemesi (Sistem Ayarları → Gizlilik ve Güvenlik → Otomasyon) ve Word'ün dosyaya
> erişimi. Word yoksa betik açık bir mesajla durur; PDF'i Word'de elle üretin.

## Kurulum

| Platform | Skill klasörü |
|---|---|
| macOS | `~/.claude/skills/etik-kurul-asistani` |
| Windows | `%USERPROFILE%\.claude\skills\etik-kurul-asistani` |

### A. Claude Code plugin

```
/plugin marketplace add uglobetrotter/etik-kurul-asistani
/plugin install etik-kurul-asistani@etik-kurul-asistani
```

Repo gizli olduğu için makinenin GitHub'a git ile erişebilmesi gerekir
(`gh auth login` ya da Git Credential Manager). Skill plugin içinde
`etik-kurul-asistani:etik-kurul-asistani` adıyla görünür. `~/.claude/skills/etik-kurul-asistani` zaten varsa ikisini
birden kurmayın.

### B. Klonla ve bağla

**macOS:**

```bash
git clone https://github.com/uglobetrotter/etik-kurul-asistani.git
cd etik-kurul-asistani
./scripts/install.sh            # sembolik bağ; git pull ile güncellenir
```

**Windows:**

```powershell
git clone https://github.com/uglobetrotter/etik-kurul-asistani.git
cd etik-kurul-asistani
.\install.cmd                   # ya da dosyaya çift tıklayın
```

Windows'ta dizin bağlantısı (junction) kullanılır; yönetici izni gerekmez.
Seçenekler: `--copy` / `-Copy` bağımsız kopya, `--uninstall` / `-Uninstall` kaldırır.
Hedefte gerçek bir klasör varsa silinmez, `.bak-<tarih>` adıyla yedeklenir.

### C. claude.ai ve Claude Desktop

`.skill` paketini Releases'tan indirin ya da üretin (`./scripts/build-skill.sh`,
Windows'ta `powershell -ExecutionPolicy Bypass -File scripts\build-skill.ps1`),
sonra Settings → Capabilities → Skills bölümünden yükleyin.

## Sürüm

Plugin sürümü `1.0.0`. Kaynak: `skills-export-2026-09-08.zip`
(`~/.claude/skills` deposu, `2271084`); skill dosyaları değiştirilmeden alındı.
8 Eylül'den sonra yerelde değiştirdiysen bu kopya geride kalır.

Yeni sürüm: `.claude-plugin/plugin.json` içindeki `version` alanını artırıp `main`'e
gönderin; sonra GitHub'da Actions → CI → Run workflow, dal `main`, `release_tag`
alanına `v<sürüm>`. Testler üç sistemde geçmeden, etiket `plugin.json` ile
eşleşmeden ya da etiket zaten varsa yayımlanmaz.

## Satır sonları

Metin dosyaları LF, `.ps1` ve `.cmd` CRLF; PDF ve DOCX ikili. PowerShell betikleri
UTF-8 BOM ile kaydedilmiştir; Windows PowerShell 5.1 Türkçe karakterleri ancak böyle
bozmadan okur.
