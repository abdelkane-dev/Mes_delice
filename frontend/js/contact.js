/**
 * Gestion du formulaire de contact avec API Django REST
 */

// Initialiser le formulaire de contact
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', handleContactFormSubmit);
    }
});

/**
 * Gère la soumission du formulaire de contact
 * @param {Event} e - Événement de soumission
 */
async function handleContactFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    // Récupérer les données du formulaire
    const contactData = {
        name: formData.get('name'),
        email: formData.get('email'),
        phone: formData.get('phone') || '',
        subject: formData.get('subject'),
        message: formData.get('message')
    };
    
    // Validation
    if (!contactData.name || !contactData.email || !contactData.subject || !contactData.message) {
        showNotification('Veuillez remplir tous les champs requis', 'error');
        return;
    }
    
    // Valider l'email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(contactData.email)) {
        showNotification('Adresse email invalide', 'error');
        return;
    }
    
    try {
        // Désactiver le bouton de soumission
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Envoi en cours...';
        
        // Envoyer le message via l'API
        await ContactAPI.create(contactData);
        
        // Afficher un message de succès
        showNotification('Message envoyé avec succès! Nous vous répondrons dans les plus brefs délais.', 'success');
        
        // Réinitialiser le formulaire
        form.reset();
        
        // Réactiver le bouton
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
    } catch (error) {
        console.error('❌ Erreur lors de l\'envoi du message:', error);
        showNotification('Erreur lors de l\'envoi du message: ' + error.message, 'error');
        
        // Réactiver le bouton
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Envoyer le message';
    }
}

/**
 * Charge les messages de contact (pour l'admin)
 * Cette fonction peut être appelée depuis une page d'administration
 */
async function loadContactMessages() {
    try {
        const messages = await ContactAPI.getAll();
        // console.log('📧 Messages de contact:', messages);
        return messages;
    } catch (error) {
        console.error('❌ Erreur lors du chargement des messages:', error);
        throw error;
    }
}

/**
 * Charge les messages non lus
 */
async function loadUnreadMessages() {
    try {
        const messages = await ContactAPI.getUnread();
        // console.log('📧 Messages non lus:', messages);
        return messages;
    } catch (error) {
        console.error('❌ Erreur lors du chargement des messages non lus:', error);
        throw error;
    }
}

/**
 * Charge et affiche les messages du client connecté (avec réponses)
 */
async function loadMesMessages() {
    const container = document.getElementById('mesMessagesContainer');
    if (!container) return;
    
    try {
        container.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Chargement...</div>';
        
        const messages = await MessagesAPI.getMesMessages();
        
        if (!messages || messages.length === 0) {
            container.innerHTML = `
                <div class="no-data" style="text-align:center; padding: 3rem;">
                    <i class="fas fa-inbox" style="font-size:3rem; color:#dbb082; display:block; margin-bottom:1rem;"></i>
                    <p>Vous n'avez envoyé aucun message pour le moment.</p>
                    <p>Utilisez l'onglet "Envoyer un message" pour nous contacter.</p>
                </div>
            `;
            return;
        }
        
        const subjectLabels = {
            'commande': 'Passer une commande',
            'renseignement': 'Demande de renseignement',
            'allergene': 'Information sur les allergènes',
            'autre': 'Autre'
        };
        
        container.innerHTML = messages.map(msg => {
            const estRepondu = msg.est_repondu || msg.admin_reponse;
            const badgeClass = estRepondu ? 'badge-replied' : 'badge-pending';
            const badgeText = estRepondu ? '✓ Répondu' : '⏳ En attente';
            
            const replySection = estRepondu ? `
                <div class="admin-reply-box">
                    <h5><i class="fas fa-reply"></i> Réponse de l'équipe :</h5>
                    <p class="admin-reply-text">${escapeHtml(msg.admin_reponse || '')}</p>
                    ${msg.repondu_le ? `<small style="color:#9c6b4a;"><i class="fas fa-clock"></i> Répondu le ${formatDate(msg.repondu_le)}</small>` : ''}
                </div>
            ` : `
                <div class="admin-reply-box" style="background:#fff9f0; border-color:#dbb082;">
                    <p style="color:#9c6b4a; margin:0; font-style:italic;">
                        <i class="fas fa-hourglass-half"></i> 
                        Votre message est en attente de réponse. Nous vous répondrons dans les meilleurs délais.
                    </p>
                </div>
            `;
            
            return `
                <div class="my-message-card">
                    <div class="my-message-header">
                        <div>
                            <strong>${subjectLabels[msg.subject] || msg.subject_label || msg.subject}</strong>
                            <br>
                            <small style="color:#9c6b4a;"><i class="fas fa-calendar"></i> ${formatDate(msg.created_at)}</small>
                        </div>
                        <span class="badge ${badgeClass}">${badgeText}</span>
                    </div>
                    <div class="my-message-body">
                        <p style="margin:0 0 1rem 0; color:#5d3a2a; line-height:1.6;">${escapeHtml(msg.message)}</p>
                        ${replySection}
                    </div>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('Erreur lors du chargement des messages:', error);
        container.innerHTML = '<div class="error">Erreur lors du chargement de vos messages.</div>';
    }
}

/**
 * Échappe le HTML
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
}

/**
 * Initialise les onglets de la section contact
 */
function setupContactTabs() {
    // Gérer les onglets contact via délégation d'événements
    document.addEventListener('click', function(e) {
        const tabBtn = e.target.closest('.tab-btn');
        if (!tabBtn) return;
        
        const tabId = tabBtn.getAttribute('data-tab');
        if (!tabId) return;
        
        // Seulement les onglets contact-form-tab ou mes-messages-tab
        if (tabId !== 'contact-form-tab' && tabId !== 'mes-messages-tab') return;
        
        // Activer le bon bouton dans le même groupe
        const parentTabs = tabBtn.closest('.management-tabs');
        if (!parentTabs) return;
        
        parentTabs.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        tabBtn.classList.add('active');
        
        // Afficher le bon panneau dans la section contact uniquement
        const contactSection = document.getElementById('contact');
        if (!contactSection) return;
        
        // Cacher les panneaux contact
        ['contact-form-tab', 'mes-messages-tab'].forEach(id => {
            const p = contactSection.querySelector(`#${id}`);
            if (p) p.classList.remove('active');
        });
        
        const panel = contactSection.querySelector(`#${tabId}`);
        if (panel) {
            panel.classList.add('active');
            // Charger les messages si on clique sur cet onglet
            if (tabId === 'mes-messages-tab') {
                loadMesMessages();
            }
        }
    });
}

// Initialiser au chargement
document.addEventListener('DOMContentLoaded', function() {
    setupContactTabs();
});

// Exporter les fonctions
window.loadContactMessages = loadContactMessages;
window.loadUnreadMessages = loadUnreadMessages;
window.loadMesMessages = loadMesMessages;
window.setupContactTabs = setupContactTabs;
