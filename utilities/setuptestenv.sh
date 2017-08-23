#!/bin/bash

# This dynamically generates the .env file for tests prior to running the
# Docker commands because the circle environment variables need to be exposed
# to Docker before it starts up

env > .env
