# Gate

- Governance tool to limit vat.suck() integration risk\*

## Designs

Gate contracts can be customized and deployed to handle the needs of their linked integration.

### Gate1 "Simple Gate"

Implementation: [`gate1.sol`](src/gate1.sol)

Documentation: [gate1](docs/gate1.md)

Features:

- Token approval style draw limit on vat.suck()
- Backup dai balance in case vat.suck fails
- Access priority- vat.suck first, backup balance second
- No hybrid draw at one time from both vat.suck and backup balance

## Development

- Works with [Dapptools](https://github.com/dapphub/dapptools) or [Foundry](https://github.com/gakonst/foundry)

## Disclaimer

This code belongs to the MakerDAO community and the Copyright for the code belongs to the Dai Foundation.
