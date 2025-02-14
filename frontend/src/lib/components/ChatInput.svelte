<script>
  // Import icons directly from Font Awesome Pro packages
  import { faPaperclip, faCamera, faAngleDown } from '@fortawesome/pro-solid-svg-icons';
  import { faGoogleDrive as faGoogleDriveBrand } from '@fortawesome/free-brands-svg-icons/faGoogleDrive';

  let inputValue = '';
  let selectedModel = 'Claude 3.5 Sonnet';
</script>

<div class="w-full">
  <div class="w-full bg-surface-50-900-token border border-surface-300-600-token rounded-2xl p-4">
    <div class="bg-surface-100-800-token rounded-xl p-3 mb-3">
      <textarea
        placeholder="How can Prism help you today?"
        bind:value={inputValue}
        rows="1"
        class="w-full min-h-[48px] p-2 bg-transparent resize-none text-base focus:outline-none placeholder:text-surface-500-400-token"
      ></textarea>
    </div>
    
    <div class="flex items-center gap-2 mb-3">
      <div class="relative">
        <select 
          bind:value={selectedModel} 
          class="appearance-none bg-transparent pr-6 pl-2 py-2 text-sm text-surface-900-50-token cursor-pointer focus:outline-none"
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
      
      <div>
        <button class="btn variant-soft hover:variant-soft-hover">
          Use a project
        </button>
      </div>
    </div>
  </div>
</div>

<style>
  /* Remove all custom styles as we're using Tailwind classes */
</style> 