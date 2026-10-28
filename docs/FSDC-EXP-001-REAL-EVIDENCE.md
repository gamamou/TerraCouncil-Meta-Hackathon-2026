# FSDC-EXP-001 — Premier enrichissement réel et comparaison avant/après

## Inventaire effectivement vérifié le 28 octobre 2026

**Base géospatiale existante** : ESA WorldCover 2021 et WorldPop 2026, statut SCREENED_NOT_FIELD_VALIDATED, emprise rectangulaire de Boké. Aucun PM10 ou AERMOD mesure de concentration présent.

**Nouvelle source primaire identifiée (contexte régional, PAS AOI)** :
- Déclaration publique historique GAC datée du 11 mai 2023 : contribution annoncée de **18,5 milliards GNF** au FODEL de Boké pour 2022.
- Source vérifiée : https://www.gacguinee.com/fr/media-releases/gac-supports-boke
- Statut : SOURCE_REPORTED_NOT_INDEPENDENTLY_AUDITED. La publication est archivée et indique que GAC a cessé ses activités en Guinée en août 2025. Ne pas extrapoler en 2026 ou en déduire que des projets précis ont été financés, ni lier à l'AOI WorldCover sans croisement géospatial indépendant.

**Nouvelle source scientifique publiée (contexte régional, PAS mesure PM10 de l’AOI)** :
- Kolie et al., 2024, *Environmental Management*, doi: 10.1007/s00267-024-02066-1, PMID 39527266, https://pubmed.ncbi.nlm.nih.gov/39527266/.
- Le résumé porte sur des zones minières de Boké et de Kérouané ; collecte déclarée entre octobre 2022 et janvier 2023. Il rapporte notamment une préoccupation sur des niveaux élevés de PM10 lors d’opérations minières.
- **Le résumé ne donne pas de concentration PM10 chiffrée localisable dans le rectangle TerraCouncil.** L’étude doit donc rester dans une couche de preuve scientifique documentaire régionale, avec statut PEER_REVIEWED_ABSTRACT_NOT_AOI_GEOREFERENCED ; lire ses tableaux et coordonnées d’échantillonnage avant une quantification, sans transférer à Boké des mesures de Kérouané.

**Nouvelle source secondaire retrouvée dans Google Drive (NON ADMISSIBLE tant que non confirmée)** :
- Fichier utilisateur "Guinea Research", tableau de bailleurs : entrée 2022 CECIDE / Global Greengrants Fund, montant listé **10 811 USD**, description d'un projet de suivi FODEL et d'engagements environnementaux dans la région de Boké.
- Source compilée : https://docs.google.com/spreadsheets/d/1rGQOe5D24kwTd-axXs4dlxkKWDukve-5DIyjA1yaB70/edit
- La source primaire de cette attribution individuelle n'a pas été confirmée ; son contenu ne devient pas observation FSDC admise. Les coordonnées personnelles du tableur ne sont pas copiées au registre.

**Source nationale non injectée** :
- World Bank ISR du Guinea Commercial Agriculture Development Project P164184, 14 Dec 2020, présent dans Google Drive. Les chiffres 800 km de routes et 145 000 bénéficiaires sont des **objectifs nationaux du projet, pas résultats observés à Boké** ; exclus de la couche géospatiale.

## Changement vérifiable de l'application

- data/fsdc_contextual_candidates_boke_2026.json : registry avec 3 entrées documentaires/scientifiques explicitement distinguées par statut et périmètre ; provenance et limitations.
- src/fsdc_evidence_expansion.py : compare plan baseline et document régional quand la question vise Boké + domaine minier / gouvernance / finance. Les registres documentaires ne sont pas injectés comme observations AOI et ne remplacent pas une validation scientifique.
- GET /api/fsdc-evidence-comparison?question=... : diagnostic authentifié sans appel Meta.
- Edge : **FSDC — Comparer de nouvelles preuves** affiche les sources, les restrictions et le nombre de nouveaux éléments.
- tests/test_fsdc_exp001.py : sources réelles, absence de nouveaux PM10, non-inférence spatiale et zéro appel externe.

## Démonstration reproductible

1. Question A : « Que permettent de documenter les données d'occupation du sol à Boké ? »
   - Baseline : WorldCover.
   - Aucun fait FODEL nécessaire à cette question, donc aucune fausse contextualisation financière.
2. Question B : « Quels financements FODEL et quelle occupation du sol à Boké ? »
   - Baseline scientifique AOI : WorldCover uniquement.
   - Après découverte : déclaration historique régionale GAC 2022 et résumé scientifique Kolie et al. 2024 ; entrée compilée CECIDE affichée comme non confirmée.
   - **Nouvelles mesures scientifiques AOI : 0. Nouvelles sources régionales documentées : 2. Nouveau débat Spark/Wonder : NON exécuté.** Les conclusions précédentes restent historiquement inchangées.
3. Question C : « Quelles concentrations PM10 à Boké ? »
   - Toujours ABSTAIN pour une **concentration numérique PM10 sur l’AOI** ; mais une étude scientifique régionale de 2024 apparaît dans le contexte, sans valeur locale publiée dans son résumé.

## PowerShell vérification locale

Après téléchargement/extraction de la dernière version GitHub :
```powershell
$ErrorActionPreference="Stop"
$env:PYTHONUTF8="1"
$server=Get-ChildItem . -Recurse -File -Filter local_council_server.py | Select-Object -First 1
if (-not $server) { throw "Serveur manquant" }
$root=$server.Directory.Parent.FullName
python -X utf8 -m unittest discover -s (Join-Path $root "tests") -p test_fsdc_exp001.py -v
if ($LASTEXITCODE -ne 0) { throw "FSDC-EXP-001 tests failed" }
$evidence=Join-Path $HOME "Documents\TerraCouncil-Scientific-Inputs\boke_screened_evidence.json"
python -X utf8 "$($server.FullName)" --evidence "$evidence" --port 8765
```
Dans Edge, posez la question B et cliquez sur **FSDC — Comparer de nouvelles preuves**.

## Étape suivante

Pour produire un **nouveau débat scientifiquement enrichi**, il faudra ajouter des preuves locales dont la géométrie recouvre réellement l'AOI et dont les observations respectent le contrat FSDC, ou étendre le moteur avec une voie de preuve documentaire sous contrôle explicite (sans usurper l'observation géospatiale). Puis exécuter une délibération avec consentement, comparer aux anciens résultats et mesurer les changements. Le présent jalon ne prétend PAS avoir atteint ce résultat.

Les tests sont publiés mais pas encore exécutés dans VS Code sur l'ordinateur utilisateur.

## Mise à jour : intégration documentaire dans le plan Spark / Wonder

- `attach_regional_context` attache uniquement les sources publiées pertinentes à la question ; la compilation CECIDE reste **exclue** du contexte envoyé à Meta.
- La nouvelle empreinte `plan_sha256` associe le contenu documentaire sélectionné à la question avant toute autorisation de coût et de transmission.
- Les modèles reçoivent `regional_context` dans une section séparée et sont explicitement instruits de ne **jamais** l'insérer dans `observations`, réservé aux constats géospatiaux exacts FSDC.
- Le PDF d'une **nouvelle** session indique les sources documentaires régionales et leur statut. Un ancien rapport n'est pas modifié.
- Aucun appel Meta ni débat enrichi n'a été exécuté par le développement ; la comparaison sans modèle ne prouve donc aucun changement effectif des conclusions. Pour le vérifier, comparer les réponses de la première session à une nouvelle délibération explicitement autorisée.

Questions utiles :
1. `Que permettent de documenter les données d'occupation du sol à Boké ?` : WorldCover seul.
2. `Quels impacts miniers sur l'occupation du sol à Boké ?` : WorldCover + contexte historique régional GAC et étude académique Kolie et al. Les agents doivent refuser toute causalité non démontrée pour l'AOI.
3. `Quelles concentrations PM10 sont disponibles pour Boké ?` : source académique régionale identifiée, mais aucune valeur PM10 chiffrée admissible pour l'AOI ; abstention numérique maintenue.
