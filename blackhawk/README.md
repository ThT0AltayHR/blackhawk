# BLACKHAWK v1.0.0

**Yetkili kamu kaynakları için etik Türkçe OSINT izleme, olay notlandırma ve kanıt raporlama terminali.**

[![PyPI](https://img.shields.io/pypi/v/blackhawk?color=9b2430)](https://pypi.org/project/blackhawk/)
[![Python](https://img.shields.io/pypi/pyversions/blackhawk)](https://pypi.org/project/blackhawk/)
[![License](https://img.shields.io/badge/license-MIT-5b6470)](LICENSE)

![BlackHawk terminal arayüzü](https://raw.githubusercontent.com/ThT0AltayHR/blackhawk/main/blackhawk/assets/blackhawk-terminal.png)

BlackHawk, operatörün açıkça yetkilendirdiği HTTP/HTTPS kaynaklarından sınırlı,
kaynaklı gözlemler alır; gözlemleri zaman, URL, güven sınıfı ve audit log ile
raporlar. Aracın amacı istihbarat görüntüsü vermek değil, **kanıt zincirini
okunabilir ve denetlenebilir tutmaktır**. Kaynak bulunmadığında veri uydurmaz.

## Öne çıkan yetenekler

- Türkçe, koyu siyah-kırmızı, klavye odaklı Textual TUI.
- Textual bulunmayan Termux/minimal Python ortamları için ANSI fallback arayüz.
- İlk çalıştırmada üç aşamalı operatör sözleşmesi ve etik kullanım kapısı.
- En az 20 karakter, yalnızca büyük harf/rakam içeren oturum tokeni doğrulaması.
- Token ve profil parolası için yalnızca SHA-256 parmak izi; ham gizli değer kaydedilmez.
- Operatör adı, yaş ve isteğe bağlı cinsiyeti kaynak raporuna yansıtan şifreli yerel profil kasası.
- Yetkili tekli hedef, çoklu hedef, canlı gözlem, kaynak/hashtag düzenleme,
  zaman çizelgesi, ilişki özeti, kanıt ve ajan durum ekranları.
- Olay Analizi: kullanıcının verdiği anlatımı yerel olarak anahtar kelime,
  aciliyet sinyali ve gerekli kanıt başlıklarına ayırır. Bu bir soruşturma motoru,
  kolluk veri tabanı veya suç isnadı sistemi değildir.
- HTML, JSON, TXT ve bağımlılıksız PDF raporları.
- URL kullanıcı adı/parolası ve URL içine yerleştirilmiş token/secret reddi.
- Rapor yollarında path traversal önleme, HTML escape ve kaynak/zaman görünürlüğü.
- Demo modu yoktur. Sahte hedef, sahte bulgu ve sahte doğrulama üretilmez.

## Kurulum

```bash
python -m pip install --upgrade blackhawk
blackhawk
```

Termux:

```bash
pkg update
pkg install python
python -m pip install --upgrade pip blackhawk
blackhawk
```

Kurulumun ardından ilk açılışta:

1. Her sözleşme ekranında `EVET` yazıp Enter'a basın.
2. En az 20 karakterli, yalnızca `A-Z` ve `0-9` karakterlerinden oluşan
   bir oturum tokeni girin.
3. Operatör adınızı rapor kimliği için girin.
4. Profil kasası için en az 8 karakterli; en az bir büyük harf ve bir rakam
   içeren yeni bir parola belirleyin ve tekrar doğrulayın.

Profil parolasını e-Devlet, MHRS, banka veya sosyal medya parolanızla aynı
seçmeyin. Parola terminalde yıldızlarla da gösterilmez. Yerel ayarlar
`~/.blackhawk/` altında, profil verisi `lock.file.zip` içinde şifreli yük olarak
ve parola özeti `scaret.txt` içinde SHA-256 olarak tutulur. Tokenin kendisi
saklanmaz; yalnızca `session-token.sha256` parmak izi oluşturulur.

## Kullanım

```bash
blackhawk --version
blackhawk
blackhawk --target https://example.org --duration 60 --reports reports
```

Ana menüde `↑/↓` ile hareket edin, `Enter` ile modül açın, `r` ile kaynak
gözlemi başlatın, `h` ile kapsamlı yardımı açın, `Esc` ile geri dönün ve `q`
ile çıkın. Her modül kendi ekranında `BAŞLAT` ve `GERİ` akışına sahiptir.

`reports/` içinde hedef adıyla dört çıktı oluşur:

- `.json`: makine tarafından işlenebilir oturum ve gözlem verisi,
- `.txt`: sade arşiv ve denetim özeti,
- `.html`: koyu temalı okunabilir rapor,
- `.pdf`: ek sistem bağımlılığı istemeyen arşiv PDF'i.

## Etik ve hukuki sınır

BlackHawk özel hesaplara erişmez, parola/token toplamaz, güvenlik aşmaz,
doxxing, taciz, ısrarlı takip, hedefli zarar, kimlik bilgisi denemesi,
rate-limit/robots kurallarını atlatma veya gizli veri birleştirme için
kullanılamaz. Kamuya açık olmak, otomatik kullanım için sınırsız izin değildir.
Kaynak şartları, telif, KVKK, TCK, 5651 sayılı Kanun ve diğer güncel mevzuat
önceliklidir. Bu yazılım hukuki danışmanlık, delil kabulü veya resmi soruşturma
garantisi vermez. Acil tehlikede 112'yi, olay bildiriminde yetkili resmi kanalları
kullanın.

Olay Analizi bölümü yalnızca kullanıcının yazdığı metni düzenler. “Biri beni
bıçakladı” gibi bir anlatımda acil tehlike sinyali gösterebilir ve zaman, yer,
tanık, belge ve kamuya açık URL gibi kanıt başlıklarını hatırlatabilir; kişi
bulamaz, suçlu ilan etmez, özel veri aramaz ve emniyet adına karar vermez.

## Geliştirme ve test

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m build
```

Güvenlik bildirimi için canlı token, parola, özel URL veya kişisel veri
göndermeyin. Geliştirici iletişimi ve hata/öneri kanalı: **Telegram @AltayHR**.
Topluluk: **TurkHackTeam**.

## Bağlantılar

- GitHub: https://github.com/ThT0AltayHR/blackhawk
- PyPI: https://pypi.org/project/blackhawk/
- TurkHackTeam: https://turkhackteam.org/

## Hashtag

`#osint #open-source-intelligence #public-data #evidence #termux #python
#textual #ethical-security #turkhackteam #blackhawk`

## Lisans

MIT. Ayrıntılı güvenlik sınırları için `SECURITY.md` dosyasına bakın.