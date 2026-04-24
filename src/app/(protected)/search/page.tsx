import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";

export default function SearchPage() {
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center py-4">
        <h1 className="text-3xl font-bold text-primary">🔍 دور على حكمة</h1>
        <p className="text-muted-foreground mt-2">
          اسأل الجدة عن أي حاجة عايز تعرفها
        </p>
      </div>

      <div className="flex gap-2">
        <Input
          placeholder="ابحث... مثلاً: علاج البرد، وصفة كشري"
          className="flex-1 py-6 text-base"
        />
        <button className="h-12 w-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center hover:bg-primary/90 transition-colors">
          🎤
        </button>
      </div>

      <Card className="border-border/50">
        <CardContent className="p-8 text-center text-muted-foreground">
          <div className="text-5xl mb-4">🔍</div>
          <p className="text-lg">ابحث عن حكمة أو اسأل الجدة بصوتك</p>
          <p className="text-sm mt-2">
            &ldquo;اسأل الجدة عن علاج البرد&rdquo;
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
