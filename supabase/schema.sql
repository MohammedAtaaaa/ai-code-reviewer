-- سر الجدة (Sir El Gedda) - Database Schema
-- Run this in the Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Categories table
CREATE TABLE IF NOT EXISTS categories (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

-- Insert default categories
INSERT INTO categories (name) VALUES
  ('وصفات'),
  ('علاجات شعبية'),
  ('أمثال'),
  ('نصائح حياتية'),
  ('حكايات'),
  ('حكم أخرى')
ON CONFLICT (name) DO NOTHING;

-- Wisdoms table
CREATE TABLE IF NOT EXISTS wisdoms (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('text', 'voice')),
  content TEXT NOT NULL,
  audio_url TEXT,
  category TEXT NOT NULL,
  city TEXT,
  ai_modern_version TEXT,
  ai_comment TEXT,
  likes_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Comments table
CREATE TABLE IF NOT EXISTS comments (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  wisdom_id UUID REFERENCES wisdoms(id) ON DELETE CASCADE NOT NULL,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User collections (saved wisdoms)
CREATE TABLE IF NOT EXISTS user_collections (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  wisdom_id UUID REFERENCES wisdoms(id) ON DELETE CASCADE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, wisdom_id)
);

-- Likes table (for tracking individual likes)
CREATE TABLE IF NOT EXISTS wisdom_likes (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  wisdom_id UUID REFERENCES wisdoms(id) ON DELETE CASCADE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, wisdom_id)
);

-- Reports table
CREATE TABLE IF NOT EXISTS reports (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  wisdom_id UUID REFERENCES wisdoms(id) ON DELETE CASCADE NOT NULL,
  reason TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_wisdoms_user_id ON wisdoms(user_id);
CREATE INDEX IF NOT EXISTS idx_wisdoms_category ON wisdoms(category);
CREATE INDEX IF NOT EXISTS idx_wisdoms_city ON wisdoms(city);
CREATE INDEX IF NOT EXISTS idx_wisdoms_created_at ON wisdoms(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_comments_wisdom_id ON comments(wisdom_id);
CREATE INDEX IF NOT EXISTS idx_user_collections_user_id ON user_collections(user_id);
CREATE INDEX IF NOT EXISTS idx_wisdom_likes_wisdom_id ON wisdom_likes(wisdom_id);

-- Full text search index for wisdoms
CREATE INDEX IF NOT EXISTS idx_wisdoms_content_search ON wisdoms USING GIN (to_tsvector('arabic', content));

-- Row Level Security (RLS)
ALTER TABLE wisdoms ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_collections ENABLE ROW LEVEL SECURITY;
ALTER TABLE wisdom_likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- Wisdoms policies
CREATE POLICY "Anyone can read wisdoms" ON wisdoms
  FOR SELECT USING (true);

CREATE POLICY "Authenticated users can create wisdoms" ON wisdoms
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own wisdoms" ON wisdoms
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own wisdoms" ON wisdoms
  FOR DELETE USING (auth.uid() = user_id);

-- Comments policies
CREATE POLICY "Anyone can read comments" ON comments
  FOR SELECT USING (true);

CREATE POLICY "Authenticated users can create comments" ON comments
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own comments" ON comments
  FOR DELETE USING (auth.uid() = user_id);

-- User collections policies
CREATE POLICY "Users can read their own collections" ON user_collections
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can add to their collections" ON user_collections
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can remove from their collections" ON user_collections
  FOR DELETE USING (auth.uid() = user_id);

-- Likes policies
CREATE POLICY "Anyone can read likes" ON wisdom_likes
  FOR SELECT USING (true);

CREATE POLICY "Authenticated users can like" ON wisdom_likes
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can unlike" ON wisdom_likes
  FOR DELETE USING (auth.uid() = user_id);

-- Reports policies
CREATE POLICY "Users can create reports" ON reports
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Function to update likes count
CREATE OR REPLACE FUNCTION update_likes_count()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE wisdoms SET likes_count = likes_count + 1 WHERE id = NEW.wisdom_id;
    RETURN NEW;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE wisdoms SET likes_count = likes_count - 1 WHERE id = OLD.wisdom_id;
    RETURN OLD;
  END IF;
END;
$$ LANGUAGE plpgsql;

-- Trigger for likes count
DROP TRIGGER IF EXISTS trigger_update_likes_count ON wisdom_likes;
CREATE TRIGGER trigger_update_likes_count
AFTER INSERT OR DELETE ON wisdom_likes
FOR EACH ROW
EXECUTE FUNCTION update_likes_count();

-- Storage bucket for audio files
-- Note: Run this in Supabase Dashboard > Storage
-- Create a bucket called "wisdom-audio" with public access
