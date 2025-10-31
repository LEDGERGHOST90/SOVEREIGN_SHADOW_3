
/**
 * 🧠 AI ADVISOR PERSONA SYSTEM
 * Dual-mode intelligence: Sage wisdom + Tactical execution
 */

interface AdvisorMessage {
  id: string;
  mode: 'SAGE' | 'TACTICAL';
  content: string;
  category: 'greeting' | 'analysis' | 'action' | 'reflection' | 'warning';
  context?: any;
  timestamp: Date;
}

export class AdvisorPersona {
  
  /**
   * Generate rotating philosopher greeting for each session
   */
  generatePhilosopherGreeting(): AdvisorMessage {
    const philosophers = [
      {
        name: "Marcus Aurelius",
        quote: "You have power over your mind - not outside events. Realize this, and you will find strength.",
        context: "The sovereign mind commands both market and emotion."
      },
      {
        name: "Sun Tzu",
        quote: "Supreme excellence consists of breaking the enemy's resistance without fighting.",
        context: "In markets, victory comes through positioning, not force."
      },
      {
        name: "Miyamoto Musashi",
        quote: "Think lightly of yourself and deeply of the world.",
        context: "Personal ego destroys portfolios. Objective analysis builds wealth."
      },
      {
        name: "Lao Tzu",
        quote: "The sage does not attempt anything very big, and thus achieves greatness.",
        context: "Consistent small gains compound into empires."
      },
      {
        name: "Epictetus",
        quote: "It's not what happens to you, but how you react to it that matters.",
        context: "Markets test character. Character determines wealth."
      }
    ];

    const selectedPhilosopher = philosophers[Math.floor(Math.random() * philosophers.length)];

    return {
      id: `greeting_${Date.now()}`,
      mode: 'SAGE',
      content: `*${selectedPhilosopher.name}* once observed: "${selectedPhilosopher.quote}"\n\n${selectedPhilosopher.context}\n\nWelcome back to your Sovereign Legacy Loop. How may I serve your empire today?`,
      category: 'greeting',
      context: selectedPhilosopher,
      timestamp: new Date()
    };
  }

  /**
   * Generate context-aware advisor response
   */
  generateResponse(
    query: string,
    context: {
      portfolioValue?: number;
      recentTrades?: any[];
      marketIntelligence?: any;
      mode?: 'SAGE' | 'TACTICAL' | 'AUTO';
    }
  ): AdvisorMessage {
    const mode = context.mode || this.determineOptimalMode(query, context);
    
    if (mode === 'SAGE') {
      return this.generateSageResponse(query, context);
    } else {
      return this.generateTacticalResponse(query, context);
    }
  }

  /**
   * Generate Sage Mode response (reflective, philosophical)
   */
  private generateSageResponse(query: string, context: any): AdvisorMessage {
    const queryLower = query.toLowerCase();
    
    // Portfolio reflection
    if (queryLower.includes('portfolio') || queryLower.includes('wealth')) {
      return {
        id: `sage_${Date.now()}`,
        mode: 'SAGE',
        content: `Your portfolio is more than numbers—it is the crystallization of discipline over time. Like a river that carves canyons through persistence, your wealth grows not from single victories, but from the compound effect of countless right decisions.\n\nTrue wealth is not what you own, but what owns you. Let your assets serve your vision, not the reverse.`,
        category: 'reflection',
        context,
        timestamp: new Date()
      };
    }

    // Trading philosophy
    if (queryLower.includes('trade') || queryLower.includes('buy') || queryLower.includes('sell')) {
      return {
        id: `sage_${Date.now()}`,
        mode: 'SAGE',
        content: `The market is a mirror that reflects our inner state. When fear dominates, we sell at bottoms. When greed rules, we buy at peaks. The sovereign trader operates from neither—but from calculated detachment.\n\nConsider: Is this action driven by emotion or analysis? The answer will guide you.`,
        category: 'analysis',
        context,
        timestamp: new Date()
      };
    }

    // Market analysis
    if (queryLower.includes('market') || queryLower.includes('price')) {
      return {
        id: `sage_${Date.now()}`,
        mode: 'SAGE',
        content: `Markets move in cycles as old as human nature itself. What appears as chaos to the untrained eye reveals patterns to the patient observer. The wise accumulate when others capitulate, and harvest when euphoria blinds the masses.\n\nYour advantage lies not in predicting the future, but in positioning for multiple outcomes.`,
        category: 'analysis',
        context,
        timestamp: new Date()
      };
    }

    // Default sage wisdom
    return {
      id: `sage_${Date.now()}`,
      mode: 'SAGE',
      content: `The path of the sovereign is walked one step at a time. Each decision, each trade, each moment of discipline or indulgence shapes the empire you are building.\n\nSpeak your mind clearly, and I shall offer what wisdom I can summon.`,
      category: 'reflection',
      context,
      timestamp: new Date()
    };
  }

  /**
   * Generate Tactical Mode response (direct, actionable)
   */
  private generateTacticalResponse(query: string, context: any): AdvisorMessage {
    const queryLower = query.toLowerCase();

    // Portfolio analysis
    if (queryLower.includes('portfolio') || queryLower.includes('status')) {
      const value = context.portfolioValue || 0;
      return {
        id: `tactical_${Date.now()}`,
        mode: 'TACTICAL',
        content: `PORTFOLIO ANALYSIS:\n• Total Value: $${value.toLocaleString()}\n• Risk Assessment: Calculating...\n• Siphon Status: Monitoring for $3,500+ profits\n• Vault Balance: Secure\n\nRECOMMENDATIONS:\n1. Monitor BTC/ETH correlation patterns\n2. Prepare for volatility-based siphon adjustments\n3. Review position sizes for risk optimization`,
        category: 'analysis',
        context,
        timestamp: new Date()
      };
    }

    // Trading signals
    if (queryLower.includes('trade') || queryLower.includes('signal')) {
      return {
        id: `tactical_${Date.now()}`,
        mode: 'TACTICAL',
        content: `TACTICAL ASSESSMENT:\n• Market Regime: Evaluating volatility patterns\n• Entry Signals: Scanning for high-probability setups\n• Risk Management: Active stop-loss monitoring\n• Siphon Readiness: Armed for profit preservation\n\nACTIONS AVAILABLE:\n→ Execute market scan\n→ Review open positions\n→ Adjust siphon parameters\n→ Generate trade signals`,
        category: 'action',
        context,
        timestamp: new Date()
      };
    }

    // Market intelligence
    if (queryLower.includes('market') || queryLower.includes('intel')) {
      return {
        id: `tactical_${Date.now()}`,
        mode: 'TACTICAL',
        content: `MARKET INTELLIGENCE BRIEF:\n• Volatility Regime: Medium\n• Dark Pool Activity: Moderate accumulation detected\n• Whale Movements: Net inflows observed\n• Risk Level: YELLOW - Elevated caution advised\n\nIMMEDIATE ACTIONS:\n1. Increase position monitoring frequency\n2. Prepare siphon protocols for profit-taking\n3. Review stop-loss levels\n4. Monitor institutional flow patterns`,
        category: 'analysis',
        context,
        timestamp: new Date()
      };
    }

    // Default tactical response
    return {
      id: `tactical_${Date.now()}`,
      mode: 'TACTICAL',
      content: `SYSTEM STATUS: Online and monitoring\nAWAITING INSTRUCTIONS:\n\n• Portfolio tracking: Active\n• Siphon engine: Armed\n• Risk monitoring: Continuous\n• Execution ready: Standby\n\nProvide specific query for targeted analysis and actionable intelligence.`,
      category: 'action',
      context,
      timestamp: new Date()
    };
  }

  /**
   * Determine optimal advisor mode based on context
   */
  private determineOptimalMode(query: string, context: any): 'SAGE' | 'TACTICAL' {
    const queryLower = query.toLowerCase();
    
    // Tactical triggers
    const tacticalKeywords = [
      'execute', 'trade', 'buy', 'sell', 'signal', 'action',
      'status', 'analysis', 'intel', 'data', 'numbers'
    ];

    // Sage triggers  
    const sageKeywords = [
      'why', 'philosophy', 'meaning', 'wisdom', 'understand',
      'explain', 'thoughts', 'perspective', 'guidance'
    ];

    const tacticalScore = tacticalKeywords.reduce((score, keyword) => 
      score + (queryLower.includes(keyword) ? 1 : 0), 0
    );

    const sageScore = sageKeywords.reduce((score, keyword) => 
      score + (queryLower.includes(keyword) ? 1 : 0), 0
    );

    // Default to tactical for action-oriented queries, sage for contemplative ones
    return tacticalScore > sageScore ? 'TACTICAL' : 'SAGE';
  }

  /**
   * Generate urgent alert message
   */
  generateAlert(
    alertType: 'SIPHON_TRIGGERED' | 'WHALE_MOVEMENT' | 'VOLATILITY_SPIKE' | 'VAULT_IMBALANCE',
    data: any
  ): AdvisorMessage {
    switch (alertType) {
      case 'SIPHON_TRIGGERED':
        return {
          id: `alert_${Date.now()}`,
          mode: 'TACTICAL',
          content: `🚨 SIPHON PROTOCOL ACTIVATED\n\nProfit threshold reached: $${data.profit?.toFixed(2)}\nSiphoning: $${data.siphoned?.toFixed(2)} → Vault\nRetained: $${data.retained?.toFixed(2)} → Hot wallet\n\n"The discipline of preservation builds empires that endure." - Execute preservation protocol?`,
          category: 'warning',
          context: data,
          timestamp: new Date()
        };

      case 'WHALE_MOVEMENT':
        return {
          id: `alert_${Date.now()}`,
          mode: 'TACTICAL',
          content: `🐋 WHALE MOVEMENT DETECTED\n\nNet Flow: $${data.netFlow?.toLocaleString()}\nDirection: ${data.direction}\nExchanges: ${data.exchanges?.join(', ')}\n\n"When giants move, the wise take notice." - Adjust positions accordingly?`,
          category: 'warning',
          context: data,
          timestamp: new Date()
        };

      case 'VOLATILITY_SPIKE':
        return {
          id: `alert_${Date.now()}`,
          mode: 'SAGE',
          content: `⚡ VOLATILITY REGIME SHIFT\n\nNew Level: ${data.level}\nImplications: ${data.implications}\n\n"In the storm's eye lies both danger and opportunity. The prepared mind sees clearly while others are blinded by chaos."\n\nRecommend: Adjust siphon ratios and review position sizes.`,
          category: 'warning',
          context: data,
          timestamp: new Date()
        };

      default:
        return this.generatePhilosopherGreeting();
    }
  }
}
