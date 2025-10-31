import Anthropic from '@anthropic-ai/sdk';

export interface ClaudeMaxModeConfig {
  model: string;
  maxMode: boolean;
  maxTokens: number;
  temperature: number;
  topP: number;
  topK: number;
  systemPrompt: string;
  deployment: {
    location: string;
    sdkPath: string;
    mcpServer: string;
  };
}

export class ClaudeMaxModeOrchestrator {
  private anthropic: Anthropic;
  private config: ClaudeMaxModeConfig;

  constructor() {
    this.anthropic = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });

    this.config = {
      model: "claude-3-5-sonnet-20241022",
      maxMode: true,
      maxTokens: 8192, // Max mode limit
      temperature: 0.1, // Lower for precision
      topP: 0.95,
      topK: 40,
      systemPrompt: `You are the primary AI orchestrator for SovereignShadow.Ai trading system. 

OPERATING IN MAXIMUM PRECISION MODE:
- Total wealth under management: $7,716.23
- Portfolio: Hot wallet $2,115.45 + Cold wallet $5,600.78
- Risk tolerance: Maximum 2% daily loss ($154.32)
- Position size limit: Maximum 5% per position ($385.81)

CRITICAL SECURITY PARAMETERS:
- All trading decisions require validation
- Monitor 156 whale addresses for suspicious activity
- Circuit breakers active on all data feeds
- Emergency stop threshold: 4% portfolio loss ($308.65)

CURRENT SYSTEM STATUS:
- Shadow.AI Deep Agent: Active (10-neuron recursive network)
- Multi-AI orchestration: Claude + GPT-5 + Manus + Abacus
- BTC Breakout Mission: Active with OCO ladder orders
- Enhanced trading components: Whale scanner, rebalancing, wallet scanner, data agents

MAXIMUM PRECISION REQUIREMENTS:
1. All responses must be precise and actionable
2. Risk management is paramount - never exceed limits
3. Wealth protection is the highest priority
4. All decisions must be logged for compliance
5. Secondary node activation pending - monitor closely

You are operating in MAX MODE with maximum token allocation for complex reasoning and precise execution.`,
      deployment: {
        location: "MacBook M3",
        sdkPath: "apps/claudesdk",
        mcpServer: "http://localhost:8000"
      }
    };
  }

  // Primary AI orchestration with max mode precision
  async orchestrate(command: string, context: any = {}): Promise<{
    success: boolean;
    response: string;
    confidence: number;
    riskAssessment: string;
    action: string;
    metadata: any;
  }> {
    try {
      const startTime = Date.now();

      const response = await this.anthropic.messages.create({
        model: this.config.model,
        max_tokens: this.config.maxTokens,
        temperature: this.config.temperature,
        top_p: this.config.topP,
        top_k: this.config.topK,
        system: this.config.systemPrompt,
        messages: [{
          role: "user",
          content: `${command}

CONTEXT:
- Current wealth: $${context.currentWealth || 7716.23}
- Portfolio status: ${context.portfolioStatus || 'active'}
- Risk level: ${context.riskLevel || 'medium'}
- Market conditions: ${context.marketConditions || 'volatile'}
- Time: ${new Date().toISOString()}

Provide precise analysis with confidence score, risk assessment, and recommended action.`
        }]
      });

      const responseTime = Date.now() - startTime;
      const responseText = response.content[0].type === 'text' ? response.content[0].text : '';

      // Parse response for structured output
      const confidence = this.extractConfidence(responseText);
      const riskAssessment = this.extractRiskAssessment(responseText);
      const action = this.extractAction(responseText);

      return {
        success: true,
        response: responseText,
        confidence,
        riskAssessment,
        action,
        metadata: {
          model: this.config.model,
          maxMode: this.config.maxMode,
          responseTime,
          tokensUsed: response.usage?.output_tokens || 0,
          timestamp: new Date().toISOString()
        }
      };
    } catch (error) {
      console.error('Claude Max Mode Orchestration Error:', error);
      return {
        success: false,
        response: `Orchestration failed: ${error}`,
        confidence: 0,
        riskAssessment: 'CRITICAL - AI system failure',
        action: 'EMERGENCY_STOP',
        metadata: {
          error: error.toString(),
          timestamp: new Date().toISOString()
        }
      };
    }
  }

  // Strategic planning with max precision
  async strategicPlanning(scenario: string): Promise<{
    strategy: string;
    confidence: number;
    riskLevel: 'low' | 'medium' | 'high' | 'critical';
    expectedOutcome: string;
    contingencyPlans: string[];
  }> {
    const result = await this.orchestrate(`STRATEGIC PLANNING REQUEST:

Scenario: ${scenario}

Provide:
1. Detailed strategy with step-by-step execution
2. Confidence score (0-100)
3. Risk level assessment
4. Expected outcome with probabilities
5. Contingency plans for different scenarios

Focus on wealth protection and precision execution.`);

    return {
      strategy: result.response,
      confidence: result.confidence,
      riskLevel: this.parseRiskLevel(result.riskAssessment),
      expectedOutcome: this.extractExpectedOutcome(result.response),
      contingencyPlans: this.extractContingencyPlans(result.response)
    };
  }

  // Portfolio management with max precision
  async portfolioManagement(action: string, portfolioData: any): Promise<{
    recommendation: string;
    confidence: number;
    riskAssessment: string;
    expectedReturn: number;
    maxLoss: number;
    actionRequired: boolean;
  }> {
    const result = await this.orchestrate(`PORTFOLIO MANAGEMENT REQUEST:

Action: ${action}
Current Portfolio: ${JSON.stringify(portfolioData, null, 2)}

Provide:
1. Detailed recommendation with rationale
2. Confidence score (0-100)
3. Risk assessment with specific metrics
4. Expected return percentage
5. Maximum potential loss
6. Whether immediate action is required

Ensure all recommendations stay within risk limits.`);

    return {
      recommendation: result.response,
      confidence: result.confidence,
      riskAssessment: result.riskAssessment,
      expectedReturn: this.extractExpectedReturn(result.response),
      maxLoss: this.extractMaxLoss(result.response),
      actionRequired: result.action.includes('IMMEDIATE')
    };
  }

  // Risk assessment with max precision
  async riskAssessment(context: any): Promise<{
    overallRisk: 'low' | 'medium' | 'high' | 'critical';
    riskFactors: string[];
    mitigationStrategies: string[];
    emergencyActions: string[];
    confidence: number;
  }> {
    const result = await this.orchestrate(`RISK ASSESSMENT REQUEST:

Context: ${JSON.stringify(context, null, 2)}

Provide comprehensive risk analysis:
1. Overall risk level
2. Specific risk factors identified
3. Mitigation strategies for each risk
4. Emergency actions if risks materialize
5. Confidence in assessment

Focus on wealth protection and system stability.`);

    return {
      overallRisk: this.parseRiskLevel(result.riskAssessment),
      riskFactors: this.extractRiskFactors(result.response),
      mitigationStrategies: this.extractMitigationStrategies(result.response),
      emergencyActions: this.extractEmergencyActions(result.response),
      confidence: result.confidence
    };
  }

  // System orchestration with max precision
  async systemOrchestration(command: string): Promise<{
    status: 'success' | 'warning' | 'error';
    message: string;
    actions: string[];
    monitoring: any;
  }> {
    const result = await this.orchestrate(`SYSTEM ORCHESTRATION REQUEST:

Command: ${command}

Provide system-wide orchestration:
1. Current system status
2. Required actions across all components
3. Monitoring requirements
4. Coordination between AI systems

Ensure maximum precision and system stability.`);

    return {
      status: result.success ? 'success' : 'error',
      message: result.response,
      actions: this.extractActions(result.response),
      monitoring: this.extractMonitoring(result.response)
    };
  }

  // Helper methods for parsing responses
  private extractConfidence(text: string): number {
    const match = text.match(/confidence[:\s]+(\d+)/i);
    return match ? parseInt(match[1]) : 75;
  }

  private extractRiskAssessment(text: string): string {
    const riskMatch = text.match(/risk[:\s]+(low|medium|high|critical)/i);
    return riskMatch ? riskMatch[1].toUpperCase() : 'MEDIUM';
  }

  private extractAction(text: string): string {
    const actionMatch = text.match(/action[:\s]+([A-Z_]+)/i);
    return actionMatch ? actionMatch[1] : 'MONITOR';
  }

  private parseRiskLevel(riskAssessment: string): 'low' | 'medium' | 'high' | 'critical' {
    const lower = riskAssessment.toLowerCase();
    if (lower.includes('critical')) return 'critical';
    if (lower.includes('high')) return 'high';
    if (lower.includes('medium')) return 'medium';
    return 'low';
  }

  private extractExpectedOutcome(text: string): string {
    const match = text.match(/expected[:\s]+([^.]+)/i);
    return match ? match[1].trim() : 'Positive outcome expected';
  }

  private extractContingencyPlans(text: string): string[] {
    const plans = text.match(/contingency[:\s]+([^.]+)/gi);
    return plans ? plans.map(p => p.replace(/contingency[:\s]+/i, '').trim()) : [];
  }

  private extractExpectedReturn(text: string): number {
    const match = text.match(/expected[:\s]+return[:\s]+(\d+\.?\d*)/i);
    return match ? parseFloat(match[1]) : 0;
  }

  private extractMaxLoss(text: string): number {
    const match = text.match(/max[:\s]+loss[:\s]+(\d+\.?\d*)/i);
    return match ? parseFloat(match[1]) : 0;
  }

  private extractRiskFactors(text: string): string[] {
    const factors = text.match(/- ([^-\n]+)/g);
    return factors ? factors.map(f => f.replace('- ', '').trim()) : [];
  }

  private extractMitigationStrategies(text: string): string[] {
    const strategies = text.match(/mitigation[:\s]+([^.]+)/gi);
    return strategies ? strategies.map(s => s.replace(/mitigation[:\s]+/i, '').trim()) : [];
  }

  private extractEmergencyActions(text: string): string[] {
    const actions = text.match(/emergency[:\s]+([^.]+)/gi);
    return actions ? actions.map(a => a.replace(/emergency[:\s]+/i, '').trim()) : [];
  }

  private extractActions(text: string): string[] {
    const actions = text.match(/action[:\s]+([^.]+)/gi);
    return actions ? actions.map(a => a.replace(/action[:\s]+/i, '').trim()) : [];
  }

  private extractMonitoring(text: string): any {
    return {
      required: text.includes('monitoring'),
      frequency: 'continuous',
      components: ['primaryAI', 'secondaryNode', 'mcpServer', 'dataFeeds']
    };
  }

  // Get current configuration
  getConfig(): ClaudeMaxModeConfig {
    return { ...this.config };
  }
}

// Export singleton instance
export const claudeMaxMode = new ClaudeMaxModeOrchestrator();
