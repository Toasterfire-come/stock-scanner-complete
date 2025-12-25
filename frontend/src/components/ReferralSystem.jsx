import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Input } from "./ui/input";
import { Alert, AlertDescription } from "./ui/alert";
import { Progress } from "./ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import {
  Share2,
  Copy,
  DollarSign,
  Users,
  Gift,
  Trophy,
  TrendingUp,
  Mail,
  Twitter,
  Facebook,
  Linkedin,
  CheckCircle,
  Star,
  Target,
  Zap
} from "lucide-react";
import { toast } from "sonner";
import { getPartnerReferralSummary, getPartnerReferralTimeseries } from "../api/client";
import { useAuth } from "../context/SecureAuthContext";
import logger from '../lib/logger';

const ReferralSystem = ({ user: propUser = null, code: propCode = "" }) => {
  const { user: authUser, isAuthenticated } = useAuth();
  const resolvedUser = propUser || authUser;

  const [referralCode, setReferralCode] = useState(propCode || "");
  const [summary, setSummary] = useState(null);
  const [timeseries, setTimeseries] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const fetchData = async () => {
      if (!propUser && !isAuthenticated) {
        setIsLoading(false);
        setError("Sign in to access your referral analytics.");
        return;
      }

      setIsLoading(true);
      setError(null);
      try {
        const query = {};
        if (propCode) {
          query.code = propCode;
        }
        const [summaryRes, timeseriesRes] = await Promise.all([
          getPartnerReferralSummary(query),
          getPartnerReferralTimeseries({ ...query, interval: "day" }),
        ]);
        if (cancelled) return;
        if (!summaryRes.success) {
          throw new Error(summaryRes.error || "Unable to load referral analytics");
        }
        const summaryData = summaryRes.data || {};
        setSummary(summaryData);
        setReferralCode(summaryData.code || propCode || "");
        setTimeseries(timeseriesRes.success ? (timeseriesRes.data?.series || []) : []);
        if (!timeseriesRes.success && timeseriesRes.error) {
          logger.warn("Referral timeseries load failed:", timeseriesRes.error);
        }
      } catch (err) {
        if (cancelled) return;
        logger.error("Referral analytics error:", err);
        setSummary(null);
        setTimeseries([]);
        setError(err.message || "Unable to load referral analytics");
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      cancelled = true;
    };
  }, [propCode, isAuthenticated, resolvedUser?.id, propUser?.id]);

  const windowTotals = summary?.totals || {};
  const revenueWindow = summary?.revenue?.window || {};
  const revenueLifetime = summary?.revenue?.lifetime || {};
  const pendingCommission = summary?.revenue?.pending_commission || 0;
  const lifetimeTotals = summary?.lifetime || {};
  const recentReferrals = summary?.recent_referrals || [];
  const discountMeta = summary?.discount || null;

  const clicksWindow = windowTotals?.clicks ?? 0;
  const trialsWindow = windowTotals?.trials ?? 0;
  const purchasesWindow = windowTotals?.purchases ?? 0;
  const trialConversion = windowTotals?.trial_conversion_percent ?? 0;
  const purchaseConversion = windowTotals?.purchase_conversion_percent ?? 0;

  const toNumber = (value) => {
    const n = Number(value);
    return Number.isFinite(n) ? n : 0;
  };

  const windowRevenueAmount = toNumber(revenueWindow.total_revenue);
  const windowCommissionAmount = toNumber(revenueWindow.total_commission);
  const lifetimeRevenueAmount = toNumber(revenueLifetime.total_revenue);
  const lifetimeCommissionAmount = toNumber(revenueLifetime.total_commission);
  const lifetimeDiscountAmount = toNumber(revenueLifetime.total_discount);

  const lifetimeClicks = lifetimeTotals?.clicks ?? 0;
  const lifetimeTrials = lifetimeTotals?.trials ?? 0;
  const lifetimePurchases = lifetimeTotals?.purchases ?? 0;

  const currentTier = lifetimePurchases >= 50 ? "Platinum"
                    : lifetimePurchases >= 25 ? "Gold"
                    : lifetimePurchases >= 10 ? "Silver"
                    : "Bronze";
  const nextTierTarget = lifetimePurchases < 10 ? 10
                      : lifetimePurchases < 25 ? 25
                      : lifetimePurchases < 50 ? 50
                      : null;
  const progressToNext = nextTierTarget ? Math.min(100, (lifetimePurchases / nextTierTarget) * 100) : 100;

  const avgRevenuePerPurchase = lifetimePurchases ? lifetimeRevenueAmount / lifetimePurchases : 0;
  const avgCommissionPerPurchase = lifetimePurchases ? lifetimeCommissionAmount / lifetimePurchases : 0;

  const referralLink = referralCode ? `${process.env.REACT_APP_PUBLIC_URL || window.location.origin}/?ref=${referralCode}` : "";
  const timeseriesPreview = timeseries.slice(-7).reverse();

  const formatDate = (iso) => {
    if (!iso) return "-";
    try {
      return new Date(iso).toLocaleDateString();
    } catch {
      return iso;
    }
  };

  const formatCurrency = (value, placeholder = "$0.00") => {
    const numeric = Number(value);
    if (!Number.isFinite(numeric)) return placeholder;
    return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(numeric);
  };

  const copyReferralLink = async () => {
    if (!referralLink) {
      toast.error("Referral code is not available yet.");
      return;
    }
    try {
      if (typeof navigator !== "undefined" && navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(referralLink);
      } else if (typeof window !== "undefined") {
        const textarea = document.createElement("textarea");
        textarea.value = referralLink;
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        document.execCommand("copy");
        document.body.removeChild(textarea);
      }
      toast.success("Referral link copied!", {
        description: "Share this link to start earning commissions",
      });
    } catch (err) {
      logger.error("Copy referral link failed:", err);
      toast.error("Unable to copy referral link. You can copy it manually.");
    }
  };

  const shareViaEmail = () => {
    if (!referralLink) {
      toast.error("Referral code is not available yet.");
      return;
    }
    if (typeof window === "undefined") return;
    const subject = "Check out Trade Scan Pro - Get 50% off your first month!";
    const body = `I've been using Trade Scan Pro for my stock trading and it's amazing! \
\nUse my referral link to get 50% off your first month:\n${referralLink}\n\nFeatures I love:\n✅ Real-time stock data and alerts\n✅ Advanced portfolio analytics  \n✅ Professional screening tools\n✅ API access for custom integrations\n\nGive it a try - there's a 7-day free trial!\n\nBest regards,\n${resolvedUser?.name || resolvedUser?.username || "A fellow trader"}`;
    window.location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  };

  const shareViaSocial = (platform) => {
    if (!referralLink) {
      toast.error("Referral code is not available yet.");
      return;
    }
    if (typeof window === "undefined") return;
    const text = "Just discovered Trade Scan Pro - incredible stock trading platform! Get 50% off with my link:";
    const urls = {
      twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(referralLink)}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(referralLink)}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(referralLink)}`,
    };
    const target = urls[platform];
    if (target) {
      window.open(target, "_blank", "width=600,height=400");
    }
  };

  const tiers = [
    { name: "Bronze", referrals: "1-9", commission: "10%", badge: "🥉" },
    { name: "Silver", referrals: "10-24", commission: "15%", badge: "🥈" },
    { name: "Gold", referrals: "25-49", commission: "20%", badge: "🥇" },
    { name: "Platinum", referrals: "50+", commission: "25%", badge: "💎" },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Referral Program</h2>
        <p className="text-gray-600 text-lg">Earn up to 25% commission on every referral</p>
        {referralCode && (
          <p className="text-sm text-gray-500 mt-2">
            Your partner code: <span className="font-semibold">{referralCode}</span>
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-6 text-center">
            <Share2 className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">{clicksWindow}</p>
            <p className="text-sm text-gray-600">Tracked Clicks (30 days)</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <Users className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">{trialsWindow}</p>
            <p className="text-sm text-gray-600">Trial Signups (30 days)</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <DollarSign className="h-8 w-8 text-purple-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">{purchasesWindow}</p>
            <p className="text-sm text-gray-600">Paid Conversions (30 days)</p>
            <p className="text-xs text-gray-500 mt-1">Purchase conversion {purchaseConversion}%</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <TrendingUp className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(windowCommissionAmount)}</p>
            <p className="text-sm text-gray-600">Commission Earned (30 days)</p>
            <p className="text-xs text-gray-500 mt-1">Pending payout: {formatCurrency(pendingCommission)}</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="share" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="share">Share & Earn</TabsTrigger>
          <TabsTrigger value="stats">Performance</TabsTrigger>
          <TabsTrigger value="tiers">Tier System</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        <TabsContent value="share" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Share2 className="h-5 w-5 mr-2" />
                Your Referral Link
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex space-x-2">
                <Input
                  value={referralLink || "Referral code pending..."}
                  readOnly
                  className="flex-1"
                />
                <Button onClick={copyReferralLink} disabled={!referralLink}>
                  <Copy className="h-4 w-4 mr-2" />
                  Copy
                </Button>
              </div>

              <Alert>
                <Gift className="h-4 w-4" />
                <AlertDescription>
                  <strong>Your referrals get {discountMeta ? `${discountMeta.discount_percentage}%` : "50%"} off their first month!</strong> You earn commission on every successful signup.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Share with Friends</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Button variant="outline" className="h-20 flex-col" onClick={shareViaEmail} disabled={!referralLink}>
                  <Mail className="h-6 w-6 mb-2" />
                  Email
                </Button>

                <Button variant="outline" className="h-20 flex-col" onClick={() => shareViaSocial('twitter')} disabled={!referralLink}>
                  <Twitter className="h-6 w-6 mb-2" />
                  Twitter
                </Button>

                <Button variant="outline" className="h-20 flex-col" onClick={() => shareViaSocial('facebook')} disabled={!referralLink}>
                  <Facebook className="h-6 w-6 mb-2" />
                  Facebook
                </Button>

                <Button variant="outline" className="h-20 flex-col" onClick={() => shareViaSocial('linkedin')} disabled={!referralLink}>
                  <Linkedin className="h-6 w-6 mb-2" />
                  LinkedIn
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Maximize Your Earnings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <Target className="h-5 w-5 text-blue-600 mt-1" />
                  <div>
                    <h4 className="font-semibold">Target Active Traders</h4>
                    <p className="text-sm text-gray-600">Focus on day traders, swing traders, and investment professionals who need real-time data.</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <Star className="h-5 w-5 text-blue-600 mt-1" />
                  <div>
                    <h4 className="font-semibold">Share Your Wins</h4>
                    <p className="text-sm text-gray-600">Mention specific results you've achieved using our screeners or alerts to build trust.</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <Zap className="h-5 w-5 text-blue-600 mt-1" />
                  <div>
                    <h4 className="font-semibold">Highlight the Trial</h4>
                    <p className="text-sm text-gray-600">Emphasize the 7-day free trial with no risk and the partner discount.</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stats" className="space-y-6">
          <div className="grid lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Referral Performance</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Clicks → Trials Conversion:</span>
                  <span className="font-semibold text-blue-600">{trialConversion}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Trial → Paid Conversion:</span>
                  <span className="font-semibold text-green-600">{purchaseConversion}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Lifetime Purchases:</span>
                  <span className="font-semibold">{lifetimePurchases}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Avg. Revenue per Purchase:</span>
                  <span className="font-semibold">{formatCurrency(avgRevenuePerPurchase)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Avg. Commission per Purchase:</span>
                  <span className="font-semibold">{formatCurrency(avgCommissionPerPurchase)}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Earnings Breakdown</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Revenue (30 days):</span>
                  <span className="font-semibold">{formatCurrency(windowRevenueAmount)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Commission (30 days):</span>
                  <span className="font-semibold text-green-600">{formatCurrency(windowCommissionAmount)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Lifetime Revenue:</span>
                  <span className="font-semibold">{formatCurrency(lifetimeRevenueAmount)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Lifetime Commission Earned:</span>
                  <span className="font-semibold text-green-600">{formatCurrency(lifetimeCommissionAmount)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Discounts Given:</span>
                  <span className="font-semibold text-blue-600">{formatCurrency(lifetimeDiscountAmount)}</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {timeseriesPreview.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity (last 7 data points)</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                {timeseriesPreview.map((entry) => (
                  <div key={entry.t} className="flex flex-wrap justify-between border-b pb-2 last:border-b-0 last:pb-0">
                    <span className="font-medium text-gray-700">{formatDate(entry.t)}</span>
                    <div className="flex gap-4 text-gray-600">
                      <span>Clicks: {entry.clicks}</span>
                      <span>Trials: {entry.trials}</span>
                      <span>Purchases: {entry.purchases}</span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="tiers" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Trophy className="h-5 w-5 mr-2" />
                Current Tier: {currentTier}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {nextTierTarget && (
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span>Progress to next tier</span>
                    <span>{lifetimePurchases}/{nextTierTarget} referrals</span>
                  </div>
                  <Progress value={progressToNext} className="h-2" />
                  <p className="text-sm text-gray-600">
                    {nextTierTarget - lifetimePurchases} more referrals to reach the next tier!
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {tiers.map((tier) => (
              <Card key={tier.name} className={currentTier === tier.name ? "ring-2 ring-blue-500" : ""}>
                <CardContent className="p-6 text-center">
                  <div className="text-4xl mb-2">{tier.badge}</div>
                  <h3 className="font-bold text-lg mb-1">{tier.name}</h3>
                  <p className="text-sm text-gray-600 mb-2">{tier.referrals} referrals</p>
                  <Badge variant={currentTier === tier.name ? "default" : "secondary"}>
                    {tier.commission} commission
                  </Badge>
                  {currentTier === tier.name && (
                    <div className="mt-2">
                      <CheckCircle className="h-4 w-4 text-green-500 mx-auto" />
                      <p className="text-xs text-green-600 mt-1">Current Tier</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Tier Benefits</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>Higher commission rates with more referrals</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>Monthly bonuses for top performers</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>Priority support and dedicated partner resources</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>Exclusive marketing materials and co-branded assets</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Recent Referrals</CardTitle>
            </CardHeader>
            <CardContent>
              {recentReferrals.length === 0 ? (
                <p className="text-sm text-gray-500">No recent paid referrals yet. Share your link to get started!</p>
              ) : (
                <div className="space-y-4">
                  {recentReferrals.map((referral) => {
                    const initials = referral?.user?.name
                      ? referral.user.name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()
                      : 'REF';
                    return (
                      <div key={referral.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-4">
                          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <span className="text-blue-600 font-semibold text-sm">{initials}</span>
                          </div>
                          <div>
                            <p className="font-medium">{referral?.user?.name || 'Referral customer'}</p>
                            <p className="text-sm text-gray-600">
                              {referral.plan ? `${referral.plan} plan` : 'Plan pending'} • {formatDate(referral.payment_date)}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge variant={referral.status === 'paid' ? 'default' : 'secondary'}>
                            {referral.status || 'pending'}
                          </Badge>
                          <p className="text-sm font-medium mt-1">{formatCurrency(referral.final_amount)}</p>
                          <p className="text-xs text-gray-500">Commission: {formatCurrency(referral.commission_amount)}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Program Snapshot</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm text-gray-600">
              <div className="flex justify-between">
                <span>Total lifetime clicks</span>
                <span className="font-semibold text-gray-800">{lifetimeClicks}</span>
              </div>
              <div className="flex justify-between">
                <span>Total trial signups</span>
                <span className="font-semibold text-gray-800">{lifetimeTrials}</span>
              </div>
              <div className="flex justify-between">
                <span>Lifetime paid conversions</span>
                <span className="font-semibold text-gray-800">{lifetimePurchases}</span>
              </div>
              <div className="flex justify-between">
                <span>Lifetime commission earned</span>
                <span className="font-semibold text-gray-800">{formatCurrency(lifetimeCommissionAmount)}</span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ReferralSystem;