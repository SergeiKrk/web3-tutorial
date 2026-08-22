---
title: "OpenZeppelin — безопасные смарт-контракты"
date: 2026-07-19
tags: [web3, solidity, openzeppelin, безопасность]
category: tool
source_count: 8
---

# OpenZeppelin — безопасные смарт-контракты

> **OpenZeppelin Contracts** — самая популярная и проверенная библиотека смарт-контрактов для Ethereum и EVM-совместимых блокчейнов. Прошедшие аудит реализации стандартов (ERC-20, ERC-721, ERC-1155), контроль доступа, утилиты безопасности и обновляемые контракты. Де-факто стандарт индустрии.

**Документация:** [docs.openzeppelin.com](https://docs.openzeppelin.com/contracts/5.x/) | **GitHub:** [OpenZeppelin/openzeppelin-contracts](https://github.com/OpenZeppelin/openzeppelin-contracts) | **Форум:** [forum.openzeppelin.com](https://forum.openzeppelin.com)

---

## Уровень 1: 🍵 Зачем нужен OpenZeppelin

В блокчейне нельзя просто нажать «Ctrl+Z». Транзакция выполнена — и навсегда. Баг в смарт-контракте = деньги потеряны безвозвратно. Вспомни:

- **The DAO hack (2016)** — $60M украдено из-за reentrancy-атаки
- **Parity wallet (2017)** — $280M заморожено навсегда из-за бага в multisig
- **Wormhole bridge (2022)** — $326M украдено

**OpenZeppelin решает эту проблему** — даёт тебе контракты, которые:

- **Прошли аудит** профессиональных security-фирм (каждый релиз!)
- **Следуют EIP/ERC стандартам** — твой токен будут понимать все кошельки и биржи
- **Покрыты тестами** на 100% (почти каждый контракт)
- **Используются в продакшене** крупнейшими проектами: Uniswap, Aave, Compound, Optimism, Arbitrum

**Аналогия:** как не строить дом с нуля каждый раз, а взять проверенные стройматериалы, которые инженеры уже испытали на прочность.

### Установка

```bash
# npm (Hardhat, стандарт)
npm install @openzeppelin/contracts

# Foundry (git)
forge install OpenZeppelin/openzeppelin-contracts
```

В коде — просто импортируешь и наследуешь:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MyToken is ERC20 {
    constructor(uint256 initialSupply) ERC20("MyToken", "MTK") {
        _mint(msg.sender, initialSupply);
    }
}
```

> **Как читать `contract MyToken is ERC20 { constructor(uint256 initialSupply) ERC20("MyToken", "MTK") { _mint(msg.sender, initialSupply); } }`:** «создай свой токен, унаследовав ВСЮ стандартную логику ERC-20: в конструкторе передай имя и символ родительскому контракту, затем напечатай стартовый запас на кошелёк деплойера». Мнемоника: `is ERC20` = скопировал весь стандарт бесплатно, `_mint` = напечатал токены из воздуха.

Готово. Твой токен совместим с MetaMask, Etherscan, Uniswap и всеми ERC-20-инструментами.

---

## Уровень 2: 🔧 Основные модули

### 1. ERC-20: взаимозаменяемые токены

Стандарт для «обычных» токенов — как USDT, UNI, LINK. Каждый токен равен другому (fungible).

**Ключевой контракт:** `ERC20.sol`

```solidity
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract GoldToken is ERC20 {
    constructor() ERC20("Gold", "GLD") {
        _mint(msg.sender, 1000 * 10 ** decimals());
    }
}
```

**Важные расширения ERC-20:**

| Расширение | Зачем |
|---|---|
| `ERC20Burnable` | Возможность сжигать токены (`burn`) |
| `ERC20Capped` | Ограничение максимального supply |
| `ERC20Pausable` | Админ может приостановить трансферы |
| `ERC20Permit` | Безгазовые approval через подписи (EIP-2612) |
| `ERC20Votes` | Токен как голос в governance |
| `ERC20FlashMint` | Flash-loans (займи и верни в одной транзакции) |

**Decimals:** По умолчанию 18 (как у ETH). Если хочешь изменить — переопредели `decimals()`.

Связано: [[wiki/ERC-20-стандарт-токенов]]

---

### 2. ERC-721: NFT (невзаимозаменяемые токены)

Каждый токен уникален — `tokenId`. Идеально для коллекционных предметов, игровых айтемов, билетов.

**Ключевой контракт:** `ERC721.sol`

```solidity
import {ERC721URIStorage, ERC721} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract GameItem is ERC721URIStorage {
    uint256 private _nextTokenId;

    constructor() ERC721("GameItem", "ITM") {}

    function awardItem(address player, string memory tokenURI)
        public
        returns (uint256)
    {
        uint256 tokenId = _nextTokenId++;
        _mint(player, tokenId);
        _setTokenURI(tokenId, tokenURI);
        return tokenId;
    }
}
```

**Важные расширения ERC-721:**

| Расширение | Зачем |
|---|---|
| `ERC721URIStorage` | Хранит метаданные каждого токена (JSON с image, name, attributes) |
| `ERC721Enumerable` | Возможность перебирать все токены владельца (дорого по газу!) |
| `ERC721Burnable` | Сжигание токенов |
| `ERC721Pausable` | Пауза трансферов |
| `ERC721Royalty` (EIP-2981) | Роялти создателю при перепродаже |

**tokenURI** — ссылка на JSON-метаданные токена. Может быть:
- HTTP URL: `https://example.com/metadata/1.json`
- IPFS: `ipfs://Qm...`
- Data URI (on-chain): `data:application/json;base64,...`

Связано: [[wiki/ERC-721-NFT-стандарт]]

---

### 3. Access Control: кто что может делать

#### Ownable — простейший контроль

Самый базовый паттерн: у контракта есть **owner** — один адрес с особыми правами.

```solidity
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract MyContract is Ownable {
    constructor(address initialOwner) Ownable(initialOwner) {}

    function normalThing() public {
        // кто угодно может вызвать
    }

    function adminThing() public onlyOwner {
        // только owner!
    }
}
```

- `transferOwnership(newOwner)` — передать владение другому
- `renounceOwnership()` — отказаться от владения навсегда
- **Ownable2Step** — safer-версия: новый owner должен подтвердить принятие (`acceptOwnership()`)

**Проблема Ownable:** один ключ = одна точка отказа. Для серьёзных проектов используй RBAC.

#### AccessControl — ролевой доступ (RBAC)

Role-Based Access Control: роли как «должности» с разными правами.

```solidity
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract TokenWithRoles is ERC20, AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BURNER_ROLE = keccak256("BURNER_ROLE");

    constructor(address minter, address burner)
        ERC20("MyToken", "MTK")
    {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MINTER_ROLE, minter);
        _grantRole(BURNER_ROLE, burner);
    }

    function mint(address to, uint256 amount) public onlyRole(MINTER_ROLE) {
        _mint(to, amount);
    }

    function burn(address from, uint256 amount) public onlyRole(BURNER_ROLE) {
        _burn(from, amount);
    }
}
```

> **Как читать `bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE")`:** «преврати человекочитаемое имя роли в уникальный 32-байтовый идентификатор — хеш, который Solidity будет использовать для проверок `onlyRole(MINTER_ROLE)`». Мнемоника: `keccak256("ИМЯ_РОЛИ")` = строку в bytes32; роль — это просто хеш, а не enum.

**Ключевые концепты:**

- `DEFAULT_ADMIN_ROLE` — супер-админ, может назначать/снимать любые роли
- Роль = `bytes32` (хеш от названия, например `keccak256("MINTER_ROLE")`)
- Каждый адрес может иметь несколько ролей
- `grantRole(role, account)` / `revokeRole(role, account)` — динамическое управление
- **AccessControlDefaultAdminRules** — безопасная версия с 2-шаговой передачей админа и задержкой

**TimelockController** — прокси с временной задержкой. Действия проходят стадии: предложение → ожидание (например, 48 часов) → исполнение. Пользователи успевают выйти, если им не нравится изменение.

---

### 4. Upgradeable-контракты: обновление логики

Смарт-контракты в блокчейне неизменяемы... если не использовать **proxy-паттерн**.

**Идея:** разделяем контракт на две части:
- **Proxy** — хранит состояние (балансы, storage), его адрес не меняется
- **Implementation** — содержит логику, может быть заменён на новую версию

OpenZeppelin поддерживает два типа прокси:

| Тип | Как работает | Плюсы | Минусы |
|---|---|---|---|
| **Transparent Proxy** | Админ-адрес всегда вызывает через proxy; пользователи — напрямую | Простой, проверенный | Дороже gas, админ проверяется каждый вызов |
| **UUPS** (Universal Upgradeable Proxy Standard) | Логика обновления в самом implementation | Дешевле gas (проверка только при upgrade) | Сложнее в реализации, риск забыть вызвать upgrade-функцию |

**Установка плагина Hardhat для upgrades:**

```bash
npm install --save-dev @openzeppelin/hardhat-upgrades
```

**Деплой через UUPS:**

```solidity
// V1
import {UUPSUpgradeable} from "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import {OwnableUpgradeable} from "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";

contract MyContractV1 is Initializable, UUPSUpgradeable, OwnableUpgradeable {
    function initialize() public initializer {
        __Ownable_init(msg.sender);
        __UUPSUpgradeable_init();
    }

    function _authorizeUpgrade(address newImplementation)
        internal
        override
        onlyOwner
    {}
}
```

```javascript
// deploy.js (Hardhat)
const { ethers, upgrades } = require("hardhat");

const MyContract = await ethers.getContractFactory("MyContractV1");
const proxy = await upgrades.deployProxy(MyContract, [], {
    kind: "uups",
    initializer: "initialize",
});
await proxy.waitForDeployment();
```

> **Как читать `upgrades.deployProxy(MyContract, [], { kind: "uups", initializer: "initialize" })`:** «задеплой прокси-контракт, который делегирует все вызовы на логику `MyContract`, а начальную инициализацию сделай через функцию `initialize` — потому что у обновляемых контрактов конструктор не работает». Мнемоника: прокси = вечная обёртка с неизменным адресом, реализация = сменная начинка, `initializer` = конструктор на стероидах.

**Важные правила upgradeable-контрактов:**

- **Не используй конструктор** — используй `initialize()` с модификатором `initializer`
- **Не меняй порядок переменных** в storage между версиями
- **Не удаляй переменные** — только добавляй новые в конец
- **Пакет `@openzeppelin/contracts-upgradeable`** — специальные версии, где конструкторы заменены на `__Xxx_init()`

---

### 5. SafeERC20: безопасная работа с токенами

Стандарт ERC-20 не требует, чтобы `transfer` и `transferFrom` возвращали `bool`. Некоторые токены (например, USDT) не возвращают ничего. Без `SafeERC20` твой контракт может сломаться на таких токенах.

```solidity
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract Vault {
    using SafeERC20 for IERC20;

> **Как читать `using SafeERC20 for IERC20;` + `token.safeTransfer(to, amount)`:** «прикрепи безопасные обёртки к стандартному интерфейсу токена: теперь `safeTransfer` работает даже с „неправильными“ токенами вроде USDT, которые не возвращают `bool` после перевода». Мнемоника: `SafeERC20` = страховка от кривых реализаций ERC-20; всегда используй `safeTransfer`, а не `transfer`.

    function withdraw(IERC20 token, address to, uint256 amount) external {
        // Безопасно: работает и с USDT, и с DAI
        token.safeTransfer(to, amount);
    }
}
```

**Методы SafeERC20:**
- `safeTransfer(token, to, amount)`
- `safeTransferFrom(token, from, to, amount)`
- `safeApprove(token, spender, amount)` — безопаснее, чем обычный approve
- `safeIncreaseAllowance(token, spender, amount)` — избегает race condition approve-фронтраннинга
- `safeDecreaseAllowance(token, spender, amount)`

**Правило:** всегда используй `SafeERC20` при взаимодействии с внешними токенами. Никогда не делай `token.transfer()` напрямую.

---

### 6. Утилиты

#### Address — проверки адресов и вызовы

```solidity
import {Address} from "@openzeppelin/contracts/utils/Address.sol";

// Проверить, что адрес — контракт
Address.isContract(someAddress);

// Отправить ETH через call (безопаснее, чем .transfer())
Address.sendValue(payable(recipient), amount);

// Вызвать функцию контракта — вернёт ошибку с bubbling
Address.functionCall(target, data);
Address.functionDelegateCall(target, data);
```

#### Strings — работа со строками

```solidity
import {Strings} from "@openzeppelin/contracts/utils/Strings.sol";

Strings.toString(123);         // "123"
Strings.toHexString(address);  // "0xabcd..."
Strings.toHexString(42);       // "0x2a"
Strings.equal(str1, str2);     // сравнение строк (газ-эффективно)
```

#### Math — безопасная арифметика

Solidity 0.8+ имеет встроенные overflow-проверки, но OpenZeppelin даёт дополнительные утилиты:

```solidity
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";

Math.max(a, b);         // максимум
Math.min(a, b);         // минимум
Math.average(a, b);     // среднее без overflow
Math.ceilDiv(a, b);     // деление с округлением вверх
Math.sqrt(x);           // квадратный корень
Math.log2(x);           // логарифм по основанию 2
Math.log10(x);          // логарифм по основанию 10
```

**SignedMath** — `abs`, `average`, `max`, `min` для `int256`.

---

### 7. Безопасность (Security)

#### ReentrancyGuard — защита от повторных вызовов

Reentrancy — атака #1 в смарт-контрактах. Злоумышленник вызывает твою функцию, она вызывает его контракт, а тот — снова твою функцию до завершения первой.

```solidity
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract Vault is ReentrancyGuard {
    mapping(address => uint256) public balances;

    function withdraw() external nonReentrant {
        uint256 amount = balances[msg.sender];
        balances[msg.sender] = 0;

        (bool success, ) = msg.sender.call{value: amount}("");
        require(success);
        // Без nonReentrant: атакующий мог бы повторно вызвать withdraw
        // через fallback до обнуления balances
    }
}
```

- `nonReentrant` — блокирует повторный вход в ту же функцию
- `_nonReentrantBefore()` / `_nonReentrantAfter()` — ручное управление для сложных случаев

#### Pausable — экстренная пауза

Возможность приостановить критические операции. Например, если обнаружен баг.

```solidity
import {Pausable} from "@openzeppelin/contracts/utils/Pausable.sol";

contract MyToken is ERC20, Pausable {
    constructor() ERC20("MyToken", "MTK") {}

    function transfer(address to, uint256 amount)
        public
        override
        whenNotPaused
        returns (bool)
    {
        return super.transfer(to, amount);
    }

    function pause() external onlyOwner {
        _pause();   // эмитит Paused
    }

    function unpause() external onlyOwner {
        _unpause(); // эмитит Unpaused
    }
}
```

Модификаторы:
- `whenNotPaused` — требует, чтобы контракт был активен
- `whenPaused` — требует, чтобы контракт был на паузе

---

## Уровень 3: 🧠 Продвинутые темы

### ERC-20 Permit — безгазовые approval

Обычный процесс: `approve(spender, amount)` → жди транзакцию → `transferFrom`. ERC-20 Permit заменяет первую транзакцию подписью вне цепи (EIP-2612).

```solidity
import {ERC20Permit} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";

contract MyToken is ERC20, ERC20Permit {
    constructor() ERC20("MyToken", "MTK") ERC20Permit("MyToken") {}
}
```

Пользователь подписывает сообщение (бесплатно), а кто угодно может отправить `permit()` — и approval готов. Экономия газа для пользователя.

### ERC-1155 — мульти-токены

Один контракт управляет и fungible, и non-fungible токенами. Один NFT и 1000 золотых монет — в одном контракте.

```solidity
import {ERC1155} from "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";

contract GameItems is ERC1155 {
    uint256 public constant GOLD = 0;
    uint256 public constant SWORD = 1;

    constructor() ERC1155("https://game.example/api/item/{id}.json") {
        _mint(msg.sender, GOLD, 1000, "");   // 1000 золотых (fungible)
        _mint(msg.sender, SWORD, 1, "");     // 1 меч (NFT, quantity=1)
    }
}
```

**Преимущество:** `safeBatchTransferFrom` — отправить несколько типов токенов в одной транзакции.

### Контракты Governance

OpenZeppelin даёт полный набор для DAO-голосований:

- `Governor` + `GovernorCountingSimple` — создание и подсчёт proposal'ов
- `GovernorVotes` — голосование токенами (привязка к ERC20Votes)
- `GovernorTimelockControl` — интеграция с TimelockController
- `Tally` — off-chain подсчёт голосов (экономия газа)

### Wizard — генератор контрактов

Не хочешь писать руками? [wizard.openzeppelin.com](https://wizard.openzeppelin.com/) — выбери ERC-20/ERC-721/ERC-1155/Governor, отметь галками фичи, получи готовый код.

---

## Уровень 4: 🎓 Architectural Decisions

### Почему наследование, а не библиотеки?

OpenZeppelin Contracts — **фреймворк на наследовании**. Ты наследуешь контракт и опционально переопределяешь функции (`virtual` / `override`). Не библиотеки, которые вызываешь через `delegatecall`. Причины:

- **Газовая эффективность:** прямые вызовы дешевле delegatecall
- **Прозрачность:** код твоего контракта — это весь код (Flat, проверяемый в Etherscan)
- **Компилятор всё проверяет:** никаких сюрпризов с layout'ом памяти

### Аудит и версионирование

OpenZeppelin использует **семантическое версионирование**:

- `@openzeppelin/contracts@5.x` — MAJOR: breaking changes (меняют storage layout)
- `@openzeppelin/contracts@5.0.x` — MINOR: новые фичи, обратная совместимость
- NPM-теги: `latest` (аудирован), `dev` (финальный, но без аудита), `next` (в разработке)

**Каждый major-релиз проходит независимый аудит.** Баунти-программа на Immunefi.

### Выбор: Transparent Proxy vs UUPS

```
Transparent Proxy:
  User → Proxy → Implementation
  Admin → Proxy → ProxyAdmin → Implementation (дороже, но проще)

UUPS:
  User → Proxy → Implementation (как обычно)
  Upgrade: Proxy → Implementation.upgradeTo(...) (логика в implementation)
```

**Когда UUPS:**
- Хочешь экономить газ
- Готов следить, чтобы `_authorizeUpgrade` не потерялся при наследовании

**Когда Transparent:**
- Предпочитаешь простоту и проверенность
- Не критично дороже на ~2100 gas за вызов

### Принцип наименьших привилегий

Не давай `DEFAULT_ADMIN_ROLE` всем подряд. Используй granular-роли:

```
DEFAULT_ADMIN_ROLE: multisig (2-of-3), только назначает роли
MINTER_ROLE:        контракт бриджа (автоматический)
BURNER_ROLE:        multisig (ручное сжигание)
PAUSER_ROLE:        дежурный бот (может поставить паузу)
```

---

## Быстрый старт (чит-лист)

```bash
# 1. Установка
npm install @openzeppelin/contracts

# 2. ERC-20 токен
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";

# 3. ERC-721 NFT
import {ERC721URIStorage} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

# 4. Контроль доступа
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";

# 5. Безопасность
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {Pausable} from "@openzeppelin/contracts/utils/Pausable.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

# 6. Upgradeable
npm install @openzeppelin/contracts-upgradeable @openzeppelin/hardhat-upgrades

# 7. Wizard (генератор кода)
# https://wizard.openzeppelin.com/
```

## Связанные страницы

- [[wiki/ERC-20-стандарт-токенов]] — детальный разбор стандарта ERC-20
- [[wiki/ERC-721-NFT-стандарт]] — детальный разбор NFT-стандарта
- [[wiki/Solidity-основы]] — синтаксис Solidity, необходимый для понимания контрактов
- [[wiki/Hardhat-среда-разработки]] — среда разработки, в которой используется OpenZeppelin

## Источники

1. [OpenZeppelin Contracts 5.x Documentation](https://docs.openzeppelin.com/contracts/5.x/) — официальная документация
2. [OpenZeppelin Access Control Guide](https://docs.openzeppelin.com/contracts/5.x/access-control) — гайд по Ownable и AccessControl
3. [OpenZeppelin Tokens Guide](https://docs.openzeppelin.com/contracts/5.x/tokens) — ERC-20/ERC-721/ERC-1155
4. [OpenZeppelin ERC-20 Guide](https://docs.openzeppelin.com/contracts/5.x/erc20)
5. [OpenZeppelin ERC-721 Guide](https://docs.openzeppelin.com/contracts/5.x/erc721)
6. [OpenZeppelin Upgrades Plugins](https://docs.openzeppelin.com/upgrades-plugins/1.x/) — Transparent/UUPS proxy
7. [OpenZeppelin GitHub Repository](https://github.com/OpenZeppelin/openzeppelin-contracts)
8. [EIP-1967: Proxy Storage Slots](https://eips.ethereum.org/EIPS/eip-1967) — стандарт прокси-слотов
