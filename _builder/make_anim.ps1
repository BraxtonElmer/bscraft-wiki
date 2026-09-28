# Builds the animated title-screen hero from the pack's FancyMenu "forest" menu layers.
# For every layer (in the order forest_bg.txt draws them) it writes the first frame as a base image, and for
# animated layers a sprite sheet holding only the rectangle that changes. Output: theme/anim/*.png + theme/anim.json
param([string[]]$Slow = @('back_anim', 'front_anim', 'front_tree'), [string[]]$StaticOnly = @())   # slow layers keep every 2nd frame
Add-Type -AssemblyName System.Drawing; Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @"
using System; using System.Drawing; using System.Drawing.Imaging; using System.Runtime.InteropServices;
public static class Anim {
  public static int[] Px(Bitmap b) { var d = b.LockBits(new Rectangle(0,0,b.Width,b.Height), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
    var a = new int[b.Width*b.Height]; Marshal.Copy(d.Scan0, a, 0, a.Length); b.UnlockBits(d); return a; }
  static bool Same(int p, int q) { return p == q || (((p>>24)&255) == 0 && ((q>>24)&255) == 0); }
  // union rectangle of pixels that differ from frame 0 (transparent pixels count as equal)
  public static int[] Changed(Bitmap[] f) { int w = f[0].Width, h = f[0].Height; var p0 = Px(f[0]);
    int x0=w, y0=h, x1=-1, y1=-1;
    for (int i = 1; i < f.Length; i++) { var p = Px(f[i]);
      for (int y = 0; y < h; y++) for (int x = 0; x < w; x++) if (!Same(p[y*w+x], p0[y*w+x])) {
        if (x<x0) x0=x; if (x>x1) x1=x; if (y<y0) y0=y; if (y>y1) y1=y; } }
    return x1 < 0 ? null : new int[]{x0, y0, x1-x0+1, y1-y0+1}; }
}
"@
$W = Split-Path -Parent $MyInvocation.MyCommand.Path
$src = "$W\theme_src\bg"; $out = "$W\theme\anim"; New-Item -ItemType Directory -Force $out | Out-Null
Get-ChildItem $out -Filter *.png | ForEach-Object { [IO.File]::Delete($_.FullName) }

function Frames($fma) {
  $z = [System.IO.Compression.ZipFile]::OpenRead("$src\animated\$fma.fma"); $list = @()
  $n = ($z.Entries | Where-Object { $_.FullName -match '^frames/\d+\.png$' }).Count
  for ($i = 0; $i -lt $n; $i++) { $e = $z.GetEntry("frames/$i.png"); $ms = New-Object System.IO.MemoryStream; $s = $e.Open(); $s.CopyTo($ms); $s.Close(); $ms.Position = 0
    $list += ,(New-Object System.Drawing.Bitmap ([System.Drawing.Bitmap]::FromStream($ms))) }
  $z.Dispose(); return ,$list
}
function SavePng($bmp, $name) { $bmp.Save("$out\$name.png", [System.Drawing.Imaging.ImageFormat]::Png) }
function Canvas($w, $h) { $b = New-Object System.Drawing.Bitmap $w, $h, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $g = [System.Drawing.Graphics]::FromImage($b); $g.InterpolationMode = 'NearestNeighbor'; $g.PixelOffsetMode = 'Half'; $g.CompositingMode = 'SourceCopy'; return @($b, $g) }

# name, file (fma name or png), parallax depth (menu base pixels at full mouse travel)
$layers = @(
  @('sky', '#sky', 0.4), @('back_anim', '01_back', 0.8), @('back', 'back.png', 1.0), @('flag', '03_hanging_flag', 1.3),
  @('leaves', '04_leaves', 1.6), @('bush_back', '08_bush_flower_back', 1.4), @('front_anim', '05_front', 1.8), @('wisteria', '06_wisteria_falls.png', 2.2),
  @('wall_flower', '07_wall_flower', 1.9), @('bush', '08_bush_flower', 2.3), @('travellers', 'xx_elf_and_boy', 2.0), @('front', 'front.png|11_front_sword.png', 2.8),
  @('front_tree', '10_front_tree', 3.2), @('leaves_front', 'xx_leaves_fix', 3.4))
$meta = @()
foreach ($L in $layers) {
  $name, $file, $depth = $L
  $entry = [ordered]@{ n = $name; d = $depth }
  if ($file -eq '#sky') {
    $c = Canvas 341 190; $c[1].Clear([System.Drawing.ColorTranslator]::FromHtml('#8FC3EA')); $c[1].CompositingMode = 'SourceOver'
    $cl = [System.Drawing.Bitmap]::FromFile("$src\cloud.png"); $c[1].DrawImage($cl, 0, 0, 373, 190); $cl.Dispose(); SavePng $c[0] $name; $c[1].Dispose(); $c[0].Dispose()
  } elseif ($file -like '*.png*') {
    $c = Canvas 341 190; $c[1].CompositingMode = 'SourceOver'
    foreach ($f in $file.Split('|')) { $b = [System.Drawing.Bitmap]::FromFile("$src\$f"); $c[1].DrawImage($b, 0, 0, 341, 190); $b.Dispose() }
    SavePng $c[0] $name; $c[1].Dispose(); $c[0].Dispose()
  } else {
    $fr = Frames $file; SavePng $fr[0] $name
    $box = [Anim]::Changed($fr)
    if ($box -and ($StaticOnly -notcontains $name)) {
      # (PowerShell names are case-insensitive, so the box uses bx/by/bw/bh to stay clear of $W)
      $bx, $by, $bw, $bh = $box; $step = if ($Slow -contains $name) { 2 } else { 1 }
      $idx = @(); for ($i = 0; $i -lt $fr.Count; $i += $step) { $idx += $i }
      $cols = [Math]::Max(1, [Math]::Min($idx.Count, [Math]::Floor(2048 / $bw))); $rows = [Math]::Ceiling($idx.Count / $cols)
      $c = Canvas ($cols * $bw) ($rows * $bh)
      for ($k = 0; $k -lt $idx.Count; $k++) {
        $c[1].DrawImage($fr[$idx[$k]], (New-Object System.Drawing.Rectangle (($k % $cols) * $bw), ([Math]::Floor($k / $cols) * $bh), $bw, $bh), (New-Object System.Drawing.Rectangle $bx, $by, $bw, $bh), 'Pixel') }
      SavePng $c[0] "$name.sheet"; $c[1].Dispose(); $c[0].Dispose()
      $entry.box = @($bx, $by, $bw, $bh); $entry.cols = $cols; $entry.frames = $idx.Count; $entry.ms = 66 * $step
    }
    $fr | ForEach-Object { $_.Dispose() }
  }
  $meta += [pscustomobject]$entry
}
$meta | ConvertTo-Json -Depth 4 -Compress | Set-Content -Encoding utf8 "$W\theme\anim.json"
Get-ChildItem $out | Sort-Object Length -Descending | ForEach-Object { "{0,-26} {1,8:N0} KB" -f $_.Name, ($_.Length / 1KB) }
"total {0:N0} KB" -f ((Get-ChildItem $out | Measure-Object Length -Sum).Sum / 1KB)
