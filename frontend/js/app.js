/**
 * Application principale pour la pâtisserie artisanale
 * Gestion de la navigation SPA et des fonctionnalités globales
 * VERSION AVEC API DJANGO REST
 */

// État de l'application
const app = {
    currentPage: 'home',
    products: [],
    orders: [],
    isInitialized: false
};

// Initialisation de l'application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialise l'application au chargement de la page
 */
function initializeApp() {
    // console.log('🍰 Initialisation de Les Délices de Marie...');

    // Si la page n'inclut pas de conteneur SPA (.page), on ne lance pas l'initialisation
    const anyPage = document.querySelector('.page');
    if (!anyPage) {
        return;
    }

    // Configurer le menu mobile d'abord
    setupMobileMenu();

    // Afficher la page par défaut après un délai plus long pour s'assurer que le DOM est prêt
    setTimeout(() => {
        // Vérifier que les éléments nécessaires sont présents
        const homePage = document.getElementById('home');
        const navLinks = document.querySelectorAll('.nav-link[data-page]');

        // console.log(`🔍 Vérification DOM - Page home trouvée: ${!!homePage}`);
        // console.log(`🔍 Vérification DOM - Liens de navigation trouvés: ${navLinks.length}`);

        // Configurer la navigation après le chargement du DOM
        if (navLinks && navLinks.length) {
            setupNavigation();
        }

        if (homePage) {
            showPage('home');
        } else {
            // Si aucune page "home" n'est présente (ex: page de login), respecter
            // une page déjà marquée `.page.active` ou ne rien faire silencieusement.
            const activePage = document.querySelector('.page.active');
            if (activePage) {
                if (activePage.id) {
                    app.currentPage = activePage.id;
                    const activeNavLink = document.querySelector(`[data-page="${app.currentPage}"]`);
                    if (activeNavLink) activeNavLink.classList.add('active');
                }
            } else {
                // Pas de page SPA pertinente sur cette vue — ne pas spammer la console.
            }
        }
    }, 200);
    
    // console.log('✅ Application initialisée avec succès!');
}

/**
 * Configure la navigation entre les pages
 */
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link[data-page]');
    // console.log(`🔗 Configuration de la navigation - ${navLinks.length} liens trouvés`);
    
    navLinks.forEach((link, index) => {
        // console.log(`🔗 Lien ${index}: ${link.getAttribute('data-page')} - ${link.textContent.trim()}`);
    });
    
    // Utiliser la délégation d'événements sur le document
    document.addEventListener('click', function(e) {
        const target = e.target.closest('.nav-link[data-page]');
        if (target) {
            e.preventDefault();
            const pageName = target.getAttribute('data-page');
            console.error(`=== CLIQUE SUR LIEN ===`);
            console.error(`Page demandée: ${pageName}`);
            console.error(`Texte du lien: ${target.textContent.trim()}`);
            // console.log(`🖱️ Clic sur le lien: ${pageName}`);
            showPage(pageName);
        }
    });
}

/**
 * Affiche une page spécifique
 * @param {string} pageName - Nom de la page à afficher
 */
function showPage(pageName) {
    // console.log(`📝 Affichage de la page: ${pageName}`);
    
    // Lister toutes les pages disponibles
    const allPages = document.querySelectorAll('.page');
    // console.log(`📄 Pages disponibles dans le DOM: ${allPages.length}`);
    allPages.forEach((page, index) => {
        // console.log(`📄 Page ${index}: ${page.id} - classe: ${page.className}`);
    });
    
    // Cacher toutes les pages
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => page.classList.remove('active'));
    
    // Retirer la classe active des liens de navigation
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => link.classList.remove('active'));
    
    // Afficher la page demandée avec une tentative retardée si nécessaire
    const targetPage = document.getElementById(pageName);
    if (targetPage) {
        // console.log(`✅ Page trouvée: ${pageName}`);
        targetPage.classList.add('active');
        
        // Mettre à jour le lien de navigation actif
        const activeNavLink = document.querySelector(`[data-page="${pageName}"]`);
        if (activeNavLink) {
            activeNavLink.classList.add('active');
        }
        
        // Charger les données spécifiques à la page
        loadPageData(pageName);

        // Mettre à jour l'état de la page actuelle après le chargement
        app.currentPage = pageName;
        
        // Fermer le menu mobile si ouvert
        closeMobileMenu();
    } else {
        // Si l'élément n'est pas trouvé, attendre un peu et réessayer (cas de chargement asynchrone)
        setTimeout(() => {
            const retryPage = document.getElementById(pageName);
            if (retryPage) {
                // console.log(`✅ Page trouvée au deuxième essai: ${pageName}`);
                retryPage.classList.add('active');
                
                // Mettre à jour le lien de navigation actif
                const activeNavLink = document.querySelector(`[data-page="${pageName}"]`);
                if (activeNavLink) {
                    activeNavLink.classList.add('active');
                }
                
                // Charger les données spécifiques à la page
                loadPageData(pageName);

                // Mettre à jour l'état de la page actuelle après le chargement
                app.currentPage = pageName;

                // Fermer le menu mobile si ouvert
                closeMobileMenu();
            } else {
                console.error(`❌ Page non trouvée: ${pageName}`);
                console.error('Conteneur de pages non trouvé');
            }
        }, 100);
    }
}

/**
 * Charge les données spécifiques à une page
 * @param {string} pageName - Nom de la page
 */
function loadPageData(pageName) {
    // Éviter le rechargement si on est déjà sur la même page
    if (app.currentPage === pageName) {
        // console.log(`⏭️ Déjà sur la page ${pageName}, pas de rechargement`);
        return;
    }
    
    switch (pageName) {
        case 'products':
            console.error('=== SHOWING PRODUCTS PAGE ===');
            loadProducts();
            break;
        case 'orders':
            console.error('=== SHOWING ORDERS PAGE ===');
            loadOrders();
            break;
        case 'management':
            loadManagement();
            break;
        case 'contact':
            // La page contact est statique
            break;
        default:
            break;
    }
}

/**
 * Configure le menu mobile
 */
function setupMobileMenu() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
}

/**
 * Ferme le menu mobile
 */
function closeMobileMenu() {
    const navMenu = document.getElementById('navMenu');
    if (navMenu) {
        navMenu.classList.remove('active');
    }
}

/**
 * Génère un ID unique
 * @returns {string} ID unique
 */
function generateId() {
    return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Formate un prix en euros
 * @param {number} price - Prix à formater
 * @returns {string} Prix formaté
 */
function formatPrice(price) {
    return `${parseFloat(price).toFixed(2)} cfa`;
}

/**
 * Formate une date
 * @param {string} dateString - Date au format ISO
 * @returns {string} Date formatée
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('fr-FR', options);
}

/**
 * Formate une date courte
 * @param {string} dateString - Date au format ISO
 * @returns {string} Date formatée
 */
function formatShortDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

/**
 * Retourne le nom d'une catégorie
 * @param {string} categorySlug - Slug de la catégorie
 * @returns {string} Nom de la catégorie
 */
function getCategoryName(categorySlug) {
    const categories = {
        'gateaux': 'Gâteaux',
        'patisseries': 'Pâtisseries',
        'viennoiseries': 'Viennoiseries',
        'macarons': 'Macarons',
        'chocolats': 'Chocolats'
    };
    return categories[categorySlug] || categorySlug;
}

/**
 * Retourne le label d'un statut de commande
 * @param {string} status - Statut de la commande
 * @returns {string} Label du statut
 */
function getOrderStatusLabel(status) {
    const statusLabels = {
        'pending': 'En préparation',
        'paid': 'Payée',
        'ready': 'Prête',
        'delivered': 'Livrée',
        'cancelled': 'Annulée'
    };
    return statusLabels[status] || status;
}

/**
 * Retourne la classe CSS pour un statut de commande
 * @param {string} status - Statut de la commande
 * @returns {string} Classe CSS
 */
function getOrderStatusClass(status) {
    const statusClasses = {
        'pending': 'status-pending',
        'paid': 'status-paid',
        'ready': 'status-ready',
        'delivered': 'status-delivered',
        'cancelled': 'status-cancelled'
    };
    return statusClasses[status] || 'status-default';
}

/**
 * Affiche une notification
 * @param {string} message - Message à afficher
 * @param {string} type - Type de notification (success, error, info)
 */
function showNotification(message, type = 'info') {
    // Créer la notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Ajouter au DOM
    document.body.appendChild(notification);
    
    // Animer l'apparition
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Retirer après 4 secondes
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 4000);
}

/**
 * Crée un élément de chargement
 * @returns {HTMLElement} Élément de chargement
 */
function createLoader() {
    const loader = document.createElement('div');
    loader.className = 'loader';
    loader.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Chargement...';
    return loader;
}

/**
 * Crée un élément "aucune donnée"
 * @param {string} message - Message à afficher
 * @returns {HTMLElement} Élément
 */
function createNoData(message = 'Aucune donnée disponible') {
    const noData = document.createElement('div');
    noData.className = 'no-data';
    noData.innerHTML = `<i class="fas fa-info-circle"></i> ${message}`;
    return noData;
}

/**
 * Crée un élément d'erreur
 * @param {string} message - Message d'erreur
 * @returns {HTMLElement} Élément d'erreur
 */
function createError(message = 'Une erreur est survenue') {
    const error = document.createElement('div');
    error.className = 'error';
    error.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
    return error;
}

// Exporter les fonctions globales
window.showPage = showPage;
window.formatPrice = formatPrice;
window.formatDate = formatDate;
window.formatShortDate = formatShortDate;
window.getCategoryName = getCategoryName;
window.getOrderStatusLabel = getOrderStatusLabel;
window.getOrderStatusClass = getOrderStatusClass;
window.showNotification = showNotification;
window.generateId = generateId;
