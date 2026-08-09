# BLACKHAWK

**Kamu Kaynaklı İstihbarat ve İzleme Terminali**

BlackHawk, yalnızca yetkili ve kamuya açık kaynaklardan elde edilen gözlemleri
toplayan, kaynakları ilişkilendiren ve Türkçe raporlayan yerel bir TUI aracıdır.
Özel hesaplara erişmez, parola toplamaz, güvenlik aşmaz, kimlik tahmini satmaz ve
bulgu yoksa veri uydurmaz.

![BlackHawk terminal arayüzü](assets/blackhawk-terminal.png)

## Özellikler

- Türkçe, klavye odaklı Textual terminal arayüzü
- Yeni hedef ve çoklu hedef oturumları
- Demo/offline çalışma modu
- Yalnızca `http` ve `https` kamu URL'leri için güvenli kaynak gözlemi
- Alias, URL ve zaman eşleştirmeli korelasyon
- `zayıf sinyal`, `tek kaynak`, `muhtemel`, `doğrulanmış`, `çelişkili` sınıfları
- Kaynaklı olaylar, doğrulama durumları ve audit log
- 1 dakika, 5 dakika, 10 dakika, 1 saat, 2 saat, 3 saat, 20 saat, 24 saat,
  48 saat, 72 saat, 200 saat, 265 saat, 300 saat ve özel süre
- HTML, JSON ve TXT raporları
- Path sanitization, HTML escaping, gizli veri maskesi ve oran sınırlama
- TCK / etik kullanım rehberi ve bağlamsal yardım

## Kurulum

```bash
pip install blackhawk
blackhawk
```

Geliştirme kurulumu:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest
blackhawk --demo
```

## Güvenlik sınırı

Bu proje bir hedefin özel bilgilerini bulmaya, gizli bir hesaba erişmeye,
doxxing yapmaya veya kişileri takip etmeye yönelik değildir. Yalnızca açıkça
yetkilendirilmiş çalışma kapsamındaki kamu kaynaklarını kullanın. Her rapor,
kaynak ve zaman bilgisi olmadan iddia üretmez.

Gerçek CVE numarası içermez. Güvenlik bildirimleri için
[SECURITY.md](SECURITY.md) içindeki CVE-ready şablonu kullanılabilir.

## Yapay zekâ görselleri

Depo tanıtımında kullanılmak üzere üretilen görseller:

1. `assets/gallery/blackhawk-hero.png`
2. `assets/gallery/blackhawk-public-sources.png`
3. `assets/gallery/blackhawk-timeline.png`
4. `assets/gallery/blackhawk-network.png`
5. `assets/gallery/blackhawk-evidence.png`
6. `assets/gallery/blackhawk-monitoring.png`
7. `assets/gallery/blackhawk-report.png`

## Lisans

MIT. Kamu kaynaklarının kullanım koşulları, telif, robots.txt, API şartları ve
yerel hukuk her zaman önceliklidir.