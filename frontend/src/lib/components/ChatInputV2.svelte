<!-- ChatInputV2.svelte -->
<script lang="ts">
  // Import icons directly from Font Awesome Pro packages
  import { faPaperclip, faCamera, faAngleDown, faChevronRight, faXmark } from '@fortawesome/pro-solid-svg-icons';
  import { faGoogleDrive as faGoogleDriveBrand } from '@fortawesome/free-brands-svg-icons/faGoogleDrive';
  import { createEventDispatcher, onMount } from 'svelte';
  import { page } from '$app/stores';
  import { config } from '../config/environment';
  import type { StorageError } from '@supabase/storage-js';

  const dispatch = createEventDispatcher();
  let inputValue = '';
  let selectedModel = 'claude-3-7-sonnet-20250219';
  let isLoading = false;
  let fileInput: HTMLInputElement;
  let uploadStatus = '';
  let processingStatus = '';
  let isUploading = false;
  let selectedFiles: File[] = [];
  
  // Generate a unique session ID that persists for the page session
  const sessionId = crypto.randomUUID();
  console.log('[DEBUG] Generated session ID:', sessionId);

  // Get backend URL from centralized config
  const backendUrl = config.backendUrl;
  console.log('[DEBUG] Environment mode:', config.environment);
  console.log('[DEBUG] Backend URL:', backendUrl);
  
  if (!backendUrl.startsWith('http')) {
    console.error('[DEBUG] Invalid backend URL format:', backendUrl);
  }

  // Function to get initial welcome message from n8n
  async function getWelcomeMessage() {
    try {
      console.log('[DEBUG] Requesting welcome message from n8n');
      console.log('[DEBUG] Using backend URL:', backendUrl);
      console.log('[DEBUG] Using session ID:', sessionId);
      
      const response = await fetch(`${backendUrl}/api/welcome`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          chatInput: "Hello, this is the PRISM application frontend requesting a welcome message. Please introduce yourself and begin the conversation with our user.",
          sessionId: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('[DEBUG] Welcome message response:', data);

      if (data.output) {
        dispatch('update', {
          question: null,
          answer: data.output
        });
        console.log('[DEBUG] Dispatched welcome message update event');
      }

    } catch (error: any) {
      console.error('[DEBUG] Error getting welcome message:', error);
      dispatch('error', { error: error.message || 'Failed to get welcome message' });
    }
  }

  // Get welcome message on component mount
  onMount(() => {
    getWelcomeMessage();
  });

  // Function to get public URL of uploaded file
  async function getPublicUrl(path: string) {
    const { supabase } = $page.data;
    const { data } = supabase.storage
      .from('documents')
      .getPublicUrl(path);
    return data.publicUrl;
  }

  // Function to generate file hash
  async function generateFileHash(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const arrayBuffer = e.target?.result as ArrayBuffer;
          const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
          const hashArray = Array.from(new Uint8Array(hashBuffer));
          const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
          resolve(hashHex);
        } catch (error) {
          reject(error);
        }
      };
      reader.onerror = error => reject(error);
      reader.readAsArrayBuffer(file);
    });
  }

  // Function to handle file selection
  function handleFileSelect(event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
      // Convert FileList to array and append to selectedFiles
      const newFiles = Array.from(target.files);
      selectedFiles = [...selectedFiles, ...newFiles];
      updateFileStatus();
    }
  }

  // Function to remove a file from selection
  function removeFile(index: number) {
    selectedFiles = selectedFiles.filter((_, i) => i !== index);
    updateFileStatus();
    
    // Clear file input if all files are removed
    if (selectedFiles.length === 0 && fileInput) {
      fileInput.value = '';
    }
  }

  // Function to update file status message
  function updateFileStatus() {
    if (selectedFiles.length === 0) {
      uploadStatus = '';
    } else if (selectedFiles.length === 1) {
      uploadStatus = `File selected: ${selectedFiles[0].name}`;
    } else {
      uploadStatus = `${selectedFiles.length} files selected`;
    }
    dispatch('status', { message: uploadStatus });
  }

  // Function to trigger document processing
  async function triggerDocumentProcessing(documentData: any, isUpdate: boolean = false) {
    try {
      processingStatus = 'Triggering document processing...';
      dispatch('status', { message: processingStatus });
      
      const payload = {
        documentId: documentData.id,
        name: documentData.name,
        filePath: documentData.file_path,
        publicUrl: documentData.metadata.publicUrl,
        mimeType: documentData.metadata.type,
        contentHash: documentData.content_hash || documentData.metadata?.contentHash,
        isUpdate: isUpdate
      };
      
      const response = await fetch('http://localhost:5678/webhook/process-document', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to trigger processing: ${errorText}`);
      }

      processingStatus = 'Document processing started...';
      dispatch('status', { message: processingStatus });
    } catch (error: any) {
      console.error('Processing error:', error);
      processingStatus = `Failed to trigger processing: ${error.message}`;
      dispatch('error', { error: processingStatus });
    }
  }

  // Modified submit handler to handle multiple file uploads
  async function handleSubmit() {
    if (!inputValue.trim() && selectedFiles.length === 0) return;
    
    isLoading = true;
    
    try {
      if (selectedFiles.length > 0) {
        isUploading = true;
        uploadStatus = 'Uploading files...';
        dispatch('status', { message: uploadStatus });

        // Process each file sequentially
        for (const file of selectedFiles) {
          const contentHash = await generateFileHash(file);
          const timestamp = Date.now();
          const filePath = `${timestamp}-${file.name}`;
          const { supabase } = $page.data;
          
          // Upload file
          const { error: uploadError } = await supabase.storage
            .from('documents')
            .upload(filePath, file);

          if (uploadError) throw uploadError;
          
          // Get public URL
          const publicUrl = await getPublicUrl(filePath);
          
          // Create metadata
          const metadata = {
            size: file.size,
            type: file.type,
            lastModified: file.lastModified,
            publicUrl,
            contentHash
          };
          
          // Create document record
          const { error: rpcError, data: documentId } = await supabase
            .rpc('upsert_document', {
              doc_name: file.name,
              doc_file_path: filePath,
              doc_metadata: metadata,
              doc_content_hash: contentHash
            });

          if (rpcError) throw rpcError;
          
          // Get full document record
          const { data: document, error: docError } = await supabase
            .from('documents')
            .select('*, content_hash')
            .eq('id', documentId)
            .single();
            
          if (docError) throw docError;
          
          // Trigger processing for this document
          await triggerDocumentProcessing(document, false);
        }
        
        uploadStatus = 'All files uploaded successfully!';
        dispatch('status', { message: uploadStatus });
        selectedFiles = [];
        
        // Clear the file input
        if (fileInput) {
          fileInput.value = '';
        }
      }
      
      // Handle regular chat input if present
      if (inputValue.trim()) {
        dispatch('message', {
          question: inputValue,
          answer: null
        });
        
        const response = await fetch(`${backendUrl}/api/chat-v2`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            chatInput: inputValue,
            model: selectedModel,
            sessionId: sessionId
          })
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.output) {
          dispatch('update', {
            question: inputValue,
            answer: data.output
          });
          inputValue = '';
        }
      }

    } catch (error: any) {
      console.error('Error:', error);
      const errorMessage = error.message || 'An error occurred';
      dispatch('error', { error: errorMessage });
      uploadStatus = `Error: ${errorMessage}`;
      dispatch('status', { message: uploadStatus });
    } finally {
      isLoading = false;
      isUploading = false;
    }
  }

  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  }
</script>

<div class="w-full">
  <div class="w-full bg-surface-50-900-token border custom-border rounded-container-token p-4">
    <div class="bg-white rounded-container-token p-3 mb-3">
      <textarea
        placeholder="How can we help you today?"
        bind:value={inputValue}
        on:keydown={handleKeyDown}
        rows="1"
        class="w-full min-h-[48px] p-2 bg-white text-surface-900 resize-none text-base focus:outline-none placeholder:text-surface-400"
      ></textarea>
    </div>
    
    <div class="flex items-center justify-between w-full mb-3">
      <div class="relative">
        <select 
          bind:value={selectedModel} 
          class="custom-select"
        >
          <!-- Anthropic Models -->
          <optgroup label="Anthropic">
            <option value="claude-3-7-sonnet-20250219">Claude 3.7 Sonnet</option>
            <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
            <option value="claude-3-opus-20240229">Claude 3 Opus</option>
            <option value="claude-3-5-haiku-20241022">Claude 3.5 Haiku</option>
          </optgroup>

          <!-- OpenAI Models -->
          <optgroup label="OpenAI">
            <option value="gpt-4o">GPT-4o (Latest Flagship)</option>
            <option value="gpt-4o-mini">GPT-4o Mini (Fast & Affordable)</option>
            <option value="o1">O1 (Complex Reasoning)</option>
            <option value="o1-mini">O1 Mini (Fast Reasoning)</option>
            <option value="o3-mini">O3 Mini (Latest Fast Reasoning)</option>
          </optgroup>

          <!-- Perplexity Models -->
          <optgroup label="Perplexity">
            <option value="sonar-reasoning-pro">Sonar Reasoning Pro (127k)</option>
            <option value="sonar-reasoning">Sonar Reasoning (127k)</option>
            <option value="sonar-pro">Sonar Pro (200k)</option>
            <option value="sonar">Sonar (127k)</option>
          </optgroup>
        </select>
        <svg 
          class="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none w-3 h-3 text-surface-900-50-token fill-current" 
          viewBox={`0 0 ${faAngleDown.icon[0]} ${faAngleDown.icon[1]}`}
        >
          <path d={String(faAngleDown.icon[4])} />
        </svg>
      </div>

      <div class="relative">
        <select 
          class="custom-select"
        >
          <option value="user-project">Use a project</option>
        </select>
        <svg 
          class="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none w-3 h-3 text-surface-900-50-token fill-current" 
          viewBox={`0 0 ${faAngleDown.icon[0]} ${faAngleDown.icon[1]}`}
        >
          <path d={String(faAngleDown.icon[4])} />
        </svg>
      </div>
    </div>

    <div class="flex flex-col gap-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <!-- Hidden file input with multiple attribute -->
          <input
            type="file"
            bind:this={fileInput}
            class="hidden"
            accept=".pdf,.doc,.docx,.txt"
            on:change={handleFileSelect}
            multiple
          />
          
          <button 
            class="btn-icon variant-soft hover:variant-soft-hover" 
            aria-label="Attach file"
            on:click={() => fileInput.click()}
            disabled={isUploading}
          >
            <svg class="w-3.5 h-3.5 text-surface-900-50-token fill-current" viewBox={`0 0 ${faPaperclip.icon[0]} ${faPaperclip.icon[1]}`}>
              <path d={String(faPaperclip.icon[4])} />
            </svg>
          </button>
          <button class="btn-icon variant-soft hover:variant-soft-hover" aria-label="Take photo">
            <svg class="w-3.5 h-3.5 text-surface-900-50-token fill-current" viewBox={`0 0 ${faCamera.icon[0]} ${faCamera.icon[1]}`}>
              <path d={String(faCamera.icon[4])} />
            </svg>
          </button>
          <button class="btn-icon variant-soft hover:variant-soft-hover" aria-label="Open Google Drive">
            <svg class="w-3.5 h-3.5 text-surface-900-50-token fill-current" viewBox={`0 0 ${faGoogleDriveBrand.icon[0]} ${faGoogleDriveBrand.icon[1]}`}>
              <path d={String(faGoogleDriveBrand.icon[4])} />
            </svg>
          </button>
        </div>
        
        <button 
          class="btn-icon bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed" 
          aria-label="Submit"
          on:click={handleSubmit}
          disabled={isLoading || (!inputValue.trim() && selectedFiles.length === 0)}
        >
          <svg class="w-3.5 h-3.5 text-black fill-current" viewBox={`0 0 ${faChevronRight.icon[0]} ${faChevronRight.icon[1]}`}>
            <path d={String(faChevronRight.icon[4])} />
          </svg>
        </button>
      </div>

      <!-- Selected files list -->
      {#if selectedFiles.length > 0}
        <div class="flex flex-col gap-2">
          {#each selectedFiles as file, i}
            <div class="flex items-center justify-between p-2 bg-surface-100 dark:bg-surface-800 rounded-container-token">
              <span class="text-sm text-surface-900 dark:text-surface-50">{file.name}</span>
              <button
                class="btn-icon variant-soft hover:variant-soft-hover"
                aria-label="Remove file"
                on:click={() => removeFile(i)}
              >
                <svg class="w-3.5 h-3.5 text-surface-900-50-token fill-current" viewBox={`0 0 ${faXmark.icon[0]} ${faXmark.icon[1]}`}>
                  <path d={String(faXmark.icon[4])} />
                </svg>
              </button>
            </div>
          {/each}
        </div>
      {/if}
    </div>
    
    {#if uploadStatus || processingStatus}
      <div class="mt-3 text-sm">
        {#if uploadStatus}
          <p class="text-surface-600 dark:text-surface-300">{uploadStatus}</p>
        {/if}
        {#if processingStatus}
          <p class="text-surface-600 dark:text-surface-300">{processingStatus}</p>
        {/if}
      </div>
    {/if}
  </div>
</div>

<style>
  /* Custom border styles for light/dark mode */
  .custom-border {
    @apply border;
  }

  :global(.light) .custom-border {
    border-color: rgb(var(--color-surface-100) / 1);
  }

  :global(.dark) .custom-border {
    border-color: rgb(var(--color-surface-500) / 1);
  }

  /* Custom button icon styling */
  :global(.btn-icon.variant-soft) {
    @apply bg-surface-100 hover:bg-surface-300;
  }

  :global(.dark) :global(.btn-icon.variant-soft) {
    @apply bg-surface-600 hover:bg-surface-500;
  }

  /* Custom select styling */
  .custom-select {
    @apply appearance-none text-sm px-4 py-2 rounded-container-token;
    @apply bg-surface-50 text-surface-900;
    @apply border;
    @apply focus:outline-none focus:ring-2 focus:ring-primary-500;
    @apply hover:bg-surface-100;
    @apply pr-8; /* Space for the custom arrow icon */
  }

  :global(.light) .custom-select {
    border-color: rgb(var(--color-surface-100) / 1);
  }

  :global(.dark) .custom-select {
    @apply bg-surface-900 text-surface-50;
    @apply hover:bg-surface-800;
    border-color: rgb(var(--color-surface-500) / 1);
  }

  /* Remove default select arrow */
  .custom-select::-ms-expand {
    display: none;
  }

  /* For Firefox */
  .custom-select {
    -moz-appearance: none;
  }

  /* For Chrome/Safari */
  .custom-select::-webkit-appearance {
    -webkit-appearance: none;
  }
</style> 