# فصل ۷ — ایمیج تمیز: multi-stage و کاهش حجم

> 🎯 **هدف:** Dockerfile فصل ۶ کار می‌کنه ولی «مبتدیانه» است. یاد می‌گیری چرا ایمیج‌های Node معمولی چاق‌ان، و با **multi-stage build** اون‌ها رو به ایمیج‌های تمیز production تبدیل کنی — همون چیزی که در Dockerfile های شرکت‌ها می‌بینی.

---

## ۷.۱ — مشکل: ایمیج من چرا اینقدر چاقه؟

ایمیج `myapi` فصل قبل ۱۳۲MB بود برای یک API ده‌خطی! چرا؟ چون **همه‌چیز تو اونه:**

| چی داخلشه | حجم | ولی برای اجرا لازمه؟ |
|---|---|---|
| لایه پایه alpine + Node | ~۱۲۰MB | ✅ بله |
| npm cache (باگ یا نه، npm کش می‌سازه) | ده‌ها MB | ❌ نه |
| node_modules شامل devDependencies | عظیم | ❌ نه — فقط برای build/test |
| کد سورس کامل | کم | ⚠️ در production فقط خروجی build لازمه |

و برای Next.js بدتر: در build به همه devDependencies نیاز داری، ولی برای *اجرا* فقط خروجی `.next` + وابستگی‌های production لازمه.

## ۷.۲ — راه‌حل: Multi-Stage Build ⭐

فکرش ساده‌ست: **دو مرحله — یکی برای build (می‌تونه چاق باشه)، یکی برای اجرا (فقط خروجی رو می‌بره).**

```dockerfile
# ─── مرحله ۱: build (ابزارهای سنگین اینجاست) ───
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# ─── مرحله ۲: production (فقط خروجی) ───
FROM node:22-alpine
WORKDIR /app

COPY package*.json ./
RUN npm install --omit=dev && npm cache clean --force

COPY --from=builder /app/dist ./dist

EXPOSE 3000
CMD ["node", "dist/server.js"]
```

خط به خط چیزهای جدید:

| دستور | کار |
|---|---|
| `AS builder` | اسم‌گذاری مرحله اول |
| `npm install --omit=dev` | فقط وابستگی‌های production (بدون devDependencies مثل TypeScript و eslint) |
| `npm cache clean --force` | حذف کش npm از همون لایه — جلوگیری از قچاق شدن ایمیج |
| `COPY --from=builder /app/dist ./dist` | ⭐ جادو: فقط پوشه خروجی رو از مرحله build بکش بیرون |

نتیجه: مرحله builder (با typescript، eslint، کش‌ها و...) **دور انداخته می‌شه** — ایمیج نهایی فقط runtime است. حجم معمولاً از صدها مگ به ده‌ها مگ می‌رسه (۳-۵ برابر کوچیک‌تر).

> 🔑 چرا امن‌تر هم هست؟ چون سورس کامل، devDependencies و ابزارهای build تو ایمیج نهایی نیستن — سطح حمله کمتر. (این جمله رو در مصاحبه بگو، امتیاز می‌گیری 😄)

## ۷.۳ — Next.js واقعی (الگوی رسمی)

الگوی multi-stage برای Next.js (که خود Next.js در مستنداتش هم می‌ده — با `output: "standalone"` در next.config):

```dockerfile
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
```

+ `npm ci` به جای `npm install`: نصب دقیق از `package-lock.json` — سریع‌تر و تکرارپذیر (مثل قفل شدن نسخه‌ها).

## ۷.۴ — چند قانون طلایی حجم

| قانون | چرا |
|---|---|
| پایه alpine/slim | پایه ۱۲۰MB → ۵۰MB |
| `RUN` های مرتبط رو با `&&` یکی کن | هر RUN یک لایه — لایه حذف‌شده فضا آزاد نمی‌کنه! |
| `npm cache clean` در **همین** RUN | فایل اضافه‌شده در لایه قبلی، در لایه بعد پاک نمی‌شه |
| `npm ci --omit=dev` در آخرین مرحله | devDependencies نریز |
| چند stage در صورت نیاز | فایل‌های build از ایمیج نهایی بیرون می‌مونن |

نمونه‌ی قانون «یکی‌کردن RUN»:

```dockerfile
# ❌ کش npm در لایه قبلی می‌ماند:
RUN npm install
RUN npm cache clean --force

# ✅ همه در یک لایه — پاک‌سازی داخل همان لایه:
RUN npm install --omit=dev && npm cache clean --force
```

## ۷.۵ — measure: چطوری بفهمم چقدر لاغر شد؟

```bash
$ docker build -t myapi:2.0 .
$ docker images myapi
myapi   1.0   ...   132MB      ← نسخه تک‌مرحله‌ای
myapi   2.0   ...   96MB       ← بعد از multi-stage + omit=dev

# جزئیات لایه به لایه:
$ docker history myapi:2.0
```

و ابزار تحلیل حرفه‌ای: `dive` (github.com/wagoodman/dive) — داخل ایمیج رو لایه‌به‌لایه نشون می‌ده و می‌گه چه چیزی هدر رفته. (فعلاً فقط اسمش رو بدونی کافیه.)

---

## ✅ جمع‌بندی فصل

- ایمیج چاق = ابزارهای build + devDeps + کش‌ها داخل ایمیج نهایی
- **Multi-stage:** مرحله builder (چاق، دور انداخته می‌شود) → مرحله final (فقط خروجی + runtime)
- `COPY --from=builder` = انتقال فقط خروجی؛ `npm ci --omit=dev` = فقط production deps
- پاک‌سازی باید **داخل همان RUN** باشد (لایه‌ها فقط‌خواندن‌اند)
- حجم کمتر = دپلوی سریع‌تر + سطح حمله کمتر

## 📝 تمرین فصل ۷

1. Dockerfile فصل ۶ را به multi-stage تبدیل کن (حتی اگر اپ build ندارد — یک مرحله deps و یک مرحله runtime با `--omit=dev`) و فرق حجم را با `docker images` ببین.
2. در Dockerfile، دو `RUN` پشت هم بنویس (نصب + پاک‌سازی جدا) و بعد `docker history` بزن — لایه پاک‌سازی را پیدا کن. چرا SIZE اش 0 یا کم است ولی فضا آزاد نشده؟ (جواب: فایل‌های حذف‌شده در لایه قبلی زنده‌ان!)
3. `npm ci` رو جایگزین `npm install` کن — اگه package-lock نداری، اول یک بار `npm install` لوکال بزن تا ساخته شه.
4. چالش: Dockerfile مربوط به Next.js در بخش ۷.۳ را روی یک پروژه Next.js امتحان کن (`output: 'standalone'` را به `next.config.js` اضافه کن) و تغییر حجم ایمیج را بررسی کن.

<details><summary>جواب تمرین ۲</summary>

لایه‌ها فقط‌خواندنی و انباشته‌اند: اگر در لایه ۱ فایل ۱۰۰MB بسازی و در لایه ۲ حذفش کنی، فایل در لایه ۱ هنوز هست — ایمیج نهایی هر دو لایه را حمل می‌کند (فقط دیده نمی‌شود). پاک‌سازی باید در همان لایه‌ای انجام شود که فایل ساخته شده (با `&&`).
</details>

➡️ **فصل بعد:** وقتی چند کانتینر لازم داری (اپ + دیتابیس + ...) — Docker Compose!
