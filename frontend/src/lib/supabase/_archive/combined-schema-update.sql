-- Safe schema update script that handles existing objects

-- Safely create the vector extension if it doesn't exist
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_extension WHERE extname = 'vector'
  ) THEN
    CREATE EXTENSION vector;
  END IF;
END
$$;

-- Check if tables exist and create them if they don't
DO $$
BEGIN
  -- Create documents table if it doesn't exist
  IF NOT EXISTS (
    SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'documents'
  ) THEN
    CREATE TABLE documents (
      id bigserial primary key,
      name text not null,
      file_path text not null,
      metadata jsonb default '{}'::jsonb,
      created_at timestamptz default now(),
      updated_at timestamptz default now(),
      unique(name) -- This ensures we can identify documents with the same name
    );
    
    RAISE NOTICE 'Created documents table';
  END IF;

  -- Create document_embeddings table if it doesn't exist
  IF NOT EXISTS (
    SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'document_embeddings'
  ) THEN
    CREATE TABLE document_embeddings (
      id bigserial primary key,
      document_id bigint references documents(id) on delete cascade,
      content text, -- corresponds to Document.pageContent
      embedding vector(1536), -- 1536 works for OpenAI embeddings, change if needed
      metadata jsonb default '{}'::jsonb, -- Additional metadata specific to this chunk
      chunk_index int, -- To keep track of the order of chunks
      created_at timestamptz default now()
    );
    
    RAISE NOTICE 'Created document_embeddings table';
  END IF;
END
$$;

-- Create or replace indexes
DO $$
BEGIN
  -- Drop existing indexes if they exist to avoid conflicts
  DROP INDEX IF EXISTS idx_documents_name;
  DROP INDEX IF EXISTS idx_document_embeddings_document_id;
  
  -- Create indexes
  CREATE INDEX idx_documents_name ON documents(name);
  CREATE INDEX idx_document_embeddings_document_id ON document_embeddings(document_id);
  
  RAISE NOTICE 'Created or replaced indexes';
END
$$;

-- Drop and recreate functions that might have changed return types
-- First, drop the match_documents function if it exists
DROP FUNCTION IF EXISTS match_documents(vector, integer, jsonb);

-- Function to search for documents
CREATE FUNCTION match_documents (
  query_embedding vector(1536),
  match_count int default null,
  filter jsonb DEFAULT '{}'
) RETURNS TABLE (
  id bigint,
  document_id bigint,
  content text,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
#variable_conflict use_column
BEGIN
  RETURN QUERY
  SELECT
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
    ) AS metadata,
    1 - (de.embedding <=> query_embedding) AS similarity
  FROM document_embeddings de
  JOIN documents d ON de.document_id = d.id
  WHERE (filter = '{}'::jsonb OR d.metadata @> filter)
  ORDER BY de.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Function to delete existing embeddings for a document by name
CREATE OR REPLACE FUNCTION delete_document_embeddings_by_name(doc_name text)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
  doc_id bigint;
BEGIN
  -- Find the document ID
  SELECT id INTO doc_id FROM documents WHERE name = doc_name;
  
  -- If document exists, delete its embeddings
  IF doc_id IS NOT NULL THEN
    DELETE FROM document_embeddings WHERE document_id = doc_id;
  END IF;
END;
$$;

-- Function to update a document's metadata and timestamp
CREATE OR REPLACE FUNCTION update_document_metadata(doc_name text, new_file_path text, new_metadata jsonb)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
  doc_id bigint;
BEGIN
  -- Check if document exists
  SELECT id INTO doc_id FROM documents WHERE name = doc_name;
  
  -- If document exists, update it
  IF doc_id IS NOT NULL THEN
    UPDATE documents 
    SET 
      file_path = new_file_path,
      metadata = new_metadata,
      updated_at = now()
    WHERE id = doc_id;
  ELSE
    -- If document doesn't exist, insert it
    INSERT INTO documents (name, file_path, metadata)
    VALUES (doc_name, new_file_path, new_metadata)
    RETURNING id INTO doc_id;
  END IF;
  
  RETURN doc_id;
END;
$$;

-- Function to update a document and clear its embeddings in one operation
CREATE OR REPLACE FUNCTION upsert_document_and_clear_embeddings(
  doc_name text, 
  new_file_path text, 
  new_metadata jsonb
)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
  doc_id bigint;
BEGIN
  -- Check if document exists
  SELECT id INTO doc_id FROM documents WHERE name = doc_name;
  
  -- If document exists, update it and clear embeddings
  IF doc_id IS NOT NULL THEN
    -- Update document metadata
    UPDATE documents 
    SET 
      file_path = new_file_path,
      metadata = new_metadata,
      updated_at = now()
    WHERE id = doc_id;
    
    -- Delete existing embeddings
    DELETE FROM document_embeddings WHERE document_id = doc_id;
  ELSE
    -- If document doesn't exist, insert it
    INSERT INTO documents (name, file_path, metadata)
    VALUES (doc_name, new_file_path, new_metadata)
    RETURNING id INTO doc_id;
  END IF;
  
  RETURN doc_id;
END;
$$;

-- Enable RLS on tables if not already enabled
DO $$
BEGIN
  -- Enable RLS on documents table
  ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
  
  -- Create a policy for the documents table if it doesn't exist
  IF NOT EXISTS (
    SELECT FROM pg_policies 
    WHERE tablename = 'documents' 
    AND policyname = 'Enable all access for testing'
  ) THEN
    CREATE POLICY "Enable all access for testing"
    ON documents
    FOR ALL
    USING (true)
    WITH CHECK (true);
    
    RAISE NOTICE 'Created RLS policy for documents table';
  END IF;
  
  -- Enable RLS on document_embeddings table
  ALTER TABLE document_embeddings ENABLE ROW LEVEL SECURITY;
  
  -- Create a policy for the document_embeddings table if it doesn't exist
  IF NOT EXISTS (
    SELECT FROM pg_policies 
    WHERE tablename = 'document_embeddings' 
    AND policyname = 'Enable all access for testing'
  ) THEN
    CREATE POLICY "Enable all access for testing"
    ON document_embeddings
    FOR ALL
    USING (true)
    WITH CHECK (true);
    
    RAISE NOTICE 'Created RLS policy for document_embeddings table';
  END IF;
END
$$;

-- Final confirmation message
DO $$
BEGIN
  RAISE NOTICE 'Schema update completed successfully!';
END
$$; 