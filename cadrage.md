# Fiche de Cadrage — Projet Machine Learning
# Détecteur de Chocs Économiques — World Bank API


## 1. Domaine métier

**Secteur :** Économie macroéconomique internationale  
**Contexte :** Les institutions internationales telles que le FMI et la Banque Mondiale ont besoin de systèmes capables de détecter les signes avant-coureurs de crises économiques dans les pays membres. Une détection précoce permet une intervention rapide : financement d'urgence, ajustement des politiques fiscales, mobilisation de l'aide internationale.

**Utilisateur cible :** Économiste analyste dans une institution internationale souhaitant identifier les pays à risque de crise économique soudaine avant que la situation ne devienne incontrôlable.

---

## 2. Sujet du projet

**Titre :** Détection de chocs économiques soudains par pays et par année

**Question métier :**
> "Étant donné les indicateurs macroéconomiques d'un pays pour une année donnée, ce pays a-t-il subi un choc économique soudain cette année-là ?"

**Type de problème :** Classification supervisée binaire

**Unité d'observation :** Une ligne = un pays × une année

---

## 3. Source de données

**API principale :** World Bank Indicators API  
**URL de base :** `https://api.worldbank.org/v2/`  
**Authentification :** Aucune — entièrement gratuite et publique  
**Limite de requêtes :** Aucune limite significative pour un usage académique  
**Documentation :** `https://datahelpdesk.worldbank.org/knowledgebase/articles/889386`

**Volume de données attendu :**
- ~217 pays disponibles dans la base World Bank
- ~60 années de données (1960 à 2023)
- Volume brut estimé : 217 × 60 = **~13 000 lignes** avant nettoyage
- Volume final estimé après suppression des valeurs manquantes : **≥ 10 000 lignes**

---

## 4. Définition de la variable cible

**Nom de la variable :** `economic_shock`  
**Type :** Binaire (0 ou 1)

**Règle d'étiquetage exacte :**

Un pays-année reçoit le label **1 (choc économique)** si toutes les conditions suivantes sont réunies :
- Le taux de croissance annuel du PIB est **inférieur à 0 %** (l'économie s'est contractée)
- Le taux de croissance du PIB a **chuté de plus de 4 points de pourcentage** par rapport à l'année précédente
- Le taux de croissance de l'année précédente était **supérieur à 0 %** (le choc est soudain, pas une continuation d'une récession déjà en cours)

Dans tous les autres cas, le label est **0 (année normale)**.

Le seuil de 4 points a été retenu car il correspond aux critères utilisés dans la littérature économique pour distinguer un ralentissement cyclique normal d'un choc structurel soudain.

**Exemples concrets :**

| Pays | Année N-1 (PIB) | Année N (PIB) | Variation | Label |
|---|---|---|---|---|
| Pays A | +3.0% | -2.0% | -5.0 pts, négatif | **1 — choc** |
| Pays B | +5.0% | -4.0% | -9.0 pts, négatif | **1 — choc** |
| Pays C | +2.0% | +1.5% | -0.5 pts, positif | **0 — normal** |
| Pays D | -1.0% | -1.5% | -0.5 pts | **0 — normal** (déjà en récession) |

**Distribution attendue de la variable cible :**
- Classe majoritaire (0 — normal) : ~85 à 90 % des lignes
- Classe minoritaire (1 — choc) : ~10 à 15 % des lignes
- Ce ratio naturel est conforme à la contrainte imposée (entre 5 % et 25 %)

---

## 5. Objectifs métiers quantifiés

**Objectif 1 — Détection précoce des crises**
Détecter au moins 80 % des pays-années ayant réellement subi un choc économique, afin de permettre aux institutions de préparer une réponse politique avant que la situation ne devienne incontrôlable.

**Objectif 2 — Crédibilité du système d'alerte**
Maintenir un taux de fausses alertes suffisamment bas pour que les avertissements soient pris au sérieux par les analystes. Objectif : au moins 50 % des pays signalés ont réellement subi un choc.

**Objectif 3 — Équité géographique**
Le modèle doit fonctionner de manière raisonnable dans toutes les régions et tous les groupes de revenus, pas uniquement pour les pays à revenu élevé où les données sont plus complètes.

---

## 6. Tableau de traduction Métier → ML

| Objectif métier | Objectif ML | Métrique principale | Valeur cible |
|---|---|---|---|
| Détecter 80 % des chocs réels | Maximiser le Recall sur la classe choc (label = 1) | Recall | ≥ 0.80 |
| Limiter les fausses alertes | Maintenir une Précision acceptable sur la classe choc | Precision | ≥ 0.50 |
| Équilibrer détection et crédibilité | Optimiser la moyenne harmonique Précision/Recall | F1-score | ≥ 0.65 |
| Comparer les modèles équitablement | Évaluer la capacité de classement sur données déséquilibrées | PR-AUC | Maximiser |
| Assurer l'équité géographique | Performance acceptable par région | F1-score |  ≥ 0.55 par région   |

---

## 7. Analyse du coût métier asymétrique

### Question fondamentale
**Qu'est-ce qui coûte plus cher : un faux positif ou un faux négatif ?**

### Faux Négatif — le modèle prédit "normal" mais un vrai choc survient
Le modèle ne déclenche pas d'alerte. Le gouvernement du pays et les partenaires internationaux ne reçoivent aucun avertissement anticipé. Au moment où la crise devient visible pour tous, elle est déjà grave. Les conséquences possibles incluent :
- Retard dans le financement d'urgence international
- Accumulation accélérée de la dette publique
- Hausse rapide du chômage et de la pauvreté
- Instabilité politique et sociale
- Des années de récupération économique lente

**Coût estimé : extrêmement élevé** — potentiellement des milliards de dollars et des millions de personnes affectées.

### Faux Positif — le modèle prédit "choc" mais l'année est normale
Le modèle déclenche une fausse alerte. Les analystes effectuent un suivi supplémentaire ou préparent des plans de contingence qui s'avèrent inutiles. Quelques ressources mineures sont dépensées par excès de prudence.

**Coût estimé : faible** — inefficacité mineure, légère perturbation des ressources analytiques.

### Conclusion
Les faux négatifs sont dramatiquement plus coûteux que les faux positifs dans ce domaine. Manquer une vraie crise a des conséquences humaines irréversibles. Déclencher une fausse alerte entraîne au pire une légère inefficacité.

**→ Nous priorisons le Recall comme métrique principale.**

### Quantification approximative de l'asymétrie

| Type d'erreur | Conséquence | Coût estimé |
|---|---|---|
| Faux Négatif | Crise non détectée, pas d'intervention précoce | ~1 milliard USD + (impact humain majeur) |
| Faux Positif | Fausse alerte, surveillance inutile | ~quelques milliers USD (temps analyste) |
| **Ratio asymétrique** | | **~1 000 : 1** |

---

## 8. Métriques choisies et justification

### Métriques acceptées (notre choix)

**Recall (métrique principale)**
Mesure : parmi tous les pays-années ayant réellement subi un choc, combien le modèle en a-t-il correctement identifiés ?
Justification : correspond directement à notre objectif métier le plus important — ne pas manquer une vraie crise.
Cible : ≥ 0.80

**Precision (métrique secondaire)**
Mesure : parmi tous les pays-années que le modèle a signalés comme chocs, combien étaient réels ?
Justification : évite que le système devienne inutilisable à cause d'un trop grand nombre de fausses alertes.
Cible : ≥ 0.50

**F1-score (métrique d'équilibre)**
Mesure : moyenne harmonique de la Précision et du Recall. Force les deux métriques à être correctes simultanément.
Justification : utile pour comparer des modèles en un seul chiffre sans sacrifier l'une des deux dimensions.
Cible : ≥ 0.65

**PR-AUC (métrique de comparaison)**
Mesure : aire sous la courbe Précision-Recall sur tous les seuils de décision possibles.
Justification : contrairement au ROC-AUC, il n'est pas optimiste sur les données déséquilibrées et donne une image fidèle de la performance réelle.
Usage : comparaison entre algorithmes lors des expérimentations.

### Métriques explicitement rejetées

**Accuracy**
Raison du rejet : avec ~85-90 % des lignes étant de classe 0, un modèle naïf qui prédit toujours 0 obtiendrait 85-90 % d'accuracy tout en ne détectant jamais aucun choc réel. Cette métrique est trompeuse sur des données déséquilibrées.

**ROC-AUC seul**
Raison du rejet : optimiste sur les données déséquilibrées car il tient compte des vrais négatifs (très nombreux dans notre cas) et surestime donc la performance réelle du modèle sur la classe minoritaire.

---

## 9. Features du dataset

### Variables catégorielles

| Feature | Description | Valeurs possibles | Source |
|---|---|---|---|
| `region` | Région géographique World Bank | Sub-Saharan Africa, East Asia & Pacific, Europe & Central Asia, Latin America & Caribbean, Middle East & North Africa, North America, South Asia | Metadata pays |
| `income_group` | Groupe de revenu World Bank | Low income, Lower-middle income, Upper-middle income, High income | Metadata pays |
| `lending_type` | Type de prêt World Bank | IDA, IBRD, Blend, Not classified | Metadata pays |
| `is_crisis_decade` | Décennie de l'année (feature engineerée) | 1960s, 1970s, 1980s, 1990s, 2000s, 2010s, 2020s | Feature engineering |

### Variables numériques

| Feature | Code indicateur | Description | Unité |
|---|---|---|---|
| `gdp_growth` | NY.GDP.MKTP.KD.ZG | Taux de croissance annuel du PIB | % |
| `inflation` | FP.CPI.TOTL.ZG | Inflation des prix à la consommation | % |
| `unemployment` | SL.UEM.TOTL.ZS | Taux de chômage | % de la population active |
| `gdp_per_capita` | NY.GDP.PCAP.KD | PIB par habitant (USD constants) | USD |
| `external_debt` | DT.DOD.DECT.GN.ZS | Dette extérieure en % du RNB | % |
| `trade_openness` | NE.TRD.GNFS.ZS | Commerce en % du PIB | % |
| `fdi_inflows` | BX.KLT.DINV.WD.GD.ZS | Investissements directs étrangers | % du PIB |
| `gov_expenditure` | GC.XPN.TOTL.GD.ZS | Dépenses publiques | % du PIB |
| `gdp_growth_lag1` | Engineerée | Croissance du PIB de l'année précédente | % |
| `gdp_growth_delta` | Engineerée | Variation de la croissance vs année précédente | points de % |

**Total features : 10 (4 catégorielles + 6 numériques + 2 engineerées)** → conforme à l'exigence ≥ 8

---

## 10. Contraintes du projet — Vérification de conformité

| Critère | Exigence | Notre projet | Conforme ? |
|---|---|---|---|
| Type de tâche | Classification supervisée | Classification binaire (choc / normal) | ✅ |
| Taille totale | ≥ 10 000 lignes | ~13 000 lignes (217 pays × 60 ans) | ✅ |
| Nombre de features | ≥ 8 après feature engineering | 10 features | ✅ |
| Classe minoritaire | Entre 5 % et 25 % | ~10-15 % (chocs économiques rares) | ✅ |
| Types de variables | Numérique + catégorielle | 6 numériques + 4 catégorielles | ✅ |
| Source des données | API publique et gratuite | World Bank API — sans clé, sans limite | ✅ |
| Variable cible naturelle | Pas inventée artificiellement | PIB négatif après chute soudaine — concept économique réel | ✅ |

---

