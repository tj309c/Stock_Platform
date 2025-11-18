"""
WSB Quotes Generator for Analysis Master
Provides humorous, WSB-style quotes and commentary to add personality to the platform.
Blends professional quantitative analysis with irreverent market commentary.
"""

import random
from typing import List, Optional
from enum import Enum


class QuoteCategory(Enum):
    """Categories of quotes for different contexts."""
    GENERAL = "general"
    BULLISH = "bullish"
    BEARISH = "bearish"
    VOLATILITY = "volatility"
    EARNINGS = "earnings"
    OPTIONS = "options"
    CRYPTO = "crypto"
    RISK = "risk"
    YOLO = "yolo"
    LOSS = "loss"
    GAIN = "gain"
    HODL = "hodl"
    DIP = "dip"


class WSBQuotes:
    """
    Generates humorous WSB-style quotes and commentary.
    Maintains the balance between professional analysis and ape energy.
    """

    QUOTES = {
        QuoteCategory.GENERAL: [
            "💎🙌 Diamond hands don't fold, they HODL.",
            "This is the way. 🚀",
            "Apes together strong. 🦍",
            "We like the stock. We REALLY like the stock.",
            "I just like the stock, okay?",
            "Sir, this is a Wendy's... but also a quantitative research lab.",
            "Buy high, sell low. Wait, that's not right...",
            "Not financial advice. Just a bunch of crayons and calculations.",
            "In Elon we trust. In data we verify.",
            "The market can remain irrational longer than you can remain solvent. - Some smart guy",
        ],
        QuoteCategory.BULLISH: [
            "To the moon! 🚀🌙",
            "Stonks only go up. 📈",
            "Bulls make money, apes make history.",
            "Green candles for breakfast. 💚",
            "FOMO is real, but so is this opportunity.",
            "Buckle up, we're going parabolic.",
            "This stock has more potential than my portfolio has losses.",
            "Buy the rumor, buy the news, buy everything.",
            "Printer goes BRRRRR 💵",
            "Can't stop, won't stop, GameStop... I mean, this play.",
        ],
        QuoteCategory.BEARISH: [
            "Big oof. 📉",
            "Red is just spicy green.",
            "It's not a loss until you sell. (Copium)",
            "Alexa, play 'In the End' by Linkin Park.",
            "I tried to catch a falling knife. It was sharp.",
            "Sometimes the bear wins. Most times, actually.",
            "The dip keeps dipping. This is fine. 🔥🐶☕",
            "My portfolio is down, but my spirits are... also down.",
            "F in the chat, boys.",
            "Time to average down! (For the 47th time)",
        ],
        QuoteCategory.VOLATILITY: [
            "Volatility is opportunity... or bankruptcy. Usually both.",
            "This chart looks like my heart rate monitor.",
            "IV Crush is real, and it doesn't care about your feelings.",
            "When VIX is high, it's time to fly. Or cry.",
            "Theta gang sends their regards. ⏰💀",
            "The only constant is chaos.",
            "Buckle up, buttercup. We're in for a wild ride.",
            "My stop loss is wherever I feel like crying.",
            "Volatility smile? More like volatility SCREAM.",
            "This price action is more bipolar than my ex.",
        ],
        QuoteCategory.EARNINGS: [
            "Earnings whispers louder than my bank account.",
            "Beat expectations? Believe it or not, straight to jail.",
            "Priced in. Everything is priced in. Your breakfast was priced in.",
            "Earnings call drinking game: take a shot every time they say 'headwinds.'",
            "Miss by 1 cent? Straight to the shadow realm.",
            "Revenue beat, guidance down. Classic.",
            "The market expected expectations to be unexpected.",
            "Forward guidance is just astrology for suits.",
            "Analysts upgraded the stock to 'Still Trash' from 'Mega Trash.'",
            "Earnings surprise! (It's never a good surprise)",
        ],
        QuoteCategory.OPTIONS: [
            "0DTE options are a hell of a drug.",
            "What's an exit strategy?",
            "Theta decay is just time's way of saying 'LOL.'",
            "Greeks? I thought this was financial analysis, not mythology.",
            "Assignment is just forced diamond hands.",
            "My options are worthless, just like my degree.",
            "Buying FDs because YOLO. 🎰",
            "That's a lot of gamma for one ape.",
            "Sell the strike you want to own the stock at. Or just panic.",
            "Max pain is exactly what it sounds like.",
        ],
        QuoteCategory.CRYPTO: [
            "Not your keys, not your coins. Not your coins, not your Lambo.",
            "HODL like your WiFi depends on it.",
            "Crypto never sleeps, and neither do I (send help).",
            "When Lambo? When moon? When financial stability?",
            "Buy high, sell low, blame Elon.",
            "It's not a Ponzi scheme, it's decentralized wealth redistribution!",
            "Number go up. Ape happy.",
            "Cope, seethe, HODL, repeat.",
            "Bitcoin fixes this. (Narrator: It didn't)",
            "Few understand. (I don't understand either)",
        ],
        QuoteCategory.RISK: [
            "Risk management? Never heard of her.",
            "Diversification is for people who don't believe in themselves.",
            "YOLO is a risk management strategy, right?",
            "My risk tolerance is 'yes.'",
            "Hedge? Like, the plant?",
            "Max loss is only 100%. Max gain is infinite. I like those odds.",
            "Margin call? More like margin YOLO.",
            "Risk/Reward ratio: All/Everything",
            "Stop loss? Stops losses? Sounds fake.",
            "I'm not overleveraged, I'm efficiently capitalized.",
        ],
        QuoteCategory.YOLO: [
            "YOLO. You Only Liquidate Once.",
            "Went all in. No regrets. (Okay, some regrets)",
            "Fortune favors the bold. And occasionally, the really stupid.",
            "Life savings? More like YOLO savings.",
            "You miss 100% of the trades you don't take. You also lose 100% of the bad ones.",
            "Calculated risk. I'm just bad at math.",
            "If you're not living on the edge, you're taking up too much space.",
            "Go big or go home. I went big. Now I'm home.",
            "YOLO isn't a strategy, it's a lifestyle.",
            "All in on this play. What could go wrong? (Everything)",
        ],
        QuoteCategory.LOSS: [
            "It's just money. (It was a lot of money)",
            "I'm playing both sides, so I always come out on... bottom.",
            "Tax loss harvesting season came early this year.",
            "My portfolio is down 80%, but I'm only 60% sad.",
            "Red is my favorite color now. (Copium)",
            "Bought the top like a true professional.",
            "Losses build character. I have SO much character now.",
            "Behind every meme is a margin call.",
            "I'm not losing, I'm just winning in reverse.",
            "The IRS won't believe this one.",
        ],
        QuoteCategory.GAIN: [
            "Tendies for everyone! 🍗",
            "We're eating good tonight, boys!",
            "Profits are just unrealized losses waiting to happen.",
            "Finally, a green day. Quick, screenshot it!",
            "This is why we endure 47 red days.",
            "Gains? Is this real life?",
            "Take profits? Nah, let it ride. (Narrator: He should have taken profits)",
            "I'm up 10%! Time to leverage and lose it all!",
            "Green candles hit different. 💚📈",
            "Turned $100 into $150. Basically Warren Buffett.",
        ],
        QuoteCategory.HODL: [
            "HODL through the pain. Character building.",
            "Diamond hands are forged in fire. 💎🔥",
            "Panic sell? I don't even know her.",
            "Hold the line! (We're still holding)",
            "Selling is admitting defeat. I'd rather go to zero.",
            "Long-term investment strategy: Forget password.",
            "Buy and hold. Mostly hold. Okay, all hold.",
            "I didn't hear no bell. 🔔",
            "Holding bags like a champ. 💼",
            "The best time to plant a tree was 20 years ago. The second best time is... still holding.",
        ],
        QuoteCategory.DIP: [
            "Buy the dip! (The dip keeps dipping)",
            "Dip? More like a sale!",
            "This isn't a dip, it's a crater.",
            "Ran out of money to buy the dip. Now what?",
            "Every dip is transitory. (Copium)",
            "The dip after the dip after the dip.",
            "Dip so hard, I need a ladder to get out.",
            "Buy the dip, sell the... wait, when do we sell?",
            "I bought the dip. Turns out it was a cliff.",
            "This dip is dippier than expected.",
        ],
    }

    @staticmethod
    def get_random_quote(category: Optional[QuoteCategory] = None) -> str:
        """
        Get a random quote, optionally filtered by category.

        Args:
            category: Optional QuoteCategory to filter quotes

        Returns:
            str: A random quote
        """
        if category and category in WSBQuotes.QUOTES:
            quotes = WSBQuotes.QUOTES[category]
        else:
            # Get all quotes from all categories
            quotes = [quote for category_quotes in WSBQuotes.QUOTES.values() for quote in category_quotes]

        return random.choice(quotes)

    @staticmethod
    def get_contextual_quote(
        price_change: Optional[float] = None,
        volatility: Optional[float] = None,
    ) -> str:
        """
        Get a contextually appropriate quote based on market conditions.

        Args:
            price_change: Percentage price change
            volatility: Volatility metric

        Returns:
            str: A contextually relevant quote
        """
        # Determine category based on context
        if price_change is not None:
            if price_change > 5:
                return WSBQuotes.get_random_quote(QuoteCategory.BULLISH)
            elif price_change < -5:
                return WSBQuotes.get_random_quote(QuoteCategory.BEARISH)
            elif price_change > 0:
                return WSBQuotes.get_random_quote(QuoteCategory.GAIN)
            else:
                return WSBQuotes.get_random_quote(QuoteCategory.LOSS)

        if volatility is not None and volatility > 30:
            return WSBQuotes.get_random_quote(QuoteCategory.VOLATILITY)

        # Default to general quote
        return WSBQuotes.get_random_quote(QuoteCategory.GENERAL)

    @staticmethod
    def get_greeting() -> str:
        """Get a random greeting for the app."""
        greetings = [
            "Welcome, fellow ape! 🦍",
            "Time to find some alpha. 📈",
            "Let's make some (informed) bets! 🎲",
            "Ready to analyze like a pro, trade like an ape? 🚀",
            "Your Bloomberg Terminal? We have one at home. 💻",
            "Crayons loaded. Calculations ready. Let's go! 🖍️",
            "Another day, another opportunity to lose... I mean WIN! 💰",
            "Prepare for takeoff! 🚀🌙",
        ]
        return random.choice(greetings)

    @staticmethod
    def get_loading_message() -> str:
        """Get a random loading message."""
        messages = [
            "Calculating rocket trajectory... 🚀",
            "Consulting the magic 8-ball... 🎱",
            "Reading tea leaves and 10-Ks...",
            "Asking the almighty algorithm...",
            "Crunching numbers (and crayons)... 🖍️",
            "Summoning the tendie gods... 🍗",
            "Loading moon coordinates... 🌙",
            "Calculating maximum pain...",
            "Diversifying into hopium...",
            "Running it through the ape AI...",
        ]
        return random.choice(messages)


# Convenience function
def get_random_quote(category: Optional[QuoteCategory] = None) -> str:
    """Shortcut to get a random quote."""
    return WSBQuotes.get_random_quote(category)
