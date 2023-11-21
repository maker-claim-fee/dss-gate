# Gate 1 "Simple Gate"

Governance does not have the ability to impose limits on the amount of dai an authorized contract can be draw from the Maker protocol through `vat.suck()`. Even the amount of dai held in the surplus buffer does not act as a natural upper bound to limit risk on the Maker protocol.

Maker protocol needs to impose limits on the amount of Dai an integration can suck from vat interface.

The integration might need to draw Dai even after emergency shutdown (ES) is triggered and cannot rely on the simple vat suck interface that stops working after ES.

Goal for the design of the Simple Gate contract is to impose limits on vat.suck() without adding special integration requirements to the integration.

## Features

Functionality of the Gate contract can be broken down into these items,

### Draw Limits

Governance needs the ability to setup mechanisms that define limits on `vat.suck()` calls initiated by an integration. Suck call is approved when the amount falls within the limit but rejected when the amount is beyond the limits set. Such risk limits can either be encoded in a static manner, like a max amount allowed to be drawn, or the limit can be more dynamic based on calculations derived from other on-chain parameters.

Gate contracts should implement a standard `accessSuck` function to perform the draw limit check, and manage the call to vat.suck(). accessSuck will return true if successful or false if unsuccessful.

Simple gate implements a static draw limit- like an approval on an ERC20 token, and this approval limit is decreased as it is drawn down.

### Backup Balance

Hold a dai balance within the contract to be used as a backup source of funds for draw calls from the integration when the draw limit is not sufficient to allow the vat.suck() or the gate contract is not authorized in vat which results in vat.suck() failure.

Dai balance can be supplied either by a DssVest like stream or timely Dai transfers from Maker governance based on integration needs.

Backup balance gives integrations an additional guarantee of funds if vat.suck() fails due to a revoked governance authorization or emergency shutdown.

Gate contracts should implement a standard `withdrawalConditionSatisfied()` function which returns true or false based on backup balance withdrawal condition checks. Withdrawal condition of a gate contract can be custom designed for the needs of the integration it is attached to.

Simple Gate encodes an withdraw-after timestamp as a withdrawal condition to allow governance to withdraw the entire balance after the current timestamp is past withdraw-after.

The withdraw-after date can be increased by governance at any time but cannot be decreased and moved back into the past to prevent early withdrawal of the backup balance.

### Suck Interface

Gate contracts always implement a `suck()` function with the same signature as `vat.suck()` to maintain backwards compatibility. An integration is able to execute `gate.suck()` for its needs just like it would call `vat.suck()`. Gate in turn will call vat.suck() after performing internal draw limit to approve the call made by the integration.

Other draw functions can also be implemented based on the specific needs of the contracts that are going to be attached to it.

Simple Gate implements a simple `draw(uint256 amount)` function to allow an integration to draw dai.

### Vat Forwarding functions

Gate contract deployed for an integration can also implement forwarding functions to allow the attached integration to use gate as the sole interface to access vat. Integration can send all vat calls to the gate contract when appropriate forwarding functions are implemented within gate to handle them. This removes the need for an integration to store a second vat address to access vat functions other than vat.suck().

Gate is a permanent solution that does not limit but rather improves the vat.suck() interface for integrations with its storage of a backup dai balance.

### Ownership

Ownership of the gate contract will be with maker governance.

## Usage Scenarios

### Disconnected

Gate contract can be used by an integration even when gate is not authorized by vat, or when its internal vat draw limit is set to zero, which disables its use of `vat.suck()`.

All calls to `gate.suck()` from the integration will now try to draw Dai from the backup balance which is the dai balance of the Gate contract itself.

### Connected

Maker governance can authorize the gate contract within vat and allow it to call `vat.suck()`. Maker governance can then increase the draw limit in the gate contract to allow gate to execute `vat.suck()` up to a certain amount of dai.

Backup dai balance held in gate contract can also be present to handle any future uncertainties.

## Deployment & Configuration

1. One gate contract is deployed for the needs of a single integration. Sharing this contract among multiple parties should be discouraged.

2. Governance approves the gate contract in vat.

3. Governance either sets a draw limit as defined by the gate contract, or loads the gate contract with a backup dai balance to service the needs of the integration.

4. Governance sets withdraw conditions on the backup balance.

5. Governance authorizes the integration contract address to access its draw functions like gate.suck().
