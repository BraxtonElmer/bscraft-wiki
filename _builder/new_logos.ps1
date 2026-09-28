# Pulls the logo out of each newly added jar and saves it into logos/ at the same size as the others (max 220px).
Add-Type -AssemblyName System.Drawing; Add-Type -AssemblyName System.IO.Compression.FileSystem
$W = Split-Path -Parent $MyInvocation.MyCommand.Path
$MODS = 'C:\Users\raxtr\AppData\Roaming\BSCraft\minecraft\mods'
$want = @{
  'mca' = @('minecraft-comes-alive*', 'mca.png')
  'fast_travel_waypoints' = @('Fast_Travel*', 'logo.png')
  'curiouslanterns' = @('curiouslanterns*', 'curious_lanterns.png')
  'fallingtree' = @('FallingTree*', 'logo.png')
  'saplanting' = @('saplanting*', 'assets/saplanting/icon.png')
  'create_enchantment_industry' = @('create-enchantment*', 'icon.png')
  'create_dragons_plus' = @('CreateDragonsPlus*', 'icon.png')
}
foreach ($id in $want.Keys) {
  $pat, $entry = $want[$id]
  $jar = (Get-ChildItem $MODS -Filter $pat | Select-Object -First 1).FullName
  $z = [System.IO.Compression.ZipFile]::OpenRead($jar)
  $e = $z.Entries | Where-Object { $_.FullName -eq $entry } | Select-Object -First 1
  if (-not $e) { "$id : entry not found"; $z.Dispose(); continue }
  $ms = New-Object System.IO.MemoryStream; $s = $e.Open(); $s.CopyTo($ms); $s.Close(); $z.Dispose(); $ms.Position = 0
  $img = [System.Drawing.Image]::FromStream($ms)
  $max = 220
  $scale = [Math]::Min(1.0, [Math]::Min($max / $img.Width, $max / $img.Height))
  $nw = [int]($img.Width * $scale); $nh = [int]($img.Height * $scale)
  $bmp = New-Object System.Drawing.Bitmap $nw, $nh, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.InterpolationMode = if ($img.Width -le 64) { 'NearestNeighbor' } else { 'HighQualityBicubic' }
  $g.DrawImage($img, 0, 0, $nw, $nh)
  $g.Dispose()
  $bmp.Save("$W\logos\$id.png", [System.Drawing.Imaging.ImageFormat]::Png)
  "{0,-30} {1}x{2}" -f $id, $nw, $nh
  $bmp.Dispose(); $img.Dispose()
}
