// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

contract Insurance {
    address payable public insurer;
    address payable public policyholder;
    uint public premium;
    uint public coverage;
    uint public expiration;
    bool public isExpired;
    bool public isClaimed;

    constructor(
        address payable _insurer,
        address payable _policyholder,
        uint _premium,
        uint _coverage,
        uint _expiration
    ) {
        insurer = _insurer;
        policyholder = _policyholder;
        premium = _premium;
        coverage = _coverage;
        expiration = _expiration;
    }

    function payPremium() public payable {
        require(msg.value == premium, "Incorrect premium amount");
    }

    function expirePolicy() public {
        require(msg.sender == insurer, "Only insurer can expire the policy");
        isExpired = true;
    }

    function claim() public {
        require(msg.sender == policyholder, "Only policyholder can claim");
        require(!isExpired, "Policy has expired");
        require(!isClaimed, "Claim has already been made");
        isClaimed = true;
        policyholder.transfer(coverage);
    }
}
