import uuid

from django.db import models
from django.contrib.auth import models as auth_models
from django.utils import timezone
from datetime import timedelta

"""
Gestion des utilisateurs
"""

class Poste(models.Model):
    nom_du_poste = models.CharField(max_length=255, null=True, blank=False)
    archive = models.BooleanField(default=False)
    # pass

    def __str__(self):
        return self.nom_du_poste


class Niveau(models.Model):
    nom_du_niveau = models.CharField(max_length=255, null=True, blank=False)
    archive = models.BooleanField(default=False)

    def __str__(self):
        return self.nom_du_niveau


class Palier(models.Model):
    nom_du_palier = models.CharField(max_length=255, null=True, blank=False)
    archive = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.nom_du_palier


class Groupe(models.Model):
    nom_du_groupe = models.CharField(max_length=255, null=True, blank=False,
                                     help_text="Le nom du groupe permet de différencier les groupes, ex. Groupe 1")
    manageur_du_groupe = models.CharField(max_length=255,
                                          help_text="Celui pour qui le groupe se cré et contiendra tous ses filleuls")
    archive = models.BooleanField(default=False)

    def __str__(self):
        return self.nom_du_groupe


class CodePays(models.Model):
    pays = models.CharField(max_length=100, null=True, blank=False)
    code_pays = models.CharField(max_length=15, null=True, blank=False)
    archive = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.pays} - {self.code_pays}"

class Droits(models.Model):
    nom_du_droit = models.CharField(max_length=255)
    archive = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.nom_du_droit


class Profils(models.Model):
    nom = models.CharField(max_length=255, null=True)
    archive = models.BooleanField(default=False, null=True)
    droits = models.ManyToManyField(Droits, through="DroitsProfils")

    def __str__(self):
        return self.nom


class DroitsProfils(models.Model):
    profil = models.ForeignKey(Profils, on_delete=models.SET_NULL, null=True)
    droit = models.ForeignKey(Droits, on_delete=models.SET_NULL, null=True)
    ecriture = models.BooleanField(default=False, null=True)
    lecture = models.BooleanField(default=False, null=True)
    modification = models.BooleanField(default=False, null=True)
    suppression = models.BooleanField(default=False, null=True)


class UserManager(auth_models.BaseUserManager):

    def create_user(self, nom_d_utilisateur, nom, prenom, mail, password=None):
        if not nom_d_utilisateur:
            raise ValueError('Users must have an telephone number')
        user = self.model(nom_d_utilisateur=nom_d_utilisateur)
        user.nom = nom
        user.prenom = prenom
        user.mail = mail
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nom_d_utilisateur, nom, prenom, mail, password):
        user = self.create_user(
            nom_d_utilisateur,
            nom=nom,
            prenom=prenom,
            mail=mail,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(auth_models.AbstractBaseUser, auth_models.PermissionsMixin):
    SEXE = (
        (u"Homme", u"Homme"),
        (u"Femme", u"Femme")
    )

    """
    Informations de base
    """
    nom_d_utilisateur = models.CharField(unique=True, max_length=255, null=True, blank=False,
                                         help_text="Le nom d'utilisateur servira à se connecter à la plateforme, "
                                                   "également pour parrainer un membre. Ex. toto21")
    nom_du_parent = models.ForeignKey("self", on_delete=models.SET_NULL, verbose_name='Parrain', null=True, blank=True)
    nom = models.CharField(max_length=255, null=True)
    prenom = models.CharField(max_length=255, blank=False, null=True)
    mail = models.EmailField(null=True, blank=False)
    pays = models.ForeignKey(CodePays, on_delete=models.SET_NULL, null=True, blank=True)
    telephone = models.BigIntegerField(blank=True, null=True, unique=True)
    # telephone = models.CharField(max_length=25, blank=False, null=True, unique=True)
    palier = models.ForeignKey(Palier, null=True, blank=True, on_delete=models.SET_NULL)
    groupe = models.ForeignKey(Groupe, null=True, blank=False, on_delete=models.SET_NULL,
                               verbose_name="Nom de l'équipe",
                               help_text="Le groupe permettra de voir l'ensemble de ses membres")

    """
    Informations supplémentaires
    """
    avatar = models.ImageField(blank=True, null=True, upload_to="avatars")
    annee_de_naissance = models.DateField(null=True, blank=True)
    sexe = models.CharField(choices=SEXE, max_length=120, null=True, blank=True)

    """
    Données systèmes
    """
    don_bam = models.BooleanField(default=False, null=True, blank=True)
    don_zou = models.BooleanField(default=False, null=True, blank=True)
    don_maya = models.BooleanField(default=False, null=True, blank=True)

    profil = models.ForeignKey(Profils, on_delete=models.SET_NULL, null=True, blank=True)
    nb_pers_amene = models.PositiveSmallIntegerField(null=True, blank=True, default=0)

    point = models.PositiveSmallIntegerField(null=True, blank=True, default=0)
    balances = models.JSONField(default=dict, blank=True)  # Balance des achats par catégorie
    points_initial_attribues = models.JSONField(default=dict, blank=True)  # Suivi des points initiaux par catégorie
    palier_recommence = models.IntegerField(default=0, blank=True)

    # auto inscription
    unique_id = models.CharField(max_length=100, null=True, blank=True, unique=True)

    """
    Django settings
    """
    is_active = models.BooleanField(default=True, blank=True)
    is_admin = models.BooleanField(default=False, blank=True)
    date_d_ajout = models.DateTimeField(auto_now_add=True, null=True, blank=True,
                                        verbose_name="Date d'enrégistrement de l'utilisateur")

    objects = UserManager()

    USERNAME_FIELD = 'nom_d_utilisateur'
    REQUIRED_FIELDS = ['nom', 'prenom', 'mail']

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ('-id',)

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?"""
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?"""
        # Simplest possible answer: Yes, always
        return self.is_admin

    @property
    def is_staff(self):
        """Is the user a member of staff?"""
        # Réponse la plus simple possible : Tous les administrateurs sont du personnel
        return self.is_active

    def __unicode__(self):
        # pass
        return u'{0}'.format(self.get_full_name())

    def get_short_name(self):
        # pass
        return self.nom

    def get_full_name(self):
        # pass
        return u'{0} {1}'.format(self.nom, self.prenom)


"""
Gestion des produits : STOCKs
"""

class CategorieProduit(models.Model):
    libelle = models.CharField(max_length=255, unique=True, null=False, verbose_name="Renseigner la catégorie du produit")
    seuil = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Seuil pour générer des points (ex: 8000)
    points_initial = models.IntegerField(default=5)  # Points pour le premier seuil atteint
    points_suivants = models.IntegerField(default=3)  # Points pour les seuils suivants
    points_par_parrainage = models.IntegerField(default=5)  # Points pour le parrainage

    date = models.DateTimeField(auto_now_add=True)
    archive = models.BooleanField(default=False)

    def __str__(self):
        return self.libelle


class Produit(models.Model):
    codeproduit = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    libelle = models.CharField(max_length=100, verbose_name="Désignation du produit")
    description = models.TextField(null=True)
    categorie = models.ForeignKey(CategorieProduit, on_delete=models.SET_NULL, null=True)
    quantite = models.IntegerField()
    madein = models.CharField(max_length=100, blank=True, verbose_name="Pays de fabrication")

    # images produits
    image1 = models.ImageField(null=True, upload_to="produits/")
    image2 = models.ImageField(null=True, blank=True, upload_to="produits/")
    image3 = models.ImageField(null=True, blank=True, upload_to="produits/")
    image4 = models.ImageField(null=True, blank=True, upload_to="produits/")
    image5 = models.ImageField(null=True, blank=True, upload_to="produits/")

    # Informations complémentaires
    marque = models.CharField(max_length=100, null=True, blank=True)
    modele = models.CharField(max_length=100, null=True, blank=True)
    forme = models.CharField(max_length=100, null=True, blank=True)
    couleur = models.CharField(max_length=100, null=True, blank=True)

    date = models.DateTimeField(auto_now_add=True)
    archive = models.BooleanField(default=False)

    def __str__(self):
        return self.libelle


class PrixProduit(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True)
    prix = models.DecimalField(max_digits=15, decimal_places=2)
    ancien_prix = models.DecimalField(max_digits=15, decimal_places=2, null=True, default=0, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    archive = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.produit} - {self.prix}"

    @classmethod
    def nouveau_produit(cls):
        """
        Retourne les instances dont le produit n'a pas dépassé 5 jours.
        """
        limite_temps = timezone.now() - timedelta(days=5)
        return cls.objects.filter(date__gte=limite_temps)


class Panier(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_cree = models.DateTimeField(auto_now_add=True)
    date_modifie = models.DateTimeField(auto_now=True)
    archive = models.BooleanField(default=False)

    def __str__(self):
        return f"Panier de {self.utilisateur} - {self.date_cree}"

class ArticlePanier(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.SET_NULL, null=True, related_name="articles")
    produit = models.ForeignKey(PrixProduit, on_delete=models.SET_NULL, null=True)
    quantite = models.PositiveIntegerField(default=0)
    archive = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.produit} - Quantité : {self.quantite}"


class HistoriqueVente(models.Model):
    STATUT = (
        (u"Achevé", u"Achevé"),
        (u"En attente", u"En attente")
    )
    panier = models.ManyToManyField(ArticlePanier)
    prix = models.DecimalField(max_digits=15, decimal_places=2)
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    commentaire = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(choices=STATUT, max_length=120, null=True, blank=True)
    commande = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return f"Commande de {self.client} le {self.date}"


class Payement(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    type_don = models.CharField(max_length=50)
    palier = models.CharField(max_length=50)
    statut = models.BooleanField(default=False, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)


class GetPoint(models.Model):
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    produit = models.ForeignKey(PrixProduit, on_delete=models.SET_NULL, null=True)
    point = models.PositiveSmallIntegerField(default=0)
    somme = models.DecimalField(max_digits=15, decimal_places=2)
    retrait = models.DecimalField(max_digits=10, decimal_places=2)
    parrainer = models.PositiveSmallIntegerField(default=0)
    reinitialise = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.client} : Point - {self.point}"
