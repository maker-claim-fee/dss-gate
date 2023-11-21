#!/usr/bin/env bash

# Script to run certora prover formal verification of Dss-Gate

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https:#www.gnu.org/licenses/>.

set -e

echo "Running Certora Prover for dss-gate";

SOLC=~/.nix-profile/bin/solc-0.8.1

# Certora Prover Command Runner
certoraRun ../src/gate1.sol:Gate1 Vat.sol Vow.sol \
         --link Gate1:vat=Vat Gate1:vow=Vow \
         --verify Gate1:Gate1.spec \
         --msg "$1"
