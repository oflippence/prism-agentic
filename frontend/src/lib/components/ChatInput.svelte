<script lang="ts">
  // Import icons directly from Font Awesome Pro packages
  import { faPaperclip, faCamera, faAngleDown, faChevronRight } from '@fortawesome/pro-solid-svg-icons';
  import { faGoogleDrive as faGoogleDriveBrand } from '@fortawesome/free-brands-svg-icons/faGoogleDrive';
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();
  let inputValue = '';
  let selectedModel = 'claude-3-5-sonnet-20240620';
  let isLoading = false;

  // Get backend URL from environment with fallback
  const backendUrl = import.meta.env?.PUBLIC_BACKEND_URL || 'http://localhost:3001';
  console.log('[DEBUG] Environment mode:', import.meta.env.MODE);
  console.log('[DEBUG] Backend URL:', backendUrl);
  
  if (!backendUrl.startsWith('http')) {
    console.error('[DEBUG] Invalid backend URL format:', backendUrl);
  }

  async function handleSubmit() {
    if (!inputValue.trim()) return;
    
    // Emit message immediately for display
    dispatch('message', {
      question: inputValue,
      answer: null // Indicates this message is pending a response
    });
    
    isLoading = true;
    try {
      // Send to backend for processing and response
      console.log('[DEBUG] Attempting to send request to:', `${backendUrl}/webhook/chat`);
      console.log('[DEBUG] Request payload:', {
        message: inputValue,
        model: selectedModel
      });
      
      const response = await fetch(`${backendUrl}/webhook/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue,
          model: selectedModel
        })
      });

      console.log('[DEBUG] Response status:', response.status);
      console.log('[DEBUG] Response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[DEBUG] Error response body:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }
      
      const text = await response.text(); // First get the raw text
      let responseData;
      
      try {
        responseData = JSON.parse(text); // Then try to parse it
        console.log('Raw response text:', text);
        console.log('Parsed response data:', responseData);
        console.log('Response data type:', typeof responseData);
        console.log('Response data keys:', Object.keys(responseData));
      } catch (e) {
        console.error('Failed to parse response:', text);
        throw new Error('Invalid JSON response from server');
      }

      // Check for error field first
      if (responseData.error) {
        throw new Error(responseData.error);
      }

      // Handle the response - if we have question/answer directly or need to extract from response_data
      const question = responseData.question || inputValue;
      const answer = responseData.answer || 'No response generated';

      console.log('Question value:', question);
      console.log('Answer value:', answer);
      console.log('Answer type:', typeof answer);
      console.log('Answer length:', answer ? answer.length : 0);
      
      if (!answer || answer === 'No response generated') {
        console.error('No valid answer in response:', responseData);
        throw new Error('No valid response received from server');
      }

      // Update the pending message with the response
      dispatch('update', {
        question,
        answer
      });
      
      // Clear input after successful send
      inputValue = '';
    } catch (error: any) {
      console.error('Error sending message:', error);
      dispatch('error', { error: error.message || 'Failed to get response from chatbot' });
    } finally {
      isLoading = false;
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
            <option value="claude-3-5-sonnet-20240620">Claude 3.5 Sonnet</option>
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

    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <button class="btn-icon variant-soft hover:variant-soft-hover" aria-label="Attach file">
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
        disabled={isLoading || !inputValue.trim()}
      >
        <svg class="w-3.5 h-3.5 text-black fill-current" viewBox={`0 0 ${faChevronRight.icon[0]} ${faChevronRight.icon[1]}`}>
          <path d={String(faChevronRight.icon[4])} />
        </svg>
      </button>
    </div>
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