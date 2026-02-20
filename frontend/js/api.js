/**
 * Configuration de l'API Backend Django
 */

// URL de base de l'API
const API_BASE_URL = window.location.origin + '/api';

// Configuration des endpoints
const API_ENDPOINTS = {
    products: `${API_BASE_URL}/products/`,
    orders: `${API_BASE_URL}/orders/`,
    contact: `${API_BASE_URL}/contact/`,
};

/**
 * Fonctions utilitaires pour les appels API
 */

async function apiCall(url, options = {}) {
    try {
        // Ensure cookies (including CSRF cookie) are sent for same-origin requests
        const finalOptions = {
            credentials: 'same-origin',
            ...options,
        };

        // Build headers and inject CSRF token for unsafe methods
        const headers = {
            'Content-Type': 'application/json',
            ...finalOptions.headers,
        };

        const method = (finalOptions.method || 'GET').toUpperCase();
        if (method !== 'GET' && method !== 'HEAD') {
            // Read CSRF token from cookie or from the hidden form input and set X-CSRFToken header
            const csrftoken = getCSRFToken();
            if (csrftoken) headers['X-CSRFToken'] = csrftoken;
        }

        // If body is a FormData, let the browser set the Content-Type (including boundary)
        if (finalOptions.body instanceof FormData) {
            // Remove Content-Type so fetch can set the correct multipart boundary
            delete headers['Content-Type'];
        }

        finalOptions.headers = headers;

        const response = await fetch(url, finalOptions);

        if (!response.ok) {
            let error = { message: 'Erreur lors de la requête' };
            
            try {
                const body = await response.json();
                error = body;
                console.error('🚨 Erreur détaillée du serveur:', {
                    status: response.status,
                    statusText: response.statusText,
                    body: body
                });

                // If body contains field errors (object), include them in the thrown message
                let detailed = '';
                if (body && typeof body === 'object') {
                    try {
                        detailed = JSON.stringify(body);
                    } catch (e) {
                        detailed = String(body);
                    }
                }
                throw new Error(body.detail || body.message || detailed || 'Erreur lors de la requête');
            } catch (e) {
                // If parsing JSON failed or we rethrew above, handle generic server error
                if (e instanceof Error && e.message && e.message !== 'Erreur lors de la requête') {
                    throw e; // rethrow detailed error
                }
                console.error('🚨 Erreur serveur (pas de JSON):', {
                    status: response.status,
                    statusText: response.statusText
                });
                throw new Error('Erreur lors de la requête');
            }
        }

        // 204 No Content -> return empty object
        if (response.status === 204) return {};

        try {
            return await response.json();
        } catch (e) {
            console.warn('⚠️ Impossible de parser la réponse en JSON:', e);
            return {};
        }
    } catch (error) {
        console.error('Erreur API:', error);
        throw error;
    }
}

// Helper: lire un cookie par nom (utilisé pour CSRF)
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// Get CSRF token from cookie or from hidden input rendered by {% csrf_token %}
function getCSRFToken() {
    const fromCookie = getCookie('csrftoken');
    if (fromCookie) return fromCookie;
    // Fallback: look for Django's csrf input in the DOM
    try {
        const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (input && input.value) return input.value;
    } catch (e) {
        // ignore
    }
    return null;
}

function unwrapListResponse(resp) {
    // DRF pagination returns an object {count, next, previous, results: [...]}
    if (resp && typeof resp === 'object' && Array.isArray(resp.results)) {
        return resp.results;
    }
    return resp;
}

/**
 * API Products
 */
const ProductsAPI = {
    // GET /api/products/ - Liste tous les produits
    getAll: async (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${API_ENDPOINTS.products}?${queryString}` : API_ENDPOINTS.products;
        const r = await apiCall(url);
        return unwrapListResponse(r) || [];
    },

    // GET /api/products/{id}/ - Détails d'un produit
    getById: async (id) => {
        return await apiCall(`${API_ENDPOINTS.products}${id}/`);
    },

    // POST /api/products/ - Créer un produit
    create: async (data) => {
        const body = data instanceof FormData ? data : JSON.stringify(data);
        return await apiCall(API_ENDPOINTS.products, {
            method: 'POST',
            body: body,
        });
    },

    // PUT /api/products/{id}/ - Mettre à jour un produit
    update: async (id, data) => {
        const body = data instanceof FormData ? data : JSON.stringify(data);
        return await apiCall(`${API_ENDPOINTS.products}${id}/`, {
            method: 'PUT',
            body: body,
        });
    },

    // PATCH /api/products/{id}/ - Mise à jour partielle
    partialUpdate: async (id, data) => {
        const body = data instanceof FormData ? data : JSON.stringify(data);
        return await apiCall(`${API_ENDPOINTS.products}${id}/`, {
            method: 'PATCH',
            body: body,
        });
    },

    // DELETE /api/products/{id}/ - Supprimer un produit
    delete: async (id) => {
        return await apiCall(`${API_ENDPOINTS.products}${id}/`, {
            method: 'DELETE',
        });
    },

    // POST /api/products/{id}/update_stock/ - Mettre à jour le stock
    updateStock: async (id, stock) => {
        return await apiCall(`${API_ENDPOINTS.products}${id}/update_stock/`, {
            method: 'POST',
            body: JSON.stringify({ stock }),
        });
    },

    // POST /api/products/{id}/toggle_availability/ - Activer/désactiver
    toggleAvailability: async (id) => {
        return await apiCall(`${API_ENDPOINTS.products}${id}/toggle_availability/`, {
            method: 'POST',
        });
    },

    // GET /api/products/low_stock/ - Produits avec stock faible
    getLowStock: async () => {
        return await apiCall(`${API_ENDPOINTS.products}low_stock/`);
    },

    // GET /api/products/out_of_stock/ - Produits en rupture
    getOutOfStock: async () => {
        return await apiCall(`${API_ENDPOINTS.products}out_of_stock/`);
    },
};

/**
 * API Orders
 */
const OrdersAPI = {
    // GET /api/orders/ - Liste toutes les commandes
    getAll: async (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${API_ENDPOINTS.orders}?${queryString}` : API_ENDPOINTS.orders;
        const r = await apiCall(url);
        return unwrapListResponse(r) || [];
    },

    // GET /api/orders/{id}/ - Détails d'une commande
    getById: async (id) => {
        return await apiCall(`${API_ENDPOINTS.orders}${id}/`);
    },

    // POST /api/orders/ - Créer une commande
    create: async (data) => {
        return await apiCall(API_ENDPOINTS.orders, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    // PUT /api/orders/{id}/ - Mettre à jour une commande
    update: async (id, data) => {
        return await apiCall(`${API_ENDPOINTS.orders}${id}/`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    // PATCH /api/orders/{id}/ - Mise à jour partielle
    partialUpdate: async (id, data) => {
        return await apiCall(`${API_ENDPOINTS.orders}${id}/`, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    },

    // DELETE /api/orders/{id}/ - Supprimer une commande
    delete: async (id) => {
        return await apiCall(`${API_ENDPOINTS.orders}${id}/`, {
            method: 'DELETE',
        });
    },

    // POST /api/orders/{id}/update_status/ - Mettre à jour le statut
    updateStatus: async (id, status) => {
        return await apiCall(`${API_ENDPOINTS.orders}${id}/update_status/`, {
            method: 'POST',
            body: JSON.stringify({ status }),
        });
    },

    // POST /api/orders/{id}/cancel/ - Annuler une commande
    cancel: async (id) => {
        return await apiCall(`${API_ENDPOINTS.orders}${id}/cancel/`, {
            method: 'POST',
        });
    },

    // POST /api/orders/{id}/confirm/ - Confirmer une commande
    confirm: async (id) => {
        return await apiCall(`${API_ENDPOINTS.orders}${id}/confirm/`, {
            method: 'POST',
        });
    },

    // GET /api/orders/statistics/ - Statistiques des commandes
    getStatistics: async () => {
        return await apiCall(`${API_ENDPOINTS.orders}statistics/`);
    },
};

/**
 * API Contact
 */
const ContactAPI = {
    // GET /api/contact/ - Liste tous les messages
    getAll: async (params = {}) => {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${API_ENDPOINTS.contact}?${queryString}` : API_ENDPOINTS.contact;
        const r = await apiCall(url);
        return unwrapListResponse(r) || [];
    },

    // GET /api/contact/{id}/ - Détails d'un message
    getById: async (id) => {
        return await apiCall(`${API_ENDPOINTS.contact}${id}/`);
    },

    // POST /api/contact/ - Envoyer un message
    create: async (data) => {
        return await apiCall(API_ENDPOINTS.contact, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    // POST /api/contact/{id}/mark_as_read/ - Marquer comme lu
    markAsRead: async (id) => {
        return await apiCall(`${API_ENDPOINTS.contact}${id}/mark_as_read/`, {
            method: 'POST',
        });
    },

    // POST /api/contact/{id}/mark_as_replied/ - Marquer comme répondu
    markAsReplied: async (id) => {
        return await apiCall(`${API_ENDPOINTS.contact}${id}/mark_as_replied/`, {
            method: 'POST',
        });
    },

    // GET /api/contact/unread/ - Messages non lus
    getUnread: async () => {
        return await apiCall(`${API_ENDPOINTS.contact}unread/`);
    },
};

// Exporter les API
window.ProductsAPI = ProductsAPI;
window.OrdersAPI = OrdersAPI;
window.ContactAPI = ContactAPI;
