# Hugging Face Spaces - Troubleshooting Guide

## Critical Issue: Python Version & Gradio Compatibility

### Problem
HF Spaces was failing with:
```
ImportError: cannot import name 'HfFolder' from 'huggingface_hub'
```

### Root Cause
1. HF Spaces was using **Python 3.10** instead of **3.11**
2. `gradio==6.3.0` requires a newer `huggingface_hub` API that's incompatible with older versions
3. HF Spaces reads configuration from **README.md frontmatter**, not just `.space_config.yml`

### Solution Applied

#### 1. **README.md Frontmatter** (Primary configuration)
HF Spaces reads configuration from the YAML frontmatter in `README.md`:

```yaml
---
title: Tech Explanation Service
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 6.3.0
app_file: spaces_app.py
pinned: false
python_version: 3.11  # ← CRITICAL: Forces Python 3.11
---
```

#### 2. **Exact Version Pins in requirements.txt**
```txt
gradio==6.3.0
huggingface_hub==1.3.1
```

#### 3. **Backup Configuration: .space_config.yml**
```yaml
sdk: gradio
sdk_version: 6.3.0
python_version: 3.11
app_file: spaces_app.py
```

### File Structure for HF Spaces

```
/
├── README.md                 # ← MUST have frontmatter with python_version: 3.11
├── README_LOCAL.md           # Local development documentation
├── .space_config.yml         # Backup config
├── spaces_app.py             # Entrypoint (defined in app_file)
├── requirements.txt          # Exact versions
└── ...
```

### Key Learnings

1. **HF Spaces ignores `.space_config.yml` if README.md has no frontmatter**
2. **Python version in README.md frontmatter is mandatory**
3. **Gradio 6.3.0+ requires huggingface_hub 1.x+**
4. **Always use exact versions (`==`) for critical dependencies in HF Spaces**

### Verification Steps

After pushing to GitHub:
1. HF Spaces auto-rebuilds from GitHub
2. Check build logs for: `Using Python 3.11`
3. Verify packages: `gradio==6.3.0` and `huggingface_hub==1.3.1`
4. If still failing: "Factory reboot" in HF Spaces Settings

### Factory Reboot (Last Resort)

If the error persists after all fixes:
1. Go to HF Spaces → Settings
2. Click "Factory reboot"
3. This clears all caches and forces a complete rebuild

---

## Reference: Version Compatibility Matrix

| Gradio Version | huggingface_hub Version | Python Version | Status |
|---------------|------------------------|----------------|--------|
| 6.3.0         | 1.3.1                  | 3.11           | ✅ Works |
| 6.3.0         | 0.x.x                  | 3.10           | ❌ HfFolder error |
| 5.x.x         | 0.x.x                  | 3.10           | ⚠️ Legacy |

---

**Status**: ✅ Fixed - Pushed to GitHub on 2026-01-11

