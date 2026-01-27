/**
 * CODEOWNERS file parser
 * Extracts team/user ownership from the repository's CODEOWNERS file
 */

import * as github from '@actions/github';
import * as core from '@actions/core';
import { CodeOwnerEntry } from './types';

/**
 * Parse CODEOWNERS file content into structured entries
 */
export function parseCodeOwners(content: string): CodeOwnerEntry[] {
  const entries: CodeOwnerEntry[] = [];
  const lines = content.split('\n');

  for (const line of lines) {
    const trimmed = line.trim();
    
    // Skip empty lines and comments
    if (!trimmed || trimmed.startsWith('#')) {
      continue;
    }

    // Split into pattern and owners
    const parts = trimmed.split(/\s+/);
    if (parts.length >= 2) {
      const pattern = parts[0];
      const owners = parts.slice(1).filter(owner => 
        owner.startsWith('@') || owner.includes('@')
      );
      
      if (owners.length > 0) {
        entries.push({ pattern, owners });
      }
    }
  }

  return entries;
}

/**
 * Get the default/root owners from CODEOWNERS
 * These are typically defined with pattern '*' or '/'
 */
export function getDefaultOwners(entries: CodeOwnerEntry[]): string[] {
  // Look for catch-all patterns
  const defaultEntry = entries.find(e => 
    e.pattern === '*' || e.pattern === '/' || e.pattern === '/*'
  );
  
  if (defaultEntry) {
    return defaultEntry.owners;
  }

  // If no default, return the first entry's owners as fallback
  if (entries.length > 0) {
    return entries[0].owners;
  }

  return [];
}

/**
 * Fetch and parse CODEOWNERS from the repository
 */
export async function fetchCodeOwners(
  octokit: ReturnType<typeof github.getOctokit>,
  owner: string,
  repo: string
): Promise<CodeOwnerEntry[]> {
  // CODEOWNERS can be in root, .github/, or docs/
  const possiblePaths = [
    'CODEOWNERS',
    '.github/CODEOWNERS',
    'docs/CODEOWNERS',
  ];

  for (const path of possiblePaths) {
    try {
      const response = await octokit.rest.repos.getContent({
        owner,
        repo,
        path,
      });

      if ('content' in response.data && response.data.type === 'file') {
        const content = Buffer.from(response.data.content, 'base64').toString('utf-8');
        core.debug(`Found CODEOWNERS at ${path}`);
        return parseCodeOwners(content);
      }
    } catch (error) {
      // File not found at this path, try next
      continue;
    }
  }

  core.warning('No CODEOWNERS file found in repository');
  return [];
}

/**
 * Extract team names from owners (filter out individual users)
 */
export function extractTeams(owners: string[]): string[] {
  return owners.filter(owner => owner.includes('/'));
}

/**
 * Extract individual users from owners (filter out teams)
 */
export function extractUsers(owners: string[]): string[] {
  return owners.filter(owner => owner.startsWith('@') && !owner.includes('/'));
}
