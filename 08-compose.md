# فصل ۸ — Docker Compose: کل استک با یک دستور ⭐

> 🎯 **هدف:** پروژه واقعی یک کانتینر نیست — اپ + دیتابیس + شاید redis. یاد می‌گیری همه رو با یک فایل YAML تعریف و با **یک دستور** بالا بیاری: `docker compose up`. پرکاربردترین ابزار روزمره‌ی دولوپرها.

---

## ۸.۱ — مسئله: ده دستور برای هر بار بالا آوردن استک

بدون compose، استک واقعی پروژه یعنی:

```bash
docker run -d --name db -e POSTGRES_PASSWORD=1234 -p 5432:5432 postgres:18
docker run -d --name redis -p 6379:6379 redis:7-alpine
docker run -d --name api -p 3000:3000 --link db... myapi:1.0   # و اتصالات و ترتیب‌ها...
```

تکرار دستی این دستورات در هر بار راه‌اندازی، توسط هر عضو تیم یا در محیط‌های مختلف، بسیار خطاپذیر است و مدیریت فلگ‌ها و پورت‌ها را دشوار می‌کند.

**جواب Compose:** همه رو در یک فایل `compose.yaml` تعریف کن (نسخه‌پذیر در git!) و:

```bash
docker compose up -d      # همه با هم — همون npm install + start جهان داکر
```

## ۸.۲ — اولین compose.yaml

در پوشه پروژه (کنار Dockerfile)، فایل `compose.yaml`:

```yaml
services:
  api:
    build: .                  # از Dockerfile همین پوشه بساز
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - db

  db:
    image: postgres:18
    environment:
      POSTGRES_PASSWORD: mysecretpass
      POSTGRES_DB: shop
    ports:
      - "5432:5432"
```

آناتومی:

| کلید | معنی |
|---|---|
| `services:` | هر سرویس = یک کانتینر از یک ایمیج |
| `build: .` | از Dockerfile این پوشه build کن (به جای image آماده) |
| `image: postgres:18` | یا از ایمیج آماده |
| `ports: - "3000:3000"` | همون `-p` (میزبان:کانتینر) |
| `environment:` | همون `-e` ها — و چون YAML است، خواناتر |
| `depends_on:` | ترتیب: اول db بالا بیاد، بعد api |

## ۸.۳ — سه دستور طلایی

```bash
$ docker compose up -d        # بالا بیاور (build در صورت نیاز) — کافیه!
$ docker compose ps           # وضعیت سرویس‌ها
$ docker compose logs -f api  # لاگ یک سرویس (یا همه: بدون اسم)

$ docker compose down         # توقف + حذف کانتینرها و شبکه (ایمیج‌ها و volumes می‌مانند)
```

حتی `build` هم لازم نیست جدا بزنی — `up` خودش تشخیص می‌ده. و برای «کد عوض شد، دوباره بساز»:

```bash
$ docker compose up -d --build
```

> 💡 سرویس‌ها با اسمشون صدا زده می‌شن: `docker compose restart db`، `docker compose exec api sh` — همون دستورهای فصل ۵، فقط به جای اسم کانتینر، اسم سرویس.

## ۸.۴ — پروژه نمونه: استک واقعی (api + db)

همون اپ `myapi` فصل ۶ — ولی این‌بار با دیتابیس. اول کد رو به Postgres وصل کنیم (`server.js` ساده‌شده):

```js
const express = require("express");
const { Pool } = require("pg");
const app = express();

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,   // از environment کانتینر!
});

app.get("/", async (req, res) => {
  const { rows } = await pool.query("SELECT version()");
  res.json({ db: rows[0].version.slice(0, 30) });
});

app.listen(3000);
```

(توجه: پیش از بیلد، پکیج `pg` را با دستور `npm i pg` به پروژه اضافه کرده و در `package.json` قرار دهید.)

و compose.yaml نهایی:

```yaml
services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgres://postgres:mysecretpass@db:5432/shop   # ← host = اسم سرویس!
    depends_on:
      - db

  db:
    image: postgres:18
    environment:
      POSTGRES_PASSWORD: mysecretpass
      POSTGRES_DB: shop
    volumes:
      - pgdata:/var/lib/postgresql/data   # داده ماندگار (فصل ۹!)

volumes:
  pgdata:
```

اجرا و تست:

```bash
$ docker compose up -d --build
$ curl http://localhost:3000
{"db":"PostgreSQL 18.4 (Debian 12..."}
```

API تو از داخل یک کانتینر به دیتابیس داخل کانتینر دیگه وصل شد. 🎉 (راز `@db:5432` — فصل ۱۰!)

## ۸.۵ — .env در compose (همون الگوی همیشگی ⭐)

پسورد داخل YAML که توی git می‌ره؟ نه! الگوی استاندارد:

**`.env`** (کنار compose.yaml، در .gitignore):

```
POSTGRES_PASSWORD=mysecretpass
```

**`compose.yaml`:**

```yaml
  db:
    image: postgres:18
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

Compose خودش فایل `.env` کنار خودش رو می‌خونه و جایگزین می‌کنه — مقادیر در دو لایه تزریق می‌شوند: env فایل → YAML → env کانتینر → برنامه. (توصیه حرفه‌ای: همیشه یک فایل `.env.example` بدون مقادیر حساس برای مخزن گیت ایجاد کنید تا سایر توسعه‌دهندگان از ساختار متغیرها مطلع شوند.)

## ۸.۶ — دستورهای مکمل

```bash
$ docker compose up -d --build db      # فقط یک سرویس
$ docker compose exec db psql -U postgres   # اجرای دستورات مدیریت دیتابیس در کانتینر
$ docker compose restart api
$ docker compose down -v               # ⚠️ با حذف volumes — داده‌ها می‌روند!
$ docker compose config                # خروجی نهایی YAML (با env جایگزین‌شده) — برای چک
```

---

## ✅ جمع‌بندی فصل

- استک چند‌کانتینره = `compose.yaml` در git + `docker compose up -d`
- `build:` vs `image:`؛ ports/environment/depends_on = معادل فلگ‌های run
- `down` کانتینرها را می‌برد؛ با `-v` داده هم می‌رود (خطرناک!)
- راز اتصال: اسم سرویس = hostname (`@db:5432`) — فصل ۱۰ کامل
- رازها با `.env` کنار compose — هرگز در YAML خالی

## 📝 تمرین فصل ۸

1. استک api + db این فصل را کامل بساز و بالا بیار؛ curl بزن و پاسخ PostgreSQL را ببین.
2. `docker compose ps` و `docker compose logs -f api` را تست کن.
3. با `docker compose exec db psql -U postgres -d shop` برو داخل دیتابیس و `\l` بزن.
4. compose را down کن و دوباره up — curl دوباره جواب می‌دهد؟ (بله! چون ایمیج و volume باقی‌اند.)
5. پسورد را به `.env` منتقل کن و با `docker compose config` صحت جایگزینی را چک کن.

<details><summary>نکته تمرین ۲</summary>

`logs -f api` فقط لاگ سرویس api را زنده نشان می‌دهد؛ بدون اسم سرویس، همه سرویس‌ها قاطی می‌آیند (با پیشوند اسم سرویس) — برای دیدن «همه‌چیز با هم» موقع startup عالی است.
</details>

➡️ **فصل بعد:** volume ها — داده‌ای که با down نمی‌میرد و توسعه‌ی زنده با bind mount.
