import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { api } from "../../api/client";
import { toast } from "sonner";
import { CheckCircle, AlertTriangle } from "lucide-react";

const OAuthCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [status, setStatus] = useState("processing"); // processing, success, error

  useEffect(() => {
    const handleOAuthCallback = async () => {
      const code = searchParams.get("code");
      const error = searchParams.get("error");
      const state = searchParams.get("state");

      if (error) {
        setStatus("error");
        toast.error("OAuth authentication failed");
        setTimeout(() => navigate("/auth/sign-in"), 3000);
        return;
      }

      if (!code) {
        setStatus("error");
        toast.error("Invalid OAuth callback");
        setTimeout(() => navigate("/auth/sign-in"), 3000);
        return;
      }

      try {
        const { data: res } = await api.post('/auth/oauth/callback/', { code, state });
        if (res?.success && res?.token) {
          localStorage.setItem('rts_token', res.token);
          setStatus('success');
          toast.success('Successfully signed in!');
          setTimeout(() => navigate('/app/dashboard'), 1500);
        } else {
          throw new Error('OAuth exchange failed');
        }
      } catch (error) {
        console.error("OAuth callback error:", error);
        setStatus("error");
        toast.error("Authentication failed");
        setTimeout(() => navigate("/auth/sign-in"), 3000);
      }
    };

    handleOAuthCallback();
  }, [searchParams, navigate, login]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50 flex items-center justify-center p-4">
      <div className="w-full max-w-md text-center space-y-6">
        <div className="bg-white rounded-lg shadow-lg p-8">
          {status === "processing" && (
            <>
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Completing sign in...
              </h2>
              <p className="text-gray-600">
                Please wait while we verify your account.
              </p>
            </>
          )}

          {status === "success" && (
            <>
              <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Sign in successful!
              </h2>
              <p className="text-gray-600">
                Redirecting you to your dashboard...
              </p>
            </>
          )}

          {status === "error" && (
            <>
              <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Authentication failed
              </h2>
              <p className="text-gray-600">
                There was an error signing you in. Redirecting back to sign in page...
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default OAuthCallback;