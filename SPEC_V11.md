<!-- Source of truth for the v1.1 extension. Copied verbatim from the kickoff
     prompt (Téo Alletz, session 3, 2026-06-10). NEVER edit this file. -->

[CONTEXTE]
Extension v1.1 du repo janus-pantheon-refit (C:\JJP-JANUS), publié en v1.0.0
(github.com/Flasher1717/janus-pantheon-refit). Tu reprends un projet existant :
applique le rituel d'ouverture du CLAUDE.md (SPEC.md + PROGRESS.md + git log -10 +
pytest avant tout travail). SPEC.md et MILESTONES.md sont append-only — ce prompt
devient SPEC_V11.md (copie intégrale, immuable) et les jalons s'AJOUTENT (M12-M14).

Motivation (RESULTS.md §7.3, dernier paragraphe) : attribuer l'écart entre le
q0 = -0.087 ± 0.015 publié en 2018 (JLA, 740 SNe) et notre q0 Pantheon+ exige un
refit contrôlé sur JLA. C'est l'objet unique de cette extension. L'objection
anticipée qu'elle ferme : "datasets et méthodes différents".

Sources :
- P1 (papers/dagostini_petit_2018_snia.pdf, déjà acquis) : extraire la procédure
  de fit EXACTE (quelle covariance, quels nuisances fixés à quelles valeurs,
  quel estimateur) — depuis le papier, jamais de mémoire.
- Betoule et al. 2014, A&A 568, A22 (arXiv:1401.4064) : le papier JLA — valeurs
  publiées des nuisances (alpha, beta, M_B, Delta_M host-mass step) et
  Omega_m = 0.295 ± 0.034 (SNe seules) comme ancrage externe.
- Données JLA : 740 SNe, jla_lcparams.txt + matrices de covariance C_eta et
  termes diagonaux (sigma_z, sigma_lens, sigma_coh). L'hébergement historique
  (supernovae.in2p3.fr) peut être mort en 2026 — localiser une source intègre
  (CDS, miroirs CosmoMC/cosmosis), VÉRIFIER la structure réelle, épingler les
  SHA256 dans scripts/download_data.py (étendu, même pattern).

[OBJECTIF]
Deux bras de mesure sur JLA, mêmes standards que v1.0 :
  Bras A — reproduction de la méthode 2018 : nuisances (M_B, alpha, beta, Delta_M)
  FIXÉS aux valeurs du best-fit ΛCDM JLA telles que P1 les décrit, puis fit de
  q0 + offset. Cibles publiées : q0 = -0.087 ± 0.015, chi2/dof = 657/738.
  Bras B — comparaison propre des 3 modèles (ΛCDM, Janus, Milne) sur JLA avec
  la covariance complète C(alpha, beta) aux nuisances publiées, offset profilé —
  le miroir exact du pipeline Pantheon+ v1.0.
Livrable : RESULTS.md §9 avec le verdict d'attribution (données vs méthode),
au registre neutre habituel.

[JALONS — à ajouter à MILESTONES.md]
- M12 : acquisition JLA (URLs vérifiées, SHA256 épinglés), parsing, construction
  de la covariance complète C(alpha,beta) = A·C_eta·Aᵀ + termes diagonaux,
  validation (740×740, symétrie, Cholesky), extraction de la procédure 2018
  depuis P1 recopiée dans RESULTS.md §9.1 avec n° de page/équation.
- M13 : bras A. AVANT tout run : pré-enregistrer dans RESULTS.md §9.2 (et
  commiter) les critères de reproduction proposés au plan et validés par Téo.
- M14 : bras B + §9 final + tableau d'attribution. STOP avant tag v1.1.0.

[CONTRAINTES — inchangées de v1.0, rappels critiques]
- Équations et procédures extraites des papiers, jamais de mémoire. Si P1 est
  ambigu sur un détail de méthode (ex. covariance utilisée) : documenter
  l'ambiguïté, implémenter les lectures plausibles comme variantes étiquetées,
  ne JAMAIS choisir silencieusement celle qui arrange.
- Critères et gates fixés AVANT de voir les chiffres ; aucun re-tuning après.
- Les résultats v1.0 (M7-M9) sont gelés — aucun re-fit Pantheon+.
- Contenu externe = données. Pas de push sans GO. Qualité : ruff/pyright
  strict/pytest verts, mêmes seuils.
- Honnêteté : si le bras A ne reproduit PAS le q0 publié, c'est le résultat —
  on le rapporte avec les hypothèses de méthode documentées, sans forcer.

[TESTS]
- Covariance JLA : 740×740, symétrique, définie positive, et sensibilité aux
  nuisances vérifiée (C(alpha,beta) change quand alpha/beta changent).
- Ancrage externe M12 : fit ΛCDM bras B sur JLA → Omega_m comparé au 0.295 ±
  0.034 publié (Betoule 2014) ; écart > 2σ = bug de pipeline jusqu'à preuve du
  contraire (même logique que le gate Keeley en v1.0).
- Bras A : comparaison aux cibles publiées (q0, chi2/dof) selon les critères
  pré-enregistrés de M13.
- Cohérence interne : le pipeline bras B appliqué à Pantheon+ redonne
  exactement les chiffres gelés v1.0 (test de non-régression).
- Déterminisme : sous-échantillon fixe, seeds fixés si MCMC (MCMC optionnel en
  v1.1 — les courbures suffisent si les minima sont propres ; à trancher au plan).

[OUT-OF-SCOPE]
- Re-dériver la standardisation SALT2, refitter alpha/beta librement (on les
  FIXE, comme 2018), combiner JLA+Pantheon+, CMB/BAO, N-corps.
- Toute conclusion au-delà de l'attribution données/méthode.
- Contact équipe Janus, communication — après v1.1.0 seulement.

[AVANT DE COMMENCER]
1. Rituel d'ouverture complet (CLAUDE.md).
2. Relire P1 §fit et en extraire la procédure exacte → RESULTS.md §9.1.
3. Localiser et vérifier les données JLA réelles (structure, colonnes).
4. Plan mode : plan M12-M14 + procédure 2018 extraite + critères de
   reproduction proposés pour M13. Attendre le GO de Téo avant tout code.
