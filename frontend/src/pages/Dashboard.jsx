import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { pitchAPI } from '../services/api';
import UploadModal from '../components/pitches/UploadModal';
import PitchDeckModal from '../components/pitches/PitchDeckModal';
import { 
  Sparkles, 
  FileText, 
  LogOut,
  Settings,
  Upload,
  Loader2,
  CheckCircle2,
  Clock,
  AlertCircle,
  Mic,
  MessageSquare,
  TrendingUp,
  Calendar,
  Search,
  Filter,
  X
} from 'lucide-react';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [pitchDecks, setPitchDecks] = useState([]);
  const [filteredDecks, setFilteredDecks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  
  // Modal states
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [selectedDeckId, setSelectedDeckId] = useState(null);
  const [deckModalOpen, setDeckModalOpen] = useState(false);

  useEffect(() => {
    fetchPitchDecks();
  }, []);

  useEffect(() => {
    filterDecks();
  }, [searchQuery, statusFilter, pitchDecks]);

  const fetchPitchDecks = async () => {
    try {
      const data = await pitchAPI.list();
      setPitchDecks(data.results || []);
      setFilteredDecks(data.results || []);
    } catch (error) {
      console.error('Error fetching pitch decks:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterDecks = () => {
    let filtered = pitchDecks;

    if (searchQuery.trim()) {
      filtered = filtered.filter(deck =>
        deck.title.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(deck => deck.status === statusFilter);
    }

    setFilteredDecks(filtered);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const clearFilters = () => {
    setSearchQuery('');
    setStatusFilter('all');
  };

  const handleUploadSuccess = () => {
    fetchPitchDecks(); // Refresh list
  };

  const handleViewDeck = (deckId) => {
    setSelectedDeckId(deckId);
    setDeckModalOpen(true);
  };

  const getStatusBadge = (status) => {
    const badges = {
      completed: {
        icon: <CheckCircle2 className="w-3.5 h-3.5" />,
        text: 'Ready',
        class: 'bg-green-500/20 text-green-400 border-green-500/30'
      },
      processing: {
        icon: <Loader2 className="w-3.5 h-3.5 animate-spin" />,
        text: 'Analyzing',
        class: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      },
      failed: {
        icon: <AlertCircle className="w-3.5 h-3.5" />,
        text: 'Failed',
        class: 'bg-red-500/20 text-red-400 border-red-500/30'
      },
      pending: {
        icon: <Clock className="w-3.5 h-3.5" />,
        text: 'Pending',
        class: 'bg-gray-500/20 text-gray-400 border-gray-500/30'
      }
    };
    
    return badges[status] || badges.pending;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Top Navigation Bar */}
      <nav className="bg-white/5 backdrop-blur-xl border-b border-white/10 sticky top-0 z-50">
        <div className="container-custom">
          <div className="flex items-center justify-between py-4">
            {/* Logo */}
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="w-9 h-9 sm:w-10 sm:h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
              </div>
              <span className="text-lg sm:text-xl font-bold text-white hidden sm:block">
                Pitch Perfect AI
              </span>
            </div>

            {/* User Menu */}
            <div className="flex items-center gap-2 sm:gap-3">
              {/* User Info - Hidden on mobile */}
              <div className="hidden md:flex items-center gap-3 px-4 py-2 bg-white/5 rounded-lg border border-white/10">
                <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                  <span className="text-white font-semibold text-sm">
                    {user?.username?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="text-left">
                  <div className="text-white font-medium text-sm">
                    {user?.username}
                  </div>
                  <div className="text-gray-400 text-xs capitalize">
                    {user?.profile?.subscription_tier || 'Free'} Plan
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <button 
                className="p-2 sm:p-2.5 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-all"
                title="Settings"
              >
                <Settings className="w-5 h-5" />
              </button>
              <button 
                onClick={handleLogout}
                className="p-2 sm:p-2.5 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-all"
                title="Logout"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container-custom py-6 sm:py-8 lg:py-12">
        
        {/* Welcome Header */}
        <div className="mb-8 sm:mb-10">
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-2">
            Welcome back{user?.first_name ? `, ${user.first_name}` : ''}! 👋
          </h1>
          <p className="text-gray-400 text-base sm:text-lg">
            {pitchDecks.length === 0 
              ? "Upload your first pitch deck to get started" 
              : `You have ${pitchDecks.length} pitch ${pitchDecks.length === 1 ? 'deck' : 'decks'}`}
          </p>
        </div>

        {/* Main Upload Card - Only show if no decks */}
        {pitchDecks.length === 0 && (
          <div className="mb-8 sm:mb-12">
            <button
              onClick={() => setUploadModalOpen(true)}
              className="group relative block w-full bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl sm:rounded-3xl p-6 sm:p-8 lg:p-10 overflow-hidden hover:shadow-glow-lg transition-all"
            >
              <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl transform translate-x-32 -translate-y-32"></div>
              
              <div className="relative z-10 text-center">
                <div className="inline-flex items-center gap-2 bg-white/20 backdrop-blur-sm px-3 py-1.5 rounded-full mb-4">
                  <Sparkles className="w-4 h-4 text-white" />
                  <span className="text-white text-xs font-semibold">Get Started</span>
                </div>
                <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3">
                  Upload Your First Pitch Deck
                </h2>
                <p className="text-purple-100 text-sm sm:text-base mb-6 max-w-2xl mx-auto">
                  Get instant AI analysis, personalized coaching scripts, and practice tools to perfect your pitch
                </p>
                <div className="inline-flex items-center gap-3 px-6 py-3 bg-white/20 backdrop-blur-sm rounded-xl text-white font-semibold">
                  <Upload className="w-5 h-5" />
                  <span>Upload Pitch Deck</span>
                </div>
              </div>
            </button>
          </div>
        )}

        {/* Search & Filter Bar - Only show if there are decks */}
        {pitchDecks.length > 0 && (
          <div className="mb-6 sm:mb-8">
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
              {/* Search Input */}
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search pitch decks..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 sm:py-3.5 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>

              {/* Status Filter */}
              <div className="relative">
                <Filter className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 pointer-events-none" />
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="pl-12 pr-8 py-3 sm:py-3.5 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all appearance-none cursor-pointer min-w-[140px] sm:min-w-[160px]"
                >
                  <option value="all" className="bg-slate-900">All Status</option>
                  <option value="completed" className="bg-slate-900">Ready</option>
                  <option value="processing" className="bg-slate-900">Analyzing</option>
                  <option value="pending" className="bg-slate-900">Pending</option>
                  <option value="failed" className="bg-slate-900">Failed</option>
                </select>
              </div>

              {/* Upload Button */}
              <button
                onClick={() => setUploadModalOpen(true)}
                className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 sm:py-3.5 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:shadow-glow transition-all whitespace-nowrap"
              >
                <Upload className="w-5 h-5" />
                <span>Upload</span>
              </button>
            </div>

            {/* Active Filters Info */}
            {(searchQuery || statusFilter !== 'all') && (
              <div className="mt-3 flex items-center gap-3 text-sm text-gray-400">
                <span>
                  Showing {filteredDecks.length} of {pitchDecks.length} decks
                </span>
                <button
                  onClick={clearFilters}
                  className="text-purple-400 hover:text-purple-300 transition-colors"
                >
                  Clear filters
                </button>
              </div>
            )}
          </div>
        )}

        {/* Your Pitch Decks Section */}
        {pitchDecks.length > 0 && (
          <div className="mb-8 sm:mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-6">
              Your Pitch Decks
            </h2>

            {loading ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="w-10 h-10 text-purple-500 animate-spin" />
              </div>
            ) : filteredDecks.length === 0 ? (
              /* No Results */
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8 sm:p-12 text-center">
                <div className="w-16 h-16 bg-white/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Search className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">No decks found</h3>
                <p className="text-gray-400 mb-6">
                  {searchQuery 
                    ? `No results for "${searchQuery}"`
                    : `No ${statusFilter} pitch decks`}
                </p>
                <button
                  onClick={clearFilters}
                  className="text-purple-400 hover:text-purple-300 transition-colors font-medium"
                >
                  Clear filters
                </button>
              </div>
            ) : (
              /* Pitch Decks Grid */
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                {filteredDecks.map((deck) => {
                  const badge = getStatusBadge(deck.status);
                  
                  return (
                    <div
                      key={deck.id}
                      className="group bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl sm:rounded-2xl p-5 sm:p-6 hover:bg-white/10 hover:border-white/20 transition-all"
                    >
                      {/* Card Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center flex-shrink-0">
                          <FileText className="w-6 h-6 sm:w-7 sm:h-7 text-white" />
                        </div>
                        
                        <span className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border ${badge.class}`}>
                          {badge.icon}
                          {badge.text}
                        </span>
                      </div>

                      {/* Title */}
                      <h3 className="text-base sm:text-lg font-bold text-white mb-3 line-clamp-2 group-hover:text-purple-300 transition-colors">
                        {deck.title}
                      </h3>

                      {/* Meta Info */}
                      <div className="flex items-center gap-4 text-xs sm:text-sm text-gray-400 mb-4">
                        <div className="flex items-center gap-1.5">
                          <FileText className="w-4 h-4" />
                          <span>{deck.total_slides || 0} slides</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <Calendar className="w-4 h-4" />
                          <span>{new Date(deck.uploaded_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      {deck.status === 'completed' ? (
                        <div className="flex gap-2 pt-4 border-t border-white/10">
                          <button
                            onClick={() => handleViewDeck(deck.id)}
                            className="flex-1 px-4 py-2.5 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg text-sm font-semibold hover:shadow-glow transition-all flex items-center justify-center gap-2"
                          >
                            <FileText className="w-4 h-4" />
                            View
                          </button>
                          <button 
                            className="px-4 py-2.5 bg-white/10 hover:bg-white/20 border border-white/20 text-white rounded-lg transition-all"
                            title="Practice"
                          >
                            <Mic className="w-4 h-4" />
                          </button>
                        </div>
                      ) : deck.status === 'processing' ? (
                        <div className="pt-4 border-t border-white/10">
                          <div className="flex items-center gap-3 text-yellow-400 text-sm">
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span>Analyzing deck...</span>
                          </div>
                        </div>
                      ) : deck.status === 'failed' ? (
                        <div className="pt-4 border-t border-white/10">
                          <button className="w-full px-4 py-2.5 bg-red-500/20 hover:bg-red-500/30 border border-red-500/30 text-red-400 rounded-lg text-sm font-semibold transition-all">
                            Retry Analysis
                          </button>
                        </div>
                      ) : null}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Feature Info Cards - Only show if user has decks */}
        {pitchDecks.length > 0 && (
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl sm:rounded-3xl p-6 sm:p-8">
            <div className="grid sm:grid-cols-3 gap-6 sm:gap-8">
              <div className="text-center sm:text-left">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-purple-500/20 rounded-xl mb-3">
                  <Mic className="w-6 h-6 text-purple-400" />
                </div>
                <h3 className="text-white font-semibold mb-1 text-sm sm:text-base">Practice Delivery</h3>
                <p className="text-gray-400 text-xs sm:text-sm">Record and get AI feedback</p>
              </div>
              
              <div className="text-center sm:text-left">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-500/20 rounded-xl mb-3">
                  <MessageSquare className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-white font-semibold mb-1 text-sm sm:text-base">Q&A Preparation</h3>
                <p className="text-gray-400 text-xs sm:text-sm">Practice investor questions</p>
              </div>
              
              <div className="text-center sm:text-left">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-green-500/20 rounded-xl mb-3">
                  <TrendingUp className="w-6 h-6 text-green-400" />
                </div>
                <h3 className="text-white font-semibold mb-1 text-sm sm:text-base">Track Progress</h3>
                <p className="text-gray-400 text-xs sm:text-sm">Monitor improvement</p>
              </div>
            </div>
          </div>
        )}

      </div>

      {/* Modals */}
      <UploadModal 
        isOpen={uploadModalOpen} 
        onClose={() => setUploadModalOpen(false)}
        onSuccess={handleUploadSuccess}
      />

      <PitchDeckModal
        isOpen={deckModalOpen}
        onClose={() => setDeckModalOpen(false)}
        deckId={selectedDeckId}
      />
    </div>
  );
};

export default Dashboard;