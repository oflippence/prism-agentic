-- SQL script to fix the database schema

-- Enable the Vector extension if not already enabled
create extension if not exists vector;

-- Create a function to check if a column exists in a table
create or replace function column_exists(p_table_name text, p_column_name text) 
returns boolean as $$
declare
  exists_bool boolean;
begin
  select exists (
    select 1
    from information_schema.columns
    where table_schema = 'public'
      and table_name = p_table_name
      and column_name = p_column_name
  ) into exists_bool;
  
  return exists_bool;
end;
$$ language plpgsql;

-- Create or update the documents table
do $$
begin
  -- Check if documents table exists
  if not exists (select from information_schema.tables where table_schema = 'public' and table_name = 'documents') then
    -- Create the documents table if it doesn't exist
    create table documents (
      id uuid default gen_random_uuid() primary key,
      content text,
      metadata jsonb default '{}'::jsonb,
      embedding vector(1536),
      file_path text,
      name text,
      created_at timestamp with time zone default timezone('utc'::text, now()) not null,
      updated_at timestamp with time zone default timezone('utc'::text, now()) not null
    );
    
    raise notice 'Created documents table';
  else
    -- Add missing columns if the table exists
    if not column_exists('documents', 'file_path') then
      alter table documents add column file_path text;
      raise notice 'Added file_path column to documents table';
    end if;
    
    if not column_exists('documents', 'name') then
      alter table documents add column name text;
      raise notice 'Added name column to documents table';
    end if;
    
    if not column_exists('documents', 'content') then
      alter table documents add column content text;
      raise notice 'Added content column to documents table';
    end if;
    
    if not column_exists('documents', 'metadata') then
      alter table documents add column metadata jsonb default '{}'::jsonb;
      raise notice 'Added metadata column to documents table';
    end if;
    
    if not column_exists('documents', 'embedding') then
      alter table documents add column embedding vector(1536);
      raise notice 'Added embedding column to documents table';
    end if;
  end if;
  
  -- Enable RLS on the documents table
  alter table documents enable row level security;
  
  -- Create a policy for the documents table if it doesn't exist
  if not exists (
    select from pg_policies 
    where tablename = 'documents' 
    and policyname = 'Enable all access for testing'
  ) then
    create policy "Enable all access for testing"
    on documents
    for all
    using (true)
    with check (true);
    
    raise notice 'Created RLS policy for documents table';
  end if;
end;
$$; 