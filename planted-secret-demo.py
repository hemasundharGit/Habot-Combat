# =============================================================================
# planted-secret-demo.py
#
# PURPOSE: This file exists ONLY to demonstrate the fail-closed behavior of
# the Poka-Yoke build gate for the HabotConnect hiring project presentation.
#
# It contains a deliberately fake, non-functional API key so that Gitleaks
# (the secret scanner in ci-cd/.github/workflows/build-gate.yml) detects it
# and fails the pipeline. This proves the gate blocks insecure commits before
# they can merge or deploy.
#
# DO NOT leave this file in the main branch after capturing your screenshot —
# push it on a throwaway branch, open a PR, screenshot the failed check, then
# delete the branch. See the "How to trigger this demo" steps at the bottom
# of this file.
# =============================================================================

API_KEY = "sk-fake12345678901234567890abcdef"
DATABASE_PASSWORD = "SuperSecretPassword123!"

# =============================================================================
# How to trigger this demo:
#
# 1. git checkout -b demo/fail-closed-proof
# 2. Add this file to your repo root (or anywhere under version control)
# 3. git add planted-secret-demo.py
# 4. git commit -m "demo: intentionally insecure commit for fail-closed proof"
# 5. git push origin demo/fail-closed-proof
# 6. Open a Pull Request into main on GitHub
# 7. Wait for the "Poka-Yoke Build Gate" checks to run — the "Gate 1 — Secret
#    Scan (Fail-Closed)" job should fail with a red X, and if branch
#    protection is enabled, GitHub will show "Merging is blocked" on the PR
# 8. Screenshot: (a) the red X failed check list, (b) the Gitleaks job log
#    showing the detected secret, (c) the "Merging is blocked" banner
# 9. Close the PR without merging, then delete the demo branch:
#      git push origin --delete demo/fail-closed-proof
# =============================================================================
