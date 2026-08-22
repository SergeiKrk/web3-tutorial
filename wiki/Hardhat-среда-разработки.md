---
title: "Hardhat — среда разработки смарт-контрактов"
date: 2026-07-19
tags: [web3, solidity, hardhat, инструменты]
category: tool
---

# Hardhat — среда разработки смарт-контрактов

> Hardhat — это **фреймворк полного цикла** для разработки смарт-контрактов на Ethereum. Компиляция, тестирование, деплой, отладка и скрипты — всё в одном инструменте.

**Документация:** [hardhat.org](https://hardhat.org/) | **Репозиторий:** [github.com/NomicFoundation/hardhat](https://github.com/NomicFoundation/hardhat)

---

## Уровень 1: 🍵 Для новичка (что это и зачем)

Hardhat — это как **create-react-app + Jest + Webpack для блокчейна**. Ты пишешь Solidity-код, а Hardhat:

- **Компилирует** его в байт-код (то, что понимает EVM — Ethereum Virtual Machine)
- **Запускает локальный блокчейн** у тебя на машине (Hardhat Network) — мгновенный, бесплатный, с 10 000 тестовых ETH
- **Прогоняет тесты** — на JavaScript/TypeScript, с привычными Chai-ассертами
- **Деплоит** контракты в тестовые сети (Sepolia) или mainnet
- **Даёт консоль** — интерактивный REPL, где можно дёргать контракты на лету

**Аналогия:** если Solidity — это язык (как JavaScript), то Hardhat — это среда выполнения (как Node.js). Без Hardhat ты бы компилировал через solc вручную, деплоил сырыми транзакциями и отлаживал через print-дебаг.

### Минимальный старт за 2 минуты

```bash
mkdir my-project && cd my-project
npm init -y
npm install --save-dev hardhat
npx hardhat init          # выбрать «Create a JavaScript project»
npx hardhat compile       # скомпилировать
npx hardhat test          # прогнать тесты
```

Всё. Ты уже в экосистеме Hardhat. Дальше — копай вглубь.

---

## Уровень 2: 🔧 Рабочий минимум (каждодневные операции)

### Установка

Устанавливается **локально в проект** (не глобально). Это важно: версия Hardhat фиксируется в `package.json`, и проект воспроизводим.

```bash
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
```

`@nomicfoundation/hardhat-toolbox` — батарейка в комплекте: тянет ethers.js, hardhat-chai-matchers, hardhat-network-helpers, typechain и ещё 10 плагинов. **Рекомендуется всегда.**

### Инициализация проекта

```bash
npx hardhat init
```

Hardhat предложит 3 варианта:
- **JavaScript project** — стандарт, для большинства
- **TypeScript project** — если хочешь типы (рекомендую)
- **Empty config** — только `hardhat.config.js`, без примера

После инициализации структура:

```
my-project/
├── contracts/           ← смарт-контракты (.sol)
│   └── Lock.sol         ← пример от Hardhat
├── ignition/            ← модули деплоя (Hardhat Ignition — новый способ)
│   └── modules/
├── test/                ← тесты (.js/.ts)
│   └── Lock.js
├── hardhat.config.js    ← главный конфиг
└── package.json
```

### hardhat.config.js — центр управления

```javascript
require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.24",                    // версия компилятора
  networks: {
    hardhat: {},                          // локальная сеть (автоматически)
    sepolia: {
      url: `https://sepolia.infura.io/v3/${INFURA_KEY}`,
      accounts: [PRIVATE_KEY]             // НИКОГДА не коммитить ключи!
    }
  }
};
```

**Важно:** для переменных окружения используй `dotenv`:

```bash
npm install --save-dev dotenv
```

```javascript
require("dotenv").config();
// ...
accounts: [process.env.PRIVATE_KEY]
```

### Компиляция

```bash
npx hardhat compile
```

Что происходит:
1. `solc` (Solidity-компилятор) — скачивается автоматически, первая компиляция дольше
2. Артефакты кладутся в `artifacts/contracts/<Имя>.sol/<Имя>.json`
3. В артефактах: ABI (интерфейс), байт-код, AST, source map
4. Кеш: `cache/` — повторная компиляция почти мгновенная

```bash
npx hardhat compile --force   # перекомпилировать всё, игнорируя кеш
```

### Hardhat Network — локальный блокчейн

Запускается **автоматически** при `npx hardhat test` или `npx hardhat run`. Не нужен Ganache, не нужен Docker.

```bash
npx hardhat node              # явно запустить ноду (HTTP: localhost:8545)
```

Возможности:
- **20 предустановленных аккаунтов** с 10 000 ETH каждый (мнемоника: `test test test...`)
- **Мгновенный майнинг** — транзакции подтверждаются сразу
- **console.log в Solidity** — `import "hardhat/console.sol";` и вызывай `console.log(x)`
- **Форкинг mainnet** — копирует состояние Ethereum на твой локальный блок:

```javascript
networks: {
  hardhat: {
    forking: {
      url: `https://mainnet.infura.io/v3/${INFURA_KEY}`,
    }
  }
}
```

### Деплой в тестовую сеть (Sepolia)

Sepolia — основная тестовая сеть Ethereum (заменила Goerli). Для деплоя нужны:
1. **RPC-URL** — Infura, Alchemy или публичный
2. **Приватный ключ** аккаунта с Sepolia ETH
3. **Тестовые ETH** — [sepoliafaucet.com](https://sepoliafaucet.com/) или кран Alchemy

**Скрипт деплоя** (`scripts/deploy.js`):

```javascript
const hre = require("hardhat");

async function main() {
  // Получаем фабрику контракта
  const Counter = await hre.ethers.getContractFactory("Counter");

> **Как читать `hre.ethers.getContractFactory("Counter")`:** «найди скомпилированный контракт по имени и подготовь фабрику для его развёртывания — это как взять чертёж перед стройкой». Мнемоника: `getContractFactory` = взял чертёж, `deploy()` = построил дом на блокчейне.

  // Деплоим (это создаёт транзакцию)
  const counter = await Counter.deploy();

  // Ждём подтверждения
  await counter.waitForDeployment();

  console.log(`Counter deployed to: ${counter.target}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

**Запуск:**

```bash
npx hardhat run scripts/deploy.js --network sepolia
```

Проверить деплой можно на [sepolia.etherscan.io](https://sepolia.etherscan.io/) — вставь адрес контракта.

**Верификация контракта** (чтобы код был виден на Etherscan):

```bash
npm install --save-dev @nomicfoundation/hardhat-verify
npx hardhat verify --network sepolia DEPLOYED_ADDRESS
```

### Тестирование (Chai + hardhat-chai-matchers)

Hardhat использует **Mocha** + **Chai** + специальные Ethereum-ассерты. Файлы тестов лежат в `test/`.

**Базовый тест для Counter.sol** (разбираем наш контракт из ``raw/Counter.sol``):

```javascript
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Counter", function () {
  let counter, owner, other;

  beforeEach(async function () {
    [owner, other] = await ethers.getSigners();

    const Counter = await ethers.getContractFactory("Counter");
    counter = await Counter.deploy();
    await counter.waitForDeployment();
  });

  it("должен начинаться с нуля", async function () {
    expect(await counter.getCount()).to.equal(0);
  });

  it("должен увеличивать счётчик", async function () {
    await counter.increment();
    expect(await counter.getCount()).to.equal(1);

    await counter.increment();
    expect(await counter.getCount()).to.equal(2);
  });

  it("должен уменьшать счётчик", async function () {
    await counter.increment();
    await counter.increment();
    await counter.decrement();
    expect(await counter.getCount()).to.equal(1);
  });

  it("только owner может сбросить счётчик", async function () {
    // Ожидаем revert от не-owner
    await expect(
      counter.connect(other).reset()
    ).to.be.revertedWith("Only owner can call this");

> **Как читать `counter.connect(other).reset()`:** «вызови функцию `reset` от имени другого аккаунта `other` — Hardhat притворится, что транзакцию отправил `other`, а не деплойер». Мнемоника: `.connect(аккаунт)` = надень чужую шляпу и действуй от его лица в тесте.

    // Owner может
    await counter.connect(owner).reset();
    expect(await counter.getCount()).to.equal(0);
  });

  it("должен эмитить событие Incremented", async function () {
    await expect(counter.increment())
      .to.emit(counter, "Incremented")
      .withArgs(1);
  });

  it("должен эмитить событие Reset с правильными параметрами", async function () {
    await counter.increment();
    await counter.increment(); // count = 2

    await expect(counter.reset())
      .to.emit(counter, "Reset")
      .withArgs(owner.address, 2);
  });
});
```

**Ключевые ассерты hardhat-chai-matchers:**

| Ассерт | Для чего |
|--------|----------|
| `expect(tx).to.emit(contract, "Event")` | Проверка событий |
| `expect(tx).to.be.revertedWith("msg")` | Ожидание revert |
| `expect(tx).to.be.revertedWithoutReason()` | Revert без сообщения |
| `expect(tx).to.changeEtherBalance(addr, delta)` | Изменение ETH-баланса |
| `expect(tx).to.changeTokenBalance(token, addr, delta)` | Изменение токен-баланса |
| `expect(value).to.be.properHex(length)` | Валидный hex |

**Запуск тестов:**

```bash
npx hardhat test                          # все тесты
npx hardhat test test/Counter.js          # конкретный файл
npx hardhat test --grep "должен увеличивать"  # по названию
```

### Hardhat Console — интерактивная песочница

```bash
npx hardhat console
```

Открывает Node.js REPL с подключённой сетью Hardhat. Можно на лету деплоить контракты и вызывать функции:

```javascript
// Внутри консоли:
const [owner] = await ethers.getSigners();

const Counter = await ethers.getContractFactory("Counter");
const counter = await Counter.deploy();
await counter.waitForDeployment();

await counter.increment();
(await counter.getCount()).toString();  // "1"

// Быстрая проверка revert:
await counter.connect(ethers.ZeroAddress).reset();
// Error: VM Exception... "Only owner can call this"
```

**Консоль с подключением к Sepolia:**

```bash
npx hardhat console --network sepolia
```

### Скрипты — автоматизация задач

Скрипты в `scripts/` делают что угодно: деплой, вызов функций, проверку состояния.

```javascript
// scripts/check-counter.js
const hre = require("hardhat");

async function main() {
  const counter = await hre.ethers.getContractAt(
    "Counter",
    "0x..."  // адрес задеплоенного контракта
  );
  const count = await counter.getCount();
  console.log(`Текущее значение: ${count}`);
}

main().catch(console.error);
```

```bash
npx hardhat run scripts/check-counter.js --network sepolia
```

---

## Уровень 3: 🧠 Понимание (как это устроено внутри)

### Архитектура Hardhat

Hardhat — модульная система. Ядро минимально, всё остальное — плагины:

```
Hardhat Runtime Environment (HRE)
├── hardhat-core           ← компилятор, нода, таск-раннер
├── Плагины (npm-пакеты)
│   ├── @nomicfoundation/hardhat-toolbox   ← батарейка
│   ├── @nomicfoundation/hardhat-verify    ← верификация на Etherscan
│   ├── @nomicfoundation/hardhat-ignition  ← декларативный деплой
│   ├── hardhat-gas-reporter              ← отчёт по газу
│   └── solidity-coverage                 ← покрытие тестами
└── Твои скрипты и тесты
```

**HRE (Hardhat Runtime Environment)** — глобальный объект, доступный в скриптах и тестах. Содержит `ethers`, `network`, `artifacts`, `config`, `run`. Импортируется как `const hre = require("hardhat")`.

### Компиляция: что внутри

```
.sol → solc → байт-код (creation + runtime) + ABI + source map
       ↓
  artifacts/contracts/Имя.sol/Имя.json:
    {
      "abi": [...],              // интерфейс контракта
      "bytecode": "0x6080...",   // байт-код для деплоя
      "deployedBytecode": "...", // байт-код который живёт на chain
      "sourceMap": "...",        // маппинг байт-код → исходник (для отладки)
    }
```

**Creation bytecode** содержит constructor-логику — выполняется один раз при деплое. **Deployed (runtime) bytecode** — то, что хранится в блокчейне и выполняется при вызовах.

### Hardhat Network: как работает локальный блокчейн

Hardhat Network — это **in-process EVM**, написанный на TypeScript. Не отдельный процесс (как ganache), а внутри Node.js:

- **Мгновенный майнинг:** по умолчанию каждый вызов майнит блок сразу (auto-mining)
- **Интервальный майнинг:** задаёшь интервал в секундах или вручную через `evm_mine`
- **Снэпшоты:** `await network.provider.send("evm_snapshot")` / `evm_revert` — git stash для блокчейна
- **impersonate:** вызывай функции от имени любого адреса — `await network.provider.request({method: "hardhat_impersonateAccount", params: ["0x..."]})`

```javascript
// В тесте: заморозить время
await network.provider.send("evm_increaseTime", [3600]); // +1 час
await network.provider.send("evm_mine");                 // майним блок
```

### Hardhat Ignition (новый способ деплоя)

На смену `scripts/deploy.js` пришёл **Hardhat Ignition** — декларативный подход:

```typescript
// ignition/modules/CounterModule.js
const { buildModule } = require("@nomicfoundation/hardhat-ignition/modules");

module.exports = buildModule("CounterModule", (m) => {
  const counter = m.contract("Counter");

  return { counter };
});

> **Как читать `buildModule("CounterModule", (m) => { const counter = m.contract("Counter"); return { counter }; })`:** «опиши декларативно, *что* задеплоить: модуль — это именованный набор контрактов; `m.contract()` регистрирует контракт, возвращаемый объект передаёт результаты зависимым модулям». Мнемоника: Ignition = скажи *что* деплоить, а не *как*; повторный запуск не создаст дубликат.

```
```bash
npx hardhat ignition deploy ignition/modules/CounterModule.js --network sepolia
```

Преимущества Ignition:
- **Декларативность:** описываешь *что* задеплоить, а не *как*
- **Идемпотентность:** повторный деплой не создаст дубликат
- **Зависимости:** один модуль может ссылаться на результат другого
- **Верификация:** автоматическая после деплоя (`--verify`)

### Система тасков (Tasks)

Таски — аналог npm scripts, но с аргументами и типами. Живут в `hardhat.config.js` или `tasks/`.

```javascript
task("accounts", "Показать список аккаунтов").setAction(async (_, hre) => {
  const accounts = await hre.ethers.getSigners();
  for (const acc of accounts) {
    console.log(acc.address, ":", ethers.formatEther(
      await hre.ethers.provider.getBalance(acc.address)
    ), "ETH");
  }
});

> **Как читать `task("accounts", "описание").setAction(async (_, hre) => { ... })`:** «зарегистрируй новую команду `npx hardhat accounts`, которая выполнит эту async-функцию с доступом ко всему окружению Hardhat (hre)». Мнемоника: `task` = npm-скрипт с аргументами, но с полным доступом к блокчейну и контрактам.

```
```bash
npx hardhat accounts
```

**С параметрами:**

```javascript
task("counter-status", "Проверить счётчик")
  .addParam("address", "Адрес контракта")
  .setAction(async ({ address }, hre) => {
    const counter = await hre.ethers.getContractAt("Counter", address);
    console.log("Count:", (await counter.getCount()).toString());
  });
```

```bash
npx hardhat counter-status --address 0x... --network sepolia
```

### Gas-оптимизация

```
npx hardhat test                   # обычные тесты
REPORT_GAS=true npx hardhat test   # с отчётом по газу (hardhat-gas-reporter)
```

hardhat-gas-reporter показывает таблицу: какая функция сколько газа тратит. Критично для продакшена.

### Обновление до Hardhat 3

Hardhat v3 (вышел в 2025) принёс:
- **Hardhat Ignition** как основной способ деплоя (замена scripts deploy)
- **Ускоренную компиляцию** через кеширование на уровне файлов
- **Встроенную поддержку ESM** (import/export вместо require)
- **Viem** как альтернативу ethers.js (через `@nomicfoundation/hardhat-viem`)

Чтобы обновиться:
```bash
npm install --save-dev hardhat@latest @nomicfoundation/hardhat-toolbox@latest
```

---

## Уровень 4: 🏗️ Разбор Counter.sol через Hardhat

Контракт ``raw/Counter.sol`` — наш учебный пример. Разберём его **полный цикл разработки** через Hardhat.

### Код контракта

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Counter {
    uint256 public count;
    address public owner;

    event Incremented(uint256 newValue);
    event Decremented(uint256 newValue);
    event Reset(address indexed by, uint256 oldValue);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }

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
```

### Шаг 1: Инициализация проекта под Counter

```bash
mkdir counter-project && cd counter-project
npm init -y
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
npx hardhat init       # выбрать JavaScript
```

Копируем `Counter.sol` в `contracts/`, удаляем `Lock.sol`.

### Шаг 2: Конфигурация

```javascript
// hardhat.config.js
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: "0.8.20",   // совпадает с прагмой в контракте!
  networks: {
    sepolia: {
      url: `https://sepolia.infura.io/v3/${process.env.INFURA_KEY}`,
      accounts: [process.env.PRIVATE_KEY],
    }
  }
};
```

### Шаг 3: Компиляция

```bash
npx hardhat compile
# → Compiled 1 Solidity file successfully
```

После компиляции в `artifacts/contracts/Counter.sol/Counter.json` можно найти:
- **ABI** — JSON с описанием функций (нужен фронтенду)
- **bytecode** — hex-строка, которая загружается в блокчейн

### Шаг 4: Тестирование (полный набор)

Файл `test/Counter.js`:

```javascript
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Counter — полный цикл", function () {
  let counter, owner, other;

  beforeEach(async function () {
    [owner, other] = await ethers.getSigners();
    const Counter = await ethers.getContractFactory("Counter");
    counter = await Counter.deploy();
    await counter.waitForDeployment();
  });

  describe("Развёртывание", function () {
    it("owner = деплойер", async function () {
      expect(await counter.owner()).to.equal(owner.address);
    });

    it("начальное значение = 0", async function () {
      expect(await counter.getCount()).to.equal(0);
    });
  });

  describe("increment()", function () {
    it("увеличивает на 1", async function () {
      await counter.increment();
      expect(await counter.getCount()).to.equal(1);
    });

    it("эмитит Incremented с новым значением", async function () {
      await expect(counter.increment())
        .to.emit(counter, "Incremented")
        .withArgs(1);
    });

    it("может вызывать кто угодно", async function () {
      await counter.connect(other).increment();
      expect(await counter.getCount()).to.equal(1);
    });
  });

  describe("decrement()", function () {
    it("уменьшает на 1", async function () {
      await counter.increment();
      await counter.increment(); // 2
      await counter.decrement(); // 1
      expect(await counter.getCount()).to.equal(1);
    });

    it("может уйти в underflow (опасно!)", async function () {
      // count = 0, decrement → ошибка в Solidity 0.8+ (built-in overflow check)
      await expect(counter.decrement()).to.be.revertedWithPanic(0x11);
      // 0x11 = арифметическое переполнение
    });
  });

  describe("reset()", function () {
    it("сбрасывает в 0", async function () {
      await counter.increment();
      await counter.increment(); // 2
      await counter.reset();
      expect(await counter.getCount()).to.equal(0);
    });

    it("только owner", async function () {
      await expect(
        counter.connect(other).reset()
      ).to.be.revertedWith("Only owner can call this");
    });

    it("эмитит Reset со старым значением", async function () {
      await counter.increment();
      await counter.increment();
      await expect(counter.reset())
        .to.emit(counter, "Reset")
        .withArgs(owner.address, 2);
    });
  });

  describe("getCount()", function () {
    it("view-функция: не тратит газ при внешнем вызове", async function () {
      const tx = await counter.getCount();
      // view-функция, вызванная через ethers call, не создаёт транзакцию
    });
  });
});
```

Запускаем:

```bash
npx hardhat test
```

### Шаг 5: Деплой в Sepolia

`scripts/deploy.js`:

```javascript
const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Деплой с адреса:", deployer.address);

  const Counter = await hre.ethers.getContractFactory("Counter");
  const counter = await Counter.deploy();
  await counter.waitForDeployment();

  console.log("Counter задеплоен по адресу:", counter.target);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

```bash
npx hardhat run scripts/deploy.js --network sepolia
```

### Шаг 6: Проверка через консоль

```bash
npx hardhat console --network sepolia
```

```javascript
const counter = await ethers.getContractAt("Counter", "0x...");
(await counter.getCount()).toString();
// → "0"

await counter.increment();
(await counter.getCount()).toString();
// → "1"
```

### Чему учит этот пример

Counter.sol демонстрирует **все ключевые концепции Solidity**, развёрнутые через Hardhat:

| Концепция | В контракте | В тестах |
|-----------|------------|----------|
| **Состояние (storage)** | `count`, `owner` | Проверка начальных значений |
| **Модификатор** | `onlyOwner` | `revertedWith("Only owner...")` |
| **События** | `Incremented`, `Decremented`, `Reset` | `.to.emit().withArgs()` |
| **View-функция** | `getCount()` | Вызов без газа |
| **msg.sender** | `constructor`, `onlyOwner` | `.connect(other)` — смена отправителя |
| **Access Control** | `require(msg.sender == owner)` | Тест на несанкционированный вызов |
| **SafeMath (встроен)** | underflow при decrement от 0 | `revertedWithPanic(0x11)` |

---

## Связанное
- [[wiki/OpenZeppelin-безопасные-контракты]] — безопасные контракты для Hardhat-проектов


- [[wiki/Solidity-основы]] — синтаксис, типы, события, модификаторы
- [[wiki/ERC-20-стандарт-токенов]] — следующий шаг: токены
- [[wiki/Блокчейн-как-это-работает]] — база: газ, транзакции, консенсус
- [[wiki/Словарь-web3]] — термины (EVM, ABI, байт-код, gas)
- [[wiki/Сравнение-ethers-viem-wagmi]] — библиотеки для вызова контрактов с фронтенда
- [[wiki/Главная]] — дорожная карта обучения

---

## Источники

- [hardhat.org/docs](https://hardhat.org/docs) — официальная документация (v3)
- [hardhat.org/hardhat-runner/docs/guides/project-setup](https://hardhat.org/hardhat-runner/docs/guides/project-setup)
- [@nomicfoundation/hardhat-chai-matchers](https://hardhat.org/hardhat-chai-matchers/docs/overview) — документация по ассертам
- [hardhat.org/hardhat-network/docs/overview](https://hardhat.org/hardhat-network/docs/overview) — Hardhat Network
- [hardhat.org/ignition/docs/getting-started](https://hardhat.org/ignition/docs/getting-started) — Hardhat Ignition
