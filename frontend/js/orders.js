/**
 * Gestion des commandes avec API Django REST
 */

/**
 * Charge et affiche les commandes depuis l'API
 */
async function loadOrders() {
    // console.log('📦 Chargement des commandes depuis l\'API...');
    
    const ordersContainer = document.getElementById('ordersContainer');
    if (!ordersContainer) return;
    
    try {
        // Afficher un loader
        ordersContainer.innerHTML = '<div class="loading">Chargement des commandes...</div>';
        
        // Récupérer les commandes depuis l'API
        let orders = await OrdersAPI.getAll();

        // Normaliser la réponse (pagination DRF etc.)
        orders = normalizeList(orders);

        // Vider le conteneur
        ordersContainer.innerHTML = '';

        if (orders.length === 0) {
            ordersContainer.innerHTML = '<div class="no-data">Aucune commande pour le moment</div>';
            return;
        }

        // Afficher chaque commande
        orders.forEach(order => {
            const orderCard = createOrderCard(order);
            ordersContainer.appendChild(orderCard);
        });
        
        // console.log(`✅ ${orders.length} commandes chargées`);
    } catch (error) {
        console.error('❌ Erreur lors du chargement des commandes:', error);
        ordersContainer.innerHTML = '<div class="error">Erreur lors du chargement des commandes</div>';
        showNotification('Erreur lors du chargement des commandes', 'error');
    }
}

/**
 * Crée une carte de commande
 * @param {Object} order - Données de la commande
 * @returns {HTMLElement} Carte de commande
 */
function createOrderCard(order) {
    const card = document.createElement('div');
    card.className = 'order-card';
    
    const statusClass = getOrderStatusClass(order.status);
    const statusLabel = order.status_label || getOrderStatusLabel(order.status);
    
    // Créer la liste des articles
    const itemsList = order.items.map(item => `
        <div class="order-item">
            <span class="item-quantity">${item.quantity}x</span>
            <span class="item-name">${item.product_name}</span>
            <span class="item-price">${formatPrice(item.total_price)}</span>
        </div>
    `).join('');
    
    card.innerHTML = `
        <div class="order-header">
            <div class="order-info">
                <h4>Commande #${order.id}</h4>
                <p class="order-customer">${order.customer_name}</p>
                <p class="order-date">${formatDate(order.created_at)}</p>
            </div>
            <span class="order-status ${statusClass}">${statusLabel}</span>
        </div>
        <div class="order-body">
            <div class="order-items-summary">
                <strong>${order.items_count} article(s)</strong> - ${formatPrice(order.total_price)}
            </div>
        </div>
        <div class="order-footer">
            <div class="order-actions">
                ${order.status === 'pending' ? `
                    <button class="btn btn-sm btn-primary" onclick="editOrder(${order.id})">
                        <i class="fas fa-edit"></i> Modifier
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="cancelOrder(${order.id})">
                        <i class="fas fa-times"></i> Annuler
                    </button>
                ` : ''}
                <button class="btn btn-sm btn-info" onclick="showOrderDetails(${order.id})">
                    <i class="fas fa-eye"></i> Détails
                </button>
            </div>
        </div>
    `;
    
    return card;
}

/**
 * Affiche les détails d'une commande dans une popup
 * @param {number} orderId - ID de la commande
 */
async function showOrderDetails(orderId) {
    try {
        const order = await OrdersAPI.getById(orderId);
        showOrderPopup(order, 'details');
    } catch (error) {
        console.error('❌ Erreur lors du chargement des détails:', error);
        showNotification('Erreur lors du chargement des détails de la commande', 'error');
    }
}

/**
 * Modifie une commande
 * @param {number} orderId - ID de la commande
 */
async function editOrder(orderId) {
    try {
        const order = await OrdersAPI.getById(orderId);
        showOrderPopup(order, 'edit');
    } catch (error) {
        console.error('❌ Erreur lors du chargement pour modification:', error);
        showNotification('Erreur lors du chargement de la commande pour modification', 'error');
    }
}

/**
 * Annule une commande
 * @param {number} orderId - ID de la commande
 */
async function cancelOrder(orderId) {
    // console.log('🔄 Tentative d\'annulation de la commande:', orderId);
    
    if (!confirm('Êtes-vous sûr de vouloir annuler cette commande ?\n\nLe stock sera automatiquement restauré.')) {
        console.log('❌ Annulation annulée par l\'utilisateur');
        return;
    }
    
    try {
        // console.log('📡 Appel API pour annuler la commande:', orderId);
        const result = await OrdersAPI.cancel(orderId);
        // console.log('✅ Commande annulée avec succès:', result);
        
        // Afficher une notification détaillée
        const restoredItems = result.items || [];
        let message = 'Commande annulée avec succès !';
        
        if (restoredItems.length > 0) {
            const itemsList = restoredItems.map(item => 
                `${item.quantity}x ${item.product_name}`
            ).join(', ');
            message += `\n\n✅ Actions effectuées :\n`;
            message += `• Statut changé vers "Annulée"\n`;
            message += `• Stock restauré pour : ${itemsList}\n`;
            message += `• Liste des commandes mise à jour`;
        } else {
            message += '\n\nStatut changé vers "Annulée"';
        }
        
        showNotification(message, 'success');
        
        // Afficher l'indicateur visuel de stock restauré
        if (restoredItems.length > 0) {
            showStockRestoredIndicator(restoredItems);
        }
        
        // Recharger les commandes
        loadOrders();
        
        // Si on est sur la page produits, recharger aussi pour voir le stock mis à jour
        if (app.currentPage === 'products') {
            await loadProducts();
        }
        
    } catch (error) {
        console.error('❌ Erreur lors de l\'annulation:', error);
        console.error('Détails de l\'erreur:', error.message);
        
        let errorMessage = 'Erreur lors de l\'annulation de la commande';
        
        // Messages d'erreur spécifiques selon le type d'erreur
        if (error.message) {
            if (error.message.includes('déjà annulée')) {
                errorMessage = 'Cette commande est déjà annulée';
            } else if (error.message.includes('déjà livrée')) {
                errorMessage = 'Impossible d\'annuler une commande déjà livrée';
            } else if (error.message.includes('Stock insuffisant')) {
                errorMessage = 'Erreur lors de la restauration du stock';
            } else {
                errorMessage += ': ' + error.message;
            }
        }
        
        showNotification(errorMessage, 'error');
    }
}

/**
 * Affiche un indicateur visuel de stock restauré
 * @param {Array} items - Liste des articles dont le stock a été restauré
 */
function showStockRestoredIndicator(items) {
    if (!items || items.length === 0) return;
    
    // Créer un indicateur temporaire
    const indicator = document.createElement('div');
    indicator.className = 'stock-restored-indicator';
    indicator.innerHTML = `
        <div class="indicator-content">
            <i class="fas fa-undo"></i>
            <span>Stock restauré !</span>
        </div>
    `;
    
    // Ajouter au DOM
    document.body.appendChild(indicator);
    
    // Animation
    setTimeout(() => indicator.classList.add('show'), 10);
    
    // Retirer après 3 secondes
    setTimeout(() => {
        indicator.classList.remove('show');
        setTimeout(() => document.body.removeChild(indicator), 300);
    }, 3000);
}

/**
 * Affiche une popup avec les détails ou le formulaire de modification d'une commande
 * @param {Object} order - Données de la commande
 * @param {string} mode - 'details' ou 'edit'
 */
function showOrderPopup(order, mode = 'details') {
    // Créer la popup
    const popup = document.createElement('div');
    popup.className = 'modal-overlay';
    popup.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>${mode === 'edit' ? 'Modifier la commande' : 'Détails de la commande'}</h3>
                <button class="modal-close" onclick="closeOrderPopup()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                ${mode === 'edit' ? createOrderEditForm(order) : createOrderDetailsContent(order)}
            </div>
            ${mode === 'edit' ? `
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="closeOrderPopup()">Annuler</button>
                    <button class="btn btn-primary" onclick="saveOrderChanges(${order.id})">Enregistrer</button>
                </div>
            ` : ''}
        </div>
    `;
    
    // Ajouter au DOM
    document.body.appendChild(popup);
    
    // Animation d'apparition
    setTimeout(() => popup.classList.add('show'), 10);
}

/**
 * Crée le contenu des détails de la commande
 * @param {Object} order - Données de la commande
 * @returns {string} HTML des détails
 */
function createOrderDetailsContent(order) {
    const itemsList = order.items.map(item => `
        <div class="order-item-detail">
            <div class="item-header">
                <span class="item-quantity">${item.quantity}x</span>
                <span class="item-name">${item.product_name}</span>
                <span class="item-price">${formatPrice(item.total_price)}</span>
            </div>
            <div class="item-details">
                <small>Prix unitaire: ${formatPrice(item.price)}</small>
            </div>
        </div>
    `).join('');
    
    return `
        <div class="order-details">
            <div class="order-info-section">
                <h4>Informations</h4>
                <p><strong>Commande #${order.id}</strong></p>
                <p>Date: ${formatDate(order.created_at)}</p>
                <p>Statut: <span class="order-status ${getOrderStatusClass(order.status)}">${getOrderStatusLabel(order.status)}</span></p>
            </div>
            
            <div class="order-customer-section">
                <h4>Client</h4>
                <p><strong>${order.customer_name}</strong></p>
                ${order.customer_email ? `<p>Email: ${order.customer_email}</p>` : ''}
                ${order.customer_phone ? `<p>Téléphone: ${order.customer_phone}</p>` : ''}
            </div>
            
            <div class="order-items-section">
                <h4>Articles (${order.items_count})</h4>
                <div class="items-list">
                    ${itemsList}
                </div>
            </div>
            
            ${order.notes ? `
                <div class="order-notes-section">
                    <h4>Notes</h4>
                    <p>${order.notes}</p>
                </div>
            ` : ''}
            
            <div class="order-total-section">
                <h4>Total</h4>
                <p class="total-amount">${formatPrice(order.total_price)}</p>
            </div>
        </div>
    `;
}

/**
 * Crée le formulaire de modification de commande
 * @param {Object} order - Données de la commande
 * @returns {string} HTML du formulaire
 */
function createOrderEditForm(order) {
    return `
        <form id="orderEditForm">
            <div class="form-group">
                <label for="editCustomerName">Nom du client</label>
                <input type="text" id="editCustomerName" name="customer_name" value="${order.customer_name}" required>
            </div>
            
            <div class="form-group">
                <label for="editCustomerEmail">Email</label>
                <input type="email" id="editCustomerEmail" name="customer_email" value="${order.customer_email || ''}">
            </div>
            
            <div class="form-group">
                <label for="editCustomerPhone">Téléphone</label>
                <input type="tel" id="editCustomerPhone" name="customer_phone" value="${order.customer_phone || ''}">
            </div>
            
            <div class="form-group">
                <label for="editNotes">Notes</label>
                <textarea id="editNotes" name="notes" rows="3">${order.notes || ''}</textarea>
            </div>
            
            <div class="form-group">
                <label>Articles</label>
                <div class="order-items-edit">
                    ${order.items.map((item, index) => `
                        <div class="item-edit-row">
                            <span>${item.product_name}</span>
                            <div class="item-quantity-control">
                                <button type="button" onclick="updateItemQuantity(${index}, -1)">-</button>
                                <input type="number" id="itemQty${index}" value="${item.quantity}" min="1" readonly>
                                <button type="button" onclick="updateItemQuantity(${index}, 1)">+</button>
                            </div>
                            <span>${formatPrice(item.total_price)}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        </form>
    `;
}

/**
 * Ferme la popup de commande
 */
function closeOrderPopup() {
    const popup = document.querySelector('.modal-overlay');
    if (popup) {
        popup.classList.remove('show');
        setTimeout(() => popup.remove(), 300);
    }
}

/**
 * Met à jour la quantité d'un article dans le formulaire
 * @param {number} index - Index de l'article
 * @param {number} change - Changement de quantité
 */
function updateItemQuantity(index, change) {
    const input = document.getElementById(`itemQty${index}`);
    const newValue = parseInt(input.value) + change;
    if (newValue >= 1) {
        input.value = newValue;
        updateOrderTotal();
    }
}

/**
 * Met à jour le total de la commande
 */
function updateOrderTotal() {
    // Cette fonction pourrait être implémentée pour recalculer le total
    // Pour l'instant, elle sert de placeholder
    // console.log('Mise à jour du total de la commande');
}

/**
 * Sauvegarde les modifications d'une commande
 * @param {number} orderId - ID de la commande
 */
async function saveOrderChanges(orderId) {
    const form = document.getElementById('orderEditForm');
    const formData = new FormData(form);
    
    try {
        // Préparer les données pour l'API
        const updateData = {
            customer_name: formData.get('customer_name'),
            customer_email: formData.get('customer_email'),
            customer_phone: formData.get('customer_phone'),
            notes: formData.get('notes')
        };
        
        await OrdersAPI.update(orderId, updateData);
        showNotification('Commande modifiée avec succès', 'success');
        closeOrderPopup();
        loadOrders(); // Recharger la liste
    } catch (error) {
        console.error('❌ Erreur lors de la modification:', error);
        showNotification('Erreur lors de la modification de la commande', 'error');
    }
}

// Charger automatiquement les commandes quand la page est affichée
window.loadOrders = loadOrders;
window.showOrderDetails = showOrderDetails;
window.editOrder = editOrder;
window.cancelOrder = cancelOrder;
window.closeOrderPopup = closeOrderPopup;
window.updateItemQuantity = updateItemQuantity;
window.saveOrderChanges = saveOrderChanges;

// Normalise une réponse API en tableau
function normalizeList(resp) {
    if (!resp) return [];
    if (Array.isArray(resp)) return resp;
    if (typeof resp === 'object' && Array.isArray(resp.results)) return resp.results;
    if (typeof resp === 'object' && Array.isArray(resp.data)) return resp.data;
    if (typeof resp === 'object') {
        const vals = Object.values(resp);
        const allObjects = vals.length && vals.every(v => typeof v === 'object');
        if (allObjects) return vals;
    }
    return [resp];
}

// Exporter les fonctions pour l'accès global
window.loadOrders = loadOrders;
window.showOrderDetails = showOrderDetails;
window.editOrder = editOrder;
window.cancelOrder = cancelOrder;
window.closeOrderPopup = closeOrderPopup;
window.updateItemQuantity = updateItemQuantity;
window.saveOrderChanges = saveOrderChanges;
window.updateOrderTotal = updateOrderTotal;
window.showStockRestoredIndicator = showStockRestoredIndicator;
