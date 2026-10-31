# TERRA-META-012 — Hackathon Experience (première tranche)

Application statique autonome. Aucune écriture/modification des sources FSDC. Aucun appel Meta/ElevenLabs.
Ne pas présenter cette tranche comme le moteur autonome complet.

## Démarrage Windows

Depuis la racine du dépôt :
```powershell
python -m http.server 8765 --directory ".\apps\terra-meta-012"
```
Ouvrir http://localhost:8765 (ne pas confondre avec l'application historique).

## Données
- Overview → charger `Sessions-HACK016/Boke-011A-Council-Consolidation.json`.
- Council Debate → lire les 19 narrations et les alertes sans masquer les cinq tours signalés.
- Ask Terra → planification heuristique visuelle; ce formulaire n'exécute PAS encore 011B ni aucun modèle. Aucune réponse scientifique n'est générée.
- Geo Intelligence → importer GeoJSON FSDC local; la carte OpenStreetMap dépend d'une connexion réseau. Aucune couche inventée, aucune animation temporelle encore.
- Scientific Brief → impression du navigateur, destination « Enregistrer au format PDF »; export provisoire non certifié.
- Voice Registry → charger un registre JSON avec vos vrais ID de voix (modèle dans `voice-registry.template.json`). Il n'y a ni clé API stockée, ni génération ElevenLabs, ni synchronisation automatique.
- Audio → charger des MP3 existants et validés par tour. Le lecteur par tour fonctionne; le montage du débat intégral et la synchronisation restent à développer.

## Scientific safeguards
Ne pas confondre empreintes SHA-256 et validation scientifique.
Les alertes T02, T06, T07, T11 et T13 doivent rester visibles. Audio final non autorisé avant une revue éditoriale, scientifique et de continuité globale.
Le chargement par sélecteur de fichiers se fait dans le navigateur; GeoJSON ne quitte pas le navigateur mais les tuiles OSM nécessitent Internet.

## Étapes suivantes
012B: importer les voix historiques ElevenLabs et créer un rendu MP3 traçable après approbation humaine.
012C: carte animée en fonction de séries datées réelles, pas animation fictive.
012D: connecter la planification 011B et l'API Meta avec backend sûr, plafonds persistants et approbation; ne jamais exposer les clés dans le navigateur.
