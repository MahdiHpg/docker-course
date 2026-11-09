# فصل ۱۱ — 🚀 داکر در کار روزمره: استک کامل Next.js + Postgres + Prisma

> 🎯 **هدف:** سناریوی واقعی تیم‌های مهندسی نرم‌افزار: اجرای دیتابیس در کانتینر ایزوله، اجرای فریم‌ورک وب (مانند Next.js) روی سیستم میزبان، و ارتباط ORM (مانند Prisma) بین آن‌ها.

---

## ۱۱.۱ — الگوی استاندارد: دیتابیس داکری، اپ لوکال

در اغلب پروژه‌های مدرن تحت وب: **برنامه اصلی روی سیستم توسعه‌دهنده اجرا می‌شود** (`npm run dev` — برای استفاده از hot-reload سریع) اما **دیتابیس‌ها و سرویس‌های جانبی در کانتینر داکر** نگه‌داری می‌شوند (برای پرهیز از نصب سنگین سرویس‌ها روی سیستم‌عامل و تضمین یکسانی نسخه در تمام تیم). این یک الگوی استاندارد در صنعت نرم‌افزار است:

```mermaid
flowchart LR
    V["محیط توسعه / IDE"] -->|"npm run dev :3000"| N["برنامه Next.js روی میزبان"]
    N -->|"DATABASE_URL<br/>@localhost:5432"| P["Postgres 18<br/>کانتینر داکر + Volume"]
```

## ۱۱.۲ — راه‌اندازی در ۵ دقیقه

در ریشه پروژه، فایل `compose.yaml` را بسازید:

```yaml
services:
  db:
    image: postgres:18
    environment:
      POSTGRES_PASSWORD: devpass
      POSTGRES_DB: myshop
    ports:
      - "127.0.0.1:5432:5432"     # فقط دسترسی امن از سیستم میزبان
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

و فایل `.env` پروژه:

```
DATABASE_URL="postgresql://postgres:devpass@localhost:5432/myshop"
```

بالا بیاورید و ابزار مهاجرت پایگاه داده (Prisma) را متصل کنید:

```bash
$ docker compose up -d
$ sleep 3 && docker compose logs --tail 5 db   # صبر برای آماده‌شدن دیتابیس

$ npx prisma migrate dev                       # اجرای migrationها روی دیتابیس کانتینری!
$ npm run dev                                  # اجرای برنامه — متصل به دیتابیس داکر
```

به این ترتیب یک محیط توسعه کامل، نسخه‌دار، قابل‌حذف و بازسازی سریع فراهم می‌شود؛ هر برنامه‌نویس دیگری در تیم با دریافت پروژه تنها با دستور `docker compose up -d` تمام سرویس‌های لازم را آماده خواهد داشت.

> 🔑 همیشه این فایل `compose.yaml` و یک نمونه `.env.example` را در مخزن گیت پروژه کامیت کنید تا فرآیند onboarding اعضای جدید تیم فوری و بی‌دردسر باشد.

## ۱۱.۳ — گردش‌های روزمره (چیت‌شیت زنده)

| کار | دستور |
|---|---|
| شروع روز کاری | `docker compose up -d` |
| ریست کامل دیتابیس توسعه | `docker compose down -v && docker compose up -d` و بعد `npx prisma migrate dev` |
| دیدن لاگ دیتابیس | `docker compose logs -f db` |
| ورود به کنسول psql بدون نصب ابزار در سیستم | `docker compose exec db psql -U postgres -d myshop` |
| چک وضعیت سرویس‌ها | `docker compose ps` |
| پایان روز کاری | `docker compose stop` (سریع‌تر از down — کانتینرها متوقف می‌مانند) |

به دستور `exec db psql` دقت کنید: حتی اگر کلاینت PostgreSQL روی سیستم‌عامل میزبان نصب نباشد، کلاینت داخلی کانتینر مستقیماً اجرا می‌شود (مطابق آموزش فصل ۵).

## ۱۱.۴ — نکات کلیدی ارتباط با دیتابیس و داکر

**۱) خطای عدم اتصال در ابتدای کار (P1001 در Prisma):** همان‌طور که در فصل ۱۰ دیدیم، بالا آمدن کانتینر دیتابیس چند ثانیه زمان می‌برد تا سوکت‌های شبکه آماده پذیرش ارتباط شوند. همیشه ابتدا با `docker compose logs db` آماده بودن سرور را بررسی کنید یا از مکانیزم `healthcheck` استفاده کنید.

**۲) خطای اشغال بودن پورت («Port already allocated»):** اگر قبلاً دیتابیسی روی سیستم میزبان پورت ۵۴۳۲ را اشغال کرده باشد، دو راه‌حل وجود دارد: متوقف کردن آن سرویس در سیستم، یا تغییر پورت بیرونی کانتینر مثلاً به `5433:5432` و تنظیم آدرس کانکشن استرینگ به `localhost:5433`. برای پیدا کردن پروسه اشغال‌کننده پورت می‌توان از `netstat -ano` استفاده کرد.

**۳) تنظیم صحیح متغیرهای آدرس‌دهی:** به تفاوت آدرس اتصال دقت کنید: زمانی که برنامه روی هاست اجرا می‌شود از `localhost` استفاده می‌کند، اما اگر برنامه داخل شبکه کانتینرها باشد از نام سرویس (مانند `db`) استفاده می‌کند.

## ۱۱.۵ — پروژه‌ی نهایی فصل: خودت اینو بساز ⭐

تمرین جامع — یک `docker-compose.yml` با سه سرویس برای یک اپ جدی:

```yaml
services:
  db:
    image: postgres:18
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine

  adminer:
    image: adminer
    ports:
      - "8081:8080"

volumes:
  pgdata:
```

چیزهای جدید این فایل:

| مفهوم | کار |
|---|---|
| `healthcheck` | داکر خودش چک می‌کنه db «واقعاً» آماده است (`pg_isready`) — و `depends_on: condition: service_healthy` می‌تونه بهش تکیه کنه! |
| `adminer` | یک GUI وب برای دیتابیس — باز کن `localhost:8081` |
| `${DB_PASSWORD}` | از فایل `.env` کنار compose می‌آید (فصل ۸) |

بزن `docker compose up -d` — سه سرویس: دیتابیس نسخه‌دار + ماندگار، ردیس، و یک داشبورد گرافیکی. به این می‌گن **محیط توسعه‌ی خودتمون‌شده** 😎

## ✅ جمع‌بندی فصل

- الگوی رایج: دیتابیس/سرویس‌ها داکری، اپ لوکال با hot-reload
- استارت یک پروژه‌ی تیمی: clone → compose up → migrate → dev
- `exec db psql` = ابزارهای داخل کانتینر؛ `down -v` = ریست کامل توسعه
- healthcheck = «واقعاً آماده»؛ پورت‌ها فقط برای میزبان (`127.0.0.1:`)

## 📝 تمرین فصل ۱۱

1. استک دو‌سرویسه (دیتابیس در داکر + برنامه لوکال) را کامل راه بینداز — دستورات migration را اجرا کن و صفحه اول برنامه را تست کن.
2. ریست کامل توسعه: `down -v` → up → `prisma migrate dev` → داده‌ی اولیه (seed) را تزریق کن (`prisma db seed`).
3. Adminer را بالا بیاور و با آن به دیتابیس وصل شو (`host: db` یا از سیستم: `localhost:5432`؟ هر دو را تست کن!).
4. healthcheck را اضافه کن و `docker compose ps` بزن — ستون health را ببین (starting → healthy).
5. فایل‌های `compose.yaml` و `.env.example` را در پروژه کامیت کن (پیام: `chore: add docker compose dev stack`) و به مخزن push کن.

<details><summary>نکته تمرین ۳</summary>

Adminer داخل کانتینر است؛ `host` اش باید `db` باشد (همان شبکه compose) — از سیستم هم `localhost:5432` کار می‌کند چون پورت مپ شده. دو مسیر، دو زاویه — همان فصل ۱۰!
</details>

➡️ **فصل بعد:** از محیط لوکال تا پروداکشن — push ایمیج و دپلوی روی سرور.
