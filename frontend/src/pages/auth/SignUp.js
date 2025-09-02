import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../../components/ui/card';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Checkbox } from '../../components/ui/checkbox';
import { Loader2, Eye, EyeOff, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

const SignUp = () => {
  const navigate = useNavigate();
  const { register, isLoading } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const validatePassword = (password) => {
    if (password.length < 8) return false;
    if (!/(?=.*[a-z])/.test(password)) return false;
    if (!/(?=.*[A-Z])/.test(password)) return false;
    if (!/(?=.*\d)/.test(password)) return false;
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.name || !formData.email || !formData.password || !formData.confirmPassword) {
      setError('Please fill in all fields');
      return;
    }

    if (!validatePassword(formData.password)) {
      setError('Password must be at least 8 characters with uppercase, lowercase, and number');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (!acceptedTerms) {
      setError('Please accept the Terms of Service and Privacy Policy');
      return;
    }

    try {
      const result = await register(formData.email, formData.password, formData.name);
      if (result.success) {
        toast.success('Account created successfully!');
        navigate('/app/dashboard');
      } else {
        setError(result.error || 'Failed to create account');
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold text-center">Start your free trial</CardTitle>
        <CardDescription className="text-center">
          Create your Trade Scan Pro account today
        </CardDescription>
      </CardHeader>

      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="name">Full Name</Label>
            <Input
              id="name"
              name="name"
              type="text"
              placeholder="Enter your full name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <div className="relative">
              <Input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Create a password"
                value={formData.password}
                onChange={handleChange}
                required
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
            <div className="text-xs text-gray-500 space-y-1">
              <div className="flex items-center space-x-2">
                <CheckCircle className={`h-3 w-3 ${formData.password.length >= 8 ? 'text-green-500' : 'text-gray-300'}`} />
                <span>At least 8 characters</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className={`h-3 w-3 ${/(?=.*[a-z])(?=.*[A-Z])/.test(formData.password) ? 'text-green-500' : 'text-gray-300'}`} />
                <span>Upper and lowercase letters</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className={`h-3 w-3 ${/(?=.*\d)/.test(formData.password) ? 'text-green-500' : 'text-gray-300'}`} />
                <span>At least one number</span>
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirmPassword">Confirm Password</Label>
            <div className="relative">
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type={showConfirmPassword ? 'text' : 'password'}
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                {showConfirmPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="terms"
              checked={acceptedTerms}
              onCheckedChange={setAcceptedTerms}
            />
            <Label htmlFor="terms" className="text-sm font-normal">
              I agree to the{' '}
              <Link to="/legal/terms" className="text-blue-600 hover:text-blue-500">
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link to="/legal/privacy" className="text-blue-600 hover:text-blue-500">
                Privacy Policy
              </Link>
            </Label>
          </div>
        </CardContent>

        <CardFooter className="flex flex-col space-y-4">
          <Button
            type="submit"
            className="w-full"
            disabled={isLoading}
          >
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Start Free Trial
          </Button>

          <div className="text-center text-sm">
            Already have an account?{' '}
            <Link to="/auth/sign-in" className="text-blue-600 hover:text-blue-500 font-medium">
              Sign in
            </Link>
          </div>
        </CardFooter>
      </form>
    </Card>
  );
};

export default SignUp;