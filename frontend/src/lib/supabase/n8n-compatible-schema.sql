-- N8n-compatible schema with document update functionality
-- This script follows the original schema structure expected by N8n

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

-- Drop existing functions first
DROP FUNCTION IF EXISTS match_documents(vector, integer, jsonb);
DROP FUNCTION IF EXISTS delete_document_embeddings_by_name(text);
DROP FUNCTION IF EXISTS update_document_metadata(text, text, jsonb);
DROP FUNCTION IF EXISTS upsert_document_and_clear_embeddings(text, text, jsonb);
DROP FUNCTION IF EXISTS upsert_document_with_embedding(text, text, jsonb, text, vector);

-- Drop existing tables with CASCADE to handle dependencies
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS document_embeddings CASCADE;

-- Create the documents table as expected by N8n
CREATE TABLE documents (
  id bigserial primary key,
  content text, -- corresponds to Document.pageContent
  metadata jsonb DEFAULT '{}'::jsonb, -- corresponds to Document.metadata
  embedding vector(1536), -- 1536 works for OpenAI embeddings
  name text, -- Added for document identification
  file_path text, -- Added for file reference
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create indexes for better performance
CREATE INDEX idx_documents_name ON documents(name);
CREATE INDEX idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops);

-- Create a function to search for documents (original N8n-compatible version)
CREATE FUNCTION match_documents (
  query_embedding vector(1536),
  match_count int DEFAULT null,
  filter jsonb DEFAULT '{}'
) RETURNS TABLE (
  id bigint,
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
    id,
    content,
    metadata,
    1 - (documents.embedding <=> query_embedding) AS similarity
  FROM documents
  WHERE metadata @> filter
  ORDER BY documents.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Function to delete existing embeddings for a document by name
CREATE OR REPLACE FUNCTION delete_document_by_name(doc_name text)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  -- Delete document with the given name
  DELETE FROM documents WHERE name = doc_name;
END;
$$;

-- Function to update a document or create it if it doesn't exist
CREATE OR REPLACE FUNCTION upsert_document(
  doc_name text, 
  doc_file_path text, 
  doc_metadata jsonb DEFAULT '{}'::jsonb,
  doc_content text DEFAULT null,
  doc_embedding vector(1536) DEFAULT null
)
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
    -- If embedding is provided, update everything
    IF doc_embedding IS NOT NULL THEN
      UPDATE documents 
      SET 
        file_path = doc_file_path,
        metadata = doc_metadata,
        content = doc_content,
        embedding = doc_embedding,
        updated_at = now()
      WHERE id = doc_id;
    -- Otherwise just update metadata and file_path
    ELSE
      UPDATE documents 
      SET 
        file_path = doc_file_path,
        metadata = doc_metadata,
        updated_at = now()
      WHERE id = doc_id;
    END IF;
  ELSE
    -- If document doesn't exist, insert it
    INSERT INTO documents (name, file_path, metadata, content, embedding)
    VALUES (doc_name, doc_file_path, doc_metadata, doc_content, doc_embedding)
    RETURNING id INTO doc_id;
  END IF;
  
  RETURN doc_id;
END;
$$;

-- New function to handle document updates with proper embedding linking
CREATE OR REPLACE FUNCTION upsert_document_with_embedding(
  doc_name text, 
  doc_file_path text, 
  doc_metadata jsonb DEFAULT '{}'::jsonb,
  doc_content text DEFAULT null,
  doc_embedding vector(1536) DEFAULT null
)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
  doc_id bigint;
  updated_metadata jsonb;
BEGIN
  -- Ensure metadata contains name and file_path
  updated_metadata = doc_metadata || jsonb_build_object(
    'name', doc_name,
    'file_path', doc_file_path
  );
  
  -- Delete existing document with the same name
  PERFORM delete_document_by_name(doc_name);
  
  -- Insert the new document with all information
  INSERT INTO documents (name, file_path, metadata, content, embedding)
  VALUES (doc_name, doc_file_path, updated_metadata, doc_content, doc_embedding)
  RETURNING id INTO doc_id;
  
  RETURN doc_id;
END;
$$;

-- Enable RLS on the documents table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create a policy for the documents table
DO $$
BEGIN
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
  END IF;
END
$$;

-- Final confirmation message
DO $$
BEGIN
  RAISE NOTICE 'N8n-compatible schema setup completed successfully!';
END
$$; 