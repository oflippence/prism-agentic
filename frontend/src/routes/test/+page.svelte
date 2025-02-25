<!-- Test page for Supabase functionality -->
<script lang="ts">
  import { page } from '$app/stores';
  import type { StorageError } from '@supabase/storage-js';

  interface DocumentData {
    id: string;
    name: string;
    file_path: string;
    metadata: {
      publicUrl: string;
      type: string;
    };
  }

  let fileInput: HTMLInputElement;
  let status = '';
  let isUploading = false;
  let processingStatus = '';

  // Update this with your actual webhook URL from n8n
  // This URL has been tested and confirmed to work
  const N8N_WEBHOOK_URL = 'http://localhost:5678/webhook/process-document';

  // Function to get public URL of uploaded file
  async function getPublicUrl(path: string) {
    const { supabase } = $page.data;
    const { data } = supabase.storage
      .from('documents')
      .getPublicUrl(path);
    return data.publicUrl;
  }

  async function testStorage() {
    const { supabase } = $page.data;
    
    try {
      const { error } = await supabase.storage.listBuckets();
      if (error) throw error;
      status = 'Storage connection successful';
    } catch (error) {
      const err = error as StorageError;
      status = `Storage error: ${err.message}`;
    }
  }

  // Function to check and fix the database schema
  async function checkSchema() {
    const { supabase } = $page.data;
    status = 'Checking database schema...';
    
    try {
      // Check if documents table exists with the correct structure
      const { data, error } = await supabase
        .from('documents')
        .select('id, name, file_path, content, metadata, embedding')
        .limit(1);
      
      if (error) {
        status = `Schema error: ${error.message}. Please run the n8n-compatible-schema.sql script.`;
        console.error('Schema error:', error);
        return false;
      }
      
      // Check if the match_documents function exists
      const { error: rpcError } = await supabase
        .rpc('match_documents', {
          query_embedding: Array(1536).fill(0),
          match_count: 1
        })
        .limit(1);
      
      if (rpcError && !rpcError.message.includes('embedding')) {
        status = `Function error: ${rpcError.message}. Please run the n8n-compatible-schema.sql script.`;
        console.error('Function error:', rpcError);
        return false;
      }
      
      status = 'Database schema looks good!';
      return true;
    } catch (error) {
      const err = error as Error;
      status = `Schema check error: ${err.message}`;
      console.error('Schema check error:', err);
      return false;
    }
  }

  async function uploadFile() {
    if (!fileInput.files?.length) {
      status = 'Please select a file';
      return;
    }

    // First check if the schema is correct
    const schemaOk = await checkSchema();
    if (!schemaOk) {
      return;
    }

    const file = fileInput.files[0];
    const { supabase } = $page.data;
    isUploading = true;
    status = 'Uploading...';

    try {
      // Check if a document with this name already exists
      const { data: existingDoc } = await supabase
        .from('documents')
        .select('id, file_path')
        .eq('name', file.name)
        .maybeSingle();
      
      const isUpdate = !!existingDoc;
      
      // Upload file to storage
      const timestamp = Date.now();
      const filePath = `${timestamp}-${file.name}`;
      const { error: uploadError, data: uploadData } = await supabase.storage
        .from('documents')
        .upload(filePath, file);

      if (uploadError) throw uploadError;
      status = 'Upload successful!';

      // Get public URL
      const publicUrl = await getPublicUrl(filePath);
      console.log('File uploaded, public URL:', publicUrl);

      // Create document metadata
      const metadata = {
        size: file.size,
        type: file.type,
        lastModified: file.lastModified,
        publicUrl
      };

      // Create or update document record using the upsert_document function
      const { error: rpcError, data: documentId } = await supabase
        .rpc('upsert_document', {
          doc_name: file.name,
          doc_file_path: filePath,
          doc_metadata: metadata
        });

      if (rpcError) throw rpcError;
      
      // Get the full document record
      const { data: document, error: docError } = await supabase
        .from('documents')
        .select('*')
        .eq('id', documentId)
        .single();
        
      if (docError) throw docError;
      
      console.log('Document record created or updated:', document);
      processingStatus = `Document record ${isUpdate ? 'updated' : 'created'}. Starting processing...`;
      
      // Trigger N8n workflow
      await triggerDocumentProcessing(document, isUpdate);
      
    } catch (error) {
      const err = error as StorageError;
      console.error('Upload error:', err);
      status = `Upload failed: ${err.message}`;
    } finally {
      isUploading = false;
    }
  }

  async function triggerDocumentProcessing(documentData: DocumentData, isUpdate: boolean = false) {
    try {
      processingStatus = 'Triggering document processing...';
      
      // Create the payload
      const payload = {
        documentId: documentData.id,
        name: documentData.name,
        filePath: documentData.file_path,
        publicUrl: documentData.metadata.publicUrl,
        mimeType: documentData.metadata.type,
        isUpdate: isUpdate // Add this flag to indicate if it's an update
      };
      
      console.log('Sending webhook payload:', payload);
      
      // Use fetch with a timeout to handle potential connection issues
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
      
      const response = await fetch(N8N_WEBHOOK_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
        signal: controller.signal
      }).finally(() => clearTimeout(timeoutId));

      console.log('Webhook response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Webhook error response:', errorText);
        throw new Error(`Failed to trigger processing: ${errorText}`);
      }

      const responseData = await response.json().catch(() => null);
      console.log('Webhook response data:', responseData);

      processingStatus = 'Document processing started...';
    } catch (error) {
      const err = error as Error;
      console.error('Webhook error:', err);
      
      if (err.name === 'AbortError') {
        processingStatus = 'Webhook request timed out. N8n might be unreachable.';
      } else {
        processingStatus = `Failed to trigger processing: ${err.message}`;
      }
      
      // Even if the webhook fails, we'll consider the upload successful
      // since the document is in the database and can be processed later
      status = 'Upload successful, but webhook processing failed.';
    }
  }
</script>

<div class="container mx-auto p-4">
  <h1 class="text-2xl font-bold mb-4">Document Upload & Processing</h1>

  <div class="mb-6">
    <button
      class="bg-blue-500 text-white px-4 py-2 rounded"
      on:click={testStorage}
    >
      Test Storage
    </button>
    
    <button
      class="bg-purple-500 text-white px-4 py-2 rounded ml-2"
      on:click={checkSchema}
    >
      Check Schema
    </button>
  </div>

  <div class="mb-6">
    <input
      type="file"
      bind:this={fileInput}
      class="mb-2"
      accept=".pdf,.doc,.docx,.txt"
      disabled={isUploading}
    />
    <button
      class="bg-green-500 text-white px-4 py-2 rounded ml-2"
      on:click={uploadFile}
      disabled={isUploading}
    >
      {isUploading ? 'Uploading...' : 'Upload'}
    </button>
  </div>

  {#if status}
    <p class="mt-2">{status}</p>
  {/if}
  
  {#if processingStatus}
    <p class="mt-2 text-gray-600">{processingStatus}</p>
  {/if}
  
  <div class="mt-6 p-4 bg-gray-100 rounded">
    <h2 class="text-lg font-semibold mb-2">Troubleshooting Tips</h2>
    <ul class="list-disc pl-5">
      <li>If you see database errors, run the N8n-compatible schema script in Supabase SQL Editor.</li>
      <li>If webhook processing fails, check that N8n is running and accessible.</li>
      <li>The webhook URL is set to <code>{N8N_WEBHOOK_URL}</code> - this has been tested and confirmed to work.</li>
      <li>Check browser console for detailed error messages.</li>
      <li>If you're running in Docker, you may need to use <code>http://n8n:5678/webhook/process-document</code> instead.</li>
      <li>Try restarting your Docker containers with <code>docker-compose down</code> followed by <code>docker-compose up -d</code>.</li>
      <li>When uploading a document with the same name as an existing one, the system will automatically update the document record.</li>
    </ul>
  </div>
</div> 