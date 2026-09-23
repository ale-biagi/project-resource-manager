---
name: resource-matching
description: Multi-step workflow for cross-referencing project demands with employee availability and skills from S/4HANA Cloud and SuccessFactors to propose ranked best-fit candidates
---

# Resource Matching Workflow

Use this skill when the user asks you to find, recommend, or propose candidates for an open resource requirement.

## Prerequisites

Before starting, you must have:
1. A specific resource demand (ProjectDemandWorkUUID or demand details) from a project
2. The required date window (start and end dates) from the demand
3. Availability data retrieved from the Workforce Daily Availability tool
4. Skills and profile data from SuccessFactors tools

## Step 1: Extract Demand Requirements

From the resource demand data, extract:
- Required role / activity type (ActivityType field)
- Required delivery organization (ProjDmndRequestedDeliveryOrg)
- Required start and end dates
- Staffing instruction text (ProjDmndStfngInstructionText) if available
- Assignment status (must be open/unassigned)

Note these requirements as your matching criteria.

## Step 2: Filter Availability by Date Window

Using the demand's start and end dates as your date range:
1. Query the TimeOverviewSet entity filtering by the date range
2. For each employee returned, calculate their total available capacity:
   - Sum `Plannedworkinghours` minus `Absencehours` for non-holiday, non-absence days
   - Exclude days where `Isnonworkingday = true`
3. Keep only employees with at least 20% available capacity during the demand window
4. Record each employee's: WorkAgreementExternalId, total available hours, and availability percentage

## Step 3: Cross-Reference SuccessFactors Skills

For each available employee from Step 2:
1. Query SkillProfile using the employee's user ID (map from work agreement ID)
2. If SkillProfile exists, query RatedSkillMapping to get all rated skills with proficiency levels
3. Query EmpJob to get current job title, department, location, and employment status
4. Query EPPublicProfile for additional context (introduction, certifications)
5. If SkillProfile does NOT exist, flag this employee as `[Skills data unavailable]` — do NOT omit them

Compile a profile per candidate:
- Name / Employee ID
- Available hours and percentage
- Skills list with proficiency levels
- Job title and department
- Data completeness flags

## Step 4: Score Candidates

Score each candidate (0–100) using these weights:

| Criterion | Weight | How to Score |
|-----------|--------|--------------|
| Skills match | 50% | Count how many required skills (from demand role/activity) the candidate has, divided by total required skills × 50 |
| Availability alignment | 30% | Availability percentage × 30 |
| Employment profile fit | 20% | Job title relevance to demand role × 20 (use 10 if partially relevant, 5 if not relevant) |

**Confidence Levels Based on Data Completeness:**

| Data Available | Confidence Level |
|----------------|-----------------|
| All 3 criteria (availability + skills + profile) | **High** |
| 2 of 3 criteria available | **Medium** — flag in output |
| 1 of 3 criteria available | **Low** — flag prominently in output |

If fewer than 2 criteria are available for any candidate, add: `⚠️ Low-confidence recommendation — [state which data is missing]`

## Step 5: Format Ranked Output

Present the top 3 candidates (or fewer if fewer qualify) in ranked order:

```
## Candidate Recommendations for Demand [Demand ID]

### 🥇 Rank 1: [Employee Name] (Score: XX/100 | Confidence: High/Medium/Low)
**Availability:** XX hours available (XX%) during [date range]
**Skills Match:** [list matching skills with proficiency levels]
**Job Profile:** [Job Title], [Department], [Location]
**Justification:** [2-3 sentences explaining why this person is a good fit — cover skills alignment, availability window, and role relevance]

### 🥈 Rank 2: [Employee Name] ...
### 🥉 Rank 3: [Employee Name] ...
```

If no candidates qualify, report:
```
No suitable candidates found for demand [Demand ID].
Reason: [specific reason — e.g., "No employees with sufficient availability in the required date range", "Skills data unavailable for all available employees", etc.]
```

## Step 6: Offer Next Step

After presenting recommendations, ask the user:
"Would you like to proceed with assigning one of these candidates? If so, please confirm which candidate and I will guide you through the confirmation step."

Do NOT proceed to assignment without explicit user direction.
