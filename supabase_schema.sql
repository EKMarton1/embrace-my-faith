-- ============================================================
-- Embrace My Faith — Supabase Schema
-- Run this entire file in the Supabase SQL editor
-- ============================================================

-- PROFILES
create table if not exists public.profiles (
  id uuid references auth.users on delete cascade primary key,
  name text,
  email text,
  gender text default 'female',
  tier text default 'grace' check (tier in ('grace', 'philippians', 'john')),
  trial_ends_at date default (current_date + interval '10 days'),
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Add tier columns to existing installs (safe to run multiple times)
alter table public.profiles add column if not exists tier text default 'grace' check (tier in ('grace', 'philippians', 'john'));
alter table public.profiles add column if not exists trial_ends_at date default (current_date + interval '10 days');
alter table public.profiles enable row level security;
-- Drop old single policy if it exists
drop policy if exists "profiles_all" on public.profiles;
-- All authenticated users can read profiles (needed for circle search)
create policy "profiles_read" on public.profiles for select using (auth.uid() is not null);
-- Users can only write their own profile
create policy "profiles_write" on public.profiles for insert with check (auth.uid() = id);
create policy "profiles_update" on public.profiles for update using (auth.uid() = id) with check (auth.uid() = id);
create policy "profiles_delete" on public.profiles for delete using (auth.uid() = id);

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

-- CIRCLE CONNECTIONS
create table if not exists public.circle_connections (
  id uuid default gen_random_uuid() primary key,
  requester_id uuid references auth.users on delete cascade not null,
  addressee_id uuid references auth.users on delete cascade not null,
  status text default 'pending' check (status in ('pending', 'accepted', 'declined')),
  created_at timestamptz default now(),
  unique(requester_id, addressee_id)
);
alter table public.circle_connections enable row level security;
-- Both parties can see connections they're part of
create policy "circle_select" on public.circle_connections for select
  using (auth.uid() = requester_id or auth.uid() = addressee_id);
-- Only requester can create the invite
create policy "circle_insert" on public.circle_connections for insert
  with check (auth.uid() = requester_id);
-- Only addressee can accept/decline (update status)
create policy "circle_update" on public.circle_connections for update
  using (auth.uid() = addressee_id);
-- Either party can remove the connection
create policy "circle_delete" on public.circle_connections for delete
  using (auth.uid() = requester_id or auth.uid() = addressee_id);

-- PRAYER REQUESTS
create table if not exists public.prayer_requests (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users on delete cascade not null,
  request_text text not null,
  created_at timestamptz default now()
);
alter table public.prayer_requests enable row level security;
-- Users can see their own requests plus requests from accepted circle members
create policy "requests_select" on public.prayer_requests for select
  using (
    auth.uid() = user_id or
    exists (
      select 1 from public.circle_connections cc
      where cc.status = 'accepted'
        and (
          (cc.requester_id = auth.uid() and cc.addressee_id = prayer_requests.user_id) or
          (cc.addressee_id = auth.uid() and cc.requester_id = prayer_requests.user_id)
        )
    )
  );
create policy "requests_insert" on public.prayer_requests for insert
  with check (auth.uid() = user_id);
create policy "requests_delete" on public.prayer_requests for delete
  using (auth.uid() = user_id);
