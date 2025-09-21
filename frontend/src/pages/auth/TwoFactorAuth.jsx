import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Alert, AlertDescription } from "../../components/ui/alert";
import { toast } from "sonner";
import { api } from "../../api/client";
import { Shield, RefreshCw } from "lucide-react";

const twoFactorSchema = z.object({
  code: z.string().min(6, "Verification code must be 6 digits").max(6, "Verification code must be 6 digits"),
});

const TwoFactorAuth = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const email = location.state?.email || "your email";
  const from = location.state?.from?.pathname || "/app/dashboard";

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(twoFactorSchema),
  });

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      const res = await api.post('/auth/verify-2fa/', { code: data.code, email });
      if (res?.data?.success) {
        toast.success("Two-factor authentication successful!");
        navigate(from, { replace: true });
      } else {
        toast.error(res?.data?.message || "Invalid verification code. Please try again.");
      }
    } catch (error) {
      toast.error("Verification failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const resendCode = async () => {
    setIsResending(true);
    try {
      const res = await api.post('/auth/resend-2fa/', { email });
      if (res?.data?.success) {
        toast.success("New verification code sent!");
      } else {
        toast.error(res?.data?.message || "Failed to send verification code.");
      }
    } catch (error) {
      toast.error("Failed to send verification code. Please try again.");
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="flex justify-center mb-4">
          <Shield className="h-12 w-12 text-blue-500" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900">Two-Factor Authentication</h2>
        <p className="text-gray-600 mt-2">
          Enter the 6-digit verification code sent to {email}
        </p>
      </div>

      

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="code">Verification Code</Label>
          <Input
            id="code"
            type="text"
            placeholder="000000"
            className="text-center text-2xl tracking-widest"
            maxLength={6}
            {...register("code")}
          />
          {errors.code && (
            <p className="text-sm text-red-600">{errors.code.message}</p>
          )}
        </div>

        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? "Verifying..." : "Verify Code"}
        </Button>
      </form>

      <div className="text-center space-y-4">
        <p className="text-sm text-gray-600">
          Didn't receive the code?
        </p>
        
        <Button 
          variant="outline" 
          onClick={resendCode}
          disabled={isResending}
          className="w-full"
        >
          {isResending ? (
            <>
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              Sending new code...
            </>
          ) : (
            <>
              <RefreshCw className="h-4 w-4 mr-2" />
              Resend code
            </>
          )}
        </Button>

        <p className="text-sm text-gray-600">
          Having trouble?{" "}
          <Link
            to="/auth/sign-in"
            className="text-blue-600 hover:text-blue-500 font-medium"
          >
            Back to Sign In
          </Link>
        </p>
      </div>
    </div>
  );
};

export default TwoFactorAuth;