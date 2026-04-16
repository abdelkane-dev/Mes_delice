/**
 * Gestion des notifications en temps réel (polling)
 */

let notifPollingInterval = null;

// Icons par type de notification
const NOTIF_ICONS = {
    'nouvelle_commande': 'fas fa-shopping-bag',
    'commande_annulee': 'fas fa-times-circle',
    'commande_prete': 'fas fa-check-circle',
    'commande_livree': 'fas fa-truck',
    'commande_statut': 'fas fa-info-circle',
    'reponse_message': 'fas fa-reply',
    'nouveau_message': 'fas fa-envelope',
};

/**
 * Formate le temps relatif d'une notification
 */
function formatNotifTime(dateString) {
    const now = new Date();
    const date = new Date(dateString);
    const diff = Math.floor((now - date) / 1000); // secondes

    if (diff < 60) return 'À l\'instant';
    if (diff < 3600) return `Il y a ${Math.floor(diff / 60)} min`;
    if (diff < 86400) return `Il y a ${Math.floor(diff / 3600)} h`;
    return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

/**
 * Charge et affiche les notifications dans le dropdown
 */
async function loadNotifications() {
    const notifList = document.getElementById('notifList');
    const notifBadge = document.getElementById('notifBadge');
    
    if (!notifList) return;
    
    try {
        const [notifications, countData] = await Promise.all([
            NotificationsAPI.getRecent(),
            NotificationsAPI.getUnreadCount()
        ]);
        
        const count = countData.count || 0;
        
        // Mettre à jour le badge
        if (notifBadge) {
            if (count > 0) {
                notifBadge.textContent = count > 99 ? '99+' : count;
                notifBadge.style.display = 'flex';
            } else {
                notifBadge.style.display = 'none';
            }
        }
        
        // Mettre à jour la liste
        if (!notifications || notifications.length === 0) {
            notifList.innerHTML = `
                <div class="notif-empty">
                    <i class="fas fa-bell-slash"></i>
                    Aucune notification
                </div>
            `;
            return;
        }
        
        notifList.innerHTML = notifications.map(notif => `
            <div class="notif-item ${notif.est_lue ? '' : 'unread'}" 
                 onclick="handleNotifClick(${notif.id}, '${notif.lien || ''}')"
                 data-id="${notif.id}">
                <div class="notif-icon">
                    <i class="${NOTIF_ICONS[notif.type] || 'fas fa-bell'}"></i>
                </div>
                <div class="notif-content">
                    <p class="notif-message">${escapeHtml(notif.message)}</p>
                    <p class="notif-time">${formatNotifTime(notif.created_at)}</p>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        // Silencieux : l'utilisateur n'est peut-être pas connecté ou la table n'existe pas encore
        if (notifBadge) notifBadge.style.display = 'none';
    }
}

/**
 * Gère le clic sur une notification
 */
async function handleNotifClick(notifId, lien) {
    try {
        // Marquer comme lue
        await NotificationsAPI.markAsRead(notifId);
        
        // Mettre à jour l'UI immédiatement
        const item = document.querySelector(`.notif-item[data-id="${notifId}"]`);
        if (item) item.classList.remove('unread');
        
        // Recharger le compteur
        const countData = await NotificationsAPI.getUnreadCount();
        const badge = document.getElementById('notifBadge');
        if (badge) {
            const count = countData.count || 0;
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }
        
        // Fermer le dropdown
        closeNotifDropdown();
        
        // Navigation si lien fourni
        if (lien && typeof showPage === 'function') {
            if (lien === 'orders') {
                showPage('orders');
            } else if (lien === 'orders-management') {
                showPage('management');
                setTimeout(() => {
                    if (typeof showManagementTab === 'function') showManagementTab('orders-management');
                }, 300);
            } else if (lien === 'messages-management') {
                showPage('management');
                setTimeout(() => {
                    if (typeof showManagementTab === 'function') showManagementTab('messages-management');
                }, 300);
            } else if (lien === 'contact') {
                // Afficher les messages du client
                showPage('contact');
                setTimeout(() => {
                    if (typeof loadMesMessages === 'function') loadMesMessages();
                }, 300);
            }
        }
    } catch (error) {
        console.error('Erreur lors du clic sur notification:', error);
    }
}

/**
 * Marque toutes les notifications comme lues
 */
async function markAllNotifsRead() {
    try {
        await NotificationsAPI.markAllAsRead();
        const badge = document.getElementById('notifBadge');
        if (badge) badge.style.display = 'none';
        
        // Retirer la classe unread de tous les items
        document.querySelectorAll('.notif-item.unread').forEach(item => {
            item.classList.remove('unread');
        });
        
        showNotification('Toutes les notifications ont été marquées comme lues', 'success');
    } catch (error) {
        console.error('Erreur:', error);
    }
}

/**
 * Bascule l'affichage du dropdown
 */
function toggleNotifDropdown() {
    const dropdown = document.getElementById('notifDropdown');
    if (!dropdown) return;
    
    const isOpen = dropdown.classList.contains('open');
    
    if (isOpen) {
        closeNotifDropdown();
    } else {
        dropdown.classList.add('open');
        loadNotifications(); // Recharger à l'ouverture
    }
}

/**
 * Ferme le dropdown
 */
function closeNotifDropdown() {
    const dropdown = document.getElementById('notifDropdown');
    if (dropdown) dropdown.classList.remove('open');
}

/**
 * Échappe le HTML pour éviter les XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}

/**
 * Démarre le polling des notifications (toutes les 30 secondes)
 */
function startNotifPolling() {
    // Charger immédiatement
    loadNotifications();
    
    // Puis toutes les 30 secondes
    notifPollingInterval = setInterval(() => {
        loadNotifications();
    }, 30000);
}

/**
 * Arrête le polling
 */
function stopNotifPolling() {
    if (notifPollingInterval) {
        clearInterval(notifPollingInterval);
        notifPollingInterval = null;
    }
}

// Fermer le dropdown si on clique ailleurs
document.addEventListener('click', function(e) {
    const bell = document.getElementById('notifBell');
    const dropdown = document.getElementById('notifDropdown');
    
    if (bell && dropdown && !bell.contains(e.target) && !dropdown.contains(e.target)) {
        closeNotifDropdown();
    }
});

// Initialiser au chargement
document.addEventListener('DOMContentLoaded', function() {
    // Démarrer le polling seulement si l'utilisateur est connecté (la cloche est présente)
    if (document.getElementById('notifBell')) {
        startNotifPolling();
    }
});

// Exporter les fonctions
window.loadNotifications = loadNotifications;
window.toggleNotifDropdown = toggleNotifDropdown;
window.closeNotifDropdown = closeNotifDropdown;
window.markAllNotifsRead = markAllNotifsRead;
window.handleNotifClick = handleNotifClick;
window.startNotifPolling = startNotifPolling;
window.stopNotifPolling = stopNotifPolling;
