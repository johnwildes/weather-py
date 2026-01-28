/**
 * GitHub Models LLM client for issue severity assessment
 */
import { IssueContext, AssessmentResult } from './types';
/**
 * Call GitHub Models API to assess the issue
 */
export declare function assessIssue(issue: IssueContext, token: string): Promise<AssessmentResult>;
