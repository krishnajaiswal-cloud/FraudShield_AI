import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Shield, Zap, BarChart3, Users } from 'lucide-react';
import { MainLayout, Card, Section } from '../components';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <MainLayout>
      {/* Hero Section */}
      <section className="min-h-screen bg-gradient-to-b from-cyber-darker via-cyber-dark to-cyber-darker flex items-center">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
          <div className="text-center space-y-8">
            <div>
              <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
                Advanced APK{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-risk-critical to-risk-high">
                  Security Analysis
                </span>
              </h1>
              <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                Analyze Android applications for security vulnerabilities, malware indicators, and privacy risks using advanced AI-powered detection.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
              <button
                onClick={() => navigate('/scan')}
                className="px-8 py-4 bg-gradient-to-r from-risk-critical to-risk-high text-white rounded-lg font-semibold hover:shadow-neon-red transition-all flex items-center justify-center gap-2"
              >
                Analyze APK
                <ArrowRight className="w-5 h-5" />
              </button>
              <button
                className="px-8 py-4 border border-cyber-border text-white rounded-lg font-semibold hover:border-cyber-border/50 transition-colors"
              >
                Learn More
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-cyber-dark">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Section
            title="Comprehensive Security Analysis"
            description="FraudShield AI provides detailed insights into every aspect of your APK"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                {
                  icon: Shield,
                  title: 'Permission Analysis',
                  description: 'Identify dangerous permissions and their security implications',
                },
                {
                  icon: Zap,
                  title: 'Malware Detection',
                  description: 'Advanced detection of malware signatures and suspicious behaviors',
                },
                {
                  icon: BarChart3,
                  title: 'Risk Scoring',
                  description: 'Get a comprehensive risk score based on multiple factors',
                },
                {
                  icon: Users,
                  title: 'Privacy Analysis',
                  description: 'Understand how your data is being accessed and transmitted',
                },
              ].map((feature, index) => (
                <Card key={index}>
                  <feature.icon className="w-8 h-8 text-risk-critical mb-4" />
                  <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-gray-400 text-sm">{feature.description}</p>
                </Card>
              ))}
            </div>
          </Section>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-cyber-darker">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Section
            title="How It Works"
            description="Simple, secure, and fast APK analysis"
          >
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {[
                { number: '1', title: 'Upload', description: 'Select your APK file' },
                { number: '2', title: 'Analyze', description: 'AI analyzes permissions & code' },
                { number: '3', title: 'Review', description: 'Get detailed security report' },
                { number: '4', title: 'Decide', description: 'Make informed decisions' },
              ].map((step, index) => (
                <div key={index} className="relative">
                  <Card>
                    <div className="text-center">
                      <div className="w-12 h-12 bg-gradient-to-br from-risk-critical to-risk-high rounded-full flex items-center justify-center mx-auto mb-4 text-lg font-bold text-white">
                        {step.number}
                      </div>
                      <h3 className="font-semibold text-white mb-2">{step.title}</h3>
                      <p className="text-gray-400 text-sm">{step.description}</p>
                    </div>
                  </Card>
                  {index < 3 && (
                    <div className="hidden md:block absolute top-1/2 -right-3 transform -translate-y-1/2">
                      <ArrowRight className="w-6 h-6 text-cyber-border" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Section>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-cyber-dark">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Secure Your Android Ecosystem Today
          </h2>
          <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
            Join thousands of developers and security professionals who trust FraudShield AI for comprehensive APK security analysis.
          </p>
          <button
            onClick={() => navigate('/scan')}
            className="px-8 py-4 bg-gradient-to-r from-risk-critical to-risk-high text-white rounded-lg font-semibold hover:shadow-neon-red transition-all inline-flex items-center gap-2"
          >
            Get Started Free
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </section>
    </MainLayout>
  );
};
