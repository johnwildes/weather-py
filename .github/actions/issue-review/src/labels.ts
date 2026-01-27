/**
 * Label management utilities for the Issue Review Agent
 */

import * as github from '@actions/github';
import * as core from '@actions/core';
import {
  IMPACT_LABELS,
  ASSESSED_LABEL,
  REASSESS_LABEL,
  MANUAL_REVIEW_LABEL,
  ImpactLabel,
} from './types';

type Octokit = ReturnType<typeof github.getOctokit>;

/**
 * Ensure required labels exist in the repository
 */
export async function ensureLabelsExist(
  octokit: Octokit,
  owner: string,
  repo: string
): Promise<void> {
  const labelsToCreate = [
    { name: ASSESSED_LABEL, color: '0e8a16', description: 'Issue has been assessed by the review agent' },
    { name: REASSESS_LABEL, color: 'fbca04', description: 'Request re-assessment of this issue' },
    { name: MANUAL_REVIEW_LABEL, color: 'd93f0b', description: 'Requires manual review - automated assessment failed' },
    { name: 'impact-1', color: 'c5def5', description: 'Minimal impact change' },
    { name: 'impact-2', color: '7dd3fc', description: 'Low impact change' },
    { name: 'impact-3', color: 'fcd34d', description: 'Medium impact change' },
    { name: 'impact-4', color: 'fb923c', description: 'High impact change' },
    { name: 'impact-5', color: 'ef4444', description: 'Critical impact change' },
  ];

  for (const label of labelsToCreate) {
    try {
      await octokit.rest.issues.createLabel({
        owner,
        repo,
        name: label.name,
        color: label.color,
        description: label.description,
      });
      core.debug(`Created label: ${label.name}`);
    } catch (error: unknown) {
      // Label already exists (422 error) - that's fine
      if (error instanceof Error && 'status' in error && (error as { status: number }).status !== 422) {
        core.warning(`Failed to create label ${label.name}: ${error.message}`);
      }
    }
  }
}

/**
 * Get current labels on an issue
 */
export async function getIssueLabels(
  octokit: Octokit,
  owner: string,
  repo: string,
  issueNumber: number
): Promise<string[]> {
  const response = await octokit.rest.issues.listLabelsOnIssue({
    owner,
    repo,
    issue_number: issueNumber,
  });

  return response.data.map(label => label.name);
}

/**
 * Remove all impact labels from an issue
 */
export async function removeImpactLabels(
  octokit: Octokit,
  owner: string,
  repo: string,
  issueNumber: number,
  currentLabels: string[]
): Promise<void> {
  for (const label of currentLabels) {
    if (IMPACT_LABELS.includes(label as ImpactLabel)) {
      try {
        await octokit.rest.issues.removeLabel({
          owner,
          repo,
          issue_number: issueNumber,
          name: label,
        });
        core.debug(`Removed label: ${label}`);
      } catch (error) {
        core.warning(`Failed to remove label ${label}`);
      }
    }
  }
}

/**
 * Apply assessment labels to an issue
 */
export async function applyAssessmentLabels(
  octokit: Octokit,
  owner: string,
  repo: string,
  issueNumber: number,
  impactScore: number,
  currentLabels: string[]
): Promise<void> {
  // Remove old impact labels first
  await removeImpactLabels(octokit, owner, repo, issueNumber, currentLabels);

  // Build list of labels to add
  const labelsToAdd: string[] = [];

  // Add assessed label if not present
  if (!currentLabels.includes(ASSESSED_LABEL)) {
    labelsToAdd.push(ASSESSED_LABEL);
  }

  // Add impact label
  const impactLabel = `impact-${impactScore}` as ImpactLabel;
  labelsToAdd.push(impactLabel);

  if (labelsToAdd.length > 0) {
    await octokit.rest.issues.addLabels({
      owner,
      repo,
      issue_number: issueNumber,
      labels: labelsToAdd,
    });
    core.debug(`Added labels: ${labelsToAdd.join(', ')}`);
  }

  // Remove re-assess label if present
  if (currentLabels.includes(REASSESS_LABEL)) {
    try {
      await octokit.rest.issues.removeLabel({
        owner,
        repo,
        issue_number: issueNumber,
        name: REASSESS_LABEL,
      });
      core.debug(`Removed label: ${REASSESS_LABEL}`);
    } catch (error) {
      core.warning(`Failed to remove ${REASSESS_LABEL} label`);
    }
  }
}

/**
 * Apply manual review label on error
 */
export async function applyManualReviewLabel(
  octokit: Octokit,
  owner: string,
  repo: string,
  issueNumber: number
): Promise<void> {
  await octokit.rest.issues.addLabels({
    owner,
    repo,
    issue_number: issueNumber,
    labels: [MANUAL_REVIEW_LABEL],
  });
  core.debug(`Added label: ${MANUAL_REVIEW_LABEL}`);
}
