Add-Type -AssemblyName System.Drawing
$src = Join-Path $PSScriptRoot 'logos_raw'; $dst = Join-Path $PSScriptRoot 'logos'
Get-ChildItem $src -Filter *.png | ForEach-Object {
  $img = [System.Drawing.Image]::FromFile($_.FullName)
  $max = 220
  $scale = [Math]::Min(1.0, [Math]::Min($max / $img.Width, $max / $img.Height))
  $w = [int][Math]::Max(1, $img.Width * $scale); $h = [int][Math]::Max(1, $img.Height * $scale)
  $bmp = New-Object System.Drawing.Bitmap $w, $h
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  if ($img.Width -le 64) { $g.InterpolationMode = 'NearestNeighbor' } else { $g.InterpolationMode = 'HighQualityBicubic' }
  $g.PixelOffsetMode = 'Half'
  $g.DrawImage($img, 0, 0, $w, $h)
  $bmp.Save((Join-Path $dst $_.Name), [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose(); $img.Dispose()
}
