# EY.FR.75 madde haritası

Göztepe Prof. Dr. Süleyman Yalçın Şehir Hastanesi, Girişimsel Olmayan Klinik
Araştırmalar Etik Kurul Başvuru Formu. Dok. Kodu EY.FR.75, Yayın Tarihi 16.05.2025,
Revizyon No 00. Sağlam bir kopyada **125 numaralı madde** ve **94 form kutusu** bulunur.

Yapı: 11 üst düzey tablo ve E.1 risk listesinin oluşturduğu bir iç içe tablo. E.1,
`doc.tables` ile görünmez; risk listesine ulaşmak için hücre içindeki tabloya inmek
gerekir. `scripts/ey_fr_75.py` bunu zaten yapar.

## Şablonun kendi içindeki bozuk çapraz göndermeler

Formun basılı metni, numaralandırma değiştiğinde güncellenmemiş. Aşağıdaki maddeler
artık var olmayan madde numaralarına gönderme yapar; doğru koşul sağdaki maddedir.
Kurula giden metinde bu göndermeler olduğu gibi bırakılır, düzeltilmez.

| Basılı metinde yazan | Gerçek koşul maddesi |
|---|---|
| D.1.4 — "D.1.2'ye cevabınız evet ise" | D.1.3 (nadir hastalık) |
| F.1.3 — "E.1.1'e cevabınız evet ise" | F.1.2 (18 yaş altı) |
| F.1.5 — "E.1.2'ye cevabınız evet ise" | F.1.4 (18 yaş üstü) |
| F.3.17 — "E.3.3.6'ya cevabınız evet ise" | F.3.10 / F.3.16 (hassas popülasyon, şahsen olur veremeyenler) |
| E.6.5 — "D.10.3'e cevabınız evet ise" | E.6.4 (başka ülkelerde de yürütülüyor mu) |

## A. Araştırma bilgileri

| Madde | İçerik |
|---|---|
| A.1 | Araştırmanın açık Türkçe adı. Tasarımı ad içinde belirtmek kurulun okumasını kolaylaştırır. |
| A.2 | Çalışmanın İngilizce adı. Makale hedefi varsa makale başlığıyla aynı tutulur. |

A.1/A.2 satırının iki farklı yerleşimi dolaşımdadır: bazı kopyalarda etiket ile değer
aynı hücrededir ve üçüncü hücre 0,5 cm'lik boş sütundur; bazılarında etiket 1., değer
2. hücrededir. Sabit hücre numarası kullanma — kütüphane genişliğe göre seçer.

## B. Araştırmanın özellikleri

| Madde | İçerik |
|---|---|
| B.1 / B.2 | Retrospektif / Prospektif. **Yalnızca biri işaretlenir.** Dolaşımdaki bir kopyada ikisi birden işaretli; denetleyici bunu yakalar. |
| B.3.1 | Yüksek lisans / doktora / uzmanlık tezi. İşaretlenirse B.3.2 zorunlu. |
| B.3.2 | Tez sahibinin adı soyadı. |
| B.3.3 | Bireysel araştırma projesi. Şablonda öntanımlı işaretli gelir. |
| B.3.4 | Diğer. Öğrenci katılımlı staj projeleri burada tanımlanır. |

## C. Destekleyici

C.1 "Evet" ise C.1.3–C.1.7 arasından en az biri belirtilmelidir. Destek yoksa C.1
"Hayır" işaretlenir ve **C.1.8 işaretlenir** — aksi hâlde giderin kaynağı formda
boşta kalır. C.1.8'in kutusu metniyle aynı hücrededir: o hücre metin olarak yeniden
yazılırsa kutu yok olur, `check()` ile işaretlenir.

## D. Araştırmaya ilişkin genel bilgiler

| Madde | İçerik |
|---|---|
| D.1.1 | Araştırmanın konusu. Literatür bilgisi ve referanslar **metin içinde** verilir; ayrı kaynakça bölümü yoktur. |
| D.1.2 | Literatüre katacağı yenilikler. Mevcut bilgiye katkının hangi açıdan olduğu. |
| D.1.3 | Nadir hastalık mı? Evet ise D.1.4 zorunlu. |
| D.1.5 | Amaç ve hedefler; araştırma soruları ve hipotez. |
| D.1.6 | Uygulanacak yaklaşım ve yöntemler, 5N1K ölçütleri gözetilerek. Veri kaynağı, ölçüm, körleme, istatistiksel analiz planı ve örneklem gerekçesi buraya yazılır. |
| D.1.7 | **Tek hücrede iki alan:** dahil edilme kriterleri ve dahil edilmeme kriterleri. Tam genişlikte bir satırdır ve madde numarası kendi paragrafındadır. `set_text` reddeder; `set_block` ile ayrı ayrı yazılır. |
| D.2.1 | Primer sonlanım noktası. Ölçüm zamanı ve birimi ile birlikte. |
| D.2.2 | Sekonder sonlanım noktaları. |

D.1.5, D.1.6 ve D.2.1 uzun serbest metin alanlarıdır; önceki başvurucunun koyu alt
başlıkları şablon yapısı değildir, yeniden doldururken tümü değişir.

## E. Araştırmanın riskleri ve yararları

**E.1 (iç içe tablo).** E.1.1–E.1.8 risk listesi, E.1.9 "Risk yok". E.1.9 ile diğerleri
birlikte işaretlenemez; ikisinden de hiçbiri işaretli değilse form eksiktir. Dosya
taraması ve kayıt çalışmalarında olağan seçim **E.1.7 (özel kayıtların kullanımı)**.
E.1.8 işaretlenirse risk tanımlanmalıdır.

**E.2 kapsam.** E.2.2 Teşhis, E.2.3 Tedavi, E.2.4 Güvenilirlik, E.2.5 Etkililik,
E.2.6 Diğer. Sağlık hizmeti sunum modeli ve prognoz çalışmaları E.2.6'ya yazılır.

**E.3 tür.** E.3.1–E.3.4 cerrahi yöntem, kök hücre, doku ve organ nakli içindir.
Girişimsel olmayan çalışmalarda dördü de boş bırakılır ve tasarım **E.3.5 Diğer**
alanına yazılır ("Retrospektif gözlemsel kohort çalışması" gibi).

**E.4 nitelik.** E.4.1 Tanımlayıcı, E.4.2 Analitik, E.4.3 Deneysel. Girişimsel olmayan
kurulda E.4.3 kapsam dışına düşme riski taşır; kasıtlı değilse işaretlenmez.

**E.5 tasarım.** E.5.1 Kontrollü, E.5.3 Randomize, E.5.4 Açık etiketli, E.5.5 Tek kör,
E.5.6 Çift kör, E.5.7 Çift sağır, E.5.8 Paralel grup, E.5.9 Çapraz — hepsi Evet/Hayır.
Gözlemsel çalışmalarda tümü "Hayır" işaretlenir ve tasarım E.5.10 Diğer alanında
açıklanır. E.5.1 "Evet" ise E.5.2 karşılaştırma ürünü zorunludur.

**E.6 merkez.** E.6.1 tek merkez / E.6.2 çok merkez — biri Evet, diğeri Hayır. E.6.3'e
merkez sayısı ve adı yazılır: "Göztepe Prof. Dr. Süleyman Yalçın Şehir Hastanesi Acil
Servisi (Tek merkez)." E.6.4 Hayır ise E.6.5'e "Uygulanamaz" yazmak kurulun boş alan
sorusunu önler.

**E.7 süre.** E.7.1 başlangıç, E.7.2 bitiş; gün / ay / yıl ayrı hücrelerde. Başlangıç
için şablon "etik kurul onay tarihinden sonra" notunu taşır.

## F. Gönüllüler

| Madde | İçerik |
|---|---|
| F.1.2 / F.1.4 | 18 yaş altı / 18 yaş üstü, Evet-Hayır. İşaretlenen için F.1.3 veya F.1.5'te yaş aralığı **ve öngörülen gönüllü sayısı** verilir. |
| F.2.1 / F.2.2 | Kadın / Erkek. İkisi de dahilse ikisi de işaretlenir. |
| F.3.1–F.3.16 | Gönüllü grubu, her biri Evet/Hayır. Hasta popülasyonu için F.3.9 "Hastalar" Evet ve etiketin yanına popülasyon tanımı yazılır. |
| F.3.10 | Özel hassas popülasyonlar. Evet ise F.3.17'de açıklanır. |
| F.3.15 | Acil vakalar. Acil servis çalışmalarında Evet. |
| F.3.16 | Şahsen olur veremeyecek gönüllüler. Bilinci kapalı / şok tablosundaki hastalar dahilse Evet, gerekçesi F.3.17'ye. |
| F.3.18 | Kontrol grubu sağlıklı gönüllülerden seçilecekse hangi popülasyondan seçileceği. |

Şablon F.1.4, F.3.9, F.3.15 ve F.3.16'yı öntanımlı işaretli getirir; çalışmaya
uymuyorsa açıkça kaldırılmalıdır.

## G. Araştırmacılar

G.1 koordinatör ve tek merkezli çalışmalarda sorumlu araştırmacı, G.2 sorumlu
araştırmacı, G.3 yardımcı araştırmacı. Her blokta adı soyadı, unvanı, uzmanlık alanı,
kurumu, telefon ve e-posta alanları vardır (G.3'te telefon G.3.4).

Etiketi silip yerine yalnızca değeri yazma — dolaşımdaki iki kopya bunu yapmış ve form
boş şablonla karşılaştırıldığında okunması zorlaşmış. Doğrusu "Adı Soyadı: Uğur Durmuş"
biçimi; kütüphane `keep_label=True` ile bunu korur.

Yardımcı araştırmacı sayısı şablondaki satırları aşıyorsa G.3 tablosuna yeni satır
eklenir; adlar yer tutucu olarak bırakılıp kullanıcıya doldurtulur. Her araştırmacı
için ayrı özgeçmiş ve taahhütname formu dosyaya eklenir.

## GİZLİLİK

Retrospektif çalışmalarda doldurulması zorunludur. Kişisel, tıbbi, sosyal ve demografik
verilerin nasıl korunacağı, anonimleştirmenin nasıl yapılacağı ve saklama süresi
yazılır. Saklama süresi **İKU gereği en az 15 yıl** olarak belirtilir. Hücrede şablonun
kendi yönerge paragrafı ile "Sorumlu Araştırmacı / İmza" bloğu bulunur; ikisi de
silinmez.

## H. Taahhüt

H.1 taahhüt metni ve H.2 başvuru sahibi alanı formda basılıdır. **H.3 el yazısıyla adı
soyadı, H.4 tarih ve H.5 imza elle doldurulur** — bu üçü hiçbir zaman programla
doldurulmaz, kullanıcıya bırakılır.

## Üstbilgi

Üstbilgideki "Sayfa No: x/7" ifadesindeki 7 sabittir. İçerik uzayınca belge 10–15 sayfa
olsa da "/7" yazmayı sürdürür; bu şablon kaynaklıdır, hata değildir.
