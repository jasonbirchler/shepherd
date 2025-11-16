# Branch Protection Setup

To require tests to pass before PR approval, configure these settings in GitHub:

## Repository Settings → Branches → Add Rule

**Branch name pattern:** `main` (or `master`)

### Protection Rules:
- [x] **Require a pull request before merging**
  - [x] Require approvals: 1
  - [x] Dismiss stale PR approvals when new commits are pushed
  
- [x] **Require status checks to pass before merging**
  - [x] Require branches to be up to date before merging
  - **Required status checks:**
    - `test` (from backend-tests.yml workflow)

- [x] **Require conversation resolution before merging**

- [x] **Include administrators** (optional but recommended)

## Result
- PRs cannot be merged until backend tests pass
- Tests run automatically on every PR
- Failed tests block merge until fixed