-- Add content_hash column to documents table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'documents'
        AND column_name = 'content_hash'
    ) THEN
        ALTER TABLE documents
        ADD COLUMN content_hash text;
        
        -- Create index for content_hash
        CREATE INDEX idx_documents_content_hash ON documents(content_hash);
    END IF;
END $$;

-- Add content_hash column to document_embeddings table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'document_embeddings'
        AND column_name = 'content_hash'
    ) THEN
        ALTER TABLE document_embeddings
        ADD COLUMN content_hash text;
        
        -- Create index for content_hash in embeddings
        CREATE INDEX idx_document_embeddings_content_hash ON document_embeddings(content_hash);
    END IF;
END $$;

-- Function to upsert document using content hash
CREATE OR REPLACE FUNCTION upsert_document(
    doc_name text,
    doc_file_path text,
    doc_metadata jsonb,
    doc_content_hash text
)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    doc_id bigint;
BEGIN
    -- Check if document exists by content hash
    SELECT id INTO doc_id FROM documents WHERE content_hash = doc_content_hash;
    
    -- If document exists, update it
    IF doc_id IS NOT NULL THEN
        UPDATE documents 
        SET 
            name = doc_name,
            file_path = doc_file_path,
            metadata = COALESCE(doc_metadata, metadata), -- Keep existing metadata if new is null
            updated_at = now()
        WHERE id = doc_id;
        
        -- Delete existing embeddings for this document
        DELETE FROM document_embeddings WHERE content_hash = doc_content_hash;
    ELSE
        -- If document doesn't exist, insert it
        INSERT INTO documents (name, file_path, metadata, content_hash)
        VALUES (doc_name, doc_file_path, COALESCE(doc_metadata, '{}'::jsonb), doc_content_hash)
        RETURNING id INTO doc_id;
    END IF;
    
    RETURN doc_id;
END;
$$;

-- Function to delete document embeddings by content hash
CREATE OR REPLACE FUNCTION delete_document_embeddings_by_hash(doc_content_hash text)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM document_embeddings WHERE content_hash = doc_content_hash;
END;
$$;

-- Function to update document metadata by content hash
CREATE OR REPLACE FUNCTION update_document_metadata_by_hash(
    doc_content_hash text,
    new_metadata jsonb
)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    doc_id bigint;
BEGIN
    UPDATE documents 
    SET 
        metadata = new_metadata,
        updated_at = now()
    WHERE content_hash = doc_content_hash
    RETURNING id INTO doc_id;
    
    RETURN doc_id;
END;
$$;

-- Function to insert document embedding with content hash
CREATE OR REPLACE FUNCTION insert_document_embedding(
    doc_content text,
    doc_embedding vector(1536),
    doc_metadata jsonb,
    doc_chunk_index int DEFAULT 0
)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    embedding_id bigint;
    metadata_content_hash text;
    metadata_document_name text;
BEGIN
    -- Extract content hash and document name from metadata
    metadata_content_hash := doc_metadata->>'content_hash';
    metadata_document_name := doc_metadata->>'document_name';
    
    -- If we have a content hash, delete any existing embeddings with the same hash from previous batches
    IF metadata_content_hash IS NOT NULL THEN
        DELETE FROM document_embeddings 
        WHERE metadata->>'content_hash' = metadata_content_hash
        AND updated_at < now();  -- Delete only older records
    END IF;

    -- Insert the new embedding with all available columns
    INSERT INTO document_embeddings 
        (content, embedding, metadata, content_hash, document_name, chunk_index)
    VALUES 
        (
            doc_content, 
            doc_embedding, 
            doc_metadata,
            metadata_content_hash,
            metadata_document_name,
            doc_chunk_index
        )
    RETURNING id INTO embedding_id;
    
    RETURN embedding_id;
END;
$$;

-- Restore original match_documents function
DROP FUNCTION IF EXISTS match_documents(vector(1536), integer, jsonb);

CREATE OR REPLACE FUNCTION match_documents (
  query_embedding vector(1536),
  match_count int default null,
  filter jsonb DEFAULT '{}'
) returns table (
  id bigint,
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
    id,
    content,
    metadata,
    1 - (embedding <=> query_embedding) as similarity
  from document_embeddings
  where (filter = '{}'::jsonb or metadata @> filter)
  order by embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Function to extract and populate content_hash from metadata
CREATE OR REPLACE FUNCTION populate_content_hash_from_metadata()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  -- Update content_hash from metadata where it exists in the JSON
  UPDATE document_embeddings
  SET content_hash = metadata->>'content_hash'
  WHERE content_hash IS NULL 
  AND metadata->>'content_hash' IS NOT NULL;

  -- Update content_hash from document metadata if available
  UPDATE document_embeddings
  SET content_hash = metadata->'document'->>'content_hash'
  WHERE content_hash IS NULL 
  AND metadata->'document'->>'content_hash' IS NOT NULL;

  -- Update document name if we have it in metadata
  UPDATE document_embeddings
  SET 
    document_name = COALESCE(
      metadata->'document'->>'name',
      metadata->>'document_name'
    )
  WHERE document_name IS NULL
  AND (
    metadata->'document'->>'name' IS NOT NULL
    OR metadata->>'document_name' IS NOT NULL
  );
END;
$$;

-- Add document_name column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'document_embeddings'
        AND column_name = 'document_name'
    ) THEN
        ALTER TABLE document_embeddings
        ADD COLUMN document_name text;
        
        -- Create index for document_name
        CREATE INDEX idx_document_embeddings_document_name ON document_embeddings(document_name);
    END IF;
END $$;

-- Function to query embeddings with content hash (as an alternative view)
CREATE OR REPLACE FUNCTION match_documents_with_hash(
  query_embedding vector(1536),
  match_count int default null,
  filter jsonb DEFAULT '{}'
) returns table (
  id bigint,
  content text,
  metadata jsonb,
  content_hash text,
  document_name text,
  similarity float
)
language plpgsql
as $$
#variable_conflict use_column
begin
  return query
  select
    id,
    content,
    metadata,
    content_hash,
    document_name,
    1 - (embedding <=> query_embedding) as similarity
  from document_embeddings
  where (filter = '{}'::jsonb or metadata @> filter)
  order by embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Function to update existing embeddings with content hash from metadata
CREATE OR REPLACE FUNCTION update_embeddings_content_hash()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  -- Update content_hash in document_embeddings from metadata
  UPDATE document_embeddings de
  SET content_hash = (de.metadata->>'content_hash')
  WHERE de.content_hash IS NULL 
  AND de.metadata->>'content_hash' IS NOT NULL;
  
  -- Update content_hash in document_embeddings from linked document
  UPDATE document_embeddings de
  SET content_hash = d.content_hash
  FROM documents d
  WHERE de.content_hash IS NULL 
  AND de.metadata->'document'->>'id' = d.id::text
  AND d.content_hash IS NOT NULL;
END;
$$;

-- Create trigger function to handle content hash deduplication
CREATE OR REPLACE FUNCTION handle_document_embedding_deduplication()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    metadata_content_hash text;
BEGIN
    -- Extract content hash from metadata
    metadata_content_hash := NEW.metadata->>'content_hash';
    
    -- If we found a content hash in metadata, delete older duplicates
    IF metadata_content_hash IS NOT NULL THEN
        -- Delete only records with same content_hash but from previous batches
        DELETE FROM document_embeddings 
        WHERE id != NEW.id 
        AND metadata->>'content_hash' = metadata_content_hash
        AND updated_at < NEW.updated_at;
    END IF;
    
    RETURN NEW;
END;
$$;

-- Create the trigger
DROP TRIGGER IF EXISTS tr_document_embedding_deduplication ON document_embeddings;
CREATE TRIGGER tr_document_embedding_deduplication
    AFTER INSERT ON document_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION handle_document_embedding_deduplication();

-- Function to query embeddings by content hash in metadata
CREATE OR REPLACE FUNCTION match_documents_by_hash(
    target_content_hash text,
    match_count int default null
)
RETURNS TABLE (
    id bigint,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        de.id,
        de.content,
        de.metadata,
        1.0::float as similarity
    FROM document_embeddings de
    WHERE de.metadata->>'content_hash' = target_content_hash
    LIMIT match_count;
END;
$$;

-- Function to update content_hash and document_name columns (can be run periodically)
CREATE OR REPLACE FUNCTION update_document_columns()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    -- Update content_hash if the column exists
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'document_embeddings'
        AND column_name = 'content_hash'
    ) THEN
        UPDATE document_embeddings
        SET content_hash = metadata->>'content_hash'
        WHERE metadata->>'content_hash' IS NOT NULL;
    END IF;

    -- Update document_name if the column exists
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'document_embeddings'
        AND column_name = 'document_name'
    ) THEN
        UPDATE document_embeddings
        SET document_name = metadata->>'document_name'
        WHERE metadata->>'document_name' IS NOT NULL;
    END IF;
END;
$$;

-- Function to clean up old embeddings
CREATE OR REPLACE FUNCTION cleanup_old_document_embeddings()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    -- Delete embeddings that share the same content_hash but are from older batches
    DELETE FROM document_embeddings de1
    USING document_embeddings de2
    WHERE de1.metadata->>'content_hash' = de2.metadata->>'content_hash'
    AND de1.updated_at < de2.updated_at;
END;
$$; 