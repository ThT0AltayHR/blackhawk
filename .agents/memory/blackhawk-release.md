---
name: BlackHawk dağıtımı
description: BlackHawk Python paketinin yayın ve güvenlik sınırları
---

BlackHawk yalnızca açıkça yetkilendirilmiş kamu URL'leri ve demo verisi için
tasarlanmıştır; özel hesap erişimi, kimlik bilgisi toplama, doxxing, gizli
takip ve güvenlik aşımı ürün kapsamı değildir.

**Why:** Ürün tanımı OSINT/izleme dili kullansa da güvenli ve etik kullanım
sınırı gerçek kullanıcı verisine zarar verebilecek özelliklerden daha
önceliklidir.

**How to apply:** Yeni bağlayıcı, tarama özelliği veya rapor alanı eklenirken
kaynak atfı, rate limit, veri minimizasyonu ve güvenli hedef doğrulaması
korunmalı; kaynaksız bulgu üretilmemelidir.

PyPI yayını `blackhawk` adıyla yapılır. PyPI JSON uç noktası kısa süreli eski
metadata döndürebilir; yayın kontrolünde `https://pypi.org/simple/blackhawk/`
ve resmi `--index-url https://pypi.org/simple` kurulumu esas alınmalıdır.

**Why:** Yayın sonrası 0.1.1 dosyaları simple indeksinde görünürken JSON
endpoint'i kısa süre 0.1.0 önbelleği döndürdü.

**How to apply:** Yeni sürümden sonra dosya adını simple indekste kontrol et,
cache'siz resmi PyPI kurulumu yap, ardından `blackhawk --version` doğrula.