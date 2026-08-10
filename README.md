# BlackHawk

BlackHawk, Termux ve minimal Python kurulumlarında çalışabilen, yalnızca
kullanıcının sağladığı yetkili ve kamuya açık HTTP/HTTPS kaynaklarından küçük
özetler çıkaran yerel bir terminal aracıdır.

## Termux kurulumu

```sh
pkg update
pkg install python
python -m pip install --upgrade pip
python -m pip install .
blackhawk
```

Uygulama artık oturum tokeni, PyPI tokeni, GitHub tokeni veya profil parolası
istemez. `blackhawk` komutu Termux'ta tam ekran, renkli ANSI kontrol merkezini
doğrudan açar. Textual arayüzünü yalnızca `blackhawk --ui textual` ile
isteğe bağlı olarak seçebilirsiniz.

## Kullanım

```sh
blackhawk --target https://example.com
blackhawk --ui ansi
blackhawk --help
```

ANSI menüsünde:

- `1` yetkili kaynak ekler
- `2` canlı izlemeyi çalıştırır
- `3` raporları üretir
- `4` yardım ekranını açar
- `q` çıkar

Araç özel hesaplara giriş yapmaz, kimlik bilgisi içeren URL'leri reddeder ve
yalnızca izinli/kamuya açık kaynaklar için kullanılmalıdır.