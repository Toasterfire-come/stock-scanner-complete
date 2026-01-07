export const BLOG_POSTS = [
  {
    slug: "top-10-trading-strategies-backtested-ai-results",
    title: "Top 10 Trading Strategies Backtested (AI Results)",
    date: "2026-01-05",
    description: "A practical tour through 10 common strategies and what to look for in their metrics before risking real capital.",
    mdPath: "/blog/top-10-trading-strategies-backtested-ai-results.md",
    tags: ["backtesting", "strategies", "ai"],
  },
  {
    slug: "how-to-beat-the-sp500-data-driven-analysis",
    title: "How to Beat the S&P 500: A Data-Driven Approach",
    date: "2026-01-05",
    description: "The rules, guardrails, and evaluation framework that matter more than any single indicator.",
    mdPath: "/blog/how-to-beat-the-sp500-data-driven-analysis.md",
    tags: ["investing", "benchmark", "risk"],
  },
  {
    slug: "day-trading-vs-swing-trading-which-is-more-profitable",
    title: "Day Trading vs Swing Trading: Which Is More Profitable?",
    date: "2026-01-05",
    description: "A no-hype comparison of trade frequency, costs, and the metrics that reveal survivability.",
    mdPath: "/blog/day-trading-vs-swing-trading-which-is-more-profitable.md",
    tags: ["day-trading", "swing-trading", "education"],
  },
  {
    slug: "understanding-sharpe-ratio-a-beginners-guide",
    title: "Understanding Sharpe Ratio: A Beginner’s Guide",
    date: "2026-01-05",
    description: "Sharpe demystified, plus when to prefer Sortino/Calmar and how to avoid common traps.",
    mdPath: "/blog/understanding-sharpe-ratio-a-beginners-guide.md",
    tags: ["metrics", "sharpe", "risk"],
  },
];

export function getPostBySlug(slug) {
  return BLOG_POSTS.find((p) => p.slug === slug) || null;
}

