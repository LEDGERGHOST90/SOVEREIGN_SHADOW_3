# Crypto Crash Oct 2025: Leverage Meets Liquidity | FTI

**URL:** https://www.fticonsulting.com/insights/articles/crypto-crash-october-2025-leverage-met-liquidity

---

GLOBAL
CONTACT
SERVICES
INDUSTRIES
DIGITAL
INSIGHTS
OUR EXPERTS
OUR IMPACT
CAREERS
ABOUT FTI
Home
/ Insights
/ Articles
/ The Crypto Crash of October 2025: When Leverage Met Liquidity
The Crypto Crash of October 2025: When Leverage Met Liquidity
SHARE
  

On October 10, 2025, more than $19 billion of crypto leverage was liquidated in roughly a day, sending crypto prices through levels that are still considered a “tail risk” event. This crash marked the start of a broader crypto sell-off that has continued into December. It illustrates how leverage, liquidity and venue design interact when markets are stressed.

From Tariff Headline to Margin Spiral

The October 10 crash followed a pattern that became all too familiar in 2025. A 100% China tariff threat hit global risk assets, with crypto experiencing the most severe reaction. That crypto reacts faster and stronger to negative news is not unusual in itself: crypto trades 24/7 and lacks the automatic trading halts and interventions commonly seen in other markets. What transformed this sell-off into such a crisis was the intersection of three factors: how the risk was positioned, how it was funded, and how leverage and infrastructure interacted under pressure.

Unlike Terra/Luna or FTX, this crash did not stem from fraud, insolvency or the failure of a single major institution. By early October, BTC and ETH perpetual futures open interest was elevated. Funding rates had climbed from around 10% annualized to nearly 30% by October 6, driven by the Ethereum rally. A large share of that exposure was concentrated on venues using unified (cross-asset) margin. Unified margin can be very efficient in calm markets: profits from one position offset losses elsewhere, allowing traders to increase their overall book sizes while using capital more efficiently. Under stress, however, the same design ties portfolios to their weakest assets. Those assets are typically long-only positions, and sell-offs in these may not be offset by profits from short positions.

When equity in trading accounts declines below thresholds, exchanges can forcibly liquidate positions before owners can react. Additionally, hiccups in crypto infrastructure, such as frozen exchange interfaces, prevented some traders from managing their risk dynamically or moving capital between exchanges. The combination of high leverage and exchanges’ automatic-deleveraging (“ADL”) mechanisms turned this sell-off into a margin-driven liquidation spiral.

Figure: Timeline of October 10 Cascade

How Liquidity Really Failed

Intraday order-book data showed BTC’s top-of-book depth shrinking by more than 90% on key venues that day, with bid-ask spreads widening from single-digit basis points to double-digit percentages at the extremes. Liquidity still existed, but only in small clips and at prices that did little to clear the imbalance of sellers over buyers. As executable order size evaporated, many market makers either widened their spreads dramatically or stepped away altogether.

The October 10 crash reminded us of market lessons that are often forgotten during lulls and upcycles: Markets trade at the margin, not at the mean. Market depth is a nonlinear variable that declines sharply during crises. Market impact increases when trade sizes remain constant and volume shrinks. These dynamics exacerbate any sell-off through negative feedback loops. When some crypto books effectively operate with 20-50x leverage, their primary risk lies not in the directional bets but in scenarios where liquidity disappears and exchange infrastructures turn unreliable at the same time.

When a Stablecoin Lost Its Peg

The most revealing microstructure episode was not the price action of major coins like BTC, but what happened to USDe, a delta-neutral stablecoin designed to hold a 1:1 value with the U.S. dollar. During the worst of the sell-off, USDe traded in the mid-$0.60s on Binance — implying a ~35% discount — while on other exchanges, and in several DeFi pools, it stayed much closer to $1.

This pricing divergence had little to do with fundamentals and everything to do with venue microstructure. The key issue was how local prices fed into oracles and margin engines. Many leveraged products priced collateral using the venue’s own spot price, either directly or via a simple internal oracle. When USDe crashed on Binance, margin systems marked it down sharply, reduced collateral values and pushed thousands of accounts through maintenance thresholds. Positions that could have remained solvent under cross-venue pricing were liquidated simply because Binance’s market traded through the peg.

When the Backstop Has To Liquidate Winners

Exchanges protect themselves from leveraged traders whose accounts fall into deficit when markets gap. When standard tools such as margin calls, liquidations and backstop programs (if any) are not enough, ADL kicks in, forcibly closing profitable positions on the other side of those trades to plug the deficit. This creates a distinct risk: ADL can involuntarily close profitable shorts, turning a hedged portfolio into a naked one during periods of stress.

On October 10, some of the best-hedged shorts found their positions reduced or entirely closed to maintain exchange solvency. From an exchange’s perspective, ADL is preferable to an outright default or a retrospective socialized loss (“clawback”). From a trader’s perspective, it adds a second layer of risk: the underlying economics of the trade, and the rules that dictate whether it will be allowed to persist when it matters most. Desks that rely on derivatives as hedging tools should incorporate ADL mechanics into their counterparty due diligence.

The Structural Gap Versus Traditional Markets

Traditional markets have built safety rails after their own flash-crash episodes: circuit breakers, central counterparties with conservative margin models and strict leverage limits for retail. Crypto venues play several of these roles at once, but risk is concentrated in venue-level margin engines, high leverage is widely available and price discovery is fragmented across exchanges with inconsistent practices. October’s crash revealed where this framework breaks, particularly when high leverage, exotic collateral and internalized pricing are at play.

What Has and Hasn’t Changed

Two months later, some excess has been drained from crypto markets. Crypto markets weakened, diverging from the broader trend of most other risk assets. BTC has declined ~30% from its all-time high in early October. Bitcoin ETFs experienced significant outflows. Open interest is down more than 40% from October highs.

Funding levels on perpetual futures have normalized. Several large venues tightened leverage caps on selected pairs, raised haircuts on fragile collateral and announced steps toward multi-venue pricing for key oracles. Millions of accounts were closed, leveraged players were forced out and retail inflows into leveraged products have cooled.

However, the underlying economics remain the same. As long as traders are willing to pay for leverage, someone will offer it. This keeps the cycle going and ensures crypto remains a volatile asset class.

Lessons for the Next Cycle

For traders and risk managers, headline leverage is only the starting point. Effective leverage depends on the behavior of the collateral basket under stress. Risk teams should model executable size, not just spreads, and build scenarios where market depth shrinks by 90% for short periods. Concentrating positions, collateral and oracles on a single venue saves margin in quiet times but can turn into a single point of failure when conditions become unstable.

For exchanges and infrastructure providers, the priority is “plumbing first.” Multi-venue, liquidity-weighted oracles with outlier controls should become standard. Liquidation engines should be tested against short, violent dislocations rather than smoother historical paths. Transparent documentation of margin logic, haircuts and ADL triggers would benefit all participants.

For allocators, due diligence now extends to how platforms handled this episode: venues, rulebooks and risk infrastructure belong alongside counterparty and legal terms.

For participants with large exposure, these are no longer optional questions.

Related Information
Blockchain Consulting & Digital Asset Management
Financial Services
Published

December 24, 2025

Key Contacts

Volkan Kubali, Ph.D

Managing Director

Most Popular Insights
Navigating Tariffs: 10 Strategies to Protect the Bottom Line
The Hidden Risk for Data Centers That No One is Talking About
It’s La La Land Again in Financial Markets
Geopolitical Risk Management: No Longer Just a “Nice to Have”, But a Corporate Imperative
Corporate Sustainability Report
Sign up to get access to FTI Consulting Insights
Subscribe

SERVICES
INDUSTRIES
INSIGHTS
OUR EXPERTS
LOCATIONS
CAREERS
ABOUT FTI
NEWS
INVESTOR RELATIONS

© 2025 FTI Consulting, Inc., including its subsidiaries and affiliates, is a consulting firm and is not a certified public accounting firm or a law firm. All Rights Reserved.

Stay Connected
Legal
Privacy
Cookie Policy
Sitemap