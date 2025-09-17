import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "../../components/ui/button";
import { useAuth } from "../../context/SecureAuthContext";
import { Alert, AlertDescription } from "../../components/ui/alert";
import { toast } from "sonner";
import { Mail, CheckCircle, RefreshCw } from "lucide-react";

const VerifyEmail = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const { updateUser } = useAuth();
  const [isVerified, setIsVerified] = useState(false);
  const email = location.state?.email || "your email";

  useEffect(() => {
    // Check URL for verification token
    const urlParams = new URLSearchParams(location.search);
    const token = urlParams.get("token");
    
    if (token) {
      verifyEmailWithToken(token);
    }
  }, [location.search]);

  const verifyEmailWithToken = async (token) => {
    setIsLoading(true);
    try {
      // Simulate email verification API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setIsVerified(true);
      toast.success("Email verified successfully!");
      
      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate("/auth/sign-in");
      }, 3000);
    } catch (error) {
      toast.error("Email verification failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const resendVerificationEmail = async () => {
    setIsLoading(true);
    try {
      // Simulate resend verification email API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast.success("Verification email sent!");
    } catch (error) {
      toast.error("Failed to send verification email. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  if (isVerified) {
    return (
      <div className="space-y-6 text-center">
        <div className="flex justify-center">
          <CheckCircle className="h-16 w-16 text-green-500" />
        </div>
        
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Email verified!</h2>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Your email has been successfully verified. You can now sign in to your account.
          </p>
        </div>

        <Button asChild className="w-full">
          <Link to="/auth/sign-in">Continue to Sign In</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 text-center">
      <div className="flex justify-center">
        <Mail className="h-16 w-16 text-blue-500" />
      </div>
      
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Verify your email</h2>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          We've sent a verification link to{" "}
          <span className="font-medium">{email}</span>
        </p>
      </div>

      <Alert>
        <AlertDescription>
          Click the link in the email to verify your account. 
          If you don't see the email, check your spam folder.
        </AlertDescription>
      </Alert>

      <div className="space-y-4">
        <Button 
          onClick={resendVerificationEmail} 
          variant="outline" 
          className="w-full"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              Sending...
            </>
          ) : (
            <>
              <RefreshCw className="h-4 w-4 mr-2" />
              Resend verification email
            </>
          )}
        </Button>
        
        <div className="flex flex-col space-y-2">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Wrong email address?{" "}
            <Link
              to="/auth/sign-up"
              className="text-blue-600 hover:text-blue-500 font-medium"
            >
              Update it
            </Link>
          </p>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
            <Button asChild size="sm" variant="secondary">
              <Link to="/pricing">See Paid Plans</Link>
            </Button>
            <Button 
              size="sm"
              onClick={() => {
                updateUser({ plan: 'free' });
                navigate('/app/dashboard');
              }}
            >
              Continue on Free
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VerifyEmail;