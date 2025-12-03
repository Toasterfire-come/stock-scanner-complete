import React, { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Badge } from "./ui/badge";
import { toast } from "sonner";
import {
  Share2,
  Copy,
  Check,
  Twitter,
  Facebook,
  Linkedin,
  Mail,
  Link as LinkIcon,
  Globe,
  Lock,
  Users,
} from "lucide-react";

const ShareDialog = ({ 
  type = "watchlist", // watchlist, portfolio, backtest, chart
  title,
  shareUrl,
  onCreateShareLink,
  isPublic = false,
  trigger,
}) => {
  const [copied, setCopied] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [generatedUrl, setGeneratedUrl] = useState(shareUrl || "");

  const baseUrl = typeof window !== "undefined" ? window.location.origin : "";
  const fullUrl = generatedUrl ? `${baseUrl}${generatedUrl}` : "";

  const handleCreateLink = async () => {
    if (!onCreateShareLink) return;
    setIsCreating(true);
    try {
      const result = await onCreateShareLink();
      if (result?.success && result?.share_url) {
        setGeneratedUrl(result.share_url);
        toast.success("Share link created!");
      } else {
        toast.error(result?.message || "Failed to create share link");
      }
    } catch (error) {
      toast.error("Failed to create share link");
    } finally {
      setIsCreating(false);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(fullUrl);
      setCopied(true);
      toast.success("Link copied to clipboard!");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error("Failed to copy link");
    }
  };

  const shareToSocial = (platform) => {
    const text = `Check out my ${type}: ${title}`;
    const encodedUrl = encodeURIComponent(fullUrl);
    const encodedText = encodeURIComponent(text);

    const urls = {
      twitter: `https://twitter.com/intent/tweet?text=${encodedText}&url=${encodedUrl}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
      email: `mailto:?subject=${encodedText}&body=${encodedUrl}`,
    };

    if (urls[platform]) {
      window.open(urls[platform], "_blank", "width=600,height=400");
    }
  };

  const typeLabels = {
    watchlist: "Watchlist",
    portfolio: "Portfolio",
    backtest: "Backtest Results",
    chart: "Chart Analysis",
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline" size="sm" className="gap-2">
            <Share2 className="h-4 w-4" />
            Share
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Share2 className="h-5 w-5 text-blue-500" />
            Share {typeLabels[type]}
          </DialogTitle>
          <DialogDescription>
            Share "{title}" with others
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Privacy Badge */}
          <div className="flex items-center gap-2">
            <Badge variant="outline" className={isPublic ? "bg-green-50" : "bg-gray-50"}>
              {isPublic ? (
                <><Globe className="h-3 w-3 mr-1" /> Public</>
              ) : (
                <><Lock className="h-3 w-3 mr-1" /> Private</>
              )}
            </Badge>
            <span className="text-sm text-gray-500">
              {isPublic ? "Anyone with the link can view" : "Only you can view"}
            </span>
          </div>

          {/* Generate Link Section */}
          {!generatedUrl && onCreateShareLink && (
            <div className="text-center py-4">
              <Button
                onClick={handleCreateLink}
                disabled={isCreating}
                className="gap-2"
              >
                <LinkIcon className="h-4 w-4" />
                {isCreating ? "Creating..." : "Generate Share Link"}
              </Button>
            </div>
          )}

          {/* Share URL */}
          {generatedUrl && (
            <>
              <div className="flex gap-2">
                <Input
                  value={fullUrl}
                  readOnly
                  className="bg-gray-50"
                />
                <Button
                  variant="outline"
                  size="icon"
                  onClick={handleCopy}
                  className="shrink-0"
                >
                  {copied ? (
                    <Check className="h-4 w-4 text-green-500" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>

              {/* Social Share Buttons */}
              <div className="space-y-3">
                <p className="text-sm font-medium text-gray-700">Share on social media</p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => shareToSocial("twitter")}
                    className="bg-[#1DA1F2] hover:bg-[#1a8cd8] text-white border-0"
                  >
                    <Twitter className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => shareToSocial("facebook")}
                    className="bg-[#4267B2] hover:bg-[#365899] text-white border-0"
                  >
                    <Facebook className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => shareToSocial("linkedin")}
                    className="bg-[#0077B5] hover:bg-[#006399] text-white border-0"
                  >
                    <Linkedin className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => shareToSocial("email")}
                    className="bg-gray-600 hover:bg-gray-700 text-white border-0"
                  >
                    <Mail className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ShareDialog;
