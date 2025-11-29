// Centralized API configuration
// Strip trailing slash to prevent double-slash URLs
const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';
export const API_BASE_URL = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
