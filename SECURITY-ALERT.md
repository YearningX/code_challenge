# ⚠️ Security Alert - API Key Exposure Handling

## 🚨 Issue Description

Your Qwen API Key `your-api-key-placeholder` was previously exposed in the following files:

- `.env.example` (configuration template file)
- `CONFIGURATION-SETUP.md` (configuration documentation)
- `docs/UBUNTU-DEPLOYMENT-WITH-QWEN.md` (deployment documentation)
- `ENV-CONFIG-GUIDE.md` (environment configuration guide)
- `QWEN-INTEGRATION.md` (integration guide)
- `scripts/check_qwen_models.py` (check script)
- `scripts/test_qwen_api.py` (test script)
- `scripts/test_qwen_simple.py` (simple test script)
- `scripts/test_qwen_deployment.py` (deployment test script)
- `web/config.py` (configuration file)

## ✅ Measures Taken

All real API keys in these files have been replaced with placeholders: `sk-your-qwen-api-key-here`

Verification results:
```bash
$ grep -r "your-api-key-placeholder" --include="*.md" --include="*.py" --include="*.yml"
(no results - all cleaned)
```

## 🔒 Urgent Recommended Actions

### 1. Immediately Revoke the Leaked API Key

**Go to [Alibaba Cloud DashScope Console](https://dashscope.aliyun.com/)**

1. Log in to your Alibaba Cloud account
2. Navigate to DashScope Console
3. Find API Key: `your-api-key-placeholder`
4. **Delete or disable this key**
5. Create a new API Key

### 2. Update Configuration

After generating a new API key:

1. **Update `.env` file** (will not be committed to Git)
   ```bash
   QWEN_API_KEY=your-new-api-key-here
   ```

2. **Do NOT** write it to `.env.example` or any documentation files

3. **Ensure `.env` is in `.gitignore`** (confirmed)

### 3. Check Usage Records

Check in DashScope Console:
- Any abnormal usage records
- Whether API call volume is abnormal
- Whether costs are abnormally high

### 4. Strongly Recommended: Enable API Key Permission Restrictions

In DashScope Console:
- Set IP whitelist (if supported)
- Set daily call limit
- Enable alert notifications

## 📋 Security Checklist

- [x] Clean API keys from all public files
- [ ] **Revoke old API key** (requires your manual action)
- [ ] **Generate new API key** (requires your manual action)
- [ ] Update `.env` file
- [ ] Check API usage logs
- [ ] Set permission restrictions
- [ ] Before committing code to GitHub, check for any sensitive information

## 🛡️ Future Security Best Practices

### ✅ Should Do:

1. **Use environment variables**
   ```bash
   export QWEN_API_KEY=sk-...
   ```

2. **Use `.env` file** (add to `.gitignore`)
   ```bash
   # .env
   QWEN_API_KEY=sk-...
   ```

3. **Use placeholders** (in documentation and examples)
   ```bash
   QWEN_API_KEY=sk-your-api-key-here
   ```

### ❌ Should NOT Do:

1. **Hardcode API key in code**
   ```python
   api_key = "sk-real-key"  # ❌ Dangerous
   ```

2. **Use real API key in documentation**
   ```markdown
   API_KEY=sk-real-key  # ❌ Will be committed to Git
   ```

3. **Commit `.env` file to version control**
   ```bash
   git add .env  # ❌ Dangerous
   ```

## 🔍 Git History Cleanup (Optional)

If code has been pushed to GitHub, recommend cleaning Git history:

```bash
# Use BFG Repo-Cleaner or git filter-branch
# Remove sensitive information from history

# Option 1: Use BFG (recommended)
java -jar bfg.jar --replace-text passwords.txt

# Option 2: Use git filter-branch
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch filename" \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
```

## 📞 Contact Support

If any unauthorized use is found, immediately:
1. Revoke API key
2. Contact Alibaba Cloud technical support
3. Check account security settings

---

**Date:** 2026-04-03
**Status:** ⚠️ Pending - Requires user to revoke old key and generate new key
**Severity:** 🔴 High - API key exposed in multiple files
