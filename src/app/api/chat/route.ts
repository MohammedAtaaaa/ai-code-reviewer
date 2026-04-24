import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { getOpenAIClient } from "@/lib/openai/client";
import { GRANDMOTHER_SYSTEM_PROMPT } from "@/constants";

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

  const { message, history } = (await request.json()) as {
    message: string;
    history: { role: "user" | "assistant"; content: string }[];
  };

  if (!message?.trim()) {
    return NextResponse.json(
      { error: "اكتب حاجة يا حبيبي" },
      { status: 400 }
    );
  }

  // Search for relevant wisdom from the database
  const { data: relevantWisdoms } = await supabase
    .from("wisdoms")
    .select("content, category, ai_comment")
    .textSearch("content", message.split(" ").join(" | "), { type: "plain" })
    .limit(3);

  let contextPrompt = GRANDMOTHER_SYSTEM_PROMPT;

  if (relevantWisdoms && relevantWisdoms.length > 0) {
    contextPrompt += "\n\nحكم من قاعدة البيانات ممكن تفيدك في الرد:\n";
    relevantWisdoms.forEach((w) => {
      contextPrompt += `- ${w.content} (${w.category})\n`;
    });
  }

  const openai = getOpenAIClient();

  const messages: { role: "system" | "user" | "assistant"; content: string }[] =
    [
      { role: "system", content: contextPrompt },
      ...history.slice(-10),
      { role: "user", content: message },
    ];

  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages,
      temperature: 0.8,
      max_tokens: 500,
    });

    const reply = response.choices[0]?.message?.content || "معلش يا حبيبي، جربي تاني";

    return NextResponse.json({ reply });
  } catch {
    return NextResponse.json(
      { error: "الجدة مش قادرة ترد دلوقتي يا حبيبي، جرب تاني" },
      { status: 500 }
    );
  }
}
