import { Link } from 'react-router-dom';
import { 
  Sparkles, 
  TrendingUp, 
  Mic, 
  FileText, 
  Brain, 
  Target,
  ArrowRight,
  Star,
  Zap,
  Shield,
  CheckCircle2,
  BarChart3,
  MessageSquare,
  Award,
  Rocket,
  Layers,
  Users,
  Menu,
  X
} from 'lucide-react';
import { useState } from 'react';

const LandingPage = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const features = [
    {
      icon: <Brain className="w-5 h-5 sm:w-6 sm:h-6" />,
      title: "AI Pitch Analysis",
      description: "Advanced AI analyzes every slide, identifying strengths and improvements.",
      gradient: "from-purple-500 to-pink-500"
    },
    {
      icon: <Mic className="w-5 h-5 sm:w-6 sm:h-6" />,
      title: "Voice Practice",
      description: "Real-time voice analysis with feedback on pace, clarity, and confidence.",
      gradient: "from-blue-500 to-cyan-500"
    },
    {
      icon: <Target className="w-5 h-5 sm:w-6 sm:h-6" />,
      title: "Smart Coaching",
      description: "Personalized scripts for each slide. Learn what to say for maximum impact.",
      gradient: "from-orange-500 to-red-500"
    },
    {
      icon: <MessageSquare className="w-5 h-5 sm:w-6 sm:h-6" />,
      title: "Q&A Preparation",
      description: "Practice tough investor questions with AI-generated scenarios.",
      gradient: "from-green-500 to-emerald-500"
    },
    {
      icon: <BarChart3 className="w-5 h-5 sm:w-6 sm:h-6" />,
      title: "Progress Tracking",
      description: "Detailed analytics show your improvement. Watch your scores soar.",
      gradient: "from-indigo-500 to-purple-500"
    },
    {
      icon: <Zap className="w-5 h-5 sm:w-6 sm:h-6" />,
      title: "Instant Feedback",
      description: "Get immediate AI feedback. Practice anytime, anywhere.",
      gradient: "from-yellow-500 to-orange-500"
    }
  ];

  const stats = [
    { icon: <Users className="w-6 h-6 sm:w-8 sm:h-8" />, stat: "10K+", label: "Users" },
    { icon: <Award className="w-6 h-6 sm:w-8 sm:h-8" />, stat: "92%", label: "Success" },
    { icon: <Star className="w-6 h-6 sm:w-8 sm:h-8" />, stat: "4.9/5", label: "Rating" },
    { icon: <Zap className="w-6 h-6 sm:w-8 sm:h-8" />, stat: "24/7", label: "Available" }
  ];

  const steps = [
    {
      step: "01",
      icon: <FileText className="w-6 h-6 sm:w-8 sm:h-8" />,
      title: "Upload Your Deck",
      description: "Drop your PDF or PowerPoint. AI analyzes instantly.",
      gradient: "from-purple-500 to-pink-500"
    },
    {
      step: "02",
      icon: <Mic className="w-6 h-6 sm:w-8 sm:h-8" />,
      title: "Practice Your Pitch",
      description: "Record yourself. Get real-time AI feedback.",
      gradient: "from-blue-500 to-cyan-500"
    },
    {
      step: "03",
      icon: <Award className="w-6 h-6 sm:w-8 sm:h-8" />,
      title: "Win Funding",
      description: "Ace questions. Track progress. Close deals.",
      gradient: "from-orange-500 to-red-500"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 overflow-x-hidden">
      {/* Animated background - hidden on mobile for performance */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none hidden sm:block">
        <div className="absolute top-20 left-10 w-48 sm:w-72 h-48 sm:h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float"></div>
        <div className="absolute top-40 right-10 w-48 sm:w-72 h-48 sm:h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float" style={{animationDelay: '2s'}}></div>
        <div className="absolute -bottom-32 left-1/2 w-64 sm:w-96 h-64 sm:h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float" style={{animationDelay: '4s'}}></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-50 bg-white/5 backdrop-blur-lg border-b border-white/10 sticky top-0">
        <div className="container-custom">
          <div className="flex justify-between items-center py-3 sm:py-4">
            {/* Logo */}
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
              </div>
              <span className="text-lg sm:text-2xl font-bold text-white truncate">Pitch Perfect AI</span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex gap-4">
              <Link to="/login">
                <button className="px-6 py-2.5 text-white hover:text-purple-300 transition-colors font-medium">
                  Sign In
                </button>
              </Link>
              <Link to="/register">
                <button className="btn btn-primary">
                  Get Started Free
                  <ArrowRight className="w-4 h-4" />
                </button>
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <button 
              className="md:hidden text-white p-2"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden pb-4 animate-fade-in">
              <div className="flex flex-col gap-3">
                <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                  <button className="w-full px-6 py-3 text-white bg-white/10 rounded-lg font-medium">
                    Sign In
                  </button>
                </Link>
                <Link to="/register" onClick={() => setMobileMenuOpen(false)}>
                  <button className="w-full btn btn-primary">
                    Get Started Free
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </Link>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative section pt-16 sm:pt-24 md:pt-32">
        <div className="container-custom">
          <div className="text-center max-w-5xl mx-auto">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm border border-white/20 px-3 sm:px-4 py-1.5 sm:py-2 rounded-full mb-6 sm:mb-8 animate-fade-in">
              <Sparkles className="w-3 h-3 sm:w-4 sm:h-4 text-purple-300 flex-shrink-0" />
              <span className="text-xs sm:text-sm font-semibold text-purple-200">Powered by Claude AI</span>
            </div>
            
            {/* Main Headline */}
            <h1 className="text-hero text-white mb-4 sm:mb-6 leading-tight animate-slide-in px-4">
              Perfect Your Pitch.
              <br />
              <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
                Win More Funding.
              </span>
            </h1>
            
            <p className="text-base sm:text-xl md:text-2xl text-gray-300 mb-8 sm:mb-12 leading-relaxed max-w-3xl mx-auto px-4">
              Your 24/7 AI pitch coach. Analyze your deck, perfect your delivery, 
              and ace investor questions.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center mb-8 sm:mb-16 px-4">
              <Link to="/register" className="w-full sm:w-auto">
                <button className="w-full sm:w-auto btn btn-primary text-base sm:text-lg">
                  <Rocket className="w-4 h-4 sm:w-5 sm:h-5" />
                  Start Free Trial
                </button>
              </Link>
              <button className="w-full sm:w-auto btn btn-secondary text-base sm:text-lg">
                <Star className="w-4 h-4 sm:w-5 sm:h-5" />
                Watch Demo
              </button>
            </div>

            {/* Social Proof - Stacked on mobile */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-8 text-gray-400 text-xs sm:text-sm px-4">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 sm:w-5 sm:h-5 text-green-400 flex-shrink-0" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 sm:w-5 sm:h-5 text-green-400 flex-shrink-0" />
                <span>Free forever plan</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 sm:w-5 sm:h-5 text-green-400 flex-shrink-0" />
                <span>Instant setup</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="relative section-tight border-y border-white/10 bg-white/5 backdrop-blur-sm">
        <div className="container-custom">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-8">
            {stats.map((item, i) => (
              <div key={i} className="text-center group">
                <div className="inline-flex items-center justify-center w-12 h-12 sm:w-16 sm:h-16 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-xl mb-3 sm:mb-4 group-hover:scale-110 transition-transform">
                  <div className="text-purple-300">{item.icon}</div>
                </div>
                <div className="text-2xl sm:text-4xl font-bold text-white mb-1 sm:mb-2">{item.stat}</div>
                <div className="text-xs sm:text-base text-gray-400">{item.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="relative section">
        <div className="container-custom">
          <div className="text-center mb-8 sm:mb-16 px-4">
            <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm border border-white/20 px-3 sm:px-4 py-1.5 sm:py-2 rounded-full mb-4 sm:mb-6">
              <Layers className="w-3 h-3 sm:w-4 sm:h-4 text-purple-300" />
              <span className="text-xs sm:text-sm font-semibold text-purple-200">Powerful Features</span>
            </div>
            <h2 className="text-section-title text-white mb-4 sm:mb-6">
              Everything You Need to Win
            </h2>
            <p className="text-base sm:text-xl text-gray-400 max-w-2xl mx-auto">
              AI-powered tools to perfect every aspect of your pitch
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
            {features.map((feature, index) => (
              <div 
                key={index}
                className="group relative card hover:scale-105 transition-all"
              >
                {/* Gradient icon */}
                <div className={`w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br ${feature.gradient} rounded-xl flex items-center justify-center mb-4 sm:mb-6 group-hover:scale-110 transition-transform flex-shrink-0`}>
                  <div className="text-white">
                    {feature.icon}
                  </div>
                </div>
                
                <h3 className="text-card-title text-white mb-2 sm:mb-3">
                  {feature.title}
                </h3>
                <p className="text-sm sm:text-base text-gray-400 leading-relaxed">
                  {feature.description}
                </p>

                {/* Hover glow */}
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-10 rounded-xl sm:rounded-2xl transition-opacity`}></div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="relative section bg-white/5 backdrop-blur-sm border-y border-white/10">
        <div className="container-custom">
          <div className="text-center mb-8 sm:mb-16 px-4">
            <h2 className="text-section-title text-white mb-4 sm:mb-6">
              Start in 3 Simple Steps
            </h2>
            <p className="text-base sm:text-xl text-gray-400">
              From pitch deck to funding-ready in minutes
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8 sm:gap-12 max-w-5xl mx-auto">
            {steps.map((item, i) => (
              <div key={i} className="text-center group px-4">
                <div className={`inline-flex items-center justify-center w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-br ${item.gradient} rounded-2xl mb-4 sm:mb-6 group-hover:scale-110 transition-transform`}>
                  <div className="text-white">{item.icon}</div>
                </div>
                <div className="text-4xl sm:text-6xl font-black text-white/10 mb-3 sm:mb-4">{item.step}</div>
                <h3 className="text-xl sm:text-2xl font-bold text-white mb-2 sm:mb-3">{item.title}</h3>
                <p className="text-sm sm:text-base text-gray-400">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="relative section">
        <div className="container-custom px-4">
          <div className="max-w-4xl mx-auto bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl sm:rounded-3xl p-8 sm:p-12 md:p-16 shadow-glow-lg text-center">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-4 sm:mb-6">
              Ready to Transform Your Pitch?
            </h2>
            <p className="text-base sm:text-xl text-purple-100 mb-6 sm:mb-10">
              Join 10,000+ founders who've perfected their pitches with AI
            </p>
            <Link to="/register">
              <button className="w-full sm:w-auto px-8 sm:px-10 py-4 sm:py-5 bg-white text-purple-600 rounded-xl font-bold text-base sm:text-lg hover:scale-105 transform transition-all shadow-xl inline-flex items-center justify-center gap-3">
                <Rocket className="w-5 h-5 sm:w-6 sm:h-6" />
                Start Your Free Trial
                <ArrowRight className="w-5 h-5 sm:w-6 sm:h-6" />
              </button>
            </Link>
            <p className="text-purple-200 mt-4 sm:mt-6 text-xs sm:text-base">
              No credit card required • Free forever plan available
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative border-t border-white/10 bg-white/5 backdrop-blur-sm py-8 sm:py-12">
        <div className="container-custom text-center px-4">
          <div className="flex items-center justify-center gap-2 sm:gap-3 mb-3 sm:mb-4">
            <div className="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            </div>
            <span className="text-lg sm:text-xl font-bold text-white">Pitch Perfect AI</span>
          </div>
          <p className="text-sm sm:text-base text-gray-400 mb-3 sm:mb-4">
            Powered by Claude AI • Built for Entrepreneurs
          </p>
          <p className="text-xs sm:text-sm text-gray-500">
            © 2025 Pitch Perfect AI. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;