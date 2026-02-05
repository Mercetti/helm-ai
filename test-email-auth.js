const EmailService = require('./services/email-service');
require('dotenv').config();

async function testEmailService() {
  console.log('🧪 Testing Stellar Logic AI Email Service...\n');
  
  const emailService = new EmailService();
  
  // Test 1: Get authentication URL
  console.log('1️⃣ Getting authentication URL...');
  const authUrl = emailService.getAuthUrl();
  console.log('✅ Auth URL generated:');
  console.log(authUrl);
  console.log('\n📋 Next steps:');
  console.log('1. Visit the URL above in your browser');
  console.log('2. Authorize the application');
  console.log('3. Copy the authorization code from the callback URL');
  console.log('4. Run: node test-email-auth.js YOUR_AUTH_CODE\n');
  
  // If you have auth code, you can test email sending
  const authCode = process.argv[2];
  
  if (authCode) {
    console.log('2️⃣ Authenticating with code...');
    try {
      const tokens = await emailService.getTokens(authCode);
      console.log('✅ Authentication successful!');
      console.log('📧 Testing email sending...');
      
      // Test sending an email
      const testEmail = process.env.GMAIL_EMAIL; // Send to yourself for testing
      const result = await emailService.sendEmail(
        testEmail,
        'Stellar Logic AI - Email Service Test',
        `
          <h2>🚀 Email Service Test Successful!</h2>
          <p>Your Stellar Logic AI email service is working correctly.</p>
          <div style="background-color: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 5px;">
            <h3>Test Details:</h3>
            <ul>
              <li>✅ Gmail API authentication</li>
              <li>✅ OAuth 2.0 flow</li>
              <li>✅ Email sending capability</li>
              <li>✅ HTML template rendering</li>
            </ul>
          </div>
          <p>Your AI assistant can now send professional emails!</p>
          <p>Best regards,<br>Stellar Logic AI Team</p>
        `
      );
      
      console.log('✅ Email sent successfully!');
      console.log(`📧 Message ID: ${result.messageId}`);
      console.log(`📨 Sent to: ${testEmail}`);
      
      // Test AI Assistant specific functions
      console.log('\n3️⃣ Testing AI Assistant email templates...');
      
      await emailService.sendInvestorUpdate(
        testEmail,
        'Quarterly',
        'Test investor update: Your Stellar Logic AI investment is performing well with market expansion across 7 industries.'
      );
      console.log('✅ Investor update template sent!');
      
      await emailService.sendCustomerFollowUp(
        testEmail,
        'Demo Follow-up',
        'Test customer follow-up: Thank you for your interest in Stellar Logic AI. Here are the next steps for integration.'
      );
      console.log('✅ Customer follow-up template sent!');
      
      await emailService.sendDocumentShare(
        testEmail,
        'Automotive Plugin Overview',
        './products/plugins/automotive/AUTOMOTIVE_PLUGIN_OVERVIEW.md'
      );
      console.log('✅ Document share template sent!');
      
      console.log('\n🎉 All tests passed! Your AI assistant is ready to send emails!');
      
    } catch (error) {
      console.error('❌ Test failed:', error.message);
      console.log('\n🔧 Troubleshooting:');
      console.log('1. Make sure you copied the full authorization code');
      console.log('2. Check that your Gmail credentials are correct');
      console.log('3. Ensure Gmail API is enabled in Google Cloud Console');
      console.log('4. Verify redirect URI matches in Google Cloud Console');
    }
  }
}

// Run the test
testEmailService().catch(console.error);
