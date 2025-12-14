"""
Integration Example: Combining whale_agent.py with onchain_signals.py

This demonstrates how to enhance whale detection with on-chain signals.
"""

from onchain_signals import OnChainSignals


class EnhancedWhaleDetection:
    """
    Example class showing how to combine OI-based whale detection
    with on-chain signals for more robust market analysis.
    """

    def __init__(self):
        # Initialize on-chain signals module
        self.onchain = OnChainSignals(cache_enabled=True)

    def combine_signals(self, oi_analysis: dict, symbol: str = "BTC") -> dict:
        """
        Combine Open Interest whale detection with on-chain signals

        Args:
            oi_analysis: Result from whale_agent.py analysis
                Example: {
                    'action': 'BUY',
                    'analysis': 'OI increased 2.5%...',
                    'confidence': 75
                }
            symbol: Cryptocurrency symbol

        Returns:
            Enhanced analysis with combined signals
        """
        # Get on-chain score
        onchain_data = self.onchain.get_onchain_score(symbol)

        # Combine confidence scores
        # OI confidence: 60% weight
        # On-chain score: 40% weight
        combined_confidence = (
            oi_analysis['confidence'] * 0.60 +
            abs(onchain_data['overall_score']) * 0.40
        )

        # Check for signal agreement
        oi_signal = oi_analysis['action']
        onchain_signal = onchain_data['overall_signal']

        # Determine final action
        if oi_signal == 'BUY' and onchain_signal == 'BULLISH':
            final_action = 'STRONG_BUY'
            agreement = 'CONFIRMED'
        elif oi_signal == 'SELL' and onchain_signal == 'BEARISH':
            final_action = 'STRONG_SELL'
            agreement = 'CONFIRMED'
        elif oi_signal == 'NOTHING' or onchain_signal == 'NEUTRAL':
            final_action = 'WAIT'
            agreement = 'NEUTRAL'
        else:
            final_action = 'CONFLICTED'
            agreement = 'DIVERGENCE'

        # Build enhanced analysis
        enhanced_analysis = {
            'symbol': symbol,
            'final_action': final_action,
            'agreement': agreement,
            'combined_confidence': round(combined_confidence, 2),

            # Original signals
            'oi_signal': {
                'action': oi_signal,
                'confidence': oi_analysis['confidence'],
                'analysis': oi_analysis['analysis']
            },

            'onchain_signal': {
                'signal': onchain_signal,
                'score': onchain_data['overall_score'],
                'confidence': onchain_data['confidence'],
                'recommendation': onchain_data['recommendation']
            },

            # Detailed breakdown
            'breakdown': {
                'exchange_flows': onchain_data['breakdown']['exchange_flows'],
                'whale_movements': onchain_data['breakdown']['whale_movements']
            },

            'interpretation': self._interpret_combined_signals(
                oi_signal, onchain_signal, agreement
            )
        }

        return enhanced_analysis

    def _interpret_combined_signals(self, oi_signal: str, onchain_signal: str, agreement: str) -> str:
        """
        Generate human-readable interpretation

        Args:
            oi_signal: Signal from OI analysis (BUY/SELL/NOTHING)
            onchain_signal: Signal from on-chain data (BULLISH/BEARISH/NEUTRAL)
            agreement: Agreement status (CONFIRMED/DIVERGENCE/NEUTRAL)

        Returns:
            Interpretation string
        """
        if agreement == 'CONFIRMED':
            if oi_signal == 'BUY':
                return (
                    "Strong bullish confirmation! Both OI data and on-chain metrics "
                    "suggest accumulation. High-confidence entry opportunity."
                )
            else:
                return (
                    "Strong bearish confirmation! Both OI data and on-chain metrics "
                    "suggest distribution. Consider reducing exposure or shorting."
                )

        elif agreement == 'DIVERGENCE':
            return (
                f"Signal divergence detected! OI suggests {oi_signal} but on-chain "
                f"data shows {onchain_signal} sentiment. Exercise caution and wait "
                "for alignment before taking significant positions."
            )

        else:
            return (
                "Neutral market conditions. No clear directional bias from either "
                "OI or on-chain data. Best to wait for stronger signals."
            )


# Example usage
if __name__ == "__main__":
    print("=" * 80)
    print("ENHANCED WHALE DETECTION EXAMPLE")
    print("=" * 80)

    # Initialize enhanced detector
    detector = EnhancedWhaleDetection()

    # Simulate OI analysis from whale_agent.py
    example_oi_analyses = [
        {
            'action': 'BUY',
            'analysis': 'OI increased 2.5% with price rising. Strong momentum detected.',
            'confidence': 75
        },
        {
            'action': 'SELL',
            'analysis': 'OI decreased 3.1% with price dropping. Capitulation signal.',
            'confidence': 65
        },
        {
            'action': 'NOTHING',
            'analysis': 'OI change minimal (0.3%). No significant whale activity.',
            'confidence': 40
        }
    ]

    # Test each scenario
    for i, oi_analysis in enumerate(example_oi_analyses, 1):
        print(f"\n{'=' * 80}")
        print(f"SCENARIO {i}: OI Signal = {oi_analysis['action']}")
        print('=' * 80)

        # Combine with on-chain signals
        enhanced = detector.combine_signals(oi_analysis, 'BTC')

        print(f"\nFINAL ACTION: {enhanced['final_action']}")
        print(f"Agreement Status: {enhanced['agreement']}")
        print(f"Combined Confidence: {enhanced['combined_confidence']:.2f}%")

        print(f"\nOI Signal:")
        print(f"  Action: {enhanced['oi_signal']['action']}")
        print(f"  Confidence: {enhanced['oi_signal']['confidence']}%")
        print(f"  Analysis: {enhanced['oi_signal']['analysis']}")

        print(f"\nOn-Chain Signal:")
        print(f"  Signal: {enhanced['onchain_signal']['signal']}")
        print(f"  Score: {enhanced['onchain_signal']['score']:.2f}/100")
        print(f"  Recommendation: {enhanced['onchain_signal']['recommendation']}")

        print(f"\nInterpretation:")
        print(f"  {enhanced['interpretation']}")

        print(f"\nBreakdown:")
        for component, data in enhanced['breakdown'].items():
            print(f"  {component.replace('_', ' ').title()}:")
            print(f"    Signal: {data['signal']}")
            print(f"    Score: {data['score']:.2f}")
            print(f"    Reason: {data['reason']}")

    print("\n" + "=" * 80)
    print("INTEGRATION COMPLETE")
    print("=" * 80)
    print("""
To integrate this into your whale_agent.py:

1. Add import:
   from core.signals.onchain_signals import OnChainSignals

2. In WhaleAgent.__init__():
   self.onchain = OnChainSignals(cache_enabled=True)

3. Modify _analyze_opportunity() method to include on-chain data:
   def _analyze_opportunity(self, changes, market_data):
       # ... existing AI analysis ...

       # Add on-chain analysis
       onchain_data = self.onchain.get_onchain_score('BTC')

       # Combine signals
       if analysis:  # If AI returned a signal
           # Check for confirmation
           if (analysis['action'] == 'BUY' and
               onchain_data['overall_signal'] == 'BULLISH'):
               analysis['confidence'] = min(100, analysis['confidence'] + 15)
               analysis['analysis'] += " | CONFIRMED by on-chain accumulation signals"

           elif (analysis['action'] == 'SELL' and
                 onchain_data['overall_signal'] == 'BEARISH'):
               analysis['confidence'] = min(100, analysis['confidence'] + 15)
               analysis['analysis'] += " | CONFIRMED by on-chain distribution signals"

           elif (analysis['action'] != 'NOTHING' and
                 onchain_data['overall_signal'] != 'NEUTRAL'):
               # Signals diverge - reduce confidence
               analysis['confidence'] = max(20, analysis['confidence'] - 20)
               analysis['analysis'] += " | WARNING: On-chain signals diverge!"

       return analysis

4. The on-chain module runs independently with caching, so it won't slow down
   your whale detection loop significantly.
""")
