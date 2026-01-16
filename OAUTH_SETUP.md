# 🔐 OAuth Setup Guide

This guide explains how to configure OAuth providers (Google, GitHub, Hugging Face) for the Tech Explanation Service.

---

## 🎯 **Overview**

The app supports multiple OAuth providers:
- **Google OAuth 2.0** - Most users have a Google account
- **GitHub OAuth** - Popular among developers
- **Hugging Face OAuth** - Native integration with HF platform

You can enable **one, two, or all three** providers. The app will automatically detect which providers are configured and display the appropriate login buttons.

---

## 🔵 **Google OAuth Setup**

### **1. Create Google OAuth Credentials**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Navigate to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth client ID**
5. Configure OAuth consent screen if prompted:
   - User Type: **External**
   - App name: `Tech Explanation Service`
   - User support email: Your email
   - Developer contact: Your email
   - Scopes: `openid`, `email`, `profile`
6. Application type: **Web application**
7. Authorized redirect URIs:
   ```
   http://localhost:7860/auth/google
   https://your-username-tech-explanation-service.hf.space/auth/google
   ```
8. Copy **Client ID** and **Client Secret**

### **2. Set Environment Variables**

**Local (`.env` file):**
```bash
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**HF Spaces (Repository Secrets):**
```
Name: GOOGLE_CLIENT_ID
Value: your-google-client-id.apps.googleusercontent.com

Name: GOOGLE_CLIENT_SECRET
Value: your-google-client-secret
```

---

## ⚫ **GitHub OAuth Setup**

### **1. Create GitHub OAuth App**

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in details:
   - **Application name**: `Tech Explanation Service`
   - **Homepage URL**: `https://your-username-tech-explanation-service.hf.space`
   - **Authorization callback URL**:
     ```
     http://localhost:7860/auth/github
     https://your-username-tech-explanation-service.hf.space/auth/github
     ```
4. Click **Register application**
5. Copy **Client ID**
6. Click **Generate a new client secret** and copy it

### **2. Set Environment Variables**

**Local (`.env` file):**
```bash
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

**HF Spaces (Repository Secrets):**
```
Name: GITHUB_CLIENT_ID
Value: your-github-client-id

Name: GITHUB_CLIENT_SECRET
Value: your-github-client-secret
```

---

## 🤗 **Hugging Face OAuth Setup** (Optional)

**Note:** HF OAuth on Spaces has known limitations. It's recommended to use Google or GitHub instead.

### **1. Create HF OAuth App**

1. Go to [Hugging Face Settings](https://huggingface.co/settings/applications)
2. Click **New application**
3. Fill in details:
   - **Application name**: `Tech Explanation Service`
   - **Homepage URL**: `https://your-username-tech-explanation-service.hf.space`
   - **Redirect URI**:
     ```
     http://localhost:7860/auth/huggingface
     https://your-username-tech-explanation-service.hf.space/auth/huggingface
     ```
4. Click **Create application**
5. Copy **Client ID** and **Client Secret**

### **2. Set Environment Variables**

**Local (`.env` file):**
```bash
HF_CLIENT_ID=your-hf-client-id
HF_CLIENT_SECRET=your-hf-client-secret
```

**HF Spaces (Repository Secrets):**
```
Name: HF_CLIENT_ID
Value: your-hf-client-id

Name: HF_CLIENT_SECRET
Value: your-hf-client-secret
```

---

## 🔒 **Session Secret**

The app uses a session secret for secure cookie signing.

**Local (`.env` file):**
```bash
SESSION_SECRET=your-random-secret-key-change-this-in-production
```

**HF Spaces (Repository Secrets):**
```
Name: SESSION_SECRET
Value: your-random-secret-key-change-this-in-production
```

**Generate a secure random secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🚀 **Deployment**

### **Local Development**

1. Create `.env` file with OAuth credentials
2. Run the app:
   ```bash
   python spaces_app.py
   ```
3. Visit: `http://localhost:7860`
4. You'll see login buttons for configured providers

### **Hugging Face Spaces**

1. Go to your Space settings
2. Add **Repository Secrets** for each provider you want to enable
3. Push your code:
   ```bash
   git push hf main
   ```
4. The Space will auto-deploy with OAuth enabled

---

## 🧪 **Testing**

### **Test OAuth Flow:**

1. Click "Login with Google/GitHub/HF"
2. Authorize the app
3. You should be redirected back and see the Gradio app
4. Check logs for:
   ```
   ✅ Google OAuth configured
   User logged in via google: your-email@gmail.com
   ```

### **Fallback Mode:**

If **no** OAuth providers are configured, the app automatically falls back to Basic Auth:
- Username: `demo`
- Password: `portfolio2026`

---

## ❓ **Troubleshooting**

### **"OAuth Not Configured" message**

- Verify environment variables are set correctly
- Check logs for: `✅ Google OAuth configured` (or GitHub/HF)
- Restart the app after adding credentials

### **"OAuth Error" after login**

- Verify redirect URIs match exactly (including http/https)
- Check client secret is correct
- Ensure OAuth app is enabled (not suspended)

### **"No authenticated user" in logs**

- Check session middleware is working
- Verify `SESSION_SECRET` is set
- Clear browser cookies and try again

---

## 📊 **Comparison: OAuth vs Basic Auth**

| Feature | Basic Auth | OAuth (Google/GitHub) |
|---------|------------|----------------------|
| **Setup Complexity** | ✅ None (works out of box) | ⚠️ Requires OAuth app setup |
| **User Experience** | ⚠️ Shared credentials | ✅ Personal account login |
| **Security** | ⚠️ Public password | ✅ OAuth 2.0 standard |
| **Quota Tracking** | ⚠️ Shared ("demo" user) | ✅ Per-user tracking |
| **Portfolio Demo** | ✅ Perfect for demos | ✅ Professional feature |

---

## 🎯 **Recommended Setup**

**For Portfolio/Demo:**
- Enable **Google** (most universal)
- Enable **GitHub** (appeals to developers)
- Keep **Basic Auth** fallback (for quick testing)

**For Production:**
- Enable **Google** + **GitHub**
- Remove Basic Auth fallback
- Set secure `SESSION_SECRET`

---

## 📚 **Additional Resources**

- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Documentation](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app)
- [Authlib Documentation](https://docs.authlib.org/en/latest/)
- [Gradio mount_gradio_app Docs](https://www.gradio.app/guides/sharing-your-app#oauth-with-external-providers)

