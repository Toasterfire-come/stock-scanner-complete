# Implementation Tickets - Viral Features & Strategy Metrics
**Project:** Trade Scan Pro - AI Backtester Enhancements
**Sprint:** Viral Growth Features
**Created:** January 3, 2026

---

## EPIC 1: Social Sharing & Virality
**Goal:** Enable users to share backtest results across social platforms, driving organic growth
**Impact:** High - Expected 15% share rate, 135+ new users/month
**Effort:** 40 hours
**Priority:** P0 (Critical)

---

### TICKET #1: Social Share Buttons
**Type:** Feature
**Priority:** P0 - Critical
**Effort:** 8 hours
**Assignee:** Frontend Team

**User Story:**
As a user, I want to share my backtest results on social media so I can show my trading strategy performance to others.

**Acceptance Criteria:**
- [ ] Share buttons visible on Results tab (Twitter/X, LinkedIn, Reddit, Copy Link)
- [ ] Clicking Twitter opens pre-filled tweet with strategy results
- [ ] Clicking LinkedIn opens pre-filled post
- [ ] Clicking Reddit allows subreddit selection (r/stocks, r/wallstreetbets, r/options)
- [ ] Copy Link copies shareable URL to clipboard with toast confirmation
- [ ] Share preview shows auto-generated text before sharing
- [ ] Share events tracked in analytics (platform, backtest_id, total_return)

**Technical Specification:**

```jsx
// frontend/src/pages/app/Backtesting.jsx

import { Twitter, Linkedin, MessageSquare, Link2, Share2 } from "lucide-react";

// Add after Metrics Grid in Results tab
<Card className="mt-6">
  <CardHeader>
    <CardTitle className="flex items-center gap-2">
      <Share2 className="h-5 w-5 text-blue-500" />
      Share Your Results
    </CardTitle>
    <CardDescription>
      Show your trading strategy to the world
    </CardDescription>
  </CardHeader>
  <CardContent className="space-y-4">
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      <Button
        variant="outline"
        className="w-full"
        onClick={() => shareToTwitter(currentBacktest)}
      >
        <Twitter className="h-4 w-4 mr-2" />
        Twitter/X
      </Button>
      <Button
        variant="outline"
        className="w-full"
        onClick={() => shareToLinkedIn(currentBacktest)}
      >
        <Linkedin className="h-4 w-4 mr-2" />
        LinkedIn
      </Button>
      <Button
        variant="outline"
        className="w-full"
        onClick={() => shareToReddit(currentBacktest)}
      >
        <MessageSquare className="h-4 w-4 mr-2" />
        Reddit
      </Button>
      <Button
        variant="outline"
        className="w-full"
        onClick={() => copyShareLink(currentBacktest)}
      >
        <Link2 className="h-4 w-4 mr-2" />
        Copy Link
      </Button>
    </div>

    {/* Share Preview */}
    <div className="p-3 bg-gray-50 rounded-lg border">
      <p className="text-xs text-gray-600 mb-2 font-medium">Share preview:</p>
      <p className="text-sm">{generateShareText(currentBacktest)}</p>
    </div>
  </CardContent>
</Card>
```

**Share Functions:**

```javascript
function generateShareText(backtest) {
  const { total_return, win_rate, sharpe_ratio, total_trades } = backtest.results || {};
  const emoji = total_return >= 50 ? "🚀" : total_return >= 20 ? "📈" : total_return >= 0 ? "✅" : "📉";

  if (total_return >= 0) {
    return `I just backtested "${backtest.name}" on @TradeScanPro and got +${total_return?.toFixed(1)}% returns ${emoji}

Win rate: ${win_rate?.toFixed(1)}%
Sharpe: ${sharpe_ratio?.toFixed(2)}
Trades: ${total_trades}

Try it yourself 👉 ${getShareUrl(backtest)}`;
  } else {
    return `I backtested "${backtest.name}" on @TradeScanPro and learned valuable lessons 📚

Even great strategies can fail. Always test before you trade!

Try backtesting 👉 ${getShareUrl(backtest)}`;
  }
}

function shareToTwitter(backtest) {
  const text = generateShareText(backtest);
  const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
  window.open(url, '_blank', 'width=550,height=420');
  trackShare('twitter', backtest.id);
}

function shareToLinkedIn(backtest) {
  const url = getShareUrl(backtest);
  const linkedInUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
  window.open(linkedInUrl, '_blank', 'width=550,height=420');
  trackShare('linkedin', backtest.id);
}

function shareToReddit(backtest) {
  const text = generateShareText(backtest);
  const url = getShareUrl(backtest);
  const redditUrl = `https://reddit.com/submit?url=${encodeURIComponent(url)}&title=${encodeURIComponent(backtest.name)}`;
  window.open(redditUrl, '_blank', 'width=800,height=600');
  trackShare('reddit', backtest.id);
}

async function copyShareLink(backtest) {
  const url = getShareUrl(backtest);
  await navigator.clipboard.writeText(url);
  toast.success("Link copied to clipboard!");
  trackShare('copy_link', backtest.id);
}

function getShareUrl(backtest) {
  // TODO: Replace with actual public backtest URL when implemented
  return `https://tradescanpro.com/app/backtesting?id=${backtest.id}`;
}

function trackShare(platform, backtestId) {
  // Send to analytics
  if (window.analytics) {
    window.analytics.track('Backtest Shared', {
      platform,
      backtest_id: backtestId,
      category: currentBacktest.category,
      total_return: currentBacktest.results?.total_return
    });
  }
}
```

**Dependencies:**
- None (uses native browser APIs)

**Testing:**
- [ ] Verify Twitter popup opens with correct text
- [ ] Verify LinkedIn popup opens
- [ ] Verify Reddit popup opens
- [ ] Verify Copy Link copies correct URL
- [ ] Verify toast notification appears
- [ ] Verify analytics events fire
- [ ] Test on mobile devices
- [ ] Test with long strategy names (truncation)

**Screenshots:**
- [ ] Share buttons section design
- [ ] Share preview mockup
- [ ] Mobile responsive layout

---

### TICKET #2: Image Export Feature
**Type:** Feature
**Priority:** P0 - Critical
**Effort:** 16 hours
**Assignee:** Frontend Team

**User Story:**
As a user, I want to download my backtest results as a beautiful image so I can share it on Instagram, Twitter, and other visual platforms.

**Acceptance Criteria:**
- [ ] "Download as Image" button visible on Results tab
- [ ] Clicking button generates PNG image (1200x628px for Twitter, 1080x1080px for Instagram)
- [ ] Image includes: Strategy name, key metrics, equity curve chart, branding
- [ ] Image has Trade Scan Pro watermark and QR code
- [ ] Loading state shown during image generation
- [ ] Success toast when image downloads
- [ ] Works on desktop and mobile

**Technical Specification:**

**Dependencies:**
```json
{
  "html-to-image": "^1.11.11",
  "qrcode.react": "^3.1.0"
}
```

**Install:**
```bash
npm install html-to-image qrcode.react
```

**Component:**

```jsx
import { toPng } from 'html-to-image';
import { Download } from 'lucide-react';
import QRCode from 'qrcode.react';
import { useRef } from 'react';

// Add ref to Results section
const resultsCardRef = useRef(null);

// Download button
<Button
  size="lg"
  className="w-full md:w-auto"
  onClick={() => exportAsImage()}
  disabled={isExporting}
>
  {isExporting ? (
    <>
      <Loader2 className="h-5 w-5 mr-2 animate-spin" />
      Generating...
    </>
  ) : (
    <>
      <Download className="h-5 w-5 mr-2" />
      Download as Image
    </>
  )}
</Button>

// Export function
async function exportAsImage() {
  setIsExporting(true);
  try {
    // Hide elements not needed in export
    const shareSection = document.getElementById('share-section');
    if (shareSection) shareSection.style.display = 'none';

    const dataUrl = await toPng(resultsCardRef.current, {
      quality: 1.0,
      pixelRatio: 2, // Retina quality
      backgroundColor: '#ffffff',
      width: 1200,
      height: 628 // Twitter card size
    });

    // Restore hidden elements
    if (shareSection) shareSection.style.display = 'block';

    // Download
    const link = document.createElement('a');
    link.download = `${currentBacktest.name.replace(/\s+/g, '_')}_results.png`;
    link.href = dataUrl;
    link.click();

    toast.success("Image downloaded successfully!");

    // Track event
    if (window.analytics) {
      window.analytics.track('Backtest Image Exported', {
        backtest_id: currentBacktest.id,
        total_return: currentBacktest.results?.total_return
      });
    }
  } catch (error) {
    console.error('Export failed:', error);
    toast.error("Failed to export image. Please try again.");
  } finally {
    setIsExporting(false);
  }
}
```

**Shareable Image Template:**

```jsx
// Create dedicated component for export
<div
  ref={resultsCardRef}
  className="bg-gradient-to-br from-blue-50 via-white to-purple-50 p-8"
  style={{ width: '1200px', minHeight: '628px' }}
>
  {/* Header */}
  <div className="flex items-center justify-between mb-6">
    <div className="flex items-center gap-3">
      <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
        <Brain className="h-8 w-8 text-white" />
      </div>
      <div>
        <h1 className="text-3xl font-bold">Trade Scan Pro</h1>
        <p className="text-gray-600">AI-Powered Backtesting</p>
      </div>
    </div>
    <QRCode
      value={getShareUrl(currentBacktest)}
      size={80}
      level="M"
    />
  </div>

  {/* Strategy Info */}
  <div className="mb-6">
    <h2 className="text-2xl font-bold mb-1">{currentBacktest.name}</h2>
    <div className="flex items-center gap-2">
      <Badge>{CATEGORY_LABELS[currentBacktest.category]}</Badge>
      <Badge variant="outline">{currentBacktest.symbols?.join(", ")}</Badge>
    </div>
  </div>

  {/* Key Metrics - Large & Visual */}
  <div className="grid grid-cols-4 gap-4 mb-6">
    <div className="bg-white rounded-lg p-4 shadow-md border-2 border-green-200">
      <p className="text-sm text-gray-600 mb-1">Total Return</p>
      <p className="text-4xl font-bold text-green-600">
        {currentBacktest.results?.total_return >= 0 ? "+" : ""}
        {currentBacktest.results?.total_return?.toFixed(1)}%
      </p>
    </div>
    <div className="bg-white rounded-lg p-4 shadow-md">
      <p className="text-sm text-gray-600 mb-1">Sharpe Ratio</p>
      <p className="text-4xl font-bold text-blue-600">
        {currentBacktest.results?.sharpe_ratio?.toFixed(2)}
      </p>
    </div>
    <div className="bg-white rounded-lg p-4 shadow-md">
      <p className="text-sm text-gray-600 mb-1">Win Rate</p>
      <p className="text-4xl font-bold text-purple-600">
        {currentBacktest.results?.win_rate?.toFixed(1)}%
      </p>
    </div>
    <div className="bg-white rounded-lg p-4 shadow-md">
      <p className="text-sm text-gray-600 mb-1">Max Drawdown</p>
      <p className="text-4xl font-bold text-red-600">
        {currentBacktest.results?.max_drawdown?.toFixed(1)}%
      </p>
    </div>
  </div>

  {/* Equity Curve - Simplified for export */}
  <div className="bg-white rounded-lg p-4 shadow-md mb-6">
    <ResponsiveContainer width="100%" height={200}>
      <AreaChart data={equityCurveData}>
        {/* Simplified chart for export */}
      </AreaChart>
    </ResponsiveContainer>
  </div>

  {/* Footer with branding */}
  <div className="flex items-center justify-between text-sm text-gray-600">
    <div>
      <p className="font-medium">
        {currentBacktest.results?.total_trades} trades •
        {currentBacktest.start_date} to {currentBacktest.end_date}
      </p>
    </div>
    <div className="text-right">
      <p className="font-bold text-lg">tradescanpro.com</p>
      <p className="text-xs">Scan QR code to view full results</p>
    </div>
  </div>
</div>
```

**Image Variations:**
1. **Twitter Card** (1200x628px) - Horizontal, fits in tweet preview
2. **Instagram Post** (1080x1080px) - Square, full feed post
3. **Instagram Story** (1080x1920px) - Vertical, story format

**Testing:**
- [ ] Verify image downloads with correct filename
- [ ] Check image quality (2x pixel ratio)
- [ ] Verify all metrics visible and legible
- [ ] Test QR code scans correctly
- [ ] Verify chart renders in export
- [ ] Test on different browsers (Chrome, Firefox, Safari)
- [ ] Test on mobile devices
- [ ] Verify watermark visible but not obtrusive

---

### TICKET #3: Advanced Strategy Metrics & Calculations
**Type:** Feature
**Priority:** P1 - High
**Effort:** 12 hours
**Assignee:** Backend Team + Frontend Team

**User Story:**
As a user, I want to see advanced metrics and calculations that help me judge if my strategy is truly good, beyond just total return percentage.

**Acceptance Criteria:**
- [ ] Calculate and display 15+ advanced metrics
- [ ] Show risk-adjusted returns
- [ ] Compare strategy to benchmarks (Buy & Hold, S&P 500)
- [ ] Display strategy quality score (0-100)
- [ ] Show trade quality analysis
- [ ] Include statistical significance indicators
- [ ] Add interpretation guides ("What does this mean?")
- [ ] Mobile-responsive metric cards

**Advanced Metrics to Calculate:**

**1. Risk-Adjusted Performance:**
```python
# backend/stocks/services/backtesting_service.py

def calculate_advanced_metrics(trades, equity_curve, initial_capital):
    """
    Calculate advanced metrics to help users judge strategy quality
    """
    import numpy as np
    from scipy import stats

    # Daily returns
    daily_returns = np.diff(equity_curve) / equity_curve[:-1]

    metrics = {}

    # === RISK METRICS ===

    # 1. Sortino Ratio (like Sharpe but only penalizes downside volatility)
    downside_returns = daily_returns[daily_returns < 0]
    downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
    metrics['sortino_ratio'] = (
        (np.mean(daily_returns) * 252) / (downside_std * np.sqrt(252))
        if downside_std > 0 else 0
    )

    # 2. Calmar Ratio (Return / Max Drawdown)
    max_dd = calculate_max_drawdown(equity_curve)
    annualized_return = ((equity_curve[-1] / equity_curve[0]) ** (252 / len(equity_curve)) - 1) * 100
    metrics['calmar_ratio'] = (
        annualized_return / abs(max_dd)
        if max_dd < 0 else 0
    )

    # 3. Value at Risk (VaR) - 95% confidence
    metrics['var_95'] = np.percentile(daily_returns, 5) * 100  # % loss at 95% confidence

    # 4. Conditional VaR (CVaR) - Expected loss when VaR is exceeded
    var_threshold = np.percentile(daily_returns, 5)
    cvar_returns = daily_returns[daily_returns <= var_threshold]
    metrics['cvar_95'] = np.mean(cvar_returns) * 100 if len(cvar_returns) > 0 else 0

    # 5. Omega Ratio (Probability-weighted gains/losses)
    threshold = 0
    gains = daily_returns[daily_returns > threshold]
    losses = daily_returns[daily_returns < threshold]
    metrics['omega_ratio'] = (
        np.sum(gains - threshold) / abs(np.sum(losses - threshold))
        if len(losses) > 0 else 0
    )

    # === TRADE QUALITY ===

    # 6. Average Win / Average Loss Ratio
    winning_trades = [t for t in trades if t['return_pct'] > 0]
    losing_trades = [t for t in trades if t['return_pct'] < 0]

    avg_win = np.mean([t['return_pct'] for t in winning_trades]) if winning_trades else 0
    avg_loss = np.mean([t['return_pct'] for t in losing_trades]) if losing_trades else 0
    metrics['avg_win_loss_ratio'] = (
        avg_win / abs(avg_loss)
        if avg_loss != 0 else 0
    )

    # 7. Expectancy (Average trade outcome)
    metrics['expectancy'] = np.mean([t['return_pct'] for t in trades]) if trades else 0

    # 8. Payoff Ratio
    metrics['payoff_ratio'] = metrics['avg_win_loss_ratio']

    # 9. Kelly Criterion (Optimal position sizing)
    win_rate = len(winning_trades) / len(trades) if trades else 0
    metrics['kelly_percentage'] = (
        win_rate - ((1 - win_rate) / metrics['avg_win_loss_ratio'])
        if metrics['avg_win_loss_ratio'] > 0 else 0
    ) * 100

    # === CONSISTENCY METRICS ===

    # 10. Consecutive Wins/Losses (max streak)
    streaks = []
    current_streak = 0
    for t in trades:
        if t['return_pct'] > 0:
            current_streak = max(0, current_streak) + 1
        else:
            current_streak = min(0, current_streak) - 1
        streaks.append(current_streak)

    metrics['max_win_streak'] = max(streaks) if streaks else 0
    metrics['max_loss_streak'] = abs(min(streaks)) if streaks else 0

    # 11. Percent Profitable Months
    # Group equity by month and check if positive
    # (Simplified - would need actual date grouping)
    metrics['profitable_months_pct'] = 70  # Placeholder

    # 12. Recovery Factor (Net Profit / Max Drawdown)
    net_profit = equity_curve[-1] - initial_capital
    metrics['recovery_factor'] = (
        net_profit / abs(max_dd * initial_capital / 100)
        if max_dd < 0 else 0
    )

    # === BENCHMARK COMPARISON ===

    # 13. Alpha (Excess return vs benchmark)
    # Assuming S&P 500 historical return ~10%/year
    benchmark_return = 10  # %
    metrics['alpha'] = annualized_return - benchmark_return

    # 14. Beta (Volatility vs market)
    # Would need actual S&P 500 data for accurate calculation
    metrics['beta'] = 1.0  # Placeholder (1.0 = same volatility as market)

    # 15. Information Ratio (Alpha / Tracking Error)
    tracking_error = 5  # Placeholder
    metrics['information_ratio'] = metrics['alpha'] / tracking_error if tracking_error > 0 else 0

    # === STATISTICAL SIGNIFICANCE ===

    # 16. T-Statistic (Is performance statistically significant?)
    if len(daily_returns) > 1:
        t_stat, p_value = stats.ttest_1samp(daily_returns, 0)
        metrics['t_statistic'] = t_stat
        metrics['p_value'] = p_value
        metrics['statistically_significant'] = p_value < 0.05  # 95% confidence
    else:
        metrics['t_statistic'] = 0
        metrics['p_value'] = 1.0
        metrics['statistically_significant'] = False

    # === COMPOSITE QUALITY SCORE ===

    # Calculate overall strategy quality (0-100)
    score_components = {
        'returns': min(annualized_return / 30 * 20, 20),  # Max 20 points for 30%+ return
        'sharpe': min(metrics.get('sharpe_ratio', 0) / 2 * 15, 15),  # Max 15 points for 2.0+ Sharpe
        'win_rate': (len(winning_trades) / len(trades) if trades else 0) * 15,  # Max 15 points
        'drawdown': max(20 + max_dd, 0),  # Max 20 points for low drawdown
        'consistency': min(metrics['expectancy'] * 10, 15),  # Max 15 points
        'trades': min(len(trades) / 50 * 15, 15)  # Max 15 points for 50+ trades
    }

    metrics['quality_score'] = sum(score_components.values())
    metrics['quality_grade'] = (
        'A+' if metrics['quality_score'] >= 90 else
        'A' if metrics['quality_score'] >= 80 else
        'B' if metrics['quality_score'] >= 70 else
        'C' if metrics['quality_score'] >= 60 else
        'D' if metrics['quality_score'] >= 50 else
        'F'
    )

    return metrics
```

**Frontend Display:**

```jsx
// Add new "Analysis" tab or expand Results tab

<Tabs>
  <TabsList>
    <TabsTrigger value="overview">Overview</TabsTrigger>
    <TabsTrigger value="advanced">Advanced Metrics</TabsTrigger>
    <TabsTrigger value="comparison">Benchmark Comparison</TabsTrigger>
  </TabsList>

  <TabsContent value="advanced">
    {/* Quality Score Card */}
    <Card className="mb-6 bg-gradient-to-br from-purple-50 to-blue-50">
      <CardContent className="p-6">
        <div className="text-center">
          <div className="inline-block p-6 bg-white rounded-full shadow-lg mb-4">
            <div className="text-6xl font-bold text-purple-600">
              {metrics.quality_grade}
            </div>
          </div>
          <h3 className="text-2xl font-bold mb-2">Strategy Quality Score</h3>
          <div className="flex items-center justify-center gap-2 mb-4">
            <Progress value={metrics.quality_score} className="w-64 h-3" />
            <span className="font-bold">{metrics.quality_score?.toFixed(1)}/100</span>
          </div>
          <p className="text-gray-600 max-w-2xl mx-auto">
            This composite score evaluates your strategy based on returns, risk-adjusted performance,
            consistency, and trade quality. Scores above 70 indicate a solid strategy.
          </p>
        </div>
      </CardContent>
    </Card>

    {/* Risk-Adjusted Metrics */}
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shield className="h-5 w-5 text-blue-500" />
          Risk-Adjusted Performance
        </CardTitle>
        <CardDescription>
          Understanding risk is as important as returns
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard
            title="Sortino Ratio"
            value={metrics.sortino_ratio?.toFixed(2)}
            subtitle={
              metrics.sortino_ratio > 2 ? "Excellent" :
              metrics.sortino_ratio > 1 ? "Good" :
              metrics.sortino_ratio > 0 ? "Fair" : "Poor"
            }
            tooltip="Like Sharpe ratio, but only penalizes downside volatility. Higher is better."
            icon={TrendingUp}
            color={metrics.sortino_ratio > 1.5 ? "green" : "blue"}
          />

          <MetricCard
            title="Calmar Ratio"
            value={metrics.calmar_ratio?.toFixed(2)}
            subtitle={
              metrics.calmar_ratio > 3 ? "Excellent" :
              metrics.calmar_ratio > 1 ? "Good" : "Fair"
            }
            tooltip="Return divided by max drawdown. Measures risk-adjusted returns."
            icon={Target}
            color={metrics.calmar_ratio > 2 ? "green" : "blue"}
          />

          <MetricCard
            title="Omega Ratio"
            value={metrics.omega_ratio?.toFixed(2)}
            subtitle={
              metrics.omega_ratio > 1.5 ? "Excellent" :
              metrics.omega_ratio > 1 ? "Good" : "Poor"
            }
            tooltip="Probability-weighted ratio of gains to losses. Above 1.0 is good."
            icon={BarChart3}
            color={metrics.omega_ratio > 1.2 ? "green" : "yellow"}
          />

          <MetricCard
            title="Recovery Factor"
            value={metrics.recovery_factor?.toFixed(2)}
            subtitle={
              metrics.recovery_factor > 5 ? "Excellent" :
              metrics.recovery_factor > 2 ? "Good" : "Fair"
            }
            tooltip="Net profit divided by max drawdown. Higher means faster recovery from losses."
            icon={TrendingUp}
            color={metrics.recovery_factor > 3 ? "green" : "blue"}
          />
        </div>
      </CardContent>
    </Card>

    {/* Downside Risk */}
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-red-500" />
          Downside Risk Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="p-4 bg-red-50 rounded-lg border border-red-200">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-red-700">Value at Risk (95%)</p>
              <HelpCircle className="h-4 w-4 text-red-400" />
            </div>
            <p className="text-2xl font-bold text-red-600">
              {metrics.var_95?.toFixed(2)}%
            </p>
            <p className="text-xs text-red-600 mt-1">
              95% chance of not losing more than this in a day
            </p>
          </div>

          <div className="p-4 bg-red-50 rounded-lg border border-red-200">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-red-700">Conditional VaR</p>
              <HelpCircle className="h-4 w-4 text-red-400" />
            </div>
            <p className="text-2xl font-bold text-red-600">
              {metrics.cvar_95?.toFixed(2)}%
            </p>
            <p className="text-xs text-red-600 mt-1">
              Average loss when VaR is exceeded
            </p>
          </div>

          <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-orange-700">Max Loss Streak</p>
              <HelpCircle className="h-4 w-4 text-orange-400" />
            </div>
            <p className="text-2xl font-bold text-orange-600">
              {metrics.max_loss_streak}
            </p>
            <p className="text-xs text-orange-600 mt-1">
              Longest consecutive losing trades
            </p>
          </div>
        </div>
      </CardContent>
    </Card>

    {/* Trade Quality */}
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Trophy className="h-5 w-5 text-yellow-500" />
          Trade Quality Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard
            title="Avg Win / Avg Loss"
            value={metrics.avg_win_loss_ratio?.toFixed(2) + "x"}
            subtitle={
              metrics.avg_win_loss_ratio > 2 ? "Excellent" :
              metrics.avg_win_loss_ratio > 1.5 ? "Good" : "Fair"
            }
            tooltip="How much you win vs how much you lose on average. Above 1.5x is good."
            icon={TrendingUp}
            color={metrics.avg_win_loss_ratio > 1.5 ? "green" : "yellow"}
          />

          <MetricCard
            title="Expectancy"
            value={metrics.expectancy?.toFixed(2) + "%"}
            subtitle="Per trade"
            tooltip="Average expected profit per trade. Positive is good."
            icon={DollarSign}
            color={metrics.expectancy > 0.5 ? "green" : "yellow"}
          />

          <MetricCard
            title="Kelly %"
            value={metrics.kelly_percentage?.toFixed(1) + "%"}
            subtitle={
              metrics.kelly_percentage > 20 ? "Aggressive" :
              metrics.kelly_percentage > 0 ? "Optimal" : "Not viable"
            }
            tooltip="Optimal position size per the Kelly Criterion. Use 25-50% of this value."
            icon={Percent}
            color={metrics.kelly_percentage > 0 ? "green" : "red"}
          />

          <MetricCard
            title="Max Win Streak"
            value={metrics.max_win_streak}
            subtitle="Trades"
            tooltip="Longest consecutive winning trades. Shows consistency."
            icon={Zap}
            color="green"
          />
        </div>
      </CardContent>
    </Card>

    {/* Statistical Significance */}
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-purple-500" />
          Statistical Significance
        </CardTitle>
        <CardDescription>
          Is your strategy's performance due to skill or luck?
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium mb-1">T-Statistic</p>
              <p className="text-3xl font-bold text-purple-600">
                {metrics.t_statistic?.toFixed(2)}
              </p>
            </div>
            <div className="text-right">
              <p className="font-medium mb-1">P-Value</p>
              <p className="text-2xl font-bold text-gray-700">
                {metrics.p_value?.toFixed(4)}
              </p>
            </div>
            <div>
              {metrics.statistically_significant ? (
                <Badge className="bg-green-100 text-green-700 text-lg px-4 py-2">
                  <CheckCircle className="h-5 w-5 mr-2" />
                  Statistically Significant
                </Badge>
              ) : (
                <Badge className="bg-yellow-100 text-yellow-700 text-lg px-4 py-2">
                  <AlertCircle className="h-5 w-5 mr-2" />
                  Not Significant
                </Badge>
              )}
            </div>
          </div>

          <Alert className={metrics.statistically_significant ? "bg-green-50 border-green-200" : "bg-yellow-50 border-yellow-200"}>
            <AlertDescription>
              {metrics.statistically_significant ? (
                <>
                  <strong>Good news!</strong> Your strategy's performance is statistically significant (p &lt; 0.05),
                  meaning it's unlikely due to random chance. This suggests skill-based performance.
                </>
              ) : (
                <>
                  <strong>Caution:</strong> Your strategy's performance is not statistically significant (p ≥ 0.05).
                  This could be due to random chance. Consider running more backtests or increasing sample size.
                </>
              )}
            </AlertDescription>
          </Alert>
        </div>
      </CardContent>
    </Card>
  </TabsContent>

  {/* Benchmark Comparison Tab */}
  <TabsContent value="comparison">
    <Card>
      <CardHeader>
        <CardTitle>Benchmark Comparison</CardTitle>
        <CardDescription>How does your strategy stack up?</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Comparison Table */}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4">Metric</th>
                  <th className="text-right py-3 px-4">Your Strategy</th>
                  <th className="text-right py-3 px-4">Buy & Hold</th>
                  <th className="text-right py-3 px-4">S&P 500</th>
                  <th className="text-right py-3 px-4">Difference</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="py-3 px-4">Annual Return</td>
                  <td className="text-right font-bold">{annualizedReturn?.toFixed(1)}%</td>
                  <td className="text-right">12.5%</td>
                  <td className="text-right">10.0%</td>
                  <td className={`text-right font-bold ${metrics.alpha > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {metrics.alpha > 0 ? '+' : ''}{metrics.alpha?.toFixed(1)}%
                  </td>
                </tr>
                <tr className="border-b">
                  <td className="py-3 px-4">Sharpe Ratio</td>
                  <td className="text-right font-bold">{metrics.sharpe_ratio?.toFixed(2)}</td>
                  <td className="text-right">0.85</td>
                  <td className="text-right">0.75</td>
                  <td className={`text-right font-bold ${metrics.sharpe_ratio > 0.85 ? 'text-green-600' : 'text-red-600'}`}>
                    {metrics.sharpe_ratio > 0.85 ? '✓ Better' : '✗ Worse'}
                  </td>
                </tr>
                {/* Add more rows */}
              </tbody>
            </table>
          </div>

          {/* Alpha Visualization */}
          <div className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
            <h4 className="font-bold text-lg mb-2">Alpha (Excess Return)</h4>
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <Progress
                  value={50 + (metrics.alpha / 20) * 50}
                  className="h-4"
                />
              </div>
              <div className="text-3xl font-bold text-purple-600">
                {metrics.alpha > 0 ? '+' : ''}{metrics.alpha?.toFixed(1)}%
              </div>
            </div>
            <p className="text-sm text-gray-600 mt-2">
              {metrics.alpha > 0
                ? `Your strategy beat the market by ${metrics.alpha.toFixed(1)}%!`
                : `Your strategy underperformed the market by ${Math.abs(metrics.alpha).toFixed(1)}%.`
              }
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  </TabsContent>
</Tabs>
```

**Testing:**
- [ ] Verify all 16 metrics calculate correctly
- [ ] Test with various strategy types (day trading, swing, long-term)
- [ ] Verify quality score accuracy (0-100 range)
- [ ] Test statistical significance calculation
- [ ] Verify tooltips explain metrics clearly
- [ ] Test mobile responsiveness
- [ ] Verify benchmark comparison data
- [ ] Test with edge cases (0 trades, 100% win rate, etc.)

**Documentation:**
- [ ] Add metric definitions to help docs
- [ ] Create "Understanding Your Metrics" guide
- [ ] Add video tutorial explaining key metrics
- [ ] Include benchmark data sources in footer

---

## TICKET #4: Public Backtest Pages
**Type:** Feature
**Priority:** P1 - High
**Effort:** 12 hours
**Assignee:** Full Stack Team

**User Story:**
As a user, I want to make my backtest results public and shareable via a unique URL, so others can view my strategy performance and I can build my trading reputation.

**Backend Specification:**

```python
# backend/stocks/models.py - Add to Backtest model

class Backtest(models.Model):
    # ... existing fields ...

    is_public = models.BooleanField(default=False, db_index=True)
    share_slug = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        db_index=True
    )
    share_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    fork_count = models.IntegerField(default=0)
    forked_from = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='forks'
    )

    class Meta:
        indexes = [
            models.Index(fields=['share_slug']),
            models.Index(fields=['is_public', '-created_at']),
            models.Index(fields=['-view_count']),  # For leaderboards
        ]

# backend/stocks/backtesting_api.py - Add new endpoints

import secrets
import string

def generate_share_slug():
    """Generate URL-safe random slug"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(10))

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def share_backtest(request, backtest_id):
    """
    Make a backtest publicly shareable
    POST /api/backtesting/<id>/share/
    """
    try:
        backtest = Backtest.objects.get(id=backtest_id, user=request.user)

        if not backtest.is_public:
            backtest.is_public = True
            backtest.share_slug = generate_share_slug()
            backtest.save()

        share_url = f'https://tradescanpro.com/backtest/{backtest.share_slug}'

        return JsonResponse({
            'success': True,
            'share_url': share_url,
            'share_slug': backtest.share_slug
        })
    except Backtest.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Backtest not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def unshare_backtest(request, backtest_id):
    """
    Make a backtest private again
    POST /api/backtesting/<id>/unshare/
    """
    try:
        backtest = Backtest.objects.get(id=backtest_id, user=request.user)
        backtest.is_public = False
        backtest.save()

        return JsonResponse({'success': True})
    except Backtest.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)

@csrf_exempt
@require_http_methods(["GET"])
def public_backtest(request, share_slug):
    """
    View a public backtest (no auth required)
    GET /api/backtesting/share/<slug>/
    """
    try:
        backtest = Backtest.objects.select_related('user').get(
            share_slug=share_slug,
            is_public=True
        )

        # Increment view count
        backtest.view_count += 1
        backtest.save(update_fields=['view_count'])

        # Serialize backtest data
        data = {
            'id': backtest.id,
            'name': backtest.name,
            'category': backtest.category,
            'strategy_text': backtest.strategy_text,
            'symbols': backtest.symbols,
            'start_date': backtest.start_date,
            'end_date': backtest.end_date,
            'initial_capital': float(backtest.initial_capital),
            'results': backtest.results,
            'equity_curve': backtest.equity_curve,
            'trades': backtest.trades[:50],  # Limit to 50 trades for public view
            'created_at': backtest.created_at.isoformat(),
            'view_count': backtest.view_count,
            'fork_count': backtest.fork_count,
            'user': {
                'username': backtest.user.username,
                'profile_url': f'/profile/{backtest.user.username}'
            }
        }

        return JsonResponse({
            'success': True,
            'backtest': data
        })
    except Backtest.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Backtest not found or not public'
        }, status=404)

# Add to urlpatterns
urlpatterns = [
    # ... existing patterns ...
    path('backtesting/<int:backtest_id>/share/', share_backtest),
    path('backtesting/<int:backtest_id>/unshare/', unshare_backtest),
    path('backtesting/share/<slug:share_slug>/', public_backtest),
]
```

**Frontend Specification:**

```jsx
// frontend/src/pages/PublicBacktest.jsx - New page

import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getPublicBacktest } from '../api/client';

export default function PublicBacktest() {
  const { shareSlug } = useParams();
  const [backtest, setBacktest] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBacktest();
  }, [shareSlug]);

  async function loadBacktest() {
    try {
      const response = await getPublicBacktest(shareSlug);
      if (response.success) {
        setBacktest(response.backtest);
      }
    } catch (error) {
      toast.error("Failed to load backtest");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!backtest) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <h1 className="text-3xl font-bold mb-4">Backtest Not Found</h1>
        <p className="text-gray-600 mb-6">
          This backtest doesn't exist or is no longer public.
        </p>
        <Button onClick={() => navigate('/app/backtesting')}>
          Try AI Backtesting
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* SEO */}
      <Helmet>
        <title>{backtest.name} - AI Backtest Results | Trade Scan Pro</title>
        <meta
          name="description"
          content={`${backtest.name} backtested on Trade Scan Pro. ${backtest.results?.total_return?.toFixed(1)}% return, ${backtest.results?.win_rate?.toFixed(1)}% win rate.`}
        />
        <meta property="og:title" content={`${backtest.name} - Backtest Results`} />
        <meta property="og:description" content={`Return: ${backtest.results?.total_return?.toFixed(1)}%, Win Rate: ${backtest.results?.win_rate?.toFixed(1)}%`} />
      </Helmet>

      {/* Public Badge */}
      <div className="mb-6">
        <Badge variant="outline" className="mb-2">
          <Globe className="h-3 w-3 mr-1" />
          Public Backtest
        </Badge>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">{backtest.name}</h1>
            <p className="text-gray-600">
              by{' '}
              <a
                href={backtest.user.profile_url}
                className="text-blue-600 hover:underline font-medium"
              >
                @{backtest.user.username}
              </a>
              {' '}• {backtest.view_count} views • {backtest.fork_count} forks
            </p>
          </div>

          <div className="flex gap-2">
            <Button onClick={() => forkBacktest(backtest)}>
              <GitBranch className="h-4 w-4 mr-2" />
              Fork Strategy
            </Button>
            <Button variant="outline" onClick={() => shareBacktest(backtest)}>
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>
          </div>
        </div>
      </div>

      {/* Show same Results tab content but read-only */}
      <ResultsDisplay backtest={backtest} readOnly />

      {/* CTA for non-logged-in users */}
      {!isAuthenticated && (
        <Card className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200">
          <CardContent className="p-8 text-center">
            <Brain className="h-12 w-12 mx-auto mb-4 text-blue-600" />
            <h3 className="text-2xl font-bold mb-2">Want to test your own strategies?</h3>
            <p className="text-gray-600 mb-6">
              Join Trade Scan Pro and use AI to backtest unlimited trading strategies
            </p>
            <div className="flex gap-4 justify-center">
              <Button size="lg" onClick={() => navigate('/signup')}>
                Start Free Trial
              </Button>
              <Button size="lg" variant="outline" onClick={() => navigate('/pricing')}>
                View Pricing
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// Add route to App.js
<Route path="/backtest/:shareSlug" element={<PublicBacktest />} />
```

**Testing:**
- [ ] Create public backtest and verify slug generated
- [ ] Access public URL without being logged in
- [ ] Verify view count increments
- [ ] Test non-existent slug returns 404
- [ ] Test private backtest not accessible via public URL
- [ ] Verify SEO meta tags render correctly
- [ ] Test share buttons on public page
- [ ] Test fork functionality

---

## TICKET #5: Strategy Forking
**Type:** Feature
**Priority:** P2 - Medium
**Effort:** 8 hours
**Assignee:** Full Stack Team

**User Story:**
As a user, I want to fork (copy) someone else's public strategy so I can modify it and run my own backtest, creating a network effect like GitHub.

**Implementation:**
(See full spec in ticket...)

---

## TICKET #6-12: Additional Viral Features
(Leaderboards, Achievement System, Comparison Mode, PDF Export, Embed Widgets, Challenge Mode, Viral Headlines, Before/After Viz)

---

**Total Effort Estimate:** 120 hours (3 weeks with 2 engineers)
**Expected ROI:** $15-25K additional MRR within 12 months
**Priority Order:** #1 → #2 → #3 → #4 → #5 → ... (implement in order)

---

**Document Version:** 1.0
**Last Updated:** January 3, 2026
**Status:** Ready for Sprint Planning
