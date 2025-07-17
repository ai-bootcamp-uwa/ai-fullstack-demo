# GitHub Team Setup Guide

This guide walks you through setting up a GitHub repository for a 4-member team, ensuring smooth collaboration and professional workflow.

---

## 1. Create a GitHub Organization or Repository

- Go to [GitHub](https://github.com/).
- Click the "+" icon in the top right and select **New organization** (recommended for multiple projects) or **New repository**.
- Follow the prompts to name your organization/repo and set visibility (public/private).

## 2. Add Team Members as Collaborators

- Navigate to your repository or organization settings.
- Go to **Manage access** (for repos) or **People** (for orgs).
- Invite all 4 team members by their GitHub usernames.
- Assign appropriate roles:
  - **Owner**: Has full administrative access to the organization and all repositories. Recommended to have at least two owners for redundancy and security (as suggested by GitHub).
  - **Member**: Standard access for contributing to repositories and participating in team activities.
- Review and adjust member roles as needed to ensure smooth project management and security.

## 3. Set Up Branch Protection Rules

- Go to **Settings > Branches** in your repository.
- Add a rule for the `main` branch:
  - Require pull request reviews before merging
  - Require status checks to pass before merging (if using CI)
  - Prevent force pushes and deletions

## 4. Define and Document Branching Strategy

- Decide on a workflow (e.g., `main`, `develop`, `feature/*` branches).
- Document this in your `README.md` or a new `CONTRIBUTING.md` file.

## 5. Create Issue Templates and Project Board

- Go to **Issues > New Issue > Get started with templates** to add bug/feature templates.
- Go to **Projects** and create a new board (Kanban or similar) for task tracking.

## 6. Set Up GitHub Actions (CI/CD)

- Go to **Actions** tab in your repo.
- Set up workflows for linting, testing, or deployment (choose from templates or create your own).

## 7. Write a CONTRIBUTING.md File

- Add guidelines for:
  - Pull request process
  - Code review expectations
  - Commit message style
  - Branch naming conventions
- Place this file in the root of your repository.

## 8. Schedule a Kickoff Meeting

- Align on workflow, roles, and communication channels (e.g., Slack, Discord).
- Review the setup and address any questions.

---

## Example: Branching Strategy

```
main        # Production-ready code
 develop     # Integration branch for features
 feature/*   # Individual feature branches
```

## Example: Pull Request Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Push changes and open a Pull Request (PR) to `develop` or `main`.
3. Request review from at least one teammate.
4. Merge after approval and passing checks.

---

## Additional Tips

- Use **GitHub Discussions** or **Wiki** for team communication and documentation.
- Enable **branch auto-deletion** after merge for cleanliness.
- Regularly review and update your project board and issues.

---

For more details, see the [GitHub Docs](https://docs.github.com/en) or ask your instructor for help.
