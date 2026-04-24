import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AdminPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center py-4">
        <h1 className="text-3xl font-bold text-primary">⚙️ لوحة التحكم</h1>
        <p className="text-muted-foreground mt-2">
          إدارة المحتوى والمستخدمين
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <Card className="border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">الحكم المعلقة</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-primary">0</p>
            <p className="text-sm text-muted-foreground">في انتظار المراجعة</p>
          </CardContent>
        </Card>
        <Card className="border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">المستخدمين</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-primary">0</p>
            <p className="text-sm text-muted-foreground">مستخدم مسجل</p>
          </CardContent>
        </Card>
        <Card className="border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">إجمالي الحكم</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-primary">0</p>
            <p className="text-sm text-muted-foreground">حكمة منشورة</p>
          </CardContent>
        </Card>
      </div>

      <Card className="border-border/50">
        <CardContent className="p-8 text-center text-muted-foreground">
          <div className="text-5xl mb-4">⚙️</div>
          <p className="text-lg">لوحة التحكم الكاملة قريباً إن شاء الله</p>
        </CardContent>
      </Card>
    </div>
  );
}
