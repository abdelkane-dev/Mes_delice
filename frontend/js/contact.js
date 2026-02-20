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

// Exporter les fonctions
window.loadContactMessages = loadContactMessages;
window.loadUnreadMessages = loadUnreadMessages;
