# How to Connect Your Local Project to GitHub (API-Refresh)

This guide connects your local **API-Refresh** folder to your existing GitHub repo:  
**[https://github.com/DJohnsonRoseKillik/API-Refresh](https://github.com/DJohnsonRoseKillik/API-Refresh)**

Your GitHub repo already has a `README.md`. We’ll connect, merge that with your local files, then push everything.

---

## What You’ll Do (Overview)

1. Open a terminal in your project folder.
2. Initialize Git (if needed) and make a first commit with your local files.
3. Add the GitHub repo as the `origin` remote.
4. Pull GitHub’s content (e.g. README) and merge with your local commit.
5. Push your merged branch to GitHub.

---

## Step-by-Step Instructions

### Step 1: Open the terminal in your project folder

- **Windows:** Open PowerShell or Command Prompt, then go to the project:
  ```powershell
  cd c:\Temp\xampp\htdocs\API-Refresh
  ```
- Or in VS Code / Cursor: **Terminal → New Terminal** (it often opens in the workspace folder).

---

### Step 2: Check if Git is installed

```powershell
git --version
```

- You should see something like `git version 2.x.x`. If you get “not recognized,” [install Git for Windows](https://git-scm.com/download/win) and try again.

---

### Step 3: Initialize Git (only if this folder is not a repo yet)

```powershell
git init
```

**What it does:** Creates a hidden `.git` folder so this directory becomes a Git repository. All history and branches live here. Safe to run; if the folder is already a repo, Git will say so.

---

### Step 4: Stage all your files

```powershell
git add .
```

**What it does:** Puts every file in the folder (that isn’t ignored by `.gitignore`) into the “staging area.” Only staged files are included in the next commit. The `.` means “current directory and everything under it.”

---

### Step 5: Create your first local commit

```powershell
git commit -m "chore: add CI/CD, project scaffold, and connect to GitHub"
```

**What it does:** Saves a snapshot of everything you staged. The `-m "..."` is the commit message. This commit exists only on your machine until you push.

---

### Step 6: Add the GitHub repo as the remote

```powershell
git remote add origin https://github.com/DJohnsonRoseKillik/API-Refresh.git
```

**What it does:** Registers the GitHub repo as a remote named `origin`. Later, `git push origin main` and `git pull origin main` will use this URL. You only need to add it once per clone/repo.

- **If you see “remote origin already exists”:** You’ve already added it. To overwrite the URL:
  ```powershell
  git remote set-url origin https://github.com/DJohnsonRoseKillik/API-Refresh.git
  ```

---

### Step 7: Rename your branch to `main` (if it’s something else)

```powershell
git branch -M main
```

**What it does:** Renames your current branch to `main` so it matches GitHub’s default branch. `-M` forces the rename even if `main` already exists locally.

---

### Step 8: Pull GitHub’s content and merge with your commit

Your GitHub repo already has at least one commit (e.g. README). You need to combine that with your local commit:

```powershell
git pull origin main --allow-unrelated-histories
```

**What it does:**  
- Downloads the latest from `origin`’s `main` branch.  
- `--allow-unrelated-histories` lets Git merge two branches that don’t share a common commit (your local history vs. GitHub’s).  
- Git may open an editor for a merge commit message; you can save and close to accept the default.

**If you get a conflict (e.g. in README.md):**

1. Open the conflicted file. You’ll see markers like `<<<<<<<`, `=======`, `>>>>>>>`.
2. Edit the file to keep the text you want (e.g. keep both a short description and your CI/CD notes).
3. Save, then run:
   ```powershell
   git add .
   git commit -m "merge: combine GitHub README with local project"
   ```

---

### Step 9: Push your branch to GitHub

```powershell
git push -u origin main
```

**What it does:**  
- Sends your `main` branch to GitHub (`origin`).  
- `-u origin main` sets “tracking” so later you can just run `git push` and `git pull` without typing the branch name.

You may be asked to sign in (browser or credentials). After this, your local project and [https://github.com/DJohnsonRoseKillik/API-Refresh](https://github.com/DJohnsonRoseKillik/API-Refresh) are connected and in sync.

---

## Quick Reference: All Commands in Order

Run these from `c:\Temp\xampp\htdocs\API-Refresh`:

```powershell
cd c:\Temp\xampp\htdocs\API-Refresh

git init
git add .
git commit -m "chore: add CI/CD, project scaffold, and connect to GitHub"
git remote add origin https://github.com/DJohnsonRoseKillik/API-Refresh.git
git branch -M main
git pull origin main --allow-unrelated-histories
git push -u origin main
```

*(If `origin` already exists, use `git remote set-url origin https://github.com/DJohnsonRoseKillik/API-Refresh.git` instead of `git remote add ...`.)*

---

## After Connecting: Daily Workflow

| Goal              | Command                    |
|-------------------|----------------------------|
| See status        | `git status`               |
| Stage changes     | `git add .` or `git add <file>` |
| Commit            | `git commit -m "your message"` |
| Push to GitHub    | `git push`                 |
| Get latest        | `git pull`                 |
| New feature       | `git checkout -b feature-name` then commit and push, open a Pull Request on GitHub |

---

## Troubleshooting

- **“Permission denied” or “Authentication failed”**  
  Sign in to GitHub (browser or Git Credential Manager). For HTTPS, a personal access token may be required instead of a password.

- **“Updates were rejected”**  
  Someone (or you elsewhere) pushed to `main` first. Run `git pull origin main` and fix any conflicts, then `git push`.

- **“Remote origin already exists”**  
  Run: `git remote set-url origin https://github.com/DJohnsonRoseKillik/API-Refresh.git` then continue from Step 7.

Once you’ve run through Step 9, your local project is connected to [DJohnsonRoseKillik/API-Refresh](https://github.com/DJohnsonRoseKillik/API-Refresh) and you can push and pull as above.
