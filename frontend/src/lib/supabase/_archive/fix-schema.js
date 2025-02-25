// Script to check and fix the Supabase schema
import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';

// Load environment variables
dotenv.config({ path: '../../../.env' });

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('Missing Supabase credentials. Please check your .env file.');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function checkAndFixSchema() {
  console.log('Checking database schema...');
  
  try {
    // Check if documents table exists with the correct structure
    const { data: tableInfo, error: tableError } = await supabase
      .from('documents')
      .select('*')
      .limit(1);
    
    if (tableError) {
      console.log('Error checking documents table:', tableError.message);
      console.log('Attempting to create or update the schema...');
      
      // Read the schema SQL file
      const schemaPath = path.join(process.cwd(), 'src', 'lib', 'supabase', 'schema.sql');
      const schemaSql = fs.readFileSync(schemaPath, 'utf8');
      
      // Execute the schema SQL
      const { error: schemaError } = await supabase.rpc('exec_sql', { sql: schemaSql });
      
      if (schemaError) {
        console.error('Failed to apply schema:', schemaError.message);
      } else {
        console.log('Schema applied successfully!');
      }
    } else {
      console.log('Documents table exists. Checking structure...');
      
      // Check if the file_path column exists
      const { data: columnInfo, error: columnError } = await supabase
        .rpc('get_column_info', { table_name: 'documents', column_name: 'file_path' });
      
      if (columnError || !columnInfo || columnInfo.length === 0) {
        console.log('file_path column not found. Adding it to the documents table...');
        
        // Add the file_path column if it doesn't exist
        const { error: alterError } = await supabase
          .rpc('exec_sql', { 
            sql: 'ALTER TABLE documents ADD COLUMN IF NOT EXISTS file_path TEXT;' 
          });
        
        if (alterError) {
          console.error('Failed to add file_path column:', alterError.message);
        } else {
          console.log('file_path column added successfully!');
        }
      } else {
        console.log('file_path column exists in the documents table.');
      }
    }
    
    console.log('Schema check completed.');
  } catch (error) {
    console.error('Unexpected error:', error);
  }
}

// Run the function
checkAndFixSchema(); 