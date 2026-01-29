# GitHub Pages Deployment Guide

## 🚀 Deploy Helm AI Demo Website to GitHub Pages

### Prerequisites
- GitHub account
- Git installed locally
- Helm AI demo website files

### Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click "New repository"
3. Repository name: `helm-ai-demo`
4. Description: "Helm AI Anti-Cheat Detection Demo"
5. Make it **Public** (required for GitHub Pages)
6. Don't initialize with README (we have our files)
7. Click "Create repository"

### Step 2: Initialize Git Repository

```bash
# Navigate to demo website directory
cd C:\Users\merce\Documents\helm-ai\demo-website

# Initialize Git repository
git init

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Helm AI demo website"
```

### Step 3: Connect to GitHub Repository

```bash
# Add remote origin (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/helm-ai-demo.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 4: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click "Settings" tab
3. Scroll down to "Pages" section
4. Source: Deploy from a branch
5. Branch: `main`
6. Folder: `/ (root)`
7. Click "Save"

### Step 5: Access Your Website

Your website will be available at:
```
https://YOUR_USERNAME.github.io/helm-ai-demo
```

### Step 6: Custom Domain (Optional)

#### Add CNAME File
Create `CNAME` file in demo-website directory:
```
helm-ai.com
```

#### Configure DNS
1. Go to your domain registrar
2. Add DNS records:
   - Type: CNAME
   - Name: @ (or your domain)
   - Value: YOUR_USERNAME.github.io
   - TTL: 3600

#### Update GitHub Pages Settings
1. In repository Settings > Pages
2. Enable "Enforce HTTPS"
3. Add custom domain: `helm-ai.com`

## 🔄 Automatic Deployment

### Update Workflow
```bash
# Make changes to files
# Edit index.html or other files

# Stage and commit changes
git add .
git commit -m "Update hero section with new messaging"
git push origin main
```

GitHub Pages will automatically rebuild and deploy your changes.

## 📊 Analytics Integration

### Google Analytics
1. Go to [Google Analytics](https://analytics.google.com)
2. Create new property for your website
3. Get tracking ID (GA_MEASUREMENT_ID)
4. Add to `index.html` in `<head>` section:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🔧 Troubleshooting

### Common Issues

#### 404 Error
- Check that repository is public
- Verify GitHub Pages is enabled in settings
- Ensure files are in root directory

#### Styles Not Loading
- Check file paths in HTML
- Verify CSS is embedded in HTML (no external files)
- Check for syntax errors in CSS

#### Form Not Working
- GitHub Pages is static (no backend)
- Form submission shows alert only
- For real functionality, need backend service

### Local Testing
```bash
# Serve files locally for testing
python -m http.server 8000

# Or use Node.js
npx serve .

# Access at http://localhost:8000
```

## 📱 Mobile Testing

### Test on Different Devices
1. Open website on mobile phone
2. Use Chrome DevTools device emulation
3. Test responsive design
4. Check touch interactions

### Performance Testing
1. Use [Google PageSpeed Insights](https://pagespeed.web.dev)
2. Test with [GTmetrix](https://gtmetrix.com)
3. Check Lighthouse scores in Chrome DevTools

## 🚀 Advanced Features

### Custom 404 Page
Create `404.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Page Not Found - Helm AI</title>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Inter:wght@400;600;800&display=swap">
    <style>
        body { font-family: 'Inter', sans-serif; text-align: center; padding: 50px; }
        h1 { color: #1e3a8a; font-size: 2rem; margin-bottom: 1rem; }
        a { color: #3b82f6; text-decoration: none; font-weight: 600; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>404 - Page Not Found</h1>
    <p>The page you're looking for doesn't exist.</p>
    <a href="/">Return to Helm AI Home</a>
</body>
</html>
```

### Security Headers
Create `_config.yml`:
```yaml
plugins:
  - jekyll-sitemap
  - jekyll-feed

# GitHub Pages settings
markdown: kramdown
highlighter: rouge
theme: minima

# Security headers (if using custom domain)
webrick:
  headers:
    X-Frame-Options: DENY
    X-Content-Type-Options: nosniff
    X-XSS-Protection: "1; mode=block"
    Strict-Transport-Security: "max-age=31536000; includeSubDomains"
```

## 📈 SEO Optimization

### Meta Tags Already Included
- Title tags
- Meta descriptions
- Open Graph tags
- Twitter Card tags
- Canonical URLs

### Sitemap
GitHub Pages automatically generates sitemap at:
```
https://YOUR_USERNAME.github.io/helm-ai-demo/sitemap.xml
```

### Robots.txt
Create `robots.txt`:
```txt
User-agent: *
Allow: /
Sitemap: https://YOUR_USERNAME.github.io/helm-ai-demo/sitemap.xml
```

## 🎯 Next Steps

1. **Deploy**: Follow steps above to deploy
2. **Test**: Verify all functionality works
3. **Customize**: Update with your branding
4. **Promote**: Share website with investors/customers
5. **Monitor**: Set up analytics and track performance

---

**🛡️ Your Helm AI demo website is now ready for global deployment!**
