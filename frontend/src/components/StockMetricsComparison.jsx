import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import {
  TrendingUp,
  TrendingDown,
  Target,
  DollarSign,
  AlertCircle,
  CheckCircle,
  XCircle,
  ArrowUpRight,
  ArrowDownRight,
  Sparkles,
} from 'lucide-react';
import { cn } from '../lib/utils';

// Aesthetic gauge component
const CircularGauge = ({ value, max, label, color = 'blue', size = 120 }) => {
  const percentage = Math.min((value / max) * 100, 100);
  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-gray-200"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className={cn(
              'transition-all duration-1000 ease-out',
              color === 'green' && 'text-green-500',
              color === 'red' && 'text-red-500',
              color === 'blue' && 'text-blue-500',
              color === 'purple' && 'text-purple-500',
              color === 'amber' && 'text-amber-500'
            )}
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-2xl font-bold">{percentage.toFixed(0)}%</div>
          </div>
        </div>
      </div>
      <p className="text-sm font-medium text-center">{label}</p>
    </div>
  );
};

// Beautiful comparison card
const ComparisonMetric = ({ label, current, target, suffix = '', icon: Icon }) => {
  const diff = current - target;
  const diffPercent = ((diff / target) * 100).toFixed(1);
  const isPositive = diff >= 0;

  return (
    <div className="relative overflow-hidden rounded-lg border bg-card p-4 transition-all hover:shadow-lg">
      <div className="flex items-start justify-between">
        <div className="space-y-2 flex-1">
          <div className="flex items-center gap-2">
            {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
            <p className="text-sm font-medium text-muted-foreground">{label}</p>
          </div>
          
          <div className="space-y-1">
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold">
                {suffix === '$' ? '$' : ''}{current.toFixed(2)}{suffix !== '$' ? suffix : ''}
              </span>
            </div>
            
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">
                Target: {suffix === '$' ? '$' : ''}{target.toFixed(2)}{suffix !== '$' ? suffix : ''}
              </span>
              <Badge
                variant={isPositive ? 'success' : 'destructive'}
                className="flex items-center gap-1"
              >
                {isPositive ? (
                  <ArrowUpRight className="h-3 w-3" />
                ) : (
                  <ArrowDownRight className="h-3 w-3" />
                )}
                {isPositive ? '+' : ''}{diffPercent}%
              </Badge>
            </div>
          </div>
        </div>

        <div className="flex flex-col items-end gap-2">
          {isPositive ? (
            <CheckCircle className="h-6 w-6 text-green-500" />
          ) : (
            <AlertCircle className="h-6 w-6 text-amber-500" />
          )}
          <span className={cn(
            'text-xs font-medium px-2 py-1 rounded-full',
            isPositive ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'
          )}>
            {isPositive ? 'Above' : 'Below'}
          </span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="mt-4">
        <Progress 
          value={Math.min((current / target) * 100, 100)} 
          className="h-2"
        />
      </div>
    </div>
  );
};

export default function StockMetricsComparison({ stockData, valuationData, className }) {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    if (stockData && valuationData) {
      const currentPrice = Number(stockData.current_price || 0);
      const fairValue = Number(valuationData.fair_value_restricted?.base || valuationData.fair_value_unrestricted || 0);
      const analystTarget = Number(valuationData.analyst_target || fairValue * 1.1);
      const peRatio = Number(stockData.pe_ratio || 0);
      const sectorPE = Number(valuationData.subsector_pe_base || 15);
      
      setMetrics({
        currentPrice,
        fairValue,
        analystTarget,
        peRatio,
        sectorPE,
        upside: fairValue > 0 ? ((fairValue - currentPrice) / currentPrice * 100) : 0,
        targetUpside: analystTarget > 0 ? ((analystTarget - currentPrice) / currentPrice * 100) : 0,
      });
    }
  }, [stockData, valuationData]);

  if (!metrics) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Value Analysis</CardTitle>
          <CardDescription>Loading comparison metrics...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-48 flex items-center justify-center text-muted-foreground">
            No data available
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className={cn('space-y-6', className)}>
      {/* Hero comparison card */}
      <Card className="border-2 bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl flex items-center gap-2">
                <Sparkles className="h-6 w-6 text-purple-500" />
                Value Analysis
              </CardTitle>
              <CardDescription className="text-base mt-1">
                Current price vs Fair value comparison
              </CardDescription>
            </div>
            <Badge variant="outline" className="text-lg px-4 py-2">
              {metrics.upside >= 0 ? 'Undervalued' : 'Overvalued'}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            {/* Current Price */}
            <CircularGauge
              value={metrics.currentPrice}
              max={Math.max(metrics.currentPrice, metrics.fairValue, metrics.analystTarget)}
              label="Current Price"
              color="blue"
            />
            
            {/* Fair Value */}
            <CircularGauge
              value={metrics.fairValue}
              max={Math.max(metrics.currentPrice, metrics.fairValue, metrics.analystTarget)}
              label="Fair Value"
              color={metrics.fairValue > metrics.currentPrice ? 'green' : 'amber'}
            />
            
            {/* Analyst Target */}
            <CircularGauge
              value={metrics.analystTarget}
              max={Math.max(metrics.currentPrice, metrics.fairValue, metrics.analystTarget)}
              label="Analyst Target"
              color="purple"
            />
          </div>

          {/* Upside indicators */}
          <div className="mt-6 grid md:grid-cols-2 gap-4">
            <div className="rounded-lg border-2 border-green-200 bg-green-50 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-700">Upside to Fair Value</p>
                  <p className="text-3xl font-bold text-green-600 mt-1">
                    {metrics.upside >= 0 ? '+' : ''}{metrics.upside.toFixed(1)}%
                  </p>
                </div>
                <TrendingUp className="h-12 w-12 text-green-500 opacity-50" />
              </div>
            </div>

            <div className="rounded-lg border-2 border-purple-200 bg-purple-50 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-purple-700">Upside to Target</p>
                  <p className="text-3xl font-bold text-purple-600 mt-1">
                    {metrics.targetUpside >= 0 ? '+' : ''}{metrics.targetUpside.toFixed(1)}%
                  </p>
                </div>
                <Target className="h-12 w-12 text-purple-500 opacity-50" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detailed comparisons */}
      <div className="grid md:grid-cols-2 gap-4">
        <ComparisonMetric
          label="Stock Price"
          current={metrics.currentPrice}
          target={metrics.fairValue}
          suffix="$"
          icon={DollarSign}
        />
        
        <ComparisonMetric
          label="P/E Ratio"
          current={metrics.peRatio}
          target={metrics.sectorPE}
          suffix="x"
          icon={Target}
        />
      </div>

      {/* Investment signal */}
      <Card className={cn(
        'border-2',
        metrics.upside > 20 ? 'border-green-500 bg-green-50' :
        metrics.upside > 0 ? 'border-blue-500 bg-blue-50' :
        metrics.upside > -20 ? 'border-amber-500 bg-amber-50' :
        'border-red-500 bg-red-50'
      )}>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            {metrics.upside > 20 ? (
              <CheckCircle className="h-12 w-12 text-green-600" />
            ) : metrics.upside > 0 ? (
              <AlertCircle className="h-12 w-12 text-blue-600" />
            ) : (
              <XCircle className="h-12 w-12 text-amber-600" />
            )}
            
            <div className="flex-1">
              <h3 className="text-xl font-bold">
                {metrics.upside > 20 ? 'Strong Buy Signal' :
                 metrics.upside > 0 ? 'Buy Signal' :
                 metrics.upside > -20 ? 'Hold Signal' :
                 'Caution Signal'}
              </h3>
              <p className="text-sm text-muted-foreground mt-1">
                {metrics.upside > 20 ? 'Stock appears significantly undervalued based on fundamental analysis' :
                 metrics.upside > 0 ? 'Stock shows potential upside to fair value' :
                 metrics.upside > -20 ? 'Stock is trading near fair value' :
                 'Stock appears overvalued, proceed with caution'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
