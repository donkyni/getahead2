from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from affiliation.models import User, DroitsProfils, Poste, Niveau, Palier, Groupe, CodePays, Droits, Profils, \
    CategorieProduit, Produit, PrixProduit, Panier, ArticlePanier, HistoriqueVente, GetPoint, Payement

"""
Gestion des utilisateurs
"""
class PosteAdmin(admin.ModelAdmin):
    list_display = ('nom_du_poste', 'archive')
    list_filter = ('nom_du_poste',)
    ordering = ('nom_du_poste',)
    search_fields = ('nom_du_poste',)


admin.site.register(Poste, PosteAdmin)


class NiveauAdmin(admin.ModelAdmin):
    list_display = ('nom_du_niveau', 'archive')
    list_filter = ('nom_du_niveau',)
    ordering = ('nom_du_niveau',)
    search_fields = ('nom_du_niveau',)


admin.site.register(Niveau, NiveauAdmin)


class PalierAdmin(admin.ModelAdmin):
    list_display = ('nom_du_palier', 'archive')
    list_filter = ('nom_du_palier',)
    ordering = ('nom_du_palier',)
    search_fields = ('nom_du_palier',)


admin.site.register(Palier, PalierAdmin)


class GroupeAdmin(admin.ModelAdmin):
    list_display = ('nom_du_groupe', 'manageur_du_groupe', 'archive')
    list_filter = ('manageur_du_groupe',)
    ordering = ('nom_du_groupe',)
    search_fields = ('manageur_du_groupe',)


admin.site.register(Groupe, GroupeAdmin)


class CodePaysAdmin(admin.ModelAdmin):
    list_display = ('pays', 'code_pays', 'archive')
    list_filter = ('pays',)
    ordering = ('pays',)
    search_fields = ('pays',)


admin.site.register(CodePays, CodePaysAdmin)


class DroitsAdmin(admin.ModelAdmin):
    list_display = ('nom_du_droit', 'archive')
    list_filter = ('nom_du_droit',)
    ordering = ('nom_du_droit',)
    search_fields = ('nom_du_droit',)


admin.site.register(Droits, DroitsAdmin)


class ProfilsAdmin(admin.ModelAdmin):
    list_display = ('nom', 'archive')
    list_filter = ('nom',)
    ordering = ('nom',)
    search_fields = ('nom',)


admin.site.register(Profils, ProfilsAdmin)


class DroitsProfilsAdmin(admin.ModelAdmin):
    list_display = ('profil', 'droit', 'ecriture', 'lecture', 'modification', 'suppression')
    list_filter = ('profil', 'droit')
    ordering = ('profil',)
    search_fields = ('profil',)


admin.site.register(DroitsProfils, DroitsProfilsAdmin)


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = (
            'nom_d_utilisateur', 'nom_du_parent', 'nom', 'prenom', 'mail',
            'pays', 'telephone', 'groupe',
            'avatar', 'sexe',
        )

    def clean_password(self):
        password = self.cleaned_data.get("password")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            'nom_d_utilisateur', 'nom_du_parent', 'nom', 'prenom', 'mail', 'pays', 'telephone',
            'groupe', 'avatar', 'sexe',
            )

    def clean_password(self):
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        'nom_d_utilisateur', 'nom_du_parent', 'nom', 'prenom', 'mail', 'pays', 'telephone', 'palier', 'groupe',
        'avatar', 'annee_de_naissance', 'sexe', 'profil', 'unique_id', 'point', 'balances', 'points_initial_attribues',
        'don_bam', 'don_zou', 'don_maya', 'is_admin')
    list_filter = ('is_admin', 'nom')
    fieldsets = (
        (None, {'fields': ('nom_d_utilisateur', 'password')}),
        ('Personal info', {'fields': (
            'nom_du_parent', 'nom', 'prenom', 'mail',
            'pays', 'telephone', 'groupe',
            'avatar', 'annee_de_naissance', 'sexe', 'profil', 'unique_id', 'point', 'balances', 'points_initial_attribues',
            'palier', 'don_bam', 'don_zou', 'don_maya',)}),
        ('Permissions', {'fields': ('is_admin', 'is_active', 'groups', 'user_permissions',)}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'nom_d_utilisateur', 'nom_du_parent', 'nom', 'prenom', 'mail',
                'pays', 'telephone', 'groupe',
                'avatar', 'annee_de_naissance', 'sexe', 'profil', 'unique_id', 'point',  'balances', 'points_initial_attribues',
                'palier', 'don_bam', 'don_zou', 'don_maya', 'password'),
        }),
    )
    search_fields = ('nom_d_utilisateur', 'nom',)
    ordering = ('date_d_ajout',)
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(User, UserAdmin)


class CategorieProduitAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'seuil', 'points_initial', 'points_suivants', 'points_par_parrainage', 'archive')
    list_filter = ('seuil', 'points_initial',)
    ordering = ('seuil', 'points_initial',)
    search_fields = ('seuil', 'points_initial',)


admin.site.register(CategorieProduit, CategorieProduitAdmin)


class ProduitAdmin(admin.ModelAdmin):
    list_display = ('codeproduit', 'libelle', 'categorie', 'quantite', 'madein', 'archive')
    list_filter = ('codeproduit', 'libelle', 'categorie', 'quantite', 'madein',)
    date_hierarchy = 'date'
    ordering = ('codeproduit', 'libelle', 'categorie', 'quantite', 'madein',)
    search_fields = ('codeproduit', 'libelle', 'categorie', 'quantite', 'madein',)


admin.site.register(Produit, ProduitAdmin)


class PrixProduitAdmin(admin.ModelAdmin):
    list_display = ('produit', 'prix', 'ancien_prix', 'archive')
    list_filter = ('produit', 'prix', 'archive')
    date_hierarchy = 'date'
    ordering = ('produit', 'prix', 'archive')
    search_fields = ('produit', 'prix', 'archive')


admin.site.register(PrixProduit, PrixProduitAdmin)


class PanierAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'archive')
    list_filter = ('utilisateur', 'archive')
    date_hierarchy = 'date_cree'
    ordering = ('utilisateur', 'archive')
    search_fields = ('utilisateur', 'archive')


admin.site.register(Panier, PanierAdmin)


class ArticlePanierAdmin(admin.ModelAdmin):
    list_display = ('panier', 'produit', 'quantite', 'archive')
    list_filter = ('panier', 'produit', 'quantite', 'archive')
    ordering = ('panier', 'produit', 'quantite', 'archive')
    search_fields = ('panier', 'produit', 'quantite', 'archive')


admin.site.register(ArticlePanier, ArticlePanierAdmin)


class HistoriqueVenteAdmin(admin.ModelAdmin):
    list_display = ('prix', 'client', 'statut', 'archive')
    list_filter = ('prix', 'client', 'statut', 'archive')
    date_hierarchy = 'date'
    ordering = ('prix', 'client', 'statut', 'archive')
    search_fields = ('client', 'statut', 'archive')


admin.site.register(HistoriqueVente, HistoriqueVenteAdmin)


class PayementAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'montant', 'type_don', 'palier', 'statut')
    list_filter = ('utilisateur', 'montant', 'type_don', 'palier', 'statut')
    ordering = ('utilisateur', 'montant', 'type_don', 'palier', 'statut')
    search_fields = ('utilisateur', 'montant', 'type_don', 'palier', 'statut')


admin.site.register(Payement, PayementAdmin)
