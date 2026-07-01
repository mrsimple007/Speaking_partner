-- ============================================================
-- LangBridge MVP — Supabase / PostgreSQL schema
-- ============================================================

create extension if not exists "uuid-ossp";

-- ------------------------------------------------------------
-- USERS
-- ------------------------------------------------------------
create table if not exists users (
    id              bigserial primary key,
    telegram_id     bigint unique not null,
    native_language text not null,           -- 'uz' | 'ru' | 'en' | 'tr' ...
    learning_language text,
    level           text,                     -- 'A1'..'C2' or 'native'
    gender          text,                     -- 'male' | 'female' | 'unspecified'
    ui_language     text not null default 'en', -- language of the bot interface
    premium         boolean not null default false,
    premium_until   timestamptz,
    status          text not null default 'idle', -- idle | searching | chatting | banned
    report_count    integer not null default 0,
    banned          boolean not null default false,
    banned_until    timestamptz,
    onboarding_step text default 'native_language', -- tracks where user is in onboarding
    created_at      timestamptz not null default now(),
    last_active     timestamptz not null default now()
);

create index if not exists idx_users_telegram_id on users(telegram_id);
create index if not exists idx_users_status on users(status);

-- ------------------------------------------------------------
-- INTERESTS (lookup table)
-- ------------------------------------------------------------
create table if not exists interests (
    id    serial primary key,
    code  text unique not null,   -- 'programming', 'movies', ...
    name  text not null           -- display fallback (English), UI uses translations.py
);

insert into interests (code, name) values
    ('programming','Programming'),
    ('movies','Movies'),
    ('football','Football'),
    ('chess','Chess'),
    ('music','Music'),
    ('travel','Travel'),
    ('business','Business'),
    ('reading','Reading'),
    ('anime','Anime'),
    ('cooking','Cooking'),
    ('technology','Technology'),
    ('startups','Startups')
on conflict (code) do nothing;

-- ------------------------------------------------------------
-- USER <-> INTERESTS (many-to-many, max 5 enforced in app layer)
-- ------------------------------------------------------------
create table if not exists user_interests (
    user_id     bigint not null references users(id) on delete cascade,
    interest_id integer not null references interests(id) on delete cascade,
    primary key (user_id, interest_id)
);

-- ------------------------------------------------------------
-- MATCHES (chat sessions)
-- ------------------------------------------------------------
create table if not exists matches (
    id          bigserial primary key,
    user1_id    bigint not null references users(id),
    user2_id    bigint not null references users(id),
    started_at  timestamptz not null default now(),
    ended_at    timestamptz,
    duration_seconds integer,
    end_reason  text  -- 'next' | 'end' | 'disconnect' | 'report'
);

create index if not exists idx_matches_user1 on matches(user1_id);
create index if not exists idx_matches_user2 on matches(user2_id);
create index if not exists idx_matches_active on matches(ended_at) where ended_at is null;

-- ------------------------------------------------------------
-- MESSAGES (metadata only — never store text content)
-- ------------------------------------------------------------
create table if not exists messages (
    id          bigserial primary key,
    match_id    bigint not null references matches(id) on delete cascade,
    sender_id   bigint not null references users(id),
    created_at  timestamptz not null default now()
);

create index if not exists idx_messages_match on messages(match_id);

-- ------------------------------------------------------------
-- REPORTS
-- ------------------------------------------------------------
create table if not exists reports (
    id          bigserial primary key,
    match_id    bigint references matches(id),
    reporter_id bigint not null references users(id),
    reported_id bigint not null references users(id),
    reason      text not null, -- 'spam' | 'advertising' | 'harassment' | 'inappropriate_language' | 'other'
    comment     text,
    created_at  timestamptz not null default now()
);

create index if not exists idx_reports_reported on reports(reported_id);

-- ------------------------------------------------------------
-- PAYMENTS (Telegram Stars + manual bank/card transfer)
-- ------------------------------------------------------------
create table if not exists payments (
    id              bigserial primary key,
    user_id         bigint not null references users(id),
    method          text not null,        -- 'telegram_stars' | 'manual_transfer'
    amount          numeric,              -- stars amount or UZS/whatever currency amount
    currency        text,                 -- 'XTR' for stars, 'UZS' for manual
    status          text not null default 'pending', -- pending | confirmed | rejected
    telegram_payment_charge_id text,      -- set for stars payments
    proof_screenshot_file_id   text,      -- telegram file_id of transfer screenshot, for manual
    admin_note      text,
    created_at      timestamptz not null default now(),
    confirmed_at    timestamptz
);

create index if not exists idx_payments_user on payments(user_id);
create index if not exists idx_payments_status on payments(status);

-- ------------------------------------------------------------
-- ADMIN STATS VIEW (basic)
-- ------------------------------------------------------------
create or replace view admin_stats as
select
    (select count(*) from users) as total_users,
    (select count(*) from users where last_active > now() - interval '24 hours') as active_users_24h,
    (select count(*) from users where premium = true) as premium_users,
    (select count(*) from matches where started_at::date = current_date) as matches_today,
    (select avg(duration_seconds) from matches where ended_at is not null) as avg_chat_duration_seconds,
    (select count(*) from reports where created_at::date = current_date) as reports_today;

-- ------------------------------------------------------------
-- Row Level Security (basic — bot uses service_role key, so RLS
-- mainly protects against anon/public key misuse if ever exposed)
-- ------------------------------------------------------------
alter table users enable row level security;
alter table matches enable row level security;
alter table messages enable row level security;
alter table reports enable row level security;
alter table payments enable row level security;

-- No public policies are created — only the service_role key
-- (used server-side by the bot) can read/write. This blocks
-- anonymous/public access entirely.
