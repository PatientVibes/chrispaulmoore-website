/**
 * Comments System - Cloudflare Worker
 * 
 * This worker handles comment storage and retrieval for chrispaulmoore.com
 * Features:
 * - CORS support for browser requests
 * - Basic spam protection with rate limiting
 * - Comment validation and sanitization
 * - KV storage for persistence
 * 
 * Deploy this to: comments.chrispaulmoore.com
 */

// Rate limiting configuration
const RATE_LIMIT_WINDOW = 60 * 1000; // 1 minute
const MAX_COMMENTS_PER_MINUTE = 5;

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 200,
        headers: getCorsHeaders()
      });
    }

    try {
      // Route requests
      if (url.pathname === '/comments' && request.method === 'GET') {
        return await handleGetComments(env);
      }
      
      if (url.pathname === '/comments' && request.method === 'POST') {
        return await handlePostComment(request, env);
      }

      // Health check endpoint
      if (url.pathname === '/health') {
        return new Response(JSON.stringify({ 
          status: 'healthy', 
          timestamp: new Date().toISOString() 
        }), {
          headers: { ...getCorsHeaders(), 'Content-Type': 'application/json' }
        });
      }

      return new Response('Not Found', { 
        status: 404,
        headers: getCorsHeaders()
      });

    } catch (error) {
      console.error('Worker error:', error);
      return new Response(JSON.stringify({ 
        error: 'Internal server error' 
      }), {
        status: 500,
        headers: { ...getCorsHeaders(), 'Content-Type': 'application/json' }
      });
    }
  },
};

async function handleGetComments(env) {
  try {
    // Get comments from KV storage
    const commentsData = await env.COMMENTS_KV.get('comments', 'json');
    const comments = commentsData || [];
    
    // Sort by timestamp (newest first) and limit to last 50
    const sortedComments = comments
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .slice(0, 50);

    return new Response(JSON.stringify(sortedComments), {
      headers: { ...getCorsHeaders(), 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Error getting comments:', error);
    return new Response(JSON.stringify([]), {
      headers: { ...getCorsHeaders(), 'Content-Type': 'application/json' }
    });
  }
}

async function handlePostComment(request, env) {
  try {
    // Rate limiting check
    const clientIP = request.headers.get('CF-Connecting-IP') || 'unknown';
    const rateLimitKey = `rate_limit:${clientIP}`;
    
    const rateCount = await env.COMMENTS_KV.get(rateLimitKey);
    if (rateCount && parseInt(rateCount) >= MAX_COMMENTS_PER_MINUTE) {
      return new Response(JSON.stringify({ 
        error: 'Rate limit exceeded. Please wait before posting another comment.' 
      }), {
        status: 429,
        headers: { ...getCorsHeaders(), 'Content-Type': 'application/json' }
      });
    }

    // Parse and validate comment data
    const commentData = await request.json();
    const validation = validateComment(commentData);
    
    if (!validation.valid) {
      return new Response(JSON.stringify({ 
        error: validation.error 
      }), {
        status: 400,
        headers: { ...getCorsHeaders(), 'Content-Type': 'application/json' }
      });
    }

    // Create comment object
    const comment = {
      id: crypto.randomUUID(),
      name: sanitizeText(commentData.name),
      email: commentData.email ? sanitizeEmail(commentData.email) : null,
      text: sanitizeText(commentData.text),
      timestamp: new Date().toISOString(),
      ip: clientIP // Store for moderation purposes
    };

    // Get existing comments
    const existingComments = await env.COMMENTS_KV.get('comments', 'json') || [];
    
    // Add new comment
    existingComments.push(comment);
    
    // Keep only last 1000 comments to manage storage
    const trimmedComments = existingComments
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      .slice(0, 1000);

    // Save to KV storage
    await env.COMMENTS_KV.put('comments', JSON.stringify(trimmedComments));

    // Update rate limit counter
    await env.COMMENTS_KV.put(rateLimitKey, (parseInt(rateCount || 0) + 1).toString(), {
      expirationTtl: RATE_LIMIT_WINDOW / 1000
    });

    // Return success response (don't include email or IP in response)
    const publicComment = {
      id: comment.id,
      name: comment.name,
      text: comment.text,
      timestamp: comment.timestamp
    };

    return new Response(JSON.stringify(publicComment), {
      status: 201,
      headers: { ...getCorsHeaders(), 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Error posting comment:', error);
    return new Response(JSON.stringify({ 
      error: 'Failed to post comment' 
    }), {
      status: 500,
      headers: { ...getCorsHeaders(), 'Content-Type': 'application/json' }
    });
  }
}

function validateComment(data) {
  if (!data.name || data.name.trim().length === 0) {
    return { valid: false, error: 'Name is required' };
  }
  
  if (data.name.trim().length > 100) {
    return { valid: false, error: 'Name must be less than 100 characters' };
  }
  
  if (!data.text || data.text.trim().length === 0) {
    return { valid: false, error: 'Comment text is required' };
  }
  
  if (data.text.trim().length > 2000) {
    return { valid: false, error: 'Comment must be less than 2000 characters' };
  }

  // Basic spam detection
  const spamPatterns = [
    /https?:\/\/[^\s]+\.(tk|ml|ga|cf)/i, // Suspicious domains
    /buy now|click here|visit my|check out my/i, // Spam phrases
    /(.)\1{10,}/, // Repeated characters
  ];

  const text = data.text.toLowerCase();
  for (const pattern of spamPatterns) {
    if (pattern.test(text)) {
      return { valid: false, error: 'Comment appears to be spam' };
    }
  }

  // Email validation (if provided)
  if (data.email && data.email.trim().length > 0) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email.trim())) {
      return { valid: false, error: 'Invalid email format' };
    }
  }

  return { valid: true };
}

function sanitizeText(text) {
  if (!text) return '';
  
  return text
    .trim()
    .replace(/<[^>]*>/g, '') // Remove HTML tags
    .replace(/[<>&"']/g, (char) => {
      const entities = {
        '<': '&lt;',
        '>': '&gt;',
        '&': '&amp;',
        '"': '&quot;',
        "'": '&#x27;'
      };
      return entities[char] || char;
    });
}

function sanitizeEmail(email) {
  if (!email) return null;
  return email.trim().toLowerCase().replace(/[<>&"']/g, '');
}

function getCorsHeaders() {
  return {
    'Access-Control-Allow-Origin': 'https://chrispaulmoore.com',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
  };
}

// Additional helper functions for moderation (future use)
async function moderateComment(comment) {
  // Placeholder for future AI-based moderation
  // Could integrate with OpenAI Moderation API or similar
  return { approved: true, reason: null };
}

async function getCommentsByIP(env, ip) {
  // Helper for admin/moderation purposes
  const comments = await env.COMMENTS_KV.get('comments', 'json') || [];
  return comments.filter(comment => comment.ip === ip);
}