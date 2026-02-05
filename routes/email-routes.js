const express = require('express');
const EmailService = require('../services/email-service');
const router = express.Router();

const emailService = new EmailService();

// Get authentication URL
router.get('/auth/url', (req, res) => {
  try {
    const authUrl = emailService.getAuthUrl();
    res.json({ 
      success: true, 
      authUrl,
      message: 'Visit this URL to authorize Gmail access' 
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Handle OAuth callback
router.get('/auth/callback', async (req, res) => {
  try {
    const { code } = req.query;
    
    if (!code) {
      return res.status(400).json({ 
        success: false, 
        error: 'Authorization code not provided' 
      });
    }

    const tokens = await emailService.getTokens(code);
    
    // For browser testing, show success page
    res.send(`
      <html>
        <head><title>Authentication Successful</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
          <h2 style="color: #2563eb;">✅ Gmail Authentication Successful!</h2>
          <p>Your Stellar Logic AI email service is now authenticated.</p>
          <p>You can close this window and return to the terminal.</p>
          <div style="background-color: #f8f9fa; padding: 20px; margin: 20px auto; border-radius: 5px; max-width: 400px;">
            <h3>Next Steps:</h3>
            <ol style="text-align: left; display: inline-block;">
              <li>Run: <code>node test-email-auth.js YOUR_AUTH_CODE</code></li>
              <li>Your AI assistant can now send emails!</li>
            </ol>
          </div>
        </body>
      </html>
    `);
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// Send email endpoint
router.post('/send', async (req, res) => {
  try {
    const { to, subject, html, attachments } = req.body;
    
    if (!to || !subject || !html) {
      return res.status(400).json({ 
        success: false, 
        error: 'Missing required fields: to, subject, html' 
      });
    }

    const result = await emailService.sendEmail(to, subject, html, attachments);
    
    res.json({ 
      success: true, 
      message: 'Email sent successfully',
      messageId: result.messageId 
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// AI Assistant specific endpoints
router.post('/send/investor-update', async (req, res) => {
  try {
    const { investorEmail, updateType, content } = req.body;
    
    if (!investorEmail || !updateType || !content) {
      return res.status(400).json({ 
        success: false, 
        error: 'Missing required fields: investorEmail, updateType, content' 
      });
    }

    const result = await emailService.sendInvestorUpdate(investorEmail, updateType, content);
    
    res.json({ 
      success: true, 
      message: 'Investor update sent successfully',
      messageId: result.messageId 
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

router.post('/send/customer-followup', async (req, res) => {
  try {
    const { customerEmail, followUpType, content } = req.body;
    
    if (!customerEmail || !followUpType || !content) {
      return res.status(400).json({ 
        success: false, 
        error: 'Missing required fields: customerEmail, followUpType, content' 
      });
    }

    const result = await emailService.sendCustomerFollowUp(customerEmail, followUpType, content);
    
    res.json({ 
      success: true, 
      message: 'Customer follow-up sent successfully',
      messageId: result.messageId 
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

router.post('/send/document-share', async (req, res) => {
  try {
    const { email, documentType, documentPath } = req.body;
    
    if (!email || !documentType || !documentPath) {
      return res.status(400).json({ 
        success: false, 
        error: 'Missing required fields: email, documentType, documentPath' 
      });
    }

    const result = await emailService.sendDocumentShare(email, documentType, documentPath);
    
    res.json({ 
      success: true, 
      message: 'Document share sent successfully',
      messageId: result.messageId 
    });
  } catch (error) {
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

module.exports = router;
