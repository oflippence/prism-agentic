<script lang="ts">
  import { ProgressBar } from '@skeletonlabs/skeleton';

  let progress = 65;
  let tags = ['Tailwind', 'Skeleton UI', 'Svelte'];
</script>

<div class="card variant-filled-surface p-4 space-y-4">
  <!-- Header with Avatar -->
  <header class="flex items-center gap-4">
    <div class="avatar bg-primary-500 flex items-center justify-center w-12 h-12 rounded-full">
      <span class="text-xl font-bold text-white">TS</span>
    </div>
    <div>
      <h3 class="h3">Complex Test Component</h3>
      <p class="opacity-75">Created with Tailwind & Skeleton</p>
    </div>
  </header>

  <!-- Content Section -->
  <div class="card variant-ghost p-4 space-y-4">
    <div class="flex justify-between items-center">
      <span class="badge variant-filled-success">Status: Active</span>
      <span class="badge variant-soft-primary">Premium</span>
    </div>
    
    <!-- Progress Bar -->
    <div class="space-y-2">
      <div class="flex justify-between">
        <span>Progress</span>
        <span>{progress}%</span>
      </div>
      <ProgressBar value={progress} />
    </div>

    <!-- Tags -->
    <div class="flex flex-wrap gap-2">
      {#each tags as tag}
        <span class="chip variant-filled">{tag}</span>
      {/each}
    </div>
  </div>

  <!-- Actions -->
  <footer class="flex justify-end gap-2">
    <button type="button" class="btn variant-soft">Cancel</button>
    <button type="button" class="btn variant-filled-primary">Save Changes</button>
  </footer>
</div>

<style>
  /* Custom styles that work alongside Tailwind/Skeleton */

</style> 