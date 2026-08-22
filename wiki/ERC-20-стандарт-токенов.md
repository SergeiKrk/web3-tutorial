---
title: "ERC-20 — стандарт токенов"
date: 2026-07-19
tags: [web3, solidity, erc20, токены]
category: concept
source_count: 5
---

# ERC-20 — стандарт токенов

## Уровень 1. Для пятилетнего ребёнка

Представь, что у тебя есть игровые жетоны в парке аттракционов. Все жетоны одинаковые — один жетон ничем не отличается от другого. Ты можешь:

- Посмотреть, сколько у тебя жетонов
- Передать жетоны другу
- Узнать, сколько всего жетонов существует в парке

**ERC-20** — это правила игры для таких жетонов, но в интернете. Благодаря этим правилам все программы (кошельки, биржи, игры) понимают друг друга, потому что «говорят на одном языке». Если токен следует правилам ERC-20 — любой кошелёк сразу знает, как с ним работать.

---

## Уровень 2. Для новичка в web3

ERC-20 — это **технический стандарт взаимозаменяемых токенов** (fungible tokens) в Ethereum и совместимых блокчейнах. Стандарт описан в документе **EIP-20** (Ethereum Improvement Proposal), предложенном Fabian Vogelsteller в ноябре 2015 года.

### Что такое взаимозаменяемый токен?

Взаимозаменяемый (fungible) — значит, что один токен абсолютно идентичен другому. Как доллар: одна купюра в $1 равна любой другой купюре в $1. В отличие от **ERC-721 (NFT)** — невзаимозаменяемых токенов, где каждый уникален (как билет на концерт с конкретным местом).

### Зачем нужен стандарт?

До ERC-20 каждый разработчик придумывал свой интерфейс токена. Кошельки и биржи не могли работать с новыми токенами без индивидуальной интеграции. Стандарт решил эту проблему: **любой контракт, реализующий ERC-20, автоматически поддерживается всеми кошельками, биржами и dApps**.

### Где используются ERC-20 токены?

- **Стейблкоины** — USDT, USDC, DAI (привязаны к курсу доллара)
- **Governance-токены** — UNI (Uniswap), AAVE (Aave), MKR (MakerDAO) — дают право голоса
- **Токены проектов** — LINK (Chainlink), MATIC (Polygon)
- **Wrapped ETH (WETH)** — «обёрнутый» ETH в формате ERC-20 для совместимости с DeFi

---

## Уровень 3. Для разработчика (интерфейс и механика)

### Интерфейс ERC-20 (EIP-20)

Смарт-контракт считается ERC-20, если реализует все перечисленные методы и события:

#### Обязательные методы

```solidity
// Имя токена (человекочитаемое)
function name() public view returns (string)
// Пример: "USD Coin"

// Символ (тикер)
function symbol() public view returns (string)
// Пример: "USDC"

// Количество знаков после запятой
function decimals() public view returns (uint8)
// Пример: 6 (значит 1 USDC = 1_000_000 минимальных единиц)

// Общее количество токенов
function totalSupply() public view returns (uint256)

// Баланс конкретного адреса
function balanceOf(address _owner) public view returns (uint256)

// Перевод токенов отправителем транзакции
function transfer(address _to, uint256 _value) public returns (bool)

// Одобрение списания токенов третьим лицом
function approve(address _spender, uint256 _value) public returns (bool)

// Перевод токенов от имени другого адреса (требует approve)
function transferFrom(address _from, address _to, uint256 _value) public returns (bool)

// Сколько spender может потратить с адреса _owner
function allowance(address _owner, address _spender) public view returns (uint256)
```

#### Обязательные события

```solidity
// Эмитится при любом переводе токенов (включая mint и burn)
event Transfer(address indexed _from, address indexed _to, uint256 _value)
// Особый случай: mint — _from = address(0), burn — _to = address(0)

// Эмитится при вызове approve()
event Approval(address indexed _owner, address indexed _spender, uint256 _value)
```

`indexed` позволяет фильтровать события по этим полям при чтении логов (до 3 indexed-параметров на событие).

### Как работает approve + transferFrom

Это **двухшаговая модель делегирования** — один из ключевых паттернов ERC-20:

1. **Шаг 1 — `approve(spender, amount)`**: Алиса разрешает контракту-бирже списать до 1000 токенов с её адреса.
2. **Шаг 2 — `transferFrom(alice, bob, amount)`**: Биржа вызывает `transferFrom`, переводя токены от имени Алисы Бобу.

```
Алиса --approve(биржа, 1000)--> ERC-20 контракт
                                 |
Биржа --transferFrom(Алиса, Боб, 500)--> ERC-20 контракт
```

**Важно**: `transfer` переводит токены от `msg.sender`, а `transferFrom` — от любого адреса, который предварительно сделал `approve`.

> **Как читать связку `approve` + `transferFrom`:** читай approve как «я, Алиса, говорю контракту: разрешаю вот этому адресу-бирже снять с моего баланса до N токенов», а transferFrom как «биржевая логика говорит контракту: переведи токены от Алисы к Бобу, используя выданное мне разрешение». Мнемоника: `approve` = подписать доверенность, `transferFrom` = предъявить доверенность и совершить перевод.

### Decimals — почему баланс не в токенах

ERC-20 хранит балансы в **минимальных неделимых единицах** (как wei для ETH). Параметр `decimals` указывает, на сколько знаков нужно сдвинуть запятую:

```
decimals = 6   → balanceOf = 1_000_000 → реально 1.000000 токенов
decimals = 18  → balanceOf = 1_000_000_000_000_000_000 → реально 1.0 токен
```

Solidity **не поддерживает дробные числа**, поэтому все расчёты в целых числах, а `decimals` — чисто информационное поле для фронтенда. Большинство токенов используют `decimals = 18` (аналогично ETH).

> **Как читать `totalSupply = _initialSupply * 10**decimals`:** читай как «запиши начальную эмиссию в минимальных единицах: если хочу 1000 токенов с 18 знаками после запятой, умножь 1000 на 10¹⁸». Мнемоника: `decimal = 18` значит «храни как wei, показывай как ETH» — баланс `1000000000000000000` в контракте = `1.0` токенов в интерфейсе.

---

## Уровень 4. Для продвинутого разработчика (реализация и нюансы)

### Минимальная реализация ERC-20 на Solidity

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MyToken {
    string public name = "My Token";
    string public symbol = "MTK";
    uint8 public decimals = 18;
    uint256 public totalSupply;
    
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

> **Как читать `mapping(address => mapping(address => uint256)) public allowance`:** читай как «двухэтажный словарь: `allowance[владелец][кому_разрешил]` возвращает сколько токенов разрешено потратить». Мнемоника: это как `Map<Address, Map<Address, BigInt>>` — таблица разрешений «кто → кому → сколько».
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    
    constructor(uint256 _initialSupply) {
        totalSupply = _initialSupply * 10**decimals;
        balanceOf[msg.sender] = totalSupply;
        emit Transfer(address(0), msg.sender, totalSupply);
    }
    
    function transfer(address _to, uint256 _value) public returns (bool) {
        require(balanceOf[msg.sender] >= _value, "Insufficient balance");
        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        emit Transfer(msg.sender, _to, _value);
        return true;
    }
    
    function approve(address _spender, uint256 _value) public returns (bool) {
        allowance[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }
    
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool) {
        require(balanceOf[_from] >= _value, "Insufficient balance");
        require(allowance[_from][msg.sender] >= _value, "Insufficient allowance");
        balanceOf[_from] -= _value;
        balanceOf[_to] += _value;
        allowance[_from][msg.sender] -= _value;
        emit Transfer(_from, _to, _value);
        return true;
    }
}
```

### OpenZeppelin — промышленная реализация

В реальных проектах **никто не пишет ERC-20 с нуля** — используют проверенную библиотеку OpenZeppelin:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MyToken is ERC20 {
    constructor(uint256 initialSupply) ERC20("My Token", "MTK") {
        _mint(msg.sender, initialSupply * 10**decimals());
    }
}
```

**Что даёт OpenZeppelin сверх базового стандарта:**
- Защита от целочисленного переполнения (overflow/underflow) — встроено в Solidity 0.8+
- `_mint()` и `_burn()` — внутренние методы для создания и уничтожения токенов
- `increaseAllowance` / `decreaseAllowance` — безопасная работа с `approve` (защита от race condition)
- `permit()` (в ERC20Permit) — gasless-approve через EIP-2612 подписи
- Расширения: `ERC20Burnable`, `ERC20Capped`, `ERC20Pausable`, `ERC20Votes`

### Известные проблемы и уязвимости

#### 1. Проблема «потерянных токенов» (reception issue)

Если отправить ERC-20 токены на адрес смарт-контракта, который не умеет с ними работать — токены **навсегда потеряны**. Контракт-получатель не получает уведомления о входящем переводе. По состоянию на 2024 год таким образом потеряно более **$83 млн**.

**Способы защиты:**
- Запретить `transfer` на адрес самого токена: `require(_to != address(this))`
- Использовать `approve + transferFrom` вместо `transfer` для депозитов в контракты
- Рассмотреть альтернативные стандарты: ERC-223, ERC-1363, ERC-777
- Всегда предусматривать функцию экстренного вывода (emergency withdraw) в контрактах-получателях

#### 2. Race condition в approve

Классическая атака: Алиса одобрила 100 токенов для Боба, потом хочет изменить на 50, но Боб успевает снять 100 до того как транзакция Алисы попадёт в блок.

**Решение**: использовать `increaseAllowance` / `decreaseAllowance` из OpenZeppelin, которые изменяют allowance атомарно относительно текущего значения.

#### 3. Отсутствие обработки возвращаемого bool

Некоторые токены (особенно USDT) не возвращают `bool` из `transfer` и `transferFrom`, хотя стандарт требует. OpenZeppelin использует `safeTransfer` из `SafeERC20` для совместимости.

### Gas-оптимизации

> **Как читать gas-оптимизацию `uint256 fromBalance = balanceOf[msg.sender]`:** читай как «вместо того чтобы дважды читать из дорогого блокчейн-хранилища (SLOAD), прочитай один раз в локальную переменную памяти и работай с ней». Мнемоника: storage-чтение (SLOAD) — это как запрос к удалённой базе, а memory-переменная — как кеш в оперативке; всегда кешируй storage-переменные перед использованием в функции.

```solidity
// ❌ Дорого: двойное чтение из storage
function transfer(address to, uint256 value) public returns (bool) {
    require(balanceOf[msg.sender] >= value);  // SLOAD 1
    balanceOf[msg.sender] -= value;           // SSTORE
    balanceOf[to] += value;                   // SLOAD + SSTORE
}

// ✅ Дёшево: кеширование в memory
function transfer(address to, uint256 value) public returns (bool) {
    uint256 fromBalance = balanceOf[msg.sender];  // SLOAD (1 раз)
    require(fromBalance >= value);
    balanceOf[msg.sender] = fromBalance - value;
    balanceOf[to] += value;
}
```

### ERC-20 на практике: ethers.js / viem

```typescript
// Чтение баланса (бесплатно, view-функция)
const balance = await contract.balanceOf(address);

// Чтение с учётом decimals (формат для пользователя)
const raw = await contract.balanceOf(address);
const decimals = await contract.decimals();
const formatted = Number(raw) / 10 ** Number(decimals);

// Отправка токенов (транзакция, стоит gas)
const tx = await contract.transfer(to, amount);
await tx.wait();  // ждём подтверждения

// Подписка на события Transfer в реальном времени
contract.on("Transfer", (from, to, value) => {
    console.log(`${from} → ${to}: ${value}`);
});
```

### Альтернативные стандарты

| Стандарт | Отличие от ERC-20 |
|----------|-------------------|
| **ERC-223** | Уведомляет контракт-получатель через `tokenFallback`, решает проблему потерянных токенов |
| **ERC-777** | Хуки `tokensReceived` + операторы по умолчанию, более гибкий, но сложнее (есть уязвимости) |
| **ERC-1363** | `transferAndCall` — перевод + вызов функции получателя в одной транзакции |
| **ERC-4626** | Стандарт для токенизированных хранилищ (vaults) — надстройка над ERC-20 |
| **ERC-2612** | `permit()` — approve через подпись, без отдельной транзакции (gasless) |

---

## Связанное

- [[wiki/Solidity-основы]] — синтаксис Solidity, необходимый для написания ERC-20
- [[wiki/Словарь-web3]] — термины: event, gas, ABI, storage, mapping
- [[wiki/Главная]] — дорожная карта изучения web3, этап 2 (смарт-контракты)
- [[wiki/Блокчейн-как-это-работает]] — база по блокчейну: аккаунты, транзакции, gas
