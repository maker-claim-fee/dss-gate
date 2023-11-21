// SPDX-License-Identifier: AGPL-3.0-or-later

using Vat as vat
using Vow as vow

////////////////////////////////////////////////////////////////////////////
//                      Methods                                           //
////////////////////////////////////////////////////////////////////////////

methods {

  // Gate Contract methods - env free
  wards(address) returns (uint256) envfree
  bud(address) returns (uint256) envfree
  withdrawAfter() returns (uint256) envfree
  approvedTotal() returns (uint256) envfree
  vow() returns (address) envfree

  // Vat related external contract methods
  vat.dai(address) returns (uint256) envfree
  vat.wards(address) returns (uint256) envfree
  vat.sin(address) returns (uint256) envfree
  vat.debt() returns (uint256) envfree
  vat.vice() returns (uint256) envfree
  vat.live() returns (uint256) envfree
  vat.move(address, address, uint256)

  // Vow
  vow.vat() returns (address) envfree

  // Gate contract methods
  suck(address, address, uint256)
  rely(address)
  deny(address)
  kiss(address)
  diss(address)
  file(bytes32, uint256)
  maxDrawAmount() returns (uint256)
  daiBalance() returns (uint256)
  draw(uint256)
  withdrawDai(address, uint256)
  debt() returns (uint256)
  vice() returns (uint256)
}

////////////////////////////////////////////////////////////////////////////
//                       Rules                                            //
////////////////////////////////////////////////////////////////////////////


/*
  Rule : Verify if the draw method works as expected.

  1. If the approved total is sufficient, backup balance remains constant.
  2. If the approved total is insufficient, backup balance is utilized.

*/
rule draw(uint256 amount) {

  env e;

  require(vat.live() == 1, "Vat is not live");

  uint256 _approvedTotal = approvedTotal(); // max approved total to suck.
  address currCont = currentContract;
  uint256 _balance = vat.dai(currentContract); // backup balance of gate
  address vowAddress = vow();
  uint256 sinBalance = vat.sin(vowAddress);

  draw(e, amount);

  uint256 balance_ = vat.dai(currentContract);
  uint256 approvedTotal_ = approvedTotal();

  assert(e.msg.sender != currentContract && _approvedTotal > amount => _approvedTotal - amount == approvedTotal_, "Approved total is sufficient, backup balance remains same");

  assert(e.msg.sender != currentContract && _approvedTotal < amount && _balance > amount => _balance - amount == balance_ , "Approved total is not sufficient, backup balance is leveraged");

}

/*
 Rule : Verify if the suck methods works as expected.

 1. If the backup balance is sufficient, then the destination balance is increased by amount.
 2. If the approvated total is sufficient, then the approvedTotal is decreased by amount.s

*/
rule suck(address src, address dest, uint256 amount) {
  env e;

  require(vat.live() == 1, "Vat is not live");

  address currContract = currentContract;
  require(currContract != dest, "Gate cannot self withdraw to itself");

  uint256 _gateBalance = vat.dai(currContract);
  uint256 _destBalance = vat.dai(dest);
  uint256 _approvedTotal = approvedTotal();

  suck(e, src, dest, amount);

  uint256 gateBalance_ = vat.dai(currContract);
  uint256 destBalance_ = vat.dai(dest);
  uint256 approvedTotal_ = approvedTotal();

  assert(_approvedTotal >= amount  => approvedTotal_ == _approvedTotal - amount, "the approved total is not adjusted correctly after suck invocation");
  assert(_approvedTotal < amount && _gateBalance >= amount => gateBalance_ == _gateBalance - amount, "the balance could not be suck'd from gate");

}

/*
Rule : Capture and assert all the possible reverts from suck method.
*/
rule suck_with_revert(address src, address dest, uint256 amount) {

  env e;

  address currCont = currentContract;
  address vowAddress = vow();

  uint256 _budStatus = bud(e.msg.sender);
  uint256 _wardStatus = wards(e.msg.sender);

  uint256 sinBalance = vat.sin(vowAddress);
  uint256 _destBalance = vat.dai(dest);
  uint256 _gateBalance = daiBalance(e);
  uint256 _approvedTotal = approvedTotal();
  uint256 _vatWardStatus = vat.wards(currCont);
  uint256 _vatLiveStatus = vat.live();

  require(bud(e.msg.sender) == 0 || bud(e.msg.sender) == 1, "bud value can be either 0 or 1");

  require(debt(e) + amount < max_uint, "vat debt overflow");
  require(vice(e) + amount < max_uint, "vat vice overflow");
  require(sinBalance + amount < max_uint, "vat sin overflow");
  require(vat.dai(currCont) + amount < max_uint, "gate bal overflow");
  require(_vatLiveStatus == 1);

  suck@withrevert(e, src, dest, amount);

  bool suckReverted = lastReverted;

  bool revert1 = _budStatus != 1;
  bool revert2 = _gateBalance < amount && _approvedTotal < amount && _vatWardStatus != 1;
  bool revert3 = amount > _gateBalance && amount > _approvedTotal;
  bool revert4 = _destBalance + amount > max_uint;
  bool revert5 = _approvedTotal >= amount && _gateBalance < amount && _vatWardStatus != 1;
  bool revert6 = _gateBalance + amount < _gateBalance;

  assert(revert1 => suckReverted, "bud is not authorized, The suck method did not revert");
  assert(revert2 => suckReverted, "the gate contract is not added as a ward in vat. The suck did not revert");
  assert(revert3 => suckReverted, "Insufficient balance - both backup and gate, The suck method did not revert");
  assert(revert4 => suckReverted, "destination balance overflow, the suck did not revert");
  assert(revert5 => suckReverted, "Gate not authorized to suck from Vat, the suck did not revert");
  assert(revert6 => suckReverted, "gate balance cannot overflow, the suck did not revert");

 assert( suckReverted => revert1 || revert2 || revert3 || revert4 || revert5 || revert6, "All possible revert are not covered in suck method in process of formal verification");
}

/*
 Rule : Verify that governance can withdraw dai from gate contract.

 If the gate balance is sufficient, then the amount can be withdrawn by governance.
*/

rule withdrawDai(address destination, uint256 amount)
{
  env e;

  address currCont = currentContract;
  require(currCont != destination, "Gate cannot self withdraw to itself");

  uint256 _gateBalance = vat.dai(currCont);
  uint256 _destBalance = vat.dai(destination);

  withdrawDai(e, destination, amount);

  uint256 gateBalance_ = vat.dai(currCont);
  uint256 destBalance_ = vat.dai(destination);

  assert(_gateBalance >= amount => destBalance_ == _destBalance + amount, "the balance could not be withdrawn from gate");

}

/*
 Rule : Capture and assert all the possible reverts from the withdrawDai method
*/
rule withdrawDaiWithRevert(address destination, uint256 amount) {

  env e;

  address currCont = currentContract;

  uint256 _destBalance = vat.dai(destination);
  uint256 _wardStatus = wards(e.msg.sender);
  uint256 withdrawAfter = withdrawAfter();
  uint256 gateBalance = daiBalance(e);

  require(_destBalance + amount < max_uint, "Vat dai overflow");

  withdrawDai@withrevert(e, destination, amount);

  bool withdrawReverted = lastReverted;

  bool revert1 = _wardStatus != 1;
  bool revert2 = e.msg.value > 0; // withdraw is not payable
  bool revert3 = gateBalance < amount;
  bool revert4 = _destBalance + amount < _destBalance ;
  bool revert5 = e.block.timestamp < withdrawAfter;

  assert(revert1 => withdrawReverted, "Ward is not authorized, The withdrawDai method did not revert");
  assert(revert2 => withdrawReverted, "Sending ETH, msg.value is not zero. The withdrawDai did not revert");
  assert(revert3 => withdrawReverted, "The amount requested to withdraw is greater than gateBalance. The withdrawDai method did not revert");
  assert(revert4 => withdrawReverted, "vat dai overflow, The withdrawdai did not revert");
  assert(revert5 => withdrawReverted, "gov cannot withdraw before wtihdrawafter timestamp. The method did not revert");

  assert(withdrawReverted => revert1 || revert2 || revert3 || revert4 || revert5, "All the possible reverts in withdrawDai are not covered in process formal verification");

}

/*
 Rule : Verify that method 'rely' works as expected.

 A new ward will be set.
*/
rule rely(address usr)
description "Verify that method 'rely' works as expected for user : ${usr}"
{
  env e;

  rely(e, usr);

  assert(wards(usr) ==  1, "rely did not add ward as expected");
}

/*
 Rule : Verify that method 'rely' reverts when sender is not authorized.

 Only a ward (aka governance) can add yet another ward.
*/
rule rely_with_revert(address usr)
description "Verify that method 'rely' reverts when ${e.msg.sender} is not authorized."
{
  env e;

  uint256 _wardstatus = wards(e.msg.sender);

  rely@withrevert(e, usr);

  assert(_wardstatus != 1 => lastReverted, "Rely did not revert when user is unauthorized");
}

/*
 Rule : Verify that method 'deny' works as expected,

 An existing ward will be removed. The value of ward will be set to 0.
*/
rule deny(address usr)
description "Verify that method 'deny' works as expected for user : ${usr}"
{
  env e;

  deny(e, usr);

  assert(wards(usr) == 0, "deny did not remove ward as expected");
}

/*
 Rule : Verify that method 'deny' reverts when sender is not authorized
*/
rule deny_with_revert(address usr)
description "Verify that method 'deny' reverts when user ${msg.sender} is not authorized"
{
  env e;

  uint256 _wardstatus = wards(e.msg.sender);

  deny@withrevert(e, usr);

  assert(_wardstatus != 1 => lastReverted, "Deny did not revert when user is unauthorized");

}

/*
 Rule : Verify that method 'kiss' works as expected
 */
rule kiss(address usr)
description "Verify that the method 'kiss' works as expected"
{
  env e;

  kiss(e, usr);

  assert(bud(usr) == 1, "The kiss method did not add integration as expected.");

}

/*
 Rule : Verify that method 'kiss' reverts as expected
*/
rule kiss_with_revert(address usr)
{
  env e;

  uint256 _wardStatus = wards(e.msg.sender);
  uint256 _budStatus = bud(usr); // TODO : requireinvariant bud can be only 0 or 1.
  require(bud(usr) == 0 || bud(usr) == 1, "bud should be either 0 or 1");
  uint256 _withdrawAfter = withdrawAfter();

  kiss@withrevert(e, usr);

  bool revert1 = _wardStatus != 1;
  bool revert2 = _budStatus == 1;
  bool revert3 = usr == 0;
  bool revert4 = e.msg.value > 0; // kiss is not payable.
  bool revert5 = e.block.timestamp < _withdrawAfter;

  assert( revert1 => lastReverted, "Ward not authorized, The kiss did not revert");
  assert( revert2 => lastReverted, "Bud is already approved, The kiss did not revert");
  assert( revert3 => lastReverted, "address(0) cannot be added as bud, The kiss did not revert");
  assert( revert4 => lastReverted, "Sending ETH, msg.value is not zero, The kiss did not revert");
  assert( revert5 => lastReverted, "withdraw condition failed");

  assert( lastReverted => revert1 || revert2 || revert3 || revert4 || revert5 , "All the revert rules are not covered in kiss method during the process of formal verification");

}

/*
 Rule : Verify that method 'diss' works as expected.

 An existing bud is removed. The value of bud to be removed is set to 0.
*/
rule diss(address usr)
description "Verify that method 'diss' works as expected"
{
  env e;

  diss(e, usr);

  assert(bud(usr) == 0, "The diss method did not remove integration as expected.");
}

/*
 Rule : Verify that method 'diss' reverts as expected

Possible Revertions :

 1. If a msg.sender is not authorized.
 2. If existing bud is not approved.
 3. Cannot send any ETH when calling this function

*/
rule diss_with_revert(address usr)
{
  env e;

  uint256 _wardStatus = wards(e.msg.sender);
  uint256 _budStatus = bud(usr); // TODO : requireinvariant bud can be only 0 or 1.
  require(bud(usr) == 0 || bud(usr) == 1, "bud should be either 0 or 1");

  diss@withrevert(e, usr);

  bool revert1 = _wardStatus != 1;
  bool revert2 = _budStatus == 0;
  bool revert3 = e.msg.value > 0; // diss is not payable.

  assert( revert1 => lastReverted, "Ward not authorized, The diss did not revert");
  assert( revert2 => lastReverted, "Bud is not approved, No reason to diss. The diss did not revert");
  assert( revert3 => lastReverted, "Sending ETH, msg.value is not zero, The diss did not revert");

  assert( lastReverted => revert1 || revert2 || revert3 , "All the revert rules are not covered in process of formal verification");

}

/*
 Rule : Verify if the file method works as expected

 Set values for approvedTotal and withdrawAfter
*/
rule file(bytes32 configKey, uint256 configValue)
{

  uint256 _approvedTotal = approvedTotal();
  uint256 _withdrawAfter = withdrawAfter();

  env e;

  file(e, configKey, configValue);

  uint256 approvedTotal_ = approvedTotal();
  uint256 withdrawAfter_ = withdrawAfter();

  assert(_approvedTotal != approvedTotal_ => approvedTotal_ == configValue);
  assert(_withdrawAfter != withdrawAfter_ => withdrawAfter_ == configValue);

}

/*
 Rule : Verify if the file method reverts as expected.

 Potential Revertions :

 1. Unrecognized value for 'what'. [Permissible values : approvedTotal, withdrawAfter]
 2. msg.value ETH cannot be sent to this method.
 3. msg.sender is not authorized
 4. The new value of withdrawAfter > currentValueOf(withdrawAfter)
*/
rule file_with_reverts(bytes32 what, uint256 data) {

  env e;

  uint256 _wardStatus = wards(e.msg.sender);
  uint256 _withdrawAfter = withdrawAfter();

  file@withrevert(e, what, data);

  // 0x617070726f766564746f74616c00000000000000000000000000000000000000 = approvedtotal
  // 0x7769746864726177616674657200000000000000000000000000000000000000 = withdrawafter
  bool revert1 = what != 0x617070726f766564746f74616c00000000000000000000000000000000000000 &&
                 what != 0x7769746864726177616674657200000000000000000000000000000000000000;

  bool revert2 = e.msg.value > 0;
  bool revert3 = _wardStatus != 1;
  bool revert4 = what == 0x7769746864726177616674657200000000000000000000000000000000000000 &&
                 data <= _withdrawAfter;

  assert(revert1 => lastReverted, "The unrecognized 'what' did not revert, The file method did not revert");
  assert(revert2 => lastReverted, "Sending ETH - msg.value is not zero, file method is not payable, The file method did not revert");
  assert(revert3 => lastReverted, "sender is not authorized to call file, The file method did not revert");
  assert(revert4 => lastReverted, "withdrawafter value should be greater than current value, The file method did not revert");

  assert(lastReverted => revert1 || revert2 || revert3 || revert4 , "All the revert cases are not covered in CVL rule for method 'file' ");
}

/*
Rule : Verify that maximum draw amount possible is maximum of (backup balance , approvedTotal )
*/
rule maxdraw_amount()
{
  env e;

  uint256 _daiBalance = daiBalance(e);
  uint256 _approvedTotal = approvedTotal();

  uint256 maxAmount = maxDrawAmount(e);

  assert(maxAmount == (_daiBalance > _approvedTotal ? _daiBalance : _approvedTotal),
          "The max amount is not computed as expected");
}

/*
Rule : Verify that maxdrawAmount reverts as expected
*/
rule maxdraw_amount_reverts()
{
  env e;

  uint256 _daiBalance = daiBalance(e);
  uint256 _approvedTotal = approvedTotal();

  uint256 maxAmount = maxDrawAmount@withrevert(e);

  assert(maxAmount == (_daiBalance > _approvedTotal ? _daiBalance : _approvedTotal),
          "The max amount is not equal to daibalance");
}