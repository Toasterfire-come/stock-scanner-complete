import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../../context/SecureAuthContext";
import { Loader2, AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "../../components/ui/alert";

export default function OAuthCallback() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login } = useAuth();
  const [error, setError] = useState("");
  const [isProcessing, setIsProcessing] = useState(true);

  useEffect(() => {
    const processOAuthCallback = async () => {
      try {
        const code = searchParams.get("code");
        const state = searchParams.get("state");
        const error = searchParams.get("error");

        if (error) {
          throw new Error(`OAuth error: ${error}`);
        }

        if (!code) {
          throw new Error("Authorization code not received");
        }

        // In a real app, you would send the code to your backend
        // For now, we'll simulate a successful login
        const result = await login("oauth_user", "oauth_password");
        
        if (result.success) {
          navigate("/app/dashboard");
        } else {
          throw new Error(result.error || "OAuth login failed");
        }
      } catch (err) {
        setError(err.message);
        setIsProcessing(false);
      }
    };

    processOAuthCallback();
  }, [searchParams, login, navigate]);

  if (isProcessing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
            Completing sign in...
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Please wait while we process your authentication.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="mb-4">
            {error}
          </AlertDescription>
        </Alert>
        
        <div className="text-center mt-6">
          <button
            onClick={() => navigate("/auth/sign-in")}
            className="text-blue-600 hover:text-blue-500 font-medium"
          >
            Return to sign in
          </button>
        </div>
      </div>
    </div>
  );
}