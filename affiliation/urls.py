from affiliation import views
from django.urls import re_path as url, path

urlpatterns = [
        # FRONTEND
        url(r'^produit$', views.produitfrontend, name="produitfrontend"),
        url(r'^(?P<id>\d+)/afficherdetailproduit$', views.detailproduitfrontend, name="detailproduitfrontend"),
        url(r'^(?P<id>\d+)/ajout-panier-detail-de-produit$', views.ajouter_au_panier_frontend, name='ajouter_au_panier_frontend'),
        url(r'^liste-article-present-dans-panier', views.voir_panierfrontend, name="voir_panierfrontend"),
        url(r'^finalisation-des-commandes-du-panier', views.soumettre_panierfrontend, name="soumettre_panierfrontend"),
        url(r'^(?P<id>\d+)/mettre-a-jour-article-panier', views.updatepanierfrontend, name='updatepanierfrontend'),
        url(r'^(?P<id>\d+)/suppression-article-panier', views.deletearticlepanierfrontend, name='deletearticlepanierfrontend'),

        # stock produit
        url(r'^ajout-de-produit$', views.addproduct, name="addproduct"),
        url(r'^liste-des-produit$', views.stock, name="stock"),
        url(r'^(?P<id>\d+)/modifier-le-produit$', views.updatestock, name="updatestock"),
        url(r'^(?P<id>\d+)/suppression-stock-de-produit$', views.deletestock, name="deletestock"),

        # categorie de produit
        url(r'^categorie-de-produit$', views.categorieproduct, name="categorieproduct"),
        url(r'^ajout-de-type-de-produit$', views.addcategoriestock, name="addcategoriestock"),
        url(r'^(?P<id>\d+)/modifier-la-categorie-de-produit$', views.updatecategoriestock, name="updatecategoriestock"),
        url(r'^(?P<id>\d+)/suppression-stock-produit$', views.deletecategoriestock, name="deletecategoriestock"),

        # prix des produits
        url(r'^parametrage-de-prix-aux-produits$', views.prixproduit, name="prixproduit"),
        url(r'^definir-un-prix-a-produit$', views.addprixproduit, name="addprixproduit"),
        url(r'^(?P<id>\d+)/modifier-le-prix-de-produit$', views.updateprixproduit, name="updateprixproduit"),
        url(r'^(?P<id>\d+)/retirer-le prix-dun-produit$', views.deleteprixproduit, name="deleteprixproduit"),

        # boutique
        url(r'^boutique-affichage-grille-de-produit$', views.boutique, name="boutique"),
        url(r'^(?P<id>\d+)/boutique-affichage-detail-de-produit$', views.detailproduit, name="detailproduit"),
        url(r'^boutique-affichage-panier-des-produits$', views.voir_panier, name="voir_panier"),
        url(r'^(?P<id>\d+)/boutique-affichage-panier-detail-de-produit$', views.ajouter_au_panier, name='ajouter_au_panier'),
        url(r'^(?P<id>\d+)/boutique-affichage-panier-modification-de-produit$', views.updatepanier, name='updatepanier'),
        url(r'^(?P<id>\d+)/boutique-affichage-suppression-article-panier', views.deletearticlepanier, name='deletearticlepanier'),
        url(r'^boutique-affichage-gestion-des-ventes', views.vente, name="vente"),
        url(r'^boutique-affichage-soumettre-le-panier', views.soumettre_panier, name="soumettre_panier"),
        path('mettre-a-jour-statut/<int:historique_id>/<str:statut>/', views.mettre_a_jour_statut, name='mettre_a_jour_statut'),

        path('choix-palier/<int:utilisateur_id>/<int:palier_id>/', views.choix_palier, name='choix_palier'),

        url(r'^tableau-de-board', views.dash, name="dash"),

        # gestion des utilisateurs
        url(r'^mon-espace-membre', views.profile, name="profile"),
        url(r'^modifier-les-informations-du-compte', views.editerprofile, name="editerprofile"),
        url(r'^(?P<id>\d+)/attribuer-un-payement-a-un-membre$', views.paydash, name="paydash"),
        url(r'^création-d-un-nouvel-utilisateur', views.user_creation, name="user_creation"),

]
