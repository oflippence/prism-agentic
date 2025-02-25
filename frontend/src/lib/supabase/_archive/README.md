# Supabase Schema Fix

This directory contains scripts to fix the Supabase schema for the RAG agent application.

## Problem

The application is encountering the error: "Could not find the 'file_path' column of 'documents' in the schema cache". This happens because:

1. The Supabase database schema doesn't match what the frontend code expects
2. The `documents` table might be missing the `file_path` column
3. The schema cache in Supabase might be out of sync

## Solution

We've created two ways to fix this:

### Option 1: Run the SQL script directly in Supabase

1. Go to your Supabase dashboard
2. Open the SQL Editor
3. Copy the contents of `fix-schema.sql`
4. Run the SQL in the editor

### Option 2: Run the automated script

1. Make sure you have Node.js installed
2. Add your Supabase credentials to the `.env` file in the project root:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_KEY=your_supabase_service_key
   ```
3. Navigate to this directory: `cd frontend/src/lib/supabase`
4. Install dependencies: `npm install`
5. Run the fix script: `npm run fix-schema`

## What the Fix Does

1. Creates the `documents` table if it doesn't exist
2. Adds any missing columns to the table, including `file_path`
3. Sets up proper row-level security policies
4. Enables the Vector extension for embeddings

## N8n Webhook Connection

If you're having issues with the N8n webhook connection:

1. Make sure N8n is running: `docker-compose up n8n`
2. Check that the webhook URL in `frontend/src/routes/test/+page.svelte` matches your N8n setup
3. The default URL is `http://n8n:5678/webhook/process-document` which works in Docker networking
4. If running locally without Docker, change it to `http://localhost:5678/webhook/process-document`

## Troubleshooting

- If you still see the error after running the fix, try clearing your browser cache
- Check the browser console for detailed error messages
- Verify that the document is being uploaded to Supabase storage successfully
- Check the N8n logs for any webhook processing errors 