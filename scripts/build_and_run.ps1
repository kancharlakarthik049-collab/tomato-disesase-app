Param(
    [string]$ImageName = 'tomato-app:latest',
    [string]$ModelUrl = ''
)

Write-Host "Building image $ImageName..."
docker build -t $ImageName .

$runArgs = @('--rm','-p','5000:5000','-e','PORT=5000','-v',"${PWD}\static\uploads:/app/static/uploads")
if ($ModelUrl -ne '') { $runArgs += ('-e', "MODEL_URL=$ModelUrl") }

Write-Host "Running container from $ImageName..."
docker run @runArgs $ImageName
