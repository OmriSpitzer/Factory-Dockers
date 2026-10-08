$root = Split-Path -Parent $PSScriptRoot

$workers = @(
    "workers.assemble.assembler",
    "workers.testing.tester",
    "workers.package.packager",
    "workers.shipping.shipper"
)

foreach ($module in $workers) {
    Start-Process -FilePath "python" -ArgumentList "-m", $module -WorkingDirectory $root
}
