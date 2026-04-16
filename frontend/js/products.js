/**
 * Gestion des produits avec API Django REST
 * CRUD des produits et affichage
 */

/**
 * Charge et affiche les produits depuis l'API
 */
async function loadProducts() {
    // console.log('🍰 Chargement des produits depuis l\'API... (debug)');
    
    const productsGrid = document.getElementById('productsGrid');
    if (!productsGrid) return;
    
    try {
        // Afficher un loader
        productsGrid.innerHTML = '<div class="loading">Chargement des produits...</div>';
        
        // Récupérer les produits depuis l'API
        let products = await ProductsAPI.getAll({ available: true });
        // console.log('products.raw ->', products);

        // Normaliser la réponse pour accepter paginated objects, objets ou tableaux
        products = normalizeList(products);
        // console.log('products.normalized ->', products);

        // Vider la grille
        productsGrid.innerHTML = '';

        // Afficher chaque produit
        try {
            products.forEach(product => {
                const productCard = createProductCard(product);
                productsGrid.appendChild(productCard);
            });
        } catch (e) {
            console.error('Erreur lors du rendu des produits:', e, products);
            productsGrid.innerHTML = '<div class="error">Erreur d\'affichage des produits</div>';
        }
        
        // console.log(`✅ ${products.length} produits chargés`);
        
        if (products.length === 0) {
            productsGrid.innerHTML = '<div class="no-data">Aucun produit disponible pour le moment</div>';
        }
    } catch (error) {
        console.error('❌ Erreur lors du chargement des produits:', error);
        productsGrid.innerHTML = '<div class="error">Erreur lors du chargement des produits</div>';
        showNotification('Erreur lors du chargement des produits', 'error');
    }
}

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

/**
 * Crée une carte produit
 * @param {Object} product - Données du produit
 * @returns {HTMLElement} Carte produit
 */
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    // Vérifier si le produit est en stock
    const inStock = product.stock > 0 && product.available;
    const stockText = product.stock > 0 ? `${product.stock} disponibles` : 'En rupture';
    const stockClass = inStock ? 'in-stock' : 'out-of-stock';
    
    // Déterminer l'icône selon la catégorie
    const categoryIcons = {
        'gateaux': 'fas fa-birthday-cake',
        'patisseries': 'fas fa-cookie',
        'viennoiseries': 'fas fa-bread-slice',
        'macarons': 'fas fa-circle',
        'chocolats': 'fas fa-candy-cane'
    };
    
    const iconClass = categoryIcons[product.category] || 'fas fa-birthday-cake';
    
    card.innerHTML = `
        <div class="product-image">
            ${getProductImage(product) ? 
                `<img src="${getProductImage(product)}" alt="${product.name}" onerror="this.parentElement.innerHTML='<i class=\\"${iconClass}\\"></i>'">` :
                `<i class="${iconClass}"></i>`
            }
        </div>
        <div class="product-info">
            <h3 class="product-name">${product.name}</h3>
            <p class="product-description">${product.description}</p>
            <div class="product-footer">
                <span class="product-price">${formatPrice(product.price)}</span>
                <span class="product-stock ${stockClass}">${stockText}</span>
            </div>
            ${inStock ? 
                `<button class="btn btn-primary" onclick="showOrderDialog(${product.id})">
                    <i class="fas fa-cart-plus"></i> Commander
                </button>` :
                `<button class="btn btn-secondary" disabled>
                    <i class="fas fa-times-circle"></i> Rupture
                </button>`
            }
        </div>
    `;
    
    return card;
}

/**
 * Affiche une popup pour créer une commande
 * @param {number} productId - ID du produit
 */
async function showOrderDialog(productId) {
    try {
        const product = await ProductsAPI.getById(productId);
        
        if (product.stock <= 0) {
            showNotification('Ce produit est en rupture de stock', 'error');
            return;
        }
        
        // Créer la popup
        const popup = document.createElement('div');
        popup.className = 'modal-overlay';
        popup.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Passer une commande</h3>
                    <button class="modal-close" onclick="closeOrderDialog()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="product-summary">
                        <h4>${product.name}</h4>
                        <p class="product-price">${formatPrice(product.price)}</p>
                        <p class="stock-info">Stock disponible: ${product.stock}</p>
                    </div>
                    
                    <form id="orderForm">
                        <div class="form-group">
                            <label for="customerName">Nom du client *</label>
                            <input type="text" id="customerName" name="customer_name" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="customerEmail">Email</label>
                            <input type="email" id="customerEmail" name="customer_email" placeholder="optionnel">
                        </div>
                        
                        <div class="form-group">
                            <label for="customerPhone">Téléphone</label>
                            <input type="tel" id="customerPhone" name="customer_phone" placeholder="optionnel">
                        </div>
                        
                        <div class="form-group">
                            <label for="quantity">Quantité *</label>
                            <div class="quantity-control">
                                <button type="button" onclick="updateQuantity(-1)">-</button>
                                <input type="number" id="quantity" name="quantity" value="1" min="1" max="${product.stock}" required>
                                <button type="button" onclick="updateQuantity(1)">+</button>
                            </div>
                            <small>Maximum: ${product.stock}</small>
                        </div>
                        
                        <div class="form-group">
                            <label for="notes">Notes</label>
                            <textarea id="notes" name="notes" rows="3" placeholder="Instructions spéciales..."></textarea>
                        </div>
                        
                        <div class="order-summary">
                            <div class="summary-row">
                                <span>Prix unitaire:</span>
                                <span id="unitPrice">${formatPrice(product.price)}</span>
                            </div>
                            <div class="summary-row">
                                <span>Quantité:</span>
                                <span id="totalQuantity">1</span>
                            </div>
                            <div class="summary-row total">
                                <strong>Total:</strong>
                                <strong id="totalPrice">${formatPrice(product.price)}</strong>
                            </div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="closeOrderDialog()">Annuler</button>
                    <button type="button" class="btn btn-primary" onclick="submitOrder(${productId})">Confirmer la commande</button>
                </div>
            </div>
        `;
        
        // Ajouter au DOM
        document.body.appendChild(popup);
        
        // Animation d'apparition
        setTimeout(() => popup.classList.add('show'), 10);
        
        // Stocker les infos du produit
        window.currentProduct = product;
        
        // Ajouter le support de la touche Échap
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                closeOrderDialog();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
        
        // Initialiser le résumé de commande
        updateOrderSummary();
        
    } catch (error) {
        console.error('Erreur lors de l\'ouverture du formulaire:', error);
        showNotification('Erreur lors de l\'ouverture du formulaire de commande', 'error');
    }
}

/**
 * Ouvre le modal d'ajout/modification de produit
 * @param {number} productId - ID du produit (optionnel pour modification)
 */
async function openProductModal(productId = null) {
    const modal = document.getElementById('productModal');
    const form = document.getElementById('productForm');
    const title = document.getElementById('modalTitle');
    
    if (productId) {
        try {
            // Mode modification
            const product = await ProductsAPI.getById(productId);
            
            title.textContent = 'Modifier le produit';
            form.reset();
            
            // Remplir le formulaire
            document.getElementById('productName').value = product.name;
            document.getElementById('productDescription').value = product.description;
            document.getElementById('productPrice').value = product.price;
            document.getElementById('productStock').value = product.stock;
            document.getElementById('productImage').value = product.image || '';
            document.getElementById('productCategory').value = product.category;
            
            // Afficher l'aperçu de l'image existante
            const imagePreview = document.getElementById('imagePreview');
            const productImage = getProductImage(product);
            if (productImage) {
                imagePreview.innerHTML = `<img src="${productImage}" alt="Aperçu de ${product.name}">`;
            } else {
                imagePreview.innerHTML = '<i class="fas fa-image"></i><span>Aperçu de l\'image</span>';
            }
            
            // Stocker l'ID pour la modification
            form.dataset.productId = productId;
        } catch (error) {
            console.error('Erreur lors du chargement du produit:', error);
            showNotification('Erreur lors du chargement du produit', 'error');
            return;
        }
    } else {
        // Mode ajout
        title.textContent = 'Ajouter un produit';
        form.reset();
        delete form.dataset.productId;
    }
    
    modal.classList.add('active');
}

/**
 * Ferme le modal de produit
 */
function closeProductModal() {
    const modal = document.getElementById('productModal');
    const form = document.getElementById('productForm');
    const imagePreview = document.getElementById('imagePreview');
    
    modal.classList.remove('active');
    form.reset();
    delete form.dataset.productId;
    
    // Réinitialiser l'aperçu de l'image
    if (imagePreview) {
        imagePreview.innerHTML = '<i class="fas fa-image"></i><span>Aperçu de l\'image</span>';
    }
    
    // Réinitialiser les champs d'image
    const fileInput = document.getElementById('productImageFile');
    const urlInput = document.getElementById('productImage');
    const toggleBtn = document.getElementById('toggleUrlInput');
    
    if (fileInput) fileInput.value = '';
    if (urlInput) urlInput.value = '';
    
    // Remettre le mode par défaut (fichier)
    if (urlInput && toggleBtn) {
        urlInput.style.display = 'none';
        fileInput.style.display = 'block';
        toggleBtn.innerHTML = '<i class="fas fa-link"></i> URL';
    }
}

/**
 * Gère la soumission du formulaire de produit
 */
async function handleProductFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const imageFile = form.querySelector('input[name="image_file"]').files[0];
    
    try {
        // Helper: construit un FormData propre avec le fichier image correctement nommé
        function buildFormData(form, imageFile) {
            const fd = new FormData();
            fd.append('name', form.querySelector('input[name="name"]').value);
            fd.append('description', form.querySelector('textarea[name="description"]').value);
            fd.append('price', form.querySelector('input[name="price"]').value);
            fd.append('stock', form.querySelector('input[name="stock"]').value);
            fd.append('category', form.querySelector('select[name="category"]').value);
            fd.append('available', 'true');
            if (imageFile) {
                fd.append('image', imageFile);
            }
            return fd;
        }

        if (form.dataset.productId) {
            // Modification
            const productId = form.dataset.productId;
            
            if (imageFile) {
                // Avec fichier image: envoyer FormData
                const formData = buildFormData(form, imageFile);
                await ProductsAPI.update(productId, formData);
            } else {
                // Sans fichier: envoyer JSON (sans toucher à l'image existante)
                const productData = {
                    name: form.querySelector('input[name="name"]').value,
                    description: form.querySelector('textarea[name="description"]').value,
                    price: parseFloat(form.querySelector('input[name="price"]').value),
                    stock: parseInt(form.querySelector('input[name="stock"]').value),
                    category: form.querySelector('select[name="category"]').value,
                    available: true
                };
                // Si une URL d'image est fournie, l'inclure
                const imageUrl = form.querySelector('input[name="image"]') && form.querySelector('input[name="image"]').value;
                if (imageUrl) productData.image = imageUrl;
                
                await ProductsAPI.update(productId, productData);
            }
            
            showNotification('Produit modifié avec succès', 'success');
        } else {
            // Ajout
            if (imageFile) {
                // Avec fichier image: envoyer FormData
                const formData = buildFormData(form, imageFile);
                await ProductsAPI.create(formData);
                showNotification('Produit ajouté avec succès', 'success');
            } else {
                // Sans fichier: envoyer JSON avec URL éventuelle
                const imageUrlInput = form.querySelector('input[name="image"]');
                const productData = {
                    name: form.querySelector('input[name="name"]').value,
                    description: form.querySelector('textarea[name="description"]').value,
                    price: parseFloat(form.querySelector('input[name="price"]').value),
                    stock: parseInt(form.querySelector('input[name="stock"]').value),
                    category: form.querySelector('select[name="category"]').value,
                    available: true
                };
                if (imageUrlInput && imageUrlInput.value) {
                    productData.image = imageUrlInput.value;
                }
                
                await ProductsAPI.create(productData);
                showNotification('Produit ajouté avec succès', 'success');
            }
        }
        
        // Fermer le modal
        closeProductModal();
        
        // Recharger la page actuelle
        if (app.currentPage === 'products') {
            await loadProducts();
        } else if (app.currentPage === 'management') {
            await loadProductsForManagement();
        }
        
    } catch (error) {
        console.error('❌ Erreur lors de la sauvegarde du produit:', error);
        console.error('Détails de l\'erreur:', error.message);
        
        // Afficher un message d'erreur plus détaillé
        let errorMessage = 'Erreur lors de la sauvegarde';
        
        // Si l'erreur contient des détails du backend
        if (error.message) {
            // Essayer de parser les erreurs Django
            if (error.message.includes('non valide')) {
                // Erreur de validation Django
                errorMessage += ': ' + error.message;
            } else if (error.message.includes('400')) {
                if (error.message.includes('image')) {
                    errorMessage += ': Format d\'image invalide. Utilisez une URL valide ou sélectionnez un fichier.';
                } else {
                    errorMessage += ': Données invalides. Vérifiez tous les champs.';
                }
            } else if (error.message.includes('403')) {
                errorMessage += ': Permission refusée.';
            } else if (error.message.includes('404')) {
                errorMessage += ': Ressource non trouvée.';
            } else if (error.message.includes('500')) {
                errorMessage += ': Erreur serveur. Veuillez réessayer.';
            } else {
                errorMessage += ': ' + error.message;
            }
        }
        
        showNotification(errorMessage, 'error');
    }
}

/**
 * Convertit un fichier en base64
 * @param {File} file - Fichier à convertir
 * @returns {Promise<string>} Image en base64
 */
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
        reader.readAsDataURL(file);
    });
}


/**
 * Toggle between file input and URL input for product image
 */
function toggleImageInput() {
    const urlInput = document.getElementById('productImage');
    const fileInput = document.getElementById('productImageFile');
    const toggleBtn = document.getElementById('toggleUrlInput');

    if (!urlInput || !fileInput || !toggleBtn) return;

    if (urlInput.style.display === 'none') {
        // Show URL input, hide file input
        urlInput.style.display = 'block';
        fileInput.style.display = 'none';
        toggleBtn.innerHTML = '<i class="fas fa-file-upload"></i> Fichier';
    } else {
        urlInput.style.display = 'none';
        fileInput.style.display = 'block';
        toggleBtn.innerHTML = '<i class="fas fa-link"></i> URL';
    }
}

// Preview handling for image inputs
document.addEventListener('change', async (e) => {
    if (e.target && e.target.id === 'productImageFile') {
        const file = e.target.files[0];
        const preview = document.getElementById('imagePreview');
        if (file && preview) {
            try {
                const data = await fileToBase64(file);
                preview.innerHTML = `<img src="${data}" alt="Aperçu" style="max-width:120px;max-height:80px;">`;
            } catch (err) {
                preview.innerHTML = '<i class="fas fa-image"></i><span>Aperçu indisponible</span>';
            }
        }
    }

    if (e.target && e.target.id === 'productImage') {
        const url = e.target.value;
        const preview = document.getElementById('imagePreview');
        if (url && preview) {
            preview.innerHTML = `<img src="${url}" alt="Aperçu" style="max-width:120px;max-height:80px;">`;
        }
    }
});

/**
 * Sauvegarde une image dans le dossier frontend/images
 * @param {string} fileName - Nom du fichier
 * @param {string} base64Data - Données base64 de l'image
 * @returns {Promise<boolean>} True si succès
 */
async function saveImageToFile(fileName, base64Data) {
    try {
        // Créer un lien de téléchargement
        const link = document.createElement('a');
        link.href = base64Data;
        link.download = fileName;
        link.style.display = 'none';
        
        // Ajouter le lien au DOM et cliquer dessus
        document.body.appendChild(link);
        link.click();
        
        // Retirer le lien du DOM
        document.body.removeChild(link);
        
        // console.log('💾 Image téléchargée:', fileName);
        
        // Afficher un message pour informer l'utilisateur
        showNotification(`Image ${fileName} téléchargée`, 'success');
        
        return true;
    } catch (error) {
        console.error('Erreur lors de la sauvegarde de l\'image:', error);
        return false;
    }
}

/**
 * Récupère l'image d'un produit (URL, locale ou par défaut)
 * @param {Object} product - Données du produit
 * @returns {string} URL de l'image ou chaîne vide
 */
function getProductImage(product) {
    // Priorité à l'image fournie par le serveur (persistante)
    if (product && product.image && isValidUrl(product.image)) {
        return product.image;
    }

    // Ancien fallback : image locale stockée dans localStorage (legacy)
    try {
        const localImageFile = localStorage.getItem(`product_image_${product.id}`);
        if (localImageFile) {
            const pendingUpload = localStorage.getItem('pending_image_upload');
            if (pendingUpload) {
                const uploadData = JSON.parse(pendingUpload);
                if (uploadData.fileName === localImageFile) {
                    return uploadData.fileData; // base64 temporaire
                }
            }
        }
    } catch (e) {
        // ignore localStorage errors
    }
    
    // Sinon, retourner une chaîne vide (affichera l'icône par défaut)
    return '';
}

/**
 * Valide si une chaîne est une URL valide (absolue ou relative /media/)
 * @param {string} url - URL à valider
 * @returns {boolean} True si valide
 */
function isValidUrl(url) {
    if (!url) return false;
    // Accepter les URLs relatives /media/ (upload Django)
    if (url.startsWith('/media/') || url.startsWith('/static/')) return true;
    try {
        const urlObj = new URL(url);
        return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch (e) {
        return false;
    }
}

/**
 * Supprime un produit
 * @param {number} productId - ID du produit
 */
async function deleteProduct(productId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce produit ?')) {
        return;
    }
    
    try {
        await ProductsAPI.delete(productId);
        showNotification('Produit supprimé avec succès', 'success');
        
        // Recharger la page actuelle
        if (app.currentPage === 'products') {
            await loadProducts();
        } else if (app.currentPage === 'management') {
            await loadManagement();
        }
    } catch (error) {
        console.error('Erreur lors de la suppression du produit:', error);
        showNotification('Erreur: ' + error.message, 'error');
    }
}

/**
 * Ferme la popup de commande
 */
function closeOrderDialog() {
    const popup = document.querySelector('.modal-overlay');
    if (popup) {
        popup.classList.remove('show');
        setTimeout(() => {
            if (popup.parentNode) {
                document.body.removeChild(popup);
            }
        }, 300);
    }
    window.currentProduct = null;
    
    // Nettoyer tous les écouteurs d'événements Échap
    document.removeEventListener('keydown', () => {});
}

/**
 * Met à jour la quantité dans le formulaire
 * @param {number} change - Changement à appliquer (+1 ou -1)
 */
function updateQuantity(change) {
    const quantityInput = document.getElementById('quantity');
    const currentQuantity = parseInt(quantityInput.value);
    const newQuantity = currentQuantity + change;
    const maxQuantity = parseInt(quantityInput.max);
    
    if (newQuantity >= 1 && newQuantity <= maxQuantity) {
        quantityInput.value = newQuantity;
        updateOrderSummary();
    }
}

/**
 * Met à jour le résumé de la commande
 */
function updateOrderSummary() {
    const quantity = parseInt(document.getElementById('quantity').value);
    const unitPrice = window.currentProduct.price;
    const totalPrice = unitPrice * quantity;
    
    document.getElementById('totalQuantity').textContent = quantity;
    document.getElementById('totalPrice').textContent = formatPrice(totalPrice);
}

/**
 * Soumet la commande
 * @param {number} productId - ID du produit
 */
async function submitOrder(productId) {
    const form = document.getElementById('orderForm');
    const formData = new FormData(form);
    
    const orderData = {
        customer_name: formData.get('customer_name'),
        customer_email: formData.get('customer_email'),
        customer_phone: formData.get('customer_phone'),
        notes: formData.get('notes'),
        items: [
            {
                product_id: productId,
                quantity: parseInt(formData.get('quantity'))
            }
        ]
    };
    
    // Validation
    if (!orderData.customer_name || !orderData.items[0].quantity) {
        showNotification('Veuillez remplir les champs obligatoires', 'error');
        return;
    }
    
    try {
        // Créer la commande via l'API
        await OrdersAPI.create(orderData);
        showNotification('Commande passée avec succès!', 'success');
        closeOrderDialog();
        
        // Recharger les produits si nécessaire
        if (app.currentPage === 'products') {
            await loadProducts();
        }
    } catch (error) {
        console.error('Erreur lors de la commande:', error);
        showNotification('Erreur lors de la commande: ' + error.message, 'error');
    }
}

/**
 * Affiche les produits pour la gestion
 */
async function loadProductsForManagement() {
    const container = document.getElementById('productsManagementGrid');
    if (!container) return;
    
    try {
        container.innerHTML = '<div class="loading">Chargement...</div>';
        
        // Récupérer tous les produits (même non disponibles)
        let products = await ProductsAPI.getAll();
        // console.log('products.loadProductsForManagement - raw products:', products);
        products = normalizeList(products);

        container.innerHTML = '';

        products.forEach(product => {
            const productElement = createProductManagementCard(product);
            container.appendChild(productElement);
        });
        
        if (products.length === 0) {
            container.innerHTML = '<div class="no-data">Aucun produit</div>';
        }
    } catch (error) {
        console.error('Erreur:', error);
        container.innerHTML = '<div class="error">Erreur de chargement</div>';
    }
}

/**
 * Crée une carte de produit pour la gestion
 * @param {Object} product - Données du produit
 * @returns {HTMLElement} Carte de gestion
 */
function createProductManagementCard(product) {
    const card = document.createElement('div');
    card.className = 'product-management-card';
    
    const inStock = product.stock > 0;
    const stockText = inStock ? `${product.stock} en stock` : 'Rupture';
    const stockClass = inStock ? 'in-stock' : 'out-of-stock';
    const availableText = product.available ? 'Disponible' : 'Non disponible';
    const availableClass = product.available ? 'badge-success' : 'badge-danger';
    
    card.innerHTML = `
        <div class="product-management-header">
            <div class="product-management-image">
                ${getProductImage(product) ? 
                    `<img src="${getProductImage(product)}" alt="${product.name}" onerror="this.parentElement.innerHTML='<i class=\\"fas fa-birthday-cake\\"></i>'">` :
                    `<i class="fas fa-birthday-cake"></i>`
                }
            </div>
            <div class="product-management-info">
                <h4>${product.name}</h4>
                <p class="product-category">${getCategoryName(product.category)}</p>
                <p class="product-price">${formatPrice(product.price)}</p>
                <span class="badge ${availableClass}">${availableText}</span>
            </div>
        </div>
        <div class="product-management-body">
            <p class="product-description">${product.description}</p>
            <div class="product-stock-info">
                <span class="stock-label">Stock:</span>
                <span class="stock-value ${stockClass}">${stockText}</span>
            </div>
        </div>
        <div class="product-management-actions">
            <button class="btn btn-secondary" onclick="openProductModal(${product.id})">
                <i class="fas fa-edit"></i> Modifier
            </button>
            <button class="btn ${product.available ? 'btn-warning' : 'btn-success'}" onclick="toggleProductAvailability(${product.id})">
                <i class="fas fa-toggle-${product.available ? 'on' : 'off'}"></i>
            </button>
            <button class="btn btn-danger" onclick="deleteProduct(${product.id})">
                <i class="fas fa-trash"></i> Supprimer
            </button>
        </div>
    `;
    
    return card;
}

/**
 * Active/désactive la disponibilité d'un produit
 * @param {number} productId - ID du produit
 */
async function toggleProductAvailability(productId) {
    try {
        await ProductsAPI.toggleAvailability(productId);
        showNotification('Disponibilité mise à jour', 'success');
        
        if (app.currentPage === 'management') {
            await loadManagement();
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Erreur: ' + error.message, 'error');
    }
}

// Ajouter le gestionnaire d'événements pour le formulaire de produit
document.addEventListener('DOMContentLoaded', function() {
    const productForm = document.getElementById('productForm');
    if (productForm) {
        productForm.addEventListener('submit', handleProductFormSubmit);
    }
});

// Exporter les fonctions nécessaires
window.openProductModal = openProductModal;
window.closeProductModal = closeProductModal;
window.deleteProduct = deleteProduct;
window.showOrderDialog = showOrderDialog;
window.closeOrderDialog = closeOrderDialog;
window.updateQuantity = updateQuantity;
window.updateOrderSummary = updateOrderSummary;
window.submitOrder = submitOrder;
window.toggleProductAvailability = toggleProductAvailability;
// Exporter loadProducts pour tests manuels
window.loadProducts = loadProducts;
