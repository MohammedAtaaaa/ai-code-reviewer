export type WisdomCategory =
  | "وصفات"
  | "علاجات شعبية"
  | "أمثال"
  | "نصائح حياتية"
  | "حكايات"
  | "حكم أخرى";

export type WisdomType = "text" | "voice";

export interface Wisdom {
  id: string;
  user_id: string;
  type: WisdomType;
  content: string;
  audio_url: string | null;
  category: WisdomCategory;
  city: string | null;
  ai_modern_version: string | null;
  ai_comment: string | null;
  likes_count: number;
  created_at: string;
  user?: UserProfile;
  is_liked?: boolean;
  is_saved?: boolean;
}

export interface Category {
  id: string;
  name: WisdomCategory;
}

export interface Comment {
  id: string;
  wisdom_id: string;
  user_id: string;
  content: string;
  created_at: string;
  user?: UserProfile;
}

export interface UserCollection {
  id: string;
  user_id: string;
  wisdom_id: string;
  created_at: string;
  wisdom?: Wisdom;
}

export interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export interface WisdomAIResponse {
  category: WisdomCategory;
  ai_modern_version: string;
  ai_comment: string;
  transcription?: string;
}
