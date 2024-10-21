from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string

from affiliation.forms import ProduitForm, CategorieProduitForm, PrixProduitForm, ArticlePanierForm, UserUpdateForm, \
    PayDashForm, UserCreation20Form
from .forms import SelectionUtilisateurForm
from affiliation.models import Produit, CategorieProduit, PrixProduit, Panier, ArticlePanier, HistoriqueVente, User, \
    Palier, Payement, Groupe
from django.contrib.auth.decorators import login_required


import decimal

def decimal_to_float(val):
    if isinstance(val, decimal.Decimal):
        return float(val)
    return val


# gestion du frontend
def produitfrontend(request):
    """try:
        panier = Panier.objects.get(utilisateur=request.user)
        articles = panier.articles.filter(archive=False)
        nombre_articles = articles.count()
    except Panier.DoesNotExist:
        panier = 'PANIER'
        nombre_articles = 0"""

    produits = PrixProduit.objects.filter(archive=False)

    valider_commande = request.session.pop('valider_commande', False)

    ajout_reussi = request.session.pop('ajout_reussi', False)

    all_categorie = CategorieProduit.objects.filter(archive=False)
    vedettes = PrixProduit.nouveau_produit()
    return render(request, 'frontend/produit/produitfrontend.html', locals())



def detailproduitfrontend(request, id):
    """try:
        panier = Panier.objects.get(utilisateur=request.user)
        articles = panier.articles.filter(archive=False)
        nombre_articles = articles.count()
    except Panier.DoesNotExist:
        panier = 'PANIER'
        nombre_articles = 0"""

    get_product = PrixProduit.objects.get(id=id)
    all_categorie = CategorieProduit.objects.filter(archive=False)
    vedettes = PrixProduit.nouveau_produit()
    return render(request, 'frontend/produit/detailproduitfrontend.html', locals())


@login_required
def ajouter_au_panier_frontend(request, id):
    produit = get_object_or_404(PrixProduit, id=id)
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)

    if request.method == "POST":
        quantite = int(request.POST.get('quantite', 1))
        print("quantité: ", quantite)
        article, created = ArticlePanier.objects.get_or_create(panier=panier, produit=produit)
        if not created:
            article.quantite += quantite
        else:
            article.quantite = quantite
        article.save()

    # Ajouter une variable dans la session pour indiquer que l'ajout a été réussi
    request.session['ajout_reussi'] = True

    # return JsonResponse({"success": True, "message": f"{produit.produit.libelle} a été ajouté à votre panier."})
    return redirect('produitfrontend')


@login_required
def voir_panierfrontend(request):
    all_categorie = CategorieProduit.objects.filter(archive=False)
    vedettes = PrixProduit.nouveau_produit()
    panier = Panier.objects.get(utilisateur=request.user)
    articles = panier.articles.filter(archive=False)
    nombre_articles = articles.count()

    articlespanier = ArticlePanier.objects.filter(archive=False, panier=panier)

    # Calculer le sous-total pour chaque article et le total du panier
    articles_avec_sous_total = []
    total = 0
    for article in articles:
        sous_total = article.quantite * article.produit.prix
        articles_avec_sous_total.append({
            'article': article,
            'sous_total': sous_total
        })
        total += sous_total

    context = {
        'all_categorie': all_categorie,
        'vedettes': vedettes,
        'panier': panier,
        'articles_avec_sous_total': articles_avec_sous_total,
        'total': total,
        'nombre_articles': nombre_articles,
        'articlespanier': articlespanier,
    }

    return render(request, 'frontend/panierfront/panierfront.html', context)


@login_required
def updatepanierfrontend(request, id):
    panier = Panier.objects.get(utilisateur=request.user)
    articlespanier = ArticlePanier.objects.filter(archive=False, panier=panier)
    mycontext = {
        'articlespanier': articlespanier
    }
    article = get_object_or_404(ArticlePanier, id=id)
    if request.method == 'POST':
        form = ArticlePanierForm(request.POST, instance=article)
    else:
        form = ArticlePanierForm(instance=article)
    return save_all(request, form, 'frontend/panierfront/updatepanierfrontend.html', 'panier',
                    'frontend/panierfront/listpanierfront.html', mycontext)


@login_required
def deletearticlepanierfrontend(request, id):
    data = dict()
    article = get_object_or_404(ArticlePanier, id=id)
    if request.method == "POST":
        article.delete()
        data['form_is_valid'] = True
        panier = Panier.objects.get(utilisateur=request.user)
        articlespanier = ArticlePanier.objects.filter(archive=False, panier=panier)
        data['panier'] = render_to_string('frontend/panierfront/listpanierfront.html',
                                          {'articlespanier': articlespanier})
    else:
        context = {
            'article': article
        }
        data['html_form'] = render_to_string('frontend/panierfront/deletearticlefrontend.html', context, request=request)

    return JsonResponse(data)


@login_required
def soumettre_panierfrontend(request):
    panier = get_object_or_404(Panier, utilisateur=request.user, archive=False)
    articles = ArticlePanier.objects.filter(panier=panier, archive=False)

    if not articles.exists():
        return redirect('voir_panierfrontend')

    prix_total = sum(article.quantite * article.produit.prix for article in articles)
    statut = "En attente"

    # Création de l'historique de vente
    historique = HistoriqueVente.objects.create(
        prix=prix_total,
        client=request.user,
        statut=statut,
    )

    # Ajout des articles du panier à l'historique
    for article in articles:
        historique.panier.add(article)

    historique.save()

    # Vider le panier associé
    utilisateur = request.user
    panieravider = Panier.objects.filter(utilisateur=utilisateur)
    panieravider.delete()

    request.session['valider_commande'] = True

    return redirect('produitfrontend')


def save_all(request, form, template_name, model, template_name2, mycontext):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            if model == "stock":
                system = form.save(commit=False)
                system.save()

                data['form_is_valid'] = True
                data[model] = render_to_string(template_name2, mycontext)
            else:
                form.save()
                data['form_is_valid'] = True
                data[model] = render_to_string(template_name2, mycontext)
        else:
            data['form_is_valid'] = False

    context = {
        'form': form
    }
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


@login_required
def dash(request):
    try:
        # affichage du panier sur tous les pages
        panier = Panier.objects.get(utilisateur=request.user)
        articles = panier.articles.filter(archive=False)
        nombre_articles = articles.count()
    except Panier.DoesNotExist:
        panier = None

    commande_acheve_count = HistoriqueVente.objects.filter(statut="Achevé").count()
    commande_en_attente_count = HistoriqueVente.objects.filter(statut="En attente").count()
    categorie_count = CategorieProduit.objects.filter(archive=False).count()
    produit_count = Produit.objects.filter(archive=False).count()
    payement_count = Payement.objects.filter(statut=False).count()
    payements = Payement.objects.filter(statut=False)
    groupe_count = Groupe.objects.filter(archive=False).count()
    users_count_is_admin = User.objects.filter(is_admin=True).count()

    return render(request, 'dash/dashboard.html', locals())


@login_required
def paydash(request, id):
    payements = Payement.objects.filter(statut=False)
    mycontext = {
        'payements': payements
    }
    paydashmemb = get_object_or_404(Payement, id=id)
    if request.method == 'POST':
        p_form = PayDashForm(request.POST, instance=paydashmemb)
    else:
        p_form = PayDashForm(instance=paydashmemb)
    return save_all(request, p_form, 'dash/paydash.html', 'paydash',
                    'dash/listpaydash.html', mycontext)


@login_required
def stock(request):
    products = Produit.objects.filter(archive=False)
    return render(request, 'stock/stock.html', locals())


@login_required
def addproduct(request):
    if request.method == 'POST':
        p_form = ProduitForm(request.POST, request.FILES)
        if p_form.is_valid():
            p_form.save()
            return redirect('addproduct')
    else:
        p_form = ProduitForm()

    count_product = Produit.objects.filter(archive=False).count()
    products = Produit.objects.filter(archive=False)
    count_quantity = 0
    for product in products:
        count_quantity += product.quantite
    return render(request, 'stock/addproduct.html', locals())


@login_required
def updatestock(request, id):
    products = Produit.objects.filter(archive=False)
    mycontext = {
        'products': products
    }
    product = get_object_or_404(Produit, id=id)
    if request.method == 'POST':
        form = ProduitForm(request.POST, instance=product)
    else:
        form = ProduitForm(instance=product)
    return save_all(request, form, 'stock/updatestock.html', 'stock',
                    'stock/liststock.html', mycontext)


@login_required
def deletestock(request, id):
    data = dict()
    product = get_object_or_404(Produit, id=id)
    if request.method == "POST":
        product.archive = True
        product.save()
        data['form_is_valid'] = True
        products = Produit.objects.filter(archive=False)
        data['stock'] = render_to_string('stock/liststock.html', {'products': products})
    else:
        context = {
            'product': product
        }
        data['html_form'] = render_to_string('stock/deletestock.html', context, request=request)

    return JsonResponse(data)


@login_required
def categorieproduct(request):
    categories = CategorieProduit.objects.filter(archive=False)
    return render(request, 'stock/type/categorieproduct.html', locals())


@login_required
def addcategoriestock(request):
    categories = CategorieProduit.objects.filter(archive=False)
    if request.method == 'POST':
        form = CategorieProduitForm(request.POST)
    else:
        form = CategorieProduitForm()
    mycontext = {'categories': categories, 'form': form}
    return save_all(request, form, 'stock/type/addcategoriestock.html',
                    'categoriestock', 'stock/type/listcategoriestock.html', mycontext)


@login_required
def updatecategoriestock(request, id):
    categories = CategorieProduit.objects.filter(archive=False)
    mycontext = {
        'categories': categories
    }
    categorie = get_object_or_404(CategorieProduit, id=id)
    if request.method == 'POST':
        form = CategorieProduitForm(request.POST, instance=categorie)
    else:
        form = CategorieProduitForm(instance=categorie)
    return save_all(request, form, 'stock/type/updatecategoriestock.html', 'categoriestock',
                    'stock/type/listcategoriestock.html', mycontext)


@login_required
def deletecategoriestock(request, id):
    data = dict()
    categorie = get_object_or_404(CategorieProduit, id=id)
    if request.method == "POST":
        categorie.archive = True
        categorie.save()
        data['form_is_valid'] = True
        categories = CategorieProduit.objects.filter(archive=False)
        data['categoriestock'] = render_to_string('stock/type/listcategoriestock.html', {'categories': categories})
    else:
        context = {
            'categorie': categorie
        }
        data['html_form'] = render_to_string('stock/type/deletecategoriestock.html', context, request=request)

    return JsonResponse(data)


@login_required
def prixproduit(request):
    prixproduits = PrixProduit.objects.filter(archive=False)

    produits_avec_prix_ids = PrixProduit.objects.values_list('produit_id', flat=True)

    # Trouver les produits qui ne sont pas dans la liste des produits ayant un prix
    produits_sans_prix = Produit.objects.exclude(id__in=produits_avec_prix_ids)

    return render(request, 'stock/prix/prixproduit.html', locals())


@login_required
def addprixproduit(request):
    prixproduits = PrixProduit.objects.filter(archive=False)
    if request.method == 'POST':
        form = PrixProduitForm(request.POST)
    else:
        form = PrixProduitForm()
    mycontext = {'prixproduits': prixproduits, 'form': form}
    return save_all(request, form, 'stock/prix/addprixproduit.html',
                    'prixproduit', 'stock/prix/listprixproduit.html', mycontext)


@login_required
def updateprixproduit(request, id):
    prixproduits = PrixProduit.objects.filter(archive=False)
    mycontext = {
        'prixproduits': prixproduits
    }
    prixproduit = get_object_or_404(PrixProduit, id=id)
    if request.method == 'POST':
        form = PrixProduitForm(request.POST, instance=prixproduit)
    else:
        form = PrixProduitForm(instance=prixproduit)
    return save_all(request, form, 'stock/prix/updateprixproduit.html', 'prixproduit',
                    'stock/prix/listprixproduit.html', mycontext)


@login_required
def deleteprixproduit(request, id):
    data = dict()
    prixproduit = get_object_or_404(PrixProduit, id=id)
    if request.method == "POST":
        prixproduit.archive = True
        prixproduit.save()
        data['form_is_valid'] = True
        prixproduits = PrixProduit.objects.filter(archive=False)
        data['prixproduit'] = render_to_string('stock/prix/listprixproduit.html', {'prixproduits': prixproduits})
    else:
        context = {
            'prixproduit': prixproduit
        }
        data['html_form'] = render_to_string('stock/prix/deleteprixproduit.html', context, request=request)

    return JsonResponse(data)


# gestion du panier
"""def boutique(request):
    try:
        # affichage du panier sur tous les pages
        panier = Panier.objects.get(utilisateur=request.user)
        articles = panier.articles.filter(archive=False)
        nombre_articles = articles.count()
    except Panier.DoesNotExist:
        panier = None

    produits = PrixProduit.objects.filter(archive=False)

    valider_commande = request.session.pop('valider_commande', False)

    ajout_reussi = request.session.pop('ajout_reussi', False)

    return render(request, 'vente/boutique.html', locals())
    """


@login_required
def boutique(request):
    produits = PrixProduit.objects.filter(archive=False)
    valider_commande = request.session.pop('valider_commande', False)
    ajout_reussi = request.session.pop('ajout_reussi', False)

    # Vérifier si un utilisateur est déjà sélectionné dans la session
    utilisateur_selectionne_id = request.session.get('utilisateur_selectionne_id', None)
    utilisateur_selectionne = None

    # Si un utilisateur est déjà sélectionné, on le récupère
    if utilisateur_selectionne_id:
        utilisateur_selectionne = get_user_model().objects.get(id=utilisateur_selectionne_id)
        form = None  # Pas besoin du formulaire si un utilisateur est sélectionné
    else:
        # Si aucun utilisateur n'est sélectionné, afficher le formulaire
        if request.method == "POST":
            form = SelectionUtilisateurForm(request.POST)
            if form.is_valid():
                # Stocker l'utilisateur sélectionné dans la session
                utilisateur_selectionne = form.cleaned_data['utilisateur']
                request.session['utilisateur_selectionne_id'] = utilisateur_selectionne.id
                return redirect('boutique')  # Rediriger pour éviter les soumissions multiples
        else:
            form = SelectionUtilisateurForm()  # Afficher le formulaire si aucun utilisateur n'est sélectionné

    return render(request, 'vente/boutique.html', {
        'produits': produits,
        'form': form,  # Ne sera envoyé au template que si aucun utilisateur n'est sélectionné
        'utilisateur_selectionne': utilisateur_selectionne,  # L'utilisateur sélectionné sera envoyé au template si disponible
        'valider_commande': valider_commande,
        'ajout_reussi': ajout_reussi
    })


@login_required
def detailproduit(request, id):
    # Récupérer l'utilisateur sélectionné dans la session
    utilisateur_selectionne_id = request.session.get('utilisateur_selectionne_id', None)

    # Si aucun utilisateur n'a été sélectionné, on peut par exemple rediriger vers la boutique pour forcer la sélection
    if not utilisateur_selectionne_id:
        return redirect('boutique')

    # Récupérer l'utilisateur sélectionné
    utilisateur_selectionne = get_user_model().objects.get(id=utilisateur_selectionne_id)

    try:
        # Affichage du panier sur toutes les pages, en utilisant l'utilisateur sélectionné
        panier = Panier.objects.get(utilisateur=utilisateur_selectionne)
        articles = panier.articles.filter(archive=False)
        nombre_articles = articles.count()
    except Panier.DoesNotExist:
        panier = None

    detail = get_object_or_404(PrixProduit, id=id)
    return render(request, 'vente/detailproduit.html', locals())



@login_required
def ajouter_au_panier(request, id):
    # Récupérer l'utilisateur sélectionné dans la session
    utilisateur_selectionne_id = request.session.get('utilisateur_selectionne_id', None)

    # Si aucun utilisateur n'a été sélectionné, on peut rediriger vers la boutique pour sélectionner un utilisateur
    if not utilisateur_selectionne_id:
        return redirect('boutique')

    # Récupérer l'utilisateur sélectionné
    utilisateur_selectionne = get_user_model().objects.get(id=utilisateur_selectionne_id)

    # Récupérer le produit à ajouter au panier
    produit = get_object_or_404(PrixProduit, id=id)

    # Créer ou récupérer le panier associé à l'utilisateur sélectionné
    panier, created = Panier.objects.get_or_create(utilisateur=utilisateur_selectionne)

    if request.method == "POST":
        quantite = int(request.POST.get('quantite', 1))  # Récupérer la quantité du produit
        # Ajouter le produit au panier ou mettre à jour la quantité si déjà présent
        article, created = ArticlePanier.objects.get_or_create(panier=panier, produit=produit)
        if not created:
            article.quantite += quantite
        else:
            article.quantite = quantite
        article.save()

    # Ajouter une variable dans la session pour indiquer que l'ajout a été réussi
    request.session['ajout_reussi'] = True

    # Rediriger vers la boutique après ajout au panier
    return redirect('boutique')


@login_required
def voir_panier(request):
    # Récupérer l'utilisateur sélectionné dans la session
    utilisateur_selectionne_id = request.session.get('utilisateur_selectionne_id', None)

    # Si aucun utilisateur n'a été sélectionné, on peut rediriger vers la boutique pour sélectionner un utilisateur
    if not utilisateur_selectionne_id:
        return redirect('boutique')

    # Récupérer l'utilisateur sélectionné
    utilisateur_selectionne = get_user_model().objects.get(id=utilisateur_selectionne_id)

    # Récupérer le panier de l'utilisateur sélectionné
    panier = get_object_or_404(Panier, utilisateur=utilisateur_selectionne)

    # Récupérer les articles du panier
    articles = panier.articles.filter(archive=False)
    nombre_articles = articles.count()

    # Récupérer les articles du panier (à vérifier si nécessaire, sinon cette ligne peut être supprimée)
    articlespanier = ArticlePanier.objects.filter(archive=False, panier=panier)

    # Calculer le sous-total pour chaque article et le total du panier
    articles_avec_sous_total = []
    total = 0
    for article in articles:
        sous_total = article.quantite * article.produit.prix
        articles_avec_sous_total.append({
            'article': article,
            'sous_total': sous_total
        })
        total += sous_total

    # Passer les données à la vue
    context = {
        'panier': panier,
        'articles_avec_sous_total': articles_avec_sous_total,
        'total': total,
        'nombre_articles': nombre_articles,
        'articlespanier': articlespanier,
    }

    return render(request, 'vente/panier/panier.html', context)


@login_required
def updatepanier(request, id):
    # Récupérer l'utilisateur sélectionné dans la session
    utilisateur_selectionne_id = request.session.get('utilisateur_selectionne_id', None)

    # Si aucun utilisateur n'a été sélectionné, on peut rediriger vers la boutique pour sélectionner un utilisateur
    if not utilisateur_selectionne_id:
        return redirect('boutique')

    # Récupérer l'utilisateur sélectionné
    utilisateur_selectionne = get_user_model().objects.get(id=utilisateur_selectionne_id)

    # Récupérer le panier de l'utilisateur sélectionné
    panier = get_object_or_404(Panier, utilisateur=utilisateur_selectionne)

    # Récupérer les articles du panier
    articlespanier = ArticlePanier.objects.filter(archive=False, panier=panier)

    # Contexte à passer à la vue
    mycontext = {
        'articlespanier': articlespanier
    }

    # Récupérer l'article à mettre à jour
    article = get_object_or_404(ArticlePanier, id=id)

    # Si la méthode est POST, traiter le formulaire avec les données envoyées
    if request.method == 'POST':
        form = ArticlePanierForm(request.POST, instance=article)
    else:
        # Si ce n'est pas une requête POST, afficher le formulaire avec les données actuelles
        form = ArticlePanierForm(instance=article)

    # Sauvegarder le formulaire et rediriger si le formulaire est valide
    return save_all(request, form, 'vente/panier/updatepanier.html', 'panier',
                    'vente/panier/listpanier.html', mycontext)


@login_required
def deletearticlepanier(request, id):
    data = dict()

    # Récupérer l'utilisateur sélectionné dans la session
    utilisateur_selectionne_id = request.session.get('utilisateur_selectionne_id', None)

    # Si aucun utilisateur n'a été sélectionné, on peut rediriger vers la boutique pour sélectionner un utilisateur
    if not utilisateur_selectionne_id:
        return redirect('boutique')

    # Récupérer l'utilisateur sélectionné
    utilisateur_selectionne = get_user_model().objects.get(id=utilisateur_selectionne_id)

    # Récupérer l'article du panier à supprimer
    article = get_object_or_404(ArticlePanier, id=id, panier__utilisateur=utilisateur_selectionne)

    # Si la méthode est POST, on marque l'article comme archivé (supprimé)
    if request.method == "POST":
        article.archive = True
        article.save()

        # Indiquer que la suppression est valide
        data['form_is_valid'] = True

        # Récupérer le panier de l'utilisateur sélectionné
        panier = get_object_or_404(Panier, utilisateur=utilisateur_selectionne)

        # Récupérer les articles du panier mis à jour
        articlespanier = ArticlePanier.objects.filter(archive=False, panier=panier)

        # Mettre à jour le panier dans la réponse
        data['panier'] = render_to_string('vente/panier/listpanier.html', {'articlespanier': articlespanier})

    else:
        # Si ce n'est pas une requête POST, afficher le formulaire de confirmation de suppression
        context = {
            'article': article
        }
        data['html_form'] = render_to_string('vente/panier/deletearticlepanier.html', context, request=request)

    return JsonResponse(data)



@login_required
def soumettre_panier(request):
    # Récupérer l'utilisateur sélectionné depuis la session
    utilisateur_selectionne_id = request.session.get('utilisateur_selectionne_id', None)

    # Si aucun utilisateur n'est sélectionné, rediriger vers la boutique pour en choisir un
    if not utilisateur_selectionne_id:
        return redirect('boutique')

    # Récupérer l'utilisateur sélectionné
    utilisateur_selectionne = get_user_model().objects.get(id=utilisateur_selectionne_id)

    # Récupérer le panier de l'utilisateur sélectionné
    panier = get_object_or_404(Panier, utilisateur=utilisateur_selectionne, archive=False)
    articles = ArticlePanier.objects.filter(panier=panier)

    # Si le panier est vide, rediriger vers la vue de visualisation du panier
    if not articles.exists():
        return redirect('voir_panier')

    # Calcul du prix total du panier
    prix_total = sum(article.quantite * article.produit.prix for article in articles)
    statut = "En attente"

    # Création de l'historique de vente
    historique = HistoriqueVente.objects.create(
        prix=prix_total,
        client=utilisateur_selectionne,
        statut=statut,
    )

    # Ajout des articles du panier à l'historique
    for article in articles:
        historique.panier.add(article)

    historique.save()

    # Vider le panier associé
    panier.delete()

    # Marquer la commande comme validée dans la session
    request.session['valider_commande'] = True

    # Supprimer l'utilisateur sélectionné de la session pour permettre de sélectionner un autre utilisateur
    if 'utilisateur_selectionne_id' in request.session:
        del request.session['utilisateur_selectionne_id']

    # Rediriger vers la boutique après la soumission du panier
    return redirect('boutique')


# gestion des ventes
@login_required
def vente(request):
    historiques = HistoriqueVente.objects.filter(archive=False).order_by('-date')

    context = {
        'historiques': historiques,
    }
    return render(request, 'vente/vente.html', context)


@login_required
def mettre_a_jour_statut(request, historique_id, statut):
    commande = get_object_or_404(HistoriqueVente, id=historique_id)

    commande.statut = statut
    commande.save()

    if statut == "Achevé":
        for article in commande.panier.all():
            produit = article.produit.produit
            montant_achat = article.quantite * float(article.produit.prix)
            categorie = produit.categorie

            redirection = mettre_a_jour_points(commande.client, categorie, montant_achat)

            produit.quantite -= article.quantite
            produit.save()

            if redirection:
                return redirection

    # return redirect('vente')



@login_required
def profile(request):
    try:
        # affichage du panier sur tous les pages
        panier = Panier.objects.get(utilisateur=request.user)
        articles = panier.articles.filter(archive=False)
        nombre_articles = articles.count()
    except Panier.DoesNotExist:
        panier = None

    utilisateur = User.objects.get(is_active=True, id=request.user.id)
    historiques = HistoriqueVente.objects.filter(client=utilisateur, archive=False)

    if utilisateur.palier is not None:
        palier = utilisateur.palier.nom_du_palier

    user_bill = Payement.objects.filter(utilisateur=utilisateur, statut=False)
    user_bill_count = Payement.objects.filter(utilisateur=utilisateur).count()

    import uuid

    utilisateur = request.user
    if utilisateur.unique_id is None:
        utilisateur.unique_id = uuid.uuid4()
        utilisateur.save()

    pourcentages_paliers = {
        "Bamiléké": int(min(utilisateur.point / 35 * 100, 100)),
        "Zoulou": int(min((utilisateur.point - 35) / (155 - 35) * 100, 100)) if utilisateur.point > 35 else 0,
        "Maya": int(min((utilisateur.point - 155) / (485 - 155) * 100, 100)) if utilisateur.point > 155 else 0
    }

    return render(request, 'Profile/profile.html', locals())


@login_required
def editerprofile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if u_form.is_valid():
            u_form.save()
    else:
        u_form = UserUpdateForm(instance=request.user)

    return render(request, 'profile/editerprofile.html', locals())


"""
def generate_lien(request, unique_id):
    parrain = get_object_or_404(User, unique_id=unique_id)
    groupe_parrain_html = parrain.groupe
    nom_parrain_html = parrain

    groupe_parrain = parrain.groupe
    nom_parrain = parrain

    if request.method == 'POST':
        form = UserCreation20Form(request.POST, request.FILES,
                                  initial={'groupe': groupe_parrain, 'nom_du_parent': nom_parrain})
        if form.is_valid():
            if form.is_valid():
                form.save(commit=False)
                systeme = form.save()
                return redirect('mongroupe')
        else:
            form = UserCreation20Form(initial={'groupe': groupe_parrain, 'nom_du_parent': nom_parrain})

    return render(request, 'investissement/generate_lien.html', locals())
"""

def mettre_a_jour_points(utilisateur, categorie, montant_achat):
    if categorie.libelle not in utilisateur.balances:
        utilisateur.balances[categorie.libelle] = 0
    if categorie.libelle not in utilisateur.points_initial_attribues:
        utilisateur.points_initial_attribues[categorie.libelle] = False

    utilisateur.balances[categorie.libelle] += montant_achat

    while utilisateur.balances[categorie.libelle] >= categorie.seuil:
        if not utilisateur.points_initial_attribues[categorie.libelle]:
            utilisateur.point += categorie.points_initial
            utilisateur.points_initial_attribues[categorie.libelle] = True

            attribuer_points_parrains_hierarchie(utilisateur, categorie)
        else:
            utilisateur.point += categorie.points_suivants

        # Réduction de la balance fictive par le seuil atteint
        utilisateur.balances[categorie.libelle] -= float(categorie.seuil)

        utilisateur.save()

    utilisateur.save()

    redirection = verifier_palier(utilisateur)

    if redirection:
        return redirection


def attribuer_points_parrains_hierarchie(utilisateur, categorie):
    if utilisateur.nom_du_parent:
        attribuer_points_parrain(utilisateur.nom_du_parent, categorie)


def attribuer_points_parrain(parrain, categorie):
    # Calcul des points attribués au parrain en fonction de la catégorie
    points_attribues = categorie.points_par_parrainage
    parrain.point += points_attribues
    parrain.save()

    # Récompense parrains du parrain (hiérarchie)
    if parrain.nom_du_parent:
        attribuer_points_parrain(parrain.nom_du_parent, categorie)


def verifier_palier(utilisateur):
    if utilisateur.point >= 35 and not utilisateur.don_bam:
        utilisateur.don_bam = True
        palier1 = get_object_or_404(Palier, nom_du_palier="Bamiléké")
        utilisateur.palier = palier1
        utilisateur.save()
        return redirect('choix_palier', utilisateur_id=utilisateur.id, palier_id=palier1.id)

    elif utilisateur.point >= 155 and not utilisateur.don_zou:
        utilisateur.don_zou = True
        palier2 = get_object_or_404(Palier, nom_du_palier="Zoulou")
        utilisateur.palier = palier2
        utilisateur.save()
        return redirect('choix_palier', utilisateur_id=utilisateur.id, palier_id=palier2.id)

    elif utilisateur.point >= 485 and not utilisateur.don_maya:
        utilisateur.don_maya = True
        palier3 = get_object_or_404(Palier, nom_du_palier="Maya")
        utilisateur.palier = palier3
        utilisateur.save()
        return redirect('choix_palier', utilisateur_id=utilisateur.id, palier_id=palier3.id)

    return redirect('vente')


def choix_palier(request, utilisateur_id, palier_id):
    utilisateur = get_object_or_404(User, id=utilisateur_id)
    palier = get_object_or_404(Palier, id=palier_id)

    if request.method == 'POST':
        decision = request.POST.get('decision')

        if decision == 'quitter':
            if palier.nom_du_palier == "Bamiléké":
                creer_payement(utilisateur, montant=15000, type_don="quitter le programme", palier="Bamiléké", statut=False)
            elif palier.nom_du_palier == "Zoulou":
                creer_payement(utilisateur, montant=75000, type_don="quitter le programme", palier="Zoulou", statut=False)
            elif palier.nom_du_palier == "Maya":
                creer_payement(utilisateur, montant=300000, type_don="quitter le programme", palier="Maya", statut=False)

        elif decision == 'rester':
            if palier.nom_du_palier == "Bamiléké":
                creer_payement(utilisateur, montant=5000, type_don="continuer le programme", palier="Bamiléké", statut=False)
                creer_payement(utilisateur, montant=-10000, type_don="Don pour le palier Zoulou", palier="Bamiléké", statut=True)
            elif palier.nom_du_palier == "Zoulou":
                creer_payement(utilisateur, montant=20000, type_don="continuer le programme", palier="Zoulou", statut=False)
                creer_payement(utilisateur, montant=-55000, type_don="Don pour le palier Maya", palier="Zoulou", statut=True)
            elif palier.nom_du_palier == "Maya":
                creer_payement(utilisateur, montant=300000, type_don="Terminé", palier="Maya", statut=False)

        return redirect('vente')

    return render(request, 'payement/choix_palier.html', {'utilisateur': utilisateur, 'palier': palier})


def creer_payement(utilisateur, montant, type_don, palier, statut):
    Payement.objects.create(
        utilisateur=utilisateur,
        montant=montant,
        type_don=type_don,
        palier=palier,
        statut=statut
    )


@login_required
def user_creation(request):
    admin_count = User.objects.filter(is_active=True, is_admin=True).count
    user_count = User.objects.filter(is_active=True).count
    if request.method == 'POST':
        u_form = UserCreation20Form(request.POST, request.FILES)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, 'Utilisateur créé avec succès !')  # Message de succès
            return redirect('user_creation')
        else:
            messages.error(request, 'Erreur lors de la création de l\'utilisateur.')  # Message d'erreur
    else:
        u_form = UserCreation20Form()

    # Passe explicitement les variables à la vue pour plus de clarté
    context = {
        'u_form': u_form,
        'user_count': user_count,
        'admin_count': admin_count,
    }
    return render(request, 'Profile/user_creation.html', context)


"""
@login_required
def change_password(request, id):
    user_u = get_object_or_404(User, id=id)
    if request.method == 'POST':
        form = PasswordChangeForm(user_u, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Le mot de passe a bien été enrégistré')
            return redirect('listeupdateuser', user_u.id)
        else:
            messages.error(request, 'ERREUR | VERIFIER VOS DONNEES')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'affiliation/password_change_form.html', {
        'form': form,
        'user_u': user_u
    })
"""