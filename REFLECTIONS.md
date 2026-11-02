# Réflexions — TD2 Smart Mobility Le Mans

Ce document contient des **propositions de réponse à relire et personnaliser**. Les 11 questions de la « Reflection checklist » sont reprises dans leur formulation originale et dans leur ordre exact. Les hypothèses personnelles non consignées avant le développement ne sont pas reconstituées comme des faits. Les vérifications de terrain et les conclusions historiques non réalisées sont signalées explicitement.

Les résultats de référence sont ceux obtenus pendant le TD : **66 lignes GTFS**, 1 799 arrêts dans le flux, **798 arrêts retenus**, 9 715 trajets et 214 507 passages horaires dans le GTFS complet ; **26 lignes observées en temps réel**, **22,9 secondes de retard moyen calculé** et aucune alerte active lors du test communiqué ; **20 communes** et **43 401 passages programmés** dans l’analyse statique. Ces valeurs décrivent nos traitements et notre snapshot de test, pas des constantes du réseau ni nécessairement son état actuel.

## 1. Which sub-questions of the central business question did you expect to be easy vs. hard, before building anything?


Avant de commencer ce TD, je pensais que la récupération des données de transport et la création d'un tableau de bord seraient relativement simples, puisque nous disposions de sources de données et d'outils de programmation.

En revanche, je pensais que déterminer quelles communes avaient réellement besoin d'une amélioration des transports serait plus difficile. En effet, il ne suffit pas de connaître le nombre de bus ou les horaires pour identifier les besoins des habitants.

Il faut également prendre en compte la population, les déplacements quotidiens et la qualité du service. Je pensais donc que la difficulté principale serait davantage liée à l'interprétation des données et à la prise de décision qu'à leur visualisation.

## 2. Your prediction for why the static GTFS feed doesn't also refresh every 15 minutes.

**À personnaliser : prédiction initiale, et non réponse écrite avant réalisation attestée.**

Proposition : les horaires programmés changent beaucoup moins souvent que les retards. Télécharger et recalculer le même référentiel toutes les 15 minutes produirait généralement le même résultat, tout en répétant les transferts et les calculs. Un traitement mensuel semble donc plus proportionné, avec un déclenchement manuel en cas de changement connu.

La cadence mensuelle est un compromis du TD : elle ne garantit pas à elle seule que le référentiel suit immédiatement chaque modification des horaires.

## 3. Your prediction for what breaks when two files' "same" ID column gets auto-typed independently and then joined.

**Réponse technique ; formulation de la prédiction à personnaliser.**

Proposition de prédiction : si un fichier interprète `stop_id` comme un entier et un autre comme une chaîne de caractères, la jointure peut échouer ou ne pas retrouver les correspondances attendues. Une conversion numérique peut également faire perdre les zéros initiaux d’un identifiant. Un identifiant comme `FLEX-381` montre qu’il ne s’agit pas d’une quantité sur laquelle calculer.

Le script du professeur lit donc tous les fichiers GTFS avec `dtype=str` : les clés `stop_id`, `trip_id`, `route_id` et `service_id` restent compatibles entre fichiers. Seules les colonnes nécessaires aux calculs, comme les coordonnées, sont ensuite converties. Cette précaution évite un problème de typage ; elle ne garantit pas à elle seule que chaque clé possède une correspondance valide.

## 4. Order-of-magnitude row-count comparison: per-route vs. per-stop logging over a semester, and what question the per-route choice makes harder.

**Estimation théorique, pas volume effectivement collecté.**

Sur 12 semaines, avec une collecte toutes les 15 minutes, on prévoit :

`12 × 7 × 24 × 4 = 8 064 snapshots`.

Avec environ 5 000 mises à jour d’arrêt par snapshot, conserver chaque mise à jour représenterait environ **40 320 000 lignes**, soit plusieurs dizaines de millions. Il s’agit de mises à jour, pas de 5 000 arrêts distincts.

À raison de 27 à 40 lignes de transport par snapshot, les agrégats représentent **217 728 à 322 560 lignes**. Avec les 26 lignes de notre test, supposées constantes uniquement pour l’estimation, ce serait **209 664 lignes**. L’ordre de grandeur passe ainsi de dizaines de millions à quelques centaines de milliers de lignes. Les volumes réels dépendront du service, de la disponibilité du flux et des collectes exécutées.

Le stockage par ligne économise de la place, mais empêche de répondre précisément à « quels arrêts subissent régulièrement des retards à une heure donnée ? ». Une moyenne de ligne peut masquer des retards concentrés sur quelques arrêts et la compensation entre avances et retards. Notre historique par ligne ne permet pas de reconstruire ensuite les observations par arrêt perdues.

## 5. Your proposed alternative to the delay chart's early-good/late-bad color encoding, and what decision it would change.

**Proposition de conception ; non implémentée dans le graphique des retards.**

Je proposerais de conserver les barres signées, pour distinguer avance et retard, avec une zone verte proche de zéro et des couleurs distinctes pour les avances et retards importants. Par exemple, une tolérance illustrative de −60 à +60 secondes pourrait être verte, une avance au-delà de cette zone orange et un retard au-delà rouge. Ces seuils seraient à discuter avec les utilisateurs, pas à présenter comme une norme officielle.

Le graphique actuel normalise les couleurs entre le retard minimum et le maximum du snapshot : le plus faible est vert et le plus élevé rouge, même si toutes les lignes sont en retard. Des seuils fixes rendraient la signification des couleurs plus stable entre snapshots.

La décision changerait : une ligne très en avance pourrait aussi devenir prioritaire pour une action de régulation, car un véhicule parti avant l’heure peut faire manquer le passage à un usager. Une avance ne serait plus automatiquement valorisée. Cependant, recolorer une moyenne ne révèle pas toutes les dispersions : une moyenne proche de zéro peut encore masquer des avances et retards importants.

## 6. The real reasoning for both halves of the static-vs-real-time scheduling mismatch.

Les deux pipelines ne représentent pas la même temporalité. Le statique décrit des horaires prévus, valables sur une période ; le temps réel décrit une situation qui peut évoluer en quelques minutes.

Recalculer le statique toutes les 15 minutes serait généralement redondant : téléchargement du ZIP, lectures, jointures et calculs géographiques seraient répétés sans changement utile. À l’inverse, un snapshot temps réel mensuel manquerait presque toutes les perturbations et ne permettrait ni un état récent du réseau ni une analyse des variations horaires.

Le TD prévoit donc un référentiel mensuel, le premier du mois à 04:00 UTC, et une collecte temps réel toutes les 15 minutes, avec déclenchement manuel possible pour chacun. L’analyse offre/population suit désormais le traitement statique, car elle dépend de ces horaires et du référentiel de population, pas des retards instantanés.

Un dashboard n’est pas automatiquement frais parce qu’un planning est configuré : il faut vérifier l’avancement de l’horodatage et la croissance des historiques. La preuve de fonctionnement autonome sur GitHub reste à réaliser après publication et activation personnelles des workflows.

## 7. What you actually found when you sanity-checked one delayed route against reality.

**À compléter obligatoirement : vérification réelle non réalisée dans les éléments disponibles.**

Le test communiqué a observé **26 lignes**, un indicateur réseau de **22,9 secondes** et **0 alerte active**. Ces valeurs démontrent un résultat de collecte ; elles ne constituent pas une comparaison avec les départs SETRAM, une observation personnelle ou une preuve d’absence de perturbation. Le retard moyen réseau n’identifie pas non plus une ligne particulièrement retardée.

Le collecteur calcule d’abord une moyenne des retards des mises à jour par ligne, puis une **moyenne non pondérée des moyennes de ligne**. Chaque ligne a le même poids dans l’indicateur réseau, quel que soit son nombre de mises à jour ou de voyageurs. Le code attribue aussi zéro lorsqu’une ligne n’a aucune valeur de retard retenue : zéro ne prouve donc pas toujours une ponctualité mesurée. Les messages temps réel ne sont pas un relevé exhaustif de tous les passages réellement effectués.

À renseigner lors d’une observation contemporaine :

- Date, heure, fuseau et horodatage du snapshot : **[à compléter]**.
- Ligne choisie, direction, arrêt ou trajet comparé : **[à compléter]**.
- Retard moyen, retard maximal et volume d’observations de cette ligne : **[à compléter]**.
- Source consultée ou observation effectuée, avec heure de consultation : **[à compléter]**.
- Résultat de la comparaison et éventuel écart : **[à compléter]**.
- Interprétation étayée, en distinguant fait et hypothèse : **[à compléter]**.

Comparer un départ individuel à une moyenne de ligne ne doit pas conduire à attendre leur égalité : les périmètres diffèrent. Aucun événement local, chantier ou incident n’est affirmé ici faute de vérification.

## 8. A concrete case where population would mislead as a demand proxy.

**Exemple explicatif hypothétique, pas observation locale vérifiée.**

Une commune peu peuplée accueillant une importante zone d’emplois ou un campus peut recevoir chaque matin de nombreux salariés ou étudiants qui résident ailleurs. Sa population résidente sous-estimerait alors la demande de transport pendant ces horaires. Inversement, une commune résidentielle peut connaître une demande dirigée surtout vers d’autres communes.

Cet exemple décrit un mécanisme réaliste, mais ne démontre pas qu’une commune particulière de notre classement présente ce profil. La population ne renseigne ni les déplacements entrants, ni les destinations, ni les horaires, ni la part des habitants qui utilisent effectivement les transports publics. **Si je souhaite citer un exemple local nommé, je dois le documenter personnellement.**

## 9. Your chosen supply-vs-population metric, and a real commune where it misleads.

**Calcul et classement vérifiés ; interprétation territoriale à compléter.**

La métrique est le **nombre de passages programmés aux arrêts pour le jour représentatif, rapporté à 1 000 habitants de la commune** :

`ratio = somme des daily_trip_count attribués à la commune / population × 1 000`.

Le script regroupe les passages avec pandas, puis réalise une jointure gauche depuis les 20 communes. Une commune sans arrêt attribué serait conservée avec zéro passage ; dans notre résultat, chacune possède au moins un arrêt attribué. Le total reste de **43 401 passages pour 798 arrêts**.

| Rang | Commune (nom du référentiel) | Arrêts attribués | Passages programmés | Population | Passages pour 1 000 habitants |
|---:|---|---:|---:|---:|---:|
| 1 | La-Chapelle-Saint-Aubin | 53 | 2 343 | 2 319 | 1 010,35 |
| 2 | Coulaines | 105 | 6 267 | 8 226 | 761,85 |
| 3 | Rouillon | 41 | 1 906 | 2 666 | 714,93 |
| 4 | Allonnes | 69 | 4 017 | 10 846 | 370,37 |
| 5 | Arnage | 34 | 1 638 | 5 548 | 295,24 |
| 6 | Yvre-l-Eveque | 22 | 750 | 4 269 | 175,69 |
| 7 | Saint-Saturnin | 21 | 490 | 2 864 | 171,09 |
| 8 | La-Milesse | 15 | 425 | 2 650 | 160,38 |
| 9 | Sarge-les-le-Mans | 15 | 630 | 3 941 | 159,86 |
| 10 | Le Mans | 329 | 22 900 | 148 876 | 153,82 |
| 11 | Ruaudin | 22 | 536 | 3 542 | 151,33 |
| 12 | Champagne | 19 | 425 | 3 728 | 114,00 |
| 13 | Mulsanne | 18 | 525 | 5 352 | 98,09 |
| 14 | Aigne | 6 | 138 | 1 724 | 80,05 |
| 15 | Pruille-le-Chetif | 8 | 88 | 1 357 | 64,85 |
| 16 | Fay | 3 | 44 | 770 | 57,14 |
| 17 | Trange | 6 | 87 | 1 678 | 51,85 |
| 18 | Chaufour-Notre-Dame | 3 | 58 | 1 187 | 48,86 |
| 19 | Saint-Georges-du-Bois | 7 | 96 | 2 308 | 41,59 |
| 20 | Fatines | 2 | 38 | 937 | 40,55 |

Source : `data/gtfs_static/supply_by_commune.csv`, issu de `stops_frequency.csv` et `data/reference/communes.csv`. Les valeurs du tableau sont arrondies à deux décimales ; le classement utilise les valeurs non arrondies.

Exemple de calcul réel : La-Chapelle-Saint-Aubin obtient `2 343 / 2 319 × 1 000 ≈ 1 010,35`. Le Mans concentre **22 900 passages**, environ **52,8 %** du total, mais se classe dixième. Interpréter ce rang comme une dixième place d’accessibilité serait trompeur : il décrit un ratio par résident, pas la proximité des arrêts ou les possibilités de déplacement.

**Cas local à approfondir :** La-Chapelle-Saint-Aubin arrive première avec 53 arrêts attribués. C’est un résultat à examiner, pas la preuve d’une anomalie. Je dois identifier un ou plusieurs arrêts contributeurs dans nos données, vérifier leur localisation et leur utilité pour les habitants, puis expliquer avec un fait territorial pourquoi le ratio serait trompeur. Je ne peux pas affirmer sans preuve qu’il existe un dépôt, un pôle commercial ou une mauvaise attribution expliquant ce résultat. La seule comparaison numérique avec Le Mans ne satisfait pas encore toute l’exigence du manuel d’un cas expliqué par une connaissance réelle de la commune.

Limites et choix de traitement :

- **Population :** approximation de la demande, sans fréquentation réelle ni flux entrants ou sortants.
- **Géographie :** rattachement au centre communal le plus proche par Haversine, pas appartenance vérifiée à un périmètre administratif. Des arrêts d’une commune peuvent donc être attribués à une autre.
- **Jour représentatif :** le script retient un seul `service_id` actif le mardi ayant la plus longue période de validité. Cela évite de choisir une période courte, mais ne reconstitue pas nécessairement tous les services simultanés d’une date précise et ne traite pas les exceptions de calendrier. Ce n’est ni une moyenne annuelle ni l’offre du week-end.
- **Périmètre :** les 798 arrêts sont ceux retenus après filtrage et jointure ; les autres arrêts du GTFS ne sont pas pour autant déclarés inutilisés en toute circonstance.
- **Unité :** un passage est une visite programmée à un arrêt ; le même véhicule peut en produire plusieurs au cours d’un trajet. Ce ne sont ni des voyageurs, ni des véhicules distincts, ni une capacité de transport.
- **Accessibilité :** le ratio ignore les distances à pied, correspondances, amplitudes, fréquences selon l’heure, accessibilité physique et qualité réelle du service.

## 10. Your proposed approach to aggregating stop-level delay events without blowing up the history file.

**Proposition uniquement : ce traitement n’a pas été développé.**

Je conserverais un agrégat par arrêt et par jour, découpé en trois périodes utiles à la décision (matin, milieu de journée, soir, avec bornes explicites en heure locale). Pour chaque clé, je stockerais le nombre de mises à jour, la somme des retards, le nombre de retards au-delà d’un seuil annoncé, le nombre d’avances importantes et le retard maximal. La moyenne serait calculable avec `somme / nombre`, et les proportions avec leurs compteurs, sans garder chaque événement.

À chaque snapshot, le traitement mettrait à jour les agrégats de la journée au lieu d’ajouter tous les événements bruts. Les sorties seraient réparties en fichiers mensuels. À titre d’ordre de grandeur, 798 arrêts × 84 jours × 3 périodes donnent **201 096 lignes au maximum**, si tous ces arrêts étaient observés chaque jour dans chaque période. Les 798 arrêts statiques servent ici d’hypothèse de dimensionnement, pas de garantie sur le périmètre du temps réel.

Il faudrait détecter les snapshots déjà traités grâce à leur horodatage, éviter de compter les mêmes mises à jour répétées comme de nouveaux passages et définir l’unité d’observation (mise à jour ou événement unique de trajet-arrêt). Sans cette précaution, une perturbation persistante serait surreprésentée. Les périodes devraient traiter explicitement le fuseau et les changements d’heure.

Cette approche permettrait de rechercher des arrêts fréquemment perturbés par période. Elle sacrifierait le détail exact des snapshots et ne permettrait pas de retrouver des quantiles exacts sans structure de stockage supplémentaire.

## 11. How your Reflection 1 predictions compared to what you actually found.

**Bilan technique fondé sur nos résultats ; comparaison personnelle et conclusions historiques à compléter.**

Aujourd’hui, le projet permet de consulter un état instantané, de décrire l’offre programmée et de comparer les 20 communes avec une métrique explicite. Le traitement statique porte sur 66 lignes GTFS et retient 798 arrêts ; notre snapshot de test ne rapporte que 26 lignes. Ces nombres décrivent deux périmètres différents : je ne peux pas conclure que les 40 autres lignes sont nécessairement défaillantes. L’heure, le service et la couverture du flux peuvent intervenir, mais ces causes ne sont pas établies ici.

Le retard moyen calculé de 22,9 secondes résume un snapshot selon la formule du collecteur. Il ne prouve ni une ponctualité générale ni une régularité durable. L’analyse de 43 401 passages permet d’identifier des contrastes d’offre rapportée aux habitants, mais le choix du proxy, du service représentatif, du rattachement géographique et des couleurs nécessite des jugements explicites.

Les questions « quelles lignes sont souvent retardées ? », « à quels moments les difficultés reviennent-elles ? » et « peut-on anticiper les perturbations ? » exigent plusieurs semaines de collecte, une couverture suffisante et une analyse tenant compte des manques. Accumuler des semaines ne garantit pas à lui seul une prédiction fiable. La récurrence par arrêt exige en plus une collecte à cette granularité : l’historique actuel par ligne ne suffira pas, même après plusieurs semaines.

La question d’investissement reste donc partiellement ouverte : nous disposons d’indicateurs d’aide au diagnostic, pas d’une preuve complète des besoins ni d’une recommandation budgétaire validée.

**À personnaliser :** « Au départ, je pensais que **[hypothèse réellement formulée]**. Les résultats **[résultat observé]** l’ont **[confirmée / nuancée / contredite]**, parce que **[raison]**. » La vérification d’une ligne retardée et le cas communal trompeur doivent encore être renseignés avant une conclusion définitive.
