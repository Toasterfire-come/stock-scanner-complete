import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Alert, AlertDescription } from "../../components/ui/alert";
import { Avatar, AvatarFallback, AvatarImage } from "../../components/ui/avatar";
import {
  User,
  Calendar,
  Trophy,
  Target,
  TrendingUp,
  List,
  Briefcase,
  LineChart,
  Loader2,
  AlertCircle,
  Share2,
  Star,
  Eye,
  Copy,
} from "lucide-react";
import { toast } from "sonner";
import { api } from "../../api/client";
import SEO from "../../components/SEO";

export default function PublicProfile() {
  const { username } = useParams();
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    loadProfile();
  }, [username]);

  const loadProfile = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const { data } = await api.get(`/user/public/${encodeURIComponent(username)}/`);
      if (data?.success) {
        setProfile(data.profile || data.data);
      } else {
        setError(data?.message || "Profile not found");
      }
    } catch (err) {
      setError("User not found or profile is private");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <Loader2 className="h-12 w-12 mx-auto animate-spin text-blue-500 mb-4" />
        <p className="text-gray-500">Loading profile...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-12 max-w-2xl">
        <SEO title="Profile Not Found | Trade Scan Pro" robots="noindex" />
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
        <div className="text-center mt-6">
          <Link to="/">
            <Button>Go to Homepage</Button>
          </Link>
        </div>
      </div>
    );
  }

  const initials = profile?.username?.slice(0, 2).toUpperCase() || "?";

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl" data-testid="public-profile-page">
      <SEO 
        title={`${profile?.username || "User"}'s Profile | Trade Scan Pro`}
        description={`View ${profile?.username}'s trading profile and public portfolios`}
      />

      {/* Profile Header */}
      <Card className="mb-8 bg-gradient-to-r from-blue-50 to-purple-50 border-0">
        <CardContent className="p-8">
          <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
            <Avatar className="h-24 w-24 border-4 border-white shadow-lg">
              <AvatarImage src={profile?.avatar_url} />
              <AvatarFallback className="text-2xl font-bold bg-blue-500 text-white">
                {initials}
              </AvatarFallback>
            </Avatar>

            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900">{profile?.username}</h1>
              {profile?.bio && (
                <p className="text-gray-600 mt-2 max-w-2xl">{profile.bio}</p>
              )}
              <div className="flex flex-wrap items-center gap-3 mt-4">
                {profile?.plan && (
                  <Badge variant="outline" className="bg-white">
                    <Star className="h-3 w-3 mr-1 text-yellow-500" />
                    {profile.plan} Plan
                  </Badge>
                )}
                {profile?.joined_date && (
                  <span className="text-sm text-gray-500 flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    Joined {new Date(profile.joined_date).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="p-3 bg-blue-100 rounded-full w-fit mx-auto mb-2">
              <List className="h-5 w-5 text-blue-600" />
            </div>
            <p className="text-2xl font-bold">{profile?.public_watchlists || 0}</p>
            <p className="text-sm text-gray-500">Watchlists</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="p-3 bg-green-100 rounded-full w-fit mx-auto mb-2">
              <Briefcase className="h-5 w-5 text-green-600" />
            </div>
            <p className="text-2xl font-bold">{profile?.public_portfolios || 0}</p>
            <p className="text-sm text-gray-500">Portfolios</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="p-3 bg-purple-100 rounded-full w-fit mx-auto mb-2">
              <LineChart className="h-5 w-5 text-purple-600" />
            </div>
            <p className="text-2xl font-bold">{profile?.backtests || 0}</p>
            <p className="text-sm text-gray-500">Backtests</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="p-3 bg-orange-100 rounded-full w-fit mx-auto mb-2">
              <Eye className="h-5 w-5 text-orange-600" />
            </div>
            <p className="text-2xl font-bold">{profile?.profile_views || 0}</p>
            <p className="text-sm text-gray-500">Profile Views</p>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="watchlists">Watchlists</TabsTrigger>
          <TabsTrigger value="portfolios">Portfolios</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Trading Style */}
            {profile?.trading_style && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Trading Style</CardTitle>
                </CardHeader>
                <CardContent>
                  <Badge variant="outline" className="text-base">
                    {profile.trading_style}
                  </Badge>
                </CardContent>
              </Card>
            )}

            {/* Top Holdings */}
            {profile?.top_holdings?.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Top Holdings</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {profile.top_holdings.map((symbol) => (
                      <Badge key={symbol} variant="secondary">
                        {symbol}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="watchlists">
          {profile?.watchlists?.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {profile.watchlists.map((wl) => (
                <Card key={wl.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold">{wl.name}</h3>
                        <p className="text-sm text-gray-500">{wl.stock_count || 0} stocks</p>
                      </div>
                      <Link to={`/w/${wl.share_slug}`}>
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-1" />
                          View
                        </Button>
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-8 text-center">
              <List className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500">No public watchlists</p>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="portfolios">
          {profile?.portfolios?.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2">
              {profile.portfolios.map((pf) => (
                <Card key={pf.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold">{pf.name}</h3>
                        <p className="text-sm text-gray-500">
                          {pf.holdings_count || 0} holdings
                          {pf.total_return && (
                            <span className={pf.total_return >= 0 ? "text-green-600" : "text-red-600"}>
                              {" "}({pf.total_return >= 0 ? "+" : ""}{pf.total_return.toFixed(1)}%)
                            </span>
                          )}
                        </p>
                      </div>
                      <Link to={`/p/${pf.share_slug}`}>
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-1" />
                          View
                        </Button>
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-8 text-center">
              <Briefcase className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500">No public portfolios</p>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* CTA */}
      <div className="mt-8 text-center">
        <p className="text-gray-600 mb-4">Create your own trading profile</p>
        <Link to="/auth/sign-up">
          <Button size="lg">Get Started Free</Button>
        </Link>
      </div>
    </div>
  );
}
