import { Card, CardContent } from "@/components/ui/card";
import { CATEGORIES } from "@/constants";

export default function FeedPage() {
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center py-4">
        <h1 className="text-3xl font-bold text-primary">حكم الجدات 📜</h1>
        <p className="text-muted-foreground mt-2">
          يا حبيبي اتفضل شوف حكم وأسرار الجدات
        </p>
      </div>

      {/* Category Filters */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        <button className="shrink-0 px-4 py-2 rounded-full bg-primary text-primary-foreground text-sm font-medium">
          الكل
        </button>
        {CATEGORIES.map((cat) => (
          <button
            key={cat.value}
            className="shrink-0 px-4 py-2 rounded-full bg-secondary text-secondary-foreground text-sm font-medium hover:bg-primary/10 transition-colors"
          >
            {cat.emoji} {cat.label}
          </button>
        ))}
      </div>

      {/* Placeholder Cards */}
      <div className="space-y-4">
        <Card className="border-border/50">
          <CardContent className="p-6 text-center text-muted-foreground">
            <div className="text-5xl mb-4">🧓</div>
            <p className="text-lg">
              لسه مفيش حكم هنا يا حبيبي
            </p>
            <p className="text-sm mt-2">
              كن أول واحد يشارك حكمة الجدة!
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
