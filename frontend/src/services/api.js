// API service layer for all backend calls

const API_BASE_URL = '/api';

/**
 * Get CSRF token from cookies (required by Django)
 */
const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
};

/**
 * Base fetch wrapper with credentials and CSRF
 */
const apiFetch = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;

  const config = {
    credentials: 'include', // CRITICAL: Include cookies
    headers: {
      'X-CSRFToken': getCookie('csrftoken') || '', // CSRF token for Django
      ...options.headers,
    },
    ...options,
  };

  // Don't set Content-Type for FormData (browser sets it with boundary)
  if (!(options.body instanceof FormData)) {
    config.headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(url, config);

    // Handle different response types
    if (response.status === 204) {
      return { success: true };
    }

    const data = await response.json();

    if (!response.ok) {
      throw {
        status: response.status,
        message: data.message || data.error || 'Request failed',
        errors: data.errors || data,
      };
    }

    return data;
  } catch (error) {
    if (error.status) {
      throw error;
    }
    throw {
      status: 500,
      message: 'Network error. Please check your connection.',
      errors: {},
    };
  }
};

// ===== AUTHENTICATION APIs =====

export const authAPI = {
  register: (data) =>
    apiFetch('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  login: (credentials) =>
    apiFetch('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),

  logout: () =>
    apiFetch('/auth/logout/', {
      method: 'POST',
    }),

  getCurrentUser: () =>
    apiFetch('/auth/me/'),

  getProfile: () =>
    apiFetch('/auth/profile/'),

  updateProfile: (data) =>
    apiFetch('/auth/profile/', {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  healthCheck: () =>
    apiFetch('/auth/health/'),
};

// ===== PITCH DECK APIs =====

export const pitchAPI = {
  upload: (formData) =>
    apiFetch('/pitches/upload/', {
      method: 'POST',
      body: formData, // FormData automatically sets Content-Type
    }),

  list: () =>
    apiFetch('/pitches/'),

  get: (deckId) =>
    apiFetch(`/pitches/${deckId}/`),

  delete: (deckId) =>
    apiFetch(`/pitches/${deckId}/delete/`, {
      method: 'DELETE',
    }),

  checkStatus: (deckId) =>
    apiFetch(`/pitches/${deckId}/status/`),

  getSlides: (deckId) =>
    apiFetch(`/pitches/${deckId}/slides/`),

  getSlide: (deckId, slideNumber) =>
    apiFetch(`/pitches/${deckId}/slides/${slideNumber}/`),

  getCoaching: (deckId, slideNumber) =>
    apiFetch(`/pitches/${deckId}/slides/${slideNumber}/coaching/`),
};

// ===== PRACTICE APIs =====

export const practiceAPI = {
  create: (data) =>
    apiFetch('/practice/sessions/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  list: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return apiFetch(`/practice/sessions/list/${query ? '?' + query : ''}`);
  },

  get: (sessionId) =>
    apiFetch(`/practice/sessions/${sessionId}/`),

  getFeedback: (sessionId) =>
    apiFetch(`/practice/sessions/${sessionId}/feedback/`),

  getProgress: (deckId) =>
    apiFetch(`/practice/progress/${deckId ? '?pitch_deck=' + deckId : ''}`),
};

// ===== Q&A APIs =====

export const qaAPI = {
  getQuestions: (deckId) =>
    apiFetch(`/qa/questions/${deckId}/`),

  getQuestion: (questionId) =>
    apiFetch(`/qa/questions/detail/${questionId}/`),

  submitAnswer: (data) =>
    apiFetch('/qa/answers/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getAnswer: (answerId) =>
    apiFetch(`/qa/answers/${answerId}/`),

  listAnswers: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return apiFetch(`/qa/answers/list/${query ? '?' + query : ''}`);
  },
};

// ===== POLLING UTILITY =====

/**
 * Poll an endpoint until a condition is met
 * @param {Function} fetchFn - Function that returns a promise
 * @param {Function} checkFn - Function that checks if polling should stop
 * @param {number} interval - Polling interval in ms
 * @param {number} maxAttempts - Maximum number of attempts
 */
export const poll = async (fetchFn, checkFn, interval = 3000, maxAttempts = 60) => {
  let attempts = 0;

  const executePoll = async (resolve, reject) => {
    try {
      const result = await fetchFn();
      attempts++;

      if (checkFn(result)) {
        return resolve(result);
      } else if (attempts >= maxAttempts) {
        return reject(new Error('Polling timeout'));
      } else {
        setTimeout(() => executePoll(resolve, reject), interval);
      }
    } catch (error) {
      reject(error);
    }
  };

  return new Promise(executePoll);
};

export default {
  authAPI,
  pitchAPI,
  practiceAPI,
  qaAPI,
  poll,
};