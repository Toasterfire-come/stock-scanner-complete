import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Award, X, Twitter, Linkedin, Share2 } from "lucide-react";
import { Button } from "./ui/button";
import { toast } from "sonner";

const API_BASE_URL = (process.env.REACT_APP_BACKEND_URL || "https://api.retailtradescanner.com").replace(/\/$/, "");

export default function AchievementUnlock({ achievement, onClose }) {
  const [isSharing, setIsSharing] = useState(false);

  if (!achievement) return null;

  const getRarityColor = (rarity) => {
    const colors = {
      common: "from-gray-400 to-gray-600",
      uncommon: "from-green-400 to-green-600",
      rare: "from-blue-400 to-blue-600",
      epic: "from-purple-400 to-purple-600",
      legendary: "from-yellow-400 to-orange-600"
    };
    return colors[rarity] || colors.common;
  };

  const getRarityBorder = (rarity) => {
    const colors = {
      common: "border-gray-300",
      uncommon: "border-green-300",
      rare: "border-blue-300",
      epic: "border-purple-300",
      legendary: "border-yellow-400"
    };
    return colors[rarity] || colors.common;
  };

  const shareToTwitter = () => {
    const text = `Just unlocked "${achievement.name}" on @TradeScanPro! ${achievement.icon}

${achievement.description}

Join me: ${window.location.origin}`;
    const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
    window.open(twitterUrl, "_blank", "width=550,height=420");
    markAsShared();
  };

  const shareToLinkedIn = () => {
    const url = `${window.location.origin}?achievement=${achievement.id}`;
    const linkedInUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
    window.open(linkedInUrl, "_blank", "width=550,height=420");
    markAsShared();
  };

  const copyShareText = () => {
    const text = `Just unlocked "${achievement.name}" on TradeScanPro! ${achievement.icon}

${achievement.description}

Check it out: ${window.location.origin}`;

    navigator.clipboard.writeText(text);
    toast.success("Share text copied!");
    markAsShared();
  };

  const markAsShared = async () => {
    setIsSharing(true);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/achievements/${achievement.id}/share/`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json"
          }
        }
      );

      const data = await response.json();

      if (data.new_achievement_unlocked) {
        toast.success("New achievement: Shareholder! 📤");
      }
    } catch (error) {
      console.error("Error marking achievement as shared:", error);
    } finally {
      setIsSharing(false);
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
        <motion.div
          initial={{ scale: 0, rotate: -180, opacity: 0 }}
          animate={{ scale: 1, rotate: 0, opacity: 1 }}
          exit={{ scale: 0, rotate: 180, opacity: 0 }}
          transition={{ type: "spring", duration: 0.6 }}
          className={`relative max-w-md w-full mx-4 bg-white rounded-2xl shadow-2xl overflow-hidden border-4 ${getRarityBorder(achievement.rarity)}`}
        >
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 z-10 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>

          {/* Header with gradient */}
          <div className={`bg-gradient-to-br ${getRarityColor(achievement.rarity)} text-white p-8 text-center relative overflow-hidden`}>
            {/* Animated particles */}
            <div className="absolute inset-0">
              {[...Array(20)].map((_, i) => (
                <motion.div
                  key={i}
                  className="absolute w-2 h-2 bg-white/30 rounded-full"
                  initial={{
                    x: Math.random() * 400 - 200,
                    y: 100,
                    opacity: 1
                  }}
                  animate={{
                    y: -100,
                    opacity: 0
                  }}
                  transition={{
                    duration: 2,
                    delay: i * 0.1,
                    repeat: Infinity
                  }}
                />
              ))}
            </div>

            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3, type: "spring" }}
            >
              <Award className="h-16 w-16 mx-auto mb-4" />
            </motion.div>

            <motion.h2
              className="text-2xl font-bold mb-2"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              Achievement Unlocked!
            </motion.h2>

            <motion.div
              className="text-6xl mb-2"
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.5, type: "spring" }}
            >
              {achievement.icon}
            </motion.div>

            <motion.div
              className="uppercase text-sm font-semibold opacity-90"
              initial={{ y: 10, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.6 }}
            >
              {achievement.rarity}
            </motion.div>
          </div>

          {/* Content */}
          <div className="p-6">
            <motion.h3
              className="text-2xl font-bold text-gray-900 mb-2 text-center"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.7 }}
            >
              {achievement.name}
            </motion.h3>

            <motion.p
              className="text-gray-600 text-center mb-4"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.8 }}
            >
              {achievement.description}
            </motion.p>

            <motion.div
              className="flex items-center justify-center gap-2 mb-6"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.9 }}
            >
              <div className="bg-gradient-to-br from-yellow-400 to-yellow-600 text-white px-4 py-2 rounded-full font-bold shadow-lg">
                +{achievement.points} Points
              </div>
            </motion.div>

            {/* Share buttons */}
            <motion.div
              className="space-y-3"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 1.0 }}
            >
              <p className="text-sm text-gray-500 text-center mb-3">
                Share your achievement:
              </p>

              <div className="grid grid-cols-3 gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={shareToTwitter}
                  disabled={isSharing}
                  className="hover:bg-blue-50 hover:border-blue-300"
                >
                  <Twitter className="h-4 w-4 text-blue-500" />
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={shareToLinkedIn}
                  disabled={isSharing}
                  className="hover:bg-blue-50 hover:border-blue-700"
                >
                  <Linkedin className="h-4 w-4 text-blue-700" />
                </Button>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={copyShareText}
                  disabled={isSharing}
                  className="hover:bg-gray-50"
                >
                  <Share2 className="h-4 w-4" />
                </Button>
              </div>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
