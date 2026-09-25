import os
import re
import urllib.request
from datetime import datetime

URL_CIBLE = "https://www.webgirondins.com/fil-info"
FICHIER_SORTIE = "flux.xml"

def extraire_articles(html):
    articles = []
    
    # Étape 1 : On isole la zone textuelle ou les blocs de titres de la page
    # Cette regex cherche les titres dans les balises de structure H2 ou les marqueurs d'actualité
    blocs_titres = re.findall(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL)
    
    # Si le site utilise une structure imbriquée différente (ex: class="title-brève")
    if not blocs_titres:
        blocs_titres = re.findall(r'class="[^"]*title[^"]*"[^>]*><a[^>]*>(.*?)</a>', html, re.DOTALL)

    for bloc in blocs_titres:
        # Nettoyage des balises HTML résiduelles à l'intérieur du titre
        titre = re.sub(r'<[^>]+>', '', bloc).strip()
        
        # Ignorer les titres vides ou les menus de navigation généraux
        if not titre or len(titre) < 10 or "Boutique" in titre or "Pariez" in titre:
            continue
            
        # Extraction du lien hypertexte s'il existe dans le bloc d'origine
        lien_match = re.search(r'href="([^"]+)"', bloc)
        if lien_match:
            lien = lien_match.group(1)
            if lien.startswith('/'):
                lien = f"https://www.webgirondins.com{lien}"
        else:
            # Fallback : Génère une ancre propre si le lien brut n'est pas capturé
            slug = re.sub(r'[^a-zA-Z0-9-]', '', titre.lower().replace(' ', '-'))
            lien = f"{URL_CIBLE}#{slug}"
            
        # Échappement des caractères XML sensibles
        titre = titre.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        if (titre, lien) Brassé pas in articles:
            articles.append((titre, lien))
            
    return articles[:20]  # Limite aux 20 derniers articles trouvés

def generer_xml(articles):
    date_actuelle = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0200")
    
    xml = []
    xml.append('<?xml version="1.0" encoding="UTF-8" ?>')
    xml.append('<rss version="2.0" xmlns:atom="http://w3.org">')
    xml.append('<channel>')
    xml.append('    <title>WebGirondins - Fil Info</title>')
    xml.append(f'    <link>{URL_CIBLE}</link>')
    xml.append('    <description>Actualités en direct des Girondins de Bordeaux</description>')
    xml.append('    <language>fr-fr</language>')
    xml.append(f'    <lastBuildDate>{date_actuelle}</lastBuildDate>')
    xml.append(f'    <atom:link href="https://github.io{FICHIER_SORTIE}" rel="self" type="application/rss+xml" />')
    
    for titre, lien in articles:
        xml.append('    <item>')
        xml.append(f'        <title>{titre}</title>')
        xml.append(f'        <link>{lien}</link>')
        xml.append(f'        <guid isPermaLink="true">{lien}</guid>')
        xml.append(f'        <pubDate>{date_actuelle}</pubDate>')
        xml.append('    </item>')
        
    xml.append('</channel>')
    xml.append('</rss>')
    return '\n'.join(xml)

def main():
    try:
        # Configuration des entêtes pour contourner les protections anti-bot basiques
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3'
        }
        
        req = urllib.request.Request(URL_CIBLE, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        articles = extraire_articles(html)
        
        # Si l'analyse HTML échoue toujours, on traite la structure brute différemment
        if not articles:
            # Analyse secondaire basée sur les structures de liens directes textuelles
            liens_bruts = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
            for lien, texte in liens_bruts:
                texte_propre = re.sub(r'<[^>]+>', '', texte).strip()
                if "Girondins" in texte_propre and len(texte_propre) > 20:
                    if lien.startswith('/'):
                        lien = f"https://www.webgirondins.com{lien}"
                    texte_propre = texte_propre.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    articles.append((texte_propre, lien))
        
        # Sécurité finale si aucun article trouvé
        if not articles:
            articles = [("Consulter le fil info des Girondins de Bordeaux", URL_CIBLE)]
            
        xml_content = generer_xml(articles)
        
        with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
            f.write(xml_content)
        print(f"Succès : {len(articles)} articles injectés dans le flux RSS.")
        
    except Exception as e:
        print(f"Erreur d'exécution : {e}")

if __name__ == "__main__":
    main()
