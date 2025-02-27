-- Function cleanup and standardization

-- First, drop potentially conflicting functions
DO $$
BEGIN
  -- Drop old functions if they exist
  DROP FUNCTION IF EXISTS delete_document_by_name(text);
  DROP FUNCTION IF EXISTS delete_document_embeddings_by_name(text);
  DROP FUNCTION IF EXISTS upsert_document(text, text, jsonb);
  DROP FUNCTION IF EXISTS process_document_update(text, text, jsonb);
END$$;

-- Create standardized functions that use content_hash

-- Function to delete document and its embeddings
CREATE OR REPLACE FUNCTION delete_document(doc_content_hash text)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  -- Delete document embeddings first (due to foreign key)
  DELETE FROM document_embeddings WHERE content_hash = doc_content_hash;
  -- Delete document
  DELETE FROM documents WHERE content_hash = doc_content_hash;
END;
$$;

-- Function to upsert document with content hash
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
  
  IF doc_id IS NOT NULL THEN
    -- Update existing document
    UPDATE documents 
    SET 
      name = doc_name,
      file_path = doc_file_path,
      metadata = doc_metadata,
      updated_at = now()
    WHERE content_hash = doc_content_hash
    RETURNING id INTO doc_id;
    
    -- Delete existing embeddings
    DELETE FROM document_embeddings WHERE content_hash = doc_content_hash;
  ELSE
    -- Insert new document
    INSERT INTO documents (name, file_path, metadata, content_hash)
    VALUES (doc_name, doc_file_path, doc_metadata, doc_content_hash)
    RETURNING id INTO doc_id;
  END IF;
  
  RETURN doc_id;
END;
$$;

-- Function to get document by content hash
CREATE OR REPLACE FUNCTION get_document(doc_content_hash text)
RETURNS TABLE (
  id bigint,
  name text,
  file_path text,
  metadata jsonb,
  content_hash text,
  created_at timestamptz,
  updated_at timestamptz
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT d.* FROM documents d WHERE d.content_hash = doc_content_hash;
END;
$$; 