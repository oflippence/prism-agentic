-- Enable the pgvector extension to work with embedding vectors
create extension vector;

-- Create a table to store document metadata
create table documents (
  id bigserial primary key,
  name text not null,
  file_path text not null,
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  unique(name) -- This ensures we can identify documents with the same name
);

-- Create a table to store document embeddings
create table document_embeddings (
  id bigserial primary key,
  document_id bigint references documents(id) on delete cascade,
  content text, -- corresponds to Document.pageContent
  embedding vector(1536), -- 1536 works for OpenAI embeddings, change if needed
  metadata jsonb default '{}'::jsonb, -- Additional metadata specific to this chunk
  chunk_index int, -- To keep track of the order of chunks
  created_at timestamptz default now()
);

-- Create indexes for better performance
create index on documents(name);
create index on document_embeddings(document_id);

-- Create a function to search for documents
create function match_documents (
  query_embedding vector(1536),
  match_count int default null,
  filter jsonb DEFAULT '{}'
) returns table (
  id bigint,
  document_id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
#variable_conflict use_column
begin
  return query
  select
    de.id,
    de.document_id,
    de.content,
    jsonb_build_object(
      'document', jsonb_build_object(
        'id', d.id,
        'name', d.name,
        'file_path', d.file_path,
        'metadata', d.metadata
      ),
      'chunk', de.metadata
    ) as metadata,
    1 - (de.embedding <=> query_embedding) as similarity
  from document_embeddings de
  join documents d on de.document_id = d.id
  where (filter = '{}'::jsonb or d.metadata @> filter)
  order by de.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Create a function to delete existing embeddings for a document by name
create function delete_document_embeddings_by_name(doc_name text)
returns void
language plpgsql
as $$
declare
  doc_id bigint;
begin
  -- Find the document ID
  select id into doc_id from documents where name = doc_name;
  
  -- If document exists, delete its embeddings
  if doc_id is not null then
    delete from document_embeddings where document_id = doc_id;
  end if;
end;
$$;

-- Create a function to update a document's metadata and timestamp
create function update_document_metadata(doc_name text, new_file_path text, new_metadata jsonb)
returns bigint
language plpgsql
as $$
declare
  doc_id bigint;
begin
  -- Check if document exists
  select id into doc_id from documents where name = doc_name;
  
  -- If document exists, update it
  if doc_id is not null then
    update documents 
    set 
      file_path = new_file_path,
      metadata = new_metadata,
      updated_at = now()
    where id = doc_id;
  else
    -- If document doesn't exist, insert it
    insert into documents (name, file_path, metadata)
    values (doc_name, new_file_path, new_metadata)
    returning id into doc_id;
  end if;
  
  return doc_id;
end;
$$;

-- Create a function to update a document and clear its embeddings in one operation
-- This is useful when re-processing a document that already exists
create function upsert_document_and_clear_embeddings(
  doc_name text, 
  new_file_path text, 
  new_metadata jsonb
)
returns bigint
language plpgsql
as $$
declare
  doc_id bigint;
begin
  -- Check if document exists
  select id into doc_id from documents where name = doc_name;
  
  -- If document exists, update it and clear embeddings
  if doc_id is not null then
    -- Update document metadata
    update documents 
    set 
      file_path = new_file_path,
      metadata = new_metadata,
      updated_at = now()
    where id = doc_id;
    
    -- Delete existing embeddings
    delete from document_embeddings where document_id = doc_id;
  else
    -- If document doesn't exist, insert it
    insert into documents (name, file_path, metadata)
    values (doc_name, new_file_path, new_metadata)
    returning id into doc_id;
  end if;
  
  return doc_id;
end;
$$;
