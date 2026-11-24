param(
    [string]$Bundle = (Join-Path $PSScriptRoot 'Sources/Kingambit-Cinematiques.bundle')
)

# Lancer depuis un clone de Destiny déjà authentifié à GitHub. Aucun jeton dans ce script.
$ErrorActionPreference = 'Stop'
$Depot = 'https://github.com/meromoonmeri/PMDO-Destiny.git'
$Branche = 'refs/heads/wip/reverie-integration-kingambit-cafe'
$Base = '3d86bd838698d9de699c76f6f715c8eef35562e5'
$Candidat = '0c0a13f75e13ab95132b66b282dae1b369ef885b'
$RefBundle = 'refs/heads/apercu/kingambit-cinematiques'

function Lire-TeteDistante {
    $lignes = @(git ls-remote --exit-code $Depot $Branche)
    if ($LASTEXITCODE -ne 0 -or $lignes.Count -ne 1) {
        throw 'Branche distante introuvable ou accès à GitHub impossible.'
    }
    return ($lignes[0] -split '\s+')[0]
}

$null = git rev-parse --git-dir
if ($LASTEXITCODE -ne 0) { throw 'Exécutez le script depuis votre clone Git de Destiny.' }
$Bundle = (Resolve-Path -LiteralPath $Bundle).Path
$Tete = Lire-TeteDistante
if ($Tete -eq $Candidat) {
    Write-Host "Déjà en ligne : $Candidat sur $Branche"
    exit 0
}
if ($Tete -ne $Base) { throw "La branche a avancé vers $Tete. Aucun push effectué." }

git fetch --no-tags $Depot $Branche
if ($LASTEXITCODE -ne 0) { throw 'Impossible de récupérer la base.' }
git bundle verify $Bundle
if ($LASTEXITCODE -ne 0) { throw 'Bundle invalide ou base manquante.' }
git fetch --no-tags $Bundle $RefBundle
if ($LASTEXITCODE -ne 0) { throw 'Impossible de lire le candidat dans le bundle.' }
if ((git rev-parse FETCH_HEAD) -ne $Candidat -or (git rev-parse 'FETCH_HEAD^1') -ne $Base) {
    throw 'Le candidat ou son parent ne correspond pas à la révision vérifiée.'
}

git push --porcelain $Depot "${Candidat}:$Branche"
if ($LASTEXITCODE -ne 0) { throw 'Push refusé. Vérifiez les droits GitHub et l’état de la branche.' }
if ((Lire-TeteDistante) -ne $Candidat) { throw 'Le SHA distant ne correspond pas au candidat.' }
Write-Host "Push vérifié : $Candidat sur $Branche. Aucun tag, release ou workflow déclenché par ce script."
