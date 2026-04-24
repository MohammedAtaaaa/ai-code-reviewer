import { Card, CardContent } from "@/components/ui/card";

export default function MapPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center py-4">
        <h1 className="text-3xl font-bold text-primary">🗺️ خريطة الجدات</h1>
        <p className="text-muted-foreground mt-2">
          اكتشف حكم وأسرار من كل محافظات مصر
        </p>
      </div>

      <Card className="border-border/50">
        <CardContent className="p-12 text-center text-muted-foreground">
          <div className="text-6xl mb-4">🗺️</div>
          <p className="text-xl font-semibold">الخريطة قريباً إن شاء الله</p>
          <p className="text-sm mt-2">
            هنا هتقدر تشوف حكم الجدات من كل مكان في مصر
          </p>
          <div className="grid grid-cols-3 md:grid-cols-5 gap-3 mt-8">
            {[
              "القاهرة",
              "الإسكندرية",
              "الجيزة",
              "أسوان",
              "الأقصر",
              "المنصورة",
              "طنطا",
              "دمياط",
              "بورسعيد",
              "السويس",
            ].map((city) => (
              <div
                key={city}
                className="bg-secondary rounded-lg p-3 text-sm text-secondary-foreground"
              >
                📍 {city}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
