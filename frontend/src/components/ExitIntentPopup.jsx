import React, { useState, useEffect } from 'react';
import { X, Gift, ArrowRight, TrendingUp } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

const ExitIntentPopup = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [email, setEmail] = useState('');
  const [hasShown, setHasShown] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if already shown in this session
    const shown = sessionStorage.getItem('exitIntentShown');
    if (shown) {
      setHasShown(true);
      return;
    }

    const handleMouseLeave = (e) => {
      // Only trigger if mouse leaves from top of viewport
      if (e.clientY <= 0 && !hasShown && !isVisible) {
        setIsVisible(true);
        setHasShown(true);
        sessionStorage.setItem('exitIntentShown', 'true');
      }
    };

    // Add slight delay before attaching listener
    const timer = setTimeout(() => {
      document.addEventListener('mouseout', handleMouseLeave);
    }, 3000);

    return () => {
      clearTimeout(timer);
      document.removeEventListener('mouseout', handleMouseLeave);
    };
  }, [hasShown, isVisible]);

  const handleClose = () => {
    setIsVisible(false);
  };

  const handleContinue = () => {
    setIsVisible(false);
  };

  const handleGetOffer = async () => {
    if (!email || !/\S+@\S+\.\S+/.test(email)) {
      toast.error('Please enter a valid email address');
      return;
    }

    // Store email and navigate to signup with offer
    localStorage.setItem('offerEmail', email);
    toast.success('Great! Redirecting you to start your free trial...');
    setIsVisible(false);

    setTimeout(() => {
      navigate('/auth/sign-up', { state: { email, offer: 'exit-intent' } });
    }, 1000);
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-in fade-in">
      <Card className="relative max-w-2xl w-full mx-4 shadow-2xl border-4 border-blue-500 animate-in zoom-in-95">
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors z-10"
          aria-label="Close"
        >
          <X className="h-6 w-6" />
        </button>

        <CardHeader className="text-center pt-8 pb-4">
          <div className="flex justify-center mb-4">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-4 rounded-full">
              <Gift className="h-12 w-12 text-white" />
            </div>
          </div>
          <CardTitle className="text-3xl font-bold text-gray-900 mb-2">
            Wait! Don't Miss This Special Offer
          </CardTitle>
          <p className="text-xl text-gray-600">
            Start your <span className="font-bold text-blue-600">7-day free trial</span> and get exclusive access to:
          </p>
        </CardHeader>

        <CardContent className="px-8 pb-8">
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="flex items-start gap-3 p-4 bg-blue-50 rounded-lg">
              <TrendingUp className="h-6 w-6 text-blue-600 flex-shrink-0 mt-1" />
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">Real-Time Alerts</h4>
                <p className="text-sm text-gray-600">Never miss a profitable trading opportunity</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 bg-purple-50 rounded-lg">
              <TrendingUp className="h-6 w-6 text-purple-600 flex-shrink-0 mt-1" />
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">7,000+ Stocks</h4>
                <p className="text-sm text-gray-600">Complete NYSE & NASDAQ coverage</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 bg-green-50 rounded-lg">
              <TrendingUp className="h-6 w-6 text-green-600 flex-shrink-0 mt-1" />
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">14 Indicators</h4>
                <p className="text-sm text-gray-600">Advanced technical analysis tools</p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 bg-orange-50 rounded-lg">
              <TrendingUp className="h-6 w-6 text-orange-600 flex-shrink-0 mt-1" />
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">No Credit Card</h4>
                <p className="text-sm text-gray-600">Start completely free for 7 days</p>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg mb-6">
            <div className="text-center mb-4">
              <p className="text-lg font-semibold text-gray-900 mb-2">
                🎁 Special Offer: Join 5,000+ Successful Traders
              </p>
              <p className="text-sm text-gray-600">
                Enter your email to start your free trial and receive exclusive trading insights
              </p>
            </div>
            <div className="flex gap-3">
              <Input
                type="email"
                placeholder="Enter your email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleGetOffer()}
                className="flex-1"
              />
              <Button
                onClick={handleGetOffer}
                size="lg"
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                Start Free Trial
                <ArrowRight className="h-5 w-5 ml-2" />
              </Button>
            </div>
          </div>

          <div className="text-center">
            <button
              onClick={handleContinue}
              className="text-sm text-gray-500 hover:text-gray-700 underline"
            >
              No thanks, I'll continue browsing
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ExitIntentPopup;
