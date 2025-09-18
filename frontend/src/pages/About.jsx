import React from "react";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Link } from "react-router-dom";
import { 
  TrendingUp, 
  Users, 
  Target, 
  Award,
  ArrowRight,
  CheckCircle,
  BarChart3,
  Zap,
  Shield
} from "lucide-react";

const About = () => {
  const stats = [
    { label: "Stocks Available", value: "10,000+" },
    { label: "Real-time Updates", value: "24/7" },
    { label: "Professional Tools", value: "Advanced" },
    { label: "Documentation", value: "Complete" }
  ];

  const team = [
    {
      name: "Trade Scan Pro Team",
      role: "Professional Development Team",
      background: "Experienced professionals dedicated to building superior trading tools",
      image: "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=300&h=300&fit=crop&crop=faces"
    }
  ];

  const values = [
    {
      icon: <Target className="h-8 w-8" />,
      title: "Trader-First Approach",
      description: "Every feature we build is designed from a trader's perspective, solving real problems that active traders face daily."
    },
    {
      icon: <Shield className="h-8 w-8" />,
      title: "Data Integrity",
      description: "We maintain the highest standards for data accuracy and reliability, with multiple validation layers and real-time monitoring."
    },
    {
      icon: <Users className="h-8 w-8" />,
      title: "Community Driven",
      description: "Our roadmap is shaped by feedback from our community of professional traders and institutional clients."
    },
    {
      icon: <Zap className="h-8 w-8" />,
      title: "Innovation",
      description: "We constantly push the boundaries of what's possible in trading technology, leveraging AI and machine learning."
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      {/* Hero Section */}
      <section className="py-20 sm:py-32">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <Badge variant="secondary" className="mb-6 text-lg px-4 py-2">
              <Award className="h-4 w-4 mr-2" />
              About Trade Scan Pro
            </Badge>
            
            <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-8 leading-tight">
              Empowering Traders with
              <span className="text-blue-600 block">Professional Tools</span>
            </h1>
            
            <p className="text-2xl text-gray-700 mb-12 leading-relaxed">
              We're on a mission to democratize professional-grade trading tools, 
              making sophisticated market analysis accessible to retail traders worldwide.
            </p>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl font-bold text-blue-600 mb-2">{stat.value}</div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-24 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-6">Our Mission</h2>
              <p className="text-xl text-gray-600">
                Bridging the gap between institutional and retail trading
              </p>
            </div>
            
            <Card className="mb-12">
              <CardContent className="p-12">
                <div className="text-center">
                  <TrendingUp className="h-16 w-16 text-blue-600 mx-auto mb-8" />
                  <h3 className="text-3xl font-bold text-gray-900 mb-6">
                    Leveling the Playing Field
                  </h3>
                  <p className="text-xl text-gray-700 leading-relaxed mb-8">
                    For too long, professional trading tools have been locked behind expensive institutional licenses, 
                    creating an unfair advantage for large firms. We believe every serious trader deserves access to 
                    the same high-quality data, analytics, and insights that drive success in the markets.
                  </p>
                  <p className="text-xl text-gray-700 leading-relaxed">
                    Trade Scan Pro was founded by a team of former Wall Street professionals who experienced firsthand 
                    the power of institutional-grade tools. We're committed to bringing that same level of sophistication 
                    to retail traders at a fraction of the cost.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-24 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Meet Our Team</h2>
            <p className="text-xl text-gray-600">
              Led by industry veterans with decades of combined experience
            </p>
          </div>
          
          <div className="grid lg:grid-cols-3 gap-8">
            {team.map((member, index) => (
              <Card key={index} className="hover:shadow-xl transition-shadow duration-300">
                <CardContent className="p-8 text-center">
                  <img 
                    src={member.image} 
                    alt={member.name}
                    className="w-32 h-32 rounded-full mx-auto mb-6 object-cover"
                  />
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{member.name}</h3>
                  <p className="text-blue-600 font-semibold mb-4">{member.role}</p>
                  <p className="text-gray-600 leading-relaxed">{member.background}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-24 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">Our Values</h2>
            <p className="text-xl text-gray-600">
              The principles that guide everything we do
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            {values.map((value, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow duration-300">
                <CardContent className="p-8">
                  <div className="flex items-start space-x-4">
                    <div className="w-16 h-16 bg-blue-100 rounded-xl flex items-center justify-center text-blue-600 flex-shrink-0">
                      {value.icon}
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900 mb-4">{value.title}</h3>
                      <p className="text-gray-700 leading-relaxed">{value.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Story Section */}
      <section className="py-24 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-6">Our Story</h2>
              <p className="text-xl text-gray-600">
                From Wall Street to Main Street
              </p>
            </div>
            
            <div className="space-y-8">
              <Card>
                <CardContent className="p-8">
                  <div className="flex items-start space-x-4">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      1
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-gray-900 mb-2">The Problem</h3>
                      <p className="text-gray-700">
                        Our founders worked at major investment banks and hedge funds, where they had access to 
                        sophisticated trading platforms costing hundreds of thousands of dollars per year. When they 
                        left to trade independently, they were shocked by the limited tools available to retail traders.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-8">
                  <div className="flex items-start space-x-4">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      2
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-gray-900 mb-2">The Solution</h3>
                      <p className="text-gray-700">
                        In 2019, we set out to build the platform we wished existed - combining the power of 
                        institutional tools with the accessibility and affordability that retail traders need. 
                        We started with a simple stock screener and have evolved into a comprehensive trading platform.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-8">
                  <div className="flex items-start space-x-4">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      3
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-gray-900 mb-2">The Future</h3>
                      <p className="text-gray-700">
                        Today, we serve over 50,000 traders worldwide and continue to innovate. Our roadmap includes 
                        advanced AI-powered analytics, social trading features, and expanded international market coverage. 
                        We're just getting started in our mission to democratize professional trading tools.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-br from-blue-600 to-blue-700 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-8">
            Join Our Trading Community
          </h2>
          <p className="text-xl mb-12 max-w-2xl mx-auto">
            Experience the difference that professional-grade tools can make in your trading success.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center mb-12">
            <Button asChild size="lg" variant="secondary" className="text-xl px-12 py-6 h-auto">
              <Link to="/auth/sign-up">
                Start Free Trial
                <ArrowRight className="h-6 w-6 ml-3" />
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="text-xl px-12 py-6 h-auto border-white text-white hover:bg-white hover:text-blue-700">
              <Link to="/contact">
                Contact Us
              </Link>
            </Button>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-8 text-lg">
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 mr-2" />
              7-Day Free Trial
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 mr-2" />
              No Credit Card Required
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 mr-2" />
              Cancel Anytime
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;