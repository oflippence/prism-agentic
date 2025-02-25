-- Enable the Vector extension
create extension if not exists vector;

-- Create a table for documents
create table if not exists documents (
    id uuid default gen_random_uuid() primary key,
    user_id uuid references auth.users(id),
    name text not null,
    file_path text not null,
    content text,
    metadata jsonb default '{}'::jsonb,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create a table for document embeddings
create table if not exists document_embeddings (
    id uuid default gen_random_uuid() primary key,
    document_id uuid references documents(id) on delete cascade,
    embedding vector(1536), -- dimensionality for OpenAI embeddings
    chunk_start integer,
    chunk_end integer,
    chunk_text text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create an index for similarity search
create index on document_embeddings 
using ivfflat (embedding vector_cosine_ops)
with (lists = 100);

-- Function to update updated_at timestamp
create or replace function update_updated_at_column()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = timezone('utc'::text, now());
    return new;
end;
$$;

-- Trigger to update updated_at
create trigger documents_updated_at
    before update on documents
    for each row
    execute function update_updated_at_column();

-- Enable Row Level Security
alter table documents enable row level security;
alter table document_embeddings enable row level security;

-- Create policies for documents table
create policy "Enable all access for testing"
on documents
for all
using (true)
with check (true);

-- Create policies for document_embeddings table
create policy "Enable all access for embeddings testing"
on document_embeddings
for all
using (true)
with check (true);

-- Note: For production, replace with these more restrictive policies:
/*
create policy "Users can only access their own documents"
on documents
for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create policy "Users can only access their own document embeddings"
on document_embeddings
for all
using (
    document_id in (
        select id from documents 
        where user_id = auth.uid()
    )
);
*/ 