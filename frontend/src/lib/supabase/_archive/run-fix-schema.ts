// Script to run the SQL fix directly in Supabase
// Run with: npx ts-node run-fix-schema.ts

import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get the directory name
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Read environment variables from .env file
const envPath = path.resolve(__dirname, '../../../.env');
const envContent = fs.readFileSync(envPath, 'utf8');
const env: Record<string, string> = {};

envContent.split('\n').forEach(line => {
  const match = line.match(/^([^#=]+)=(.*)$/);
  if (match) {
    const key = match[1].trim();
    const value = match[2].trim().replace(/^['"]|['"]$/g, ''); // Remove quotes if present
    env[key] = value;
  }
});

// Initialize Supabase client
const supabaseUrl = env['SUPABASE_URL'];
const supabaseKey = env['SUPABASE_SERVICE_KEY'];

if (!supabaseUrl || !supabaseKey) {
  console.error('Missing Supabase credentials. Please add SUPABASE_URL and SUPABASE_SERVICE_KEY to your .env file.');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function runFixSchema() {
  try {
    console.log('Reading SQL fix script...');
    const sqlPath = path.join(__dirname, 'fix-schema.sql');
    const sql = fs.readFileSync(sqlPath, 'utf8');
    
    console.log('Executing SQL fix script...');
    
    // Split the SQL into separate statements
    const statements = sql.split(';').filter(stmt => stmt.trim());
    
    for (const statement of statements) {
      if (statement.trim()) {
        console.log(`Executing: ${statement.trim().substring(0, 50)}...`);
        
        // Execute each statement
        const { error } = await supabase.rpc('exec_sql', { sql: statement });
        
        if (error) {
          console.error('Error executing SQL statement:', error.message);
        }
      }
    }
    
    console.log('SQL fix script executed successfully!');
    
    // Verify the documents table structure
    const { data, error } = await supabase
      .from('documents')
      .select('id, name, file_path')
      .limit(1);
    
    if (error) {
      console.error('Error verifying documents table:', error.message);
    } else {
      console.log('Documents table verified successfully!');
      if (data && data.length > 0) {
        console.log('Table structure:', Object.keys(data[0]).join(', '));
      } else {
        console.log('Table is empty, but structure is verified.');
      }
    }
  } catch (error) {
    console.error('Unexpected error:', error);
  }
}

runFixSchema(); 