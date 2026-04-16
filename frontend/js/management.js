/**
 * Gestion de la section Management avec API Django REST
 * Gestion des produits, stocks et commandes
 */

/**
 * Charge la page de gestion
 */
async function loadManagement() {
    // console.log('⚙️ Chargement de la gestion...');
    
    // Configurer les onglets
    setupManagementTabs();
    
    // Charger l'onglet actif
    const activeTab = document.querySelector('.tab-btn.active');
    if (activeTab) {
        const tabId = activeTab.getAttribute('data-tab');
        showManagementTab(tabId);
    } else {
        showManagementTab('products-management');
    }
}

/**
 * Configure les onglets de gestion
 */
function setupManagementTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Retirer la classe active de tous les boutons
            tabBtns.forEach(b => b.classList.remove('active'));
            
            // Ajouter la classe active au bouton cliqué
            this.classList.add('active');
            
            // Afficher le panneau correspondant
            const tabId = this.getAttribute('data-tab');
            showManagementTab(tabId);
        });
    });
}

/**
 * Affiche un onglet de gestion
 * @param {string} tabId - ID de l'onglet
 */
async function showManagementTab(tabId) {
    // console.log('🔄 Affichage de l\'onglet:', tabId);
    
    // Cacher tous les panneaux
    const panels = document.querySelectorAll('.tab-panel');
    // console.log('📋 Panneaux trouvés:', panels.length);
    panels.forEach(panel => {
        panel.classList.remove('active');
        // console.log('❌ Panneau masqué:', panel.id);
    });
    
    // Afficher le panneau demandé
    const targetPanel = document.getElementById(tabId);
    if (targetPanel) {
        targetPanel.classList.add('active');
        // console.log('✅ Panneau affiché:', tabId);
        
        // Charger les données selon l'onglet
        switch(tabId) {
            case 'products-management':
                await loadProductsForManagement();
                break;
            case 'stock-management':
                await loadStockManagement();
                break;
            case 'orders-management':
                await loadOrdersManagement();
                break;
            case 'messages-management':
                // Les messages sont chargés via un listener séparé
                break;
            case 'users-management':
                // Les utilisateurs sont chargés via un listener séparé dans admin.html
                break;
        }
    } else {
        console.error('❌ Panneau non trouvé:', tabId);
    }
}

function normalizeListResponse(resp) {
    if (!resp) return [];
    if (Array.isArray(resp)) return resp;
    // DRF pagination
    if (typeof resp === 'object' && Array.isArray(resp.results)) return resp.results;
    // Some APIs return {data: [...]}
    if (typeof resp === 'object' && Array.isArray(resp.data)) return resp.data;
    // If it's an object with numeric keys like {'0': {...}, '1': {...}}
    if (typeof resp === 'object') {
        const vals = Object.values(resp);
        const allObjects = vals.length && vals.every(v => typeof v === 'object');
        if (allObjects) return vals;
    }
    // Fallback: wrap single item
    return [resp];
}

/**
 * Charge la gestion des stocks
 */
async function loadStockManagement() {
    const container = document.getElementById('stockGrid');
    if (!container) return;
    
    try {
        container.innerHTML = '<div class="loading">Chargement...</div>';
        
        // Récupérer tous les produits
        let products = await ProductsAPI.getAll();
        // console.log('management.loadStockManagement - raw products:', products);
        products = normalizeListResponse(products);

        container.innerHTML = '';

        if (products.length === 0) {
            container.innerHTML = '<div class="no-data">Aucun produit</div>';
            return;
        }

        // Créer un tableau de gestion des stocks
        products.forEach(product => {
            const stockCard = createStockCard(product);
            container.appendChild(stockCard);
        });
    } catch (error) {
        console.error('Erreur:', error);
        container.innerHTML = '<div class="error">Erreur de chargement</div>';
    }
}

/**
 * Crée une carte de gestion des stocks
 * @param {Object} product - Données du produit
 * @returns {HTMLElement} Carte de stock
 */
function createStockCard(product) {
    const card = document.createElement('div');
    card.className = 'stock-card';
    
    let stockClass = 'stock-good';
    if (product.stock === 0) {
        stockClass = 'stock-empty';
    } else if (product.stock <= 5) {
        stockClass = 'stock-low';
    }
    
    card.innerHTML = `
        <div class="stock-header">
            <h4>${product.name}</h4>
            <span class="stock-badge ${stockClass}">${product.stock}</span>
        </div>
        <div class="stock-body">
            <p class="stock-category">${getCategoryName(product.category)}</p>
            <p class="stock-status">${product.stock_status}</p>
        </div>
        <div class="stock-actions">
            <input type="number" 
                   id="stock-${product.id}" 
                   value="${product.stock}" 
                   min="0" 
                   class="stock-input">
            <button class="btn btn-primary" onclick="updateProductStock(${product.id})">
                <i class="fas fa-save"></i> Mettre à jour
            </button>
        </div>
    `;
    
    return card;
}

/**
 * Met à jour le stock d'un produit
 * @param {number} productId - ID du produit
 */
async function updateProductStock(productId) {
    const input = document.getElementById(`stock-${productId}`);
    const newStock = parseInt(input.value);
    
    if (isNaN(newStock) || newStock < 0) {
        showNotification('Valeur de stock invalide', 'error');
        return;
    }
    
    try {
        await ProductsAPI.updateStock(productId, newStock);
        showNotification('Stock mis à jour', 'success');
        await loadStockManagement();
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Erreur: ' + error.message, 'error');
    }
}

/**
 * Charge la gestion des commandes
 */
async function loadOrdersManagement() {
    const container = document.getElementById('ordersManagementGrid');
    if (!container) return;
    
    try {
        container.innerHTML = '<div class="loading">Chargement...</div>';
        
        // Récupérer toutes les commandes
        let orders = await OrdersAPI.getAll();
        // console.log('management.loadOrdersManagement - raw orders:', orders);
        orders = normalizeListResponse(orders);

        container.innerHTML = '';

        if (orders.length === 0) {
            container.innerHTML = '<div class="no-data">Aucune commande</div>';
            return;
        }

        // Afficher chaque commande
        orders.forEach(order => {
            const orderCard = createOrderManagementCard(order);
            container.appendChild(orderCard);
        });
    } catch (error) {
        console.error('Erreur:', error);
        container.innerHTML = '<div class="error">Erreur de chargement</div>';
    }
}

/**
 * Crée une carte de gestion de commande (vue complète admin)
 * @param {Object} order - Données de la commande
 * @returns {HTMLElement} Carte de commande
 */
function createOrderManagementCard(order) {
    const card = document.createElement('div');
    card.className = 'order-management-card';
    
    const statusClass = getOrderStatusClass(order.status);
    const statusLabel = order.status_label || getOrderStatusLabel(order.status);
    
    // Options de statut
    const statusOptions = [
        { value: 'pending', label: 'En préparation' },
        { value: 'paid', label: 'Payée' },
        { value: 'ready', label: 'Prête' },
        { value: 'delivered', label: 'Livrée' },
        { value: 'cancelled', label: 'Annulée' }
    ];
    
    const statusSelect = statusOptions.map(opt => 
        `<option value="${opt.value}" ${opt.value === order.status ? 'selected' : ''}>${opt.label}</option>`
    ).join('');

    // Liste complète des articles (comme côté client)
    const items = order.items || [];
    const itemsList = items.map(item => `
        <div class="admin-order-item">
            <span class="item-qty-badge">${item.quantity}x</span>
            <span class="item-name-text">${item.product_name || (item.product_details && item.product_details.name) || 'Produit'}</span>
            <span class="item-price-text">${formatPrice(item.unit_price)} / unité</span>
            <span class="item-total-text"><strong>${formatPrice(item.total_price)}</strong></span>
        </div>
    `).join('');
    
    card.innerHTML = `
        <div class="order-management-header">
            <div class="order-info">
                <h4>Commande #${order.id}</h4>
                <p class="order-date"><i class="fas fa-calendar-alt"></i> ${formatDate(order.created_at)}</p>
            </div>
            <span class="order-status ${statusClass}">${statusLabel}</span>
        </div>
        <div class="order-management-body">
            <!-- Informations client -->
            <div class="admin-order-section">
                <h5><i class="fas fa-user"></i> Client</h5>
                <p><strong>${order.customer_name}</strong></p>
                ${order.customer_email ? `<p><i class="fas fa-envelope"></i> ${order.customer_email}</p>` : ''}
                ${order.customer_phone ? `<p><i class="fas fa-phone"></i> ${order.customer_phone}</p>` : ''}
            </div>
            <!-- Articles commandés -->
            <div class="admin-order-section">
                <h5><i class="fas fa-shopping-basket"></i> Articles (${order.items_count || items.length})</h5>
                <div class="admin-order-items-list">
                    ${itemsList || '<p class="text-muted">Aucun article</p>'}
                </div>
            </div>
            <!-- Total et remboursement -->
            <div class="admin-order-section admin-order-total">
                <div class="total-row">
                    <span>Total de la commande :</span>
                    <strong>${formatPrice(order.total_price)}</strong>
                </div>
                ${order.refund_amount > 0 ? `
                <div class="total-row refund-row">
                    <span>Montant remboursé :</span>
                    <strong>${formatPrice(order.refund_amount)}</strong>
                </div>` : ''}
            </div>
            <!-- Notes -->
            ${order.notes ? `
            <div class="admin-order-section">
                <h5><i class="fas fa-sticky-note"></i> Notes</h5>
                <p class="order-notes-text">${order.notes}</p>
            </div>` : ''}
            <!-- Mise à jour du statut -->
            <div class="admin-order-section">
                <h5><i class="fas fa-edit"></i> Modifier le statut</h5>
                <div class="order-management-actions">
                    <select class="status-select" id="status-${order.id}">
                        ${statusSelect}
                    </select>
                    <button class="btn btn-primary" onclick="updateOrderStatus(${order.id})">
                        <i class="fas fa-save"></i> Mettre à jour
                    </button>
                    ${order.status !== 'cancelled' && order.status !== 'delivered' ? `
                        <button class="btn btn-danger" onclick="cancelOrderFromManagement(${order.id})">
                            <i class="fas fa-times"></i> Annuler
                        </button>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
    
    return card;
}

/**
 * Met à jour le statut d'une commande
 * @param {number} orderId - ID de la commande
 */
async function updateOrderStatus(orderId) {
    const select = document.getElementById(`status-${orderId}`);
    const newStatus = select.value;
    
    try {
        await OrdersAPI.updateStatus(orderId, newStatus);
        showNotification('Statut mis à jour', 'success');
        await loadOrdersManagement();
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Erreur: ' + error.message, 'error');
    }
}

/**
 * Annule une commande depuis la gestion
 * @param {number} orderId - ID de la commande
 */
async function cancelOrderFromManagement(orderId) {
    if (!confirm('Êtes-vous sûr de vouloir annuler cette commande ?')) {
        return;
    }
    
    try {
        await OrdersAPI.cancel(orderId);
        showNotification('Commande annulée', 'success');
        await loadOrdersManagement();
        
        // Recharger les stocks si on est sur l'onglet stock
        const stockTab = document.getElementById('stock-management');
        if (stockTab && stockTab.classList.contains('active')) {
            await loadStockManagement();
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Erreur: ' + error.message, 'error');
    }
}

// Exporter les fonctions
window.loadManagement = loadManagement;
window.updateProductStock = updateProductStock;
window.updateOrderStatus = updateOrderStatus;
window.cancelOrderFromManagement = cancelOrderFromManagement;
window.createOrderManagementCard = createOrderManagementCard;
window.showManagementTab = showManagementTab; // Pour debug

// Fonction de test pour les onglets
window.testTabs = function() {
    // console.log('🧪 Test des onglets de gestion');
    const tabs = ['products-management', 'stock-management', 'orders-management', 'messages-management'];
    tabs.forEach(tab => {
        const element = document.getElementById(tab);
        console.log(`📁 Onglet ${tab}:`, element ? '✅ trouvé' : '❌ non trouvé');
        if (element) {
            console.log(`🎯 Classes: ${element.className}`);
        }
    });
    
    const buttons = document.querySelectorAll('.tab-btn');
    // console.log(`🔘 Boutons d'onglets trouvés: ${buttons.length}`);
    buttons.forEach(btn => {
        // console.log(`🔘 Bouton: ${btn.getAttribute('data-tab')} - ${btn.className}`);
    });
};
