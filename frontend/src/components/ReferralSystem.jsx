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
  MessageSquare,
  Twitter,
  Facebook,
  Linkedin,
  CheckCircle,
  Star,
  Target,
  Zap
} from "lucide-react";
import { toast } from "sonner";

const ReferralSystem = ({ user, referralCode: referralCodeProp }) => {
  const [referralCode, setReferralCode] = useState("");
  const [referralStats, setReferralStats] = useState({
    totalReferrals: 0,
    activeReferrals: 0,
    totalEarnings: 0,
    pendingEarnings: 0,
    conversionRate: 0,
    lifetimeValue: 0
  });
  const [recentReferrals, setRecentReferrals] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initializeReferral = async () => {
      try {
        // Prefer provided referral code when available; fall back to generated
        if (referralCodeProp && typeof referralCodeProp === 'string') {
          setReferralCode(referralCodeProp.toUpperCase());
        } else {
          const code = `REF${user?.id || '123'}${Math.random().toString(36).substr(2, 4).toUpperCase()}`;
          setReferralCode(code);
        }
        
        // Mock data - replace with real API calls
        setReferralStats({
          totalReferrals: 23,
          activeReferrals: 18,
          totalEarnings: 1247.50,
          pendingEarnings: 385.20,
          conversionRate: 78.3,
          lifetimeValue: 2847.30
        });

        setRecentReferrals([
          { name: "John D.", plan: "Silver", status: "active", date: "2024-01-15", earnings: 39.99 },
          { name: "Sarah M.", plan: "Gold", status: "active", date: "2024-01-12", earnings: 89.99 },
          { name: "Mike R.", plan: "Bronze", status: "trial", date: "2024-01-10", earnings: 0 },
          { name: "Lisa K.", plan: "Silver", status: "active", date: "2024-01-08", earnings: 39.99 },
        ]);
      } catch (error) {
        console.error("Failed to initialize referral system:", error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeReferral();
  }, [user, referralCodeProp]);

  const copyReferralLink = () => {
    const referralLink = `https://tradescanpro.com/?ref=${referralCode}`;
    navigator.clipboard.writeText(referralLink);
    toast.success("Referral link copied!", {
      description: "Share this link to start earning commissions"
    });
  };

  const shareViaEmail = () => {
    const subject = "Check out Trade Scan Pro - Get 50% off your first month!";
    const body = `I've been using Trade Scan Pro for my stock trading and it's amazing! 

Use my referral link to get 50% off your first month:
https://tradescanpro.com/?ref=${referralCode}

Features I love:
✅ Real-time stock data and alerts
✅ Advanced portfolio analytics  
✅ Professional screening tools
✅ API access for custom integrations

Give it a try - there's a 7-day free trial!

Best regards,
${user?.name || 'Your friend'}`;
    
    window.location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  };

  const shareViaSocial = (platform) => {
    const text = "Just discovered Trade Scan Pro - incredible stock trading platform! Get 50% off with my link:";
    const url = `https://tradescanpro.com/?ref=${referralCode}`;
    
    const urls = {
      twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`
    };
    
    window.open(urls[platform], '_blank', 'width=600,height=400');
  };

  const tiers = [
    { name: "Bronze", referrals: "1-9", commission: "10%", badge: "🥉" },
    { name: "Silver", referrals: "10-24", commission: "15%", badge: "🥈" },
    { name: "Gold", referrals: "25-49", commission: "20%", badge: "🥇" },
    { name: "Platinum", referrals: "50+", commission: "25%", badge: "💎" }
  ];

  const currentTier = referralStats.totalReferrals >= 50 ? "Platinum" : 
                     referralStats.totalReferrals >= 25 ? "Gold" :
                     referralStats.totalReferrals >= 10 ? "Silver" : "Bronze";

  const nextTierTarget = referralStats.totalReferrals < 10 ? 10 :
                        referralStats.totalReferrals < 25 ? 25 :
                        referralStats.totalReferrals < 50 ? 50 : null;

  const progressToNext = nextTierTarget ? (referralStats.totalReferrals / nextTierTarget) * 100 : 100;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Referral Program</h2>
        <p className="text-gray-600 text-lg">Earn up to 25% commission on every referral</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-6 text-center">
            <Users className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">{referralStats.totalReferrals}</p>
            <p className="text-sm text-gray-600">Total Referrals</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <DollarSign className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">${referralStats.totalEarnings}</p>
            <p className="text-sm text-gray-600">Total Earnings</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <TrendingUp className="h-8 w-8 text-purple-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">{referralStats.conversionRate}%</p>
            <p className="text-sm text-gray-600">Conversion Rate</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6 text-center">
            <Trophy className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-gray-900">${referralStats.pendingEarnings}</p>
            <p className="text-sm text-gray-600">Pending Payout</p>
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
          {/* Referral Link */}
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
                  value={`https://tradescanpro.com/?ref=${referralCode}`}
                  readOnly
                  className="flex-1"
                />
                <Button onClick={copyReferralLink}>
                  <Copy className="h-4 w-4 mr-2" />
                  Copy
                </Button>
              </div>
              
              <Alert>
                <Gift className="h-4 w-4" />
                <AlertDescription>
                  <strong>Your referrals get 50% off their first month!</strong> You earn commission on every successful signup.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>

          {/* Sharing Options */}
          <Card>
            <CardHeader>
              <CardTitle>Share with Friends</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Button variant="outline" className="h-20 flex-col" onClick={shareViaEmail}>
                  <Mail className="h-6 w-6 mb-2" />
                  Email
                </Button>
                
                <Button variant="outline" className="h-20 flex-col" onClick={() => shareViaSocial('twitter')}>
                  <Twitter className="h-6 w-6 mb-2" />
                  Twitter
                </Button>
                
                <Button variant="outline" className="h-20 flex-col" onClick={() => shareViaSocial('facebook')}>
                  <Facebook className="h-6 w-6 mb-2" />
                  Facebook
                </Button>
                
                <Button variant="outline" className="h-20 flex-col" onClick={() => shareViaSocial('linkedin')}>
                  <Linkedin className="h-6 w-6 mb-2" />
                  LinkedIn
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Tips for Success */}
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
                    <h4 className="font-semibold">Share Success Stories</h4>
                    <p className="text-sm text-gray-600">Mention specific wins you've had using our alerts or screening tools.</p>
                  </div>
                </div>
                
                <div className="flex items-start space-x-3">
                  <Zap className="h-5 w-5 text-blue-600 mt-1" />
                  <div>
                    <h4 className="font-semibold">Highlight Free Trial</h4>
                    <p className="text-sm text-gray-600">Emphasize the 7-day free trial with no credit card required.</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stats" className="space-y-6">
          {/* Performance Metrics */}
          <div className="grid lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Referral Performance</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Active Referrals:</span>
                  <span className="font-semibold">{referralStats.activeReferrals}/{referralStats.totalReferrals}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Conversion Rate:</span>
                  <span className="font-semibold text-green-600">{referralStats.conversionRate}%</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Avg. Customer Value:</span>
                  <span className="font-semibold">${(referralStats.lifetimeValue / referralStats.totalReferrals).toFixed(2)}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Monthly Recurring:</span>
                  <span className="font-semibold">${(referralStats.totalEarnings * 0.7).toFixed(2)}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Earnings Breakdown</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Bronze Plan Commissions:</span>
                    <span className="font-semibold">$247.50</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Silver Plan Commissions:</span>
                    <span className="font-semibold">$599.70</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Gold Plan Commissions:</span>
                    <span className="font-semibold">$400.30</span>
                  </div>
                  <hr />
                  <div className="flex justify-between font-bold">
                    <span>Total Paid:</span>
                    <span className="text-green-600">${referralStats.totalEarnings}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Pending:</span>
                    <span className="text-yellow-600">${referralStats.pendingEarnings}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="tiers" className="space-y-6">
          {/* Current Tier Status */}
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
                    <span>{referralStats.totalReferrals}/{nextTierTarget} referrals</span>
                  </div>
                  <Progress value={progressToNext} className="h-2" />
                  <p className="text-sm text-gray-600">
                    {nextTierTarget - referralStats.totalReferrals} more referrals to reach the next tier!
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Tier System */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {tiers.map((tier, index) => (
              <Card key={tier.name} className={currentTier === tier.name ? 'ring-2 ring-blue-500' : ''}>
                <CardContent className="p-6 text-center">
                  <div className="text-4xl mb-2">{tier.badge}</div>
                  <h3 className="font-bold text-lg mb-1">{tier.name}</h3>
                  <p className="text-sm text-gray-600 mb-2">{tier.referrals} referrals</p>
                  <Badge variant={currentTier === tier.name ? 'default' : 'secondary'}>
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

          {/* Tier Benefits */}
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
                  <span>Priority support and dedicated account manager</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>Exclusive marketing materials and tools ('Gold' tier+)</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="space-y-6">
          {/* Recent Referrals */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Referrals</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentReferrals.map((referral, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-blue-600 font-semibold text-sm">
                          {referral.name.split(' ').map(n => n[0]).join('')}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium">{referral.name}</p>
                        <p className="text-sm text-gray-600">{referral.plan} plan • {referral.date}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant={referral.status === 'active' ? 'default' : 'secondary'}>
                        {referral.status}
                      </Badge>
                      <p className="text-sm font-medium mt-1">
                        {referral.earnings > 0 ? `$${referral.earnings}` : 'Pending'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Payout History */}
          <Card>
            <CardHeader>
              <CardTitle>Payout History</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <div>
                    <p className="font-medium">January 2024 Payout</p>
                    <p className="text-sm text-gray-600">Paid via PayPal</p>
                  </div>
                  <span className="font-bold text-green-600">$425.30</span>
                </div>
                
                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <div>
                    <p className="font-medium">December 2023 Payout</p>
                    <p className="text-sm text-gray-600">Paid via PayPal</p>
                  </div>
                  <span className="font-bold text-green-600">$387.75</span>
                </div>
                
                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <div>
                    <p className="font-medium">November 2023 Payout</p>
                    <p className="text-sm text-gray-600">Paid via PayPal</p>
                  </div>
                  <span className="font-bold text-green-600">$434.45</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ReferralSystem;