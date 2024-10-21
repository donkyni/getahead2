from django import forms

from affiliation.models import Produit, CategorieProduit, PrixProduit, ArticlePanier, User, Payement


class DateInput(forms.DateInput):
    input_type = 'date'


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['libelle', 'description', 'categorie', 'quantite', 'madein',
                  'image1', 'image2', 'image3', 'image4', 'image5',
                  'marque', 'modele', 'forme', 'couleur']


class CategorieProduitForm(forms.ModelForm):
    class Meta:
        model = CategorieProduit
        fields = ['libelle', 'seuil', 'points_initial', 'points_suivants', 'points_par_parrainage']


class PrixProduitForm(forms.ModelForm):
    class Meta:
        model = PrixProduit
        fields = ['produit', 'prix']


class ArticlePanierForm(forms.ModelForm):
    class Meta:
        model = ArticlePanier
        fields = ['produit', 'quantite']


class UserUpdateForm(forms.ModelForm):
    annee_de_naissance = forms.DateTimeField(widget=DateInput)
    nom_d_utilisateur = forms.CharField(disabled=True)

    class Meta:
        model = User
        fields = ('nom_d_utilisateur', 'nom', 'prenom', 'mail', 'telephone', 'pays',
                  'avatar', 'annee_de_naissance', 'sexe')


class PayDashForm(forms.ModelForm):
    class Meta:
        model = Payement
        fields = ['statut',]


class SelectionUtilisateurForm(forms.Form):
    utilisateur = forms.ModelChoiceField(queryset=User.objects.all(), label="Sélectionnez un utilisateur")



class UserCreation20Form(forms.ModelForm):
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = (
            'nom_d_utilisateur', 'nom_du_parent', 'nom', 'prenom', 'mail',
            'pays', 'telephone', 'groupe', 'avatar', 'sexe', 'password',
        )
        widgets = {
            'nom_du_parent': forms.Select(
                attrs={'class': 'selectpicker, text-bold', 'data-live-search': 'true', 'readonly': 'false'}),
            'pays': forms.Select(
                attrs={'class': 'selectpicker', 'data-live-search': 'true'}),
            'groupe': forms.Select(
                attrs={'class': 'selectpicker, text-bold', 'data-live-search': 'true', 'readonly': 'false'})
        }

    def clean_groupe(self):
        if not self['groupe'].html_name in self.data:
            return self.fields['groupe'].initial
        return self.cleaned_data['groupe']

    def clean_nom_du_parent(self):
        if not self['nom_du_parent'].html_name in self.data:
            return self.fields['nom_du_parent'].initial
        return self.cleaned_data['nom_du_parent']

    def clean_password(self):
        password = self.cleaned_data.get("password")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

