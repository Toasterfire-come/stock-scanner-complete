import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './ui/tooltip';
import {
  TrendingUp,
  TrendingDown,
  Minus,
  Info,
  Target,
  Shield,
  DollarSign,
  BarChart3,
} from 'lucide-react';
import { cn } from '../lib/utils';

const STATUS_CONFIG = {
  significantly_undervalued: {
    label: 'Significantly Undervalued',
    color: 'text-green-600 dark:text-green-400',
    bgColor: 'bg-green-100 dark:bg-green-900/30',
    icon: TrendingUp,
  },
  undervalued: {
    label: 'Undervalued',
    color: 'text-green-500 dark:text-green-400',
    bgColor: 'bg-green-50 dark:bg-green-900/20',
    icon: TrendingUp,
  },
  fair_value: {
    label: 'Fair Value',
    color: 'text-gray-600 dark:text-gray-400',
    bgColor: 'bg-gray-100 dark:bg-gray-800/30',
    icon: Minus,
  },
  overvalued: {
    label: 'Overvalued',
    color: 'text-red-500 dark:text-red-400',
    bgColor: 'bg-red-50 dark:bg-red-900/20',
    icon: TrendingDown,
  },
  significantly_overvalued: {
    label: 'Significantly Overvalued',
    color: 'text-red-600 dark:text-red-400',
    bgColor: 'bg-red-100 dark:bg-red-900/30',
    icon: TrendingDown,
  },
  insufficient_data: {
    label: 'Insufficient Data',
    color: 'text-gray-400',
    bgColor: 'bg-gray-50 dark:bg-gray-800/20',
    icon: Info,
  },
};

const RECOMMENDATION_CONFIG = {
  'STRONG BUY': { color: 'bg-green-600 text-white', textColor: 'text-green-600' },
  'BUY': { color: 'bg-green-500 text-white', textColor: 'text-green-500' },
  'HOLD': { color: 'bg-yellow-500 text-white', textColor: 'text-yellow-600' },
  'SELL': { color: 'bg-red-500 text-white', textColor: 'text-red-500' },
  'STRONG SELL': { color: 'bg-red-600 text-white', textColor: 'text-red-600' },
};

const GRADE_COLORS = {
  'A': 'text-green-600 bg-green-100',
  'B': 'text-blue-600 bg-blue-100',
  'C': 'text-yellow-600 bg-yellow-100',
  'D': 'text-orange-600 bg-orange-100',
  'F': 'text-red-600 bg-red-100',
};

function ScoreGauge({ score, label, maxScore = 100 }) {
  const percentage = score ? (score / maxScore) * 100 : 0;
  const color = percentage >= 70 ? 'bg-green-500' : percentage >= 50 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className="font-semibold">{score?.toFixed(1) || 'N/A'}</span>
      </div>
      <Progress value={percentage} className="h-2" indicatorClassName={color} />
    </div>
  );
}

function ValuationModel({ label, value, currentPrice, description }) {
  if (!value) return null;

  const margin = currentPrice ? ((value / currentPrice) - 1) * 100 : 0;
  const isUndervalued = margin > 0;

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="flex items-center justify-between p-2 rounded-lg bg-muted/50 hover:bg-muted transition-colors cursor-help">
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">{label}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-semibold">${value.toFixed(2)}</span>
              <Badge
                variant="outline"
                className={cn(
                  'text-xs',
                  isUndervalued ? 'text-green-600 border-green-200' : 'text-red-600 border-red-200'
                )}
              >
                {margin > 0 ? '+' : ''}{margin.toFixed(1)}%
              </Badge>
            </div>
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <p className="max-w-xs">{description}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

export default function ValuationCard({
  ticker,
  companyName,
  currentPrice,
  valuationScore,
  valuationStatus,
  recommendation,
  confidence,
  strengthScore,
  strengthGrade,
  models,
  metrics,
  className,
}) {
  const statusConfig = STATUS_CONFIG[valuationStatus] || STATUS_CONFIG.insufficient_data;
  const StatusIcon = statusConfig.icon;
  const recConfig = RECOMMENDATION_CONFIG[recommendation] || {};
  const gradeColor = GRADE_COLORS[strengthGrade] || 'text-gray-600 bg-gray-100';

  return (
    <Card className={cn('overflow-hidden', className)} data-testid="valuation-card">
      <CardHeader className={cn('pb-2', statusConfig.bgColor)}>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Valuation Analysis
            </CardTitle>
            <CardDescription className="mt-1">
              {ticker} • {companyName}
            </CardDescription>
          </div>
          {recommendation && (
            <Badge className={cn('text-sm font-semibold', recConfig.color)}>
              {recommendation}
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-6 pt-4">
        {/* Status and Score */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <StatusIcon className={cn('h-5 w-5', statusConfig.color)} />
            <span className={cn('font-semibold', statusConfig.color)}>
              {statusConfig.label}
            </span>
          </div>
          {confidence && (
            <Badge variant="outline" className="capitalize">
              {confidence} confidence
            </Badge>
          )}
        </div>

        {/* Current Price */}
        <div className="flex items-center justify-between p-3 rounded-lg bg-primary/5">
          <div className="flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-primary" />
            <span className="text-sm font-medium">Current Price</span>
          </div>
          <span className="text-xl font-bold">${currentPrice?.toFixed(2) || 'N/A'}</span>
        </div>

        {/* Scores */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <ScoreGauge score={valuationScore} label="Valuation Score" />
          </div>
          <div className="space-y-1">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Financial Strength</span>
              <div className="flex items-center gap-2">
                <span className="font-semibold">{strengthScore?.toFixed(1) || 'N/A'}</span>
                {strengthGrade && (
                  <Badge className={cn('font-bold', gradeColor)}>
                    {strengthGrade}
                  </Badge>
                )}
              </div>
            </div>
            <Progress
              value={strengthScore || 0}
              className="h-2"
              indicatorClassName={
                strengthScore >= 65 ? 'bg-green-500' :
                strengthScore >= 50 ? 'bg-blue-500' :
                strengthScore >= 35 ? 'bg-yellow-500' : 'bg-red-500'
              }
            />
          </div>
        </div>

        {/* Fair Value Models */}
        {models && (
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-muted-foreground flex items-center gap-2">
              <Target className="h-4 w-4" />
              Fair Value Estimates
            </h4>
            <div className="space-y-2">
              <ValuationModel
                label="DCF Value"
                value={models.dcf?.dcf_value}
                currentPrice={currentPrice}
                description="Discounted Cash Flow model projects future free cash flows and discounts them to present value."
              />
              <ValuationModel
                label="Graham Number"
                value={models.graham_number?.graham_number}
                currentPrice={currentPrice}
                description="Benjamin Graham's formula: √(22.5 × EPS × Book Value). Classic value investing metric."
              />
              <ValuationModel
                label="EPV"
                value={models.epv?.epv_value}
                currentPrice={currentPrice}
                description="Earnings Power Value assumes no growth, valuing current earnings capacity at perpetuity."
              />
              <ValuationModel
                label="PEG Fair Value"
                value={models.peg_fair_value?.peg_fair_value}
                currentPrice={currentPrice}
                description="Fair value based on PEG ratio of 1, where fair P/E equals growth rate."
              />
            </div>
          </div>
        )}

        {/* Key Metrics */}
        {metrics && (
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-muted-foreground flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Key Metrics
            </h4>
            <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
              {metrics.pe_ratio && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">P/E Ratio</span>
                  <span className="font-medium">{metrics.pe_ratio.toFixed(1)}</span>
                </div>
              )}
              {metrics.price_to_book && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">P/B Ratio</span>
                  <span className="font-medium">{metrics.price_to_book.toFixed(2)}</span>
                </div>
              )}
              {metrics.roe && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">ROE</span>
                  <span className="font-medium">{metrics.roe.toFixed(1)}%</span>
                </div>
              )}
              {metrics.profit_margin && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Profit Margin</span>
                  <span className="font-medium">{metrics.profit_margin.toFixed(1)}%</span>
                </div>
              )}
              {metrics.debt_to_equity != null && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Debt/Equity</span>
                  <span className="font-medium">{metrics.debt_to_equity.toFixed(1)}%</span>
                </div>
              )}
              {metrics.current_ratio && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Current Ratio</span>
                  <span className="font-medium">{metrics.current_ratio.toFixed(2)}</span>
                </div>
              )}
              {metrics.fcf_yield && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">FCF Yield</span>
                  <span className="font-medium">{metrics.fcf_yield.toFixed(2)}%</span>
                </div>
              )}
              {metrics.dividend_yield && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Div Yield</span>
                  <span className="font-medium">{metrics.dividend_yield.toFixed(2)}%</span>
                </div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
