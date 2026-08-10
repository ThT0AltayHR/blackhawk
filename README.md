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
istemez. Varsayılan Termux arayüzü bağımlılıksız ANSI menüsüdür. İsterseniz
Textual arayüzünü ayrıca kurup `blackhawk --ui textual` ile deneyebilirsiniz.

## Kullanım

```sh
blackhawk --target https://example.com
blackhawk --ui ansi
blackhawk --help
```

Araç özel hesaplara giriş yapmaz, kimlik bilgisi içeren URL'leri reddeder ve
yalnızca izinli/kamuya açık kaynaklar için kullanılmalıdır.