# Rapport préalable : ressources PMU dans Destiny

Base distante v0.5.7 `ee39156a24f350b67e81740478be8505f4ff1a05`. Avant intervention : la sauvegarde complète des 35 fichiers locaux et du placement Draco est `chantier-bassin-audit/sauvegarde-travail-local-draco-devant-pierre.zip`, CRC vérifié. Les cinq objets étaient déjà préparés dans `chantier-defauts-46-52/sauvegarde-objets-pmu-local.zip`, CRC vérifié ; aucun ne porte un nom de fichier existant dans la base.

Résultat nouveau : les 40 banques de tuiles PMU historiques figurent déjà dans la branche distante, et les 40 SHA-256 téléchargés correspondent au manifeste. Cela ne garantit ni l'index réellement chargé dans un paquet installé, ni les objets complets, ni les animations, ni les ressources d'autres époques PMU.

Ne copier que les cinq objets entiers préexistants, avec leurs PNG d'import, dans le chantier local : pas de modification de Ground, ni de scripts ou d'index. Ces objets sont statiques (une trame) et ne représentent pas tous les objets PMU. Refaire les tests sans présumer de l'éditeur ou du moteur. La licence MIT du dépôt PMU ne prouve pas les droits de chaque graphisme, bien que l'utilisateur indique qu'ils sont libres.

Cadence : code source historique `Client/Widgets/MapViewer.cs` alterne l'état global des tuiles avec un test `e.Tick > lastAnimTick + 250`. Le rendu `MapRenderer.cs` remplace la tuile par sa variante lorsqu'elle existe. Il s'agit d'un intervalle d'environ 250 ms, régi par l'horloge du client et non d'une cadence individuellement stockée pour chaque objet. Le mode développeur Destiny expose pour les décorations `FrameLength`, `StartFrame`, `EndFrame` et le choix de l'animation via `GroundTabDecorationsViewModel.cs`. Les feuilles d'objets multi-images doivent encore être construites depuis des regroupements vérifiés ; une banque de tuiles ne suffit pas à les fournir comme objets.

L'inventaire des 2 000 cartes standards trouve 4 080 paires de tuiles différentes, 293 742 occurrences sur 962 cartes, dont 22 paires/34 occurrences avec référence invalide. Une paire de cases n'établit ni les contours d'un objet complet ni les autres versions PMU. Ne pas découper automatiquement des fleurs ou des meubles en affirmant que chaque fragment est un objet complet.

L'autorisation Device a été confirmée par l'utilisateur, mais le processus détenant temporairement la session n'a pas survécu à l'étape d'autorisation. Aucun jeton n'a été affiché ou sauvegardé et aucun push n'a été effectué.
