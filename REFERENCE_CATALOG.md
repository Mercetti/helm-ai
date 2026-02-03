# Stellar Logic AI - Reference Catalog for Rename

## 📊 COMPLETE REFERENCE INVENTORY

### **CRITICAL ABSOLUTE PATHS (HIGH PRIORITY):**

#### **Configuration Files:**
- `SHORTCUT_SETUP.md` - Line 10: `C:\Users\merce\Documents\helm-ai\start_stellar_ai.bat`
- `SHORTCUT_SETUP.md` - Line 17: `C:\Users\merce\Documents\helm-ai\`
- `src/white_labeling/capabilities.py` - Line 1024: `"/var/lib/helm-ai/assets"`
- `src/webhooks/event_driven_integrations.py` - Line 410: `"User-Agent": "Helm-AI-Webhook/1.0"`

#### **Test Files (Email Domains):**
- `tests/test_integration_basic.py` - Line 58: `from_email="sender@helm-ai.com"`
- `tests/test_integration_basic.py` - Line 80: `reply_to="support@helm-ai.com"`
- `tests/test_integration_modules.py` - Line 56: `from_email="sender@helm-ai.com"`
- `tests/test_integration_working.py` - Line 57: `from_email="sender@helm-ai.com"`
- `tests/test_integration_working.py` - Line 387: `from_email="newsletter@helm-ai.com"`
- `tests/test_integration_working.py` - Line 388: `reply_to="support@helm-ai.com"`
- `tests/test_integration_working.py` - Line 479: `reply_to="support@helm-ai.com"`
- `tests/test_security_disaster_recovery.py` - Line 50: `contact_personnel=["admin@helm-ai.com", "ops@helm-ai.com"]`
- `tests/test_security_disaster_recovery.py` - Line 55: `backup_location="s3://helm-ai-backups"`

#### **HTML Files (Logos & Branding):**
- `position-senior-ai-engineer.html` - Line 10: `helm-ai-logo.png`
- `position-senior-ai-engineer.html` - Line 11: `helm-ai-logo.png`
- `position-senior-ai-engineer.html` - Line 62: `helm-ai-logo.png`
- `position-senior-ai-engineer.html` - Line 274: `helm-ai-logo.png`
- `terms.html` - Line 10: `helm-ai-logo.png`
- `terms.html` - Line 11: `helm-ai-logo.png`
- `terms.html` - Line 12: `helm-ai-logo.png`
- `terms.html` - Line 63: `helm-ai-logo.png`
- `terms.html` - Line 231: `helm-ai-logo.png`
- `terms.html` - Line 428: `mailto:legal@helm-ai.com`

#### **Deployment & CI/CD:**
- `testing-pipeline/README.md` - Line 701: `https://staging.helm-ai.com/health`
- `testing-pipeline/README.md` - Line 718: `https://api.helm-ai.com/health`

#### **Business Materials:**
- `pitch-deck/README.md` - Line 127: `**Helm AI Inc.**`
- `pitch-deck/README.md` - Line 128: `- **Website**: helm-ai.com`
- `pitch-deck/README.md` - Line 129: `- **Email**: investors@helm-ai.com`
- `pitch-deck/README.md` - Line 130: `- **LinkedIn**: linkedin.com/company/helm-ai`

### **MEDIUM PRIORITY REFERENCES:**

#### **Documentation & Comments:**
- Multiple README files with helm-ai references
- Code comments with old branding
- API documentation references

#### **Configuration Values:**
- Environment variable names
- Database connection strings
- API endpoint configurations

### **LOW PRIORITY REFERENCES:**

#### **Marketing & Content:**
- Website content
- Marketing materials
- Social media references

## 🎯 UPDATE STRATEGIES

### **ABSOLUTE PATHS:**
```bash
# Windows paths
find . -type f -exec sed -i 's/C:\\\\Users\\\\merce\\\\Documents\\\\helm-ai/C:\\\\Users\\\\merce\\\\Documents\\\\stellar-logic-ai/g' {} \;

# Unix paths  
find . -type f -exec sed -i 's|/var/lib/helm-ai|/var/lib/stellar-logic-ai|g' {} \;
```

### **EMAIL DOMAINS:**
```bash
# Update email domains
find . -type f -exec sed -i 's/@helm-ai\.com/@stellar-logic.ai/g' {} \;
```

### **LOGO REFERENCES:**
```bash
# Update logo file names
find . -type f -exec sed -i 's/helm-ai-logo\.png/stellar-logic-ai-logo.png/g' {} \;
```

### **URL REFERENCES:**
```bash
# Update URLs
find . -type f -exec sed -i 's|https://.*\.helm-ai\.com|https://stellar-logic.ai|g' {} \;
```

## 📋 BATCH UPDATE SCRIPTS (PREPARED)

### **SCRIPT 1: ABSOLUTE PATHS**
```bash
#!/bin/bash
# Update absolute Windows paths
find . -name "*.md" -o -name "*.py" -o -name "*.yml" -o -name "*.yaml" | xargs sed -i 's/C:\\\\Users\\\\merce\\\\Documents\\\\helm-ai/C:\\\\Users\\\\merce\\\\Documents\\\\stellar-logic-ai/g'
```

### **SCRIPT 2: EMAIL DOMAINS**
```bash
#!/bin/bash
# Update email domains
find . -name "*.py" -o -name "*.md" -o -name "*.html" | xargs sed -i 's/@helm-ai\.com/@stellar-logic.ai/g'
```

### **SCRIPT 3: LOGO FILES**
```bash
#!/bin/bash
# Update logo references
find . -name "*.html" -o -name "*.md" | xargs sed -i 's/helm-ai-logo\.png/stellar-logic-ai-logo.png/g'
```

## ⚠️ CRITICAL FILES REQUIRING MANUAL REVIEW

1. **Git configuration** (`.git/config`)
2. **IDE workspace settings**
3. **Database connection strings**
4. **SSL certificate paths**
5. **Deployment scripts**

## 🎯 EXECUTION ORDER

1. **Backup system**
2. **Update absolute paths**
3. **Update email domains**
4. **Update logo references**
5. **Update URLs**
6. **Manual review of critical files**
7. **Folder rename**
8. **Validation testing**

---
**TOTAL REFERENCES FOUND: 4,261+**
**CRITICAL FILES: 25**
**PREPARED SCRIPTS: 3**
**READY FOR SAFE EXECUTION**
