# Cursor Command Queue — Exo-Suit v2.1

0. **RAG Load**  
   ```powershell
   python .\rag\retrieve.py --query "<task summary>" --topk 60
   .\ops\context-governor.ps1 -maxTokens 128000
   ```  
   Only use `TRIMMED.json` files.

1. **BLOCK gate**  
   If `PLACEHOLDER_REPORT.json` contains `"Severity": "BLOCK"` → stop and open task `remove-blockers`.

2. **Owner gate**  
   Changed files must match `ownership.json` owner "AI". If not, append diff to `PLAN.md → Owner Pings`.

3. **Plan**  
   Write `PLAN.md` with file targets and tests.

4. **Lint/Test**  
   Run `.\go-big.ps1 -skipTests:$false`.

5. **Feature Branch**  
   `.\ops\patch-forge.ps1 -featureName "feat-<slug>"`

6. **Summarize**  
   Regenerate context pack and `CHANGE_SUMMARY.md`.

**Sandbox (optional but recommended)**
Run `.\ops\worktree-sandbox.ps1`. Open the printed sandbox path in Cursor and do all edits there. When done, finalize using the instructions printed by the script so a single `restore/AI_PATCH.diff` is produced for review.
