# Chat Version 1 (Backup)

This directory contains a backup of the original chat implementation that used Universal Agents branding and backend system prompts.

## Files

- `+page.svelte`: Original home page implementation
- `components/ChatInput.svelte`: Original chat input component

## Usage

To revert to this version:

1. Copy `+page.svelte` back to `frontend/src/routes/+page.svelte`
2. Copy `components/ChatInput.svelte` back to `frontend/src/lib/components/ChatInput.svelte`
3. Update any imports in `+page.svelte` to point to the correct component paths

Note: This version uses the original backend system prompts and Universal Agents branding. It does not use the n8n workflow for system prompts or the PRISM branding. 