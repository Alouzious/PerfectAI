import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { pitchAPI, poll } from '../services/api';
import {
  Sparkles,
  Upload,
  FileText,
  CheckCircle2,
  AlertCircle,
  Loader2,
  ArrowLeft,
  X,
  File
} from 'lucide-react';

const UploadPitch = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const [uploadedDeck, setUploadedDeck] = useState(null);
  const [progress, setProgress] = useState(0);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = ['application/pdf', 'application/vnd.ms-powerpoint', 
                         'application/vnd.openxmlformats-officedocument.presentationml.presentation'];
      
      if (!validTypes.includes(selectedFile.type)) {
        setError('Please upload a PDF or PowerPoint file');
        return;
      }

      // Validate file size (50MB)
      if (selectedFile.size > 50 * 1024 * 1024) {
        setError('File size must be less than 50MB');
        return;
      }

      setFile(selectedFile);
      setError('');
      
      // Auto-fill title from filename
      if (!title) {
        const fileName = selectedFile.name.replace(/\.[^/.]+$/, '');
        setTitle(fileName);
      }
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      const fakeEvent = { target: { files: [droppedFile] } };
      handleFileChange(fakeEvent);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const removeFile = () => {
    setFile(null);
    setError('');
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!file || !title) {
      setError('Please provide both a file and title');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('uploaded_file', file);
      formData.append('title', title);

      // Upload the file
      const response = await pitchAPI.upload(formData);
      setUploadedDeck(response.pitch_deck);
      setUploading(false);
      setAnalyzing(true);

      // Poll for analysis completion
      await poll(
        () => pitchAPI.checkStatus(response.pitch_deck.id),
        (result) => {
          setProgress(result.progress_percentage || 0);
          return result.status === 'completed' || result.status === 'failed';
        },
        3000, // Poll every 3 seconds
        60 // Max 60 attempts (3 minutes)
      );

      // Analysis complete
      setAnalyzing(false);
      
      // Redirect to pitch deck view
      setTimeout(() => {
        navigate(`/pitch/${response.pitch_deck.id}`);
      }, 1500);

    } catch (err) {
      setUploading(false);
      setAnalyzing(false);
      setError(err.message || 'Upload failed. Please try again.');
    }
  };

  // Check if user can upload
  const canUpload = user?.profile?.can_upload_more_decks;
  const remainingUploads = user?.profile?.remaining_pitch_decks;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="bg-white/5 backdrop-blur-xl border-b border-white/10">
        <div className="container-custom">
          <div className="flex items-center justify-between py-4">
            <Link to="/dashboard" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-white hidden sm:block">Pitch Perfect AI</span>
            </Link>

            <Link to="/dashboard">
              <button className="flex items-center gap-2 px-4 py-2 text-gray-400 hover:text-white transition-colors">
                <ArrowLeft className="w-5 h-5" />
                <span className="hidden sm:inline">Back to Dashboard</span>
              </button>
            </Link>
          </div>
        </div>
      </nav>

      <div className="container-custom py-8 sm:py-12">
        <div className="max-w-3xl mx-auto">
          
          {/* Header */}
          <div className="text-center mb-8 sm:mb-12">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-3">
              Upload Your Pitch Deck
            </h1>
            <p className="text-gray-400 text-base sm:text-lg">
              Get instant AI analysis and personalized coaching
            </p>
            
            {/* Upload Limit Info */}
            {user?.profile?.subscription_tier === 'free' && (
              <div className="inline-flex items-center gap-2 bg-purple-500/20 border border-purple-500/30 text-purple-300 px-4 py-2 rounded-lg mt-4 text-sm">
                <FileText className="w-4 h-4" />
                <span>{remainingUploads} upload{remainingUploads !== 1 ? 's' : ''} remaining on Free plan</span>
              </div>
            )}
          </div>

          {/* Upload Card */}
          <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl sm:rounded-3xl p-6 sm:p-8 lg:p-10">
            
            {!canUpload ? (
              /* Upgrade Required */
              <div className="text-center py-12">
                <div className="w-20 h-20 bg-red-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <AlertCircle className="w-10 h-10 text-red-400" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-3">Upload Limit Reached</h3>
                <p className="text-gray-400 mb-8 max-w-md mx-auto">
                  You've reached the upload limit for the Free plan. Upgrade to Pro for unlimited uploads.
                </p>
                <button className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:shadow-glow transition-all">
                  Upgrade to Pro
                </button>
              </div>
            ) : uploading || analyzing ? (
              /* Upload/Analysis Progress */
              <div className="text-center py-12">
                <div className="w-20 h-20 bg-purple-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6 animate-pulse">
                  <Loader2 className="w-10 h-10 text-purple-400 animate-spin" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-3">
                  {uploading ? 'Uploading...' : 'Analyzing Your Deck'}
                </h3>
                <p className="text-gray-400 mb-6">
                  {uploading 
                    ? 'Please wait while we upload your pitch deck'
                    : 'Our AI is analyzing every slide. This may take 1-2 minutes.'}
                </p>
                
                {/* Progress Bar */}
                <div className="max-w-md mx-auto">
                  <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <p className="text-gray-400 text-sm mt-3">{progress}% Complete</p>
                </div>
              </div>
            ) : (
              /* Upload Form */
              <form onSubmit={handleUpload}>
                
                {/* Error Message */}
                {error && (
                  <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-xl flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <p className="text-red-200 text-sm">{error}</p>
                  </div>
                )}

                {/* Title Input */}
                <div className="mb-6">
                  <label className="block text-white font-semibold mb-3 text-sm sm:text-base">
                    Pitch Deck Title
                  </label>
                  <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="e.g., My Startup Series A Pitch"
                    className="w-full px-4 py-3 sm:py-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                    required
                  />
                </div>

                {/* File Upload Area */}
                <div className="mb-6">
                  <label className="block text-white font-semibold mb-3 text-sm sm:text-base">
                    Upload File
                  </label>
                  
                  {!file ? (
                    <div
                      onDrop={handleDrop}
                      onDragOver={handleDragOver}
                      className="border-2 border-dashed border-white/20 rounded-xl p-8 sm:p-12 text-center hover:border-purple-500/50 hover:bg-white/5 transition-all cursor-pointer"
                      onClick={() => document.getElementById('file-input').click()}
                    >
                      <div className="w-16 h-16 bg-white/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <Upload className="w-8 h-8 text-gray-400" />
                      </div>
                      <h3 className="text-white font-semibold mb-2 text-base sm:text-lg">
                        Drop your file here, or click to browse
                      </h3>
                      <p className="text-gray-400 text-sm mb-4">
                        Supports PDF, PPT, PPTX (Max 50MB)
                      </p>
                      <input
                        id="file-input"
                        type="file"
                        accept=".pdf,.ppt,.pptx"
                        onChange={handleFileChange}
                        className="hidden"
                      />
                    </div>
                  ) : (
                    /* Selected File */
                    <div className="bg-white/5 border border-white/10 rounded-xl p-4 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center flex-shrink-0">
                          <File className="w-6 h-6 text-white" />
                        </div>
                        <div className="min-w-0">
                          <p className="text-white font-medium truncate">{file.name}</p>
                          <p className="text-gray-400 text-sm">
                            {(file.size / (1024 * 1024)).toFixed(2)} MB
                          </p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={removeFile}
                        className="p-2 text-gray-400 hover:text-white transition-colors"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                  )}
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={!file || !title || uploading}
                  className="w-full py-3 sm:py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:shadow-glow transform hover:scale-[1.02] transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-3 text-base sm:text-lg"
                >
                  <Upload className="w-5 h-5 sm:w-6 sm:h-6" />
                  {uploading ? 'Uploading...' : 'Upload & Analyze'}
                </button>

                {/* Info Text */}
                <p className="text-gray-400 text-xs sm:text-sm text-center mt-4">
                  By uploading, you agree to our Terms of Service. Analysis typically takes 1-2 minutes.
                </p>
              </form>
            )}
          </div>

          {/* Success Message */}
          {uploadedDeck && !analyzing && (
            <div className="mt-6 bg-green-500/10 border border-green-500/30 rounded-xl p-6 flex items-start gap-4 animate-fade-in">
              <CheckCircle2 className="w-6 h-6 text-green-400 flex-shrink-0" />
              <div>
                <h4 className="text-white font-semibold mb-1">Analysis Complete!</h4>
                <p className="text-green-200 text-sm">
                  Redirecting you to your pitch deck...
                </p>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default UploadPitch;