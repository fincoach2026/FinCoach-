"""
FinCoach — Financial Literacy Course data.

COURSE_UNITS: the full 20-unit curriculum outline (titles + lesson lists),
used to build the sidebar navigation for every unit.

UNIT_CONTENT: fully written article/flashcard/quiz content, keyed by unit
number. Only Unit 1 is fully written out right now (per the source material
provided). Any unit without an entry here will render with a friendly
"content coming soon" placeholder in the UI, so the whole course is
browsable today and easy to fill in unit-by-unit later.
"""

# ---------------------------------------------------------------------------
# Full 20-unit outline (titles + lesson titles only)
# ---------------------------------------------------------------------------
COURSE_UNITS = [
    {"num": 1, "title": "Money Mindset & Financial Foundations", "lessons": [
        "1.1 Needs vs. Wants vs. Values",
        "1.2 Opportunity Cost & Trade-Offs",
        "1.3 Setting Financial Goals (Short/Medium/Long-Term)",
        "1.4 Why Financial Literacy Is a Lifelong Skill",
    ]},
    {"num": 2, "title": "Budgeting & Cash Flow Management", "lessons": [
        "2.1 Understanding Income vs. Expenses",
        "2.2 The 50/30/20 Rule and Alternative Frameworks",
        "2.3 Budgeting for Variable/Gig Income",
        "2.4 Budgeting Tools (Apps, Spreadsheets, Envelope Method)",
        "2.5 Adjusting a Budget for Life Changes",
    ]},
    {"num": 3, "title": "Banking & Financial Institutions", "lessons": [
        "3.1 Checking vs. Savings Accounts",
        "3.2 Banks vs. Credit Unions vs. Online Banks",
        "3.3 Understanding Fees & Fine Print",
        "3.4 Managing Multiple Accounts (Joint, Business, Personal)",
    ]},
    {"num": 4, "title": "Saving Strategies & Emergency Funds", "lessons": [
        "4.1 Why Emergency Funds Matter",
        "4.2 How Much to Save & Where to Keep It",
        "4.3 Sinking Funds for Planned Expenses",
        "4.4 Saving for Major Life Goals",
    ]},
    {"num": 5, "title": "Understanding & Building Credit", "lessons": [
        "5.1 What Is a Credit Score and How It's Calculated",
        "5.2 Reading a Credit Report",
        "5.3 Building Credit From Zero",
        "5.4 How Credit Impacts Life Decisions (Renting, Loans, Employment)",
    ]},
    {"num": 6, "title": "Debt Management", "lessons": [
        "6.1 Types of Debt: Good vs. Bad",
        "6.2 How Interest and APR Work",
        "6.3 Repayment Strategies (Snowball vs. Avalanche)",
        "6.4 When to Seek Help (Consolidation, Counseling)",
    ]},
    {"num": 7, "title": "Student Loans & Financing Education", "lessons": [
        "7.1 Federal vs. Private Loans",
        "7.2 How Interest Accrues During School",
        "7.3 Repayment Plans & Forgiveness Programs",
        "7.4 Evaluating ROI on Education",
    ]},
    {"num": 8, "title": "Taxes Across a Lifetime", "lessons": [
        "8.1 Why We Pay Taxes & How They're Used",
        "8.2 Understanding W-2s, W-4s, and Pay Stubs",
        "8.3 Filing a Basic Tax Return",
        "8.4 Taxes and Major Life Events (Marriage, Home, Self-Employment)",
        "8.5 Taxes in Retirement",
    ]},
    {"num": 9, "title": "Earning, Careers & Income Growth", "lessons": [
        "9.1 Wages vs. Salary vs. Benefits Packages",
        "9.2 Negotiating Pay & Evaluating Job Offers",
        "9.3 Side Income & Entrepreneurship",
        "9.4 Long-Term Income Growth Strategy",
    ]},
    {"num": 10, "title": "Investing Fundamentals", "lessons": [
        "10.1 Saving vs. Investing: Why It Matters",
        "10.2 Stocks, Bonds, Mutual Funds & ETFs",
        "10.3 Risk Tolerance & Diversification",
        "10.4 Compound Growth Over Time",
        "10.5 Getting Started with a Brokerage Account",
    ]},
    {"num": 11, "title": "Retirement Planning", "lessons": [
        "11.1 401(k)s and Employer Matching",
        "11.2 IRAs: Roth vs. Traditional",
        "11.3 Social Security & Pensions",
        "11.4 Adjusting Retirement Strategy by Life Stage",
    ]},
    {"num": 12, "title": "Insurance & Risk Management", "lessons": [
        "12.1 Why Insurance Exists (Risk Pooling)",
        "12.2 Health Insurance Basics",
        "12.3 Auto & Renters/Homeowners Insurance",
        "12.4 Life & Disability Insurance",
        "12.5 Choosing Coverage by Life Stage",
    ]},
    {"num": 13, "title": "Major Purchases & Big Financial Decisions", "lessons": [
        "13.1 Buying vs. Leasing a Car",
        "13.2 Understanding Contracts & Fine Print",
        "13.3 Negotiation Skills for Big Purchases",
        "13.4 Avoiding Buyer's Remorse & High-Pressure Sales",
    ]},
    {"num": 14, "title": "Homeownership & Real Estate", "lessons": [
        "14.1 Renting vs. Buying: The Real Math",
        "14.2 Mortgages: Types & How They Work",
        "14.3 Down Payments & Closing Costs",
        "14.4 Home Equity & Property Taxes",
        "14.5 Real Estate as an Investment",
    ]},
    {"num": 15, "title": "Marriage, Family & Household Finances", "lessons": [
        "15.1 Merging Finances: Joint vs. Separate Accounts",
        "15.2 Communicating About Money in Relationships",
        "15.3 Raising Financially Literate Kids",
        "15.4 Planning for Childcare & Family Costs",
    ]},
    {"num": 16, "title": "Small Business & Entrepreneurship Basics", "lessons": [
        "16.1 Business vs. Personal Finances",
        "16.2 Basic Bookkeeping & Record-Keeping",
        "16.3 Business Loans & Funding Options",
        "16.4 Tax Implications of Self-Employment",
    ]},
    {"num": 17, "title": "Estate Planning & Generational Wealth", "lessons": [
        "17.1 Wills & Beneficiaries",
        "17.2 Power of Attorney & Healthcare Directives",
        "17.3 Passing On Wealth Across Generations",
    ]},
    {"num": 18, "title": "Identity Protection & Financial Fraud", "lessons": [
        "18.1 Common Scams Targeting Young People",
        "18.2 Cybersecurity for Personal Finances",
        "18.3 Recognizing Phishing & Social Engineering",
        "18.4 What to Do If You're a Victim",
    ]},
    {"num": 19, "title": "Navigating Financial Setbacks", "lessons": [
        "19.1 Job Loss & Income Disruption",
        "19.2 Medical Debt & Unexpected Expenses",
        "19.3 Divorce & Financial Separation",
        "19.4 Understanding Bankruptcy as a Last Resort",
    ]},
    {"num": 20, "title": "Capstone — Building a Lifelong Financial Plan", "lessons": [
        "20.1 Synthesizing Your Financial Identity",
        "20.2 Building a Personal Financial Roadmap",
        "20.3 Presenting & Defending Your Plan",
    ]},
]

# ---------------------------------------------------------------------------
# Fully written content — Unit 1 only for now.
# Structure per lesson:
#   article: {part1_title, part1_body, part2_title, part2_body}
#   flashcards: list of {front, back}
#   quiz: list of {question, options, answer_index, explanation}
# ---------------------------------------------------------------------------
UNIT_CONTENT = {
    1: {
        "1.1 Needs vs. Wants vs. Values": {
            "article": {
                "part1_title": "What's the Difference, Really?",
                "part1_body": (
                    "Every dollar you spend is a decision. But most people never stop to ask "
                    "*why* they're spending it. That's where needs, wants, and values come in "
                    "— three simple ideas that quietly control almost every financial choice "
                    "you'll ever make.\n\n"
                    "**Needs** are the things you must have to live and function. Food, shelter, "
                    "basic clothing, transportation to work or school, and healthcare fall into "
                    "this category. If you cut a need out of your life, something breaks — your "
                    "health, your job, your housing.\n\n"
                    "**Wants** are things that make life more enjoyable but aren't required for "
                    "survival or basic functioning. A streaming subscription, a fancier phone "
                    "than you need, eating out instead of cooking — these are wants. There's "
                    "nothing wrong with wants. The problem only shows up when wants start "
                    "crowding out needs, or when you spend on autopilot without noticing.\n\n"
                    "**Values** are different from both. Values are what actually matter to you "
                    "— the things you'd protect even if money got tight. Maybe you value "
                    "education, family time, adventure, security, or helping others. Values "
                    "don't show up as a single line on a receipt. Instead, they shape *which* "
                    "needs and wants you prioritize.\n\n"
                    "Here's the twist: two people can have the exact same income and the exact "
                    "same list of needs and wants, but spend completely differently — because "
                    "their values are different. Someone who values travel might live in a "
                    "cheap apartment and skip new clothes to save for flights. Someone who "
                    "values comfort and home life might do the opposite. Neither is wrong. "
                    "What's wrong is spending money in a way that doesn't match what you "
                    "actually care about.\n\n"
                    "A lot of financial stress doesn't come from not having enough money. It "
                    "comes from spending money in ways that don't line up with your values. You "
                    "buy something, and it doesn't actually make you happier — because deep "
                    "down, it wasn't something you valued in the first place. It was just "
                    "something in front of you."
                ),
                "part2_title": "Turning Awareness Into a Habit",
                "part2_body": (
                    "Knowing the difference between needs, wants, and values is step one. Step "
                    "two is actually using that knowledge before you spend.\n\n"
                    "Here's a simple filter to run purchases through:\n\n"
                    "1. **Is this a need?** If yes, the real question isn't \"should I buy "
                    "this\" but \"how much should I spend on it.\"\n"
                    "2. **Is this a want?** If yes, ask whether it fits your budget *and* "
                    "whether it lines up with something you value.\n"
                    "3. **Does this purchase reflect a value, or just a mood?** Buying "
                    "something because you're bored, stressed, or trying to impress someone is "
                    "a mood purchase. Buying something because it genuinely supports what "
                    "matters to you is a values purchase.\n\n"
                    "This doesn't mean you need to interrogate every $4 coffee. The goal isn't "
                    "perfection — it's awareness. Most people who feel \"bad with money\" don't "
                    "actually lack financial knowledge. They lack a clear sense of what they "
                    "value, so their spending has no compass.\n\n"
                    "One useful exercise: imagine your money as a vote. Every purchase is a "
                    "vote for the kind of life you're building. If you say you value your "
                    "future but spend every free dollar on things that don't move you toward "
                    "it, there's a mismatch worth noticing — not to feel guilty about, but to "
                    "adjust.\n\n"
                    "As you build your financial life, needs will always come first, wants "
                    "will always exist and that's fine, but values are what should guide the "
                    "choices in between. When your spending starts to reflect your values "
                    "instead of just your impulses, budgeting stops feeling like restriction "
                    "and starts feeling like direction."
                ),
            },
            "flashcards": [
                {"front": "Need", "back": "Something required to live and function — food, shelter, basic clothing, transportation to work/school, healthcare."},
                {"front": "Want", "back": "Something that makes life more enjoyable but isn't required for survival or basic functioning."},
                {"front": "Value", "back": "What actually matters to you — the things you'd protect even if money got tight. Shapes which needs/wants you prioritize."},
                {"front": "Mood purchase", "back": "Buying something because you're bored, stressed, or trying to impress someone — not because it reflects what you value."},
                {"front": "The 3-question filter", "back": "1) Is this a need? 2) Is this a want that fits budget + values? 3) Is this a value purchase or a mood purchase?"},
            ],
            "quiz": [
                {
                    "question": "Which of these is best described as a 'want' rather than a 'need'?",
                    "options": ["Rent for your apartment", "A streaming subscription", "Groceries", "Bus fare to work"],
                    "answer_index": 1,
                    "explanation": "A streaming subscription makes life more enjoyable but isn't required for survival or basic functioning — that's the definition of a want.",
                },
                {
                    "question": "What role do 'values' play in spending, according to the lesson?",
                    "options": [
                        "They replace needs and wants entirely",
                        "They shape which needs and wants you prioritize",
                        "They only matter for long-term goals",
                        "They show up as a specific line item on receipts",
                    ],
                    "answer_index": 1,
                    "explanation": "Values don't appear as a single line on a receipt — they shape which needs and wants you choose to prioritize.",
                },
                {
                    "question": "A lot of financial stress comes from...",
                    "options": [
                        "Always having too little income",
                        "Spending in ways that don't match your values",
                        "Having too many needs",
                        "Saving too aggressively",
                    ],
                    "answer_index": 1,
                    "explanation": "The lesson states financial stress often comes from spending that doesn't line up with your values, not just from low income.",
                },
            ],
            "video_urls": ["https://youtu.be/QyuU4wFIz3o"],
        },
        "1.2 Opportunity Cost & Trade-Offs": {
            "article": {
                "part1_title": "The Cost of \"Yes\" Is Always Another \"No\"",
                "part1_body": (
                    "Opportunity cost is one of the most useful ideas in all of personal "
                    "finance, and it's simple: **every choice you make means giving up "
                    "something else you could have chosen instead.**\n\n"
                    "Money is limited. Time is limited. So every time you say \"yes\" to "
                    "spending on one thing, you're automatically saying \"no\" to whatever "
                    "else that money could have done. That \"no\" — the thing you gave up — "
                    "is the opportunity cost.\n\n"
                    "Say you have $60. You could spend it on a pair of shoes, put it toward a "
                    "car repair fund, or save it toward a trip next year. If you buy the "
                    "shoes, the opportunity cost isn't just \"$60 gone.\" It's specifically the "
                    "car repair fund staying $60 short, or the trip savings not growing. "
                    "That's the real cost of the decision — not the price tag, but what you "
                    "didn't get to do instead.\n\n"
                    "This applies far beyond shopping. Choosing to work a part-time job "
                    "instead of studying has an opportunity cost (a lower grade, maybe). "
                    "Choosing to sleep in instead of exercising has one too (your health goals "
                    "move slower). Opportunity cost isn't just about money — but in personal "
                    "finance, it's one of the clearest ways to see the true price of a "
                    "decision.\n\n"
                    "The tricky part is that opportunity cost is invisible. You don't get a "
                    "receipt for the things you didn't buy or the goals you didn't fund. "
                    "That's exactly why it's so easy to ignore — and exactly why it's worth "
                    "training yourself to think about."
                ),
                "part2_title": "Making Trade-Offs on Purpose",
                "part2_body": (
                    "Once you understand opportunity cost, you can start making trade-offs "
                    "*on purpose* instead of by accident.\n\n"
                    "Here's a practical way to think it through before a purchase:\n\n"
                    "- **Name the alternative.** Before buying something, ask: \"If I don't "
                    "spend this here, what's the next most useful thing I could do with it?\"\n"
                    "- **Compare the value, not just the price.** A $50 purchase and a $50 "
                    "contribution to an emergency fund cost the same amount, but they're not "
                    "equal in value.\n"
                    "- **Watch for small trade-offs that add up.** Spending $15 a week on "
                    "takeout instead of cooking adds up to over $700 a year.\n\n"
                    "It's also worth saying: opportunity cost doesn't mean you should never "
                    "spend on wants. Enjoying your money is part of a healthy financial life. "
                    "The goal isn't to eliminate trade-offs — that's impossible. The goal is "
                    "to make them consciously, so your money moves toward what you actually "
                    "care about instead of disappearing into decisions you didn't really "
                    "think about.\n\n"
                    "Every budget, every goal, and every big financial decision you'll ever "
                    "make comes down to trade-offs. Learning to see them clearly — instead of "
                    "pretending they don't exist — is one of the most valuable financial "
                    "habits you can build."
                ),
            },
            "flashcards": [
                {"front": "Opportunity cost", "back": "The value of the next best alternative you give up when you make a choice."},
                {"front": "Why is opportunity cost 'invisible'?", "back": "You don't get a receipt for the things you didn't buy or the goals you didn't fund — so it's easy to ignore."},
                {"front": "\"Name the alternative\"", "back": "Before buying something, ask what the next most useful thing you could do with that money would be."},
                {"front": "Small trade-offs add up", "back": "E.g. $15/week on takeout instead of cooking adds up to over $700/year."},
            ],
            "quiz": [
                {
                    "question": "What is opportunity cost?",
                    "options": [
                        "The total price of a purchase",
                        "The value of the next best alternative you gave up",
                        "The interest charged on a loan",
                        "The tax paid on a purchase",
                    ],
                    "answer_index": 1,
                    "explanation": "Opportunity cost is specifically what you gave up by choosing one option over the next best alternative.",
                },
                {
                    "question": "Why is opportunity cost easy to ignore?",
                    "options": [
                        "It's usually zero",
                        "It's invisible — there's no receipt for what you didn't buy",
                        "It only applies to large purchases",
                        "Banks track it automatically",
                    ],
                    "answer_index": 1,
                    "explanation": "The lesson emphasizes that opportunity cost is invisible, which makes it easy to overlook.",
                },
            ],
            "video_urls": ["https://www.youtube.com/watch?v=pkEiHZAtoro"],
        },
        "1.3 Setting Financial Goals (Short/Medium/Long-Term)": {
            "article": {
                "part1_title": "Why Vague Goals Don't Work",
                "part1_body": (
                    "\"I want to save money\" is not a financial goal. It's a wish. Wishes "
                    "don't get funded — goals do. The difference is specificity, a timeline, "
                    "and a plan.\n\n"
                    "A real financial goal answers three questions: **What** exactly am I "
                    "saving or working toward? **How much** will it cost? **By when** do I "
                    "want it done?\n\n"
                    "Financial goals generally fall into three timeframes, and each one works "
                    "differently:\n\n"
                    "**Short-term goals** (within about a year) — a small emergency cushion, "
                    "a concert, paying off a small debt. These usually live in a regular "
                    "savings account.\n\n"
                    "**Medium-term goals** (roughly 1–5 years) — a car, a study abroad trip, "
                    "a security deposit. These need more planning and often a dedicated "
                    "savings account.\n\n"
                    "**Long-term goals** (5+ years) — retirement, buying a home, building "
                    "long-term wealth. These benefit from time itself — money invested over "
                    "decades can grow significantly through compounding.\n\n"
                    "Different timeframes call for different strategies. Treating a 20-year "
                    "goal like a 1-month goal (or vice versa) usually leads to either too "
                    "much risk or too little growth."
                ),
                "part2_title": "Building a Goal You'll Actually Follow",
                "part2_body": (
                    "Having a goal is one thing. Sticking to it is another.\n\n"
                    "**Make it specific and measurable.** \"Save $1,200 for a car down "
                    "payment in 12 months\" breaks down into $100/month — a number you can "
                    "check yourself against.\n\n"
                    "**Attach a reason.** Goals without a \"why\" are easy to abandon.\n\n"
                    "**Break big goals into smaller checkpoints.** A 5-year goal can feel too "
                    "far away — break it into yearly or monthly checkpoints.\n\n"
                    "**Automate what you can.** A goal backed by an automatic transfer happens "
                    "whether you're motivated that day or not.\n\n"
                    "**Revisit and adjust.** Life changes, and goals should flex with it.\n\n"
                    "The goal ladder — one goal for a month, a year, five years, and twenty "
                    "years — forces you to think across time, not just about this week's "
                    "paycheck."
                ),
            },
            "flashcards": [
                {"front": "Short-term goal", "back": "A goal within about a year — e.g. a small emergency cushion or paying off a small debt."},
                {"front": "Medium-term goal", "back": "A goal roughly 1–5 years out — e.g. saving for a car or a security deposit."},
                {"front": "Long-term goal", "back": "A goal 5+ years out — e.g. retirement or buying a home. Benefits from compounding over time."},
                {"front": "3 questions a real goal answers", "back": "What am I saving for? How much will it cost? By when do I want it done?"},
            ],
            "quiz": [
                {
                    "question": "\"Save $1,200 for a car down payment in 12 months\" is a good goal mainly because it's:",
                    "options": ["Cheap", "Specific and measurable", "Long-term", "Automatic"],
                    "answer_index": 1,
                    "explanation": "It names an exact amount and a deadline, making it specific and measurable — unlike a vague wish.",
                },
                {
                    "question": "Which goal is best classified as long-term?",
                    "options": ["Saving for a concert next month", "Building retirement savings", "A security deposit on an apartment", "A small emergency cushion"],
                    "answer_index": 1,
                    "explanation": "Retirement is a 5+ year goal that benefits from compounding — a defining feature of long-term goals.",
                },
            ],
            "video_urls": ["https://www.youtube.com/watch?v=nzIAe8WSSqE"],
        },
        "1.4 Why Financial Literacy Is a Lifelong Skill": {
            "article": {
                "part1_title": "This Isn't a One-Time Lesson",
                "part1_body": (
                    "It's tempting to think of financial literacy like a single unit you "
                    "complete and move past. In reality, it works more like physical fitness: "
                    "it's not something you finish, it's something you maintain and keep "
                    "adapting throughout your life.\n\n"
                    "That's because your financial life doesn't stay still. At 18, your "
                    "biggest concerns might be a part-time paycheck and a first bank account. "
                    "A few years later, it might be student loans, your first full-time job, "
                    "or renting your first apartment. Later still: buying a car, maybe a "
                    "home, building credit, planning for retirement, supporting a family, "
                    "navigating taxes that get more complex every year.\n\n"
                    "Someone who learns budgeting at 18 and never revisits their financial "
                    "knowledge again will be underprepared at 30, 40, or 60 — not because "
                    "they weren't smart, but because the financial world they're operating in "
                    "has moved on without them.\n\n"
                    "This is actually good news, not bad news. It means you don't need to "
                    "master everything right now. You just need to build the habit of "
                    "continuing to learn."
                ),
                "part2_title": "Building the Habit That Outlasts the Course",
                "part2_body": (
                    "If financial literacy is lifelong, the most important thing you can take "
                    "from any single course isn't a specific fact — it's the habit of staying "
                    "financially engaged.\n\n"
                    "**Check in with your money regularly.** A monthly look at what's coming "
                    "in and going out catches problems early.\n\n"
                    "**Stay curious when your life changes.** New job, new apartment, a raise "
                    "— every change has a financial dimension worth understanding.\n\n"
                    "**Treat mistakes as data, not failure.** Financially literate people "
                    "aren't people who never make mistakes — they notice, adjust, and keep "
                    "going.\n\n"
                    "**Reassess your goals as your life shifts.** The goals that mattered at "
                    "18 won't be the same ones that matter at 28 or 45.\n\n"
                    "The real goal of this entire course isn't to teach you everything you'll "
                    "ever need — it's to make sure you know how to keep learning it."
                ),
            },
            "flashcards": [
                {"front": "Why is financial literacy 'lifelong'?", "back": "Your financial life keeps changing (new jobs, taxes, credit, family) and the financial system itself keeps changing too."},
                {"front": "Treat mistakes as...", "back": "Data, not failure — financially literate people notice, adjust, and keep going."},
                {"front": "The real goal of the course", "back": "Not to teach everything at once, but to build the habit of continuing to learn as life gets more complex."},
            ],
            "quiz": [
                {
                    "question": "The lesson compares financial literacy to:",
                    "options": ["A single exam you pass once", "Physical fitness — maintained, not finished", "A diploma you frame", "A one-time purchase"],
                    "answer_index": 1,
                    "explanation": "Like fitness, financial literacy is something you maintain and keep adapting, not something you complete once.",
                },
                {
                    "question": "According to the lesson, financially literate people are defined by:",
                    "options": ["Never making a mistake", "Noticing, adjusting, and continuing after mistakes", "Avoiding all financial risk", "Memorizing every tax rule"],
                    "answer_index": 1,
                    "explanation": "The lesson explicitly says financially literate people aren't mistake-free — they notice, adjust, and keep going.",
                },
            ],
            "video_urls": ["https://www.youtube.com/watch?v=NdLtWDeVziU"],
        },
    }
}


def get_unit_progress(unit_num: int) -> str:
    """Return whether an entry has full written content or is a placeholder."""
    return "available" if unit_num in UNIT_CONTENT else "coming_soon"
