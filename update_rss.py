import os
import re
import urllib.request
from datetime import datetime

# Configuration
URL_CIBLE = "https://www.webgirondins.com/fil-info"
FICHIER_SORTIE = "flux.xml"

def extraire_articles(html):
    articles = []
    # Recherche les blocs de titres H2 contenant les liens et titres d'articles
    pattern = re.compile(r'<h2><a[^>]*href="([^"]+)"[^>]*>(.*?)</a></h2>', re.DOTALL)
    
    # Si la structure simplifiée de la page brute est lue (comme le texte extrait)
    # Recherche les lignes commençant par "## " ou de simples structures de titres
    matches = re.findall(r'## (.*?)\n', html)
    
    if matches:
        for match in matches[:15]:  # Prendre les 15 derniers articles
            titre = match.strip()
            # Nettoyer les caractères spéciaux basiques
            titre = titre.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            # Générer un lien fictif basé sur le texte si le vrai lien n'est pas capturé par Regex simple
            slug = re.sub(r'[^a-zA-Z0-9-]', '', titre.lower().replace(' ', '-'))
            lien = f"{URL_CIBLE}#{slug}"
            articles.append((titre, lien))
    return articles

def generer_xml(articles):
    date_actuelle = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0200")
    
    xml = []
    xml.append('<?xml version="1.0" encoding="UTF-8" ?>')
    xml.append('<rss version="2.0" xmlns:atom="http://w3.org">')
    xml.append('<channel>')
    xml.append('    <title>WebGirondins - Fil Info Automatique</title>')
    xml.append(f'    <link>{URL_CIBLE}</link>')
    xml.append('    <description>Flux mis à jour automatiquement via GitHub Actions</description>')
    xml.append('    <language>fr-fr</language>')
    xml.append(f'    <lastBuildDate>{date_actuelle}</lastBuildDate>')
    
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
        req = urllib.request.Request(URL_CIBLE, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        articles = extraire_articles(html)
        if not articles:
            # Fallback si la structure HTML est différente de la structure texte attendue
            # Crée un item de statut par défaut
            articles = [("Mise à jour du fil info Girondins", URL_CIBLE)]
            
        xml_content = generer_xml(articles)
        
        with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
            f.write(xml_content)
        print("Flux RSS mis à jour avec succès.")
    except Exception as e:
        print(f"Erreur lors de la génération : {e}")

if __name__ == "__main__":
    main()
