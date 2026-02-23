# CI/CD Plan of Action – API-Refresh

Follow this order so you have version control and automation from day one.

---

## 1. Order of operations (recommended)

| Step | Action | Why |
|------|--------|-----|
| **1** | Initialize Git locally | Version control from the first commit |
| **2** | Create repo on GitHub & connect | Single source of truth; enables Actions |
| **3** | Add minimal project + CI workflow | CI runs on every push/PR immediately |
| **4** | Add tests (even one) | CI can run tests; prevents “no tests” drift |
| **5** | Code in a loop | Code → test → commit → push → CI runs |

So: **Git → GitHub → project + CI → tests → then code**. CI is in place before you rely on it.

---

## 2. Step-by-step

### 2.1 Git + GitHub

```bash
git init
git add .
git commit -m "chore: add CI/CD and project scaffold"
```

- Create a **new repository** on GitHub (no README, no .gitignore).
- Add the remote and push:

```bash
git remote add origin https://github.com/YOUR_USERNAME/API-Refresh.git
git branch -M main
git push -u origin main
```

### 2.2 Enable GitHub Actions

- Workflows live in `.github/workflows/`. Push the `ci.yml` file and Actions are enabled.
- Optional: **Branch protection** for `main`: require status checks (e.g. “CI”) before merge.

### 2.3 Add tests early

- Add at least one test (e.g. “health” or “smoke”) so `npm test` / your test command is real.
- Keep the habit: **no merge to main without passing tests**.

### 2.4 Coding loop

- Work on a branch → run tests locally → push → open PR → CI runs → merge when green.

---

## 3. Best practices

- **Run CI on every PR and push to main** – catch breakage before merge.
- **Cache dependencies** – faster runs (this workflow caches npm).
- **Use a single source of truth** – one main branch; short-lived feature branches.
- **Keep workflows simple** – lint + test first; add deploy later when you have an environment.
- **Secrets** – store API keys and credentials in GitHub Secrets, never in the repo.
- **Conventional commits** – optional but helpful (e.g. `feat:`, `fix:`, `chore:`).

---

## 4. Suggested improvements (when you’re ready)

- **Branch protection**: Require “CI” to pass and at least one review before merging to `main`.
- **Deploy job**: Add a `deploy` job (or separate workflow) that runs only on `main` after merge.
- **Linting**: Add a lint step (e.g. ESLint) and run it in CI.
- **Security**: Use `npm audit` / `composer audit` or Dependabot in the repo.
- **Environments**: Use GitHub Environments (e.g. staging, production) for deployment and secrets.

---

## 5. What’s in this repo

- **`.github/workflows/ci.yml`** – Runs on push/PR: install deps, run tests (customize for your stack).
- **`package.json`** – Minimal Node script so CI has a `npm test` that passes until you add real tests (replace with PHP/Composer if you prefer).
- **`.gitignore`** – Ignores `node_modules`, `.env`, and common artifacts.

**Before first push:** Run `npm install` once in the project root to generate `package-lock.json` so `npm ci` in CI works.

If you switch to **PHP/Composer**, we can replace the Node steps in `ci.yml` with `composer install` and `composer test` (or `phpunit`).
