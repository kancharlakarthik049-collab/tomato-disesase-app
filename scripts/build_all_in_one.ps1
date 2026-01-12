Param(
    [string]$ImageName = 'tomato-app:allinone',
    [string]$ModelUrl = ''
)

$buildArgs = @()
if ($ModelUrl -ne '') { $buildArgs += "--build-arg"; $buildArgs += "MODEL_URL=$ModelUrl" }

Write-Host "Building all-in-one image $ImageName using Dockerfile.allinone..."
docker build -f Dockerfile.allinone -t $ImageName $buildArgs '.'

Write-Host "To run the image locally (port 5000):"
Write-Host "  docker run --rm -p 5000:5000 $ImageName"
