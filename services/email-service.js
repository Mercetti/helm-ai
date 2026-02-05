const { google } = require('googleapis');
const nodemailer = require('nodemailer');
require('dotenv').config();

class EmailService {
  constructor() {
    this.oauth2Client = new google.auth.OAuth2(
      process.env.GOOGLE_CLIENT_ID,
      process.env.GOOGLE_CLIENT_SECRET,
      'https://localhost:3001/auth/google/callback'
    );
    
    // Set up tokens if they exist (for now, we'll need to get them first)
    this.tokens = null;
  }

  getAuthUrl() {
    return this.oauth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: ['https://www.googleapis.com/auth/gmail.send'],
      prompt: 'consent'
    });
  }

  async getTokens(code) {
    try {
      const { tokens } = await this.oauth2Client.getToken(code);
      this.oauth2Client.setCredentials(tokens);
      this.tokens = tokens;
      
      // Store tokens for future use
      console.log('Tokens received successfully');
      return tokens;
    } catch (error) {
      console.error('Error getting tokens:', error);
      throw error;
    }
  }

  async sendEmail(to, subject, html, attachments = []) {
    try {
      if (!this.tokens) {
        throw new Error('No authentication tokens. Please authenticate first.');
      }

      // Refresh access token if needed
      const { credentials } = await this.oauth2Client.refreshAccessToken();
      
      const transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: {
          type: 'OAuth2',
          user: process.env.GMAIL_EMAIL,
          clientId: process.env.GOOGLE_CLIENT_ID,
          clientSecret: process.env.GOOGLE_CLIENT_SECRET,
          refreshToken: this.tokens.refresh_token,
          accessToken: credentials.access_token
        }
      });

      const mailOptions = {
        from: process.env.GMAIL_EMAIL,
        to: to,
        subject: subject,
        html: html,
        attachments: attachments
      };

      const result = await transporter.sendMail(mailOptions);
      console.log('Email sent successfully:', result.messageId);
      return result;
    } catch (error) {
      console.error('Email send error:', error);
      throw error;
    }
  }

  // AI Assistant specific email templates
  async sendInvestorUpdate(investorEmail, updateType, content) {
    const subject = `Stellar Logic AI - ${updateType} Update`;
    const html = `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb;">Stellar Logic AI Investor Update</h2>
        <p>Dear Investor,</p>
        <p>${content}</p>
        <div style="background-color: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 5px;">
          <h3 style="color: #1f2937;">Key Highlights:</h3>
          <ul style="color: #4b5563;">
            <li>Market Opportunity: $458B+ TAM</li>
            <li>Current Round: $1.5M seed at $6M valuation</li>
            <li>Products: 7 industry-specific plugins</li>
            <li>Founder Control: 75% retained</li>
          </ul>
        </div>
        <p>Best regards,<br>
        <strong>Stellar Logic AI Team</strong></p>
        <hr style="border: 1px solid #e5e7eb; margin: 30px 0;">
        <p style="font-size: 12px; color: #6b7280;">
          This email was sent by Stellar Logic AI's automated system.<br>
          If you no longer wish to receive these updates, please reply with "UNSUBSCRIBE".
        </p>
      </div>
    `;

    return await this.sendEmail(investorEmail, subject, html);
  }

  async sendCustomerFollowUp(customerEmail, followUpType, content) {
    const subject = `Stellar Logic AI - ${followUpType}`;
    const html = `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb;">Stellar Logic AI Follow Up</h2>
        <p>Dear ${customerEmail.split('@')[0]},</p>
        <p>${content}</p>
        <div style="background-color: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 5px;">
          <h3 style="color: #1f2937;">Our Solutions:</h3>
          <ul style="color: #4b5563;">
            <li>Sub-millisecond threat detection</li>
            <li>99.9% accuracy rate</li>
            <li>Zero performance impact</li>
            <li>Enterprise-grade security</li>
          </ul>
        </div>
        <p>Would you like to schedule a demo to see our platform in action?</p>
        <p>Best regards,<br>
        <strong>Stellar Logic AI Team</strong></p>
        <hr style="border: 1px solid #e5e7eb; margin: 30px 0;">
        <p style="font-size: 12px; color: #6b7280;">
          This email was sent by Stellar Logic AI's automated system.<br>
          If you no longer wish to receive these updates, please reply with "UNSUBSCRIBE".
        </p>
      </div>
    `;

    return await this.sendEmail(customerEmail, subject, html);
  }

  async sendDocumentShare(email, documentType, documentPath) {
    const subject = `Stellar Logic AI - ${documentType} Document`;
    const html = `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb;">Stellar Logic AI Document Share</h2>
        <p>Dear ${email.split('@')[0]},</p>
        <p>Please find attached the ${documentType} document you requested.</p>
        <div style="background-color: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 5px;">
          <h3 style="color: #1f2937;">Document Details:</h3>
          <ul style="color: #4b5563;">
            <li>Type: ${documentType}</li>
            <li>Format: Markdown</li>
            <li>Content: Industry-specific overview</li>
            <li>Purpose: Investor/Customer information</li>
          </ul>
        </div>
        <p>This document provides comprehensive information about our ${documentType.toLowerCase()} capabilities.</p>
        <p>Best regards,<br>
        <strong>Stellar Logic AI Team</strong></p>
        <hr style="border: 1px solid #e5e7eb; margin: 30px 0;">
        <p style="font-size: 12px; color: #6b7280;">
          This email was sent by Stellar Logic AI's automated system.<br>
          If you no longer wish to receive these updates, please reply with "UNSUBSCRIBE".
        </p>
      </div>
    `;

    const attachments = [{
      filename: `${documentType.replace(/\s+/g, '_')}.md`,
      path: documentPath
    }];

    return await this.sendEmail(email, subject, html, attachments);
  }
}

module.exports = EmailService;
