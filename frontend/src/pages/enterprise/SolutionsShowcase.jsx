import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { 
  Building2, 
  Users, 
  TrendingUp, 
  Shield, 
  Zap, 
  Globe,
  CheckCircle,
  ArrowRight,
  ExternalLink,
  Star,
  Award,
  BarChart3,
  Lock,
  Smartphone,
  Database,
  Cloud,
  Settings
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { getEnterpriseSolutions } from '../../api/client';
import logger from '../../lib/logger';

const SolutionsShowcase = () => {
  const [solutions, setSolutions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSolutions();
  }, []);

  const loadSolutions = async () => {
    try {
      const response = await getEnterpriseSolutions();
      if (response.success && response.data) {
        setSolutions(response.data);
      } else {
        // Use mock data if API doesn't return data
        setSolutions(mockSolutions);
      }
    } catch (error) {
      logger.error('Failed to load enterprise solutions:', error);
      setSolutions(mockSolutions);
    } finally {
      setLoading(false);
    }
  };

  const mockSolutions = [
    {
      id: 1,
      name: 'Financial Institution Platform',
      description: 'Complete trading platform solution for banks and investment firms',
      category: 'financial_institutions',
      features: [
        'Multi-entity account management',
        'Regulatory compliance tools',
        'Real-time risk monitoring',
        'Custom reporting suite',
        'API integration framework',
        'Advanced security protocols',
        'Automated SFTP deployment with CI/CD integration',
        'Multi-platform support (Windows, Linux, macOS)'
      ],
      benefits: [
        'Reduce operational costs by 40%',
        'Improve compliance reporting efficiency',
        'Scale to millions of users',
        'Enterprise-grade security'
      ],
      technologies: ['React', 'Node.js', 'PostgreSQL', 'Redis', 'AWS'],
      clientCount: 150,
      deploymentTime: '3-6 months'
    },
    {
      id: 2,
      name: 'Wealth Management Suite',
      description: 'Comprehensive portfolio management tools for advisors and wealth management firms',
      category: 'wealth_management',
      features: [
        'Client portal with portfolio views',
        'Risk assessment algorithms',
        'Performance attribution analysis',
        'Automated rebalancing',
        'Tax-loss harvesting',
        'Compliance monitoring'
      ],
      benefits: [
        'Increase AUM by 25% on average',
        'Reduce manual work by 60%',
        'Improve client satisfaction',
        'Ensure regulatory compliance'
      ],
      technologies: ['Vue.js', 'Python', 'MongoDB', 'Docker', 'Azure'],
      clientCount: 89,
      deploymentTime: '2-4 months'
    },
    {
      id: 3,
      name: 'Fintech Infrastructure',
      description: 'Scalable infrastructure and data feeds for emerging financial technology companies',
      category: 'fintech_startups',
      features: [
        'Real-time market data APIs with 180ms P50 latency',
        'Scalable microservices architecture',
        'Developer-friendly SDKs',
        'Automated testing suite',
        'CI/CD pipeline integration with automated deployments',
        'Performance monitoring and comprehensive logging',
        'Django-integrated data pipeline for 95%+ data quality',
        'High-throughput stock retrieval with 3-minute intervals'
      ],
      benefits: [
        'Launch products 50% faster',
        'Scale to millions of requests',
        'Reduce development costs',
        'Focus on core business logic'
      ],
      technologies: ['React', 'Node.js', 'Kubernetes', 'GraphQL', 'GCP'],
      clientCount: 245,
      deploymentTime: '1-3 months'
    },
    {
      id: 4,
      name: 'Educational Trading Platform',
      description: 'Trading simulators and educational tools for schools and training programs',
      category: 'educational',
      features: [
        'Virtual trading environment',
        'Course curriculum integration',
        'Progress tracking dashboard',
        'Risk-free learning environment',
        'Instructor admin panel',
        'Student performance analytics'
      ],
      benefits: [
        'Engage students effectively',
        'Track learning progress',
        'Safe learning environment',
        'Easy curriculum integration'
      ],
      technologies: ['Angular', 'Java', 'MySQL', 'Spring Boot', 'AWS'],
      clientCount: 67,
      deploymentTime: '1-2 months'
    }
  ];

  const caseStudies = [
    {
      company: 'Global Investment Bank',
      industry: 'Investment Banking',
      challenge: 'Legacy trading systems causing operational inefficiencies and compliance risks',
      solution: 'Implemented our Financial Institution Platform with custom risk monitoring',
      results: [
        '40% reduction in operational costs',
        '99.9% system uptime achieved',
        'Full regulatory compliance',
        '500+ trader onboarding in 6 months'
      ],
      testimonial: "The platform transformed our trading operations. The real-time risk monitoring alone saved us millions in potential losses.",
      clientLogo: '/api/placeholder/120/60'
    },
    {
      company: 'Premier Wealth Advisors',
      industry: 'Wealth Management',
      challenge: 'Manual portfolio management processes limiting growth and client satisfaction',
      solution: 'Deployed Wealth Management Suite with automated rebalancing and client portals',
      results: [
        '25% increase in assets under management',
        '60% reduction in manual processes',
        '95% client satisfaction rate',
        'Regulatory compliance automated'
      ],
      testimonial: "Our clients love the transparency and our advisors are more productive than ever. This solution was a game-changer.",
      clientLogo: '/api/placeholder/120/60'
    },
    {
      company: 'FinTech Innovators Inc.',
      industry: 'Financial Technology',
      challenge: 'Building market data infrastructure from scratch was too time-consuming and expensive',
      solution: 'Integrated our Fintech Infrastructure APIs and development framework',
      results: [
        '50% faster product development',
        'Millions of API calls handled daily',
        '70% reduction in infrastructure costs',
        'Rapid market expansion'
      ],
      testimonial: "Instead of spending months building infrastructure, we focused on our unique value proposition and launched ahead of schedule.",
      clientLogo: '/api/placeholder/120/60'
    }
  ];

  const industryStats = [
    { label: 'Enterprise Clients', value: '500+', icon: Building2 },
    { label: 'Daily API Calls', value: '100M+', icon: Database },
    { label: 'System Uptime', value: '99.9%', icon: Shield },
    { label: 'Countries Served', value: '25+', icon: Globe }
  ];

  if (loading) {
    return (
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading enterprise solutions...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Enterprise Solutions Showcase</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Discover how leading organizations transform their operations with our enterprise-grade 
            trading platforms and financial technology solutions.
          </p>
        </div>

        {/* Industry Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {industryStats.map((stat, index) => (
            <Card key={index}>
              <CardContent className="p-6 text-center">
                <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <stat.icon className="h-6 w-6 text-blue-600" />
                </div>
                <div className="text-2xl font-bold text-gray-900 mb-1">{stat.value}</div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Solutions Showcase */}
        <Tabs defaultValue="solutions" className="space-y-8">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="solutions">Our Solutions</TabsTrigger>
            <TabsTrigger value="case-studies">Case Studies</TabsTrigger>
            <TabsTrigger value="technology">Technology</TabsTrigger>
          </TabsList>

          <TabsContent value="solutions" className="space-y-8">
            <div className="grid lg:grid-cols-2 gap-8">
              {solutions.map((solution) => (
                <Card key={solution.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between mb-2">
                      <CardTitle className="text-xl">{solution.name}</CardTitle>
                      <Badge variant="secondary" className="text-xs">
                        {solution.clientCount}+ clients
                      </Badge>
                    </div>
                    <CardDescription className="text-base">
                      {solution.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Key Features */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3">Key Features</h4>
                      <div className="grid grid-cols-1 gap-2">
                        {solution.features.slice(0, 4).map((feature, index) => (
                          <div key={index} className="flex items-center gap-2 text-sm">
                            <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
                            <span>{feature}</span>
                          </div>
                        ))}
                        {solution.features.length > 4 && (
                          <div className="text-sm text-gray-600">
                            +{solution.features.length - 4} more features
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Key Benefits */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3">Key Benefits</h4>
                      <div className="space-y-1">
                        {solution.benefits.map((benefit, index) => (
                          <div key={index} className="flex items-center gap-2 text-sm text-gray-700">
                            <TrendingUp className="h-4 w-4 text-blue-600 flex-shrink-0" />
                            <span>{benefit}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Deployment Info */}
                    <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                      <div className="text-sm text-gray-600">
                        <span className="font-medium">Deployment:</span> {solution.deploymentTime}
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                          Learn More
                        </Button>
                        <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                          Get Quote
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="text-center">
              <Button asChild size="lg" className="bg-blue-600 hover:bg-blue-700">
                <Link to="/enterprise/contact">
                  Discuss Your Requirements
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Link>
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="case-studies" className="space-y-8">
            {caseStudies.map((study, index) => (
              <Card key={index}>
                <CardContent className="p-8">
                  <div className="grid lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2 space-y-6">
                      <div>
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-xl font-bold text-gray-900">{study.company}</h3>
                          <Badge variant="outline">{study.industry}</Badge>
                        </div>
                        <blockquote className="text-gray-700 italic">
                          "{study.testimonial}"
                        </blockquote>
                      </div>

                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">Challenge</h4>
                        <p className="text-gray-700">{study.challenge}</p>
                      </div>

                      <div>
                        <h4 className="font-semibold text-gray-900 mb-2">Solution</h4>
                        <p className="text-gray-700">{study.solution}</p>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-900 mb-4">Results Achieved</h4>
                      <div className="space-y-3">
                        {study.results.map((result, resultIndex) => (
                          <div key={resultIndex} className="flex items-start gap-2">
                            <Award className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
                            <span className="text-sm text-gray-700">{result}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}

            <div className="text-center">
              <Button asChild size="lg" className="bg-blue-600 hover:bg-blue-700">
                <Link to="/enterprise/quote">
                  Request Your Custom Quote
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Link>
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="technology" className="space-y-8">
            <div className="grid lg:grid-cols-2 gap-8">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Cloud className="h-5 w-5" />
                    Cloud Infrastructure
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-gray-600">
                    Our solutions are built on modern cloud infrastructure for maximum scalability, 
                    reliability, and performance.
                  </p>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Auto-scaling</span>
                      <Badge variant="secondary">99.9% uptime</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Load balancing</span>
                      <Badge variant="secondary">Global CDN</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Disaster recovery</span>
                      <Badge variant="secondary">Multi-region</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5" />
                    Security & Compliance
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-gray-600">
                    Enterprise-grade security with compliance certifications for financial services.
                  </p>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">SOC 2 Type II</span>
                      <Badge variant="secondary">Certified</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">ISO 27001</span>
                      <Badge variant="secondary">Compliant</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">GDPR</span>
                      <Badge variant="secondary">Ready</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="h-5 w-5" />
                    Real-time Data
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-gray-600">
                    High-performance data processing with sub-millisecond latency for real-time trading.
                  </p>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Market data feeds</span>
                      <Badge variant="secondary">Real-time</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">WebSocket APIs</span>
                      <Badge variant="secondary">Low latency</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Data processing</span>
                      <Badge variant="secondary">100M+ ops/sec</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="h-5 w-5" />
                    Integration & APIs
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-gray-600">
                    Comprehensive APIs and integration frameworks for seamless connectivity.
                  </p>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">REST APIs</span>
                      <Badge variant="secondary">Full coverage</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">GraphQL</span>
                      <Badge variant="secondary">Available</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Webhooks</span>
                      <Badge variant="secondary">Real-time</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Technology Stack</CardTitle>
                <CardDescription>Modern, proven technologies powering our enterprise solutions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-4 gap-8">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Frontend</h4>
                    <div className="space-y-2 text-sm">
                      <div>React 18+</div>
                      <div>TypeScript</div>
                      <div>Next.js</div>
                      <div>Tailwind CSS</div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Backend</h4>
                    <div className="space-y-2 text-sm">
                      <div>Node.js</div>
                      <div>Python</div>
                      <div>Java Spring</div>
                      <div>Microservices</div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Database</h4>
                    <div className="space-y-2 text-sm">
                      <div>PostgreSQL</div>
                      <div>MongoDB</div>
                      <div>Redis</div>
                      <div>InfluxDB</div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Infrastructure</h4>
                    <div className="space-y-2 text-sm">
                      <div>Kubernetes</div>
                      <div>Docker</div>
                      <div>AWS/Azure/GCP</div>
                      <div>Terraform</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* CTA Section */}
        <div className="text-center mt-12 pt-8 border-t border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Ready to Transform Your Operations?</h2>
          <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
            Join hundreds of organizations that have revolutionized their trading and financial operations 
            with our enterprise solutions.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" className="bg-blue-600 hover:bg-blue-700">
              <Link to="/enterprise/contact">
                Schedule a Demo
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link to="/enterprise/quote">
                Get Custom Quote
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SolutionsShowcase;