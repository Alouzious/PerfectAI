import { useState } from 'react';
import { pitchAPI } from '../../services/api';
import Modal from '../common/Modal';
import { Upload, File, X, Loader2, AlertCircle } from 'lucide-react';

const UploadModal = ({ isOpen, onClose, onSuccess }) => {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const validTypes = ['application/pdf', 'application/vnd.ms-powerpoint', 
                         'application/vnd.openxmlformats-officedocument.presentationml.presentation'];
      
      if (!validTypes.includes(selectedFile.type)) {
        setError('Please upload a PDF or PowerPoint file');
        return;
      }

      if (selectedFile.size > 50 * 1024 * 1024) {
        setError('File size must be less than 50MB');
        return;
      }

      setFile(selectedFile);
      setError('');
      
      if (!title) {
        const fileName = selectedFile.name.replace(/\.[^/.]+$/, '');
        setTitle(fileName);
      }
    }
  };

  const handleSubmit = async (e) => {
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

      await pitchAPI.upload(formData);
      
      // Reset form
      setFile(null);
      setTitle('');
      setUploading(false);
      
      // Call success callback
      onSuccess();
      onClose();
      
    } catch (err) {
      setUploading(false);
      setError(err.message || 'Upload failed. Please try again.');
    }
  };

  const handleClose = () => {
    if (!uploading) {
      setFile(null);
      setTitle('');
      setError('');
      onClose();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Upload Pitch Deck" size="md">
      <form onSubmit={handleSubmit}>
        {error && (
          <div className="mb-4 p-4 bg-red-500/10 border border-red-500/50 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-red-200 text-sm">{error}</p>
          </div>
        )}

        {/* Title */}
        <div className="mb-4">
          <label className="block text-white font-medium mb-2 text-sm">
            Pitch Deck Title
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., My Startup Series A Pitch"
            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all text-sm"
            required
            disabled={uploading}
          />
        </div>

        {/* File Upload */}
        <div className="mb-6">
          <label className="block text-white font-medium mb-2 text-sm">
            Upload File
          </label>
          
          {!file ? (
            <div
              className="border-2 border-dashed border-white/20 rounded-lg p-8 text-center hover:border-purple-500/50 hover:bg-white/5 transition-all cursor-pointer"
              onClick={() => document.getElementById('modal-file-input').click()}
            >
              <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
              <p className="text-white font-medium mb-1">Drop file or click to browse</p>
              <p className="text-gray-400 text-xs">PDF, PPT, PPTX (Max 50MB)</p>
              <input
                id="modal-file-input"
                type="file"
                accept=".pdf,.ppt,.pptx"
                onChange={handleFileChange}
                className="hidden"
                disabled={uploading}
              />
            </div>
          ) : (
            <div className="bg-white/5 border border-white/10 rounded-lg p-4 flex items-center justify-between">
              <div className="flex items-center gap-3 min-w-0">
                <File className="w-8 h-8 text-purple-400 flex-shrink-0" />
                <div className="min-w-0">
                  <p className="text-white font-medium truncate text-sm">{file.name}</p>
                  <p className="text-gray-400 text-xs">
                    {(file.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              </div>
              {!uploading && (
                <button
                  type="button"
                  onClick={() => setFile(null)}
                  className="p-2 text-gray-400 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>
          )}
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={!file || !title || uploading}
          className="w-full py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:shadow-glow transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {uploading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload className="w-5 h-5" />
              Upload & Analyze
            </>
          )}
        </button>
      </form>
    </Modal>
  );
};

export default UploadModal;