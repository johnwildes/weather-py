/**
 * GitHub Models LLM client for issue severity assessment
 */

import * as core from '@actions/core';
import { IssueContext, AssessmentResult, IMPACT_DESCRIPTIONS } from './types';

const GITHUB_MODELS_ENDPOINT = 'https://models.github.ai/inference/chat/completions';
const MODEL_NAME = 'openai/gpt-4o';

/**
 * Build the assessment prompt for the LLM
 */
function buildPrompt(issue: IssueContext): string {
  const scoringGuide = Object.entries(IMPACT_DESCRIPTIONS)
    .map(([score, desc]) => `${score} = ${desc}`)
    .join('\n');

  return `You are a GitHub issue triage assistant. Analyze this issue and provide a severity assessment.

## Issue Details
**Title:** ${issue.title}
**Repository:** ${issue.repository}
**Author:** @${issue.author}
**Existing Labels:** ${issue.labels.length > 0 ? issue.labels.join(', ') : 'None'}

**Description:**
${issue.body || 'No description provided.'}

## Your Task
Assess the impact and severity of this issue. Consider:
- Scope of affected functionality
- Potential for breaking changes
- Security implications
- User impact
- Urgency

## Scoring Guide
${scoringGuide}

## Response Format
Respond with ONLY a valid JSON object (no markdown, no explanation):
{
  "impact_score": <number 1-5>,
  "summary": "<brief 1-2 sentence summary of the issue>",
  "rationale": "<explanation of why this score was assigned>",
  "suggested_actions": ["<action 1>", "<action 2>"]
}`;
}

/**
 * Parse LLM response into AssessmentResult
 */
function parseResponse(responseText: string): AssessmentResult {
  // Try to extract JSON from the response
  let jsonStr = responseText.trim();
  
  // Handle markdown code blocks
  const jsonMatch = jsonStr.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (jsonMatch) {
    jsonStr = jsonMatch[1].trim();
  }

  const parsed = JSON.parse(jsonStr);
  
  // Validate required fields
  if (typeof parsed.impact_score !== 'number' || 
      parsed.impact_score < 1 || 
      parsed.impact_score > 5) {
    throw new Error('Invalid impact_score: must be a number between 1 and 5');
  }

  if (typeof parsed.summary !== 'string' || !parsed.summary) {
    throw new Error('Invalid summary: must be a non-empty string');
  }

  if (typeof parsed.rationale !== 'string' || !parsed.rationale) {
    throw new Error('Invalid rationale: must be a non-empty string');
  }

  if (!Array.isArray(parsed.suggested_actions)) {
    parsed.suggested_actions = [];
  }

  return {
    impact_score: parsed.impact_score as 1 | 2 | 3 | 4 | 5,
    summary: parsed.summary,
    rationale: parsed.rationale,
    suggested_actions: parsed.suggested_actions,
  };
}

/**
 * Call GitHub Models API to assess the issue
 */
export async function assessIssue(
  issue: IssueContext,
  token: string
): Promise<AssessmentResult> {
  const prompt = buildPrompt(issue);
  
  core.debug('Calling GitHub Models API...');
  
  const response = await fetch(GITHUB_MODELS_ENDPOINT, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: MODEL_NAME,
      messages: [
        {
          role: 'system',
          content: 'You are a precise issue triage assistant. Always respond with valid JSON only.',
        },
        {
          role: 'user',
          content: prompt,
        },
      ],
      temperature: 0.3,
      max_tokens: 500,
    }),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`GitHub Models API error (${response.status}): ${errorBody}`);
  }

  const data = await response.json() as {
    choices: Array<{ message: { content: string } }>;
  };
  
  if (!data.choices || data.choices.length === 0) {
    throw new Error('No response from GitHub Models API');
  }

  const content = data.choices[0].message.content;
  core.debug(`LLM Response: ${content}`);
  
  return parseResponse(content);
}
