---
name: deploy-solution
description: Deploys the solution. Requires solution.yaml per skill `setup-solution`.
metadata:
  version: 1.0.0
  author: sap-joule-studio
---

Deploys the solution using either the `deploy_solution` tool or the `joule-studio-cli` CLI. Current working directory must be the solution root (containing `solution.yaml`).

# Pre-deployment Test Check

Before deploying, run the structure tests for every `agent` asset in the solution. These tests catch broken imports and missing dependencies — the most common cause of deployment 500 errors — without requiring AI Core credentials.

For each agent asset path listed in `solution.yaml` (i.e. each `assets/<agent-name>/` whose `asset.yaml` has `type: agent`):

```bash
python -m pytest assets/<agent-name> -m structure -v
```

- If **all structure tests pass**: proceed to the quota check and deployment.
- If **any structure test fails**: stop immediately. Do NOT deploy. Show the pytest output to the user and ask them to fix the issues before retrying.

# Pre-deployment Quota Check

Before deploying, always call `get_deployment_quota` to check current usage.

- If `status` is `ok`, or `unlimited` is `true`: proceed with deployment immediately and skip the rest of this section.
- If `status` is `softWarning`, `hardWarning`, or `exceeded`: call `ask_question` with `variant: "deployQuota"` and an empty `question` string (the card renders its own copy). This call **blocks** until the user clicks a button and returns their answer:
  - `"deploy"`: the user chose to proceed anyway — continue with deployment.
  - `"cancel"`: the user chose to discard the current deployment — **do NOT deploy.** Abandon the deployment task.
- Only continue with deployment when the returned answer is `"deploy"`.

**CRITICAL:** Method 1 (tools) is ALWAYS the preferred and default path. Always attempt Method 1 first. Only fall back to Method 2 (CLI) if the Method 1 tools are genuinely unavailable in your environment. Follow this deployment order:
1. **Always try Method 1 first** — use the tools: `deploy_solution`, `get_deployment_job`, `get_deployment_job_logs`.
2. Only if these tools are unavailable, invoke the skill from **Method 2**.
3. If neither the tools nor the CLI is available, inform the user that deployment cannot proceed and explain why.

**CRITICAL — Method 1 and Method 2 are mutually exclusive:** If the Method 1 tools are available, use them exclusively. In that case you MUST NOT use, mention, reference, or suggest the CLI (`jl`) or the `joule-studio-cli` skill anywhere — not in commands, not in the deployment summary, not in troubleshooting. The CLI is only ever used or discussed when the tools are unavailable.

**CRITICAL:** If deployment fails, times out, or encounters any error:
- Return an error message that clearly states the failure and its cause.
- Only attempt minor configuration file tweaks when appropriate.
- Ask for user permission before making any changes.
- Never delete configuration files or assets.
- If the issue cannot be resolved with minor tweaks, report that manual intervention is required.
- **If the Method 1 tools are present: NEVER mention, reference, or suggest the CLI (`jl`, `joule-studio-cli`) as an alternative or fallback — not even when deployment fails repeatedly, times out, or cannot be resolved.**

# Method 1: Deploy Solution using tools ONLY

Deploy the solution using the `deploy_solution` tool, if it is available, DO NOT try anything else to deploy. **If `deploy_solution` is available, you must use it exclusively — no matter what happens (failure, timeout, repeated errors), never fall back to or mention the CLI.**

## Method 1: Check Deployment Status

Check the deployment status using the `get_deployment_job` tool, if it is available. DO NOT try anything else to check the deployment status.

## Method 1: Deployment Result
Always store the result in `deploy_result.json` in the following format:

```json
{ "solution_id": "<some_uuid>" }
```

## Method 1: Debugging

If the deployment fails, fetch the job logs using the `get_deployment_job_logs` tool, if it is available. DO NOT try anything else to fetch the job logs.

# Method 2: Deploy Solution using CLI (ONLY if tools are not available)
Invoke the `joule-studio-cli` skill to deploy the solution via the CLI.

# Reporting the Deployment to the User

After a successful deployment, if the solution contains one or more `agent` assets, include the following message. Replace `<CIS_URL>` and `<tenant_name>` with the values obtained from the method used:

- **Method 1 (tools):** call `get_deployment_info` and use the `accessUrl` field for `<CIS_URL>` and `tenant_name` from the asset entry for `<tenant_name>`.
- **Method 2 (CLI):** use `<issuerUrl>/admin` where `issuerUrl` comes from `jl login` for `<CIS_URL>`. Read `tenant_name` from `deploymentInfo.assets`. If `issuerUrl` is unavailable, omit the URL line and instead tell the user to check their IAS tenant URL.

---

To configure this agent for the production environment, complete a one-time authorization request.

Access the configuration: `<CIS_URL>/admin`
Look for the CIS registration: `<tenant_name>`
For more information, refer to the [SAP Cloud Identity Services help portal](https://help.sap.com/docs/cloud-identity-services/cloud-identity-services/operation-guide?locale=en-US&version=LATEST).

If you don't have administrator access, contact your administrator to complete the required configuration.

---
