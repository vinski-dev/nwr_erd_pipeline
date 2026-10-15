# NWR ERD Data Pipeline

This repository contains the dbt models and CI/CD deployment pipeline for the NWR data platform, transforming raw data into analytics-ready tables in Google BigQuery.

## 🏗 Architecture & Environments

This project uses a dynamically routed CI/CD pipeline via GitHub Actions. Data is automatically built into specific BigQuery datasets based on the Git branch.

| Environment | Git Branch | BigQuery Dataset | Description |
|---|---|---|---|
| Local Dev | Any local branch | `dbt_erd_nwr` | Local developer playground. Uses local `profiles.yml`. |
| Staging | Any feature branch | `dbt_erd_nwr_staging` | Automated CI testing environment. Triggered on push. |
| Production| `main` | `dbt_erd_nwr_prod` | Live production data. Triggered when merged to main. |

## 🚀 CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) automatically:
1. Authenticates securely to Google Cloud using GitHub Secrets (`GCP_SA_KEY`).
2. Dynamically generates a stateless `profiles.yml` on the runner.
3. Executes `dbt deps` and `dbt build` directly into the targeted environment.

## 💻 Local Development Setup

To run this project locally, you will need:
1. A GCP Service Account key saved at `credentials/gcp_key.json` (This folder is git-ignored).
2. A local `~/.dbt/profiles.yml` (or one placed in the `nwr_erd_pipeline` folder) targeting the `dbt_erd_nwr` dataset.

## 🛠 Developer Workflow

To contribute to this project, follow this standard Git workflow to ensure the CI/CD pipeline triggers correctly in staging before reaching production.

1. Clone the repository:
   \`\`\`bash
   git clone https://github.com/vinski-dev/nwr_erd_pipeline.git
   cd nwr_erd_pipeline
   \`\`\`

2. Create a new feature branch:
   Always create a new branch for your work. Pushing to this branch will automatically trigger a dbt build in the `dbt_erd_nwr_staging` dataset.
   \`\`\`bash
   git checkout -b feature/your-feature-name
   \`\`\`

3. Commit and push your changes:
   \`\`\`bash
   git add .
   git commit -m "Description of your changes"
   git push origin feature/your-feature-name
   \`\`\`

4. Deploy to Production:
   Open a Pull Request on GitHub. Once reviewed and merged into the `main` branch, the CI/CD pipeline will automatically build your changes into the `dbt_erd_nwr_prod` dataset.