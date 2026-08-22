// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title Counter — простейший смарт-контракт
/// @notice Демонстрирует: состояние, события, view-функции, модификаторы
contract Counter {
    // ===== Состояние =====
    uint256 public count;
    address public owner;

    // ===== События =====
    event Incremented(uint256 newValue);
    event Decremented(uint256 newValue);
    event Reset(address indexed by, uint256 oldValue);

    // ===== Конструктор =====
    constructor() {
        owner = msg.sender;  // тот, кто задеплоил
    }

    // ===== Модификатор =====
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }

    // ===== Функции =====
    function increment() public {
        count += 1;
        emit Incremented(count);
    }

    function decrement() public {
        count -= 1;
        emit Decremented(count);
    }

    function reset() public onlyOwner {
        uint256 oldValue = count;
        count = 0;
        emit Reset(msg.sender, oldValue);
    }

    function getCount() public view returns (uint256) {
        return count;
    }
}
