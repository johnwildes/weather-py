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
export declare const IMPACT_LABELS: readonly ["impact-1", "impact-2", "impact-3", "impact-4", "impact-5"];
export declare const ASSESSED_LABEL = "assessed";
export declare const REASSESS_LABEL = "re-assess";
export declare const MANUAL_REVIEW_LABEL = "needs-manual-review";
export type ImpactLabel = (typeof IMPACT_LABELS)[number];
export declare const IMPACT_DESCRIPTIONS: Record<number, string>;
