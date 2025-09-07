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
    { label: "NYSE Stocks Covered", value: "3,200+" },
    { label: "Technical Indicators", value: "14" },
    { label: "Scanner Combinations", value: "350+" },
    { label: "Active Users", value: "Growing" }
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
      description: "We maintain high standards for data accuracy and reliability, with validation layers and real-time monitoring."
    },
    {
      icon: <Users className="h-8 w-8" />,
      title: "Community Driven",
      description: "Our roadmap is shaped by feedback from our community of traders and their real-world needs."
    },
    {
      icon: <Zap className="h-8 w-8" />,
      title: "Innovation",
      description: "We constantly improve our platform, leveraging modern technology to provide better trading tools."
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
              We're focused on providing reliable stock screening and analysis tools 
              to help traders make informed decisions in the market.
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
                Providing accessible and reliable trading tools
              </p>
            </div>
            
            <Card className="mb-12">
              <CardContent className="p-12">
                <div className="text-center">
                  <TrendingUp className="h-16 w-16 text-blue-600 mx-auto mb-8" />
                  <h3 className="text-3xl font-bold text-gray-900 mb-6">
                    Making Trading Tools Accessible
                  </h3>
                  <p className="text-xl text-gray-700 leading-relaxed mb-8">
                    Trade Scan Pro was built to provide traders with reliable stock screening and analysis tools 
                    at an affordable price. We focus on delivering practical functionality that helps traders 
                    make better-informed decisions.
                  </p>
                  <p className="text-xl text-gray-700 leading-relaxed">
                    Our platform specializes in NYSE stock analysis with real-time alerts and comprehensive 
                    screening capabilities. We believe in transparent pricing and reliable service delivery.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-24 bg-white">
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
      <section className="py-24 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-6">Our Story</h2>
              <p className="text-xl text-gray-600">
                Building better trading tools
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
                      <h3 className="text-xl font-bold text-gray-900 mb-2">The Need</h3>
                      <p className="text-gray-700">
                        We identified a need for reliable, affordable stock screening tools that focus on 
                        practical functionality rather than overwhelming complexity. Many existing platforms 
                        were either too expensive or lacked the specific features traders actually needed.
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
                        We built Trade Scan Pro to focus on NYSE stocks with comprehensive screening capabilities, 
                        real-time alerts, and portfolio tracking. Our goal was to create a platform that combines 
                        reliability with affordability, starting with code TRIAL for a 7‑day 1$ trial.
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
                        We continue to improve our platform based on user feedback and market needs. 
                        Our roadmap includes enhanced analytics, improved user experience, and expanded 
                        screening capabilities while maintaining our focus on reliability and value.
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
            Experience the difference that reliable trading tools can make in your analysis and decision-making.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center mb-12">
            <Button asChild size="lg" variant="secondary" className="text-xl px-12 py-6 h-auto">
              <Link to="/auth/sign-up">
                Try Now for Free
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
              Use code TRIAL for a 7‑day 1$ trial
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 mr-2" />
              No Setup Fees
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