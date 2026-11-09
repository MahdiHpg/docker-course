# فصل ۲ — نصب داکر روی ویندوز و اولین hello-world

> 🎯 **هدف:** Docker Desktop رو درست نصب کنی (با WSL2)، مطمئن شی همه‌چیز وصل است، و اولین کانتینرت رو اجرا کنی. آخر فصل `docker run hello-world` برای تو یک دستور جادویی نیست.

---

## ۲.۱ — پیش‌نیاز ویندوز: WSL2 چیست و چرا لازمه؟

کانتینرهای دنیا **لینوکسی‌ان** و به هسته‌ی لینوکس نیاز دارن. ویندوز هسته لینوکس نداره — پس Docker Desktop یک لینوکس سبک با **WSL2** (Windows Subsystem for Linux 2) پشت صحنه بالا میاره و Engine اونجا اجرا می‌شه. تو احساسش نمی‌کنی؛ فقط بدون که داری کانتینر لینوکس واقعی اجرا می‌کنی.

چک/فعال‌سازی WSL2 (یک بار، در PowerShell با دسترسی ادمین):

```powershell
wsl --status          # اگر نصب است: نسخه پیش‌فرض باید 2 باشد
wsl --install         # اگر نیست: نصب (ویندوز ری‌استارت می‌خواهد)
```

> 💡 گاهی پیام «Virtualization not enabled» می‌بینی — یعنی باید در BIOS سیستم، Virtualization (VT-x / AMD-V) فعال شه. اکثر سیستم‌های جدید روشنه.

## ۲.۲ — نصب Docker Desktop

1. برو به **https://www.docker.com/products/docker-desktop/** → نسخه ویندوز (AMD64) رو بگیر (4.9x فعلی)
2. نصب‌کننده رو اجرا کن — گزینه **Use WSL 2 instead of Hyper-V** تیک‌خورده بمونه
3. بعد از نصب و ری‌استارت، Docker Desktop رو باز کن — آیکون نهنگ 🐳 در tray باید ثابت (بدون انیمیشن) بمونه یعنی Engine بالاست
4. قرارداد لایسنس رو قبول کن (برای استفاده شخصی و تیم‌های کوچک رایگانه)

## ۲.۳ — تأیید سلامت: چهار دستور

در Git Bash (یا ترمینال VS Code):

```bash
$ docker version
Client: Docker Engine - Community
 Version:           29.x.x
Server: Docker Engine - Community
 Engine Version:    29.x.x
 ✓ (مهم: بخش Server هم باید باشد — یعنی CLI به Engine وصل است)

$ docker info | head -20      # اطلاعات کامل محیط

$ docker run hello-world
Hello from Docker!            # 🎉 اولین کانتینر!
...

$ docker compose version
Docker Compose version v2.x.x
```

> 🔍 چیزی که تازه اتفاق افتاد، قدم‌به‌قدم:
> 1. `docker run hello-world` → داکر دید ایمیج `hello-world` لوکال نیست
> 2. از Docker Hub `pull` کرد (دانلود چند کیلوبایت)
> 3. ازش یک کانتینر ساخت و اجرا کرد
> 4. کانتینر کارش رو کرد (پیام چاپ کرد) و تموم شد
>
> این چرخه «نگردم بگیر → اجرا کن» همون npm-like رفتاریه که فصل ۱ گفتم.

## ۲.۴ — آشنایی با Docker Desktop (GUI)

ترمینال ابزار اصلی ماست ولی GUI هم برای «دیدن» خوبه — تب‌های مهمش:

- **Containers:** لیست کانتینرهای در حال اجرا/خاموش + دکمه start/stop/delete + **Logs** گرافیکی
- **Images:** ایمیج‌های دانلودشده روی سیستم
- **Volumes:** داده‌های ماندگار (فصل ۹)

> 💡 قانون دوره: هر کاری رو *اول* با CLI یاد بگیر (چون در شرکت/سرور فقط CLI داری)، بعد GUI رو به چشم «داشبورد نگاه سریع» استفاده کن.

## ۲.۵ — تنظیمات پیشنهادی اولیه

Docker Desktop → Settings (چرخ‌دنده):

| تنظیم | پیشنهاد | چرا |
|---|---|---|
| General → Start Docker Desktop when you sign in | به سلیقه | اگه هر روز کار می‌کنی، روشن بذار |
| Resources → Advanced (در WSL2 محدود است) | پیش‌فرض WSL2 | WSL2 خودش مدیریت می‌کنه |
| Choose how to configure installs... | پیش‌فرض | — |

و یک نکته ترمینالی: مطمئن شو `docker` در ترمینال (مثل Git Bash، PowerShell یا CMD) کار می‌کنه — Docker Desktop در زمان نصب مسیر اجرایی خود را به متغیر محیطی PATH سیستم اضافه می‌کند تا در هر مسیری قابل فراخوانی باشد. اگر ابتدا کار نکرد، کافیست پنجره ترمینال را ببندید و مجدداً باز کنید تا PATH بازخوانی شود.

## ۲.۶ — عیب‌یابی‌های نصب رایج

| مشکل | علاج |
|---|---|
| `docker: command not found` | Docker Desktop روشن نیست یا PATH تازه نشده — ترمینال جدید باز کن |
| Docker Desktop منتظر Engine می‌مونه | WSL2 را به‌روز کن: `wsl --update` (PowerShell ادمین) و ری‌استارت |
| «WSL 2 installation is incomplete» | همون `wsl --update` + ری‌استارت ویندوز |
| کندی عجیب | آیکون نهنگ را چک کن — Engine خاموشه؛ Desktop را باز کن |

---

## ✅ جمع‌بندی فصل

- WSL2 = لینوکس زیر داکر روی ویندوز؛ `wsl --install` و `wsl --update`
- Docker Desktop نصب شد؛ `docker version` باید Client **و** Server را نشان دهد
- `docker run hello-world` = چرخه کامل: pull از Hub → ساخت کانتینر → اجرا → پایان
- GUI فقط داشبورد؛ CLI ابزار اصلی تو است
- `command not found` = دسکتاپ خاموش یا ترمینال قدیمی

## 📝 تمرین فصل ۲

1. نصب را کامل کن و هر چهار دستور بخش ۲.۳ را بزن — خروجی `docker version` را باز کن و نسخه Engine را بنویس.
2. `docker run hello-world` را **دوبار** بزن. بار دوم چقدر سریع‌تر بود؟ چرا؟ (راهنمایی: ایمیج لوکال شده — مثل npm cache!)
3. Docker Desktop را باز کن: در تب Images، ایمیج `hello-world` را ببین. در تب Containers، کانتینر تمام‌شده را پیدا کن (وضعیتش چیه؟).
4. (کشف آزاد) `docker --help` را بزن و فقط *اسم* زیرفرمان‌های اصلی را نگاه کن — لیست طولانیه ولی از فصل بعد، این‌ها را همه می‌شناسی.

<details><summary>جواب تمرین ۲</summary>

بار دوم فوری است چون ایمیج hello-world از قبل روی دیسک است و داکر فقط کانتینر از رویش می‌سازد — دانلودی در کار نیست. با `docker images` می‌توانی ایمیج لوکال را ببینی.
</details>

➡️ **فصل بعد:** کانتینرهای واقعی — وب‌سرور اجرا کن، پورت‌ها را وصل کن و لاگ‌ها را بخوان.
