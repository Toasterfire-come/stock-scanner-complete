import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../../components/ui/card';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Loader2, ArrowLeft, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email) {
      setError('Please enter your email address');
      return;
    }

    setIsLoading(true);
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      setIsSubmitted(true);
      toast.success('Password reset email sent!');
    } catch (err) {
      setError('Failed to send reset email. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isSubmitted) {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
            <CheckCircle className="h-6 w-6 text-green-600" />
          </div>
          <CardTitle className="text-2xl font-bold">Check your email</CardTitle>
          <CardDescription>
            We've sent a password reset link to <strong>{email}</strong>
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-4">
          <div className="text-sm text-gray-600 text-center">
            <p>Didn't receive the email? Check your spam folder or</p>
            <Button
              variant="link"
              className="p-0 h-auto font-medium"
              onClick={() => setIsSubmitted(false)}
            >
              try again
            </Button>
          </div>
        </CardContent>

        <CardFooter>
          <Button asChild variant="ghost" className="w-full">
            <Link to="/auth/sign-in">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to sign in
            </Link>
          </Button>
        </CardFooter>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl font-bold text-center">Forgot your password?</CardTitle>
        <CardDescription className="text-center">
          Enter your email address and we'll send you a link to reset your password
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
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
        </CardContent>

        <CardFooter className="flex flex-col space-y-4">
          <Button
            type="submit"
            className="w-full"
            disabled={isLoading}
          >
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Send reset link
          </Button>

          <Button asChild variant="ghost" className="w-full">
            <Link to="/auth/sign-in">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to sign in
            </Link>
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
};

export default ForgotPassword;