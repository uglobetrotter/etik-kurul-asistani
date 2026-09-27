# Kurulun ve kullanıcının daha önce verdiği kararlar

Bu dosya, Göztepe Girişimsel Olmayan Klinik Araştırmalar Etik Kurulu ile yürütülen
başvurularda ortaya çıkmış ve tekrar eden durumları toplar. Her madde belirli bir
başvurudan gelir ve tarihi yazılıdır; yeni bir başvuruda körlemesine uygulanmaz,
duruma uyup uymadığı kullanıcıya sorulur.

## Onaylanmış bir protokolden sapıldığında (2026-08-18)

Kurul, daha önce onayladığı bir çalışma için uygulanan protokoldeki sapmaların
amendman ile karşılanamayacak kadar büyük olduğuna karar verdiğinde **sıfırdan yeni
bir EY.FR.75 başvurusu** istemiştir. Sapma listesi büyükse amendman önermeden önce
kurulun yeni başvuru isteyip istemediğini teyit ettir.

Kurulun bu durumda istediği biçim:

- Çalışma **prospektif düzlemde**, yani planlama kipinde yazılır. Veri toplama bitmiş
  olsa bile form gelecek zamanlı kalır.
- Forma **hiçbir sonuç girilmez**. Hasta sayısı gerçekleşen sayı olarak değil, hedef
  örneklem olarak yazılır; asgari örneklem gerekçesiyle birlikte verilir. Bulgular,
  oranlar ve etki büyüklükleri forma alınmaz.
- Kullanıcının 2026-08-18 kararı: form **önceki karara hiç atıf yapmaz**, tamamen
  bağımsız yeni bir başvuru olarak sunulur. Bu bir tercihtir, kural değildir; yeni
  başvuruda kullanıcıya yeniden sorulmalıdır.
- E.7 tarihleri, veri toplama geçmişte tamamlanmış olsa bile gerçek tarihler olarak
  yazılmıştır (2026-08-18 kullanıcı kararı).

Yeni başvuruya, onaylı protokolden gerçekten sapılan her nokta işlenir: dahil etme
ölçütünün tanımı, dışlama ölçütleri listesi, uygulanan kurallar, bildirim eşikleri,
istatistiksel tahmin yöntemi, yazılım sürümü ve raporlama standardı. Onaylı formda yer
alıp izlenmemiş bir sonlanım varsa forma alınmaz; izlenmediği kullanıcıya teyit
ettirilir.

## Boş şablonlar (2026-08-20'den beri elimizde)

Kullanıcı 2026-08-20'de kurulun resmi form setini verdi; hepsi `assets/` altındadır.
**Başvuru formu artık boş şablondan doldurulur.** Daha önce, makinede boş şablon
bulunmadığı için dolu bir kopya temizlenerek kullanılıyordu; bu yöntem her seferinde
arkasında kalıntı bıraktı — bir başvuruda E.2.4 ve E.2.5 etiketlerine önceki
çalışmanın parantezleri, F.2.2'nin altına "→ [X] EVET" satırı ve künyede başka bir
yazarın adı kalmıştı. Artık gerekmiyor, yapılmamalı.

Yine de dolu bir kopyadan çalışmak zorunda kalınırsa, önceki çalışmanın terimlerini —
konu, tarihler, örneklem sayıları, araştırmacı ve öğrenci adları, ölçek adları —
**tüm XML parçalarında** taramak gerekir; yalnız `word/document.xml` yetmez.
`scripts/scrub_check.py` bunu yapar ve docProps künyesini de denetler.

## Gizlilik ve saklama

Retrospektif çalışmalarda GİZLİLİK bölümü zorunludur. Saklama süresi **İKU gereği en az
15 yıl** yazılır. Hücredeki şablon yönergesi ile "Sorumlu Araştırmacı / İmza" bloğu
silinmez.

## Öğrenci ve yardımcı araştırmacı adları

Gözlemci öğrencilerin adları forma yazılabilir; şablonda yer yoksa G.3 tablosuna yeni
satır eklenir (bir başvuruda G.3.5 satırı bu amaçla eklenmiştir). Adlar `[AD SOYAD]`
yer tutucusu olarak bırakılıp kullanıcı tarafından doldurulur. G.3.4 telefon
numaraları, H.4 tarih ve H.5 imza da kullanıcıya bırakılır.

## Doğrulama

Bu formda XML denetimi yetmez. `win32com` ile Word'de açıp PDF'e çevirip sayfaları
gözle görmek, XML'in yakalayamadığı yerleşim bozukluklarını anında göstermiştir ve bu
formda yaşanan her yerleşim hatası yalnız burada yakalanmıştır. Zorunlu adımdır.

Üstbilgideki "Sayfa No: x/7" sabittir; belge 10 sayfa olsa da "/7" yazar. Bu şablon
kaynaklıdır, düzeltilmez.
