# Nettoie uniquement les anciens fichiers de code devenus inutiles après le passage à Firestore.
$targets = @(
  "app\db.py",
  "scripts\migrate_sqlite_to_firestore.py",
  "README-FIRESTORE.md"
)
foreach ($target in $targets) {
  if (Test-Path $target) {
    Remove-Item $target -Force
    Write-Host "Supprimé: $target"
  }
}
Write-Host "Nettoyage terminé. data\synaclock.db reste ignoré par Git pour éviter toute perte accidentelle."
