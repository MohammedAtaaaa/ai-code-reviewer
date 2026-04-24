# 🧓 سر الجدة (Sir El Gedda - Grandmother's Secret)

منصة مصرية لحفظ حكم وأسرار الجدات — وصفات أكل، علاجات شعبية، أمثال، نصائح حياتية، وحكايات من زمان.

> حكمة زمان بصوت دلوقتي ✨

## المميزات

- 🍲 **وصفات** — وصفات الأكل المصري من الجدات
- 🌿 **علاجات شعبية** — وصفات طبيعية وعلاجات من زمان
- 🧾 **أمثال** — أمثال شعبية مصرية
- 👨‍👩‍👧 **نصائح حياتية** — نصائح في التربية والحياة
- 📖 **حكايات** — قصص وحكايات من الجدات
- 🏠 **حكم أخرى** — حكم متنوعة

### الخصائص التقنية

- 🎤 تسجيل صوتي وتحويل لنص (Whisper API)
- 🤖 تصنيف تلقائي بالذكاء الاصطناعي (GPT-4o)
- 🧓 شات مع جدة مصرية ذكية
- 🗺️ خريطة الجدات — حكم من كل محافظات مصر
- ❤️ إعجاب وتعليقات وحفظ
- 🔍 بحث نصي وصوتي
- 📱 تصميم متجاوب (Mobile-First)
- 🌐 دعم كامل للـ RTL

## التقنيات

- **Next.js 15** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **shadcn/ui**
- **Supabase** (Auth, Database, Storage, Realtime)
- **OpenAI GPT-4o** + **Whisper API**
- **Web Speech API**

## البدء السريع

```bash
# Clone
git clone https://github.com/MohammedAtaaaa/ai-code-reviewer.git
cd ai-code-reviewer
git checkout devin/1777069288-sir-el-gedda

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with your Supabase and OpenAI keys

# Run the database schema
# Copy contents of supabase/schema.sql to Supabase SQL Editor

# Run dev server
npm run dev
```

## البنية

```
src/
├── app/
│   ├── (auth)/          # Login & Register
│   ├── (protected)/     # Authenticated routes
│   │   ├── feed/        # Wisdom feed
│   │   ├── wisdom/new/  # Submit wisdom
│   │   ├── chat/        # AI grandmother chatbot
│   │   ├── search/      # Search
│   │   ├── map/         # Map of grandmothers
│   │   ├── admin/       # Admin panel
│   │   └── profile/     # User profile
│   └── api/             # API routes
├── components/
│   ├── layout/          # Navbar, etc.
│   └── ui/              # shadcn/ui components
├── lib/
│   ├── supabase/        # Supabase client/server/middleware
│   ├── openai/          # OpenAI client, classify, transcribe
│   └── voice/           # Voice recorder
├── hooks/               # React hooks
├── types/               # TypeScript types
└── constants/           # App constants & AI prompts
```

## قاعدة البيانات

- `wisdoms` — الحكم والأسرار
- `categories` — التصنيفات
- `comments` — التعليقات
- `user_collections` — الحكم المحفوظة
- `wisdom_likes` — الإعجابات
- `reports` — البلاغات

## المتغيرات البيئية

| المتغير | الوصف |
|---------|-------|
| `NEXT_PUBLIC_SUPABASE_URL` | رابط مشروع Supabase |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | مفتاح Supabase العام |
| `OPENAI_API_KEY` | مفتاح OpenAI API |

## الترخيص

MIT
