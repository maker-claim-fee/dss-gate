// SPDX-License-Identifier: AGPL-3.0-or-later
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

pragma solidity ^0.8.0;

import "./vat.sol";

contract TestVat is Vat {
    uint256 internal constant RAY = 10 ** 27;
    uint256 internal constant WAD = 10 ** 18;

    // constructor(){
    // }

    function rmul(uint256 x, uint256 y) internal pure returns (uint256 z) {
        z = (x * y) / RAY;
    }

    function ilkSetup(bytes32 ilk) public {
        this.init(ilk);
    }

    // increase rate by a percentage
    function increaseRate(bytes32 ilk_, uint256 percentage, address vow) public returns (uint256) {
        Ilk storage ilk = ilks[ilk_];

        // percentage between 0 to 500  in wad
        require(percentage >= 0 && percentage <= (500 * WAD), "not-valid-percentage");
        int256 rate = int256((ilk.rate * percentage) / 10 ** 20);

        ilk.rate = _add(ilk.rate, rate);
        int256 rad = _mul(ilk.Art, rate);
        dai[vow] = _add(dai[vow], rad);
        debt = _add(debt, rad);

        return ilk.rate;
    }

    function mint(address usr, uint256 rad) public {
        dai[usr] += rad;
        debt += rad;
    }

    function shutdown() public {
        live = 0;
    }
}
