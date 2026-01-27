/**
 * Type definitions for the Issue Review Agent
 */

export interface IssueContext {
  number: number;
  title: string;
  body: string;
  author: string;
  repository: string;
  labels: string[];
}

export interface AssessmentResult {
  impact_score: 1 | 2 | 3 | 4 | 5;
  summary: string;
  rationale: string;
  suggested_actions: string[];
}

export interface CodeOwnerEntry {
  pattern: string;
  owners: string[];
}

export const IMPACT_LABELS = [
  'impact-1',
  'impact-2',
  'impact-3',
  'impact-4',
  'impact-5',
] as const;

export const ASSESSED_LABEL = 'assessed';
export const REASSESS_LABEL = 're-assess';
export const MANUAL_REVIEW_LABEL = 'needs-manual-review';

export type ImpactLabel = (typeof IMPACT_LABELS)[number];

export const IMPACT_DESCRIPTIONS: Record<number, string> = {
  1: 'Minimal impact (typo, cosmetic, minor docs)',
  2: 'Low impact (small bug, minor feature request)',
  3: 'Medium impact (moderate bug, standard feature)',
  4: 'High impact (significant bug, breaking change risk)',
  5: 'Critical impact (security issue, data loss risk, major outage)',
};
