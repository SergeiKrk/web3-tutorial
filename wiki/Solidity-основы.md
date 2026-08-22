---
title: "Solidity — основы синтаксиса"
date: 2026-07-13
tags: [solidity, смарт-контракты, синтаксис, этап-2]
category: concept
---

# Solidity — основы синтаксиса

## Что такое смарт-контракт

Код, который живёт в блокчейне по адресу (как аккаунт). Любой может его вызвать — он выполняется на всех нодах сети. Код неизменяем после деплоя, состояние хранится в блокчейне.

Контракт = класс в ООП. Имеет: состояние (storage), функции (методы), события (emit/logs).

## Структура контракта

```solidity
// SPDX-License-Identifier: MIT     ← обязательная лицензия
pragma solidity ^0.8.20;            ← версия компилятора

contract Имя {
    // 1. Переменные состояния (storage)
    // 2. События (events)
    // 3. Модификаторы (modifiers)
    // 4. Конструктор (constructor)
    // 5. Функции
}
```

## Типы данных

### Примитивы

| Тип | Размер | Пример |
|-----|--------|--------|
| `uint256` | 0..2²⁵⁶-1 | `uint256 count = 0;` |
| `int256` | знаковое | `int256 x = -5;` |
| `uint8` | 0..255 | экономит газ в массивах |
| `address` | 20 байт | `address owner = 0x...;` |
| `address payable` | 20 байт + transfer | можно отправлять ETH |
| `bool` | true/false | `bool active = true;` |
| `bytes32` | 32 байта фикс. | `bytes32 hash = 0x...;` |
| `string` | динамический | дорого, избегать где можно |

### Составные

```solidity
// Маппинг — аналог объекта/Map. НЕЛЬЗЯ итерировать
mapping(address => uint256) public balances;

> **Как читать `mapping(address => uint256) public balances`:** читай как «словарь: набираешь адрес — получаешь число, как `balances[0xABC...]` вернёт баланс этого адреса». Мнемоника: mapping в Solidity — это `Map<KeyType, ValueType>` из TypeScript, но без `.keys()`, без `.values()`, без возможности перебора; только «дай значение по ключу».

// Массив
uint256[] public dynamicArray;        // динамический
address[10] public fixedArray;        // фиксированный размер

// Структура
struct User {
    address addr;
    uint256 balance;
    bool active;
}
```

## Видимость функций

| Модификатор | Снаружи | Внутри контракта | В наследниках |
|------------|---------|-----------------|---------------|
| `public` | да | да | да |
| `private` | нет | да | нет |
| `internal` | нет | да | да |
| `external` | да | нет (только `this.f()`) | да |

## Мутабельность (читать/писать)

| Ключ | Меняет состояние | Газ (внешний вызов) |
|------|-----------------|--------------------|
| (нет) | да | да |
| `view` | нет, только читает | **нет** |
| `pure` | нет, даже не читает | **нет** |
| `payable` | да + принимает ETH | да |

```solidity
function getBalance() public view returns (uint256) {
    return address(this).balance;      // читает, газ не тратит
}

function add(uint a, uint b) public pure returns (uint) {
    return a + b;                      // не трогает состояние вообще
}

function deposit() public payable {
    // msg.value — присланные ETH
}
```

## Storage vs Memory — критично для газа

| | Storage | Memory |
|---|---|---|
| Где | Блокчейн (диск) | Оперативная память |
| Живёт | Навсегда | Только на время вызова |
| Стоимость | **ОЧЕНЬ дорого** | Дёшево |
| По умолчанию | Переменные состояния | Локальные переменные |

```solidity
uint256[] public stored;              // storage (неявно)

function example() public {
    uint256[] memory temp = new uint256[](10);  // memory (явно)
    temp[0] = 1;
    stored = temp;                     // копия storage ← memory (дорого!)
}
```

## Глобальные переменные

```solidity
msg.sender          // address — кто вызвал функцию
msg.value           // uint256 — сколько ETH прислали
block.timestamp     // uint256 — время блока (не точное!)
tx.gasprice         // цена газа
address(this)       // адрес самого контракта
```

## Модификаторы (собственные)

```solidity
modifier onlyOwner() {
    require(msg.sender == owner, "Not owner");
    _;  // ← здесь выполняется тело функции
}

> **Как читать `modifier onlyOwner() { require(...); _; }`:** читай как «перед тем как выполнить тело функции, проверь условие; `_` — это место, куда подставится код функции». Мнемоника: модификатор — это как `middleware` в Express.js или `beforeEach` в тестах: сначала проверка, потом `_` = `next()`.

function reset() public onlyOwner {
    count = 0;
}
```

## События (Events)

Пишутся в логи блокчейна. Нечитаемы из контракта (только извне через web3-библиотеки).
Дёшево (~375 gas vs ~20 000 за storage-запись). Основной способ коммуникации контракт → фронтенд.

```solidity
event Transfer(address indexed from, address indexed to, uint256 value);

function transfer(address to) public {
    emit Transfer(msg.sender, to, amount);
}
```

`indexed` — по этим полям можно фильтровать события на фронтенде (до 3 полей).

> **Как читать `event Transfer(address indexed from, address indexed to, uint256 value)`:** читай как «объявляю лог-запись с тремя полями; `indexed` значит "по этому полю можно искать и фильтровать снаружи", а `value` без `indexed` — лежит в данных события, но фильтровать по нему нельзя». Мнемоника: `indexed` = «индексируемое поле» как `WHERE` в SQL, а не-indexed = данные, которые просто лежат в теле события.

## Контракт-счётчик (итоговый пример)

См. ``raw/Counter.sol`` — полный код:

- Состояние: `count` (uint256), `owner` (address)
- События: `Incremented`, `Decremented`, `Reset`
- Модификатор: `onlyOwner`
- Функции: `increment()`, `decrement()`, `reset()`, `getCount()`

## Связанное

- [[wiki/Блокчейн-как-это-работает]] — база по блокчейну
- [[wiki/Словарь-web3]] — термины (gas, storage, event, ABI)
- [[wiki/Сравнение-ethers-viem-wagmi]] — как вызывать контракты с фронтенда
