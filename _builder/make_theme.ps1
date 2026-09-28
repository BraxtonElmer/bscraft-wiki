# Builds the wiki's theme images from the pack's FancyMenu "forest" menu assets (copied into theme_src).
Add-Type -AssemblyName System.Drawing; Add-Type -AssemblyName System.IO.Compression.FileSystem
$W   = Split-Path -Parent $MyInvocation.MyCommand.Path
$src = "$W\theme_src"
$out = "$W\theme"; New-Item -ItemType Directory -Force $out | Out-Null

function LoadLayer($p) {
  if ($p -like '*.fma') {
    $z = [System.IO.Compression.ZipFile]::OpenRead("$src\bg\$p"); $e = $z.GetEntry('frames/0.png')
    $ms = New-Object System.IO.MemoryStream; $s = $e.Open(); $s.CopyTo($ms); $s.Close(); $z.Dispose(); $ms.Position = 0
    return [System.Drawing.Bitmap]::FromStream($ms)
  }
  return [System.Drawing.Bitmap]::FromFile("$src\bg\$p")
}

# 1. the main-menu scene, frame 0 of every layer in the menu's own order, over a sky
$layers = @('animated\01_back.fma','back.png','animated\03_hanging_flag.fma','animated\04_leaves.fma','animated\08_bush_flower_back.fma',
  'animated\05_front.fma','06_wisteria_falls.png','animated\07_wall_flower.fma','animated\08_bush_flower.fma','animated\xx_elf_and_boy.fma',
  'front.png','11_front_sword.png','animated\10_front_tree.fma','animated\xx_leaves_fix.fma')
$scene = New-Object System.Drawing.Bitmap 341, 190, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$g = [System.Drawing.Graphics]::FromImage($scene); $g.InterpolationMode = 'NearestNeighbor'; $g.PixelOffsetMode = 'Half'
$g.Clear([System.Drawing.ColorTranslator]::FromHtml('#8FC3EA'))
$cloud = [System.Drawing.Bitmap]::FromFile("$src\bg\cloud.png"); $g.DrawImage($cloud, 0, 0, 373, 190); $cloud.Dispose()
foreach ($l in $layers) { $b = LoadLayer $l; $g.DrawImage($b, 0, 0, 341, 190); $b.Dispose() }
$g.Dispose(); $scene.Save("$out\scene.png", [System.Drawing.Imaging.ImageFormat]::Png)

# 2. portrait for the dialogue box: the two travellers on the stairs
$pr = New-Object System.Drawing.Bitmap 60, 60
$g = [System.Drawing.Graphics]::FromImage($pr); $g.InterpolationMode = 'NearestNeighbor'; $g.PixelOffsetMode = 'Half'
$g.DrawImage($scene, (New-Object System.Drawing.Rectangle 0, 0, 60, 60), (New-Object System.Drawing.Rectangle 143, 74, 60, 60), 'Pixel')
$g.Dispose(); $pr.Save("$out\portrait.png", [System.Drawing.Imaging.ImageFormat]::Png); $pr.Dispose(); $scene.Dispose()

# 3. nine-slice frames: the gold lattice copied pixel for pixel from the menu buttons (ui_btn_sp_0.png), on moss-dark instead of indigo.
#    frame_lit.png is the hover state: the lattice brightens, the way the menu's own buttons light up under the cursor.
$corner = @('.#oooooooo','xooooooooo','oooooXXXXX','ooooX+XoXo','oooXXXXXXo','ooXoXoXo+o','o+XXXXXooo','ooXoXooooo','ooXXXooooo','ooXooooooo')
function MakeFrame($fillHex, $fill2Hex, $lineHex, $file) {
  $fill = [System.Drawing.ColorTranslator]::FromHtml($fillHex); $fill2 = [System.Drawing.ColorTranslator]::FromHtml($fill2Hex); $line = [System.Drawing.ColorTranslator]::FromHtml($lineHex)
  $f = New-Object System.Drawing.Bitmap 21, 21, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  for ($y = 0; $y -lt 21; $y++) { for ($x = 0; $x -lt 21; $x++) {
    $cx = [Math]::Min($x, 20 - $x); $cy = [Math]::Min($y, 20 - $y)
    if ($cx -lt 10 -and $cy -lt 10) { $ch = $corner[$cy][$cx] }
    elseif ($cy -lt 10) { $ch = $corner[$cy][9]; if ($cy -eq 2) { $ch = 'X' } }
    elseif ($cx -lt 10) { $ch = $corner[$cx][9]; if ($cx -eq 2) { $ch = 'X' } }
    else { $ch = 'o' }
    $c = switch -CaseSensitive ($ch) { '.' { [System.Drawing.Color]::FromArgb(0, $fill) } '#' { [System.Drawing.Color]::FromArgb(50, $fill) }
      'x' { [System.Drawing.Color]::FromArgb(86, $fill) } 'X' { $line } '+' { $fill2 } default { $fill } }
    $f.SetPixel($x, $y, $c) } }
  $f.Save("$out\$file", [System.Drawing.Imaging.ImageFormat]::Png); $f.Dispose()
}
MakeFrame '#161B14' '#1D2419' '#BAC15A' 'frame.png'
MakeFrame '#222A1C' '#2A3423' '#E6E68F' 'frame_lit.png'

# 4. copies used as-is
Copy-Item "$src\ui\main\logo.png" "$out\logo.png" -Force
foreach ($n in 'items_hero_sword', 'items_azure_flower', 'items_girl_ring') { Copy-Item "$src\misc\$n.png" "$out\$n.png" -Force }
Get-ChildItem $out | Select-Object Name, Length
