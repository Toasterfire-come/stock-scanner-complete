import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Award, Lock, Trophy, Target, Share2, Twitter, Linkedin } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { toast } from "sonner";

const API_BASE_URL = (process.env.REACT_APP_BACKEND_URL || "https://api.retailtradescanner.com").replace(/\/$/, "");

export default function AchievementsDisplay() {
  const [achievements, setAchievements] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all"); // all, unlocked, locked

  useEffect(() => {
    fetchAchievements();
  }, []);

  const fetchAchievements = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/achievements/`, {
        credentials: "include"
      });

      const data = await response.json();

      if (data.success) {
        setAchievements(data.achievements);
      }
    } catch (error) {
      console.error("Error fetching achievements:", error);
      toast.error("Failed to load achievements");
    } finally {
      setLoading(false);
    }
  };

  const shareAchievement = async (achievement) => {
    const text = `Just unlocked "${achievement.name}" on @TradeScanPro! ${achievement.icon}

${achievement.description}

Join me: ${window.location.origin}`;

    const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
    window.open(twitterUrl, "_blank", "width=550,height=420");

    // Mark as shared
    try {
      await fetch(`${API_BASE_URL}/api/achievements/${achievement.id}/share/`, {
        method: "POST",
        credentials: "include"
      });
    } catch (error) {
      console.error("Error marking achievement as shared:", error);
    }
  };

  const getRarityColor = (rarity) => {
    const colors = {
      common: "bg-gray-100 text-gray-700 border-gray-300",
      uncommon: "bg-green-100 text-green-700 border-green-300",
      rare: "bg-blue-100 text-blue-700 border-blue-300",
      epic: "bg-purple-100 text-purple-700 border-purple-300",
      legendary: "bg-gradient-to-r from-yellow-100 to-orange-100 text-orange-700 border-yellow-400"
    };
    return colors[rarity] || colors.common;
  };

  const getCategoryIcon = (category) => {
    const icons = {
      beginner: Target,
      social: Share2,
      quality: Award,
      performance: Trophy,
      engagement: Target,
      consistency: Award,
      legendary: Trophy
    };
    const Icon = icons[category] || Award;
    return <Icon className="h-4 w-4" />;
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading achievements...</p>
        </CardContent>
      </Card>
    );
  }

  if (!achievements) {
    return null;
  }

  const { unlocked, locked, stats } = achievements;

  const filteredAchievements = filter === "all"
    ? [...unlocked, ...locked]
    : filter === "unlocked"
    ? unlocked
    : locked;

  return (
    <div className="space-y-6">
      {/* Stats Header */}
      <Card className="border-2 border-blue-100 bg-gradient-to-r from-blue-50 to-purple-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="h-6 w-6 text-blue-600" />
            Achievement Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">{stats.total_unlocked}</div>
              <div className="text-sm text-gray-600">Unlocked</div>
            </div>

            <div className="text-center">
              <div className="text-3xl font-bold text-gray-400">{stats.total_available - stats.total_unlocked}</div>
              <div className="text-sm text-gray-600">Locked</div>
            </div>

            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-600">{stats.total_points}</div>
              <div className="text-sm text-gray-600">Points</div>
            </div>

            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">{stats.completion_percentage.toFixed(0)}%</div>
              <div className="text-sm text-gray-600">Complete</div>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>Overall Progress</span>
              <span>{stats.total_unlocked} / {stats.total_available}</span>
            </div>
            <Progress value={stats.completion_percentage} className="h-3" />
          </div>
        </CardContent>
      </Card>

      {/* Filter Tabs */}
      <div className="flex gap-2">
        <Button
          variant={filter === "all" ? "default" : "outline"}
          onClick={() => setFilter("all")}
          size="sm"
        >
          All ({unlocked.length + locked.length})
        </Button>
        <Button
          variant={filter === "unlocked" ? "default" : "outline"}
          onClick={() => setFilter("unlocked")}
          size="sm"
        >
          Unlocked ({unlocked.length})
        </Button>
        <Button
          variant={filter === "locked" ? "default" : "outline"}
          onClick={() => setFilter("locked")}
          size="sm"
        >
          Locked ({locked.length})
        </Button>
      </div>

      {/* Achievements Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredAchievements.map((achievement, index) => {
          const isUnlocked = achievement.unlocked_at !== undefined;

          return (
            <motion.div
              key={achievement.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card className={`relative overflow-hidden ${isUnlocked ? "border-2" : "border opacity-60"} ${getRarityColor(achievement.rarity)}`}>
                {/* Locked overlay */}
                {!isUnlocked && (
                  <div className="absolute inset-0 bg-gray-900/10 backdrop-blur-[2px] flex items-center justify-center z-10">
                    <Lock className="h-12 w-12 text-gray-400" />
                  </div>
                )}

                <CardContent className="p-6">
                  {/* Icon and rarity */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="text-5xl">{achievement.icon}</div>
                    <div className="flex flex-col items-end gap-1">
                      <Badge variant="outline" className="text-xs">
                        {achievement.rarity}
                      </Badge>
                      {isUnlocked && (
                        <div className="text-xs text-gray-500 flex items-center gap-1">
                          {getCategoryIcon(achievement.category)}
                          {achievement.category}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Name and description */}
                  <h3 className="font-bold text-lg mb-2">{achievement.name}</h3>
                  <p className="text-sm text-gray-600 mb-3">{achievement.description}</p>

                  {/* Points */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Award className="h-4 w-4 text-yellow-600" />
                      <span className="font-semibold text-yellow-700">{achievement.points} pts</span>
                    </div>

                    {isUnlocked && (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => shareAchievement(achievement)}
                        className="hover:bg-blue-100"
                      >
                        <Twitter className="h-4 w-4 text-blue-500" />
                      </Button>
                    )}
                  </div>

                  {/* Unlock date */}
                  {isUnlocked && achievement.unlocked_at && (
                    <div className="mt-3 pt-3 border-t text-xs text-gray-500">
                      Unlocked {new Date(achievement.unlocked_at).toLocaleDateString()}
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {filteredAchievements.length === 0 && (
        <Card>
          <CardContent className="p-8 text-center">
            <Trophy className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600">No achievements to display</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
