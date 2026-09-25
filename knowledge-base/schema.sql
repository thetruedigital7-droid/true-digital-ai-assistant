-- Reference Supabase schema for the assistant.
-- kb_chunks + match_kb_chunks follow the LangChain / n8n Supabase vector store convention.
-- Column lists match the fields the n8n workflows read and write.

create extension if not exists vector;

-- Source of truth: one row per approved knowledge-base document (edited by hand).
create table if not exists kb_documents (
  id          bigserial primary key,
  slug        text unique not null,        -- e.g. 'service-seo'
  title       text not null,               -- prefixed onto every chunk at ingestion
  category    text,                        -- service | pricing-policy | faq | contact | policy | case-study
  content     text not null,
  version     int  not null default 1,
  is_active   boolean not null default true,
  updated_at  timestamptz not null default now()
);

-- Derived: rebuilt from kb_documents by workflow 05. Never edit by hand.
create table if not exists kb_chunks (
  id        bigserial primary key,
  content   text,
  metadata  jsonb,                          -- document_id, slug, title, category, version
  embedding vector(3072)                    -- gemini-embedding-001 default size
);

create or replace function match_kb_chunks (
  query_embedding vector(3072),
  match_count int default null,
  filter jsonb default '{}'
) returns table (id bigint, content text, metadata jsonb, similarity float)
language plpgsql as $$
begin
  return query
  select c.id, c.content, c.metadata, 1 - (c.embedding <=> query_embedding) as similarity
  from kb_chunks c
  where c.metadata @> filter
  order by c.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Call-back requests from both chat and voice (workflow 04).
create table if not exists leads (
  id                 bigserial primary key,
  created_at         timestamptz not null default now(),
  name               text,
  contact_method     text,                  -- whatsapp | phone | email
  contact_value      text,
  segment            text,                  -- local | international | unknown
  service_interest   text,
  qualification_data jsonb,                 -- best_time_to_call, business_type, location, goal, channel, notes...
  conversation_id    text
);

-- Leads hold personal data: keep RLS on and only use the service-role key from n8n.
alter table kb_documents enable row level security;
alter table kb_chunks    enable row level security;
alter table leads        enable row level security;
