/**
 * Language Context - Bilingual system for FR/EN
 * Manages language state across the application
 */

import React, { createContext, useContext, useState, useEffect } from 'react';

// Brand names per language - Uses unified logo
export const BRAND_NAMES = {
  fr: {
    full: "Chasse Bionic™",
    short: "Bionic™",
    company: "Chasse Bionic™",
    tagline: "Votre parcours guidé vers une chasse parfaite",
    slogan: "La science valide ce que le terrain confirme.™",
    logo: "/logos/bionic-logo-main.png"
  },
  en: {
    full: "Bionic Hunt™",
    short: "Bionic™",
    company: "Bionic Hunt™",
    tagline: "Your guided path to a perfect hunt",
    slogan: "Science validates what the field confirms.™",
    logo: "/logos/bionic-logo-main.png"
  }
};

// Complete UI translations
export const TRANSLATIONS = {
  fr: {
    // Navigation
    nav_home: "Accueil",
    nav_analyze: "Analysez",
    nav_compare: "Comparez",
    nav_shop: "Magasin",
    nav_mon_territoire_bionic: "Mon Territoire BIONIC™",
    nav_territory: "Territoire",
    nav_marketplace: "Marketplace",
    nav_formations: "Formations",
    nav_network: "Réseautage",
    nav_lands: "Terres",
    nav_admin: "Admin",
    nav_cart: "Panier",
    
    // Auth
    auth_login: "Connexion",
    auth_logout: "Déconnexion",
    auth_register: "S'inscrire",
    auth_forgot_password: "Mot de passe oublié?",
    auth_email: "Courriel",
    auth_password: "Mot de passe",
    auth_confirm_password: "Confirmer le mot de passe",
    auth_remember_me: "Se souvenir de moi",
    auth_new_user: "Nouveau compte",
    auth_existing_user: "Déjà inscrit?",
    
    // Common actions
    common_loading: "Chargement...",
    common_save: "Sauvegarder",
    common_cancel: "Annuler",
    common_delete: "Supprimer",
    common_edit: "Modifier",
    common_add: "Ajouter",
    common_search: "Rechercher",
    common_filter: "Filtrer",
    common_close: "Fermer",
    common_yes: "Oui",
    common_no: "Non",
    common_success: "Succès",
    common_error: "Erreur",
    common_back: "Retour",
    common_next: "Suivant",
    common_previous: "Précédent",
    common_submit: "Soumettre",
    common_download: "Télécharger",
    common_upload: "Téléverser",
    common_refresh: "Actualiser",
    common_view: "Voir",
    common_details: "Détails",
    common_share: "Partager",
    common_copy: "Copier",
    common_select: "Sélectionner",
    common_all: "Tout",
    common_none: "Aucun",
    common_more: "Plus",
    common_less: "Moins",
    
    // Footer & Partner
    footer_rights: "Tous droits réservés",
    footer_privacy: "Confidentialité",
    footer_terms: "Conditions",
    footer_contact: "Contact",
    footer_about: "À propos",
    footer_help: "Aide",
    footer_tagline: "La plateforme #1 pour les chasseurs au Québec",
    footer_quick_links: "Liens rapides",
    footer_partners: "Partenaires",
    footer_partner_join: "Rejoignez notre réseau de partenaires",
    footer_become_partner: "Devenez Partenaire",
    
    // Shop
    shop_title: "Boutique",
    shop_add_cart: "Ajouter au panier",
    shop_buy_now: "Acheter maintenant",
    shop_price: "Prix",
    shop_quantity: "Quantité",
    shop_in_stock: "En stock",
    shop_out_of_stock: "Épuisé",
    shop_cart_empty: "Votre panier est vide",
    shop_checkout: "Passer à la caisse",
    shop_total: "Total",
    shop_subtotal: "Sous-total",
    shop_shipping: "Livraison",
    shop_taxes: "Taxes",
    
    // Territory
    territory_title: "Analyse de Territoire",
    territory_subtitle: "Suivi et analyse de la faune sauvage",
    territory_description: "Analysez votre terrain de chasse avec notre IA",
    territory_map: "Carte",
    territory_waypoints: "Points GPS",
    territory_layers: "Couches",
    territory_analysis: "Analyse",
    territory_add_waypoint: "Ajouter un point",
    territory_add_waypoint_here: "Ajouter waypoint ici",
    territory_export: "Exporter",
    territory_import: "Importer",
    territory_species: "Espèces",
    territory_probability: "Probabilité",
    territory_high: "Élevée",
    territory_medium: "Moyenne",
    territory_low: "Faible",
    territory_events: "événements",
    territory_cameras: "caméras",
    territory_back: "Retour à l'accueil",
    territory_cart: "Panier",
    territory_logout: "Déconnexion",
    territory_gps_nav: "Navigation GPS",
    territory_start_tracking: "Démarrer tracé",
    territory_stop_tracking: "Arrêter tracé",
    territory_clear_all: "Effacer tout",
    territory_compatible: "Compatible Avenza, Garmin, etc.",
    
    // Analyzer
    analyzer_title: "Analyseur d'Attractants",
    analyzer_description: "Trouvez le produit parfait pour votre chasse",
    analyzer_species_select: "Sélectionnez l'espèce",
    analyzer_season: "Saison",
    analyzer_conditions: "Conditions",
    analyzer_results: "Résultats",
    analyzer_recommendations: "Recommandations",
    
    // Network / Réseautage
    network_title: "Réseautage",
    network_subtitle: "Connectez, partagez, développez votre réseau de chasse et gagnez des récompenses.",
    network_posts: "Publications",
    network_feed: "Fil d'actualité",
    network_prospects: "Prospects",
    network_contacts: "Contacts",
    network_groups: "Groupes",
    network_referral: "Parrainage",
    network_wallet: "Portefeuille",
    network_new_post: "Nouvelle publication",
    network_like: "J'aime",
    network_comment: "Commenter",
    network_share: "Partager",
    network_login_required: "Réseau de Chasseurs",
    network_login_desc: "Connectez-vous pour accéder au réseau social, gérer vos prospects, contacts, et profiter du programme de parrainage.",
    
    // Formations
    formations_title: "Formations de Chasse",
    formations_description: "Cours et certifications officiels",
    formations_duration: "Durée",
    formations_level: "Niveau",
    formations_enroll: "S'inscrire",
    formations_certificate: "Certificat",
    
    // Admin
    admin_title: "Administration",
    admin_dashboard: "Tableau de bord",
    admin_products: "Produits",
    admin_orders: "Commandes",
    admin_users: "Utilisateurs",
    admin_settings: "Paramètres",
    admin_reports: "Rapports",
    admin_identity: "Identité",
    admin_controls: "Contrôles",
    
    // Messages
    msg_welcome: "Bienvenue",
    msg_goodbye: "À bientôt",
    msg_saved: "Enregistré avec succès",
    msg_deleted: "Supprimé avec succès",
    msg_error_occurred: "Une erreur est survenue",
    msg_try_again: "Veuillez réessayer",
    msg_no_results: "Aucun résultat trouvé",
    msg_confirm_delete: "Êtes-vous sûr de vouloir supprimer?",
    
    // Hero Section
    hero_order: "Commandez",
    hero_description: "Chasse Bionic™ redéfinit l'art de la chasse moderne. Analysez et comparez en toute confiance votre territoire, ses zones d'achalandage, les terres à louer, les pourvoiries et les produits les plus performants. Grâce à une plateforme fondée exclusivement sur des données scientifiques, publiques, déclarées et vérifiables, vous accédez à un véritable écosystème de précision… directement au bout des doigts.",
    hero_highlight: "Identifiez gratuitement les plus performants et repérez instantanément les meilleures solutions et prix.",
    hero_subtitle: "Devenez le professionnel des leurres en quelques clics.",
    
    // Features
    feature_analyze_desc: "13 critères évalués par IA",
    feature_compare_desc: "Comparaison côte à côte",
    feature_order_desc: "Commande facile et rapide",
    
    // Cart
    cart_empty: "Votre panier est vide",
    cart_total: "Total",
    cart_checkout: "Passer à la caisse",
    
    // Common page titles
    page_best_choices: "Meilleurs choix",
    page_loading: "Chargement...",
    page_verifying: "Vérification de l'accès...",
    
    // Language
    lang_switch: "English",
    lang_current: "Français",
    lang_select: "Choisir la langue",
    
    // Analyzer Module
    analyzer_accept_terms: "Veuillez accepter les conditions",
    analyzer_fill_required: "Veuillez remplir les champs obligatoires",
    analyzer_report_sent: "Rapport envoyé à votre adresse email!",
    analyzer_send_error: "Erreur lors de l'envoi",
    analyzer_info_recognized: "Vos informations ont été reconnues automatiquement. Vérifiez et confirmez.",
    analyzer_enter_info: "Entrez vos coordonnées pour recevoir le rapport complet par email.",
    analyzer_name_placeholder: "Jean Dupont",
    analyzer_region_placeholder: "Sélectionnez votre région",
    analyzer_enter_product: "Veuillez entrer le nom du produit",
    analyzer_complete: "Analyse terminée!",
    analyzer_error: "Erreur lors de l'analyse",
    analyzer_what_analyze: "Que souhaitez-vous analyser?",
    analyzer_select_subcategory: "Sélectionnez une sous-catégorie pour préciser votre recherche",
    analyzer_choose_category: "Choisissez la catégorie de produit que vous souhaitez analyser",
    analyzer_product_placeholder: "Ex: Tink's #69 Doe-in-Rut, Code Blue Apple Jelly...",
    analyzer_auto_detect: "Détection automatique",
    analyzer_step_detect: "Détection du type de produit",
    analyzer_step_composition: "Recherche de la composition",
    analyzer_step_ingredients: "Analyse des ingrédients",
    analyzer_step_score: "Calcul du score d'attraction",
    analyzer_step_compare: "Comparaison avec les concurrents",
    analyzer_step_report: "Génération du rapport",
    
    // Brand Identity Admin
    brand_main_logo: "Logo Principal BIONIC™",
    brand_unified_desc: "Logo unifié Chasse Bionic™ / Bionic Hunt™",
    brand_full_logo_fr: "Logo Complet FR",
    brand_full_logo_en: "Full Logo EN",
    brand_official_letter: "Lettre officielle",
    brand_email_header: "En-tête Email",
    brand_contract: "Contrat",
    brand_invoice: "Facture",
    brand_partner_doc: "Document Partenaire",
    brand_zec_doc: "Document ZEC/Sépaq",
    brand_press_release: "Communiqué de Presse",
    brand_download_started: "Téléchargement lancé!",
    brand_download_error: "Erreur lors du téléchargement",
    brand_pdf_error: "Erreur lors de la génération du PDF",
    brand_format_error: "Format non supporté. Utilisez PNG, JPEG, WebP ou SVG.",
    brand_size_error: "Le fichier doit faire moins de 5MB",
    brand_upload_error: "Erreur lors de l'upload du logo",
    brand_logo_deleted: "Logo supprimé",
    brand_delete_error: "Erreur lors de la suppression",
    brand_custom_title: "Titre personnalisé du document",
    brand_recipient_name: "Nom du destinataire",
    brand_full_address: "Adresse complète",
    brand_main_content: "Contenu principal du document...",
    
    // Categories Manager
    categories_load_error: "Erreur lors du chargement des catégories",
    categories_init_success: "Catégories par défaut initialisées!",
    categories_init_error: "Erreur lors de l'initialisation",
    categories_fill_fields: "Veuillez remplir l'ID et le nom",
    categories_added: "Catégorie ajoutée!",
    categories_add_error: "Erreur lors de l'ajout",
    categories_updated: "Catégorie mise à jour!",
    categories_update_error: "Erreur lors de la mise à jour",
    categories_delete_confirm: "Supprimer cette catégorie?",
    categories_deleted: "Catégorie supprimée!",
    categories_protected: "Cette catégorie est protégée ou n'existe pas dans la base",
    categories_fill_all: "Veuillez remplir tous les champs",
    categories_sub_added: "Sous-catégorie ajoutée!",
    categories_sub_deleted: "Sous-catégorie supprimée!",
    categories_sub_error: "Erreur lors de la suppression",
    categories_manage_desc: "Gérez les catégories et sous-catégories affichées sous le bouton \"Analysez\"",
    categories_name_placeholder: "Nom",
    categories_emoji_placeholder: "Emoji",
    categories_order_placeholder: "Ordre",
    categories_new: "Nouvelle Catégorie",
    categories_new_sub: "Nouvelle Sous-catégorie",
    
    // Territory Inventory
    territory_inventory_title: "Inventaire National des Territoires",
    territory_inventory_desc: "Analyse des territoires de chasse au Canada",
    territory_pourvoyeurs: "Pourvoyeurs",
    territory_ia_scraping: "IA & Scraping",
    territory_all_types: "Tous types",
    territory_all_provinces: "Toutes provinces",
    territory_all_species: "Toutes espèces",
    territory_sort_score: "Trier par score",
    territory_score_high: "Score le plus élevé",
    territory_score_low: "Score le plus bas",
    territory_name_az: "Nom A-Z",
    territory_verified: "Vérifié",
    territory_partner: "Partenaire",
    territory_potential: "Potentiel",
    territory_score: "Score",
    territory_bionic_score: "Score BIONIC™",
    territory_success_rate: "Taux de succès",
    territory_contact: "Contact",
    territory_services: "Services",
    territory_hunting_zones: "Zones de chasse",
    territory_close: "Fermer",
    
    // Territory Map
    territory_map_interactive: "Carte Interactive",
    territory_markers: "Marqueurs",
    territory_heatmap: "Heatmap",
    territory_score_legend: "Légende des scores",
    territory_excellent: "Excellent",
    territory_good: "Bon",
    territory_average: "Moyen",
    territory_weak: "Faible",
    
    // Scraping
    scraping_title: "Scraping de Données",
    scraping_sources: "Sources",
    scraping_total_territories: "Total territoires",
    scraping_total_scraped: "Total scrapés",
    scraping_run: "Lancer",
    scraping_run_all: "Tout lancer",
    scraping_sync: "Sync complète",
    scraping_last_run: "Dernier lancement",
    scraping_items: "items",
    scraping_running: "En cours...",
    scraping_success: "Scraping démarré",
    scraping_error: "Erreur de scraping",
    
    // Partners
    partners_potential: "Partenaires potentiels",
    partners_high: "Élevé",
    partners_medium: "Moyen",
    partners_convert: "Convertir",
    partners_converted: "Converti en partenaire",
    partners_convert_error: "Erreur de conversion",
    partners_site: "Site Web",
    partners_score: "Score de partenariat",
    
    // AI Recommendations
    ai_title: "Recommandations IA",
    ai_loading: "Chargement des recommandations...",
    ai_no_results: "Aucune recommandation trouvée",
    ai_season: "Saison",
    ai_spring: "Printemps",
    ai_summer: "Été",
    ai_fall: "Automne",
    ai_winter: "Hiver",
    ai_confidence: "Confiance",
    ai_recommendation: "Recommandation",
    
    // Partnership Admin
    partnership_title: "Gestion des Partenariats",
    partnership_applications: "Demandes",
    partnership_active: "Partenaires actifs",
    partnership_settings: "Paramètres",
    partnership_pending: "En attente",
    partnership_approved: "Approuvé",
    partnership_rejected: "Rejeté",
    partnership_approve: "Approuver",
    partnership_reject: "Rejeter",
    partnership_contact: "Contacter",
    partnership_details: "Voir les détails",
    partnership_company: "Entreprise",
    partnership_email: "Email",
    partnership_phone: "Téléphone",
    partnership_website: "Site web",
    partnership_type: "Type de partenariat",
    partnership_message: "Message",
    partnership_date: "Date de demande",
    partnership_no_applications: "Aucune demande de partenariat",
    partnership_email_settings: "Paramètres des emails",
    partnership_email_on: "Activé",
    partnership_email_off: "Désactivé",
    
    // Feature Controls Admin
    feature_title: "Contrôle des Fonctionnalités",
    feature_search: "Rechercher une fonctionnalité...",
    feature_category: "Catégorie",
    feature_all_categories: "Toutes les catégories",
    feature_enabled: "Activé",
    feature_disabled: "Désactivé",
    feature_toggle: "Basculer",
    feature_core: "Fonctionnalités principales",
    feature_premium: "Fonctionnalités premium",
    feature_experimental: "Expérimental",
    feature_save_success: "Fonctionnalité mise à jour",
    feature_save_error: "Erreur lors de la mise à jour",
    
    // Site Access Control
    site_access_title: "Contrôle d'Accès au Site",
    site_mode: "Mode du site",
    site_online: "En ligne",
    site_maintenance: "Maintenance",
    site_coming_soon: "Bientôt disponible",
    site_private: "Privé",
    site_mode_warning: "Attention: Ce mode affectera l'accès de tous les utilisateurs",
    site_maintenance_message: "Message de maintenance",
    site_save: "Enregistrer",
    site_updated: "Mode du site mis à jour",
    site_update_error: "Erreur lors de la mise à jour",
    
    // Global Auth
    auth_welcome: "Bienvenue",
    auth_welcome_back: "Bon retour",
    auth_create_account: "Créer un compte",
    auth_sign_in: "Se connecter",
    auth_sign_up: "S'inscrire",
    auth_full_name: "Nom complet",
    auth_email_address: "Adresse email",
    auth_password_min: "Minimum 8 caractères",
    auth_forgot: "Mot de passe oublié?",
    auth_no_account: "Pas encore de compte?",
    auth_have_account: "Déjà un compte?",
    auth_login_success: "Connexion réussie",
    auth_login_error: "Erreur de connexion",
    auth_register_success: "Compte créé avec succès",
    auth_register_error: "Erreur lors de l'inscription",
    auth_invalid_credentials: "Identifiants invalides",
    auth_email_required: "Email requis",
    auth_password_required: "Mot de passe requis",
    
    // Lands Rental
    lands_title: "Terres à Louer",
    lands_subtitle: "Trouvez le terrain de chasse parfait",
    lands_search: "Rechercher un terrain...",
    lands_filter_province: "Province",
    lands_filter_price: "Prix",
    lands_filter_size: "Superficie",
    lands_filter_species: "Gibier",
    lands_price_per_day: "$/jour",
    lands_price_per_season: "$/saison",
    lands_acres: "acres",
    lands_hectares: "hectares",
    lands_available: "Disponible",
    lands_booked: "Réservé",
    lands_contact_owner: "Contacter le propriétaire",
    lands_book_now: "Réserver maintenant",
    lands_view_details: "Voir les détails",
    lands_no_results: "Aucun terrain trouvé",
    lands_features: "Caractéristiques",
    lands_rules: "Règles du terrain",
    lands_access: "Accès",
    
    // Hunt Marketplace
    marketplace_title: "Marketplace de Chasse",
    marketplace_subtitle: "Achetez, vendez ou louez du matériel",
    marketplace_search: "Rechercher...",
    marketplace_filter_category: "Catégorie",
    marketplace_filter_condition: "État",
    marketplace_filter_price: "Prix",
    marketplace_new: "Neuf",
    marketplace_like_new: "Comme neuf",
    marketplace_good: "Bon état",
    marketplace_fair: "État acceptable",
    marketplace_sell_item: "Vendre un article",
    marketplace_my_listings: "Mes annonces",
    marketplace_messages: "Messages",
    marketplace_price: "Prix",
    marketplace_negotiable: "Négociable",
    marketplace_firm: "Prix ferme",
    marketplace_contact_seller: "Contacter le vendeur",
    marketplace_make_offer: "Faire une offre",
    marketplace_add_to_cart: "Ajouter au panier",
    marketplace_no_results: "Aucune annonce trouvée",
    marketplace_posted: "Publié le",
    marketplace_location: "Localisation",
    marketplace_shipping: "Livraison disponible",
    marketplace_pickup: "Ramassage seulement",
    
    // Networking Admin
    network_admin_title: "Administration du Réseau",
    network_admin_users: "Utilisateurs",
    network_admin_posts: "Publications",
    network_admin_reports: "Signalements",
    network_admin_moderation: "Modération",
    network_admin_ban: "Bannir",
    network_admin_warn: "Avertir",
    network_admin_delete: "Supprimer",
    network_admin_approve: "Approuver",
    
    // Content Depot
    content_title: "Dépôt de Contenu",
    content_generate: "Générer du contenu",
    content_templates: "Modèles",
    content_history: "Historique",
    content_ai_generate: "Génération IA",
    content_describe: "Décrivez le produit, la promotion ou le contenu à générer...",
    content_generated_title: "Titre accrocheur...",
    content_description: "Description du contenu...",
    content_cta: "Achetez maintenant!",
    content_download: "Télécharger",
    content_copy: "Copier",
    content_regenerate: "Régénérer",
    
    // Maintenance Page
    maintenance_title: "Site en Maintenance",
    maintenance_message: "Nous effectuons actuellement des améliorations.",
    maintenance_back_soon: "Nous serons de retour bientôt!",
    maintenance_contact: "Pour toute urgence, contactez-nous.",
    
    // Cookie Consent
    cookie_title: "Nous utilisons des cookies",
    cookie_message: "Ce site utilise des cookies pour améliorer votre expérience.",
    cookie_accept: "Tout accepter",
    cookie_reject: "Refuser",
    cookie_settings: "Paramètres",
    cookie_necessary: "Cookies nécessaires",
    cookie_analytics: "Cookies analytiques",
    cookie_marketing: "Cookies marketing",
    
    // Notifications
    notif_title: "Notifications",
    notif_mark_read: "Marquer comme lu",
    notif_mark_all_read: "Tout marquer comme lu",
    notif_clear: "Effacer",
    notif_no_notifications: "Aucune notification",
    notif_new: "Nouvelle notification",
    
    // Reset Password
    reset_title: "Réinitialiser le mot de passe",
    reset_email_sent: "Email envoyé!",
    reset_check_inbox: "Vérifiez votre boîte de réception",
    reset_new_password: "Nouveau mot de passe",
    reset_confirm_password: "Confirmer le mot de passe",
    reset_submit: "Réinitialiser",
    reset_success: "Mot de passe réinitialisé avec succès",
    reset_error: "Erreur lors de la réinitialisation",
    reset_invalid_token: "Lien invalide ou expiré",
    
    // Prompt Manager
    prompt_title: "Gestionnaire de Prompts",
    prompt_create: "Créer un prompt",
    prompt_edit: "Modifier",
    prompt_delete: "Supprimer",
    prompt_name: "Nom du prompt",
    prompt_content: "Contenu",
    prompt_category: "Catégorie",
    prompt_save: "Enregistrer",
    prompt_saved: "Prompt enregistré",
    prompt_deleted: "Prompt supprimé",
    
    // GPS Hotspots
    gps_title: "Points GPS",
    gps_add: "Ajouter un point",
    gps_edit: "Modifier",
    gps_delete: "Supprimer",
    gps_name: "Nom du point",
    gps_lat: "Latitude",
    gps_lon: "Longitude",
    gps_type: "Type",
    gps_notes: "Notes",
    gps_export: "Exporter GPX",
    gps_import: "Importer GPX",
    
    // Toast Messages
    toast_loading_packages_error: "Erreur lors du chargement des forfaits",
    toast_login_required: "Veuillez vous connecter pour effectuer un achat",
    toast_payment_creation_error: "Erreur lors de la création du paiement",
    toast_payment_success: "Paiement réussi!",
    toast_session_expired: "Session de paiement expirée",
    toast_enter_name: "Veuillez entrer un nom",
    toast_invalid_coords: "Coordonnées invalides",
    toast_coords_out_of_bounds: "Coordonnées hors limites",
    toast_navigation_to: "Navigation vers",
    toast_gps_position_found: "Position GPS trouvée",
    toast_gps_position_error: "Impossible d'obtenir votre position",
    toast_geolocation_unsupported: "Géolocalisation non supportée",
    toast_welcome: "Bienvenue",
    toast_auto_login: "Connexion automatique",
    toast_account_created: "Compte créé avec succès!",
    toast_logout_success: "Déconnexion réussie",
    toast_auto_login_failed: "Connexion automatique échouée",
    toast_enter_email: "Veuillez entrer votre adresse courriel",
    toast_email_sent: "Email envoyé! Vérifiez votre boîte de réception.",
    toast_send_error: "Erreur lors de l'envoi. Veuillez réessayer.",
    toast_auto_categorize_error: "Erreur lors de la catégorisation automatique",
    toast_select_category: "Veuillez sélectionner une catégorie",
    toast_category_applied: "Catégorie appliquée avec succès!",
    toast_category_apply_error: "Erreur lors de l'application de la catégorie",
    toast_hotspots_load_error: "Erreur lors du chargement des hotspots",
    toast_navigation_to_hotspot: "Navigation vers:",
    toast_coords_copied: "Coordonnées copiées!",
    toast_select_content_type: "Sélectionnez un type de contenu",
    toast_content_generated: "Contenu généré avec succès!",
    toast_content_demo: "Contenu généré (mode démo)",
    toast_content_copied: "Contenu copié!",
    toast_fill_all_fields: "Remplissez tous les champs",
    toast_publication_scheduled: "Publication programmée!",
    toast_publication_demo: "Publication programmée (mode démo)",
    toast_generate_content_first: "Générez du contenu d'abord",
    toast_published_on: "Publié sur",
    toast_simulated_publish: "Publication simulée (connectez vos réseaux sociaux pour publier réellement)",
    toast_publication_deleted: "Publication supprimée",
    toast_gps_invalid: "Veuillez entrer des coordonnées GPS valides",
    toast_gps_out_of_bounds: "Coordonnées GPS hors limites",
    toast_data_load_error: "Erreur lors du chargement des données",
    toast_search_territories_error: "Erreur lors de la recherche des territoires",
    toast_photo_uploaded: "Photo uploadée! Analyse IA en cours...",
    toast_analysis_complete: "Analyse terminée:",
    toast_analysis_error: "Erreur lors de l'analyse",
    toast_upload_error: "Erreur lors de l'upload",
    toast_sync_success: "territoires synchronisés vers partenariats",
    toast_sync_error: "Erreur lors de la synchronisation",
    toast_sync_reverse_error: "Erreur lors de la synchronisation inverse"
  },
  en: {
    // Navigation
    nav_home: "Home",
    nav_analyze: "Analyze",
    nav_compare: "Compare",
    nav_shop: "Shop",
    nav_mon_territoire_bionic: "My BIONIC™ Territory",
    nav_territory: "Territory",
    nav_marketplace: "Marketplace",
    nav_formations: "Courses",
    nav_network: "Network",
    nav_lands: "Lands",
    nav_admin: "Admin",
    nav_cart: "Cart",
    
    // Auth
    auth_login: "Login",
    auth_logout: "Logout",
    auth_register: "Register",
    auth_forgot_password: "Forgot password?",
    auth_email: "Email",
    auth_password: "Password",
    auth_confirm_password: "Confirm password",
    auth_remember_me: "Remember me",
    auth_new_user: "New account",
    auth_existing_user: "Already registered?",
    
    // Common actions
    common_loading: "Loading...",
    common_save: "Save",
    common_cancel: "Cancel",
    common_delete: "Delete",
    common_edit: "Edit",
    common_add: "Add",
    common_search: "Search",
    common_filter: "Filter",
    common_close: "Close",
    common_yes: "Yes",
    common_no: "No",
    common_success: "Success",
    common_error: "Error",
    common_back: "Back",
    common_next: "Next",
    common_previous: "Previous",
    common_submit: "Submit",
    common_download: "Download",
    common_upload: "Upload",
    common_refresh: "Refresh",
    common_view: "View",
    common_details: "Details",
    common_share: "Share",
    common_copy: "Copy",
    common_select: "Select",
    common_all: "All",
    common_none: "None",
    common_more: "More",
    common_less: "Less",
    
    // Footer & Partner
    footer_rights: "All rights reserved",
    footer_privacy: "Privacy",
    footer_terms: "Terms",
    footer_contact: "Contact",
    footer_about: "About",
    footer_help: "Help",
    footer_tagline: "The #1 platform for hunters in Quebec",
    footer_quick_links: "Quick Links",
    footer_partners: "Partners",
    footer_partner_join: "Join our partner network",
    footer_become_partner: "Become a Partner",
    
    // Shop
    shop_title: "Shop",
    shop_add_cart: "Add to cart",
    shop_buy_now: "Buy now",
    shop_price: "Price",
    shop_quantity: "Quantity",
    shop_in_stock: "In stock",
    shop_out_of_stock: "Out of stock",
    shop_cart_empty: "Your cart is empty",
    shop_checkout: "Checkout",
    shop_total: "Total",
    shop_subtotal: "Subtotal",
    shop_shipping: "Shipping",
    shop_taxes: "Taxes",
    
    // Territory
    territory_title: "Territory Analysis",
    territory_subtitle: "Wildlife tracking and analysis",
    territory_description: "Analyze your hunting ground with our AI",
    territory_map: "Map",
    territory_waypoints: "GPS Points",
    territory_layers: "Layers",
    territory_analysis: "Analysis",
    territory_add_waypoint: "Add point",
    territory_add_waypoint_here: "Add waypoint here",
    territory_export: "Export",
    territory_import: "Import",
    territory_species: "Species",
    territory_probability: "Probability",
    territory_high: "High",
    territory_medium: "Medium",
    territory_low: "Low",
    territory_events: "events",
    territory_cameras: "cameras",
    territory_back: "Back to home",
    territory_cart: "Cart",
    territory_logout: "Logout",
    territory_gps_nav: "GPS Navigation",
    territory_start_tracking: "Start tracking",
    territory_stop_tracking: "Stop tracking",
    territory_clear_all: "Clear all",
    territory_compatible: "Compatible with Avenza, Garmin, etc.",
    
    // Analyzer
    analyzer_title: "Attractant Analyzer",
    analyzer_description: "Find the perfect product for your hunt",
    analyzer_species_select: "Select species",
    analyzer_season: "Season",
    analyzer_conditions: "Conditions",
    analyzer_results: "Results",
    analyzer_recommendations: "Recommendations",
    
    // Network / Networking
    network_title: "Networking",
    network_subtitle: "Connect, share, grow your hunting network and earn rewards.",
    network_posts: "Posts",
    network_feed: "Feed",
    network_prospects: "Prospects",
    network_contacts: "Contacts",
    network_groups: "Groups",
    network_referral: "Referral",
    network_wallet: "Wallet",
    network_new_post: "New post",
    network_like: "Like",
    network_comment: "Comment",
    network_share: "Share",
    network_login_required: "Hunter Network",
    network_login_desc: "Log in to access the social network, manage your prospects, contacts, and enjoy the referral program.",
    
    // Formations
    formations_title: "Hunting Courses",
    formations_description: "Official courses and certifications",
    formations_duration: "Duration",
    formations_level: "Level",
    formations_enroll: "Enroll",
    formations_certificate: "Certificate",
    
    // Admin
    admin_title: "Administration",
    admin_dashboard: "Dashboard",
    admin_products: "Products",
    admin_orders: "Orders",
    admin_users: "Users",
    admin_settings: "Settings",
    admin_reports: "Reports",
    admin_identity: "Identity",
    admin_controls: "Controls",
    
    // Messages
    msg_welcome: "Welcome",
    msg_goodbye: "Goodbye",
    msg_saved: "Saved successfully",
    msg_deleted: "Deleted successfully",
    msg_error_occurred: "An error occurred",
    msg_try_again: "Please try again",
    msg_no_results: "No results found",
    msg_confirm_delete: "Are you sure you want to delete?",
    
    // Hero Section
    hero_order: "Order",
    hero_description: "Bionic Hunt™ redefines the art of modern hunting. Analyze and compare with confidence your territory, its hotspots, lands for rent, outfitters and top-performing products. With a platform built exclusively on scientific, public, declared and verifiable data, you access a true precision ecosystem… right at your fingertips.",
    hero_highlight: "Identify the best performers for free and instantly spot the best solutions and prices.",
    hero_subtitle: "Become a lure professional in just a few clicks.",
    
    // Features
    feature_analyze_desc: "13 AI-evaluated criteria",
    feature_compare_desc: "Side-by-side comparison",
    feature_order_desc: "Quick and easy ordering",
    
    // Cart
    cart_empty: "Your cart is empty",
    cart_total: "Total",
    cart_checkout: "Checkout",
    
    // Common page titles
    page_best_choices: "Best choices",
    page_loading: "Loading...",
    page_verifying: "Verifying access...",
    
    // Language
    lang_switch: "Français",
    lang_current: "English",
    lang_select: "Select language",
    
    // Analyzer Module
    analyzer_accept_terms: "Please accept the terms",
    analyzer_fill_required: "Please fill in required fields",
    analyzer_report_sent: "Report sent to your email!",
    analyzer_send_error: "Error sending",
    analyzer_info_recognized: "Your information has been automatically recognized. Verify and confirm.",
    analyzer_enter_info: "Enter your details to receive the full report by email.",
    analyzer_name_placeholder: "John Doe",
    analyzer_region_placeholder: "Select your region",
    analyzer_enter_product: "Please enter the product name",
    analyzer_complete: "Analysis complete!",
    analyzer_error: "Error during analysis",
    analyzer_what_analyze: "What do you want to analyze?",
    analyzer_select_subcategory: "Select a subcategory to refine your search",
    analyzer_choose_category: "Choose the product category you want to analyze",
    analyzer_product_placeholder: "Ex: Tink's #69 Doe-in-Rut, Code Blue Apple Jelly...",
    analyzer_auto_detect: "Auto-detect",
    analyzer_step_detect: "Detecting product type",
    analyzer_step_composition: "Searching composition",
    analyzer_step_ingredients: "Analyzing ingredients",
    analyzer_step_score: "Calculating attraction score",
    analyzer_step_compare: "Comparing with competitors",
    analyzer_step_report: "Generating report",
    
    // Brand Identity Admin
    brand_main_logo: "Main BIONIC™ Logo",
    brand_unified_desc: "Unified Chasse Bionic™ / Bionic Hunt™ logo",
    brand_full_logo_fr: "Full Logo FR",
    brand_full_logo_en: "Full Logo EN",
    brand_official_letter: "Official Letter",
    brand_email_header: "Email Header",
    brand_contract: "Contract",
    brand_invoice: "Invoice",
    brand_partner_doc: "Partner Document",
    brand_zec_doc: "ZEC/Sépaq Document",
    brand_press_release: "Press Release",
    brand_download_started: "Download started!",
    brand_download_error: "Download error",
    brand_pdf_error: "PDF generation error",
    brand_format_error: "Unsupported format. Use PNG, JPEG, WebP or SVG.",
    brand_size_error: "File must be less than 5MB",
    brand_upload_error: "Logo upload error",
    brand_logo_deleted: "Logo deleted",
    brand_delete_error: "Deletion error",
    brand_custom_title: "Custom document title",
    brand_recipient_name: "Recipient name",
    brand_full_address: "Full address",
    brand_main_content: "Main document content...",
    
    // Categories Manager
    categories_load_error: "Error loading categories",
    categories_init_success: "Default categories initialized!",
    categories_init_error: "Initialization error",
    categories_fill_fields: "Please fill ID and name",
    categories_added: "Category added!",
    categories_add_error: "Error adding",
    categories_updated: "Category updated!",
    categories_update_error: "Update error",
    categories_delete_confirm: "Delete this category?",
    categories_deleted: "Category deleted!",
    categories_protected: "This category is protected or doesn't exist",
    categories_fill_all: "Please fill all fields",
    categories_sub_added: "Subcategory added!",
    categories_sub_deleted: "Subcategory deleted!",
    categories_sub_error: "Deletion error",
    categories_manage_desc: "Manage categories and subcategories shown under the \"Analyze\" button",
    categories_name_placeholder: "Name",
    categories_emoji_placeholder: "Emoji",
    categories_order_placeholder: "Order",
    categories_new: "New Category",
    categories_new_sub: "New Subcategory",
    
    // Territory Inventory
    territory_inventory_title: "National Territory Inventory",
    territory_inventory_desc: "Hunting territory analysis across Canada",
    territory_pourvoyeurs: "Outfitters",
    territory_ia_scraping: "AI & Scraping",
    territory_all_types: "All types",
    territory_all_provinces: "All provinces",
    territory_all_species: "All species",
    territory_sort_score: "Sort by score",
    territory_score_high: "Highest score",
    territory_score_low: "Lowest score",
    territory_name_az: "Name A-Z",
    territory_verified: "Verified",
    territory_partner: "Partner",
    territory_potential: "Potential",
    territory_score: "Score",
    territory_bionic_score: "BIONIC™ Score",
    territory_success_rate: "Success rate",
    territory_contact: "Contact",
    territory_services: "Services",
    territory_hunting_zones: "Hunting zones",
    territory_close: "Close",
    
    // Territory Map
    territory_map_interactive: "Interactive Map",
    territory_markers: "Markers",
    territory_heatmap: "Heatmap",
    territory_score_legend: "Score legend",
    territory_excellent: "Excellent",
    territory_good: "Good",
    territory_average: "Average",
    territory_weak: "Weak",
    
    // Scraping
    scraping_title: "Data Scraping",
    scraping_sources: "Sources",
    scraping_total_territories: "Total territories",
    scraping_total_scraped: "Total scraped",
    scraping_run: "Run",
    scraping_run_all: "Run all",
    scraping_sync: "Full sync",
    scraping_last_run: "Last run",
    scraping_items: "items",
    scraping_running: "Running...",
    scraping_success: "Scraping started",
    scraping_error: "Scraping error",
    
    // Partners
    partners_potential: "Potential Partners",
    partners_high: "High",
    partners_medium: "Medium",
    partners_convert: "Convert",
    partners_converted: "Converted to partner",
    partners_convert_error: "Conversion error",
    partners_site: "Website",
    partners_score: "Partnership Score",
    
    // AI Recommendations
    ai_title: "AI Recommendations",
    ai_loading: "Loading recommendations...",
    ai_no_results: "No recommendations found",
    ai_season: "Season",
    ai_spring: "Spring",
    ai_summer: "Summer",
    ai_fall: "Fall",
    ai_winter: "Winter",
    ai_confidence: "Confidence",
    ai_recommendation: "Recommendation",
    
    // Partnership Admin
    partnership_title: "Partnership Management",
    partnership_applications: "Applications",
    partnership_active: "Active Partners",
    partnership_settings: "Settings",
    partnership_pending: "Pending",
    partnership_approved: "Approved",
    partnership_rejected: "Rejected",
    partnership_approve: "Approve",
    partnership_reject: "Reject",
    partnership_contact: "Contact",
    partnership_details: "View details",
    partnership_company: "Company",
    partnership_email: "Email",
    partnership_phone: "Phone",
    partnership_website: "Website",
    partnership_type: "Partnership type",
    partnership_message: "Message",
    partnership_date: "Application date",
    partnership_no_applications: "No partnership applications",
    partnership_email_settings: "Email settings",
    partnership_email_on: "Enabled",
    partnership_email_off: "Disabled",
    
    // Feature Controls Admin
    feature_title: "Feature Controls",
    feature_search: "Search a feature...",
    feature_category: "Category",
    feature_all_categories: "All categories",
    feature_enabled: "Enabled",
    feature_disabled: "Disabled",
    feature_toggle: "Toggle",
    feature_core: "Core features",
    feature_premium: "Premium features",
    feature_experimental: "Experimental",
    feature_save_success: "Feature updated",
    feature_save_error: "Update error",
    
    // Site Access Control
    site_access_title: "Site Access Control",
    site_mode: "Site mode",
    site_online: "Online",
    site_maintenance: "Maintenance",
    site_coming_soon: "Coming soon",
    site_private: "Private",
    site_mode_warning: "Warning: This mode will affect all users' access",
    site_maintenance_message: "Maintenance message",
    site_save: "Save",
    site_updated: "Site mode updated",
    site_update_error: "Update error",
    
    // Global Auth
    auth_welcome: "Welcome",
    auth_welcome_back: "Welcome back",
    auth_create_account: "Create an account",
    auth_sign_in: "Sign in",
    auth_sign_up: "Sign up",
    auth_full_name: "Full name",
    auth_email_address: "Email address",
    auth_password_min: "Minimum 8 characters",
    auth_forgot: "Forgot password?",
    auth_no_account: "Don't have an account?",
    auth_have_account: "Already have an account?",
    auth_login_success: "Login successful",
    auth_login_error: "Login error",
    auth_register_success: "Account created successfully",
    auth_register_error: "Registration error",
    auth_invalid_credentials: "Invalid credentials",
    auth_email_required: "Email required",
    auth_password_required: "Password required",
    
    // Lands Rental
    lands_title: "Lands for Rent",
    lands_subtitle: "Find the perfect hunting ground",
    lands_search: "Search for land...",
    lands_filter_province: "Province",
    lands_filter_price: "Price",
    lands_filter_size: "Size",
    lands_filter_species: "Game",
    lands_price_per_day: "$/day",
    lands_price_per_season: "$/season",
    lands_acres: "acres",
    lands_hectares: "hectares",
    lands_available: "Available",
    lands_booked: "Booked",
    lands_contact_owner: "Contact owner",
    lands_book_now: "Book now",
    lands_view_details: "View details",
    lands_no_results: "No land found",
    lands_features: "Features",
    lands_rules: "Land rules",
    lands_access: "Access",
    
    // Hunt Marketplace
    marketplace_title: "Hunting Marketplace",
    marketplace_subtitle: "Buy, sell or rent equipment",
    marketplace_search: "Search...",
    marketplace_filter_category: "Category",
    marketplace_filter_condition: "Condition",
    marketplace_filter_price: "Price",
    marketplace_new: "New",
    marketplace_like_new: "Like new",
    marketplace_good: "Good condition",
    marketplace_fair: "Fair condition",
    marketplace_sell_item: "Sell an item",
    marketplace_my_listings: "My listings",
    marketplace_messages: "Messages",
    marketplace_price: "Price",
    marketplace_negotiable: "Negotiable",
    marketplace_firm: "Firm price",
    marketplace_contact_seller: "Contact seller",
    marketplace_make_offer: "Make an offer",
    marketplace_add_to_cart: "Add to cart",
    marketplace_no_results: "No listings found",
    marketplace_posted: "Posted on",
    marketplace_location: "Location",
    marketplace_shipping: "Shipping available",
    marketplace_pickup: "Pickup only",
    
    // Networking Admin
    network_admin_title: "Network Administration",
    network_admin_users: "Users",
    network_admin_posts: "Posts",
    network_admin_reports: "Reports",
    network_admin_moderation: "Moderation",
    network_admin_ban: "Ban",
    network_admin_warn: "Warn",
    network_admin_delete: "Delete",
    network_admin_approve: "Approve",
    
    // Content Depot
    content_title: "Content Depot",
    content_generate: "Generate content",
    content_templates: "Templates",
    content_history: "History",
    content_ai_generate: "AI Generation",
    content_describe: "Describe the product, promotion or content to generate...",
    content_generated_title: "Catchy title...",
    content_description: "Content description...",
    content_cta: "Buy now!",
    content_download: "Download",
    content_copy: "Copy",
    content_regenerate: "Regenerate",
    
    // Maintenance Page
    maintenance_title: "Site Under Maintenance",
    maintenance_message: "We are currently making improvements.",
    maintenance_back_soon: "We'll be back soon!",
    maintenance_contact: "For emergencies, contact us.",
    
    // Cookie Consent
    cookie_title: "We use cookies",
    cookie_message: "This site uses cookies to improve your experience.",
    cookie_accept: "Accept all",
    cookie_reject: "Reject",
    cookie_settings: "Settings",
    cookie_necessary: "Necessary cookies",
    cookie_analytics: "Analytics cookies",
    cookie_marketing: "Marketing cookies",
    
    // Notifications
    notif_title: "Notifications",
    notif_mark_read: "Mark as read",
    notif_mark_all_read: "Mark all as read",
    notif_clear: "Clear",
    notif_no_notifications: "No notifications",
    notif_new: "New notification",
    
    // Reset Password
    reset_title: "Reset Password",
    reset_email_sent: "Email sent!",
    reset_check_inbox: "Check your inbox",
    reset_new_password: "New password",
    reset_confirm_password: "Confirm password",
    reset_submit: "Reset",
    reset_success: "Password reset successfully",
    reset_error: "Reset error",
    reset_invalid_token: "Invalid or expired link",
    
    // Prompt Manager
    prompt_title: "Prompt Manager",
    prompt_create: "Create a prompt",
    prompt_edit: "Edit",
    prompt_delete: "Delete",
    prompt_name: "Prompt name",
    prompt_content: "Content",
    prompt_category: "Category",
    prompt_save: "Save",
    prompt_saved: "Prompt saved",
    prompt_deleted: "Prompt deleted",
    
    // GPS Hotspots
    gps_title: "GPS Points",
    gps_add: "Add point",
    gps_edit: "Edit",
    gps_delete: "Delete",
    gps_name: "Point name",
    gps_lat: "Latitude",
    gps_lon: "Longitude",
    gps_type: "Type",
    gps_notes: "Notes",
    gps_export: "Export GPX",
    gps_import: "Import GPX",
    
    // Toast Messages
    toast_loading_packages_error: "Error loading packages",
    toast_login_required: "Please login to make a purchase",
    toast_payment_creation_error: "Error creating payment",
    toast_payment_success: "Payment successful!",
    toast_session_expired: "Payment session expired",
    toast_enter_name: "Please enter a name",
    toast_invalid_coords: "Invalid coordinates",
    toast_coords_out_of_bounds: "Coordinates out of bounds",
    toast_navigation_to: "Navigating to",
    toast_gps_position_found: "GPS position found",
    toast_gps_position_error: "Unable to get your position",
    toast_geolocation_unsupported: "Geolocation not supported",
    toast_welcome: "Welcome",
    toast_auto_login: "Auto login",
    toast_account_created: "Account created successfully!",
    toast_logout_success: "Logged out successfully",
    toast_auto_login_failed: "Auto login failed",
    toast_enter_email: "Please enter your email address",
    toast_email_sent: "Email sent! Check your inbox.",
    toast_send_error: "Send error. Please try again.",
    toast_auto_categorize_error: "Auto categorization error",
    toast_select_category: "Please select a category",
    toast_category_applied: "Category applied successfully!",
    toast_category_apply_error: "Error applying category",
    toast_hotspots_load_error: "Error loading hotspots",
    toast_navigation_to_hotspot: "Navigating to:",
    toast_coords_copied: "Coordinates copied!",
    toast_select_content_type: "Select a content type",
    toast_content_generated: "Content generated successfully!",
    toast_content_demo: "Content generated (demo mode)",
    toast_content_copied: "Content copied!",
    toast_fill_all_fields: "Please fill all fields",
    toast_publication_scheduled: "Publication scheduled!",
    toast_publication_demo: "Publication scheduled (demo mode)",
    toast_generate_content_first: "Generate content first",
    toast_published_on: "Published on",
    toast_simulated_publish: "Simulated publish (connect your social networks to publish for real)",
    toast_publication_deleted: "Publication deleted",
    toast_gps_invalid: "Please enter valid GPS coordinates",
    toast_gps_out_of_bounds: "GPS coordinates out of bounds",
    toast_data_load_error: "Error loading data",
    toast_search_territories_error: "Error searching territories",
    toast_photo_uploaded: "Photo uploaded! AI analysis in progress...",
    toast_analysis_complete: "Analysis complete:",
    toast_analysis_error: "Analysis error",
    toast_upload_error: "Upload error",
    toast_sync_success: "territories synced to partnerships",
    toast_sync_error: "Synchronization error",
    toast_sync_reverse_error: "Reverse synchronization error"
  }
};

// Context
const LanguageContext = createContext();

// Provider
export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(() => {
    // Check localStorage first
    const saved = localStorage.getItem('bionic_language');
    if (saved) return saved;
    
    // Then check browser language
    const browserLang = navigator.language.toLowerCase();
    if (browserLang.startsWith('fr')) return 'fr';
    if (browserLang.startsWith('en')) return 'en';
    
    // Default to French
    return 'fr';
  });

  useEffect(() => {
    localStorage.setItem('bionic_language', language);
    document.documentElement.lang = language;
  }, [language]);

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'fr' ? 'en' : 'fr');
  };

  const t = (key) => {
    return TRANSLATIONS[language][key] || key;
  };

  const brand = BRAND_NAMES[language];

  return (
    <LanguageContext.Provider value={{ 
      language, 
      setLanguage, 
      toggleLanguage, 
      t, 
      brand,
      translations: TRANSLATIONS[language]
    }}>
      {children}
    </LanguageContext.Provider>
  );
};

// Hook
export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

// Language Switcher Component - Sliding Toggle
export const LanguageSwitcher = ({ className = "" }) => {
  const { language, setLanguage } = useLanguage();
  
  const handleToggle = () => {
    setLanguage(language === 'fr' ? 'en' : 'fr');
  };
  
  return (
    <div 
      className={`flex items-center gap-2 ${className}`}
      data-testid="language-switcher"
    >
      {/* FR Label */}
      <span 
        className={`text-sm font-medium transition-colors cursor-pointer ${
          language === 'fr' ? 'text-[#f5a623]' : 'text-gray-500 hover:text-gray-400'
        }`}
        onClick={() => setLanguage('fr')}
      >
        FR
      </span>
      
      {/* Toggle Slider */}
      <button
        onClick={handleToggle}
        className="relative w-14 h-7 rounded-full bg-card border border-border transition-colors duration-300 hover:border-[#f5a623]/50"
        aria-label="Toggle language"
        data-testid="language-toggle"
      >
        {/* Slider Track Background */}
        <div className="absolute inset-1 rounded-full bg-background" />
        
        {/* Sliding Knob with Flag */}
        <div 
          className={`absolute top-1 w-5 h-5 rounded-full bg-[#f5a623] shadow-lg flex items-center justify-center transition-all duration-300 ease-in-out ${
            language === 'fr' ? 'left-1' : 'left-8'
          }`}
        >
          <span className="text-xs">
            {language === 'fr' ? '🇫🇷' : '🇬🇧'}
          </span>
        </div>
      </button>
      
      {/* EN Label */}
      <span 
        className={`text-sm font-medium transition-colors cursor-pointer ${
          language === 'en' ? 'text-[#f5a623]' : 'text-gray-500 hover:text-gray-400'
        }`}
        onClick={() => setLanguage('en')}
      >
        EN
      </span>
    </div>
  );
};

export default LanguageContext;
