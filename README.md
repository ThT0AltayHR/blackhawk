# BLACKHAWK v1.0.0

**Yetkili kamu kaynakları için etik Türkçe OSINT izleme, olay notlandırma ve kanıt raporlama terminali.**

[![PyPI](https://img.shields.io/pypi/v/blackhawk?color=9b2430)](https://pypi.org/project/blackhawk/)
[![Python](https://img.shields.io/pypi/pyversions/blackhawk)](https://pypi.org/project/blackhawk/)
[![License](https://img.shields.io/badge/license-MIT-5b6470)](blackhawk/LICENSE)

![BlackHawk terminal arayüzü](https://raw.githubusercontent.com/ThT0AltayHR/blackhawk/main/blackhawk/assets/blackhawk-terminal.png)

BlackHawk; açıkça yetkilendirilmiş HTTP/HTTPS kaynaklarından sınırlı ve
kaynaklı gözlemler alan, erişim zamanını ve audit log'u koruyan, Türkçe
raporlar üreten yerel bir terminal aracıdır. Kaynak yoksa veri uydurmaz.
Özel hesaplara erişmez, parola veya token toplamaz, güvenlik aşmaz.

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

İlk açılışta üç sözleşme ekranında `EVET` yazılır, en az 20 karakterli ve
yalnızca büyük harf/rakam içeren bir oturum tokeni girilir. Token terminalde
gösterilmez ve ham olarak saklanmaz; yalnızca SHA-256 parmak izi tutulur.
Operatör adı rapor kimliği için alınır. Profil kasası parolası en az 8
karakter, bir büyük harf ve bir rakam içermelidir. Bu parola e-Devlet, MHRS,
banka veya sosyal medya parolasıyla aynı seçilmemelidir.

## Özellikler

- Siyah-kırmızı, Türkçe, klavye odaklı premium Textual TUI.
- Textual bulunmayan Termux/minimal ortamlarda ANSI fallback.
- Yetkili tekli/çoklu hedef, canlı gözlem, kaynak, hashtag, zaman çizelgesi,
  ilişki, kanıt, ajan, yardım, rapor, ayar, iletişim ve güvenlik ekranları.
- Olay Analizi: kullanıcının kendi metnini yerel olarak anahtar kelime,
  aciliyet sinyali ve kanıt ihtiyaçlarına ayıran taslak yardımcı.
- HTML, JSON, TXT ve bağımlılıksız PDF raporları.
- URL kimlik bilgisi, token/secret parametresi ve güvensiz rapor yolları reddi.
- Demo modu yoktur; sahte bulgu, sahte doğrulama ve sahte ajan yoktur.

## Kullanım

```bash
blackhawk --version
blackhawk --target https://example.org --duration 60 --reports reports
```

Ana menü: `↑/↓` gezin, `Enter` aç, `r` tara, `h` yardım, `Esc` geri,
`q` çıkış. Her modül kendi `BAŞLAT`/`GERİ` ekranına sahiptir. Raporlar
`reports/` altında `.json`, `.txt`, `.html` ve `.pdf` olarak oluşur.

Olay Analizi bir soruşturma veya kolluk sistemi değildir: yer, zaman, tanık,
belge ve kamuya açık URL gibi kanıt başlıklarını hatırlatır; kişiyi bulmaz,
suçlu ilan etmez, özel veri aramaz. Acil tehlikede 112'yi ve olay bildiriminde
yetkili resmi kanalları kullanın.

## Etik ve hukuki sınır

Yetkisiz erişim, kimlik bilgisi denemesi, rate limit/robots aşma, doxxing,
taciz, gizli takip, tehdit, hedefli zarar, gereksiz kişisel veri birleştirme
ve kaynaksız suç isnadı desteklenmez. Kamuya açık olmak sınırsız otomatik
kullanım izni değildir. Kaynak şartları, telif, KVKK, TCK ve diğer güncel
mevzuat önceliklidir. Bu araç hukuki danışmanlık veya resmi delil garantisi
vermez. Ayrıntılar için [blackhawk/SECURITY.md](blackhawk/SECURITY.md).

## Geliştirme

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m build
```

Hata ve öneri bildirimleri: Telegram **@AltayHR**. Canlı token, parola,
özel URL veya gereksiz kişisel veri paylaşmayın. Topluluk: **TurkHackTeam**.

## Bağlantılar ve etiketler

- GitHub: https://github.com/ThT0AltayHR/blackhawk
- PyPI: https://pypi.org/project/blackhawk/
- TurkHackTeam: https://turkhackteam.org/

`#osint #open-source-intelligence #public-data #evidence #termux #python
#textual #ethical-security #turkhackteam #blackhawk`

## Lisans

MIT. See [blackhawk/LICENSE](blackhawk/LICENSE).