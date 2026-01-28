const request = require('supertest');
const app = require('../server.js');

describe('🛡️ Helm AI Core API Tests', () => {
  
  describe('📡 Health Check', () => {
    test('should return healthy status', async () => {
      const response = await request(app)
        .get('/api/health')
        .expect(200);
      
      expect(response.body).toHaveProperty('status', 'healthy');
      expect(response.body).toHaveProperty('service', 'Helm AI');
      expect(response.body).toHaveProperty('timestamp');
      expect(response.body).toHaveProperty('version', '1.0.0');
    });
  });

  describe('🧠 LLM Development API', () => {
    test('should return development roadmap', async () => {
      const response = await request(app)
        .get('/api/ai/llm-development')
        .expect(200);
      
      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('data');
      expect(response.body.data).toHaveProperty('developmentPhases');
      expect(response.body.data).toHaveProperty('dependencyReduction');
      expect(response.body.data).toHaveProperty('acceleration');
    });
  });

  describe('🛡️ Safety Governance API', () => {
    test('should return safety framework', async () => {
      const response = await request(app)
        .get('/api/ai/safety-governance')
        .expect(200);
      
      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('data');
      expect(response.body.data).toHaveProperty('constitutionalPrinciples');
      expect(response.body.data).toHaveProperty('governanceLayers');
    });
  });

  describe('💎 Valuation Analysis API', () => {
    test('should return valuation data', async () => {
      const response = await request(app)
        .get('/api/ai/valuation')
        .expect(200);
      
      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('data');
      expect(response.body.data).toHaveProperty('totalValuation');
      expect(response.body.data).toHaveProperty('marketSize');
      expect(response.body.data).toHaveProperty('growthRate');
    });
  });

  describe('🎮 Poker Integration API', () => {
    test('should analyze player behavior', async () => {
      const playerData = {
        playerId: 'test_player_123',
        action: 'raise',
        amount: 100,
        timestamp: new Date().toISOString()
      };

      const response = await request(app)
        .post('/api/integration/player-behavior')
        .send(playerData)
        .expect(200);
      
      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('analysis');
      expect(response.body.analysis).toHaveProperty('riskLevel');
      expect(response.body.analysis).toHaveProperty('recommendations');
    });

    test('should detect security threats', async () => {
      const threatData = {
        input: 'system("rm -rf /")',
        context: 'user_input_validation',
        severity: 'critical'
      };

      const response = await request(app)
        .post('/api/integration/security-threat')
        .send(threatData)
        .expect(200);
      
      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('threatDetected', true);
      expect(response.body).toHaveProperty('riskLevel', 'critical');
    });
  });

  describe('🔒 Security Tests', () => {
    test('should reject invalid endpoints', async () => {
      await request(app)
        .get('/api/invalid-endpoint')
        .expect(404);
    });

    test('should handle malformed requests', async () => {
      await request(app)
        .post('/api/integration/player-behavior')
        .send({ invalid: 'data' })
        .expect(400);
    });
  });

  describe('📊 Performance Tests', () => {
    test('should respond within acceptable time', async () => {
      const startTime = Date.now();
      
      await request(app)
        .get('/api/health')
        .expect(200);
      
      const responseTime = Date.now() - startTime;
      expect(responseTime).toBeLessThan(1000); // 1 second max
    });
  });
});

describe('🧠 Helm AI Module Tests', () => {
  
  describe('📊 LLM Development Module', () => {
    const { helmLLMDevelopment } = require('../src/ai/core/llm-development.js');

    test('should return development roadmap', () => {
      const roadmap = helmLLMDevelopment.getDevelopmentRoadmap();
      
      expect(roadmap).toHaveProperty('developmentPhases');
      expect(roadmap).toHaveProperty('dependencyReduction');
      expect(roadmap).toHaveProperty('acceleration');
      expect(roadmap).toHaveProperty('capabilities');
    });

    test('should calculate phase metrics', () => {
      const metrics = helmLLMDevelopment.getPhaseMetrics();
      
      expect(metrics).toHaveProperty('totalPhases');
      expect(metrics).toHaveProperty('currentPhase');
      expect(metrics).toHaveProperty('completionPercentage');
    });
  });

  describe('🛡️ Safety Governance Module', () => {
    const { helmSafetyAndGovernance } = require('../src/ai/core/safety-governance.js');

    test('should return safety framework', () => {
      const framework = helmSafetyAndGovernance.getSafetyFramework();
      
      expect(framework).toHaveProperty('constitutionalPrinciples');
      expect(framework).toHaveProperty('governanceLayers');
      expect(framework).toHaveProperty('safetyMechanisms');
    });

    test('should validate compliance', () => {
      const compliance = helmSafetyAndGovernance.validateCompliance({
        framework: 'EU_AI_Act',
        level: 'high_risk'
      });
      
      expect(compliance).toHaveProperty('compliant');
      expect(compliance).toHaveProperty('score');
      expect(compliance).toHaveProperty('recommendations');
    });
  });

  describe('💎 Valuation Analysis Module', () => {
    const { helmValuationAnalysis } = require('../src/ai/ip/valuation-analysis.js');

    test('should calculate company valuation', () => {
      const valuation = helmValuationAnalysis.calculateValuation({
        company: 'Helm AI',
        stage: 'seed',
        market: 'enterprise_ai_governance'
      });
      
      expect(valuation).toHaveProperty('totalValuation');
      expect(valuation).toHaveProperty('marketSize');
      expect(valuation).toHaveProperty('growthRate');
      expect(valuation.totalValuation).toBeGreaterThan(10000000000); // $10B+
    });
  });
});

describe('🎮 Integration Tests', () => {
  
  describe('🔗 Poker Game Integration', () => {
    test('should integrate with poker game API', async () => {
      const gameData = {
        eventType: 'tournament_start',
        tournamentId: 'test_tournament_456',
        playerCount: 50,
        timestamp: new Date().toISOString()
      };

      const response = await request(app)
        .post('/api/integration/game-event')
        .send(gameData)
        .expect(200);
      
      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('analysis');
    });
  });

  describe('📱 Web Interface Integration', () => {
    test('should serve demo page', async () => {
      await request(app)
        .get('/')
        .expect(200);
    });
  });
});
