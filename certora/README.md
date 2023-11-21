# Instructions to setup and run certora formal verification of dss-gate.

## Pre-requisites

- Clone the dss-gate repository

`git clone git@github.com:maker-claim-fee/dss-gate.git`

- Install Docker

Follow instructions based on your Operating System : https://docs.docker.com/get-docker/

## Setup Certora

### Step 1 : Pull the Trail-of-bits ETH sec toolbox Container Image

`docker pull trailofbits/eth-security-toolbox`

- Change to dss-gate directory

`cd .../dss-gate`

### Step 2 : Run the Trail-Of-Bits container

`docker run -it -v "$PWD":/home/training trailofbits/eth-security-toolbox`

- Install Certora CLI

`pip3 install certora-cli`

- Set up the Certora Key

`export CERTORAKEY=<certora_key>` # You can contact Certora Inc., to get a key.

- Select the solc version

`solc-select use 0.8.0`

Note : Make sure you run this command when your pwd is set to cloned repo folder(i.e dss-gate). This will enable you to access all the files and folders in the current working directory inside the container under `/home/training` folder.

Yay !! Setup is complete

## Run Certora Tests

`./certora/runCertora.sh "Run dss-gate certora formal verification tests"`
