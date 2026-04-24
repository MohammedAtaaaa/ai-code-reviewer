import Link from "next/link";
import { Button } from "@/components/ui/button";
import { CATEGORIES } from "@/constants";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#f5e6d3] via-[#faf0e6] to-[#f5e6d3]">
      {/* Header */}
      <header className="container mx-auto px-4 py-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-primary">🧓 سر الجدة</h1>
        <div className="flex gap-3">
          <Link href="/login">
            <Button variant="ghost" className="text-primary hover:bg-primary/10">
              تسجيل الدخول
            </Button>
          </Link>
          <Link href="/register">
            <Button className="bg-primary hover:bg-primary/90">
              ابدأ الحكمة
            </Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-3xl mx-auto">
          <div className="text-7xl mb-6">🧓</div>
          <h2 className="text-4xl md:text-6xl font-extrabold text-primary mb-6 leading-tight">
            سر الجدة...
            <br />
            <span className="text-accent">حكمة زمان بصوت دلوقتي</span>
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground mb-10 leading-relaxed">
            يا حبيبي، الجدات عندهم كنوز من الحكمة والمعرفة. وصفات أكل، علاجات
            شعبية، أمثال من زمان، ونصائح حياتية مالهاش مثيل. هنا بنحفظ كل ده
            عشان ما يتنسيش.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register">
              <Button
                size="lg"
                className="text-lg px-8 py-6 bg-primary hover:bg-primary/90 shadow-lg"
              >
                ابدأ الحكمة ✨
              </Button>
            </Link>
            <Link href="/login">
              <Button
                size="lg"
                variant="outline"
                className="text-lg px-8 py-6 border-primary text-primary hover:bg-primary/10"
              >
                ادخل عالم الجدة 🏠
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="container mx-auto px-4 py-16">
        <h3 className="text-3xl font-bold text-center text-primary mb-12">
          حكمة الجدة فيها إيه؟
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {CATEGORIES.map((cat) => (
            <div
              key={cat.value}
              className="bg-card/80 backdrop-blur-sm border border-border rounded-2xl p-6 text-center hover:shadow-lg hover:scale-105 transition-all duration-300"
            >
              <div className="text-4xl mb-3">{cat.emoji}</div>
              <h4 className="text-lg font-semibold text-card-foreground">
                {cat.label}
              </h4>
            </div>
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto grid md:grid-cols-3 gap-8">
          <div className="text-center p-6">
            <div className="text-4xl mb-4">🎤</div>
            <h4 className="text-xl font-bold text-primary mb-2">
              قول زي الجدة
            </h4>
            <p className="text-muted-foreground">
              سجل حكمة الجدة بصوتك وإحنا هنكتبها ونصنفها بالذكاء الاصطناعي
            </p>
          </div>
          <div className="text-center p-6">
            <div className="text-4xl mb-4">🤖</div>
            <h4 className="text-xl font-bold text-primary mb-2">
              اسأل الجدة
            </h4>
            <p className="text-muted-foreground">
              شات مع جدة مصرية ذكية بتعرف كل حاجة عن الأكل والعلاج والحكم
            </p>
          </div>
          <div className="text-center p-6">
            <div className="text-4xl mb-4">🗺️</div>
            <h4 className="text-xl font-bold text-primary mb-2">
              خريطة الجدات
            </h4>
            <p className="text-muted-foreground">
              اكتشف حكم وأسرار من كل محافظات مصر على الخريطة
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 text-center border-t border-border">
        <p className="text-muted-foreground">
          🧓 سر الجدة - حكمة زمان بصوت دلوقتي &copy; {new Date().getFullYear()}
        </p>
        <p className="text-sm text-muted-foreground mt-2">
          ربنا يكرمك يا حبيبي ❤️
        </p>
      </footer>
    </div>
  );
}
