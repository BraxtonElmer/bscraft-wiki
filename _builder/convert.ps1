# Converts downloaded pictures to the site's format: JPEG, at most 560px on the long side, transparent
# areas flattened onto the page's slot colour. Uses WPF imaging so WebP (via Windows' codec) works too.
# Usage: convert.ps1 -Pairs <file with "src|dst" per line>
param([string]$Pairs)
Add-Type -AssemblyName PresentationCore, WindowsBase
$MAX = 560
$bg = [System.Windows.Media.Color]::FromRgb(0x10, 0x14, 0x0E)
$ok = 0; $bad = @()
foreach ($line in Get-Content $Pairs) {
  if (-not $line.Trim()) { continue }
  $src, $dst = $line.Split('|')
  try {
    $fs = [System.IO.File]::OpenRead($src)
    $dec = [System.Windows.Media.Imaging.BitmapDecoder]::Create($fs, 'PreservePixelFormat', 'OnLoad')
    $frame = $dec.Frames[0]; $fs.Close()
    $w = $frame.PixelWidth; $h = $frame.PixelHeight
    $scale = [Math]::Min(1.0, [Math]::Min($MAX / $w, $MAX / $h))
    $nw = [int][Math]::Max(1, [Math]::Round($w * $scale)); $nh = [int][Math]::Max(1, [Math]::Round($h * $scale))
    # draw onto a solid background so transparency doesn't turn black in JPEG
    $dv = New-Object System.Windows.Media.DrawingVisual
    $dc = $dv.RenderOpen()
    $dc.DrawRectangle((New-Object System.Windows.Media.SolidColorBrush $bg), $null, (New-Object System.Windows.Rect 0, 0, $nw, $nh))
    $dc.DrawImage($frame, (New-Object System.Windows.Rect 0, 0, $nw, $nh))
    $dc.Close()
    $rtb = New-Object System.Windows.Media.Imaging.RenderTargetBitmap $nw, $nh, 96, 96, ([System.Windows.Media.PixelFormats]::Pbgra32)
    $rtb.Render($dv)
    $enc = New-Object System.Windows.Media.Imaging.JpegBitmapEncoder
    $enc.QualityLevel = 82
    $enc.Frames.Add([System.Windows.Media.Imaging.BitmapFrame]::Create($rtb))
    New-Item -ItemType Directory -Force (Split-Path $dst) | Out-Null
    $out = [System.IO.File]::Create($dst); $enc.Save($out); $out.Close()
    $ok++
  } catch {
    $bad += "$src : $($_.Exception.Message)"
  }
}
"converted $ok"
if ($bad.Count) { "failed:"; $bad | ForEach-Object { "  $_" } }
