// Social Share Buttons Component - Phase 8
import React from "react";
import { Button } from "./ui/button";
import { toast } from "sonner";
import { Share2, Twitter, Facebook, Linkedin, Link2, Mail } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "./ui/dropdown-menu";

/**
 * Social Share Buttons Component
 * Allows sharing content to Twitter, Facebook, LinkedIn, Email, or copying a link
 * 
 * @param {string} title - The title of the content being shared
 * @param {string} description - A short description
 * @param {string} url - The URL to share (defaults to current page)
 * @param {string} hashtags - Comma-separated hashtags for Twitter
 * @param {boolean} showLabel - Whether to show "Share" text
 * @param {string} variant - Button variant (default, outline, ghost)
 * @param {string} size - Button size (default, sm, lg)
 */
export function SocialShareButtons({
  title = "Check this out!",
  description = "",
  url = typeof window !== "undefined" ? window.location.href : "",
  hashtags = "trading,stocks,investing",
  showLabel = true,
  variant = "outline",
  size = "default",
  className = "",
}) {
  const encodedTitle = encodeURIComponent(title);
  const encodedDescription = encodeURIComponent(description);
  const encodedUrl = encodeURIComponent(url);
  const encodedHashtags = encodeURIComponent(hashtags);

  const shareLinks = {
    twitter: `https://twitter.com/intent/tweet?text=${encodedTitle}&url=${encodedUrl}&hashtags=${encodedHashtags}`,
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}&quote=${encodedTitle}`,
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
    email: `mailto:?subject=${encodedTitle}&body=${encodedDescription}%0A%0A${encodedUrl}`,
  };

  const handleShare = (platform) => {
    if (platform === "copy") {
      navigator.clipboard.writeText(url);
      toast.success("Link copied to clipboard!");
      return;
    }
    
    const link = shareLinks[platform];
    if (link) {
      window.open(link, "_blank", "width=600,height=400,noopener,noreferrer");
    }
  };

  // Native share API for mobile
  const handleNativeShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title,
          text: description,
          url,
        });
      } catch (error) {
        if (error.name !== "AbortError") {
          console.error("Share failed:", error);
        }
      }
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant={variant} size={size} className={className} data-testid="social-share-button">
          <Share2 className="h-4 w-4" />
          {showLabel && <span className="ml-2">Share</span>}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuItem onClick={() => handleShare("twitter")} data-testid="share-twitter">
          <Twitter className="h-4 w-4 mr-2 text-[#1DA1F2]" />
          Share on Twitter
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleShare("facebook")} data-testid="share-facebook">
          <Facebook className="h-4 w-4 mr-2 text-[#4267B2]" />
          Share on Facebook
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleShare("linkedin")} data-testid="share-linkedin">
          <Linkedin className="h-4 w-4 mr-2 text-[#0A66C2]" />
          Share on LinkedIn
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => handleShare("email")} data-testid="share-email">
          <Mail className="h-4 w-4 mr-2" />
          Share via Email
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => handleShare("copy")} data-testid="share-copy">
          <Link2 className="h-4 w-4 mr-2" />
          Copy Link
        </DropdownMenuItem>
        {navigator.share && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleNativeShare} data-testid="share-native">
              <Share2 className="h-4 w-4 mr-2" />
              More Options...
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

/**
 * Inline Social Share Buttons (horizontal row)
 */
export function InlineSocialShare({
  title = "Check this out!",
  description = "",
  url = typeof window !== "undefined" ? window.location.href : "",
  hashtags = "trading,stocks,investing",
  size = "sm",
  className = "",
}) {
  const encodedTitle = encodeURIComponent(title);
  const encodedUrl = encodeURIComponent(url);
  const encodedHashtags = encodeURIComponent(hashtags);

  const share = (platform) => {
    const links = {
      twitter: `https://twitter.com/intent/tweet?text=${encodedTitle}&url=${encodedUrl}&hashtags=${encodedHashtags}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
    };
    
    if (platform === "copy") {
      navigator.clipboard.writeText(url);
      toast.success("Link copied!");
      return;
    }
    
    window.open(links[platform], "_blank", "width=600,height=400,noopener,noreferrer");
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Button
        variant="outline"
        size={size}
        onClick={() => share("twitter")}
        className="bg-[#1DA1F2]/10 hover:bg-[#1DA1F2]/20 border-[#1DA1F2]/30"
      >
        <Twitter className="h-4 w-4 text-[#1DA1F2]" />
      </Button>
      <Button
        variant="outline"
        size={size}
        onClick={() => share("facebook")}
        className="bg-[#4267B2]/10 hover:bg-[#4267B2]/20 border-[#4267B2]/30"
      >
        <Facebook className="h-4 w-4 text-[#4267B2]" />
      </Button>
      <Button
        variant="outline"
        size={size}
        onClick={() => share("linkedin")}
        className="bg-[#0A66C2]/10 hover:bg-[#0A66C2]/20 border-[#0A66C2]/30"
      >
        <Linkedin className="h-4 w-4 text-[#0A66C2]" />
      </Button>
      <Button
        variant="outline"
        size={size}
        onClick={() => share("copy")}
      >
        <Link2 className="h-4 w-4" />
      </Button>
    </div>
  );
}

export default SocialShareButtons;
