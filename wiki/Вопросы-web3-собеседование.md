---
title: "Вопросы web3-собеседования: фронтендер"
date: 2026-07-19
tags: [web3, собеседование, карьера]
category: reference
source_count: 0
---

# Вопросы web3-собеседования: фронтендер

Развёрнутые ответы на реальные вопросы, которые задают React-фронтендерам на web3-позициях. 30 вопросов с уровнями сложности — от Junior до Senior.

**Связанное:** [[wiki/web3-фронтендер-план-трудоустройства]], [[wiki/DeFi-для-фронтендера]], [[wiki/wagmi-RainbowKit-фронтенд]], [[wiki/Паттерны-транзакций-React]]

---

## 🌐 Блокчейн-основы

---

## 1. Объясни, как работает блокчейн на примере Ethereum

**Уровень:** Junior/Middle

### Что спрашивают на самом деле

Проверяют не просто «заучил определение», а понимаешь ли ты фундаментальные механизмы, которые влияют на твою работу фронтендера: почему транзакции не мгновенные, что такое финальность, почему газ дорогой.

### Развёрнутый ответ

Блокчейн Ethereum — это распределённая машина состояний. Представь глобальный компьютер, который все участники сети вычисляют синхронно.

**Структура:**
```
Block N-1               Block N                  Block N+1
┌──────────────┐       ┌──────────────┐         ┌──────────────┐
│ prevHash     │◄──────│ prevHash     │◄────────│ prevHash     │
│ timestamp    │       │ timestamp    │         │ timestamp    │
│ stateRoot    │       │ stateRoot    │         │ stateRoot    │
│ txs[...]     │       │ txs[...]     │         │ txs[...]     │
└──────────────┘       └──────────────┘         └──────────────┘
```

**Ключевые концепции:**

1. **Блок** — набор транзакций + хеш предыдущего блока. Измени хоть бит в блоке N-1 → все последующие блоки станут невалидными. Это и есть «неизменяемость».

2. **Консенсус (Proof of Stake)** — валидаторы ставят ETH (stake) и по очереди предлагают блоки. Если валидатор жульничает — его stake сжигается (slashing). Финальность наступает через 2 эпохи (~12.8 минут).

3. **Состояние (State)** — не просто «балансы», а полное дерево всех аккаунтов, контрактов и их storage. State root в заголовке блока — это как «снапшот всего».

4. **EVM (Ethereum Virtual Machine)** — среда выполнения смарт-контрактов. Каждая нода исполняет транзакции и получает одинаковый результат. Детерминированность — ключевое свойство.

**Почему это важно фронтендеру:**
- Транзакция в мемпуле ≠ транзакция в блоке. UI должен показывать `pending` → `confirming` → `confirmed`.
- После отправки транзакции данные на фронте не меняются мгновенно — нужен либо polling, либо события, либо Subgraph.
- Газ стоит денег → каждая `writeContract()` должна быть оправдана. Чтение (`call`/`readContract`) — бесплатно.

### Что хотят услышать

✅ Блоки, хеши, связь между блоками (цепочка)
✅ Консенсус (PoS), валидаторы, финальность
✅ EVM и детерминированность
✅ Связь с фронтендом: почему транзакции не мгновенные, почему нужен Subgraph
❌ «Блокчейн — это распределённая база данных» (слишком поверхностно)

---

## 2. Что такое газ (gas)? Почему одна транзакция стоит $1, а другая $50?

**Уровень:** Junior

### Что спрашивают на самом деле

Понимаешь ли ты, что каждая строчка кода в контракте стоит денег, и как это влияет на UX.

### Развёрнутый ответ

**Газ** — единица измерения вычислительной работы в Ethereum. Каждая операция EVM имеет фиксированную стоимость в газе:

| Операция | Газ |
|----------|-----|
| `ADD` (сложение) | 3 |
| `SSTORE` (запись в storage) | 20 000 (новый слот) / 2 900 (обновление) |
| `SLOAD` (чтение из storage) | 2 100 (холодное) / 100 (тёплое) |
| `CALL` (вызов другого контракта) | от 2 600 |
| Базовая стоимость транзакции | 21 000 |

**Формула стоимости:**
```
Стоимость = gasUsed × gasPrice
```

- **gasUsed** — сколько газа реально потратила транзакция (зависит от сложности контракта)
- **gasPrice** — цена за единицу газа в gwei (рыночная — зависит от загрузки сети)

**Почему цены разные:**
- Простой перевод ETH: ~21 000 газа → даже при 100 gwei = ~$5
- Своп через Uniswap V3: 150 000–300 000 газа → при 100 gwei = ~$35–70
- Минт NFT с загрузкой в storage: 100 000+ газа
- Сложная композируемая операция (multicall + flash loan): 500 000+ газа

**EIP-1559** (с августа 2021) изменил модель:
- **baseFee** — сжигается, адаптивно растёт/падает от загрузки
- **priorityFee** (чаевые) — валидатору за включение в блок

```
gasPrice = baseFee + priorityFee
```

**Для фронтендера:**
- Показывай **оценку газа перед отправкой**: `estimateGas()` из viem/ethers
- Дай пользователю выбрать priority fee (slow/medium/fast)
- Показывай экономию при L2 (Arbitrum: газ в 10–50× дешевле)

### Что хотят услышать

✅ Газ = плата за вычисления, каждая операция EVM стоит газ
✅ Разница между gasUsed (сложность) и gasPrice (рынок)
✅ EIP-1559: baseFee + priorityFee
✅ Почему storage-операции дорогие
✅ Связь с фронтендом: estimateGas, выбор комиссии, UX

---

## 3. Чем отличается EOA от Contract Account?

**Уровень:** Junior/Middle

### Развёрнутый ответ

В Ethereum два типа аккаунтов:

| | EOA | Contract Account |
|---|---|---|
| **Контролируется** | Приватным ключом | Кодом (байткодом) |
| **Может инициировать транзакцию** | ✅ Да | ❌ Нет (только в ответ на вызов) |
| **Имеет баланс ETH** | ✅ | ✅ |
| **Имеет storage** | ❌ | ✅ |
| **Имеет код** | ❌ | ✅ |
| **Газ** | 21 000 база | 21 000 + выполнение кода |
| **Создание** | Генерация ключей (бесплатно) | Деплой транзакцией (платно) |

**EOA (Externally Owned Account):**
- Твой кошелёк MetaMask
- Адрес = последние 20 байт от keccak256(publicKey)
- Может отправлять ETH и вызывать контракты
- Не имеет storage — нельзя хранить данные «внутри» EOA

**Contract Account:**
- Адрес = хеш от (адрес создателя + nonce) — CREATE
- CREATE2: адрес = хеш от (0xFF + sender + salt + bytecodeHash) — предсказуемый адрес!
- Имеет storage (persistent key-value хранилище)
- Код неизменяем после деплоя (кроме прокси-паттернов)

**Для фронтендера важно:**
- `msg.sender` в контракте — это всегда адрес того, кто инициировал транзакцию. Если контракт A вызывает контракт B, то `msg.sender` в B = адрес контракта A (а не оригинального пользователя). Это критично для безопасности.
- Чтобы проверить, контракт ли адрес: `getCode(address) !== '0x'` в viem.

### Что хотят услышать

✅ EOA = ключ, Contract = код
✅ Только EOA может инициировать транзакцию
✅ Contract имеет storage, EOA — нет
✅ `msg.sender` и цепочка вызовов
✅ Как отличить на фронте: `getCode()`

---

## 4. Что такое nonce и зачем он нужен?

**Уровень:** Middle

### Развёрнутый ответ

**Nonce** — счётчик транзакций для каждого EOA (аккаунта). Начинается с 0 и увеличивается на 1 с каждой подтверждённой транзакцией.

**Две функции nonce:**

1. **Порядок транзакций** — гарантирует, что транзакции от одного адреса выполняются строго последовательно. Нельзя отправить транзакцию с nonce 5, пока не подтверждены 0–4.

2. **Защита от повторной отправки (replay protection)** — одну и ту же подписанную транзакцию нельзя включить в блокчейн дважды. После включения nonce «занят».

**Пример проблемы:**
```
Отправил swap (nonce=3)  → ещё не попала в блок
Отправил approve (nonce=4) → застряла, ждёт nonce 3!
```

**Как это влияет на фронтенд:**

```ts
// wagmi получает nonce автоматически через viem
const { writeContract } = useWriteContract()

// Но если нужно управлять вручную — возможны коллизии:
// Пользователь в двух вкладках отправил транзакции с одинаковым nonce.
// Одна пройдёт, вторая — revert «nonce too low» или «replaced».
```

**Боевые ситуации:**
- **Застрявшая транзакция (stuck):** nonce 3 pending, а nonce 4 не может выполниться. Решение: отправить «пустую» транзакцию с nonce 3 и высоким газом (speed up / cancel в MetaMask).
- **Замена транзакции:** отправить новую с тем же nonce и газом выше на 10%+ — первая будет вытеснена (replaced).

### Что хотят услышать

✅ Nonce = счётчик транзакций аккаунта
✅ Гарантирует порядок и защиту от повторов
✅ Проблема застрявших транзакций
✅ Как ускорять/отменять (speed up / cancel)
✅ Как фронтенд получает nonce (автоматически в wagmi/viem)

---

## 5. Как работает Proof of Stake в Ethereum?

**Уровень:** Middle

### Развёрнутый ответ

**Proof of Stake (PoS)** — механизм консенсуса Ethereum с сентября 2022 (The Merge). Заменил Proof of Work (майнинг).

**Как работает:**

1. **Валидаторы** ставят 32 ETH в депозитный контракт. Сейчас ~1 млн валидаторов.

2. **Слоты и эпохи:**
   - Слот = 12 секунд. В каждом слоте один случайный валидатор предлагает блок.
   - Эпоха = 32 слота (~6.4 минуты). Каждую эпоху валидаторы голосуют за блоки (attestations).

3. **Комитеты:** валидаторы разбиваются на комитеты (≥128 валидаторов). Один комитет на слот.

4. **Финальность (finality):** блок становится «оправданным» (justified) после голосования 2/3 комитета. После двух последовательных justified-эпох наступает финальность — блок нельзя откатить без сжигания >1/3 всего stake.

**Наказания:**
- **Пропуск слота:** небольшой штраф (~$1)
- **Двойное предложение / двойное голосование:** slashing — потеря части stake (минимум 1 ETH) и принудительный выход
- **Попытка атаки 51%:** потеря всего stake

**Для фронтендера:**
- Транзакция подтверждена (в блоке) ≠ финализирована. Финальность — через ~12.8 минут.
- Для большинства dApp достаточно 1-2 подтверждений. Для крупных сумм (>$100K) ждут финальности.
- L2 (Arbitrum, Optimism) наследуют безопасность Ethereum, но имеют свою финальность.

### Что хотят услышать

✅ Валидаторы ставят ETH, предлагают блоки
✅ Слоты (12 сек), эпохи, комитеты
✅ Финальность через 2 эпохи (~12.8 мин)
✅ Slashing за жульничество
✅ Практическое значение: сколько подтверждений ждать

---

## 📜 Смарт-контракты

---

## 6. Что такое ABI и зачем он нужен фронтендеру?

**Уровень:** Junior

### Что спрашивают на самом деле

Это самый практичный вопрос для фронтендера. Без ABI ты не можешь вызвать ни одну функцию контракта. Проверяют, понимаешь ли ты, откуда берётся ABI и как его использовать.

### Развёрнутый ответ

**ABI (Application Binary Interface)** — JSON-описание интерфейса смарт-контракта. Это как «TypeScript-типы» для контракта, только в JSON.

**Как выглядит ABI:**
```json
[
  {
    "type": "function",
    "name": "balanceOf",
    "inputs": [{"name": "owner", "type": "address"}],
    "outputs": [{"name": "", "type": "uint256"}],
    "stateMutability": "view"
  },
  {
    "type": "function",
    "name": "transfer",
    "inputs": [
      {"name": "to", "type": "address"},
      {"name": "amount", "type": "uint256"}
    ],
    "outputs": [{"name": "", "type": "bool"}],
    "stateMutability": "nonpayable"
  },
  {
    "type": "event",
    "name": "Transfer",
    "inputs": [
      {"name": "from", "type": "address", "indexed": true},
      {"name": "to", "type": "address", "indexed": true},
      {"name": "value", "type": "uint256", "indexed": false}
    ]
  }
]
```

**Зачем ABI фронтендеру:**

1. **Кодирование вызовов** — `balanceOf(address)` → `0x70a08231000000000000000000000000abc...` (4 байта селектора + 32 байта аргумента)
2. **Декодирование ответов** — сырые байты → понятные значения
3. **Парсинг событий** — сырые логи → `{ from, to, value }`

**Где взять ABI:**
- Из Hardhat/Foundry после компиляции (`artifacts/contracts/Token.json`)
- Из Etherscan (вкладка Contract → Code → Contract ABI)
- Из npm-пакетов (`@uniswap/v3-core`)
- **Важно:** верифицировать ABI! Несовпадение ABI и реального байткода → непредсказуемое поведение.

**Использование в коде:**

```ts
// viem — типобезопасно через Human Readable ABI
const balance = await publicClient.readContract({
  address: '0x...',
  abi: erc20Abi,
  functionName: 'balanceOf',
  args: ['0x...'],
})

// wagmi — через хук
const { data: balance } = useReadContract({
  address: tokenAddress,
  abi: erc20Abi,
  functionName: 'balanceOf',
  args: [userAddress],
})
```

### Что хотят услышать

✅ ABI = JSON-описание функций и событий контракта
✅ Нужен для кодирования вызовов и декодирования ответов
✅ Где брать ABI (компиляция, Etherscan, пакеты)
✅ Как использовать в viem/wagmi
✅ Связь с type safety

---

## 7. ERC-20 vs ERC-721: в чём разница?

**Уровень:** Junior/Middle

### Развёрнутый ответ

**ERC-20** — стандарт взаимозаменяемых (fungible) токенов.
**ERC-721** — стандарт невзаимозаменяемых (non-fungible) токенов — NFT.

| | ERC-20 | ERC-721 |
|---|---|---|
| **Взаимозаменяемость** | 1 USDC = любой другой 1 USDC | Каждый токен уникален |
| **Баланс** | `balanceOf(address)` → число | `balanceOf(address)` → количество (какие именно — отдельно) |
| **Перевод** | `transfer(to, amount)` | `transferFrom(from, to, tokenId)` |
| **Информация о токене** | `name()`, `symbol()`, `decimals()` | Дополнительно: `tokenURI(tokenId)` → метаданные |
| **Approval** | `approve(spender, amount)` — на сумму | `approve(to, tokenId)` — на конкретный токен |
| **Владелец** | Баланс (безличный) | `ownerOf(tokenId)` → конкретный адрес |

**Интерфейс ERC-20:**
```solidity
function totalSupply() view returns (uint256)
function balanceOf(address) view returns (uint256)
function transfer(address to, uint256 amount) returns (bool)
function approve(address spender, uint256 amount) returns (bool)
function transferFrom(address from, address to, uint256 amount) returns (bool)
function allowance(address owner, address spender) view returns (uint256)

event Transfer(address from, address to, uint256 value)
event Approval(address owner, address spender, uint256 value)
```

**Интерфейс ERC-721 (дополнительно к ERC-165):**
```solidity
function ownerOf(uint256 tokenId) view returns (address)
function tokenURI(uint256 tokenId) view returns (string)
function safeTransferFrom(address from, address to, uint256 tokenId)

event Transfer(address from, address to, uint256 tokenId)  // value = tokenId!
event Approval(address owner, address approved, uint256 tokenId)
event ApprovalForAll(address owner, address operator, bool approved)
```

**Для фронтендера:**

ERC-20:
```tsx
// Показать баланс пользователя
const { data: balance } = useReadContract({
  abi: erc20Abi,
  functionName: 'balanceOf',
  args: [address],
})
// balance = 1500000000000000000n → форматируем: 1.5 USDC

// Отправить токены
const { writeContract } = useWriteContract()
writeContract({ abi: erc20Abi, functionName: 'transfer', args: [to, amount] })
```

ERC-721:
```tsx
// Получить все NFT пользователя — сложнее!
// Вариант 1: Subgraph (индексирует Transfer события)
// Вариант 2: Alchemy / Moralis NFT API
// Вариант 3: balanceOf + tokenOfOwnerByIndex (если есть enumerable extension)

// Показать картинку NFT
const { data: tokenURI } = useReadContract({
  abi: erc721Abi,
  functionName: 'tokenURI',
  args: [tokenId],
})
// tokenURI = "ipfs://Qm.../123.json" или "https://metadata.nft.com/123"
```

**Вариации:**
- **ERC-1155** — мультитокен: один контракт управляет и fungible, и non-fungible токенами. Часто используется в играх.
- **ERC-721A** (Azuki) — газ-оптимизированный минт нескольких NFT в одной транзакции.
- **Soulbound (SBT)** — NFT, который нельзя передать (нет transfer).

### Что хотят услышать

✅ Fungible vs non-fungible, ключевые отличия интерфейсов
✅ `balanceOf` возвращает число vs количество
✅ `tokenURI` — отдельный метод только у ERC-721
✅ Как показывать NFT на фронте (Subgraph/Alchemy/tokenOfOwnerByIndex)
✅ Упомянуть ERC-1155 и Soulbound как бонус

---

## 8. События (events) в Solidity: как их слушать на фронте?

**Уровень:** Middle

### Развёрнутый ответ

**Events** — это логи, которые смарт-контракт испускает при выполнении. Они хранятся в блокчейне вечно, но **недоступны изнутри смарт-контракта** (контракт не может прочитать свои же события).

**Объявление в Solidity:**
```solidity
event Transfer(address indexed from, address indexed to, uint256 value);

function transfer(address to, uint256 amount) public returns (bool) {
    balances[msg.sender] -= amount;
    balances[to] += amount;
    emit Transfer(msg.sender, to, amount);  // испускаем событие
    return true;
}
```

- `indexed` — до 3 параметров можно пометить как indexed → по ним можно фильтровать
- Не-indexed параметры хранятся в `data` (не фильтруются, но читаются)

**Чтение событий на фронтенде:**

**Способ 1: getLogs (исторические события)**
```ts
import { publicClient } from './config'

const logs = await publicClient.getLogs({
  address: tokenAddress,
  event: parseAbiItem('event Transfer(address indexed from, address indexed to, uint256 value)'),
  args: { from: userAddress },  // фильтр по from
  fromBlock: 19000000n,
  toBlock: 'latest',
})
```

**Способ 2: watchEvent (реальное время через WebSocket)**
```ts
const unwatch = publicClient.watchEvent({
  address: tokenAddress,
  event: parseAbiItem('event Transfer(address indexed from, address indexed to, uint256 value)'),
  onLogs: (logs) => {
    for (const log of logs) {
      console.log(`${log.args.from} → ${log.args.to}: ${log.args.value}`)
    }
  },
})
// unwatch() — отписаться
```

> **Как читать watchEvent({ event: parseAbiItem('event Transfer(...)'), onLogs }):** «подпишись на событие Transfer контракта: parseAbiItem превращает сигнатуру события в фильтр, onLogs — колбэк, который срабатывает каждый раз когда блокчейн рождает новый Transfer. unwatch() отписывает». Мнемоника: *watchEvent = WebSocket-подписка на блокчейн-события: «кто-то перевёл токен — покажи мне прямо сейчас».*

**Способ 3: wagmi хук useWatchContractEvent**
```tsx
import { useWatchContractEvent } from 'wagmi'

useWatchContractEvent({
  address: tokenAddress,
  abi: erc20Abi,
  eventName: 'Transfer',
  onLogs(logs) {
    // logs — массив событий
  },
})
```

**Способ 4: Subgraph (для сложных запросов)**
```graphql
{
  transfers(first: 10, where: { from: "0x..." }, orderBy: timestamp, orderDirection: desc) {
    id
    from
    to
    value
    timestamp
  }
}
```

**Когда что использовать:**

| Нужно | Инструмент |
|-------|-----------|
| История операций пользователя | Subgraph (индексация) |
| Реальное время (live feed) | `watchEvent` (WebSocket) |
| Разовый запрос данных | `getLogs` |
| Статистика/аналитика | Dune Analytics (над Subgraph) |

### Что хотят услышать

✅ Events = логи в блокчейне, контракт их не читает
✅ `indexed` параметры = фильтруемые
✅ Три способа чтения: getLogs, watchEvent, Subgraph
✅ Когда что использовать (история vs real-time vs аналитика)
✅ Понимание, что события дешевле storage и часто используются для «истории»

---

## 9. Storage vs Memory vs Calldata в Solidity

**Уровень:** Middle/Senior

### Развёрнутый ответ

Три области данных в Solidity. Понимать их критически важно для оптимизации газа и безопасности.

| | Storage | Memory | Calldata |
|---|---|---|---|
| **Где хранится** | В блокчейне (persistent) | В памяти EVM (временная) | В данных транзакции (read-only) |
| **Время жизни** | Между транзакциями | Только во время вызова | Только во время вызова |
| **Стоимость** | 💸💸💸 ОЧЕНЬ дорого | 💸 Умеренно (растёт с размером) | 💸 Дёшево |
| **Изменяемость** | ✅ mutable | ✅ mutable | ❌ read-only |
| **Где используется** | Переменные состояния | Локальные переменные | Аргументы external-функций |

**Пример кода:**
```solidity
contract Example {
    // STORAGE — хранится в блокчейне, дорого!
    uint256[] public storedArray;  // storage

    function example(
        uint256[] calldata _input    // calldata — read-only, дёшево
    ) external {
        uint256[] memory temp = new uint256[](3);  // memory — временно

        // Чтение из storage — SLOAD (2100 холодное / 100 тёплое)
        uint256 x = storedArray[0];

        // Запись в storage — SSTORE (20000 новый / 2900 обновление)
        storedArray.push(x);

        // memory → storage — дорого (копирование каждого элемента)
        storedArray = temp;  // 💸💸💸

        // calldata → memory — дёшево
        uint256[] memory copy = _input;  // 💸
    }
}
```

**Правила и подводные камни:**

1. **External-функции** — используй `calldata` для массивов и строк вместо `memory`. Экономия газа 5–10×.

2. **Storage-указатели опасны:**
```solidity
function bad() public {
    MyStruct storage s = storedStructs[0];  // s — УКАЗАТЕЛЬ, не копия!
    s.value = 100;  // меняет storedStructs[0] в storage!
}
```

3. **Чтение из storage в цикле — антипаттерн:**
```solidity
// ❌ Плохо: SLOAD на каждой итерации
for (uint i = 0; i < storedArray.length; i++) { ... }

// ✅ Хорошо: один SLOAD в memory
uint256 len = storedArray.length;
for (uint i = 0; i < len; i++) { ... }
```

**Для фронтендера:** эти знания нужны, чтобы:
- Понимать, почему одни функции стоят дороже других (пишут в storage vs читают)
- Читать код контракта и оценивать газ
- Понимать отчёты о газе в Hardhat/Foundry (`gas reporter`)

### Что хотят услышать

✅ Storage = блокчейн, memory = RAM EVM, calldata = входные данные
✅ Разница в стоимости: SSTORE дорогой, calldata дешёвый
✅ Storage-указатели и почему они опасны
✅ SLOAD в цикле — антипаттерн
✅ calldata для external-функций

---

## 10. Как работает approve + transferFrom в ERC-20?

**Уровень:** Middle

### Что спрашивают на самом деле

Это фундаментальный паттерн DeFi. Каждый своп на Uniswap начинается с `approve`. Проверяют, понимаешь ли ты двухшаговый процесс и UX-последствия.

### Развёрнутый ответ

**Проблема:** я хочу, чтобы контракт Uniswap свопнул мои USDC на ETH. Но `transfer` может вызвать только владелец токенов (я). Как дать право Uniswap перевести мои токены?

**Решение: approve + transferFrom**

```
Шаг 1: approve
Пользователь ──► ERC-20 контракт: «Разрешаю Uniswap потратить 1000 USDC с моего адреса»
             approve(uniswapRouter, 1000e18)

Шаг 2: transferFrom
Uniswap ──► ERC-20 контракт: «Перевожу 1000 USDC от пользователя на пул»
        transferFrom(user, pool, 1000e18)
```

> **Как читать approve(spender, amount) → transferFrom(owner, to, amount):** «шаг 1: ты говоришь токену "разрешаю контракту spender потратить до amount моих токенов" — это как подписать чек с лимитом. Шаг 2: spender говорит токену "переведи amount от owner на to" — контракт проверяет чек и выполняет перевод». Мнемоника: *approve = выписал чек, transferFrom = кто-то предъявил чек к оплате; два шага, две транзакции, два газа.*

**Solidity (как это внутри ERC-20):**
```solidity
mapping(address => mapping(address => uint256)) private _allowances;

function approve(address spender, uint256 amount) public returns (bool) {
    _allowances[msg.sender][spender] = amount;
    emit Approval(msg.sender, spender, amount);
    return true;
}

function transferFrom(address from, address to, uint256 amount) public returns (bool) {
    // Проверяем, что msg.sender (spender) имеет разрешение
    uint256 currentAllowance = _allowances[from][msg.sender];
    require(currentAllowance >= amount, "insufficient allowance");

    _allowances[from][msg.sender] = currentAllowance - amount;
    _transfer(from, to, amount);
    return true;
}
```

**Фронтенд — двухшаговый UX:**

```tsx
function SwapButton() {
  // Шаг 1: Проверяем allowance
  const { data: allowance } = useReadContract({
    abi: erc20Abi,
    functionName: 'allowance',
    args: [userAddress, uniswapRouter],
  })

  const needApproval = allowance < amountToSwap

  // Шаг 2a: Если allowance недостаточен — approve
  const { writeContract: approve } = useWriteContract()

  // Шаг 2b: Если allowance достаточен — swap
  const { writeContract: swap } = useWriteContract()

  if (needApproval) {
    return <button onClick={() => approve({
      abi: erc20Abi,
      address: tokenAddress,
      functionName: 'approve',
      args: [uniswapRouter, maxUint256], // infinite approval!
    })}>Approve USDC</button>
  }

  return <button onClick={() => swap({
    abi: uniswapRouterAbi,
    address: uniswapRouter,
    functionName: 'swapExactTokensForTokens',
    args: [amountIn, amountOutMin, path, userAddress, deadline],
  })}>Swap</button>
}
```

**Важные нюансы:**

- **Infinite approval** — `approve(spender, type(uint256).max)` — чтобы не делать approve каждый раз. Но риск: если контракт взломан — могут украсть весь allowance.
- **Race condition** — если изменить allowance с 100 на 200, пока транзакция в мемпуле, spender может успеть потратить и старый (100), и новый (200) allowance. Решение: сначала сбросить в 0, потом установить новое значение. Или использовать `increaseAllowance`/`decreaseAllowance`.
- **Permit (EIP-2612)** — gasless approve через подпись. Пользователь подписывает сообщение, контракт верифицирует подпись и устанавливает allowance. Одна транзакция вместо двух!

### Что хотят услышать

✅ Двухшаговый процесс: approve → transferFrom
✅ `_allowances` mapping: `owner → spender → amount`
✅ Как реализовать UX: проверить allowance → кнопка Approve или Swap
✅ Infinite approval: плюсы и риски
✅ Race condition в approve и как избежать
✅ Упомянуть Permit (EIP-2612) — бонус

---

## 11. Как прочитать и вызвать смарт-контракт из React?

**Уровень:** Junior/Middle

### Развёрнутый ответ

**Чтение (read) — бесплатно, мгновенно (с точки зрения пользователя):**

```tsx
import { useReadContract } from 'wagmi'
import { erc20Abi } from './abis/erc20'

function TokenBalance({ userAddress }: { userAddress: string }) {
  const { data: balance, isLoading, error } = useReadContract({
    address: '0xdAC17F958D2ee523a2206206994597C13D831ec7', // USDT
    abi: erc20Abi,
    functionName: 'balanceOf',
    args: [userAddress],
  })

  // balance = 1500000000n (BigInt)
  const formatted = balance ? formatUnits(balance, 6) : '0'  // USDT = 6 decimals

  if (isLoading) return <div>Загрузка баланса...</div>
  return <div>Баланс: {formatted} USDT</div>
}
```

**Запись (write) — платно, требует подтверждения:**

```tsx
import { useWriteContract, useWaitForTransactionReceipt } from 'wagmi'

function SendToken({ to }: { to: string }) {
  const { writeContract, data: hash, isPending } = useWriteContract()

  const { isLoading: isConfirming, isSuccess } = useWaitForTransactionReceipt({
    hash,
  })

  const send = () => {
    writeContract({
      address: '0xdAC17F958D2ee523a2206206994597C13D831ec7',
      abi: erc20Abi,
      functionName: 'transfer',
      args: [to, parseUnits('10', 6)], // 10 USDT
    })
  }

  return (
    <div>
      <button onClick={send} disabled={isPending}>
        {isPending ? 'Подтвердите в кошельке...' : 'Отправить 10 USDT'}
      </button>
      {hash && <div>Tx: {hash}</div>}
      {isConfirming && <div>Подтверждается...</div>}
      {isSuccess && <div>✅ Отправлено!</div>}
    </div>
  )
}
```

**Мульти-контрактное чтение (multicall) — для производительности:**

```tsx
import { useReadContracts } from 'wagmi'

function TokenInfo({ tokens }: { tokens: string[] }) {
  const { data } = useReadContracts({
    contracts: tokens.flatMap(addr => [
      { address: addr, abi: erc20Abi, functionName: 'name' },
      { address: addr, abi: erc20Abi, functionName: 'symbol' },
      { address: addr, abi: erc20Abi, functionName: 'decimals' },
    ]),
  })
  // data = [('Tether', 'USDT', 6), ('USD Coin', 'USDC', 6), ...]
}
```

> **Как читать useReadContracts({ contracts: tokens.flatMap(...) }):** «возьми массив адресов токенов, для каждого размножь в три запроса (name, symbol, decimals) через flatMap — и получи все ответы одним батчем в том же порядке». Мнемоника: *useReadContracts = мультитул для чтения: много контрактов × много функций = один вызов, один массив ответов.*

**Без wagmi — напрямую через viem:**

```ts
import { createPublicClient, http } from 'viem'
import { mainnet } from 'viem/chains'

const publicClient = createPublicClient({
  chain: mainnet,
  transport: http(),
})

const balance = await publicClient.readContract({
  address: '0xdAC17F958D2ee523a2206206994597C13D831ec7',
  abi: erc20Abi,
  functionName: 'balanceOf',
  args: ['0x...'],
})
```

### Что хотят услышать

✅ Чтение (`readContract` / `useReadContract`) — бесплатно, RPC-нода
✅ Запись (`writeContract` / `useWriteContract`) — платно, цепочка состояний
✅ Жизненный цикл: idle → pending (кошелёк) → confirming (майнинг) → confirmed
✅ `useReadContracts` для мульти-чтения (multicall)
✅ `formatUnits` / `parseUnits` для работы с decimals

---

## 🖥️ dApp-фронтенд

---

## 12. Как подключить кошелёк пользователя к dApp?

**Уровень:** Junior

### Что спрашивают на самом деле

Самый частый вопрос. Проверяют, знаешь ли ты современный стек (RainbowKit, wagmi, WalletConnect) и понимаешь ли весь flow от кнопки до подписанной транзакции.

### Развёрнутый ответ

**Современный способ: RainbowKit + wagmi + viem**

```tsx
// 1. Установка: npm i @rainbow-me/rainbowkit wagmi viem @tanstack/react-query

// 2. Конфигурация (config.ts)
import { getDefaultConfig } from '@rainbow-me/rainbowkit'
import { mainnet, polygon, arbitrum } from 'wagmi/chains'

export const config = getDefaultConfig({
  appName: 'My dApp',
  projectId: 'YOUR_WALLETCONNECT_PROJECT_ID', // из https://cloud.walletconnect.com
  chains: [mainnet, polygon, arbitrum],
  ssr: false,
})

// 3. Провайдеры (main.tsx)
import { RainbowKitProvider } from '@rainbow-me/rainbowkit'
import { WagmiProvider } from 'wagmi'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import '@rainbow-me/rainbowkit/styles.css'

const queryClient = new QueryClient()

function App() {
  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider>
          {/* Ваше приложение */}
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider>
  )
}

// 4. Кнопка Connect (любой компонент)
import { ConnectButton } from '@rainbow-me/rainbowkit'

function Header() {
  return <ConnectButton />
  // ГОТОВО: кнопка, модалка выбора кошелька, смена сети, баланс, адрес — всё из коробки!
}
```

**Что происходит при нажатии «Connect»:**

```
Пользователь → ConnectButton → Модалка RainbowKit → Выбор кошелька
                                                      │
                          ┌───────────────────────────┤
                          ▼                           ▼
                   MetaMask (injected)          WalletConnect
                   window.ethereum              ┌── QR-код
                   .request({                   │   (для мобильных
                     method:                    │    кошельков)
                     'eth_requestAccounts'      │
                   })                           └── Сканирование → пара ключей
                          │                           │
                          └───────────┬───────────────┘
                                      ▼
                              Аккаунт подключён
                              wagmi сохраняет:
                              - address
                              - chainId
                              - connector (MetaMask/WalletConnect/...)
```

**Без RainbowKit — вручную через wagmi:**

```tsx
import { useConnect, useAccount, useDisconnect } from 'wagmi'
import { injected } from 'wagmi/connectors'

function ManualConnect() {
  const { connect } = useConnect()
  const { address, isConnected } = useAccount()
  const { disconnect } = useDisconnect()

  if (isConnected) {
    return (
      <div>
        {address}
        <button onClick={() => disconnect()}>Disconnect</button>
      </div>
    )
  }

  return (
    <button onClick={() => connect({ connector: injected() })}>
      Connect MetaMask
    </button>
  )
}
```

**Важные нюансы:**
- **Смена сети:** автоматически через RainbowKit, вручную — `useSwitchChain`
- **Disconnect:** не отключает MetaMask глобально, только ваш dApp «забывает» сессию
- **WalletConnect v2:** требует `projectId` из WalletConnect Cloud
- **SSR:** Next.js требует `ssr: false` в конфиге wagmi, потому что MetaMask — browser-only

### Что хотят услышать

✅ RainbowKit + wagmi + viem как стандартный стек
✅ Полный flow: конфиг → провайдеры → ConnectButton
✅ injected (MetaMask) vs WalletConnect (QR)
✅ Как работает под капотом: `eth_requestAccounts`
✅ Смена сети, disconnect
✅ SSR-нюансы с Next.js

---

## 13. Жизненный цикл транзакции: как обработать все состояния в UI?

**Уровень:** Middle/Senior

### Что спрашивают на самом деле

Это проверка твоего опыта. Проблема: пользователь нажал кнопку, прошло 30 секунд, ничего не происходит. Что показывать? Как не потерять транзакцию при перезагрузке? Как понять, что revert?

### Развёрнутый ответ

**Пять состояний транзакции:**

```
idle → pending → confirming → confirmed
          │           │            │
          ▼           ▼            ▼
      rejected     failed        receipt
```

**Полная реализация компонента:**

```tsx
function TransactionButton() {
  const [status, setStatus] = useState<'idle' | 'pending' | 'confirming' | 'confirmed' | 'failed'>('idle')
  const [txHash, setTxHash] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const { writeContractAsync } = useWriteContract()
  const { refetch: refetchBalance } = useReadContract({ /* ... */ })

  const send = async () => {
    try {
      setStatus('pending')
      setError(null)

      // 1. Отправка — MetaMask показывает окно подтверждения
      const hash = await writeContractAsync({
        address: tokenAddress,
        abi: erc20Abi,
        functionName: 'transfer',
        args: [to, amount],
      })
      setTxHash(hash)
      setStatus('confirming')

      // 2. Ждём квитанцию
      const receipt = await publicClient.waitForTransactionReceipt({ hash })

> **Как читать writeContractAsync(...) → waitForTransactionReceipt({ hash }):** «вызови функцию контракта и жди Promise с хешем (кошелёк попросит подпись), затем передай хеш в ожидание квитанции — второй Promise разрешится когда транзакция попадёт в блок». Мнемоника: *writeContractAsync = «отправь и дай хеш», waitForTransactionReceipt = «жди пока блокчейн примет»; связка двух await'ов.*

      // 3. Проверяем статус
      if (receipt.status === 'success') {
        setStatus('confirmed')
        await refetchBalance() // Обновляем баланс
      } else {
        setStatus('failed')
        setError('Транзакция вернула revert')
      }
    } catch (err: any) {
      // Пользователь отклонил в MetaMask
      if (err?.code === 'ACTION_REJECTED' || err?.message?.includes('rejected')) {
        setStatus('idle')
        setError('Вы отклонили транзакцию')
      } else {
        setStatus('failed')
        setError(parseTxError(err))
      }
    }
  }

  return (
    <div>
      <button onClick={send} disabled={status !== 'idle'}>
        {status === 'idle' && 'Отправить'}
        {status === 'pending' && '⏳ Подтвердите в кошельке...'}
        {status === 'confirming' && '🔄 Транзакция обрабатывается...'}
        {status === 'confirmed' && '✅ Успешно!'}
        {status === 'failed' && '❌ Ошибка'}
      </button>

      {txHash && (
        <a href={`https://etherscan.io/tx/${txHash}`} target="_blank">
          Посмотреть на Etherscan ↗
        </a>
      )}

      {error && <div className="error">{error}</div>}

      {/* Прогресс-бар подтверждений */}
      {status === 'confirming' && <ConfirmationProgress hash={txHash!} requiredConfirmations={2} />}
    </div>
  )
}

// Компонент прогресса подтверждений
function ConfirmationProgress({ hash, requiredConfirmations }: { hash: string; requiredConfirmations: number }) {
  const { data: receipt } = useWaitForTransactionReceipt({ hash, confirmations: requiredConfirmations })

  // useWaitForTransactionReceipt уже ждёт N подтверждений.
  // Пока ждёт — isLoading = true.
  // Если нужен прогресс — опрашиваем вручную.
}
```

**Критические UX-требования:**

1. **Не блокировать UI на время транзакции.** Пользователь может переключиться на другую вкладку. Сохраняй `txHash` в `localStorage` и восстанавливай состояние при возвращении.

2. **«Застрявшая» транзакция:** если `pending` дольше 5 минут → показать кнопку «Ускорить» (speed up) или «Отменить».

3. **Revert с причиной:** расшифровать через `decodeErrorResult` и показать человеческое сообщение.

```ts
function parseTxError(error: any): string {
  if (error?.walk) {
    // viem: можно пройти по цепочке ошибок
    const decoded = error.walk(e => e?.data?.args?.[0])
    if (decoded) return decoded
  }
  // Ручной маппинг известных ошибок
  if (error?.message?.includes('insufficient funds')) return 'Недостаточно средств для оплаты газа'
  if (error?.message?.includes('transfer amount exceeds balance')) return 'Недостаточно токенов'
  return 'Транзакция не удалась'
}
```

4. **Тост-уведомления:** не модалки! Пользователь не должен ждать. Показывай toast с хешем и статусом.

### Что хотят услышать

✅ 5 состояний: idle → pending → confirming → confirmed/failed
✅ `writeContract` → хеш → `waitForTransactionReceipt`
✅ Обработка ошибок: rejected, revert, out of gas
✅ Persistence txHash в localStorage для восстановления при перезагрузке
✅ Ссылка на Etherscan
✅ Speed up / cancel для застрявших транзакций

---

## 14. wagmi vs ethers.js vs viem — что выбрать?

**Уровень:** Middle

### Развёрнутый ответ

| | ethers.js v6 | viem v2 | wagmi v3 |
|---|---|---|---|
| **Слой** | Низкоуровневый | Низкоуровневый | React-хуки |
| **Размер** | ~500KB | ~50KB (tree-shakeable) | ~100KB + viem |
| **TypeScript** | Родной, но исторически сложный | First-class, выведенные типы | First-class |
| **Производительность** | Средняя | Высокая | Высокая (viem под капотом) |
| **React-интеграция** | Ручная | Ручная | Из коробки |
| **Документация** | Обширная (старая) | Отличная | Отличная |
| **Поддержка** | Активная | Активная (та же команда wevm) | Активная |

**Рекомендация:**
```
Если React-приложение:
  → wagmi + viem (viem уже идёт как зависимость wagmi)

Если Node.js / скрипты / CLI:
  → viem

Если legacy проект на ethers.js:
  → можно не переписывать, но новые проекты — viem
```

**Почему viem быстрее и меньше:**
- Tree-shakeable: импортируешь только нужные функции
- Нет классов — чистые функции
- Нативные BigInt (ethers.js долго использовал BigNumber)
- Оптимизированная сериализация RPC-запросов

**Пример чтения баланса на всех трёх:**

```ts
// ethers.js v6
import { ethers } from 'ethers'
const provider = new ethers.JsonRpcProvider(rpcUrl)
const balance = await provider.getBalance(address)

// viem
import { createPublicClient, http } from 'viem'
const publicClient = createPublicClient({ chain: mainnet, transport: http() })
const balance = await publicClient.getBalance({ address })

// wagmi (React)
import { useBalance } from 'wagmi'
const { data: balance } = useBalance({ address })
```

### Что хотят услышать

✅ viem — современный низкоуровневый (лёгкий, быстрый, tree-shakeable)
✅ wagmi — React-хуки поверх viem
✅ ethers.js — legacy, но всё ещё много где используется
✅ Разница в размере бандла, производительности, TypeScript
✅ Практическая рекомендация: wagmi + viem для React

---

## 15. Как отображать «ждущие» транзакции и обновлять данные после подтверждения?

**Уровень:** Middle

### Развёрнутый ответ

Это продолжение вопроса 13, но акцент на мульти-транзакционном UX и инвалидации кеша.

**Проблема:** пользователь отправил токены, баланс должен обновиться, но React Query кеширует старый ответ RPC.

**Решение: инвалидация после подтверждения.**

```tsx
import { useQueryClient } from '@tanstack/react-query'
import { useWriteContract, useWaitForTransactionReceipt, useReadContract } from 'wagmi'

function SendWithBalanceUpdate() {
  const queryClient = useQueryClient()
  const { writeContractAsync } = useWriteContract()

  const send = async () => {
    const hash = await writeContractAsync({
      address: tokenAddress,
      abi: erc20Abi,
      functionName: 'transfer',
      args: [to, amount],
    })

    // Ждём квитанцию
    const receipt = await publicClient.waitForTransactionReceipt({ hash })

    if (receipt.status === 'success') {
      // Инвалидируем ВСЕ запросы, связанные с этим контрактом и адресом
      queryClient.invalidateQueries({
        queryKey: useReadContract.getQueryKey({
          address: tokenAddress,
          functionName: 'balanceOf',
          args: [senderAddress],
        }),
      })
      // Пользователь увидит обновлённый баланс автоматически!
    }
  }
}
```

**Мульти-транзакционный UX (очередь транзакций):**

```tsx
interface PendingTx {
  id: string
  hash: string
  description: string
  status: 'pending' | 'confirming' | 'confirmed' | 'failed'
  timestamp: number
}

function TransactionQueue() {
  const [pendingTxs, setPendingTxs] = useState<PendingTx[]>([])

  const addTx = (hash: string, description: string) => {
    const tx: PendingTx = {
      id: hash,
      hash,
      description,
      status: 'confirming',
      timestamp: Date.now(),
    }
    setPendingTxs(prev => [tx, ...prev])

    // Ждём подтверждения
    publicClient.waitForTransactionReceipt({ hash }).then(receipt => {
      setPendingTxs(prev =>
        prev.map(t => t.id === hash
          ? { ...t, status: receipt.status === 'success' ? 'confirmed' : 'failed' }
          : t
        )
      )
    })
  }

  return (
    <div className="tx-queue">
      {pendingTxs.map(tx => (
        <div key={tx.id} className={`tx-item tx-${tx.status}`}>
          <span className="tx-desc">{tx.description}</span>
          <span className="tx-status">
            {tx.status === 'confirming' && <Loader />}
            {tx.status === 'confirmed' && '✅'}
            {tx.status === 'failed' && '❌'}
          </span>
          <a href={`https://etherscan.io/tx/${tx.hash}`}>Tx ↗</a>
        </div>
      ))}
    </div>
  )
}
```

**Persistent queue (localStorage):**

```ts
// Сохраняем при добавлении
localStorage.setItem('pendingTxs', JSON.stringify(pendingTxs))

// Восстанавливаем при загрузке
useEffect(() => {
  const saved = localStorage.getItem('pendingTxs')
  if (saved) {
    const txs: PendingTx[] = JSON.parse(saved)
    // Для каждой незавершённой — проверяем статус заново
    txs.filter(t => t.status === 'confirming').forEach(tx => {
      checkTxStatus(tx.hash)
    })
  }
}, [])
```

### Что хотят услышать

✅ Инвалидация кеша React Query после подтверждения транзакции
✅ Очередь транзакций (массив pendingTxs)
✅ Persistent queue в localStorage
✅ Автоматическая проверка статуса незавершённых транзакций при загрузке
✅ Тост-уведомления вместо блокирующих модалок

---

## 16. Как обрабатывать ошибки транзакций и показывать понятные сообщения?

**Уровень:** Middle

### Развёрнутый ответ

Транзакция может упасть по десятку причин. Задача фронтендера — превратить `0x08c379a0...` в «У вас недостаточно токенов USDC».

**Типы ошибок:**

1. **Отклонение пользователем** (user rejected)
2. **Revert смарт-контракта** (логика контракта)
3. **Недостаточно газа** (out of gas)
4. **Nonce-проблемы** (слишком низкий / повтор)
5. **Сетевые ошибки** (RPC недоступен, таймаут)

**Полная функция парсинга:**

```ts
import { decodeErrorResult, BaseError, ContractFunctionRevertedError } from 'viem'

function parseTransactionError(error: unknown): string {
  // 1. Пользователь отклонил
  if (typeof error === 'object' && error !== null) {
    const err = error as any
    if (
      err.code === 4001 ||                          // MetaMask
      err.code === 'ACTION_REJECTED' ||              // ethers
      err.message?.includes('rejected') ||           // общее
      err.message?.includes('denied')                // WalletConnect
    ) {
      return 'Вы отклонили транзакцию в кошельке'
    }
  }

  // 2. Revert контракта — пробуем расшифровать
  if (error instanceof BaseError) {
    // viem: цепочка ошибок
    const revertError = error.walk(
      (e) => e instanceof ContractFunctionRevertedError
    )

    if (revertError instanceof ContractFunctionRevertedError) {
      const errorName = revertError.data?.errorName ?? ''
      // Кастомные ошибки контракта
      const errorMessages: Record<string, string> = {
        'ERC20InsufficientBalance': 'Недостаточно токенов на балансе',
        'ERC20InsufficientAllowance': 'Недостаточно разрешения (approve)',
        'OwnableUnauthorizedAccount': 'Вы не владелец контракта',
        'ReentrancyGuardReentrantCall': 'Повторный вызов заблокирован',
      }
      if (errorMessages[errorName]) return errorMessages[errorName]

      // Если есть revert reason строка
      if (revertError.reason) return revertError.reason
    }
  }

  // 3. Общие ошибки
  const msg = (error as any)?.message ?? String(error)
  if (msg.includes('insufficient funds')) return 'Недостаточно ETH для оплаты газа'
  if (msg.includes('nonce too low')) return 'Nonce слишком низкий. Попробуйте сбросить активность MetaMask'
  if (msg.includes('nonce too high')) return 'Nonce слишком высокий. Возможно, есть pending-транзакция'
  if (msg.includes('gas required exceeds allowance')) return 'Газ превышает лимит блока'
  if (msg.includes('timeout') || msg.includes('TIMEOUT')) return 'RPC-нода не отвечает. Попробуйте позже'
  if (msg.includes('network')) return 'Ошибка сети. Проверьте подключение'

  // 4. Fallback — сырая ошибка
  return `Ошибка транзакции: ${msg.slice(0, 100)}`
}
```

**Использование в компоненте:**

```tsx
function SendButton() {
  const [error, setError] = useState<string | null>(null)
  const { writeContractAsync } = useWriteContract()

  const handleSend = async () => {
    setError(null)
    try {
      const hash = await writeContractAsync({ /* ... */ })
      // успех
    } catch (err) {
      setError(parseTransactionError(err))
    }
  }

  return (
    <div>
      <button onClick={handleSend}>Отправить</button>
      {error && <div className="tx-error">{error}</div>}
    </div>
  )
}
```

**Лучшие практики:**
- **Никогда не показывай сырой стек ошибки пользователю** — это пугает и неинформативно
- **Логируй полную ошибку в консоль/Sentry** для отладки
- **Для кастомных ошибок контракта** определи mapping errorName → человеческое сообщение
- **Revert reason** в виде строки — устарело, но ещё встречается. Новые контракты используют кастомные ошибки (gas-эффективнее).

### Что хотят услышать

✅ Различать типы ошибок: rejected, revert, gas, nonce, network
✅ `decodeErrorResult` / `ContractFunctionRevertedError` в viem
✅ Маппинг кастомных ошибок на человеческие сообщения
✅ User rejected обрабатывать отдельно (это не ошибка, а отмена)
✅ Не показывать сырые ошибки пользователю

---

## 17. Как слушать события смарт-контракта в реальном времени в React?

**Уровень:** Middle/Senior

### Развёрнутый ответ

**Способ 1: wagmi `useWatchContractEvent`**

```tsx
import { useWatchContractEvent } from 'wagmi'
import { parseAbiItem } from 'viem'

function LiveTransfers({ tokenAddress }: { tokenAddress: string }) {
  const [transfers, setTransfers] = useState<Transfer[]>([])

  useWatchContractEvent({
    address: tokenAddress,
    abi: erc20Abi,
    eventName: 'Transfer',
    onLogs(logs) {
      for (const log of logs) {
        setTransfers(prev => [{
          hash: log.transactionHash,
          from: log.args.from!,
          to: log.args.to!,
          value: log.args.value!,
        }, ...prev].slice(0, 50)) // храним последние 50
      }
    },
  })

  return (
    <div>
      <h3>Live Transfers</h3>
      {transfers.map((t, i) => (
        <div key={i}>
          {t.from.slice(0, 6)} → {t.to.slice(0, 6)}: {formatUnits(t.value, 18)}
        </div>
      ))}
    </div>
  )
}
```

**Способ 2: viem watchEvent + useEffect (больше контроля)**

```tsx
function useLiveEvents(tokenAddress: string) {
  const [events, setEvents] = useState<any[]>([])

  useEffect(() => {
    const unwatch = publicClient.watchEvent({
      address: tokenAddress,
      event: parseAbiItem('event Transfer(address indexed from, address indexed to, uint256 value)'),
      onLogs: (logs) => {
        setEvents(prev => [...logs, ...prev].slice(0, 100))
      },
      // Фильтр: только новые блоки
      fromBlock: 'latest',
    })

    return () => {
      unwatch()  // очистка при размонтировании!
    }
  }, [tokenAddress])

  return events
}
```

**Способ 3: WebSocket провайдер (для максимальной производительности)**

```ts
// viem автоматически использует WebSocket, если URL ws://
const publicClient = createPublicClient({
  chain: mainnet,
  transport: webSocket('wss://mainnet.infura.io/ws/v3/YOUR_KEY'),
})
```

**Важно: WebSocket vs HTTP polling**

| | WebSocket | HTTP Polling |
|---|---|---|
| **Задержка** | ~1 сек (мгновенно при новом блоке) | ~12 сек (интервал между блоками) |
| **Нагрузка** | Только при событиях | Каждые N секунд запрос |
| **Сложность** | Переподключение при обрыве | Проще |
| **Поддержка RPC** | Не все провайдеры | Все |

**Практические проблемы:**
- **Переподключение:** WebSocket рвётся. Нужен reconnect с backoff.
- **Пропущенные блоки:** при разрыве — запросить `getLogs` за пропущенный диапазон.
- **Реконнект в React:** использовать `useEffect` cleanup + ref для хранения последнего обработанного блока.

```tsx
function useRobustEventWatch(tokenAddress: string) {
  const lastBlockRef = useRef<bigint>(0n)

  useEffect(() => {
    let unwatch: () => void
    let retries = 0

    const startWatching = () => {
      unwatch = publicClient.watchEvent({
        address: tokenAddress,
        event: parseAbiItem('event Transfer(...)'),
        fromBlock: lastBlockRef.current || 'latest',
        onLogs: (logs) => {
          // обновляем lastBlock при каждом событии
          if (logs.length > 0) {
            const maxBlock = logs.reduce((max, l) => l.blockNumber > max ? l.blockNumber : max, 0n)
            lastBlockRef.current = maxBlock
          }
          // обрабатываем логи...
        },
        onError: (error) => {
          console.error('Watch error:', error)
          retries++
          if (retries < 5) {
            setTimeout(startWatching, Math.min(1000 * 2 ** retries, 30000))
          }
        },
      })
    }

    startWatching()
    return () => unwatch?.()
  }, [tokenAddress])
}
```

### Что хотят услышать

✅ `useWatchContractEvent` из wagmi
✅ `watchEvent` из viem для ручного контроля
✅ WebSocket vs HTTP polling
✅ Очистка подписки в `useEffect` cleanup
✅ Переподключение при обрыве и восстановление пропущенных событий

---

## 18. Что такое multicall и зачем он на фронтенде?

**Уровень:** Middle/Senior

### Развёрнутый ответ

**Multicall** — контракт, который выполняет несколько `eth_call` в одной RPC-транзакции. Экономит сетевые запросы.

**Проблема без multicall:**
```
Запрос 1: balanceOf(user, tokenA)  → 200ms
Запрос 2: balanceOf(user, tokenB)  → 200ms
Запрос 3: balanceOf(user, tokenC)  → 200ms
...
Запрос 20: name(tokenA)            → 200ms
Итого: 20 запросов × 200ms = 4 секунды!
```

**С multicall:**
```
1 запрос: multicall.aggregate([
  balanceOf(user, tokenA),
  balanceOf(user, tokenB),
  ...
]) → 200ms
```

**Как работает:**
```
Multicall контракт (задеплоен на каждом chain по известному адресу):
1. Принимает массив (target, callData)
2. Для каждого элемента делает staticcall в target с callData
3. Возвращает массив результатов
```

**wagmi — автоматически через `useReadContracts`:**

```tsx
import { useReadContracts } from 'wagmi'

function Portfolio({ tokenList, userAddress }: Props) {
  const { data, isLoading } = useReadContracts({
    contracts: tokenList.flatMap(token => [
      {
        address: token.address,
        abi: erc20Abi,
        functionName: 'balanceOf',
        args: [userAddress],
      },
      {
        address: token.address,
        abi: erc20Abi,
        functionName: 'symbol',
      },
    ]),
  })

  // data = [balanceA, symbolA, balanceB, symbolB, ...]

  if (isLoading) return <div>Загрузка...</div>

  return (
    <ul>
      {tokenList.map((token, i) => (
        <li key={token.address}>
          {data?.[i * 2 + 1]}: {formatUnits(data?.[i * 2] ?? 0n, token.decimals)}
        </li>
      ))}
    </ul>
  )
}
```

**viem — напрямую:**

```ts
import { multicall } from 'viem/actions'

const results = await multicall(publicClient, {
  contracts: [
    { address: tokenA, abi: erc20Abi, functionName: 'balanceOf', args: [userAddress] },
    { address: tokenB, abi: erc20Abi, functionName: 'balanceOf', args: [userAddress] },
  ],
  multicallAddress: '0xcA11bde05977b3631167028862bE2a173976CA11', // Multicall3
})
```

**Multicall3 — стандартный адрес на всех EVM-сетях:**
- Адрес: `0xcA11bde05977b3631167028862bE2a173976CA11`
- Деплоен на Ethereum, Arbitrum, Optimism, Polygon, BSC, Avalanche и сотнях других
- Поддерживает `aggregate3` — каждая неудачная под-выборка не рушит весь multicall

**Когда не нужен multicall:**
- Один-два запроса — оверхед multicall не оправдан
- Запросы требуют разных `blockNumber` (multicall — один блок для всех подзапросов)

### Что хотят услышать

✅ Multicall = много eth_call в одном RPC-запросе
✅ `useReadContracts` из wagmi делает это автоматически
✅ Multicall3: адрес `0xcA11b0...`, доступен на всех сетях
✅ Экономия: 20 запросов → 1 запрос
✅ Когда НЕ нужен multicall

---

## 💰 DeFi

---

## 19. Как работает Uniswap? Что такое AMM?

**Уровень:** Middle

### Что спрашивают на самом деле

Понимаешь ли ты DeFi на уровне, достаточном для написания фронтенда свопа? Это не вопрос «расскажи формулу» — ждут понимание всего flow.

### Развёрнутый ответ

**Uniswap** — децентрализованная биржа (DEX), работающая по модели **AMM (Automated Market Maker)**. Вместо книги ордеров (как на Binance) используется математическая формула.

**Формула постоянного произведения (x × y = k):**
```
В пуле лежит x токенов A и y токенов B
k = x × y — константа, которая НЕ меняется при свопах

Ты покупаешь Δx токенов A. Сколько заплатишь (Δy)?
Новое количество A: x - Δx
Новое количество B: k / (x - Δx) = y + Δy
Δy = k / (x - Δx) - y
```

**Пример с числами:**
```
Пул ETH/USDC: 10 ETH × 20 000 USDC, k = 200 000
Покупаю 1 ETH:
  Новый баланс ETH: 9
  Новый баланс USDC: 200 000 / 9 ≈ 22 222
  Плачу: 22 222 - 20 000 = 2 222 USDC

Покупаю ещё 1 ETH:
  Новый баланс ETH: 8
  Новый баланс USDC: 200 000 / 8 = 25 000
  Плачу: 25 000 - 22 222 = 2 778 USDC  ← дороже!
```

**Ключевые сущности для фронтендера:**

1. **Router** (`SwapRouter` в V3, `UniswapV2Router02` в V2):
   - `swapExactTokensForTokens(amountIn, amountOutMin, path, to, deadline)`
   - `amountOutMin` — минимальное количество, которое ты готов получить (slippage protection)
   - `deadline` — через сколько секунд транзакция станет невалидной

2. **Quoter** (только чтение, off-chain):
   - `quoteExactInputSingle(tokenIn, tokenOut, fee, amountIn, sqrtPriceLimitX96)`
   - Возвращает ожидаемое количество output-токенов
   - Вызывается перед свопом, чтобы показать пользователю курс

3. **Pool** (контракт пары токенов):
   - Хранит резервы и цену
   - `slot0()` в V3: sqrtPriceX96 (текущая цена), tick, observationIndex

**Frontend flow свопа:**

```tsx
function SwapComponent() {
  // 1. Котировка (quote) — читаем, сколько получим
  const { data: quote } = useReadContract({
    address: quoterAddress,
    abi: quoterAbi,
    functionName: 'quoteExactInputSingle',
    args: [tokenIn, tokenOut, fee, amountIn, 0n],
  })
  // quote = 1 850 000 000n (ожидаемое количество USDC)

  // 2. Рассчитываем amountOutMin с учётом slippage (например, 0.5%)
  const slippageBps = 50n  // 0.5% = 50 bps
  const amountOutMin = quote
    ? quote - (quote * slippageBps) / 10000n
    : 0n

  // 3. Своп — одна транзакция (если уже есть approve)
  const { writeContract } = useWriteContract()

  const swap = () => {
    writeContract({
      address: swapRouterAddress,
      abi: swapRouterAbi,
      functionName: 'exactInputSingle',
      args: [{
        tokenIn,
        tokenOut,
        fee: 3000, // 0.3%
        recipient: userAddress,
        deadline: BigInt(Math.floor(Date.now() / 1000) + 1200), // 20 минут
        amountIn,
        amountOutMinimum: amountOutMin,
        sqrtPriceLimitX96: 0n, // без лимита цены
      }],
    })
  }
}
```

**Uniswap V2 vs V3:**
- **V2:** простое x×y=k, вся ликвидность по всей кривой (0 → ∞). Низкая эффективность капитала.
- **V3:** концентрированная ликвидность — LP выбирают диапазон цены (tick range). Выше эффективность капитала, но сложнее для LP (impermanent loss выше).
- **V4 (скоро):** хуки (hooks) — кастомная логика на каждом свопе, синглтон-пул (весь V4 в одном контракте).

### Что хотят услышать

✅ AMM: x×y=k, нет книги ордеров
✅ Цена меняется нелинейно (slippage из-за размера сделки)
✅ Router, Quoter, Pool — роли контрактов
✅ Flow свопа: quote → slippage → amountOutMin → swap
✅ V2 (простой) vs V3 (концентрированная ликвидность)

---

## 20. Что такое slippage и как его обрабатывать на фронтенде?

**Уровень:** Middle

### Развёрнутый ответ

**Slippage (проскальзывание)** — разница между ожидаемой ценой и реальной ценой исполнения свопа.

**Две причины slippage:**

1. **Price impact** — твоя сделка настолько большая относительно пула, что сама двигает цену. Чем больше `amountIn / poolLiquidity`, тем выше price impact.

2. **Фронтраннинг/сэндвич** — кто-то вставил свою транзакцию перед твоей и изменил состояние пула.

**Формула расчёта price impact (приближённая):**
```
priceImpact = amountIn / (poolReserve + amountIn)
```
Если в пуле 100 ETH, а ты покупаешь 10 ETH → price impact ~9%.

**Как обрабатывать на фронтенде:**

```tsx
function SlippageControl() {
  const [slippage, setSlippage] = useState(0.5) // 0.5% default
  const [isAuto, setIsAuto] = useState(true)

  return (
    <div className="slippage-settings">
      <span>Slippage Tolerance</span>

      <div className="slippage-options">
        <button onClick={() => { setSlippage(0.1); setIsAuto(true) }}>0.1%</button>
        <button onClick={() => { setSlippage(0.5); setIsAuto(true) }}>0.5%</button>
        <button onClick={() => { setSlippage(1.0); setIsAuto(true) }}>1.0%</button>

        <div className="custom">
          <input
            type="number"
            value={isAuto ? '' : slippage}
            onChange={e => {
              setIsAuto(false)
              setSlippage(Number(e.target.value))
            }}
            placeholder="Кастом"
          />
          <span>%</span>
        </div>
      </div>

      {/* Предупреждения */}
      {slippage < 0.1 && (
        <div className="warning">⚠️ Слишком низкий slippage: своп может не выполниться</div>
      )}
      {slippage > 5 && (
        <div className="warning error">🔴 Высокий slippage: вы можете потерять до {slippage}%!</div>
      )}
    </div>
  )
}
```

**Price impact — предупреждения:**

```tsx
function PriceImpactWarning({ impact }: { impact: number }) {
  if (impact > 15) return (
    <div className="error-box">
      🔴 Price impact {impact.toFixed(2)}% — своп невозможен
    </div>
  )

  if (impact > 5) return (
    <div className="error-box">
      🔴 Очень высокий price impact: {impact.toFixed(2)}%
      Вы потеряете значительную сумму. Рекомендуем уменьшить размер сделки.
    </div>
  )

  if (impact > 2) return (
    <div className="warning-box">
      🟡 Высокий price impact: {impact.toFixed(2)}%
    </div>
  )

  return null
}
```

**Расчёт amountOutMin (защита от slippage):**

```ts
const amountOutMin = expectedAmount - (expectedAmount * BigInt(Math.floor(slippage * 100))) / 10000n
// slippage 0.5% = (expectedAmount * 50) / 10000

// ВАЖНО: slippage + price impact — это разные вещи!
// - price impact: показывает, насколько цена изменится от твоей сделки
// - slippage tolerance: твой лимит на проскальзывание (включая MEV)
// Если price impact 1%, а slippage 0.5% — транзакция вероятно ревертнется!
```

### Что хотят услышать

✅ Slippage = разница между ожидаемой и реальной ценой
✅ Price impact vs slippage tolerance
✅ amountOutMin для защиты
✅ UI: выбор slippage, предупреждения при высоких значениях
✅ Взаимосвязь: если slippage tolerance < price impact → revert

---

## 21. Что такое MEV и sandwich attack?

**Уровень:** Middle/Senior

### Развёрнутый ответ

**MEV (Maximal Extractable Value)** — прибыль, которую можно извлечь из манипуляции порядком транзакций в блоке.

**Sandwich attack (самая распространённая MEV-атака):**

```
Мемпул (публичный):
  1. Жертва: swap 10 ETH → USDC (покупает ETH)
  2. ...

Атакующий видит транзакцию жертвы и вставляет ДВЕ своих:

  Блок:
  ┌─────────────────────────────────────┐
  │ 1. Атакующий: swap USDC → ETH       │ ← frontrun: покупает ETH до жертвы
  │ 2. Жертва: swap USDC → ETH          │ ← жертва покупает по худшей цене
  │ 3. Атакующий: swap ETH → USDC       │ ← backrun: продаёт ETH после жертвы
  └─────────────────────────────────────┘

  Результат:
  - Жертва: получила меньше ETH, чем ожидала
  - Атакующий: прибыль = разница в курсе - газ
```

**Как защищаться на уровне пользователя:**
1. **Slippage tolerance** — установить разумный (0.5–1%). Если слишком низкий — жертва сэндвича. Слишком высокий — теряешь на проскальзывании.
2. **Flashbots Protect** — отправить транзакцию в приватный мемпул, а не публичный.

**Как поддержать на фронтенде:**

```tsx
// Отправка через Flashbots (приватный мемпул)
import { FlashbotsBundleProvider } from '@flashbots/ethers-provider-bundle'

async function sendPrivateTx(tx: TransactionRequest) {
  // Вариант 1: Flashbots RPC (mev-protect)
  const client = createPublicClient({
    transport: http('https://rpc.mevblocker.io'), // MEV Blocker
  })

  // Вариант 2: Flashbots Bundle
  const flashbots = await FlashbotsBundleProvider.create(provider, authSigner)
  const signedTx = await wallet.signTransaction(tx)
  const bundle = await flashbots.sendBundle([
    { signedTransaction: signedTx },
  ], targetBlock + 5)

  return bundle
}

// UI-опция для пользователя:
<div className="tx-options">
  <label>
    <input type="checkbox" checked={useMEVProtection} onChange={...} />
    MEV-защита (приватная отправка)
  </label>
</div>
```

**Для фронтендера важно:**
- Показывать предупреждение при высоком slippage (>1%)
- Показывать real-time цену и ожидаемый output
- Объяснять, почему транзакция вернула меньше токенов, чем было в цитате (MEV + price impact)

### Что хотят услышать

✅ MEV = прибыль от манипуляции порядком транзакций
✅ Sandwich: frontrun + жертва + backrun в одном блоке
✅ Slippage как защита
✅ Flashbots / приватный мемпул
✅ Как информировать пользователя на фронтенде

---

## 22. Как работает стейкинг с точки зрения фронтендера?

**Уровень:** Middle

### Развёрнутый ответ

**Стейкинг** — блокировка токенов в смарт-контракте для получения наград. Существует несколько видов:

**1. Liquid Staking (Lido, Rocket Pool):**
```
Пользователь ──ETH──► Контракт Lido ──► stETH (токен-квитанция)
                                             │
                                             ▼
                                       Стейкинг в Beacon Chain
                                       Награды → увеличение курса stETH/ETH
```

**2. DeFi Staking/Yield Farming:**
```
Пользователь ──LP-токены──► Staking-контракт ──► Награды (обычно governance-токены)
```

**Фронтенд для liquid staking (stake ETH → stETH):**

```tsx
function StakeETH() {
  const [amount, setAmount] = useState('')
  const { writeContract, isPending } = useWriteContract()

  const { data: stEthBalance } = useReadContract({
    address: stEthAddress,
    abi: stEthAbi,
    functionName: 'balanceOf',
    args: [userAddress],
  })

  const stake = () => {
    writeContract({
      address: lidoAddress,
      abi: lidoAbi,
      functionName: 'submit',
      args: [referralAddress], // реферал (опционально)
      value: parseEther(amount), // ETH прилагается к транзакции!
    })
  }

  return (
    <div>
      <input
        type="number"
        value={amount}
        onChange={e => setAmount(e.target.value)}
        placeholder="Количество ETH"
      />
      <button onClick={stake} disabled={isPending}>
        {isPending ? 'Подтверждение...' : 'Stake'}
      </button>
      <div>Ваш stETH: {stEthBalance ? formatEther(stEthBalance) : '0'}</div>
    </div>
  )
}
```

**DeFi Staking с наградами:**

```tsx
function FarmStaking() {
  const { writeContract } = useWriteContract()

  // 1. Stake LP-токены
  const stake = () => {
    writeContract({
      address: farmAddress,
      abi: farmAbi,
      functionName: 'stake',
      args: [amount],
    })
  }

  // 2. Claim наград
  const claim = () => {
    writeContract({
      address: farmAddress,
      abi: farmAbi,
      functionName: 'getReward',
    })
  }

  // 3. Чтение данных
  const { data: stakedBalance } = useReadContract({ /* userInfo */ })
  const { data: earnedRewards } = useReadContract({ /* earned */ })
  const { data: apr } = useReadContract({ /* rewardRate / totalStaked */ })

  return (
    <div>
      <div>Застейкано: {formatEther(stakedBalance ?? 0n)} LP</div>
      <div>Награды: {formatEther(earnedRewards ?? 0n)} TOKEN</div>
      <div>APR: {apr}%</div>
      <button onClick={stake}>Stake</button>
      <button onClick={claim}>Claim Rewards</button>
    </div>
  )
}
```

**Unstake с задержкой (cooldown):**

```tsx
function UnstakeWithCooldown() {
  // Шаг 1: Запросить вывод (начинает cooldown)
  const { writeContract: requestWithdraw } = useWriteContract()

  // Шаг 2: Проверить, можно ли вывести
  const { data: canWithdraw } = useReadContract({
    address: stakingAddress,
    abi: stakingAbi,
    functionName: 'canWithdraw',
    args: [userAddress],
  })

  // Шаг 3: Вывести
  const { writeContract: withdraw } = useWriteContract()

  // Cooldown timer
  const { data: cooldownEnd } = useReadContract({
    address: stakingAddress,
    abi: stakingAbi,
    functionName: 'cooldownEnds',
    args: [userAddress],
  })

  return (
    <div>
      {!canWithdraw && (
        <button onClick={() => requestWithdraw({ /* ... */ })}>
          Request Withdraw
        </button>
      )}
      {canWithdraw && (
        <>
          <div>Cooldown ends: {new Date(Number(cooldownEnd) * 1000).toLocaleString()}</div>
          <button onClick={() => withdraw({ /* ... */ })}>Withdraw</button>
        </>
      )}
    </div>
  )
}
```

### Что хотят услышать

✅ Два типа: liquid staking (stETH) и DeFi farming (награды governance-токенами)
✅ Stake → получение токенов-квитанций / начисление наград
✅ Claim rewards, unstake с cooldown
✅ Отображение APR/APY, наград, истории
✅ Unstake с задержкой и UX для этого

---

## 23. Что такое Permit (EIP-2612) и как это упрощает UX свопа?

**Уровень:** Senior

### Развёрнутый ответ

**Проблема:** обычный своп требует двух транзакций:
1. `approve(router, amount)` — разрешить тратить токены
2. `swap(...)` — сам своп

Две транзакции = двойной газ + двойное ожидание. Ужасный UX.

**Permit (EIP-2612)** — gasless approve через подпись. Пользователь подписывает сообщение (бесплатно, мгновенно), и своп выполняется в одной транзакции, которая внутри себя вызывает `permit()` + `transferFrom()`.

**Как работает:**

```
Без permit:
  1. approve(spender, amount)      ← транзакция (платно)
  2. swap(...)                     ← транзакция (платно)

С permit:
  1. signTypedData(permitMsg)      ← подпись (бесплатно)
  2. swap(..., permitSignature)    ← ОДНА транзакция!
     Внутри свопа: permit(owner, spender, amount, deadline, v, r, s)
     Затем: transferFrom(owner, pool, amount)
```

**Реализация на фронтенде:**

```tsx
import { useSignTypedData } from 'wagmi'

function SwapWithPermit() {
  const { signTypedDataAsync } = useSignTypedData()

  const swap = async () => {
    const deadline = BigInt(Math.floor(Date.now() / 1000) + 1200)

    // 1. Получаем nonce для permit (нужен правильный nonce)
    const nonce = await publicClient.readContract({
      address: tokenAddress,
      abi: erc20PermitAbi,
      functionName: 'nonces',
      args: [userAddress],
    })

    // 2. Подписываем permit
    const signature = await signTypedDataAsync({
      domain: {
        name: 'USD Coin',
        version: '1',
        chainId: chainId,
        verifyingContract: tokenAddress,
      },
      types: {
        Permit: [
          { name: 'owner', type: 'address' },
          { name: 'spender', type: 'address' },
          { name: 'value', type: 'uint256' },
          { name: 'nonce', type: 'uint256' },
          { name: 'deadline', type: 'uint256' },
        ],
      },
      primaryType: 'Permit',
      message: {
        owner: userAddress,
        spender: swapRouterAddress,
        value: amountToSwap,
        nonce: nonce,
        deadline: deadline,
      },
    })

    // 3. Расшифровываем подпись в r, s, v
    const { r, s, v } = parseSignature(signature)

    // 4. Своп с permit — ОДНА транзакция!
    writeContract({
      address: swapRouterWithPermit,
      abi: swapRouterAbi,
      functionName: 'swapWithPermit',
      args: [
        tokenIn, tokenOut, amountIn, amountOutMin,
        deadline, v, r, s, // permit-подпись
      ],
    })
  }
}
```

**Dai-style Permit (для токенов, не поддерживающих EIP-2612):**

```tsx
// Dai использует permit(holder, spender, nonce, expiry, allowed, v, r, s)
// Важно: nonce у Dai — не счётчик, а случайное число (для защиты от replay)

const nonce = ethers.hexlify(ethers.randomBytes(32)) // уникальный каждый раз!
```

**Permit2 (Uniswap) — универсальный permit:**

```
Permit2 — отдельный контракт, через который можно делать permit для ЛЮБОГО ERC-20,
даже если он не поддерживает EIP-2612.

1. approve(Permit2, maxUint256) — один раз на все токены
2. signPermit2 — подпись на конкретный трансфер
3. swap с Permit2 — все свопы через единую подпись
```

### Что хотят услышать

✅ Permit заменяет approve-транзакцию подписью (газ-экономия)
✅ EIP-2612: EIP-712 typed data подпись
✅ Flow: nonce → signTypedData → parseSignature → одна tx
✅ Dai-style permit с random nonce
✅ Permit2 от Uniswap — универсальное решение
✅ UX: две транзакции → одна транзакция

---

## 🔒 Безопасность

---

## 24. Какие типичные уязвимости смарт-контрактов ты знаешь?

**Уровень:** Middle

### Развёрнутый ответ

Фронтендер не обязан быть аудитором, но должен знать основные уязвимости, чтобы:
- Не продвигать скам-контракты
- Понимать предупреждения MetaMask/Revoke.cash
- Осмысленно отвечать на собеседовании

**1. Reentrancy (повторный вход)**
```solidity
// Уязвимый контракт
function withdraw() public {
    uint256 amount = balances[msg.sender];
    (bool success, ) = msg.sender.call{value: amount}(""); // ← вызов ДО обнуления баланса!
    require(success);
    balances[msg.sender] = 0; // ← слишком поздно!
}

// Атакующий контракт
receive() external payable {
    if (address(victim).balance > 0) {
        victim.withdraw(); // ← повторный вход!
    }
}
// Защита: Check-Effects-Interactions паттерн, ReentrancyGuard
```

**2. Integer Overflow/Underflow** (в Solidity <0.8)
```solidity
// Solidity 0.7: 255 + 1 = 0 (переполнение)
uint8 x = 255;
x++; // x = 0!
// Solidity 0.8+: встроенная проверка, revert
```

**3. Frontrunning**
```
// Пользователь отправляет решение викторины
// Атакующий видит в мемпуле → копирует → даёт газ выше
// Решение атакующего исполняется первым → приз уходит ему
```

**4. Access Control**
```solidity
function setOwner(address newOwner) external {
    // Забыли проверку: onlyOwner!
    owner = newOwner; // любой может стать владельцем
}
```

**5. Unchecked External Call**
```solidity
function sendEth(address to, uint256 amount) public {
    to.call{value: amount}(""); // ← не проверяем success!
    // Если вызов упал — думаем, что ETH ушли, а они нет
}
```

**6. Phishing / Approval Scam**
```
Пользователь заходит на фейковый сайт Uniswap
Подписывает approve(scamContract, maxUint256)
Скам-контракт забирает ВСЕ токены через transferFrom
```

**Для фронтендера — что делать:**
- Проверять адрес контракта на Etherscan (verified, не прокси на скам)
- Показывать пользователю, что именно он approve-ит
- Рекомендовать Revoke.cash для проверки и отзыва approvals
- Использовать `transaction-simulation` перед подписью (Wallet Guard, Pocket Universe)

### Что хотят услышать

✅ Reentrancy: причина, пример, защита (CEI, ReentrancyGuard)
✅ Overflow/underflow: проблема в <0.8, фикс в 0.8+
✅ Frontrunning: мемпул, опережение
✅ Access control: забытая проверка onlyOwner
✅ Phishing через approve: как защищаться

---

## 25. Как защитить пользователя от фишинговой транзакции на фронтенде?

**Уровень:** Middle/Senior

### Развёрнутый ответ

**Уровни защиты:**

**1. Верификация контрактов (Etherscan)**
```tsx
function VerifiedBadge({ address }: { address: string }) {
  const [isVerified, setIsVerified] = useState(false)

  useEffect(() => {
    // Проверяем через Etherscan API
    fetch(`https://api.etherscan.io/api?module=contract&action=getabi&address=${address}`)
      .then(r => r.json())
      .then(data => setIsVerified(data.status === '1'))
  }, [address])

  if (!isVerified) return <span className="badge-unverified">⚠️ Unverified</span>
  return <span className="badge-verified">✅ Verified</span>
}
```

**2. Симуляция транзакции перед отправкой**

```tsx
// Используем Tenderly Simulation API
async function simulateTx(tx: TransactionRequest) {
  const result = await tenderlyClient.simulateTransaction({
    from: tx.from,
    to: tx.to,
    value: tx.value,
    data: tx.data,
    blockNumber: 'latest',
  })

  // Анализируем изменения состояния
  const assetChanges = result.transaction.transactionInfo.assetChanges

  for (const change of assetChanges) {
    if (change.type === 'TRANSFER' && change.from === tx.from) {
      console.log(`⚠️ Уходят: ${change.amount} ${change.tokenInfo.symbol}`)
    }
  }

  return result
}
```

**3. Предупреждения об известных скам-адресах**

```tsx
const SCAM_ADDRESSES = new Set([
  '0x000...scam1',
  '0x000...scam2',
])

function AddressWarning({ address }: { address: string }) {
  if (SCAM_ADDRESSES.has(address.toLowerCase())) {
    return <div className="scam-warning">🚨 Этот адрес в списке мошенников!</div>
  }

  // Проверка через BlockSec / GoPlus API
  const { data: risk } = useQuery({
    queryKey: ['address-risk', address],
    queryFn: () => fetch(`https://api.gopluslabs.io/api/v1/token_security/1?contract_addresses=${address}`),
  })

  return null
}
```

**4. Человекочитаемые описания транзакций**

```tsx
function TransactionPreview({ tx }: { tx: PreparedTx }) {
  // Парсим calldata и показываем, что именно произойдёт
  const decoded = decodeTxData(tx)

  return (
    <div className="tx-preview">
      <h3>Вы собираетесь:</h3>
      {decoded.type === 'approve' && (
        <div>
          <span className="action">Разрешить</span>
          <span className="address">{decoded.spender}</span>
          <span className="danger">
            тратить {decoded.amount === 'unlimited' ? 'ВСЕ ваши токены' : decoded.amount}
          </span>
        </div>
      )}
      {decoded.type === 'swap' && (
        <div>
          <span>Обменять {decoded.amountIn} {decoded.tokenIn}</span>
          <span>на ~{decoded.amountOut} {decoded.tokenOut}</span>
        </div>
      )}
    </div>
  )
}
```

**5. Рекомендации по отзыву approvals после взаимодействия**

```tsx
function PostSwapReminder() {
  const [showReminder, setShowReminder] = useState(false)

  // Показываем напоминание после свопа
  return (
    <div>
      {showReminder && (
        <div className="reminder">
          <p>Вы дали infinite approval контракту. Рекомендуем отозвать ненужные разрешения:</p>
          <a href="https://revoke.cash" target="_blank">Revoke.cash →</a>
        </div>
      )}
    </div>
  )
}
```

### Что хотят услышать

✅ Верификация контракта на Etherscan
✅ Симуляция транзакции (Tenderly)
✅ Проверка адресов по базам скама
✅ Декодирование calldata → человекочитаемое описание
✅ Предупреждения о infinite approval + ссылка на Revoke.cash

---

## 26. Что такое reentrancy и как от неё защищаются?

**Уровень:** Middle

### Развёрнутый ответ

**Reentrancy** — атака, при которой контракт A вызывает контракт B, а B в ответ вызывает A снова — до того как A завершил первое выполнение.

**Классический пример (DAO Hack, 2016):**
```solidity
// Уязвимый контракт
contract VulnerableBank {
    mapping(address => uint) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() external {
        uint amount = balances[msg.sender];
        require(amount > 0);

        // ❌ Ошибка: отправляем ETH ДО обнуления баланса
        (bool sent, ) = msg.sender.call{value: amount}("");
        require(sent);

        balances[msg.sender] = 0; // срабатывает слишком поздно!
    }
}

// Контракт атакующего
contract Attacker {
    VulnerableBank bank;

    constructor(address _bank) { bank = VulnerableBank(_bank); }

    function attack() external payable {
        bank.deposit{value: 1 ether}();
        bank.withdraw();
    }

    receive() external payable {
        // Пока в банке есть ETH — продолжаем выводить!
        if (address(bank).balance >= 1 ether) {
            bank.withdraw();
        }
    }
}
```

**Как это работает:**
```
1. Attacker.attack() → deposit(1 ETH) → withdraw()
2. Bank.withdraw(): проверяет баланс → 1 ETH ✅
3. Bank отправляет 1 ETH → Attacker.receive()
4. Attacker.receive() → Bank.withdraw() ← ПОВТОРНЫЙ ВХОД!
5. Bank.withdraw(): проверяет баланс → всё ещё 1 ETH (не обнулён!) ✅
6. Bank отправляет ещё 1 ETH...
...повторяется, пока не кончатся все ETH в Bank.
```

**Защита 1: Check-Effects-Interactions (CEI)**
```solidity
function withdraw() external {
    uint amount = balances[msg.sender];
    require(amount > 0);

    // 1. Check — проверка (уже сделали)
    // 2. Effects — меняем состояние ДО внешнего вызова
    balances[msg.sender] = 0;

    // 3. Interactions — внешний вызов ПОСЛЕДНИМ
    (bool sent, ) = msg.sender.call{value: amount}("");
    require(sent);
}
```

**Защита 2: ReentrancyGuard (OpenZeppelin)**
```solidity
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract SafeBank is ReentrancyGuard {
    function withdraw() external nonReentrant {
        uint amount = balances[msg.sender];
        require(amount > 0);

        balances[msg.sender] = 0;

        (bool sent, ) = msg.sender.call{value: amount}("");
        require(sent);
    }
}
// nonReentrant модификатор: при повторном входе → revert
```

**Защита 3: Pull over Push**
```solidity
// Вместо отправки ETH каждому — пусть сами забирают
function withdraw(uint amount) external {
    require(balances[msg.sender] >= amount);
    balances[msg.sender] -= amount;
    payable(msg.sender).transfer(amount); // transfer ограничен 2300 gas — reentrancy невозможна
}
```

### Что хотят услышать

✅ Механизм: внешний вызов до обновления состояния → повторный вход
✅ CEI (Check-Effects-Interactions) — главная защита
✅ ReentrancyGuard (OpenZeppelin)
✅ transfer/send (2300 gas limit) — дополнительная защита, но менее гибкая
✅ Исторический пример: DAO Hack (2016)

---

## 27. Почему нельзя использовать Math.random() или Date.now() для рандома в контракте?

**Уровень:** Middle/Senior

### Развёрнутый ответ

Блокчейн **детерминирован**: все ноды должны прийти к одинаковому результату. Если контракт использует случайность — ноды не смогут договориться о состоянии.

**Проблема `block.timestamp`:**
```solidity
// ❌ НЕбезопасно
function random() public view returns (uint) {
    return uint(keccak256(abi.encodePacked(block.timestamp, block.difficulty)));
}
// Майнер/валидатор может манипулировать timestamp в пределах ~900 секунд!
```

**Проблема `blockhash`:**
```solidity
// ❌ Всё ещё небезопасно
function random() public view returns (uint) {
    return uint(keccak256(abi.encodePacked(blockhash(block.number - 1), msg.sender)));
}
// Валидатор знает blockhash заранее и может решить — включать транзакцию или нет
```

**Почему это важно фронтендеру:**
Когда делаешь фронтенд для лотереи, NFT-drops, гейминга — нужно понимать, что настоящий рандом на блокчейне невозможен без оракула.

**Решения:**

**1. Chainlink VRF (Verifiable Random Function)**
```solidity
// Правильный способ: запрос рандома у Chainlink
function requestRandomWords() external returns (uint256 requestId) {
    return COORDINATOR.requestRandomWords(
        keyHash,
        s_subscriptionId,
        requestConfirmations,  // ждём N блоков
        callbackGasLimit,
        numWords              // сколько случайных слов
    );
}

function fulfillRandomWords(
    uint256 requestId,
    uint256[] memory randomWords
) internal override {
    // randomWords содержат ДОКАЗУЕМО случайные числа
    uint winner = randomWords[0] % participants.length;
}
```

**2. Commit-Reveal схема (без оракула)**
```
1. Commit: все участники отправляют hash(свой_вклад + secret)
2. Reveal: все раскрывают свои вклады
3. Результат: xor всех вкладов → случайное число

Недостаток: последний раскрывший может отказаться → нужен депозит
```

**3. Для некритичных случаев (игры с низкими ставками):**
```solidity
// Относительно приемлемо для низких ставок
uint random = uint(keccak256(abi.encodePacked(
    block.prevrandao,  // случайное значение от Beacon Chain (раньше block.difficulty)
    block.timestamp,
    msg.sender,
    nonce++
)));
```

### Что хотят услышать

✅ Блокчейн детерминирован — настоящего рандома нет
✅ block.timestamp и blockhash манипулируемы валидатором
✅ Chainlink VRF — стандартное решение
✅ Commit-Reveal для децентрализованного рандома
✅ block.prevrandao вместо block.difficulty (после The Merge)

---

## 28. Как работает подпись сообщений (EIP-712) и зачем она нужна?

**Уровень:** Senior

### Развёрнутый ответ

**EIP-712** — стандарт типизированных подписей. Вместо подписи сырых байтов пользователь подписывает **структурированные данные**, которые MetaMask показывает в человекочитаемом виде.

**Без EIP-712:**
```
MetaMask показывает: "Sign this message? 0xabc123def456..."
Пользователь: что я подписываю? Непонятно. → фишинг-риск!
```

**С EIP-712:**
```
MetaMask показывает:
  Domain: MyDApp
  Action: Swap
  Token In: 100 USDC
  Token Out: 0.05 ETH
  Deadline: 2026-07-19 15:30

Пользователь: ясно, подписываю!
```

**Структура EIP-712:**

```solidity
// Контракт — верификация
contract SignatureVerifier {
    bytes32 private constant PERMIT_TYPEHASH = keccak256(
        "Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)"
    );
    bytes32 private immutable DOMAIN_SEPARATOR;

    constructor() {
        DOMAIN_SEPARATOR = keccak256(abi.encode(
            keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
            keccak256(bytes("MyToken")),
            keccak256(bytes("1")),
            block.chainid,
            address(this)
        ));
    }

    function verify(
        address owner, address spender, uint256 value,
        uint256 deadline, uint8 v, bytes32 r, bytes32 s
    ) internal view returns (bool) {
        bytes32 structHash = keccak256(abi.encode(
            PERMIT_TYPEHASH, owner, spender, value, nonces[owner], deadline
        ));
        bytes32 digest = keccak256(abi.encodePacked("\x19\x01", DOMAIN_SEPARATOR, structHash));
        address signer = ecrecover(digest, v, r, s);
        return signer == owner;
    }
}
```

**Фронтенд — подпись EIP-712:**

```tsx
import { useSignTypedData } from 'wagmi'

function SignPermit() {
  const { signTypedDataAsync } = useSignTypedData()

  const sign = async () => {
    const signature = await signTypedDataAsync({
      domain: {
        name: 'MyDApp',
        version: '1',
        chainId: await getChainId(),
        verifyingContract: '0x...',
      },
      types: {
        Swap: [
          { name: 'tokenIn', type: 'address' },
          { name: 'tokenOut', type: 'address' },
          { name: 'amountIn', type: 'uint256' },
          { name: 'minAmountOut', type: 'uint256' },
          { name: 'deadline', type: 'uint256' },
        ],
      },
      primaryType: 'Swap',
      message: {
        tokenIn: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        tokenOut: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        amountIn: 100000000n, // 100 USDC
        minAmountOut: 50000000000000000n, // 0.05 ETH
        deadline: BigInt(Math.floor(Date.now() / 1000) + 1200),
      },
    })
    // signature = "0x..."
  }
}
```

**Типичные use-case'ы:**
- **Permit (газлесс approve)**
- **Газлесс транзакции** (пользователь подписывает, relayer платит газ)
- **Аутентификация** (доказательство владения адресом: «войти через кошелёк»)
- **Ордера (limit orders)** — пользователь подписывает офчейн, исполнитель платит газ
- **Snapshots/голосования** — подпись вместо транзакции для governance

**Верификация на бэкенде (если нужно проверить подпись на сервере):**

```ts
import { verifyTypedData } from 'viem'

const valid = await verifyTypedData({
  address: expectedSigner,
  domain: { /* ... */ },
  types: { /* ... */ },
  primaryType: 'Swap',
  message: { /* ... */ },
  signature,
})
```

### Что хотят услышать

✅ EIP-712 = типизированные структурированные подписи
✅ MetaMask показывает domain + message в читаемом виде → защита от фишинга
✅ DOMAIN_SEPARATOR: name, version, chainId, verifyingContract
✅ `signTypedData` / `signTypedDataAsync` в wagmi/viem
✅ Use-case'ы: Permit, газлесс tx, аутентификация, ордера

---

## 🛠️ Практические задачи

---

## 29. Напиши компонент: баланс ERC-20 + отправка токенов

**Уровень:** Middle (живое кодирование на собеседовании)

### Что спрашивают на самом деле

Могут дать эту задачу на live coding. Проверяют: знаешь ли wagmi API, обрабатываешь ли все состояния, валидируешь ли ввод, форматируешь ли decimals. Ждут рабочий код за 15–20 минут.

### Эталонное решение

```tsx
import { useState } from 'react'
import {
  useAccount,
  useReadContract,
  useWriteContract,
  useWaitForTransactionReceipt,
} from 'wagmi'
import { erc20Abi } from 'viem'
import { formatUnits, parseUnits, isAddress } from 'viem'

// Предположим, что decimals известны и токен стандартный ERC-20
const TOKEN_ADDRESS = '0x1234...' as const
const TOKEN_DECIMALS = 18
const TOKEN_SYMBOL = 'TKN'

export function TokenTransfer() {
  const { address, isConnected } = useAccount()
  const [recipient, setRecipient] = useState('')
  const [amount, setAmount] = useState('')
  const [error, setError] = useState<string | null>(null)

  // Чтение баланса
  const { data: balance, refetch: refetchBalance } = useReadContract({
    address: TOKEN_ADDRESS,
    abi: erc20Abi,
    functionName: 'balanceOf',
    args: address ? [address] : undefined,
    query: { enabled: Boolean(address) },
  })

  // Отправка
  const {
    writeContract,
    data: txHash,
    isPending: isWalletPending,
  } = useWriteContract()

  const {
    isLoading: isConfirming,
    isSuccess: isConfirmed,
  } = useWaitForTransactionReceipt({ hash: txHash })

  const handleSend = () => {
    setError(null)

    // Валидация
    if (!isAddress(recipient)) {
      setError('Некорректный адрес получателя')
      return
    }

    const parsedAmount = parseUnits(amount, TOKEN_DECIMALS)
    if (parsedAmount <= 0n) {
      setError('Сумма должна быть больше 0')
      return
    }

    if (balance !== undefined && parsedAmount > balance) {
      setError('Недостаточно токенов')
      return
    }

    writeContract({
      address: TOKEN_ADDRESS,
      abi: erc20Abi,
      functionName: 'transfer',
      args: [recipient as `0x${string}`, parsedAmount],
    })
  }

  // После успешной отправки — обновляем баланс
  if (isConfirmed) {
    // В реальном коде: queryClient.invalidateQueries
    refetchBalance()
  }

  // Состояния кнопки
  const buttonText = (() => {
    if (!isConnected) return 'Подключите кошелёк'
    if (isWalletPending) return 'Подтвердите в кошельке...'
    if (isConfirming) return 'Отправляется...'
    if (isConfirmed) return '✅ Отправлено!'
    return 'Отправить'
  })()

  const isDisabled = !isConnected || isWalletPending || isConfirming

  const formattedBalance = balance !== undefined
    ? Number(formatUnits(balance, TOKEN_DECIMALS)).toLocaleString(undefined, {
        maximumFractionDigits: 4,
      })
    : '—'

  return (
    <div className="token-transfer">
      <h3>Отправка {TOKEN_SYMBOL}</h3>

      <div className="balance">
        Баланс: {formattedBalance} {TOKEN_SYMBOL}
      </div>

      <div className="form">
        <input
          type="text"
          placeholder="0x..."
          value={recipient}
          onChange={e => setRecipient(e.target.value)}
          disabled={isDisabled}
        />

        <input
          type="number"
          placeholder="0.0"
          value={amount}
          onChange={e => setAmount(e.target.value)}
          disabled={isDisabled}
          min="0"
          step="any"
        />
        <button
          onClick={() => setAmount(formatUnits(balance ?? 0n, TOKEN_DECIMALS))}
          disabled={isDisabled}
        >
          MAX
        </button>

        <button onClick={handleSend} disabled={isDisabled}>
          {buttonText}
        </button>
      </div>

      {error && <div className="error">{error}</div>}
      {txHash && (
        <div className="tx-link">
          Tx: <a href={`https://etherscan.io/tx/${txHash}`} target="_blank">
            {txHash.slice(0, 10)}...{txHash.slice(-8)}
          </a>
        </div>
      )}
    </div>
  )
}
```

### Что хотят увидеть

✅ Правильное использование `useReadContract` и `useWriteContract`
✅ `formatUnits` / `parseUnits` для работы с decimals
✅ Валидация: адрес, сумма > 0, не больше баланса
✅ Все состояния UI: загрузка, pending, подтверждение, успех, ошибка
✅ MAX-кнопка для удобства
✅ Ссылка на Etherscan
✅ Обработка разных состояний кнопки

---

## 30. Как реализовать «Connect Wallet» с нуля без RainbowKit?

**Уровень:** Middle

### Развёрнутый ответ

Иногда нужно кастомное решение (кастомный дизайн, специфичные требования). Показываем, что понимаем, что под капотом.

```tsx
import { useConnect, useAccount, useDisconnect, useBalance, useSwitchChain } from 'wagmi'
import { injected, walletConnect } from 'wagmi/connectors'
import { mainnet, polygon, arbitrum } from 'wagmi/chains'

export function CustomConnectButton() {
  const { connect, connectors, isPending } = useConnect()
  const { address, isConnected, chainId } = useAccount()
  const { disconnect } = useDisconnect()
  const { data: balance } = useBalance({ address })
  const { switchChain } = useSwitchChain()
  const [isOpen, setIsOpen] = useState(false)

  // Отключён — показываем кнопку connect
  if (!isConnected) {
    return (
      <div className="custom-connect">
        <button onClick={() => setIsOpen(!isOpen)} className="connect-trigger">
          Connect Wallet
        </button>

        {isOpen && (
          <div className="connect-modal">
            <h3>Выберите кошелёк</h3>

            {/* MetaMask / Injected */}
            <button
              onClick={() => {
                connect({ connector: injected() })
                setIsOpen(false)
              }}
              disabled={isPending}
            >
              <img src="/metamask-icon.svg" alt="" />
              MetaMask
            </button>

            {/* WalletConnect */}
            <button
              onClick={() => {
                connect({
                  connector: walletConnect({
                    projectId: 'YOUR_PROJECT_ID',
                    showQrModal: true, // WalletConnect сам покажет QR
                  }),
                })
                setIsOpen(false)
              }}
              disabled={isPending}
            >
              <img src="/walletconnect-icon.svg" alt="" />
              WalletConnect
            </button>

            {/* Можно добавить Coinbase Wallet, Rabby и т.д. */}
          </div>
        )}
      </div>
    )
  }

  // Подключён — показываем информацию
  return (
    <div className="custom-account">
      <div className="network-badge">
        {chainId === mainnet.id && 'Ethereum'}
        {chainId === polygon.id && 'Polygon'}
        {chainId === arbitrum.id && 'Arbitrum'}
      </div>

      <div className="balance">
        {balance ? `${Number(balance.formatted).toFixed(3)} ${balance.symbol}` : '...'}
      </div>

      <button onClick={() => setIsOpen(!isOpen)} className="address-btn">
        {address?.slice(0, 6)}...{address?.slice(-4)}
      </button>

      {isOpen && (
        <div className="account-dropdown">
          <div className="account-address">{address}</div>

          <div className="network-switcher">
            <h4>Сеть</h4>
            {[mainnet, polygon, arbitrum].map(chain => (
              <button
                key={chain.id}
                onClick={() => switchChain({ chainId: chain.id })}
                className={chainId === chain.id ? 'active' : ''}
              >
                {chain.name}
              </button>
            ))}
          </div>

          <button onClick={() => disconnect()} className="disconnect-btn">
            Disconnect
          </button>
        </div>
      )}
    </div>
  )
}
```

**Что нужно помнить:**
- `injected()` — ищет `window.ethereum` (MetaMask, Rabby, Brave)
- `walletConnect()` — для мобильных кошельков, требует `projectId`
- Состояние подключения сохраняется в localStorage автоматически (wagmi)
- `useSwitchChain` — смена сети (пользователь может отклонить)
- Авто-реконнект при загрузке страницы — wagmi делает сам

### Что хотят услышать

✅ `useConnect`, `useAccount`, `useDisconnect` из wagmi
✅ `injected()` — MetaMask и подобные
✅ `walletConnect()` — для мобильных
✅ Dropdown с сетями и сменой через `useSwitchChain`
✅ Баланс ETH через `useBalance`

---

## 31. Как сделать optimistic UI при отправке транзакции?

**Уровень:** Senior

### Развёрнутый ответ

**Optimistic UI** — показываем результат сразу, не дожидаясь подтверждения блокчейна. Если транзакция сфейлилась — откатываем.

**Почему это важно:** 12 секунд на блок + финальность ~13 минут. Пользователь не должен ждать.

```tsx
function OptimisticStake() {
  const [stakedAmount, setStakedAmount] = useState(0n)  // реальный баланс из контракта
  const [optimisticAmount, setOptimisticAmount] = useState<bigint | null>(null)  // UI-состояние
  const [rollbackTimer, setRollbackTimer] = useState<NodeJS.Timeout | null>(null)

  const { writeContractAsync } = useWriteContract()
  const queryClient = useQueryClient()

  const displayAmount = optimisticAmount ?? stakedAmount  // показываем оптимистичное!

  const stake = async (amount: bigint) => {
    // 1. Оптимистичное обновление
    setOptimisticAmount(stakedAmount + amount)
    setError(null)

    try {
      // 2. Отправляем транзакцию
      const hash = await writeContractAsync({
        address: stakingAddress,
        abi: stakingAbi,
        functionName: 'stake',
        args: [amount],
      })

      // 3. Ждём подтверждения
      const receipt = await publicClient.waitForTransactionReceipt({ hash })

      if (receipt.status === 'success') {
        // 4. Подтверждено — инвалидируем кеш, получаем реальные данные
        await queryClient.invalidateQueries({ queryKey: ['stakedBalance'] })
        // wagmi перечитает balance → realAmount обновится
        setOptimisticAmount(null)  // убираем оптимистичное состояние
      } else {
        // 5. Revert — откатываем
        setOptimisticAmount(null)
        setError('Транзакция не удалась. Попробуйте снова.')
      }
    } catch (err) {
      // 6. Ошибка отправки или отклонение — откатываем
      setOptimisticAmount(null)
      if (err?.message?.includes('rejected')) {
        setError('Вы отклонили транзакцию')
      } else {
        setError('Ошибка при отправке')
      }
    }
  }

  return (
    <div>
      <div className="staked-amount">
        {/* Визуальный индикатор optimistic state */}
        Застейкано: {formatEther(displayAmount)} LP
        {optimisticAmount !== null && (
          <span className="optimistic-badge">(ожидает подтверждения)</span>
        )}
      </div>

      <button onClick={() => stake(parseEther('100'))}>
        Stake 100 LP
      </button>

      {error && <div className="error">{error}</div>}
    </div>
  )
}
```

**Более продвинутый вариант — очередь optimistic-транзакций:**

```tsx
interface OptimisticAction {
  id: string
  type: 'stake' | 'unstake' | 'claim'
  delta: bigint       // изменение баланса
  txHash?: string     // появится после отправки
  status: 'optimistic' | 'pending' | 'confirmed' | 'failed'
}

function useOptimisticBalance(contractBalance: bigint) {
  const [actions, setActions] = useState<OptimisticAction[]>([])

  // Результирующий баланс = реальный + сумма optimistic deltas
  const displayBalance = actions
    .filter(a => a.status !== 'failed')
    .reduce((sum, a) => sum + a.delta, contractBalance)

  const addOptimistic = (action: OptimisticAction) => {
    setActions(prev => [...prev, action])
  }

  const confirmAction = (id: string, txHash: string) => {
    setActions(prev => prev.map(a => a.id === id ? { ...a, txHash, status: 'pending' } : a))
  }

  const resolveAction = (id: string, success: boolean) => {
    if (success) {
      // Удаляем из optimistic (реальный баланс уже обновлён через инвалидацию)
      setActions(prev => prev.filter(a => a.id !== id))
    } else {
      setActions(prev => prev.map(a => a.id === id ? { ...a, status: 'failed', delta: 0n } : a))
    }
  }

  return { displayBalance, actions, addOptimistic, confirmAction, resolveAction }
}
```

**Когда НЕ стоит использовать optimistic UI:**
- Крупные суммы (>$10K) — пользователь должен видеть реальное подтверждение
- Необратимые действия (например, отправка на внешний адрес)
- Если высокая вероятность revert (низкая ликвидность, высокий slippage)

### Что хотят услышать

✅ Концепция: показали результат → подтвердили → убрали optimistic
✅ Откат при ошибке/revert
✅ Очередь optimistic-экшенов (мульти-транзакции)
✅ Когда НЕ использовать optimistic UI (крупные суммы, необратимые действия)
✅ Инвалидация React Query после подтверждения

---

## 32. Подпиши сообщение и верифицируй на бэкенде (EIP-191 + EIP-1271)

**Уровень:** Middle/Senior

### Развёрнутый ответ

**EIP-191 (Personal Sign)** — стандарт подписи произвольных сообщений. MetaMask показывает: «Sign this message?» + само сообщение.

```tsx
import { useSignMessage } from 'wagmi'
import { verifyMessage } from 'viem'

function SignAndVerify() {
  const { signMessageAsync } = useSignMessage()
  const [signature, setSignature] = useState<string | null>(null)
  const [verified, setVerified] = useState<boolean | null>(null)

  const sign = async () => {
    const sig = await signMessageAsync({
      message: 'Я подтверждаю вход в MyDApp',
    })
    setSignature(sig)

    // Верификация на клиенте (для мгновенной обратной связи)
    const isValid = await verifyMessage({
      address: userAddress!,
      message: 'Я подтверждаю вход в MyDApp',
      signature: sig,
    })
    setVerified(isValid)
  }

  return (
    <div>
      <button onClick={sign}>Подписать</button>
      {signature && <div>Signature: {signature}</div>}
      {verified !== null && (
        <div>{verified ? '✅ Подпись валидна' : '❌ Подпись невалидна'}</div>
      )}
    </div>
  )
}
```

**Что происходит под капотом EIP-191:**

```
Личное сообщение: "Я подтверждаю вход в MyDApp"

1. Добавляется префикс: "\x19Ethereum Signed Message:\n" + длина_сообщения
   → "\x19Ethereum Signed Message:\n29Я подтверждаю вход в MyDApp"

2. Хешируется: keccak256(префикс + сообщение)

3. Подписывается приватным ключом (через MetaMask)

4. Подпись: r, s, v → 65 байт hex
```

**Верификация на бэкенде (Node.js):**

```ts
import { verifyMessage } from 'viem'  // работает и в Node.js!

async function verifyAuth(message: string, signature: string, expectedAddress: string) {
  const recoveredAddress = await verifyMessage({
    address: expectedAddress,  // ожидаемый адрес
    message,
    signature: signature as `0x${string}`,
  })

  return recoveredAddress  // true/false
}
```

**EIP-1271 — подписи от смарт-контрактов:**

```
Проблема: контракт не имеет приватного ключа → не может подписать EIP-191.
Но контракт может верифицировать подпись ПО-СВОЕМУ.

EIP-1271: у контракта должна быть функция:
  isValidSignature(bytes32 hash, bytes memory signature) returns (bytes4 magicValue)

Если возвращает 0x1626ba7e → подпись валидна.
```

```solidity
contract MultisigWallet {
    function isValidSignature(bytes32 hash, bytes calldata signature)
        external view returns (bytes4)
    {
        // Проверяем, что подписали минимум 2 из 3 владельцев
        address[] memory signers = recoverSigners(hash, signature);
        uint validCount;
        for (uint i = 0; i < signers.length; i++) {
            if (isOwner[signers[i]]) validCount++;
        }
        if (validCount >= 2) return 0x1626ba7e; // EIP-1271 magic value
        return 0xffffffff;
    }
}
```

**На фронтенде — проверка EIP-1271:**

```ts
import { isErc6492Signature } from 'viem'

// Проверка с учётом EIP-1271 (контрактные кошельки!)
const isValid = await verifyMessage({
  address: smartWalletAddress,  // может быть контрактом!
  message: 'Hello',
  signature,  // может содержать ERC-6492 обёртку
})
// viem автоматически проверит EIP-1271, если address — контракт
```

### Что хотят услышать

✅ EIP-191: префикс `\x19Ethereum Signed Message:\n<length><message>`
✅ `useSignMessage` / `signMessage` → MetaMask → `verifyMessage`
✅ Верификация на клиенте и на бэкенде
✅ EIP-1271: контракты тоже могут «подписывать» через `isValidSignature`
✅ Use-case'ы: аутентификация, газлесс-транзакции, off-chain ордера

---

## 📋 Чек-лист для подготовки

### Перед собеседованием:
- [ ] Можешь написать компонент `ConnectWallet` + `TokenTransfer` без подсказок
- [ ] Понимаешь жизненный цикл транзакции (5 состояний) и можешь нарисовать схему
- [ ] Знаешь ERC-20 и ERC-721 интерфейсы наизусть (основные функции)
- [ ] Можешь объяснить Uniswap: AMM, формула, slippage
- [ ] Знаешь 3+ уязвимости смарт-контрактов
- [ ] Можешь написать `approve` + `transfer` / `swap` flow
- [ ] Понимаешь, зачем нужен Subgraph
- [ ] Знаешь разницу между viem, wagmi, ethers.js

### Типичные практические задачи на собеседовании:
1. **«Покажи баланс токена»** — `useReadContract` + форматирование
2. **«Отправь токены»** — `useWriteContract` + состояния + ошибки
3. **«Сделай своп»** — approve + swap, два шага
4. **«Подпиши сообщение и проверь»** — sign + verify
5. **«Слушай события контракта»** — watchEvent
6. **«Расшифруй revert-ошибку»** — decodeErrorResult

---

## Связанное
- [[wiki/web3-фронтендер-план-трудоустройства]] — полный план подготовки к web3-собеседованию
- [[wiki/DeFi-для-фронтендера]] — DeFi-концепции: Uniswap, Aave, стейкинг
- [[wiki/wagmi-RainbowKit-фронтенд]] — полный гайд по wagmi + RainbowKit
- [[wiki/Паттерны-транзакций-React]] — продвинутая работа с транзакциями
- [[wiki/Словарь-web3]] — глоссарий web3-терминов
- [[wiki/Блокчейн-как-это-работает]] — фундаментальные основы блокчейна
- [[wiki/Solidity-основы]] — Solidity для фронтендеров
- [[wiki/ERC-20-стандарт-токенов]] — стандарт ERC-20
- [[wiki/ERC-721-NFT-стандарт]] — стандарт ERC-721
- [[wiki/Сравнение-ethers-viem-wagmi]] — сравнение библиотек
- [[wiki/OpenZeppelin-безопасные-контракты]] — безопасность смарт-контрактов
- [[wiki/Subgraph-The-Graph]] — индексация ончейн-данных
