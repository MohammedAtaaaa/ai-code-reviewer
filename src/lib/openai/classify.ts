import { getOpenAIClient } from "./client";
import { WISDOM_CLASSIFICATION_PROMPT } from "@/constants";
import type { WisdomAIResponse, WisdomCategory } from "@/types";

const VALID_CATEGORIES: WisdomCategory[] = [
  "وصفات",
  "علاجات شعبية",
  "أمثال",
  "نصائح حياتية",
  "حكايات",
  "حكم أخرى",
];

export async function classifyWisdom(
  content: string
): Promise<WisdomAIResponse> {
  const openai = getOpenAIClient();

  const response = await openai.chat.completions.create({
    model: "gpt-4o",
    messages: [
      { role: "system", content: WISDOM_CLASSIFICATION_PROMPT },
      { role: "user", content },
    ],
    response_format: { type: "json_object" },
    temperature: 0.7,
  });

  const text = response.choices[0]?.message?.content;
  if (!text) {
    throw new Error("فشل في تصنيف الحكمة");
  }

  const parsed = JSON.parse(text) as {
    category: string;
    ai_modern_version: string;
    ai_comment: string;
  };

  const category = VALID_CATEGORIES.includes(parsed.category as WisdomCategory)
    ? (parsed.category as WisdomCategory)
    : "حكم أخرى";

  return {
    category,
    ai_modern_version: parsed.ai_modern_version,
    ai_comment: parsed.ai_comment,
  };
}
