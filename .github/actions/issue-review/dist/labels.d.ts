/**
 * Label management utilities for the Issue Review Agent
 */
import * as github from '@actions/github';
type Octokit = ReturnType<typeof github.getOctokit>;
/**
 * Ensure required labels exist in the repository
 */
export declare function ensureLabelsExist(octokit: Octokit, owner: string, repo: string): Promise<void>;
/**
 * Get current labels on an issue
 */
export declare function getIssueLabels(octokit: Octokit, owner: string, repo: string, issueNumber: number): Promise<string[]>;
/**
 * Remove all impact labels from an issue
 */
export declare function removeImpactLabels(octokit: Octokit, owner: string, repo: string, issueNumber: number, currentLabels: string[]): Promise<void>;
/**
 * Apply assessment labels to an issue
 */
export declare function applyAssessmentLabels(octokit: Octokit, owner: string, repo: string, issueNumber: number, impactScore: number, currentLabels: string[]): Promise<void>;
/**
 * Apply manual review label on error
 */
export declare function applyManualReviewLabel(octokit: Octokit, owner: string, repo: string, issueNumber: number): Promise<void>;
export {};
