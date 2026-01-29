# 🚀 HELM AI PDF GENERATION SETUP

## 📋 EASY SETUP INSTRUCTIONS

### **🎯 STEP 1: OPEN THE PDF GENERATOR**
```
📁 Open: pdf-generator.html in your browser
🌐 URL: file:///C:/Users/merce/Documents/helm-ai/pdf-generator.html
```

### **🎮 STEP 2: UPLOAD YOUR BRANDING**
```
📤 Upload helm-ai-logo.png
📤 Upload helm-ai-demo-qr.png
✅ Both files will be integrated into PDFs
```

### **📄 STEP 3: SELECT FILES TO CONVERT**
```
📊 INVESTOR-ONE-PAGER - Executive summary
🎮 PARTNERSHIP-SALES-KIT - Complete sales playbook
🎨 BRANDING-GUIDE - Brand specifications
🔧 ANTI-CHEAT-TECHNICAL-SPECS - Technical details
📧 PARTNERSHIP-EMAIL-TEMPLATES - Email templates
```

### **🎯 STEP 4: GENERATE PDFs**
```
🚀 Click "Generate Selected PDFs"
✅ Professional PDFs with branding
✅ Logo integration (top-right)
✅ QR code integration (bottom-right)
✅ Demo URL: https://symphonious-taiyaki-6b6494.netlify.app/
```

---

## 📱 ALTERNATIVE: NODE.JS SETUP

### **🔧 INSTALL DEPENDENCIES**
```bash
npm install puppeteer markdown-it sharp
```

### **📄 CREATE GENERATOR SCRIPT**
```javascript
// pdf-generator.js
const puppeteer = require('puppeteer');
const markdownIt = require('markdown-it');
const fs = require('fs');

async function generatePDF(markdownFile, outputFile) {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    
    // Read markdown content
    const markdownContent = fs.readFileSync(markdownFile, 'utf8');
    const md = new markdownIt();
    const html = md.render(markdownContent);
    
    // Create HTML with branding
    const brandedHTML = `
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px;
                color: #1a1a1a;
                line-height: 1.6;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
            }
            .logo {
                width: 200px;
                height: auto;
            }
            .content {
                max-width: 800px;
                margin: 0 auto;
            }
            .footer {
                position: fixed;
                bottom: 20px;
                right: 20px;
                text-align: center;
            }
            .qr-code {
                width: 150px;
                height: auto;
            }
            h1 { color: #2563EB; border-bottom: 3px solid #2563EB; }
            h2 { color: #1E40AF; }
            h3 { color: #2563EB; }
            .highlight { background: linear-gradient(135deg, #2563EB, #1E40AF); color: white; padding: 20px; border-radius: 10px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Helm AI</h1>
            <img src="helm-ai-logo.png" class="logo" alt="Helm AI Logo">
        </div>
        <div class="content">
            ${html}
        </div>
        <div class="footer">
            <img src="helm-ai-demo-qr.png" class="qr-code" alt="Demo QR Code">
            <p>Scan to try live demo:<br>https://symphonious-taiyaki-6b6494.netlify.app/</p>
        </div>
    </body>
    </html>`;
    
    await page.setContent(brandedHTML);
    await page.pdf({
        path: outputFile,
        format: 'A4',
        printBackground: true,
        margin: {
            top: '20mm',
            right: '20mm',
            bottom: '20mm',
            left: '20mm'
        }
    });
    
    await browser.close();
    console.log(`Generated: ${outputFile}`);
}

// Generate all PDFs
const files = [
    { input: 'INVESTOR-ONE-PAGER.md', output: 'INVESTOR-ONE-PAGER.pdf' },
    { input: 'PARTNERSHIP-SALES-KIT.md', output: 'PARTNERSHIP-SALES-KIT.pdf' },
    { input: 'BRANDING-GUIDE.md', output: 'BRANDING-GUIDE.pdf' },
    { input: 'ANTI-CHEAT-TECHNICAL-SPECS.md', output: 'ANTI-CHEAT-TECHNICAL-SPECS.pdf' },
    { input: 'PARTNERSHIP-EMAIL-TEMPLATES.md', output: 'PARTNERSHIP-EMAIL-TEMPLATES.pdf' }
];

async function generateAll() {
    for (const file of files) {
        await generatePDF(file.input, file.output);
    }
}

generateAll().catch(console.error);
```

### **🚀 RUN THE GENERATOR**
```bash
node pdf-generator.js
```

---

## 🎯 PYTHON SETUP (ALTERNATIVE)

### **🔧 INSTALL DEPENDENCIES**
```bash
pip install weasyprint markdown pillow
```

### **📄 CREATE GENERATOR SCRIPT**
```python
# pdf-generator.py
import markdown
from weasyprint import HTML, CSS
import os

def generate_pdf(markdown_file, output_file):
    # Read markdown content
    with open(markdown_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert to HTML
    html = markdown.markdown(markdown_content)
    
    # Create branded HTML
    branded_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 40px;
                color: #1a1a1a;
                line-height: 1.6;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
            }}
            .logo {{
                width: 200px;
                height: auto;
            }}
            .content {{
                max-width: 800px;
                margin: 0 auto;
            }}
            .footer {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                text-align: center;
            }}
            .qr-code {{
                width: 150px;
                height: auto;
            }}
            h1 {{ color: #2563EB; border-bottom: 3px solid #2563EB; }}
            h2 {{ color: #1E40AF; }}
            h3 {{ color: #2563EB; }}
            .highlight {{ 
                background: linear-gradient(135deg, #2563EB, #1E40AF); 
                color: white; 
                padding: 20px; 
                border-radius: 10px; 
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Helm AI</h1>
            <img src="helm-ai-logo.png" class="logo" alt="Helm AI Logo">
        </div>
        <div class="content">
            {html}
        </div>
        <div class="footer">
            <img src="helm-ai-demo-qr.png" class="qr-code" alt="Demo QR Code">
            <p>Scan to try live demo:<br>https://symphonious-taiyaki-6b6494.netlify.app/</p>
        </div>
    </body>
    </html>"""
    
    # Generate PDF
    HTML(string=branded_html).write_pdf(output_file)
    print(f"Generated: {output_file}")

# Generate all PDFs
files = [
    ('INVESTOR-ONE-PAGER.md', 'INVESTOR-ONE-PAGER.pdf'),
    ('PARTNERSHIP-SALES-KIT.md', 'PARTNERSHIP-SALES-KIT.pdf'),
    ('BRANDING-GUIDE.md', 'BRANDING-GUIDE.pdf'),
    ('ANTI-CHEAT-TECHNICAL-SPECS.md', 'ANTI-CHEAT-TECHNICAL-SPECS.pdf'),
    ('PARTNERSHIP-EMAIL-TEMPLATES.md', 'PARTNERSHIP-EMAIL-TEMPLATES.pdf')
]

for input_file, output_file in files:
    generate_pdf(input_file, output_file)
```

### **🚀 RUN THE GENERATOR**
```bash
python pdf-generator.py
```

---

## 🎯 RECOMMENDED: BROWSER METHOD

### **📱 EASIEST OPTION**
```
✅ No installation required
✅ Visual interface
✅ File upload support
✅ Real-time preview
✅ Instant download
```

### **🎮 STEPS**
```
1. Open pdf-generator.html in browser
2. Upload your logo and QR code
3. Select files to convert
4. Click generate
5. Download professional PDFs
```

---

## 📊 WHAT YOU GET

### **📄 PROFESSIONAL PDFs WITH:**
```
✅ Helm AI branding
✅ Logo integration (top-right)
✅ QR code integration (bottom-right)
✅ Demo URL: https://symphonious-taiyaki-6b6494.netlify.app/
✅ Blue gradient theme
✅ Professional typography
✅ Print-ready quality
✅ Mobile-friendly layout
```

### **🎯 FILES GENERATED:**
```
📊 INVESTOR-ONE-PAGER.pdf
🎮 PARTNERSHIP-SALES-KIT.pdf
🎨 BRANDING-GUIDE.pdf
🔧 ANTI-CHEAT-TECHNICAL-SPECS.pdf
📧 PARTNERSHIP-EMAIL-TEMPLATES.pdf
```

---

## 🚀 TEAM READY

### **💼 IMMEDIATE USE:**
```
📧 Email to sales team
📱 Share via cloud storage
🖨️ Print for meetings
🎯 Use for investor pitches
💰 Ready for partnerships
```

### **🎮 DEMO INTEGRATION:**
```
📱 QR codes link to live demo
🔗 Working demo URL
🎯 Investors can try immediately
💼 Partners can test live
🚀 No setup required
```

---

**Choose the browser method for easiest setup, or Node.js/Python for automated generation!** 🚀💎✨
