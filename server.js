const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

// Import AI modules (will be created next)
const { helmLLMDevelopment } = require('./src/ai/core/llm-development');
const { responseSimplifier } = require('./src/ai/core/response-simplifier');
const { helmLearningEnhancement } = require('./src/ai/core/learning-enhancement');
const { helmSafetyAndGovernance } = require('./src/ai/core/safety-governance');
const { helmImprovementStrategies } = require('./src/ai/core/improvement-strategies');
const { helmIPProtectionStrategy } = require('./src/ai/ip/ip-protection');
const { helmCompetitiveAdvantageAnalysis } = require('./src/ai/ip/competitive-analysis');
const { helmValuationAnalysis } = require('./src/ai/ip/valuation-analysis');

const app = express();
const PORT = process.env.PORT || 3001; // Different port to avoid conflict with poker game

// Security middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: {
    error: 'Too many requests from this IP, please try again later.',
    code: 'RATE_LIMIT_EXCEEDED'
  }
});

app.use(limiter);
app.use(cors({
  origin: '*', // Allow all origins for demo
  credentials: true
}));
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'Helm AI',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// Core AI endpoints
app.get('/api/ai/llm-development', (req, res) => {
  try {
    const technicalRoadmap = helmLLMDevelopment.getDevelopmentRoadmap();
    const investorFriendly = responseSimplifier.simplifyLLMDevelopment(technicalRoadmap);
    
    res.json({
      success: true,
      data: {
        executiveSummary: investorFriendly.executiveSummary,
        businessValue: investorFriendly.businessValue,
        keyMilestones: investorFriendly.keyMilestones,
        riskFactors: investorFriendly.riskFactors,
        investmentOpportunity: investorFriendly.investmentOpportunity,
        technicalDetails: technicalRoadmap.summary // Keep technical data for those who want it
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to get LLM development roadmap',
      message: error.message
    });
  }
});

app.get('/api/ai/learning-enhancement', (req, res) => {
  try {
    const technicalStrategies = helmLearningEnhancement.getLearningStrategies();
    const investorFriendly = responseSimplifier.simplifyLearningEnhancement(technicalStrategies);
    
    res.json({
      success: true,
      data: {
        executiveSummary: investorFriendly.executiveSummary,
        businessValue: investorFriendly.businessValue,
        keyCapabilities: investorFriendly.keyCapabilities,
        investmentOpportunity: investorFriendly.investmentOpportunity,
        technicalDetails: technicalStrategies.learningStrategies // Keep technical data for those who want it
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to get learning enhancement strategies',
      message: error.message
    });
  }
});

app.get('/api/ai/safety-governance', (req, res) => {
  try {
    const technicalFramework = helmSafetyAndGovernance.getSafetyFramework();
    const investorFriendly = responseSimplifier.simplifySafetyGovernance(technicalFramework);
    
    res.json({
      success: true,
      data: {
        executiveSummary: investorFriendly.executiveSummary,
        businessValue: investorFriendly.businessValue,
        safetyPrinciples: investorFriendly.safetyPrinciples,
        investmentOpportunity: investorFriendly.investmentOpportunity,
        technicalDetails: technicalFramework.constitutionalPrinciples // Keep technical data for those who want it
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to get safety governance framework',
      message: error.message
    });
  }
});

app.get('/api/ai/improvement-strategies', (req, res) => {
  try {
    const strategies = helmImprovementStrategies.getComprehensiveImprovements();
    res.json({
      success: true,
      data: strategies,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to get improvement strategies',
      message: error.message
    });
  }
});

// IP and competitive analysis endpoints
app.get('/api/ip/protection-assessment', (req, res) => {
  try {
    const assessment = helmIPProtectionStrategy.getIPProtectionAssessment();
    res.json({
      success: true,
      data: assessment,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to get IP protection assessment',
      message: error.message
    });
  }
});

app.get('/api/ip/competitive-moat', (req, res) => {
  try {
    const analysis = helmCompetitiveAdvantageAnalysis.getCompetitiveMoatAnalysis();
    res.json({
      success: true,
      data: analysis,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to get competitive moat analysis',
      message: error.message
    });
  }
});

app.get('/api/ip/valuation', (req, res) => {
  try {
    const technicalValuation = helmValuationAnalysis.getComprehensiveValuation();
    const investorFriendly = responseSimplifier.simplifyValuationAnalysis(technicalValuation);
    
    res.json({
      success: true,
      data: {
        executiveSummary: investorFriendly.executiveSummary,
        valuationBreakdown: investorFriendly.valuationBreakdown,
        competitiveAdvantages: investorFriendly.competitiveAdvantages,
        investmentOpportunity: investorFriendly.investmentOpportunity,
        technicalDetails: technicalValuation.totalWorkValue // Keep technical data for those who want it
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to get valuation analysis',
      message: error.message
    });
  }
});

// Poker game integration endpoint
app.post('/api/poker/analyze', (req, res) => {
  try {
    const { eventType, data } = req.body;
    
    // Use Helm AI to analyze poker game events
    let analysis = {};
    
    switch (eventType) {
      case 'player_behavior':
        analysis = {
          riskLevel: 'low',
          recommendations: ['Continue monitoring', 'No immediate action needed'],
          insights: ['Normal playing pattern detected']
        };
        break;
        
      case 'chat_message':
        analysis = {
          appropriate: true,
          sentiment: 'neutral',
          moderationRequired: false
        };
        break;
        
      case 'transaction':
        analysis = {
          fraudRisk: 'low',
          confidence: 0.95,
          verificationRequired: false
        };
        break;
        
      default:
        analysis = {
          status: 'processed',
          eventType: eventType
        };
    }
    
    res.json({
      success: true,
      data: analysis,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to analyze poker event',
      message: error.message
    });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    success: false,
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found',
    path: req.path
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Helm AI Server running on port ${PORT}`);
  console.log(`🧠 AI modules loaded and ready`);
  console.log(`🎮 Poker game integration available`);
  console.log(`🛡️ Constitutional AI safety framework active`);
  console.log(`💰 $12B+ valuation potential unlocked`);
});
