-- ============================================================
-- Embrace My Faith — Supabase Schema
-- Run this entire file in the Supabase SQL editor
-- ============================================================

-- PROFILES
create table if not exists public.profiles (
  id uuid references auth.users on delete cascade primary key,
  name text,
  gender text default 'female',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
alter table public.profiles enable row level security;
create policy "profiles_all" on public.profiles for all using (auth.uid() = id) with check (auth.uid() = id);

-- PRAYER COUNTERS (daily limit, resets each day)
create table if not exists public.prayer_counters (
  user_id uuid references auth.users on delete cascade primary key,
  count integer default 0,
  reset_date date default current_date,
  updated_at timestamptz default now()
);
alter table public.prayer_counters enable row level security;
create policy "counters_all" on public.prayer_counters for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- PRAYERS
create table if not exists public.prayers (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users on delete cascade not null,
  prayer_for text,
  prayer_text text not null,
  scripture text,
  tone text,
  created_at timestamptz default now()
);
alter table public.prayers enable row level security;
create policy "prayers_all" on public.prayers for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- MOMENTS
create table if not exists public.moments (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users on delete cascade not null,
  name text not null,
  category text,
  date text,
  note text,
  created_at timestamptz default now()
);
alter table public.moments enable row level security;
create policy "moments_all" on public.moments for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- RISE PREFERENCES
create table if not exists public.rise_preferences (
  user_id uuid references auth.users on delete cascade primary key,
  wake_time text default '6:30 AM',
  option_selected text,
  gender text default 'female',
  worship_song text,
  updated_at timestamptz default now()
);
alter table public.rise_preferences enable row level security;
create policy "rise_all" on public.rise_preferences for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- REST PREFERENCES
create table if not exists public.rest_preferences (
  user_id uuid references auth.users on delete cascade primary key,
  option_selected text,
  gender text default 'female',
  updated_at timestamptz default now()
);
alter table public.rest_preferences enable row level security;
create policy "rest_all" on public.rest_preferences for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
