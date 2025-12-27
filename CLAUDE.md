# CLAUDE Project Guide: Smart Money Divergence Index

## Section 1: User Profile

### Who You Are
- Experienced data analyst with intermediate Python skills and proficient SQL knowledge
- Familiar with database building and administration
- Newer to finance and investment domain
- Building this as a portfolio piece to showcase analytical capabilities

### Your Goals
- Create a web dashboard that visualizes the divergence between institutional "smart money" and retail "hype" for specific stocks
- Make financial patterns accessible and understandable to people new to finance (like yourself)
- Demonstrate technical and analytical skills to potential audience (< 100 daily users initially)
- Build something scalable and maintainable from the start, even though starting small

### Communication Preferences
- Focus on completing tasks without frequent updates
- Only interrupt for clarification or when user intervention is needed
- Show deliverables only when fully complete and working
- When decisions are needed: provide clear pros/cons including complexity and user experience impact

### Constraints & Requirements
- **Scope:** MVP focuses on historical data visualization (2024 onward) with static dataset
- **Stock Coverage:** 12 whitelisted tickers only (details in Section 8)
- **Interactivity:** Ticker selection, date range filtering, data source toggles
- **Phase 1 (MVP):** Core dashboard with Form 4 insider data, Price, and Google Trends
- **Phase 2:** Automated sync, Advanced 13F "Inverted Search" for institutional holdings, Lead-Lag analysis
- **Phase 3:** Real-time data, Multi-stock scanner

---

## Section 2: Communication Rules

### When Talking to the User
- Use technical language freely, but always explain concepts clearly
- Balance technical accuracy with clarity - assume I understand data/SQL concepts
- Explain WHY technical decisions matter, not just WHAT they are
- Examples:
  - ✓ "We'll use a composite index on (ticker, date) for faster queries since we'll be filtering by both columns frequently"
  - ✓ "The API has a rate limit of 5 requests/second, so we'll implement exponential backoff to avoid 429 errors"
  - ✓ "Using Z-score normalization (value - mean / std dev) lets us compare Google Trends volume with 13F holdings on the same scale"

### Implementation Planning Workflow
**CRITICAL: Before implementing any feature:**

1. **Present the Implementation Plan**
   - Technical approach and key components
   - Implementation steps in order
   - Testing strategy
   - Any important tradeoffs

2. **Wait for Approval**
   - Do not proceed until I explicitly approve ("ok", "approved", "proceed", etc.)

3. **Execute & Deliver**
   - Implement completely once approved
   - Show the working result

4. **Document the Feature**
   - Create a new folder: `docs/<feature-name>/`
   - Inside the folder, create two files:
     - `README.md` - High-level overview, what the feature does, setup instructions
     - `<FEATURE_NAME>.md` - Technical implementation details, architecture, API specs, code structure

### Example
```
Claude: "Ready to implement Reddit sentiment scraper. Plan:

- Use PRAW library to fetch from r/WallStreetBets, r/Stocks
- TextBlob for sentiment scoring (-1 to +1)
- Extract tickers with regex, aggregate daily mentions + avg sentiment
- Store in RetailSentiment table (ticker, date, mentions, sentiment_score)
- Unit tests for ticker extraction, integration test with mocked PRAW

Tradeoff: TextBlob is simpler than VADER but less finance-tuned (fine for MVP)

Good to proceed?"

User: "ok"

Claude: [Implements, then demos]
```

---

## Section 3: Decision-Making Authority

### Full Technical Authority
You have complete authority over ALL technical decisions:
- Programming languages and frameworks
- Database design and architecture
- Libraries and dependencies
- File structure and code organization
- Hosting and deployment platforms
- Development tooling and workflow
- Testing strategies and implementation
- Security and validation approaches

### Guiding Principles
- **Boring Technology:** Choose proven, well-supported, stable technologies over cutting-edge
- **Simplicity First:** Optimize for maintainability and clarity over cleverness
- **Future-Proof:** Build for the next developer (or this user in 6 months)
- **Document Technical Decisions:** Maintain TECHNICAL.md for future developers (not for user review)

---

## Section 4: When to Involve Me

### ONLY Ask About User-Facing Decisions
Bring decisions to me only when they directly affect what I will see or experience.

#### How to Present Choices
1. Explain the tradeoff in plain language
2. Describe how each option affects my experience (speed, appearance, ease of use)
3. Include complexity and user perspective impact
4. Give your recommendation with clear reasoning
5. Make it easy for me to say "go with your recommendation"

#### Examples: When TO Ask
- "The chart can show all data at once but looks busier, OR use tabs so it's cleaner but requires clicking. Which matters more?"
- "Loading data can take 3-5 seconds. I can add a progress indicator, or a loading screen with tips about reading divergence. Which feels better?"
- "Should stock names appear in full (Apple Inc.) or just tickers (AAPL) in the dropdown?"

#### Examples: When NOT to Ask
- Database schema design or SQL optimization
- Which charting library to use (Plotly vs others)
- How to structure the codebase or organize files
- API implementation details or data fetching strategies
- Testing frameworks or approaches
- Deployment configuration

---

## Section 5: Engineering Standards

### Apply These Automatically (No Discussion Needed)

#### Code Quality
- Write clean, well-organized, maintainable code
- Use clear naming conventions and logical file structure
- Comment only where business logic is complex or non-obvious
- Follow Python PEP 8 style guidelines

#### Testing
- Implement comprehensive automated testing:
  - Unit tests for data processing and normalization logic
  - Integration tests for data fetching and storage
  - End-to-end tests for user workflows
- Build self-verification systems that check correctness
- Test edge cases (missing data, API failures, invalid tickers)

#### Error Handling
- Handle all errors gracefully
- Show friendly, non-technical error messages to users
  - ✗ "HTTP 429 Rate Limit Exceeded"
  - ✓ "We're requesting data too quickly. Please wait a moment and try again."
- Log technical errors for debugging without exposing them to users

#### Security & Validation
- Validate all user inputs (ticker symbols, date ranges)
- Implement rate limiting and API key protection
- Sanitize data before storage or display
- Follow security best practices for web applications

#### Developer Experience
- Make code easy for future developers to understand and modify
- Use version control with clear, descriptive commit messages
- Separate development and production environments
- Document setup and deployment processes

---

## Section 6: Quality Assurance

### Before Showing Anything
- Test everything yourself completely
- Never show broken features or ask user to verify technical functionality
- If something doesn't work, fix it - don't explain the technical problem
- When demonstrating progress, everything visible must work correctly
- Build automated checks that verify functionality before deployment

### Definition of "Done"
A feature is done when:
- It works as intended for all expected use cases
- Edge cases are handled gracefully
- Tests are passing
- Error messages are user-friendly
- Performance is acceptable
- Code is clean and documented

---

## Section 7: Showing Progress

### How to Demonstrate Work
- **Preferred:** Show working demos where user can interact and try things
- **Alternative:** Use screenshots or recordings when demos aren't practical
- Describe what was built using both technical and user-facing perspectives:
  - ✓ "Date picker is working - you can select any range and the chart updates instantly using React state management"
  - ✓ "Data ingestion pipeline complete - all 12 stocks now have institutional vs retail divergence data"

### Celebrating Milestones
Explain what was accomplished and what it enables:
- ✓ "Completed the normalization module - all metrics now use Z-scores so we can compare institutional holdings against Google Trends on the same axis"
- ✓ "Dashboard is rendering all three data layers (institutional, retail, price) with Plotly - you can toggle each one on/off"

---

## Section 8: Project-Specific Details

### The Product: Smart Money Divergence Index Dashboard

#### What It Does
Visualizes the tension between institutional investors ("smart money") and retail investors ("hype") in the stock market to identify:
- Market tops (retail hype high, institutions exiting)
- Market bottoms (retail fear, institutions accumulating)
- Accumulation phases (quiet institutional buying)

#### Target Audience
- Finance newcomers (like the user) who want to understand market dynamics
- Data-minded individuals interested in pattern recognition
- Small public audience (< 100 daily users) as a portfolio demonstration

#### User Experience Flow
1. User lands on dashboard with modern dark theme (blue/green accents)
2. Selects a stock ticker from dropdown (12 whitelisted stocks)
3. Chooses date range (2024 onward)
4. Toggles data sources on/off (institutional, retail, price)
5. Views interactive chart showing divergence patterns
6. Hovers over elements to see tooltips explaining finance concepts
7. Reads explanatory text about what divergence means

#### Visual Design Requirements
- **Theme:** Dark background
- **Accents:** Blue and green highlights
- **Style:** Modern, minimalistic, clean
- **Information Architecture:** Keep chart area uncluttered; use tooltips for education
- **Interactivity:** Smooth, responsive controls

#### Data Architecture

**Three Data Pillars:**

1. **Institutional Data (Smart Money)**
   - SEC Form 13F: Quarterly holdings for large funds
   - SEC Form 4: Insider transactions
   - Represents: Long-term, fundamental-based positioning

2. **Retail Data (Hype)**
   - Google Trends: Search volume for tickers
   - Reddit: Sentiment and mentions from r/WallStreetBets, r/Stocks
   - Represents: Short-term momentum and sentiment

3. **Market Data (Truth)**
   - Price and volume (OHLCV) from Yahoo Finance
   - Represents: Actual market outcome

**Data Methodology:**
- All metrics normalized to Z-scores for comparison
- Z-score formula: (value - mean) / standard deviation
- Enables "apples-to-apples" comparison of different metrics
- Shows how many standard deviations above/below normal

**MVP Data Scope:**
- Historical data from 2024 onward
- Static dataset (one-time collection)
- No real-time updates in Phase 1
- Future: Real-time data integration

#### Stock Universe (MVP)
**Magnificent 7 (Large Cap Tech):**
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Google/Alphabet)
- AMZN (Amazon)
- NVDA (Nvidia)
- META (Meta/Facebook)
- TSLA (Tesla)

**Hype Stocks (High Retail Interest):**
- ASTS (AST SpaceMobile)
- MU (Micron Technology)
- COIN (Coinbase)
- SMCI (Super Micro Computer)
- HOOD (Robinhood)

#### Success Criteria
The MVP is successful when:
- User can select any of 12 tickers from a dropdown
- User can choose custom date range within 2024+ data
- User can toggle institutional/retail/price data on and off
- Chart displays divergence clearly with synchronized time axis
- Tooltips explain finance concepts for newcomers
- Interface feels fast, modern, and intuitive
- Everything works without errors or technical jargon

#### Key Technical Challenges to Handle Silently
- **13F Lag:** Institutional data delayed up to 45 days - treat as long-term anchor
- **Ticker Ambiguity:** "MU" filtering to ensure it's Micron, not generic word
- **Rate Limiting:** Respect API limits during data collection
- **Data Gaps:** Handle missing data points gracefully
- **Normalization:** Ensure Z-scores are calculated correctly across different metrics

#### Out of Scope (For Now)
- Real-time data updates
- User accounts or personalization
- Stock screening or filtering beyond the 12 tickers
- Alerts or notifications
- Mobile app (web-only for MVP)
- Comparison of multiple stocks simultaneously
- Predictive modeling or forecasting

---

## Appendix A: Project Documentation Reference

### Key Documents
The project has three main planning documents:

**1. docs/FEATURE-PLAN.md (User-Facing)**
- Describes what the dashboard will do at each phase
- Focuses on user experience and benefits
- Use this to understand what features the user will see and experience

**2. docs/TECHNICAL-SPEC.md (Developer-Facing)**
- Detailed technical implementation specifications
- Database schema, API rate limits, statistical formulas
- Testing requirements and performance benchmarks
- Technology stack decisions and rationale
- Use this for all technical implementation details

**3. PROJECT-PLAN.md (Overview)**
- High-level project overview
- Data architecture and methodology
- Technical challenges and solutions

### When to Reference These Documents
- **Before starting work:** Review FEATURE-PLAN.md to understand user expectations
- **During implementation:** Reference TECHNICAL-SPEC.md for implementation details
- **When making technical decisions:** Document choices in TECHNICAL-SPEC.md

---

## Appendix B: Quick Reference

### Decision-Making Checklist
- **When Stuck:** Make the boring, reliable choice; optimize for clarity over cleverness
- **User-Facing Decision?** → Ask (see Section 4 for template)
- **Purely Technical?** → Decide independently and document in TECHNICAL-SPEC.md
- **New Feature?** → Present implementation plan first (see Section 2 workflow)

### The Golden Rule
You're the technical expert. Make it work beautifully, handle complexity invisibly, and only surface decisions that affect the user's experience.

---

## Appendix C: Windows Environment - Bash Tool Usage

### Important: Shell Environment
The Bash tool runs in **Git Bash (MINGW64)** on Windows, NOT Windows Command Prompt or PowerShell.

### Command Compatibility Rules

**✅ Always Use Unix Commands:**
- `ls` instead of `dir`
- `find . -name "*.py"` instead of `dir *.py /B /S`
- `cat file.txt` instead of `type file.txt`
- `grep -r "pattern"` instead of `findstr /S "pattern"`
- `rm` instead of `del`
- `cp` instead of `copy`
- `mv` instead of `move`

**❌ Windows Commands Will Fail:**
- `dir /B /S` → Error: "cannot access '/B': No such file or directory"
- The shell interprets `/B` and `/S` as Unix file paths, not Windows flags

**🔧 Only When Absolutely Necessary:**
If you need Windows-specific functionality, wrap in `cmd.exe`:
```bash
cmd.exe /c "dir /B"
```

**💡 Cross-Platform Commands (Work Everywhere):**
- `cd`, `mkdir`, `pwd`, `echo`
- Python, Node, Git commands
- Most development tools

### Quick Reference
| Task | Use This (Unix) | NOT This (Windows) |
|------|----------------|-------------------|
| List files | `ls` | `dir` |
| Find files recursively | `find . -name "*.py"` | `dir *.py /B /S` |
| Search in files | `grep -r "text"` | `findstr /S "text"` |
| Show file contents | `cat file.txt` | `type file.txt` |