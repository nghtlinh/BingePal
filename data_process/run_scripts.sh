#!/bin/bash

echo "================================"
echo "Creating Training Data Sample..."
echo "================================"
pipenv run python create_training_data.py

echo "================="
echo "Building Model..."
echo "================="
pipenv run python build_model.py

echo "================"
echo "Running Model..."
echo "================"
pipenv run python run_model.py

echo "========="
echo "Finished!"
echo "========="