import React from "react";
import SEO from "../components/SEO";
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
import {
  marketingMetrics,
  formatNumber,
  formatPercent,
  timeframeCopy,
} from "../data/marketingMetrics";

const About = () => {
  const { usage, outcomes, reliability, testimonials } = marketingMetrics;
  const stats = [
    { label: "Monthly Screeners", value: `${formatNumber(usage.totalScreenersRunMonthly)}+` },
    { label: "Alerts Delivered Monthly", value: `${formatNumber(usage.alertsDeliveredMonthly)}+` },
    { label: "Active Accounts", value: formatNumber(usage.activeAccounts) },
    { label: "90-Day Retention", value: formatPercent(testimonials.retentionPercent90Day) }
  ];

  const values = [
    {
      icon: <Target className="h-8 w-8" />,
      title: "Trader-First Approach",
      description: `We optimize flows around the ${usage.medianTimeToFirstScreenerMinutes}-minute time-to-first-insight metric so teams see value immediately.`
    },
    {
      icon: <Shield className="h-8 w-8" />,
      title: "Data Integrity",
      description: `We maintain ${formatPercent(reliability.uptimePercent, 2)} uptime, ${reliability.incidentFreeDaysRolling} incident-free days, and 12 consecutive compliance audits.`
    },
    {
      icon: <Users className="h-8 w-8" />,
      title: "Community Driven",
      description: `Feedback from ${formatNumber(usage.teamsOnPlatform)} customer teams and ${formatNumber(testimonials.verifiedCaseStudies)} verified case studies shapes the roadmap.`
    },
    {
      icon: <Zap className="h-8 w-8" />,
      title: "Innovation",
      description: `We ship telemetry-driven updates every sprint to keep ${formatNumber(usage.totalScreenersRunMonthly)}+ monthly screeners fast and accurate.`
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50/50 to-indigo-100/50">
      <SEO
        title="About | Trade Scan Pro"
        description="Learn about Trade Scan Pro's mission, values, and story providing professional-grade screening and analytics tools for traders."
        url="https://tradescanpro.com/about"
      />
      {/* Hero Section */}
      <section className="py-20 sm:py-32">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-4xl mx-auto">
            <Badge variant="secondary" className="mb-6 text-lg px-4 py-2">
              <Award className="h-4 w-4 mr-2" />
              Telemetry from {timeframeCopy()}
            </Badge>
            
            <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-8 leading-tight">
              Empowering Traders with
              <span className="text-blue-600 block">Professional Tools</span>
            </h1>
            
            <p className="text-2xl text-gray-700 mb-12 leading-relaxed">
              We help {formatNumber(usage.activeAccounts)} accounts surface opportunities in under {usage.medianTimeToFirstScreenerMinutes} minutes, deliver {formatNumber(usage.alertsDeliveredMonthly)} alerts each month, and retain {formatPercent(testimonials.retentionPercent90Day)} of customers through day 90.
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
                Providing accessible, measurable trading intelligence
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
                    Trade Scan Pro delivers institutional-grade screening, alerts, and analytics with {formatPercent(reliability.uptimePercent, 2)} uptime and {formatNumber(usage.totalScreenersRunMonthly)}+ monthly screeners at a price point accessible to independent traders and teams.
                  </p>
                  <p className="text-xl text-gray-700 leading-relaxed">
                    We specialize in real-time equity analysis, delivering {formatNumber(usage.alertsDeliveredMonthly)} alerts every month, shaving {usage.medianTimeToFirstScreenerMinutes} minutes off discovery, and returning {formatPercent(outcomes.averagePortfolioLiftPercent)} average portfolio lift (self-reported) across cohorts.
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
                        We heard from traders and analysts who needed reliable, affordable screening without the noise. Existing platforms either demanded enterprise budgets or made it difficult to reach the first actionable signal quickly.
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
                        We built Trade Scan Pro with telemetry-driven workflows: {formatNumber(usage.totalScreenersRunMonthly)}+ monthly screeners, {formatNumber(usage.alertsDeliveredMonthly)} alerts, and {formatPercent(reliability.uptimePercent, 2)} uptime. Trials stay free until the next 1st so teams can prove value before paying.
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
                        We continue to iterate with cohort telemetry, focusing on higher-converting onboarding, deeper analytics, and global data coverage, while holding {formatPercent(reliability.uptimePercent, 2)} uptime and expanding beyond {formatNumber(usage.coverageUniverse)} equities.
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
            Experience the workflows behind {formatPercent(outcomes.averagePortfolioLiftPercent)} average portfolio lift and {formatPercent(testimonials.retentionPercent90Day)} retention.
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
              Free until the next 1st - no code needed
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 mr-2" />
              {reliability.supportFirstResponseMinutes} min median support reply
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 mr-2" />
              7-week median payback on paid plans
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;