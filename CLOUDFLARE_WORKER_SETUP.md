# Cloudflare Worker Comments System Setup

This guide walks through setting up the comments system using Cloudflare Workers.

## Prerequisites

1. Cloudflare account with your domain (chrispaulmoore.com)
2. Wrangler CLI installed: `npm install -g wrangler`
3. Authenticated with Cloudflare: `wrangler auth login`

## Setup Steps

### 1. Create KV Namespace

```bash
# Create the KV namespace for storing comments
wrangler kv:namespace create "COMMENTS_KV"
wrangler kv:namespace create "COMMENTS_KV" --preview
```

This will output namespace IDs. Update `wrangler.toml` with the actual IDs.

### 2. Deploy the Worker

```bash
# Deploy to Cloudflare
wrangler deploy
```

### 3. Set up Custom Domain

1. Go to Cloudflare Dashboard > Workers & Pages
2. Find your `comments-system` worker
3. Go to Settings > Triggers
4. Add custom domain: `comments.chrispaulmoore.com`

### 4. Update DNS

Add a CNAME record in your Cloudflare DNS:
- Type: CNAME
- Name: comments
- Target: comments-system.your-subdomain.workers.dev
- Proxy status: Proxied (orange cloud)

### 5. Test the API

```bash
# Test health endpoint
curl https://comments.chrispaulmoore.com/health

# Test getting comments (should return empty array initially)
curl https://comments.chrispaulmoore.com/comments

# Test posting a comment
curl -X POST https://comments.chrispaulmoore.com/comments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "text": "This is a test comment!"
  }'
```

## Features

### Security Features
- **CORS Protection**: Only allows requests from chrispaulmoore.com
- **Rate Limiting**: Max 5 comments per minute per IP
- **Input Validation**: Sanitizes all input and validates formats
- **Spam Detection**: Basic patterns to catch obvious spam
- **HTML Sanitization**: Removes HTML tags and escapes special characters

### Storage
- **KV Storage**: Comments stored in Cloudflare KV
- **Auto-cleanup**: Keeps only the latest 1000 comments
- **Privacy**: Email addresses are stored but not returned in public API

### API Endpoints

#### GET /comments
Returns the latest 50 comments, sorted by newest first.

#### POST /comments
Posts a new comment. Requires:
- `name` (required, max 100 chars)
- `text` (required, max 2000 chars)  
- `email` (optional, validated format)

#### GET /health
Health check endpoint

## Local Development

```bash
# Run locally with wrangler
wrangler dev

# The local dev server will be available at http://localhost:8787
```

## Monitoring

Check worker analytics in the Cloudflare dashboard:
- Workers & Pages > comments-system > Analytics
- Monitor requests, errors, and performance

## Future Enhancements

1. **Admin Dashboard**: Create admin interface for comment moderation
2. **AI Moderation**: Integrate OpenAI Moderation API
3. **Email Notifications**: Notify when new comments are posted
4. **Reply System**: Add threaded replies to comments
5. **User Authentication**: Optional user accounts with profiles

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure the worker is deployed and domain is configured correctly
2. **Rate Limiting**: Wait a minute between test requests
3. **KV Not Found**: Check that KV namespace IDs are correct in wrangler.toml

### Debug Tips

Check worker logs:
```bash
wrangler tail
```

View KV contents:
```bash
wrangler kv:key list --binding=COMMENTS_KV
wrangler kv:key get "comments" --binding=COMMENTS_KV
```