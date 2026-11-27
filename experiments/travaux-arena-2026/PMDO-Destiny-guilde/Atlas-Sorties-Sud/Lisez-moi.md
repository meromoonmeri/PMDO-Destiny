# Atlas Destiny — les 15 salles et les sorties sud

Ouvre [Guilde-Destiny-Toutes-les-Salles.html](../Guilde-Destiny-Toutes-les-Salles.html) dans un navigateur. Tout est intégré au fichier. Il s’ouvre sur **Les 15 salles**, avec **Jour** sélectionné, sans réseau.

**Les quatre lumières de Grodoudou.** Jour reprend les tons dorés et les vitres claires des [intérieurs de Grodoudou](../../Reference-Guildhouse/Project-Pokemon/Guilde-de-Grodoudou.html). Le crépuscule transpose le ciel orangé de la façade G01P01B. L’aube est une interprétation pêche, faute de carte d’aube dans les références. La nuit conserve à l’identique la palette validée : vitres bleu profond et dortoirs plus tamisés. Le fond reste brun et le mobilier suit la lumière de la salle. Les mesures sont dans `Palettes-ambiances.json` et `Palette-nuit.json` : aucun changement des géométries ou des cadres.

- **Les 15 salles** : plans natifs 0.7.7, vitrage R2, liseré et calque de verdure masqué. Les 29 accès et la géométrie d’origine sont conservés. Active **Seuils** pour repérer les passages. Un clic sur une salle ouvre l’atelier ; **Sud corrigé** ouvre directement son cadrage au seuil.
- **Sorties sud** : comparaisons avant/après pour l’Accueil, la Salle des missions, le Grand Salon, le Bureau du maître, la Cuisine et les deux dortoirs nord. Le cadre natif de 320 × 240 px ne montre plus la bande sous le passage. Le décor latéral reste apparent. Aucun seuil ni chemin n’est étendu.
- **Aménager** : 33 sprites PMU à placer sur les plans. **Comparer les 4** montre le jour, l’aube, le crépuscule et la nuit. L’export JSON conserve les aménagements. Les plans sur les coordonnées natives de l’ancien atelier sont compatibles ; un plan avec des objets placés dans une salle de géométrie Grodoudou doit rester dans cette variante.

L’HTML ne modifie pas les fichiers du jeu. Le [kit de cadrage pour Destiny 0.7.7](../Cadrage-sorties-sud/PMD-Destiny-0.7.7-Cadrage-sorties-sud.zip) reste séparé. La [variante Grodoudou](../Guilde-Destiny-Sans-Verdure.html) demeure disponible sans changement.

`Verification-plans.json` conserve les limites sud et les contrôles des décors. `Tests-navigateur.json` détaille les vérifications de l’aperçu. `Sources/Assembler.py` réassemble le HTML à partir des données déjà embarquées et des sources.
