import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { classifyWisdom } from "@/lib/openai/classify";
import { transcribeAudio } from "@/lib/openai/transcribe";

export async function GET(request: Request) {
  const supabase = await createClient();
  const { searchParams } = new URL(request.url);

  const category = searchParams.get("category");
  const page = parseInt(searchParams.get("page") || "1");
  const limit = parseInt(searchParams.get("limit") || "20");
  const offset = (page - 1) * limit;

  let query = supabase
    .from("wisdoms")
    .select("*", { count: "exact" })
    .order("created_at", { ascending: false })
    .range(offset, offset + limit - 1);

  if (category) {
    query = query.eq("category", category);
  }

  const { data, error, count } = await query;

  if (error) {
    return NextResponse.json(
      { error: "مشكلة في جلب الحكم يا حبيبي" },
      { status: 500 }
    );
  }

  return NextResponse.json({
    wisdoms: data,
    total: count,
    page,
    limit,
  });
}

export async function POST(request: Request) {
  const supabase = await createClient();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json(
      { error: "لازم تسجل دخول الأول يا حبيبي" },
      { status: 401 }
    );
  }

  const formData = await request.formData();
  const content = formData.get("content") as string | null;
  const audioFile = formData.get("audio") as File | null;
  const city = formData.get("city") as string | null;

  let wisdomContent = content || "";
  let audioUrl: string | null = null;
  let wisdomType: "text" | "voice" = "text";

  // Handle voice upload
  if (audioFile) {
    wisdomType = "voice";
    const buffer = Buffer.from(await audioFile.arrayBuffer());

    // Upload to Supabase Storage
    const fileName = `${user.id}/${Date.now()}.webm`;
    const { error: uploadError } = await supabase.storage
      .from("wisdom-audio")
      .upload(fileName, buffer, {
        contentType: "audio/webm",
      });

    if (uploadError) {
      return NextResponse.json(
        { error: "مشكلة في رفع الصوت يا حبيبي" },
        { status: 500 }
      );
    }

    const {
      data: { publicUrl },
    } = supabase.storage.from("wisdom-audio").getPublicUrl(fileName);
    audioUrl = publicUrl;

    // Transcribe audio
    try {
      wisdomContent = await transcribeAudio(buffer, audioFile.name);
    } catch {
      return NextResponse.json(
        { error: "مشكلة في تحويل الصوت لكتابة" },
        { status: 500 }
      );
    }
  }

  if (!wisdomContent.trim()) {
    return NextResponse.json(
      { error: "لازم تكتب حكمة أو تسجلها بصوتك يا حبيبي" },
      { status: 400 }
    );
  }

  // AI Classification
  let aiResponse;
  try {
    aiResponse = await classifyWisdom(wisdomContent);
  } catch {
    aiResponse = {
      category: "حكم أخرى" as const,
      ai_modern_version: null,
      ai_comment: null,
    };
  }

  // Save to database
  const { data, error } = await supabase
    .from("wisdoms")
    .insert({
      user_id: user.id,
      type: wisdomType,
      content: wisdomContent,
      audio_url: audioUrl,
      category: aiResponse.category,
      city: city || null,
      ai_modern_version: aiResponse.ai_modern_version,
      ai_comment: aiResponse.ai_comment,
      likes_count: 0,
    })
    .select()
    .single();

  if (error) {
    return NextResponse.json(
      { error: "مشكلة في حفظ الحكمة يا حبيبي" },
      { status: 500 }
    );
  }

  return NextResponse.json({ wisdom: data }, { status: 201 });
}
