<script>
  // Import icons directly from Font Awesome Pro packages
  import { faPaperclip, faCamera, faAngleDown, faChevronRight } from '@fortawesome/pro-solid-svg-icons';
  import { faGoogleDrive as faGoogleDriveBrand } from '@fortawesome/free-brands-svg-icons/faGoogleDrive';

  let inputValue = '';
  let selectedModel = 'Claude 3.5 Sonnet';
</script>

<div class="w-full">
  <div class="w-full bg-surface-50-900-token border custom-border rounded-container-token p-4">
    <div class="bg-white rounded-container-token p-3 mb-3">
      <textarea
        placeholder="How can Prism help you today?"
        bind:value={inputValue}
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
          <option value="Claude 3.5 Sonnet">Claude 3.5 Sonnet</option>
          <!-- Add other models as needed -->
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
      
      <button class="btn-icon bg-primary-600 hover:bg-primary-700" aria-label="Submit">
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