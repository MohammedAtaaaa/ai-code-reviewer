"use client";

import { useAuth } from "@/hooks/useAuth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

export default function ProfilePage() {
  const { user, loading, signOut } = useAuth();

  if (loading) {
    return (
      <div className="max-w-md mx-auto space-y-4 mt-8">
        <Skeleton className="h-32 w-full rounded-lg" />
        <Skeleton className="h-8 w-3/4" />
        <Skeleton className="h-8 w-1/2" />
      </div>
    );
  }

  const fullName = user?.user_metadata?.full_name || "مستخدم";
  const email = user?.email || "";
  const initial = fullName.charAt(0);

  return (
    <div className="max-w-md mx-auto">
      <Card className="border-border/50 shadow-lg">
        <CardHeader className="text-center">
          <Avatar className="h-20 w-20 mx-auto mb-4">
            <AvatarFallback className="bg-primary text-primary-foreground text-3xl">
              {initial}
            </AvatarFallback>
          </Avatar>
          <CardTitle className="text-2xl text-primary">{fullName}</CardTitle>
          <p className="text-muted-foreground" dir="ltr">
            {email}
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="bg-secondary rounded-lg p-3">
              <p className="text-2xl font-bold text-primary">0</p>
              <p className="text-xs text-muted-foreground">حكمة</p>
            </div>
            <div className="bg-secondary rounded-lg p-3">
              <p className="text-2xl font-bold text-primary">0</p>
              <p className="text-xs text-muted-foreground">إعجاب</p>
            </div>
            <div className="bg-secondary rounded-lg p-3">
              <p className="text-2xl font-bold text-primary">0</p>
              <p className="text-xs text-muted-foreground">محفوظ</p>
            </div>
          </div>

          <Button
            variant="outline"
            className="w-full border-destructive text-destructive hover:bg-destructive/10"
            onClick={signOut}
          >
            تسجيل خروج
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
