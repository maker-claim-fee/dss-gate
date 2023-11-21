# Gate Designs

## Gate 1

[Gate 1](gate1.md)

## Design considerations for other gate implementations

### Multi-User Gate

ApprovedTotal value can be integrated into the `bud` access control mapping to allow a single gate contract and its backup balance to be shared across multiple integrations.

### Payback function

Implement a payback function to allow approved integrations to send back dai to the surplus buffer and regain additional draw limit for their future use.

