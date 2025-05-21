## Running the App Locally

```bash

export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_SESSION_TOKEN=your_session_token
export AWS_DEFAULT_REGION=us-east-1
export S3_BUCKET_NAME=hw06-zhh20013-1
export PORT=5001

pip install -r requirements.txt

python3 app.py

# Docker command
docker --version

docker buildx build --platform linux/amd64 -t hw06-python-flask-zhisong-huang-zhh20013 .

docker run -p 5001:5001 \
  -v ~/.aws/credentials:/root/.aws/credentials:ro \
  -e AWS_DEFAULT_REGION=us-east-1 \
  -e AWS_SESSION_TOKEN=your_session_token \
  -e S3_BUCKET_NAME=hw06-zhh20013-1 \
  hw06-python-flask-zhisong-huang-zhh20013