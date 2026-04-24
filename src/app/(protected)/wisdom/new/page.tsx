"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EGYPTIAN_CITIES } from "@/constants";
import { toast } from "sonner";
function CitySelect({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
    >
      <option value="">اختار المحافظة (اختياري)</option>
      {EGYPTIAN_CITIES.map((city) => (
        <option key={city} value={city}>
          {city}
        </option>
      ))}
    </select>
  );
}

export default function NewWisdomPage() {
  const [content, setContent] = useState("");
  const [city, setCity] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleVoiceToggle = async () => {
    if (isRecording) {
      setIsRecording(false);
      toast.info("تم إيقاف التسجيل");
    } else {
      try {
        setIsRecording(true);
        toast.info("🎤 التسجيل شغال... قول الحكمة يا حبيبي");
      } catch {
        toast.error("مش قادر أفتح المايك يا حبيبي");
        setIsRecording(false);
      }
    }
  };

  const handleSubmit = async () => {
    if (!content.trim() && !audioBlob) {
      toast.error("يا حبيبي اكتب الحكمة أو سجلها بصوتك");
      return;
    }

    setSubmitting(true);
    try {
      toast.success("تمام يا حبيبي! الحكمة اتبعتت والذكاء الاصطناعي هيصنفها");
      setContent("");
      setAudioBlob(null);
      setCity("");
    } catch {
      toast.error("في مشكلة يا حبيبي، جرب تاني");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto">
      <Card className="border-border/50 shadow-lg">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl text-primary">
            شارك حكمة الجدة ✨
          </CardTitle>
          <p className="text-muted-foreground">
            يا حبيبي قول الحكمة اللي عندك أو سجلها بصوتك
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Text Input */}
          <div className="space-y-2">
            <Textarea
              placeholder="اكتب حكمة الجدة هنا... مثلاً: الأكل في الجنة يبقى في البطن"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="min-h-[120px] text-base resize-none"
            />
          </div>

          {/* Voice Recording */}
          <div className="text-center">
            <p className="text-sm text-muted-foreground mb-3">أو</p>
            <Button
              type="button"
              variant={isRecording ? "destructive" : "outline"}
              size="lg"
              className="rounded-full h-16 w-16 text-2xl"
              onClick={handleVoiceToggle}
            >
              {isRecording ? "⏹️" : "🎤"}
            </Button>
            <p className="text-sm text-muted-foreground mt-2">
              {isRecording ? "اضغط عشان توقف" : "قول زي الجدة 🎤"}
            </p>
            {audioBlob && (
              <div className="mt-3 p-3 bg-secondary rounded-lg">
                <p className="text-sm text-secondary-foreground">
                  تم التسجيل بنجاح 🎵
                </p>
              </div>
            )}
          </div>

          {/* City Selection */}
          <CitySelect value={city} onChange={setCity} />

          {/* Submit */}
          <Button
            onClick={handleSubmit}
            disabled={submitting || (!content.trim() && !audioBlob)}
            className="w-full py-6 text-lg bg-primary hover:bg-primary/90"
          >
            {submitting ? "بنبعت الحكمة..." : "ابعت الحكمة 🧓"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
