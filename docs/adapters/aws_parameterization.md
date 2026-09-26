# AWS Parameterization Adapters

This document describes the implementation and usage of AWS-based adapters for application configuration and secret management.

## Architecture

The application implements Hexagonal Architecture. The AWS adapters are outbound adapters that satisfy the following Ports:

- `SecretsPort`: Interface for retrieving sensitive credentials.
- `ConfigPort`: Interface for retrieving dynamic application settings.

## Adapters

### 1. AWSSecretsManagerAdapter
**Location**: `app/src/adapters/outbounds/aws_secrets_adapter.py`

Uses [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) to store and retrieve integration credentials.

- **Secret Name**: `secrets_bwt` (Default)
- **JSON Structure**:
  ```json
  {
    "OCTADESK_API_KEY": "...",
    "OCTADESK_BASE_URL": "...",
    "OCTADESK_SUBDOMAIN": "...",
    "RDSTATION_TOKEN": "..."
  }
  ```

### 2. AWSParameterStoreAdapter
**Location**: `app/src/adapters/outbounds/aws_config_adapter.py`

Uses [AWS Systems Manager Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) for dynamic configurations.

- **Parameters**:
  - `/bwt/scheduler/enabled`: Boolean string (`"true"`/`"false"`).
  - `/bwt/scheduler/cron`: Crontab expression (e.g., `* 5-16 * * *`).
  - `/bwt/scheduler/batch_size`: Integer string (e.g., `"50"`).

## Dynamic Configuration Polling

The `SyncronizerScheduler` (Inbound Adapter) polls the Parameter Store every **5 minutes**.

- **Cron Updates**: If the cron expression changes in SSM, the background job is automatically rescheduled using APScheduler's `reschedule_job`.
- **Batch Size**: The `OrchestratorService` batch size is updated immediately upon detection of change in SSM.
- **Enable/Disable**: If `enabled` is set to `false`, the synchronization job skips execution until re-enabled.

## Fallback Strategy

To ensure high availability:
1. **Secrets**: If AWS Secrets Manager is unreachable, the application continues with credentials provided via local environment variables.
2. **Parameters**: If SSM is unreachable, safe defaults are used:
   - `enabled`: `True`
   - `cron`: `*/5 * * * *`
   - `batch_size`: `10`
