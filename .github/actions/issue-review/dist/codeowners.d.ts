/**
 * CODEOWNERS file parser
 * Extracts team/user ownership from the repository's CODEOWNERS file
 */
import * as github from '@actions/github';
import { CodeOwnerEntry } from './types';
/**
 * Parse CODEOWNERS file content into structured entries
 */
export declare function parseCodeOwners(content: string): CodeOwnerEntry[];
/**
 * Get the default/root owners from CODEOWNERS
 * These are typically defined with pattern '*' or '/'
 */
export declare function getDefaultOwners(entries: CodeOwnerEntry[]): string[];
/**
 * Fetch and parse CODEOWNERS from the repository
 */
export declare function fetchCodeOwners(octokit: ReturnType<typeof github.getOctokit>, owner: string, repo: string): Promise<CodeOwnerEntry[]>;
/**
 * Extract team names from owners (filter out individual users)
 */
export declare function extractTeams(owners: string[]): string[];
/**
 * Extract individual users from owners (filter out teams)
 */
export declare function extractUsers(owners: string[]): string[];
