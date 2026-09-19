import { fastapiPantryApi } from '../adapters/fastapi/fastapiPantryApi';
import { fastapiRecipeApi } from '../adapters/fastapi/fastapiRecipeApi';
import { fastapiShoppingApi } from '../adapters/fastapi/fastapiShoppingApi';
import { fastapiReceiptApi } from '../adapters/fastapi/fastapiReceiptApi';

export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true';

export async function fetchApi(endpoint: string, options: RequestInit = {}) {
  // Prevent ERR_CONNECTION_REFUSED network errors in Lighthouse/Demo mode
  if (isDemoMode) {
    // Simulate latency
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Return empty arrays to prevent frontend console errors without faking business data
    if (endpoint.includes('/api/pantry')) return [];
    if (endpoint.includes('/api/recipes/recommended')) return [];
    if (endpoint.includes('/api/shopping')) return [];
    return null;
  }
  
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    }
  });
  
  if (!res.ok) {
    throw new Error(`API Error: ${res.status}`);
  }
  
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  pantry: fastapiPantryApi,
  recipes: fastapiRecipeApi,
  shopping: fastapiShoppingApi,
  receipt: fastapiReceiptApi,
};
