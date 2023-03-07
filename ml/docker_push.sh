#!/bin/bash
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker tag exam_api_service:latest isenkir/api_service:latest
docker push isenkir/api_service:latest
docker tag exam_predictor_service:latest isenkir/predictor_service:latest
docker push isenkir/models_app:latest