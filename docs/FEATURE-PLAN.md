# Feature Development Plan: Smart Money Divergence Index

This document describes what you'll be able to do with the dashboard at each stage of development. For technical implementation details, developers should see TECHNICAL-SPEC.md.

---

## Phase 1: Minimum Viable Product (MVP)

**What You'll Have:**
A working dashboard where you can explore historical patterns showing when institutional investors and retail traders were moving in opposite directions for any of the 12 stocks.

**Success Criteria:**
- Select any of the 12 stocks from a dropdown menu
- Pick custom date ranges (from 2024 onward)
- Turn different data sources on and off to see what matters
- See clear charts that show when "smart money" and retail hype diverged
- Hover over terms you don't know to get simple explanations
- Everything loads quickly and works smoothly
- No confusing error messages or technical jargon

---

### 1.1 Data Collection

**What It Does:**
Gathers all the historical data needed to show divergence patterns.

**What You'll See:**
Charts populated with data from January 2024 to now, showing:
- When big institutions were buying or selling (from official SEC filings)
- When retail investors were searching for stocks (from Google Trends)
- Actual stock prices to see what really happened

**Why It Matters:**
This is the foundation - without complete data, the patterns won't be reliable.

---

### 1.2 Making Everything Comparable (Normalization) **(Status: COMPLETED)**

**What It Does:**
Converts all different types of data (dollar amounts, search volume, social media mentions) into a common scale so you can compare them directly.

**What You'll See:**
All data displayed on the same scale where:
- 0 means "normal activity"
- +2 means "twice as active as usual"
- -2 means "half as active as usual"

**Why It Matters:**
Without this, you'd be trying to compare apples to oranges. This lets you instantly see if retail hype is way up while institutional buying is way down.

---

### 1.3 Interactive Dashboard

**What You'll Experience:**

**Stock Selection:**
- Choose from 12 stocks via a dropdown showing full company name (not just ticker symbols)
- Magnificent 7: Apple, Microsoft, Google, Amazon, Nvidia, Meta, Tesla
- Hype Stocks: AST SpaceMobile, Micron, Coinbase, Super Micro Computer, Robinhood

**Date Range Selection:**
- Pick any start and end date from 2024 onward
- See patterns over weeks, months, or the full time period

**Data Toggles:**
- Checkboxes to show/hide:
  - Institutional holdings (what the big funds own)
  - Retail sentiment (search and social media activity)
  - Stock price (what actually happened)
- Mix and match to spot patterns

**Chart Display:**
- Clean, synchronized chart where all data shares the same timeline
- Dark theme with blue and green highlights (easy on the eyes)
- Zoom, pan, and hover to explore details

**Learning Tools:**
- Hover over unfamiliar terms to see plain-English explanations
- Learn concepts like "13F filing," "Z-score," and "divergence" as you explore
- No finance background needed

**Why It Matters:**
This is what you'll actually use. The interface needs to feel intuitive so you can focus on discovering patterns, not fighting with the tool.

---

### 1.4 Data Quality Checks

**What It Does:**
Automatically verifies that all collected data is accurate and complete before showing it to you.

**What You'll See:**
- Confidence that the patterns you're seeing are based on real, verified data
- No confusing gaps or obvious errors in the charts
- Assurance that "MU" means Micron Technology (not random posts with the letters "mu")

**Why It Matters:**
Bad data leads to bad insights. This ensures you can trust what you're seeing.

---

## When Phase 1 Is Complete

You'll have a fully working dashboard where you can:
- Load any of the 12 stocks and see their divergence history since 2024
- Understand when retail traders were most excited or fearful
- See when institutions were quietly accumulating or exiting
- Discover if these groups were moving together or in opposite directions
- Learn financial concepts through tooltips and explanations
- Use it on your laptop or phone without technical issues

---

## Phase 2: Automatic Updates

**What Changes:**
The dashboard stays current without you having to do anything. New data flows in automatically every week.

**Prerequisites:**
Phase 1 must be complete and working well based on your testing and feedback.

---

### 2.1 Automated Data Refresh

**What It Does:**
Background processes fetch the latest data on a regular schedule without any manual effort.

**What You'll Experience:**
- Open the dashboard and see the most recent data automatically
- Weekly updates for search trends, social media, and prices
- Quarterly updates for institutional holdings (matches when official filings are released)
- Never see stale or outdated information

**Why It Matters:**
You want to see current patterns, not historical snapshots. This keeps the dashboard relevant without you lifting a finger.

---

### 2.2 Advanced Institutional Holdings (13F Inverted Search)

**What It Does:**
Correctly tracks institutional ownership by collecting 13F filings from *major investment funds* (e.g., BlackRock, Vanguard) and searching for their holdings of our 12 stocks.

**Why This is Phase 2:**
Phase 1 currently tracks SEC Form 4 (Insider Trading) which provides strong signal. Tracking *total* institutional ownership requires processing thousands of filings from *other* companies (the funds) rather than the stocks themselves, which is a complex "inverted search" data engineering task.

**What You'll See:**
- Total % of company owned by institutions
- Top 10 institutional holders for each stock
- Changes in ownership by major funds (e.g., "Berkshire Hathaway bought more AAPL")

---

### 2.3 Pattern Analysis (Lead-Lag Correlation)

**What It Does:**
Calculates whether retail sentiment changes tend to predict price movements (or vice versa) for each stock.

**What You'll See:**
A new section on the dashboard showing:
- **Relationship Strength:** How closely retail sentiment and price track each other
- **Timing:** Does retail hype come before price changes (leading indicator) or after (lagging indicator)?
- **Confidence:** How reliable is this pattern (shown as confidence ranges)
- **Plain-Language Explanation:** What this means for understanding the stock

For example:
- "For GameStop, retail hype typically spikes 2 days before price moves (strong leading indicator)"
- "For Apple, retail searches follow price changes by 1 day (weak lagging indicator)"

**Why It Matters:**
This helps you understand if social media buzz is driving prices or just reacting to them. It's the difference between a signal and noise.

---

## When Phase 2 Is Complete

You'll have everything from Phase 1, plus:
- Always-current data without manual updates
- Insights into whether retail sentiment is a leading or lagging indicator
- Confidence in the reliability of patterns
- A self-maintaining system that just works

---

## Phase 3: Advanced Features

**Status:** NOT STARTED - These are possibilities, not commitments.

**When This Happens:**
Only after Phase 1 and 2 are working well, you've used the dashboard for a while, and you've identified specific features you actually want based on real usage.

**Note:** These ideas may change completely based on what you discover you actually need.

---

### 3.1 Real-Time Updates (Potential Future Feature)

**What It Could Do:**
Update data throughout the trading day instead of once per week.

**What You Might See:**
- Divergence patterns emerging live during market hours
- Price and sentiment refreshing every hour
- Ability to spot divergence as it's happening

**Why Consider It:**
Could let you spot opportunities as they develop rather than reviewing history. However, requires more complex infrastructure and ongoing costs.

---

### 3.2 Stock Scanner (Potential Future Feature)

**What It Could Do:**
Show all 12 stocks at once, ranked by current divergence level.

**What You Might See:**
- **Overview Page:** All stocks displayed together
- **Top Rankings:** The 3 most "overhyped" stocks (retail excited, institutions exiting)
- **Bottom Rankings:** The 3 most "under-accumulated" stocks (institutions buying, retail quiet)
- **Quick Navigation:** Click any stock to dive into detailed view

**Why Consider It:**
Could help discover opportunities across the entire universe without checking each stock individually. Efficient for daily screening.

---

## Feature Summary

| Feature | Phase | What You Can Do | How It Helps You |
| :------ | :---: | :-------------- | :--------------- |
| **Data Collection** | 1 | See historical patterns (2024+) | Foundation for all analysis |
| **Normalization** | 1 | Compare different data types directly | Makes divergence visible |
| **Interactive Dashboard** | 1 | Explore stocks with charts and controls | Your main tool for discovery |
| **Data Quality** | 1 | Trust the patterns you're seeing | Confidence in decisions |
| **Auto-Updates** | 2 | Always see current data | Stay relevant without effort |
| **Pattern Analysis** | 2 | Understand if hype leads or follows price | Separate signal from noise |
| **Real-Time Data** | 3 | Watch patterns emerge live | Spot opportunities sooner |
| **Stock Scanner** | 3 | Compare all stocks at once | Efficient daily screening |

---

## What Happens Next

### Immediate Focus: Phase 1
Building the core dashboard with historical data. Everything must work perfectly before moving forward.

### After Phase 1: Your Feedback
Once you've used the dashboard and explored the data, we'll discuss:
- What works well and what doesn't
- What features you actually use vs. what sounded good on paper
- Whether Phase 2 automation is the right next step
- Any adjustments needed based on real usage

### Phase 2 Decision Point
Only proceed to automation if:
- Phase 1 dashboard proves useful in practice
- You're using it regularly enough to need current data
- The value justifies the additional complexity

### Phase 3 Decision Point
Only consider advanced features if:
- Phase 2 is stable and valuable
- You've identified specific needs through regular use
- There's clear demand for real-time updates or multi-stock scanning

---

## The Bottom Line

**Phase 1:** Build a working dashboard that lets you explore divergence patterns for 12 stocks.

**Phase 2:** Keep it current with automatic updates and pattern analysis.

**Phase 3:** Maybe add advanced features if they prove necessary.

Each phase must be complete and useful before considering the next one.
