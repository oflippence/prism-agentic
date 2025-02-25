-- Function to handle document updates with proper embedding linking
DROP FUNCTION IF EXISTS upsert_document_with_embedding(text, text, jsonb, text, vector);

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

-- Create a function to directly call from N8N to handle document updates
CREATE OR REPLACE FUNCTION process_document_update(
  doc_name text,
  doc_file_path text,
  doc_metadata jsonb DEFAULT '{}'::jsonb
)
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
  result jsonb;
BEGIN
  -- Delete existing document with the same name
  PERFORM delete_document_by_name(doc_name);
  
  -- Return success message
  result = jsonb_build_object(
    'success', true,
    'message', 'Document deleted successfully, ready for re-embedding',
    'document_name', doc_name,
    'document_path', doc_file_path
  );
  
  RETURN result;
END;
$$; 