-- Create a function to update a document and clear its embeddings in one operation
-- This is useful when re-processing a document that already exists
create or replace function upsert_document_and_clear_embeddings(
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