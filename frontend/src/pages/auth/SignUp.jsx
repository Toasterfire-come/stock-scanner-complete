import React, { useState, useRef, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Separator } from "../../components/ui/separator";
import { Checkbox } from "../../components/ui/checkbox";
import { toast } from "sonner";
import { Eye, EyeOff, Mail, Lock, User } from "lucide-react";
import { registerUser } from "../../api/client";
import OneTapGoogle from "../../components/OneTapGoogle";
import { setReferralCookie, normalizeReferralCode } from "../../lib/referral";
import { useAuth } from "../../context/SecureAuthContext";

// Friction-reduced: name + email + password; keep Google SSO. Username optional (derived), last name optional.
const signUpSchema = z.object({
  username: z
    .string()
    .max(20, "Username must be less than 20 characters")
    .regex(/^[a-zA-Z0-9_]*$/, "Username can only contain letters, numbers, and underscores"),
  email: z.string().email("Please enter a valid email address"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters"),
  confirmPassword: z.string(),
  firstName: z.string().min(1, "First name is required"),
  lastName: z.string().optional(),
  agreeToTerms: z.boolean().refine((val) => val === true, "You must agree to the terms and conditions"),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

const SignUp = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(signUpSchema),
  });

  const agreeToTerms = watch("agreeToTerms");
  const emailValue = watch("email");
  const usernameValue = watch("username");
  const [usernameTouched, setUsernameTouched] = useState(false);
  const lastDerivedRef = useRef("");

  // Prefill email/username from navigation state (inline capture flow)
  React.useEffect(() => {
    try {
      const st = location.state || {};
      // Accept discountCode propagated from pricing/plan pages
      if (st.discountCode && typeof st.discountCode === 'string') {
        try {
          const params = new URLSearchParams(location.search || '');
          if (!params.get('ref')) {
            const ref = String(st.discountCode).replace(/^REF_/, '');
            const url = new URL(window.location.href);
            url.searchParams.set('ref', ref);
            window.history.replaceState({}, '', url.toString());
          }
          try { setReferralCookie(st.discountCode); } catch {}
        } catch {}
      }
      if (st.emailPrefill && typeof st.emailPrefill === 'string') {
        setValue('email', st.emailPrefill);
        // Suggest username from email local-part if empty
        const local = st.emailPrefill.split('@')[0] || '';
        const derived = local.replace(/[^a-zA-Z0-9_]/g, '');
        if (derived && !watch('username')) {
          setValue('username', derived);
          lastDerivedRef.current = derived;
        }
      }
    } catch {}
  }, [location.state]);

  // Auto-suggest username from email while user hasn't edited username
  useEffect(() => {
    try {
      if (usernameTouched) return;
      const local = (emailValue || '').split('@')[0] || '';
      const derived = local.replace(/[^a-zA-Z0-9_]/g, '');
      const shouldUpdate = !usernameValue || usernameValue === lastDerivedRef.current;
      if (derived && shouldUpdate) {
        setValue('username', derived);
        lastDerivedRef.current = derived;
      }
    } catch {}
  }, [emailValue, usernameValue, usernameTouched, setValue]);

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      // Capture referral from URL path or query: /auth/sign-up/ref-abc12 or ?ref=abc12
      let refCode = null;
      try {
        const path = location.pathname || '';
        const m = path.match(/\/auth\/sign-up\/ref-([A-Za-z0-9_-]{5,32})/);
        if (m && m[1]) refCode = m[1];
        const params = new URLSearchParams(location.search || '');
        const qRef = params.get('ref');
        if (!refCode && qRef) {
          const trimmed = String(qRef).trim().slice(0, 32);
          if (/^[A-Za-z0-9_\-]{5,32}$/.test(trimmed)) refCode = trimmed;
        }
      } catch {}

      // Persist referral cookie when present
      try {
        if (refCode) setReferralCookie(normalizeReferralCode(refCode));
      } catch {}

      // Create account
      const result = await registerUser({
        username: data.username,
        email: data.email,
        password: data.password,
        first_name: data.firstName,
        last_name: data.lastName,
        ref: refCode || undefined,
      });

      if (result.success) {
        // Auto sign-in by setting backend session via redirect if available, else proceed locally
        try {
          const backend = (process.env.REACT_APP_BACKEND_URL || '').replace(/\/$/, '');
          if (backend) {
            // Optional session warm-up (non-blocking)
            fetch(`${backend}/auth/session/warmup`, { method: 'POST', credentials: 'include' }).catch(() => {});
          }
        } catch {}

        // Ensure client session is authenticated
        try {
          await login(data.email, data.password);
        } catch {}

        toast.success("Account created! Choose your plan.");
        // Send to plan selection and mark as new user; this page will handle free vs paid
        navigate("/auth/plan-selection", {
          replace: true,
          state: { newUser: true, email: data.email, ref: refCode || undefined }
        });
      } else {
        toast.error(result.message || "Registration failed");
      }
    } catch (error) {
      toast.error("An error occurred during registration");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <OneTapGoogle onCredential={(cred) => {
        try {
          window.location.assign(`${process.env.REACT_APP_BACKEND_URL || ''}/auth/google/onetap?credential=${encodeURIComponent(cred)}`);
        } catch {}
      }} />
      <div className="text-center">
        <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">Create your account</h2>
        <p className="text-gray-600 mt-2 text-sm sm:text-base">Join thousands of successful traders</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 sm:space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="firstName" className="text-sm sm:text-base">First Name</Label>
            <Input
              id="firstName"
              type="text"
              placeholder="John"
              className="h-11 sm:h-12 text-base"
              {...register("firstName")}
            />
            {errors.firstName && (
              <p className="text-sm text-red-600">{errors.firstName.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="lastName" className="text-sm sm:text-base">Last Name (optional)</Label>
            <Input
              id="lastName"
              type="text"
              placeholder="Doe"
              className="h-11 sm:h-12 text-base"
              {...register("lastName")}
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="username" className="text-sm sm:text-base">Username (optional)</Label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              id="username"
              type="text"
              placeholder="Choose a username (optional)"
              className="pl-10 h-11 sm:h-12 text-base"
              {...register("username", { onChange: () => setUsernameTouched(true) })}
            />
          </div>
          {errors.username && (
            <p className="text-sm text-red-600">{errors.username.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="email" className="text-sm sm:text-base">Email</Label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              id="email"
              type="email"
              placeholder="john@example.com"
              className="pl-10 h-11 sm:h-12 text-base"
              {...register("email")}
            />
          </div>
          {errors.email && (
            <p className="text-sm text-red-600">{errors.email.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="password" className="text-sm sm:text-base">Password</Label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              id="password"
              type={showPassword ? "text" : "password"}
              placeholder="Create a secure password"
              className="pl-10 pr-12 h-11 sm:h-12 text-base"
              {...register("password")}
            />
            <button
              type="button"
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {errors.password && (
            <p className="text-sm text-red-600">{errors.password.message}</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="confirmPassword" className="text-sm sm:text-base">Confirm Password</Label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              id="confirmPassword"
              type={showConfirmPassword ? "text" : "password"}
              placeholder="Confirm your password"
              className="pl-10 pr-12 h-11 sm:h-12 text-base"
              {...register("confirmPassword")}
            />
            <button
              type="button"
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            >
              {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {errors.confirmPassword && (
            <p className="text-sm text-red-600">{errors.confirmPassword.message}</p>
          )}
        </div>

        <div className="flex items-start space-x-3">
          <Checkbox
            id="agreeToTerms"
            checked={agreeToTerms}
            onCheckedChange={(checked) => setValue("agreeToTerms", checked)}
            className="mt-0.5"
          />
          <Label htmlFor="agreeToTerms" className="text-sm leading-relaxed">
            I agree to the{" "}
            <Link to="/legal/terms" className="text-blue-600 hover:text-blue-500">
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link to="/legal/privacy" className="text-blue-600 hover:text-blue-500">
              Privacy Policy
            </Link>
          </Label>
        </div>
        {errors.agreeToTerms && (
          <p className="text-sm text-red-600">{errors.agreeToTerms.message}</p>
        )}

        <Button type="submit" className="w-full h-11 sm:h-12 text-base" disabled={isLoading || !agreeToTerms}>
          {isLoading ? "Creating account..." : "Create account"}
        </Button>
      </form>

      {/* Social Sign-In */}
      <div className="relative py-2">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-white px-2 text-gray-500">Or continue with</span>
        </div>
      </div>
      <div className="grid">
        <Button variant="outline" className="w-full h-11 sm:h-12 text-base" asChild>
          <a href={`${process.env.REACT_APP_BACKEND_URL || ''}/auth/google/login`} rel="noopener noreferrer">
            <span className="inline-flex items-center">
              <span className="mr-2">G</span>
              Sign up with Google
            </span>
          </a>
        </Button>
      </div>

      <div className="text-center text-sm text-gray-600">
        Already have an account?{' '}
        <Link to="/auth/sign-in" className="text-blue-600 hover:text-blue-500 font-medium">
          Sign in
        </Link>
      </div>
    </div>
  );
};

export default SignUp;