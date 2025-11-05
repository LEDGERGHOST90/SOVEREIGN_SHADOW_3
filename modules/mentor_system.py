#!/usr/bin/env python3
"""
🏴 SOVEREIGN SHADOW II - MENTOR SYSTEM
NetworkChuck-Style Trading Education Delivery System

Philosophy: "Learn the right way, or don't learn at all."
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class LessonStatus(Enum):
    """Lesson completion status"""
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class QuizDifficulty(Enum):
    """Quiz difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class LessonProgress:
    """Track progress through a lesson"""
    lesson_id: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    quiz_score: Optional[float] = None
    attempts: int = 0
    time_spent_minutes: int = 0


@dataclass
class MentorState:
    """User's overall progress through curriculum"""
    current_chapter: int = 1
    current_lesson: int = 1
    total_lessons_completed: int = 0
    paper_trades_completed: int = 0
    paper_trade_win_rate: float = 0.0
    ready_for_live_trading: bool = False
    lessons_progress: Dict[str, Dict] = None
    created_at: str = None
    last_updated: str = None

    def __post_init__(self):
        if self.lessons_progress is None:
            self.lessons_progress = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.last_updated is None:
            self.last_updated = datetime.now().isoformat()


class MentorSystem:
    """
    Progressive Trading Education System

    Delivers NetworkChuck-style trading education in structured format.
    Enforces learning requirements before live trading.
    """

    def __init__(self, state_file: str = "logs/mentor/mentor_state.json"):
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        self.state = self._load_state()
        self.curriculum = self._build_curriculum()

        print("🎓 MENTOR SYSTEM initialized")
        print(f"   Current: Chapter {self.state.current_chapter}, Lesson {self.state.current_lesson}")
        print(f"   Progress: {self.state.total_lessons_completed}/42 lessons completed")
        print(f"   Paper Trades: {self.state.paper_trades_completed} (Win Rate: {self.state.paper_trade_win_rate:.1%})")

    def _load_state(self) -> MentorState:
        """Load or create mentor state"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                data = json.load(f)
                return MentorState(**data)
        return MentorState()

    def _save_state(self):
        """Save mentor state"""
        self.state.last_updated = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(asdict(self.state), f, indent=2)

    def _build_curriculum(self) -> Dict[int, Dict]:
        """
        Build complete trading curriculum from education materials
        """
        return {
            1: {
                "title": "Chapter 1: Why This Strategy Works",
                "description": "Understanding the foundation of the 15m/4h multi-timeframe strategy",
                "lessons": [
                    {
                        "id": "1.1",
                        "title": "The Two-Timeframe Philosophy",
                        "content": """
The 15-minute/4-hour strategy is built on a simple truth:
- The 4-hour chart shows you WHERE you are
- The 15-minute chart shows you WHEN to act

Think of it like navigation:
- 4H = Your GPS (shows the big picture, the direction)
- 15M = Your steering wheel (shows immediate next moves)

You wouldn't drive looking only at GPS (you'd crash).
You wouldn't drive looking only at the road ahead (you'd get lost).
You need BOTH.
                        """,
                        "key_points": [
                            "4H timeframe = Market structure & trend",
                            "15M timeframe = Precise entry timing",
                            "Never trade against 4H trend",
                            "Use 15M for entry confirmation only"
                        ],
                        "quiz": [
                            {
                                "question": "What does the 4-hour chart tell you?",
                                "options": ["Entry timing", "Market structure", "Exact price", "None"],
                                "correct": 1
                            },
                            {
                                "question": "Can you take a LONG trade if 4H is bearish?",
                                "options": ["Yes", "No", "Maybe", "Sometimes"],
                                "correct": 1
                            }
                        ]
                    },
                    {
                        "id": "1.2",
                        "title": "Why Most Traders Fail",
                        "content": """
Three reasons traders blow up their accounts:

1. SINGLE TIMEFRAME TUNNEL VISION
   - Looking only at 1-minute or 5-minute charts
   - No big picture context
   - Chasing every move = death by 1000 cuts

2. NO RISK MANAGEMENT
   - "All in" on every trade
   - No stop losses
   - One bad trade = account gone

3. EMOTIONAL TRADING
   - Revenge trading after losses
   - FOMO (Fear Of Missing Out)
   - Greed (not taking profits)

This system FORCES you to avoid all three mistakes.
                        """,
                        "key_points": [
                            "Single timeframe = tunnel vision",
                            "No risk management = account blown",
                            "Emotions = trading killer",
                            "System prevents all three mistakes"
                        ]
                    }
                ]
            },

            2: {
                "title": "Chapter 2: Understanding Two Timeframes",
                "description": "Deep dive into 4H structure and 15M execution",
                "lessons": [
                    {
                        "id": "2.1",
                        "title": "Reading the 4-Hour Chart",
                        "content": """
The 4H chart answers ONE question: "Which direction is the market moving?"

What to look for on 4H:
1. TREND: Higher highs? Lower lows? Sideways?
2. EMA 50/200: Price above = bullish, below = bearish
3. SUPPORT/RESISTANCE: Where did price bounce before?
4. RSI: Above 50 = strength, below 50 = weakness

The 4H gives you the "permission slip" to trade.
- 4H bullish? Look for LONG setups on 15M
- 4H bearish? Look for SHORT setups on 15M
- 4H sideways? DON'T TRADE (range = chop = losses)

NEVER fight the 4H trend. You will lose.
                        """,
                        "key_points": [
                            "4H shows market direction",
                            "EMA 50/200 = trend filter",
                            "Only trade WITH 4H trend",
                            "Sideways 4H = stay out"
                        ],
                        "quiz": [
                            {
                                "question": "If 4H chart shows lower lows, what do you do?",
                                "options": ["Look for LONG", "Look for SHORT", "Don't trade", "Go all in"],
                                "correct": 1
                            },
                            {
                                "question": "If price is below EMA 50 and 200 on 4H, trend is?",
                                "options": ["Bullish", "Bearish", "Neutral", "Unknown"],
                                "correct": 1
                            }
                        ]
                    },
                    {
                        "id": "2.2",
                        "title": "Reading the 15-Minute Chart",
                        "content": """
The 15M chart answers ONE question: "Is NOW the right time to enter?"

What to look for on 15M:
1. EMA 21: Price above = micro-bullish, below = micro-bearish
2. PULLBACK to support/resistance
3. VOLUME confirmation (higher volume = real move)
4. RSI: Not overbought (>70) or oversold (<30)

The 15M gives you the "trigger".

Example LONG setup:
- 4H: Bullish trend ✅
- 15M: Price pulls back to EMA 21 ✅
- 15M: Bounces off support ✅
- 15M: Volume increases ✅
- RSI: Between 40-60 ✅
→ ENTRY TRIGGER

Wait for ALL conditions. Patience = profits.
                        """,
                        "key_points": [
                            "15M shows entry timing",
                            "Wait for pullback to key level",
                            "Need volume confirmation",
                            "RSI must be neutral (40-60)"
                        ]
                    }
                ]
            },

            3: {
                "title": "Chapter 3: Risk Management (The Real Secret)",
                "description": "Position sizing, stop losses, and the 1-2% rule",
                "lessons": [
                    {
                        "id": "3.1",
                        "title": "The 1-2% Rule (Non-Negotiable)",
                        "content": """
MOST IMPORTANT LESSON IN THIS ENTIRE COURSE:

Only risk 1-2% of your account per trade.

Why?
- You can be wrong 10 times in a row and still be alive
- Protects you from one bad day destroying you
- Removes emotion (small losses = no panic)

The Formula:
    Position Size = (Account × Risk%) / (Entry - Stop Loss)

Example:
    Account: $1,660
    Risk: 2% = $33.20
    Entry: $99,000
    Stop: $97,000
    Distance: $2,000

    Position Size = $33.20 / $2,000 = 0.0166 BTC
    Position Value = 0.0166 × $99,000 = $1,643

If you lose, you lose $33.20 (2%). Not $1,643.
If you win 1:2, you make $66.40 (4%).

That's how you grow accounts. Slow, steady, disciplined.
                        """,
                        "key_points": [
                            "Only risk 1-2% per trade",
                            "Position size = (Account × Risk%) / Stop Distance",
                            "Small losses = survival",
                            "Consistency beats home runs"
                        ],
                        "quiz": [
                            {
                                "question": "If your account is $1,000 and you risk 2%, what's your risk amount?",
                                "options": ["$10", "$20", "$200", "$100"],
                                "correct": 1
                            },
                            {
                                "question": "What happens if you risk 20% per trade?",
                                "options": ["Get rich quick", "5 losses = account gone", "Perfectly safe", "Recommended"],
                                "correct": 1
                            }
                        ]
                    },
                    {
                        "id": "3.2",
                        "title": "Stop Losses (Your Life Insurance)",
                        "content": """
Stop loss = The price where you say "I was wrong, get me out"

Rules:
1. ALWAYS set stop loss BEFORE entering
2. Place it below support (LONG) or above resistance (SHORT)
3. NEVER move it further away (that's denial)
4. Let it hit if needed (accept the loss)

Common mistake: "Let me just hold a bit longer..."
→ That's how -2% losses become -20% disasters

Where to place stops:
- LONG: Below recent swing low or support
- SHORT: Above recent swing high or resistance
- Distance: Usually 2-3% from entry

The stop loss is your safety net. Don't trade without it.
                        """,
                        "key_points": [
                            "Always set stop BEFORE entry",
                            "Place below support / above resistance",
                            "Never move stop further away",
                            "Accept losses gracefully"
                        ]
                    },
                    {
                        "id": "3.3",
                        "title": "Risk:Reward Ratio (The Profit Math)",
                        "content": """
Risk:Reward (R:R) = How much you make vs how much you risk

Minimum ratio: 1:2
- Risk $1 to make $2
- Risk 2% to make 4%

Why 1:2 minimum?
- You can win 40% of trades and STILL be profitable
- Math: Win 4 trades × 4% = +16%, Lose 6 trades × -2% = -12%
- Net: +4% even with 40% win rate

How to find good R:R:
1. Entry at $99,000
2. Stop at $97,000 (risk = $2,000)
3. Target at $103,000 (reward = $4,000)
4. R:R = $4,000/$2,000 = 1:2 ✅

If R:R is less than 1:2, DON'T TAKE THE TRADE.
Wait for better setup.
                        """,
                        "key_points": [
                            "Minimum R:R = 1:2",
                            "Risk $1 to make $2+",
                            "Good R:R = profitable even with 40% wins",
                            "Don't take trades under 1:2"
                        ]
                    }
                ]
            },

            4: {
                "title": "Chapter 4: Psychology & Discipline (The Real Game)",
                "description": "Emotions, the 3-strike rule, and trading psychology",
                "lessons": [
                    {
                        "id": "4.1",
                        "title": "The Four Emotions That Kill Accounts",
                        "content": """
Trading is 20% strategy, 80% psychology.

The Four Killers:

1. FEAR
   - Symptom: Won't take good setups
   - Cause: Past losses or scared of losing
   - Fix: Trust the process, follow the system

2. GREED
   - Symptom: Won't take profits, "it'll go higher!"
   - Cause: Wanting to maximize every trade
   - Fix: Take profits at target, don't get greedy

3. REVENGE TRADING
   - Symptom: Trading right after a loss to "get it back"
   - Cause: Ego, anger, frustration
   - Fix: 3-strike rule (stop after 3 losses)

4. FOMO (Fear Of Missing Out)
   - Symptom: Jumping into trades without setup
   - Cause: Seeing others make money
   - Fix: Wait for YOUR setup, ignore noise

The system protects you from all four.
                        """,
                        "key_points": [
                            "Fear stops you from taking good trades",
                            "Greed stops you from taking profits",
                            "Revenge trading = guaranteed losses",
                            "FOMO = entering without setup"
                        ]
                    },
                    {
                        "id": "4.2",
                        "title": "The 3-Strike Rule",
                        "content": """
RULE: If you lose 3 trades in one day, you're DONE.
Close the charts. Walk away. Come back tomorrow.

Why?
- After 3 losses, you're emotional
- Emotional = bad decisions
- Bad decisions = more losses
- It's a spiral

What to do after 3 losses:
1. Close your trading platform
2. Log what went wrong (journal)
3. Take a break (gym, walk, coffee)
4. Review trades tomorrow with clear head
5. Find the pattern (did you break a rule?)

Some days, the market doesn't make sense.
Some days, YOU don't make sense.
The 3-strike rule saves you from yourself.
                        """,
                        "key_points": [
                            "3 losses in one day = stop trading",
                            "Emotional trading = disaster",
                            "Walk away and reset",
                            "Review trades with clear mind"
                        ],
                        "quiz": [
                            {
                                "question": "You've lost 3 trades today. What do you do?",
                                "options": ["Trade more to recover", "Stop trading for the day", "Go all in", "Panic"],
                                "correct": 1
                            }
                        ]
                    }
                ]
            },

            5: {
                "title": "Chapter 5: Technical Indicators (Your Tools)",
                "description": "EMA, RSI, Volume, and Support/Resistance",
                "lessons": [
                    {
                        "id": "5.1",
                        "title": "Exponential Moving Averages (EMA)",
                        "content": """
EMA = Average price over X periods, gives more weight to recent prices

We use THREE EMAs:

4-Hour Chart:
- EMA 50: Medium-term trend
- EMA 200: Long-term trend
- Price above both = bullish
- Price below both = bearish

15-Minute Chart:
- EMA 21: Short-term trend
- Price above = micro-bullish
- Price below = micro-bearish

How to use:
- 4H: Price above EMA 50 & 200 = look for LONGS
- 15M: Wait for pullback to EMA 21, then bounce = entry

Think of EMAs as "support levels" in uptrends,
and "resistance levels" in downtrends.
                        """,
                        "key_points": [
                            "4H: EMA 50 & 200 = trend direction",
                            "15M: EMA 21 = entry timing",
                            "Price above EMAs = bullish",
                            "Price below EMAs = bearish"
                        ]
                    },
                    {
                        "id": "5.2",
                        "title": "RSI (Relative Strength Index)",
                        "content": """
RSI = Measures if market is overbought or oversold (0-100 scale)

Zones:
- RSI > 70 = Overbought (price pushed too high, might reverse)
- RSI < 30 = Oversold (price pushed too low, might reverse)
- RSI 40-60 = Neutral (healthy zone for entries)

How we use it:
4H Chart:
- RSI > 50 = Strong trend
- RSI < 50 = Weak trend

15M Chart:
- Don't enter if RSI > 70 (overbought)
- Don't enter if RSI < 30 (oversold)
- Best entries = RSI between 40-60

RSI is a FILTER, not a signal.
Wait for RSI in neutral zone before entering.
                        """,
                        "key_points": [
                            "RSI shows overbought/oversold conditions",
                            ">70 = overbought, <30 = oversold",
                            "Best entries at RSI 40-60",
                            "Use as confirmation, not signal"
                        ]
                    },
                    {
                        "id": "5.3",
                        "title": "Volume (The Truth Serum)",
                        "content": """
Volume = How many coins were bought/sold

Why it matters:
- High volume = real move (strong conviction)
- Low volume = fake move (weak, might reverse)

Rule: Only take trades with INCREASING volume

Example:
- Price breaks resistance on LOW volume = fake breakout
- Price breaks resistance on HIGH volume = real breakout

How to check:
- Look at volume bars at bottom of chart
- Green bar bigger than average = good
- Red bar bigger than average = watch out

Volume confirms conviction.
No volume = no trade.
                        """,
                        "key_points": [
                            "Volume shows strength of move",
                            "High volume = real move",
                            "Low volume = fake move",
                            "Only trade on increasing volume"
                        ]
                    },
                    {
                        "id": "5.4",
                        "title": "Support & Resistance (The Levels That Matter)",
                        "content": """
Support = Price level where buyers step in (floor)
Resistance = Price level where sellers step in (ceiling)

How to find them:
1. Look for previous HIGHS (resistance)
2. Look for previous LOWS (support)
3. Look for flat areas where price bounced multiple times

Why they matter:
- Support = good place for stop loss (LONG)
- Resistance = good place for take profit (LONG)
- Resistance = good place for stop loss (SHORT)
- Support = good place for take profit (SHORT)

Pro tip: Previous resistance becomes support (and vice versa)
Example: $99k was resistance, broke through, now $99k is support

Mark these levels on your chart. They're your roadmap.
                        """,
                        "key_points": [
                            "Support = buyers step in (floor)",
                            "Resistance = sellers step in (ceiling)",
                            "Use for stop loss placement",
                            "Previous resistance becomes support"
                        ]
                    }
                ]
            },

            6: {
                "title": "Chapter 6: Your First Trade (Step-by-Step)",
                "description": "Complete walkthrough of taking a trade from setup to exit",
                "lessons": [
                    {
                        "id": "6.1",
                        "title": "The Pre-Trade Checklist",
                        "content": """
NEVER enter a trade without checking all boxes:

4-HOUR CHART (Structure):
□ Clear trend (not sideways)
□ Price above/below EMA 50 & 200
□ RSI confirms trend (>50 bull, <50 bear)
□ Support/Resistance identified

15-MINUTE CHART (Entry):
□ Pullback to key level (EMA 21 or S/R)
□ Price bouncing (reversal candle)
□ EMA 21 alignment with 4H trend
□ RSI in neutral zone (40-60)
□ Volume increasing

RISK MANAGEMENT:
□ Stop loss identified (2-3% away)
□ Risk:Reward minimum 1:2
□ Position size calculated (1-2% risk)
□ Total exposure under 10%

PSYCHOLOGY:
□ Not on losing streak (under 3 losses today)
□ Clear head (not emotional)
□ Following system (not FOMO)

ALL boxes checked = take the trade
One box missing = wait for next setup
                        """,
                        "key_points": [
                            "Check 4H structure first",
                            "Confirm 15M entry timing",
                            "Validate risk management",
                            "Check psychological state",
                            "All boxes = go, one missing = wait"
                        ]
                    },
                    {
                        "id": "6.2",
                        "title": "Example Trade Walkthrough (LONG)",
                        "content": """
Real example: BTC/USDT LONG setup

STEP 1: Check 4H Chart
- Trend: Higher highs, higher lows ✅
- EMA: Price above 50 & 200 ✅
- RSI: 62 (above 50, strong) ✅
- S/R: Support at $97k identified ✅
→ 4H says: "LONG bias confirmed"

STEP 2: Check 15M Chart
- Pullback: Price touched EMA 21 at $98.5k ✅
- Bounce: Green reversal candle ✅
- EMA 21: Price above ✅
- RSI: 48 (neutral zone) ✅
- Volume: Increasing on bounce ✅
→ 15M says: "Entry trigger activated"

STEP 3: Plan Trade
- Entry: $99,000
- Stop: $97,000 (below support)
- Target: $103,000 (previous resistance)
- Risk: $2,000
- Reward: $4,000
- R:R: 1:2 ✅

STEP 4: Calculate Position Size
- Account: $1,660
- Risk: 2% = $33.20
- Position Size: $33.20 / $2,000 = 0.0166 BTC
- Position Value: $1,643

STEP 5: Execute
- Place LIMIT order at $99,000
- Set STOP LOSS at $97,000
- Set TAKE PROFIT at $103,000
- Log trade in journal

STEP 6: Manage
- Don't touch it
- Let it play out
- Either hits target or stop
- Review afterwards

That's it. Simple, systematic, repeatable.
                        """,
                        "key_points": [
                            "Check 4H first (structure)",
                            "Wait for 15M entry (timing)",
                            "Calculate position size",
                            "Set stop & target before entry",
                            "Let trade play out"
                        ]
                    }
                ]
            },

            7: {
                "title": "Chapter 7: Common Mistakes (Learn From Others)",
                "description": "The 10 mistakes that kill accounts",
                "lessons": [
                    {
                        "id": "7.1",
                        "title": "The Top 10 Trading Mistakes",
                        "content": """
1. Trading without stop loss
   → One bad trade wipes account

2. Risking too much (10%+ per trade)
   → 3 losses = 30% gone

3. Fighting the 4H trend
   → You will lose every time

4. Entering without setup
   → FOMO trading = slow death

5. Moving stop loss further away
   → Denial + bigger losses

6. Not taking profits at target
   → Greed gives back winners

7. Revenge trading after losses
   → Emotional = bad decisions

8. Over-trading (20+ trades/day)
   → Death by fees + mistakes

9. Checking trade every 5 minutes
   → Stress + emotional exits

10. Not journaling trades
    → Never learn from mistakes

The system prevents ALL of these.
Trust it.
                        """,
                        "key_points": [
                            "Always use stop losses",
                            "Risk 1-2% max per trade",
                            "Never fight 4H trend",
                            "Wait for complete setup",
                            "Take profits at target"
                        ]
                    }
                ]
            },

            8: {
                "title": "Chapter 8: Advanced Concepts (Level Up)",
                "description": "Market structure, confluences, and trade management",
                "lessons": [
                    {
                        "id": "8.1",
                        "title": "Market Structure Deep Dive",
                        "content": """
Market Structure = The pattern of highs and lows

UPTREND (Bullish Structure):
- Higher Highs (HH)
- Higher Lows (HL)
- As long as this continues = trend intact
- Break of HL = trend might be over

DOWNTREND (Bearish Structure):
- Lower Highs (LH)
- Lower Lows (LL)
- As long as this continues = trend intact
- Break of LH = trend might be over

How to use:
- In uptrend: Look for LONG at HL
- In downtrend: Look for SHORT at LH
- Structure break = possible trend change (be careful)

This is what you see on 4H chart.
                        """,
                        "key_points": [
                            "Uptrend = HH + HL",
                            "Downtrend = LH + LL",
                            "Trade at key structure points",
                            "Structure break = caution"
                        ]
                    },
                    {
                        "id": "8.2",
                        "title": "Confluences (Stacking Probabilities)",
                        "content": """
Confluence = Multiple reasons to take a trade at same level

Example high-confluence LONG setup:
1. 4H uptrend ✅
2. 15M pullback to EMA 21 ✅
3. Pullback at previous RESISTANCE (now support) ✅
4. RSI neutral (40-60) ✅
5. Volume increasing ✅
6. Fibonacci 61.8% retracement ✅

More confluences = higher probability trade

Look for 3+ confluences before entering.

The best trades have everything lining up at same level.
That's not luck. That's structure.
                        """,
                        "key_points": [
                            "Confluence = multiple reasons at same level",
                            "Look for 3+ confirmations",
                            "More confluences = better setup",
                            "Best trades have everything aligned"
                        ]
                    }
                ]
            }
        }

    def get_current_lesson(self) -> Optional[Dict[str, Any]]:
        """Get the lesson user should work on next"""
        chapter = self.curriculum.get(self.state.current_chapter)
        if not chapter:
            return None

        lessons = chapter["lessons"]
        if self.state.current_lesson <= len(lessons):
            lesson = lessons[self.state.current_lesson - 1]
            return {
                "chapter": self.state.current_chapter,
                "lesson_num": self.state.current_lesson,
                "lesson_id": lesson["id"],
                "chapter_title": chapter["title"],
                "lesson_title": lesson["title"],
                "content": lesson["content"],
                "key_points": lesson.get("key_points", []),
                "quiz": lesson.get("quiz", [])
            }
        return None

    def complete_lesson(self, lesson_id: str, quiz_score: Optional[float] = None):
        """Mark lesson as completed"""
        progress = LessonProgress(
            lesson_id=lesson_id,
            status=LessonStatus.COMPLETED.value,
            completed_at=datetime.now().isoformat(),
            quiz_score=quiz_score
        )

        self.state.lessons_progress[lesson_id] = asdict(progress)
        self.state.total_lessons_completed += 1

        # Advance to next lesson
        chapter = self.curriculum.get(self.state.current_chapter)
        if chapter and self.state.current_lesson < len(chapter["lessons"]):
            self.state.current_lesson += 1
        else:
            # Move to next chapter
            self.state.current_chapter += 1
            self.state.current_lesson = 1

        self._save_state()
        print(f"✅ Lesson {lesson_id} completed! (Score: {quiz_score:.0%})" if quiz_score else f"✅ Lesson {lesson_id} completed!")

    def take_quiz(self, lesson_id: str, answers: List[int]) -> float:
        """Grade quiz answers"""
        current = self.get_current_lesson()
        if not current or current["lesson_id"] != lesson_id:
            return 0.0

        quiz = current.get("quiz", [])
        if not quiz:
            return 1.0  # No quiz = auto pass

        correct = sum(1 for q, a in zip(quiz, answers) if q["correct"] == a)
        score = correct / len(quiz)

        return score

    def check_live_trading_ready(self) -> Dict[str, Any]:
        """Check if user is ready for live trading"""
        requirements = {
            "lessons_completed": self.state.total_lessons_completed >= 20,  # At least first 5 chapters
            "paper_trades": self.state.paper_trades_completed >= 10,
            "paper_win_rate": self.state.paper_trade_win_rate >= 0.40,  # 40%+ win rate
            "all_chapters_done": self.state.current_chapter > 8
        }

        ready = all(requirements.values())
        self.state.ready_for_live_trading = ready
        self._save_state()

        return {
            "ready": ready,
            "requirements": requirements,
            "lessons": f"{self.state.total_lessons_completed}/20",
            "paper_trades": f"{self.state.paper_trades_completed}/10",
            "win_rate": f"{self.state.paper_trade_win_rate:.1%}/40%"
        }

    def log_paper_trade(self, trade_result: Dict[str, Any]):
        """Log paper trade result and update stats"""
        self.state.paper_trades_completed += 1

        # Recalculate win rate
        # (This would need to track individual trade results in real implementation)
        if trade_result.get("profitable"):
            wins = int(self.state.paper_trade_win_rate * (self.state.paper_trades_completed - 1))
            wins += 1
            self.state.paper_trade_win_rate = wins / self.state.paper_trades_completed

        self._save_state()

    def get_progress_summary(self) -> Dict[str, Any]:
        """Get formatted progress summary"""
        readiness = self.check_live_trading_ready()
        current = self.get_current_lesson()

        return {
            "current_chapter": self.state.current_chapter,
            "current_lesson": self.state.current_lesson,
            "total_progress": f"{self.state.total_lessons_completed}/42 lessons",
            "paper_trading": {
                "trades": self.state.paper_trades_completed,
                "win_rate": f"{self.state.paper_trade_win_rate:.1%}"
            },
            "next_lesson": current["lesson_title"] if current else "All lessons complete!",
            "ready_for_live": readiness
        }

    def display_lesson(self, lesson: Dict[str, Any]):
        """Display lesson content in formatted way"""
        print("\n" + "="*70)
        print(f"📚 {lesson['chapter_title']}")
        print(f"📖 Lesson {lesson['lesson_num']}: {lesson['lesson_title']}")
        print("="*70)
        print(lesson['content'])
        print("\n" + "-"*70)
        print("🎯 KEY POINTS:")
        for point in lesson['key_points']:
            print(f"  • {point}")
        print("-"*70)


def demo():
    """Demo the mentor system"""
    mentor = MentorSystem()

    print("\n" + "="*70)
    print("📊 PROGRESS SUMMARY")
    print("="*70)
    summary = mentor.get_progress_summary()
    print(f"Current: Chapter {summary['current_chapter']}, Lesson {summary['current_lesson']}")
    print(f"Progress: {summary['total_progress']}")
    print(f"Paper Trades: {summary['paper_trading']['trades']} (Win Rate: {summary['paper_trading']['win_rate']})")
    print(f"Next: {summary['next_lesson']}")
    print("="*70)

    print("\n📖 Loading first lesson...\n")
    lesson = mentor.get_current_lesson()
    if lesson:
        mentor.display_lesson(lesson)

        if lesson.get("quiz"):
            print("\n" + "="*70)
            print("📝 QUIZ TIME!")
            print("="*70)
            for i, q in enumerate(lesson["quiz"], 1):
                print(f"\n{i}. {q['question']}")
                for j, opt in enumerate(q['options']):
                    print(f"   {j}) {opt}")

            print("\n(This is a demo - quiz would be interactive in real usage)")

    print("\n" + "="*70)
    print("🎯 READINESS CHECK")
    print("="*70)
    readiness = mentor.check_live_trading_ready()
    print(f"Live Trading Ready: {'✅ YES' if readiness['ready'] else '❌ NOT YET'}")
    print(f"\nRequirements:")
    print(f"  Lessons: {readiness['lessons']}")
    print(f"  Paper Trades: {readiness['paper_trades']}")
    print(f"  Win Rate: {readiness['win_rate']}")
    print("="*70)


if __name__ == "__main__":
    demo()
