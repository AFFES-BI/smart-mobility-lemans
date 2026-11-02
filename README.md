Smart Mobility Le Mans — TD2 Business Intelligence
Projet étudiant réalisé dans le cadre du TD2 de Business Intelligence à l’ENSIM. Le manuel du professeur sert de référence pour les traitements et les livrables.
Objectif
Contribuer à la question : avec des ressources limitées, où et quand Le Mans Métropole devrait-elle intervenir pour améliorer son réseau de transports publics ?

Le projet combine une référence d’offre programmée, des snapshots de perturbations et une comparaison de l’offre avec la population des 20 communes. Ces indicateurs aident au diagnostic ; ils ne constituent pas à eux seuls une recommandation d’investissement.
Sources de données
- SETRAM GTFS statique : lignes, arrêts, trajets et horaires programmés, téléchargés sous forme de ZIP depuis la ressource officielle data.gouv.fr.
- SETRAM GTFS-RT TripUpdate : mises à jour de trajets et retards, au format protobuf, via le proxy transport.data.gouv.fr.
- SETRAM GTFS-RT Alert : messages de perturbation au format protobuf, via le flux d’alertes.
- Référence des communes : coordonnées et populations recopiées sans modification depuis le manuel dans data/reference/communes.csv. Le manuel attribue les populations à l’INSEE et les coordonnées des centres communaux à l’API Adresse. Le fichier local ne précise pas le millésime des populations.
Les flux SETRAM utilisés ne nécessitent pas de clé. Les données téléchargées peuvent évoluer ; les résultats ci-dessous ne sont pas des valeurs permanentes du réseau.
Organisation
smart-mobility-lemans/
├── .github/workflows/
│   ├── build_static_reference.yml
│   ├── collect_snapshot.yml
│   └── deploy_pages.yml
├── data/
│   ├── reference/communes.csv
│   ├── gtfs_static/
│   │   ├── stops_frequency.csv
│   │   ├── routes.csv
│   │   └── supply_by_commune.csv
│   └── history/
│       ├── route_delays_YYYY-MM.csv
│       └── alerts_log.csv              # créé seulement si des alertes sont présentes
├── scripts/
│   ├── build_static_reference.py
│   ├── analyze_supply_demand.py
│   └── collect_snapshot.py
├── docs/
│   ├── index.html
│   └── data/
│       ├── current_state.json
│       └── supply_by_commune.json
├── .gitignore
├── README.md
└── REFLECTIONS.md

Les CSV de data/gtfs_static/ sont des sorties générées. Les historiques conservent les observations successives ; les JSON de docs/data/ alimentent le dashboard. L’environnement local .venv/ et les caches sont exclus par .gitignore. Les données du TD restent publiables : elles ne sont pas ignorées.
Installation locale — Python 3.12
Installer Python 3.12, puis ouvrir le dossier du projet dans VS Code. Les commandes suivantes sont à lancer à la racine du projet, dans un terminal PowerShell sous Windows :
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install requests pandas gtfs-realtime-bindings
Si .venv existe déjà, vérifier qu’il utilise Python 3.12 avant de le réutiliser :
.\.venv\Scripts\python.exe --version
Dans VS Code, sélectionner .venv\Scripts\python.exe comme interpréteur Python. L’activation de l’environnement dans PowerShell n’est pas nécessaire avec les commandes explicites ci-dessus. Les versions des dépendances ne sont actuellement pas figées.
Exécution
Une connexion Internet est nécessaire pour télécharger les flux SETRAM. Exécuter dans cet ordre :
.\.venv\Scripts\python.exe scripts/build_static_reference.py
.\.venv\Scripts\python.exe scripts/analyze_supply_demand.py
.\.venv\Scripts\python.exe scripts/collect_snapshot.py
1. Le premier script produit stops_frequency.csv et routes.csv.
2. Le deuxième utilise les fréquences et le référentiel communal pour produire le classement CSV et JSON.
3. Le collecteur ajoute un snapshot aux historiques et remplace current_state.json.
Relancer le collecteur ajoute des observations ; il ne remet pas l’historique à zéro. Le script ne déduplique pas les snapshots : deux collectes recevant le même horodatage de flux peuvent ajouter des lignes répétées.
Automatisations GitHub Actions préparées
Pipeline	Déclenchements prévus	Traitements et sorties
Référence statique	Manuel et le 1er de chaque mois à 04:00 UTC	Exécute build_static_reference.py, puis analyze_supply_demand.py ; enregistre les trois CSV statiques et supply_by_commune.json
Snapshot temps réel	Manuel et toutes les 15 minutes, 24 h/24	Exécute collect_snapshot.py ; enregistre les historiques et current_state.json


Les workflows utilisent Python 3.12 et installent leurs dépendances. Les deux workflows de données partagent une coordination pour limiter les écritures concurrentes sur main, puis enregistrent les données calculées dans le dépôt. Le troisième workflow, deploy_pages.yml, prévoit le déploiement de docs/ après une collecte réussie ou à la demande. Leur fonctionnement effectif sur GitHub reste à vérifier : permissions d’écriture, exécutions réussies, publication Pages et progression de l’historique. Les déploiements automatiques n’ont pas encore été validés sur GitHub.
Indicateurs et choix de traitement
Référence d’offre
Les identifiants GTFS sont lus avec dtype=str pour éviter les incompatibilités de types lors des jointures. Le traitement sélectionne le service_id actif le mardi ayant la plus longue fenêtre de validité, puis compte ses passages par arrêt (daily_trip_count). Chaque arrêt est rattaché au centre communal le plus proche par la distance de Haversine.

Ce choix représente un service du mardi, pas une moyenne annuelle ni nécessairement tous les services actifs à une date précise. Les exceptions du calendrier ne sont pas traitées. Le rattachement géographique ne suit pas les limites administratives.
État temps réel
- Retard moyen par ligne : moyenne des retards des mises à jour retenues, en secondes ; les informations d’arrivée sont prioritaires sur celles de départ.
- Retard maximal : maximum des retards retenus par ligne.
- Retard moyen réseau : moyenne non pondérée des moyennes de ligne ; chaque ligne a le même poids.
- Trajets observés et arrêts sautés : compteurs issus des messages du snapshot, pas fréquentation de voyageurs ni décompte exhaustif des incidents.
- Lignes observées et alertes : couverture et messages présents au moment de la collecte. Zéro alerte ne prouve pas l’absence de toute perturbation.
Le collecteur utilise zéro lorsqu’une ligne ne possède aucun retard retenu : cette valeur ne prouve pas toujours une ponctualité mesurée. Les mises à jour peuvent être des prévisions ; elles ne constituent pas un relevé exhaustif de passages effectués. L’horodatage affiché provient du flux TripUpdate, en UTC.

Les couleurs du graphique des retards suivent le manuel : normalisation entre le minimum et le maximum du snapshot, du vert pour les retards les plus faibles au rouge pour les plus élevés. Il s’agit d’une comparaison relative ; une avance importante peut apparaître favorable alors qu’elle pénalise les usagers.
Offre rapportée à la population
Passages pour 1 000 habitants = somme des daily_trip_count attribués à la commune
                              / population × 1 000

Le classement conserve les 20 communes grâce à une jointure gauche depuis le référentiel ; une commune sans arrêt attribué aurait zéro passage. Un passage est une visite programmée à un arrêt : un même trajet peut en produire plusieurs.

La population est un indicateur indirect de demande, pas une fréquentation réelle. Le ratio ne mesure pas l’accessibilité réelle. Il ignore notamment les emplois et visiteurs entrants, les destinations, la distance à pied, les correspondances, la capacité des véhicules et la répartition des horaires. Les besoins et les perturbations récurrentes ne peuvent pas être déduits d’un classement statique ou d’un snapshot unique.
Résultats obtenus jusqu’à présent
Élément	Résultat vérifié
Lignes du GTFS statique	66
Arrêts du GTFS complet	1 799
Trajets du GTFS complet	9 715
Entrées stop_times du GTFS complet	214 507
Arrêts retenus par le traitement statique	798
Communes du classement	20
Passages programmés retenus	43 401
Lignes observées au premier snapshot	26
Retard moyen au premier snapshot	22,9 secondes
Lignes observées au second snapshot	27
Retard moyen au second snapshot	15,4 secondes
Alertes actives aux deux tests	0


Le premier snapshot contrôlé est horodaté 2026-10-28T16:40:25Z. Une deuxième exécution locale du collecteur a ensuite réussi (27 lignes, 15,4 secondes, 0 alerte). Le nombre de lignes historiques et leurs horodatages distincts restent à contrôler directement dans le CSV ; la mise à jour automatisée sur GitHub reste à démontrer.

Extrait du classement réel, ratios arrondis à deux décimales :
Rang	Commune	Passages programmés	Population	Passages pour 1 000 habitants
1	La-Chapelle-Saint-Aubin	2 343	2 319	1 010,35
2	Coulaines	6 267	8 226	761,85
3	Rouillon	1 906	2 666	714,93
10	Le Mans	22 900	148 876	153,82
20	Fatines	38	937	40,55


Le classement complet est disponible dans data/gtfs_static/supply_by_commune.csv et le dashboard. Ces résultats ne prouvent pas à eux seuls une sous-desserte ou une sur-desserte.
Consulter le dashboard localement
Depuis la racine du projet, démarrer un serveur limité à la machine locale :
.\.venv\Scripts\python.exe -m http.server 8000 --bind 127.0.0.1 --directory docs
Ouvrir http://127.0.0.1:8000/ dans le navigateur. Arrêter le serveur avec Ctrl+C. Utiliser ce serveur HTTP plutôt que l’ouverture directe du fichier HTML pour permettre les chargements JSON.

Le dashboard charge data/current_state.json et data/supply_by_commune.json relativement au dossier docs. Chart.js est chargé depuis un CDN et nécessite une connexion Internet. Le tableau communal reste disponible si son graphique ne peut pas être construit.

La page affiche les KPI, les alertes, les retards par ligne, l’horodatage et le classement offre/population. Elle charge les données à l’ouverture : après une nouvelle collecte, recharger la page pour les consulter. Le fonctionnement local a été vérifié visuellement pendant le TD.
Réflexions et livrables
REFLECTIONS.md reprend les 11 questions finales du manuel. Les réponses ont été retravaillées ; la comparaison indépendante d’un retard de ligne avec une observation SETRAM au même moment reste non réalisée et doit être signalée comme telle. Les conclusions sur les récurrences nécessitent plusieurs semaines de collecte ; les récurrences par arrêt exigeraient en plus un historique à cette granularité.

Le rendu final prévu comprend l’URL du dépôt, l’URL du site Pages et REFLECTIONS.md, ainsi que les preuves d’exécution et d’actualisation demandées dans le manuel.
Accès au projet
- Dépôt GitHub : https://github.com/AFFES-BI/smart-mobility-lemans
- Organisation GitHub regroupant les TD : https://github.com/AFFES-BI
- Dashboard GitHub Pages : publication à activer et à vérifier dans les paramètres du dépôt (Settings → Pages → Source : GitHub Actions).
Le dépôt a été créé, mais le transfert des fichiers et le déploiement du site ne sont pas encore confirmés. Ce README ne prétend pas que les workflows ont déjà réussi en ligne.
