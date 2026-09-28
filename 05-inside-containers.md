# فصل ۵ — داخل کانتینر: exec، متغیرها و دیباگ واقعی

> 🎯 **هدف:** یاد بگیری «بروی داخل» کانتینر — شل بگیری، فایل‌ها رو ببینی، متغیرهای محیطی رو چک کنی. این همون مهارتیه که در شرکت، وقتی «کانتینر ارور می‌ده» ازت انتظار دارن.

---

## ۵.۱ — ورود به کانتینر: `docker exec -it`

کانتینر = یک لینوکس در حال اجراست — پس می‌شه شل گرفت!

```bash
$ docker run -d --name web nginx

$ docker exec -it web bash
root@a1b2c3d4:/#         ← شل داخل کانتینر! حالا «تویی»
```

باز کردن فلگ‌ها (دو کلید طلایی):
- `-i` (interactive) = stdin باز نگه دار — بتونی تایپ کنی
- `-t` (tty) = ترمینال بساز — prompt و رنگ و رفتار درست

همیشه با هم: **`-it`**. دستور `exec` برای اجرای یک دستور یا برنامه جدید *درون کانتینری است که در حال حاضر اجرا می‌شود* (در اینجا اجرای شل `bash`).

حالا داخلش بازی کن:

```bash
root@a1b2c3d4:/# ls                 # فایل‌سیستم لینوکس ایمیج nginx
bin   dev   etc   usr   var   ...

root@a1b2c3d4:/# cat /etc/os-release   # چه توزیعی هستیم؟
PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"

root@a1b2c3d4:/# ps aux             # پروسه‌های «این کانتینر» — فقط nginx خودش!
USER  PID %CPU COMMAND
root    1  0.0  nginx: master process

root@a1b2c3d4:/# exit               # خروج — کانتینر ادامه می‌دهد اجرا ✅
```

> 🔑 نکته‌ی «آهاااا»: `ps` داخل کانتینر فقط پروسه‌های خودش رو می‌بینه (PID 1 = nginx). این همون ایزوله‌سازی فصل ۱ است — هر کانتینر دنیای خودشه. و نکته دوم: کانتینر **زنده‌ست وقتی پروسه اصلی‌اش زنده‌ست** — exit از شل، کانتینر رو نمی‌کشه.

## ۵.۲ — بدون ورود: exec برای یک دستور

برای کارهای سریع لازم نیست وارد بشی:

```bash
$ docker exec web cat /etc/nginx/nginx.conf      # فایل کانفیگ nginx را بخوان
$ docker exec web ls /usr/share/nginx/html       # فایل‌های سایت
$ docker exec web env | grep -i nginx            # متغیرهای محیطی‌اش
```

## ۵.۳ — دیباگ واقعی: چرا کانتینرم بالا نمیاد؟

چرخه‌ی استاندارد دیباگ (این رو حفظ کن — در شرکت هر هفته لازمه):

```bash
$ docker ps -a                      # ۱) کانتینر هست؟ وضعیتش چیه؟
# Exited (1) — یعنی کرش کرده و پروسه با کد خطای ۱ خارج شده (exit code 1)

$ docker logs --tail 50 my-app     # ۲) لاگ — ۹۰٪ جواب اینجاست

$ docker exec -it my-app sh        # ۳) داخل شو و دستی تست کن
# (کانتینر مرده؟ از روی ایمیجش یک کانتینر موقت بزن: docker run -it --entrypoint sh node:22-alpine)

$ docker inspect my-app            # ۴) همه جزئیات: پورت‌ها، env، مانت‌ها
```

> ⚠️ نکته‌ی `sh` به جای `bash`: ایمیج‌های alpine برای سبکی، bash ندارن — `sh` دارن. اگه `exec -it x bash` ارور داد، alpine اس؛ `sh` بزن.

## ۵.۴ — `docker inspect`: شناسنامه کانتینر

خروجی JSON بزرگه — با ابزارهای شل فیلترش کن:

```bash
$ docker inspect my-web | grep -A 5 "PortBindings"
$ docker inspect --format '{{.Config.Image}}' my-web     # nginx
$ docker inspect --format '{{.State.Status}}' my-web     # running
```

(چیز مفیدی دیدی؟ `--format` با template — مثل template literal ها.)

## ۵.۵ — کپی فایل بین میزبان و کانتینر

```bash
$ docker cp my-web:/usr/share/nginx/html/index.html ./      # از کانتینر به سیستم
$ docker cp ./new-page.html my-web:/usr/share/nginx/html/   # از سیستم به کانتینر
```

(مشابه انتقال فایل در لینوکس یا شبکه.) برای دیباگ/استخراج لاگ/گرفتن فایل کانفیگ عالیه. ⚠️ ولی توجه: این تغییر *فقط در این کانتینر* است — کانتینر rm شه می‌پره. راه درست ماندگاری = volume (فصل ۹) و راه درست تغییر ایمیج = Dockerfile (فصل ۶).

## ۵.۶ — متغیرهای محیطی از نگاه داخل

امتحان کن (از فصل ۳):

```bash
$ docker run -d --name db -e POSTGRES_PASSWORD=secret -e APP_MODE=dev postgres:18

$ docker exec db env | grep -E "POSTGRES|APP_MODE"
POSTGRES_PASSWORD=secret
APP_MODE=dev
```

این دقیقاً همان مقادیری است که برنامه از طریق `process.env` دریافت می‌کند — جریان کانفیگ: `-e` یا فایل env → متغیر محیطی کانتینر → برنامه داخلش می‌خونه. (در فصل ۸ همینو با compose حرفه‌ای‌تر می‌کنیم.)

---

## ✅ جمع‌بندی فصل

- `docker exec -it <name> bash` = ورود؛ `sh` برای ایمیج‌های alpine
- داخل کانتینر: دنیای خودش — `ps` فقط پروسه‌های خودش را می‌بیند
- چرخه دیباگ: `ps -a` → `logs` → `exec` → `inspect`
- `docker cp` = انتقال فایل بین میزبان و کانتینر (موقتی — دائمی‌اش volume/Dockerfile)
- کانفیگ از بیرون = `-e` → `env` داخل کانتینر → برنامه می‌خواند

## 📝 تمرین فصل ۵

1. nginx اجرا کن، واردش شو (`exec -it ... bash`)، نسخه Debian را بخوان، `nginx -v` را اجرا کن و خارج شو.
2. با `docker exec` (بدون ورود) فایل `/etc/nginx/nginx.conf` را بخوان و با `grep` عبارت `server {` را در آن پیدا کن.
3. یک کانتینر با دو متغیر محیطی بساز (`-e GREETING="سلام" -e ENV_NAME=test`) و از داخلش `env` بزن و هر دو را ببین.
4. چالش دیباگ ⭐: یک کانتینر بنویس که کرش کنه: `docker run --name crasher alpine sh -c "echo boom; exit 1"` — حالا چرخه دیباگ را کامل اجرا کن: ps -a (کد خروج؟) → logs (چه گفت؟) → و در آخر rm کن.
5. یک فایل از کانتینر nginx به سیستم کپی کن و محتواش را cat کن.

<details><summary>جواب تمرین ۴</summary>

```bash
docker run --name crasher alpine sh -c "echo boom; exit 1"
docker ps -a --filter name=crasher     # وضعیت: Exited (1) ← کد خروج ۱
docker logs crasher                    # خروجی: boom
docker rm crasher
```
</details>

➡️ **فصل بعد:** ساخت اولین Dockerfile و بسته‌بندی یک پروژه وب!
