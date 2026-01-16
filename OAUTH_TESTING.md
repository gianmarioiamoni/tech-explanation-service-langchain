# 🧪 OAuth Testing Checklist

This document provides a step-by-step testing guide for the OAuth implementation.

---

## ✅ **Phase 1: Basic Auth Fallback (Already Tested)**

- [x] **No OAuth configured**: App starts in Basic Auth mode
- [x] **Fallback message displayed**: Console shows "⚠️ Basic Auth Mode"
- [x] **App runs successfully**: Gradio interface accessible
- [x] **Login with demo/portfolio2026**: Works as expected

**Status**: ✅ **PASSED**

---

## 🔵 **Phase 2: Google OAuth (To Test)**

### **Setup:**
1. Configure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`
2. Add redirect URI in Google Cloud Console:
   ```
   http://localhost:7860/auth/google
   ```

### **Tests:**
- [ ] **OAuth configured message**: Console shows "✅ Google OAuth configured"
- [ ] **App starts in OAuth mode**: Console shows "🔐 OAuth Mode"
- [ ] **Login page displays**: Visit http://localhost:7860/ → shows login page
- [ ] **Google button visible**: "🔵 Login with Google" button present
- [ ] **Click Google button**: Redirects to Google login
- [ ] **Authorize app**: Grant permissions
- [ ] **Redirect back**: Returns to http://localhost:7860/gradio
- [ ] **Session created**: Console logs "User logged in via google: your-email@gmail.com"
- [ ] **Gradio app accessible**: Can use the app after login
- [ ] **Quota tracking**: User-specific quota visible
- [ ] **Logout works**: Click logout → returns to login page
- [ ] **Session cleared**: Console logs "User logged out"

### **Expected Behavior:**
- Seamless Google OAuth flow
- User email extracted and displayed
- Per-user quota tracking active

---

## ⚫ **Phase 3: GitHub OAuth (To Test)**

### **Setup:**
1. Configure `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` in `.env`
2. Add redirect URI in GitHub Developer Settings:
   ```
   http://localhost:7860/auth/github
   ```

### **Tests:**
- [ ] **OAuth configured message**: Console shows "✅ GitHub OAuth configured"
- [ ] **Login page displays**: Visit http://localhost:7860/ → shows login page
- [ ] **GitHub button visible**: "⚫ Login with GitHub" button present
- [ ] **Click GitHub button**: Redirects to GitHub login
- [ ] **Authorize app**: Grant permissions
- [ ] **Redirect back**: Returns to http://localhost:7860/gradio
- [ ] **Session created**: Console logs "User logged in via github: your-username"
- [ ] **Username extracted**: GitHub login name used for quota
- [ ] **Gradio app accessible**: Can use the app after login

### **Expected Behavior:**
- Seamless GitHub OAuth flow
- Username extracted from GitHub profile
- Works independently if Google is not configured

---

## 🤗 **Phase 4: Hugging Face OAuth (To Test)**

**Note:** HF OAuth has known limitations on Spaces. Test locally first.

### **Setup:**
1. Configure `HF_CLIENT_ID` and `HF_CLIENT_SECRET` in `.env`
2. Add redirect URI in HF Settings:
   ```
   http://localhost:7860/auth/huggingface
   ```

### **Tests:**
- [ ] **OAuth configured message**: Console shows "✅ Hugging Face OAuth configured"
- [ ] **Login page displays**: Visit http://localhost:7860/ → shows login page
- [ ] **HF button visible**: "🤗 Login with Hugging Face" button present
- [ ] **Click HF button**: Redirects to HF OAuth
- [ ] **Authorize app**: Grant permissions
- [ ] **Redirect back**: Returns to http://localhost:7860/gradio
- [ ] **Session created**: Console logs "User logged in via huggingface: username"

### **Expected Behavior:**
- HF OAuth flow works locally
- May have issues on Spaces (documented limitation)

---

## 🔀 **Phase 5: Multiple Providers (To Test)**

### **Setup:**
Configure all three providers (Google, GitHub, HF) simultaneously.

### **Tests:**
- [ ] **All configured**: Console shows ✅ for each provider
- [ ] **Login page shows all buttons**: All three login options visible
- [ ] **Can login with Google**: Works independently
- [ ] **Can login with GitHub**: Works independently
- [ ] **Can login with HF**: Works independently
- [ ] **Different users get different quotas**: Switching providers creates separate user sessions

### **Expected Behavior:**
- All three providers coexist without conflicts
- User can choose their preferred login method
- Each provider's users tracked separately

---

## 🚀 **Phase 6: HF Spaces Deployment (To Test)**

### **Setup:**
1. Add secrets to HF Space settings:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GITHUB_CLIENT_ID`
   - `GITHUB_CLIENT_SECRET`
   - `SESSION_SECRET`
2. Update OAuth redirect URIs:
   ```
   https://your-username-tech-explanation-service.hf.space/auth/google
   https://your-username-tech-explanation-service.hf.space/auth/github
   ```

### **Tests:**
- [ ] **Space builds successfully**: No errors in logs
- [ ] **OAuth mode activated**: Logs show "🔐 OAuth Mode"
- [ ] **Login page accessible**: Visit Space URL → shows login
- [ ] **HTTPS redirect URIs work**: OAuth callback succeeds
- [ ] **Google OAuth works on Space**: Full login flow
- [ ] **GitHub OAuth works on Space**: Full login flow
- [ ] **Sessions persist**: User stays logged in across requests
- [ ] **Quota tracking works**: Per-user limits enforced
- [ ] **Multiple users simultaneously**: Different users get separate quotas

### **Expected Behavior:**
- Production OAuth works seamlessly on HF Spaces
- No CORS or redirect URI issues
- Secure session management with HTTPS

---

## 🐛 **Known Issues & Workarounds**

### **Issue 1: Redirect URI Mismatch**
**Symptom:** OAuth error "redirect_uri_mismatch"  
**Solution:** Ensure exact match between configured URI and OAuth app settings (including http/https)

### **Issue 2: Session Not Persisting**
**Symptom:** User logged out after each request  
**Solution:** Verify `SESSION_SECRET` is set and consistent

### **Issue 3: HF OAuth on Spaces**
**Symptom:** HF OAuth fails on HF Spaces  
**Solution:** Known limitation, use Google/GitHub instead

### **Issue 4: CORS Errors**
**Symptom:** Browser blocks OAuth callback  
**Solution:** Ensure proper CORS headers in FastAPI (already configured)

---

## 📊 **Test Results Summary**

| Phase | Status | Notes |
|-------|--------|-------|
| **Phase 1: Basic Auth Fallback** | ✅ PASSED | Works perfectly |
| **Phase 2: Google OAuth** | ⏳ PENDING | Awaiting OAuth app setup |
| **Phase 3: GitHub OAuth** | ⏳ PENDING | Awaiting OAuth app setup |
| **Phase 4: HF OAuth** | ⏳ PENDING | Optional, may skip |
| **Phase 5: Multiple Providers** | ⏳ PENDING | After individual tests |
| **Phase 6: HF Spaces Deployment** | ⏳ PENDING | Final production test |

---

## 🎯 **Next Steps**

1. **Setup Google OAuth** (Recommended first)
   - Create OAuth credentials in Google Cloud Console
   - Test locally with Phase 2 checklist
   
2. **Setup GitHub OAuth** (Recommended second)
   - Create OAuth app in GitHub Settings
   - Test locally with Phase 3 checklist

3. **Deploy to HF Spaces**
   - Add secrets to Space settings
   - Test production OAuth with Phase 6 checklist

4. **Update Portfolio**
   - Add screenshots of OAuth login page
   - Demonstrate multi-provider support
   - Highlight professional authentication

---

## 📚 **Resources**

- [Google OAuth Setup Guide](OAUTH_SETUP.md#-google-oauth-setup)
- [GitHub OAuth Setup Guide](OAUTH_SETUP.md#-github-oauth-setup)
- [Troubleshooting Guide](OAUTH_SETUP.md#-troubleshooting)

