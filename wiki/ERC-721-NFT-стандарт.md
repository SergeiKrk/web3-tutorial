---
title: "ERC-721 — NFT стандарт"
date: 2026-07-19
tags: [web3, solidity, nft, erc721]
category: concept
source_count: 5
---

# ERC-721 — NFT стандарт

## Уровень 1. Для пятилетнего ребёнка

Представь, что у тебя есть коллекция уникальных игрушек. У каждой игрушки есть свой номер и паспорт:

- У робота — паспорт №1, цвет синий
- У динозавра — паспорт №2, цвет зелёный
- У куклы — паспорт №3, платье красное

Эти игрушки нельзя просто так обменять одну на другую — они **разные**, у каждой своя ценность. В отличие от игровых жетонов из парка аттракционов, где все жетоны одинаковые.

**ERC-721** — это правила игры для таких уникальных игрушек, но в интернете. Ты можешь:

- Узнать, какие игрушки у тебя есть (по номерам)
- Подарить игрушку другу (она переедет в его коллекцию)
- Посмотреть паспорт игрушки (картинку и описание)
- Назначить друга смотрителем, который может передать игрушку кому-то ещё

Самые известные «игрушки» по этим правилам: коллекционные картинки (CryptoPunks, Bored Apes), игровые предметы, доменные имена.

---

## Уровень 2. Для новичка в web3

ERC-721 — это **технический стандарт невзаимозаменяемых токенов** (Non-Fungible Tokens, NFT) в Ethereum и EVM-совместимых блокчейнах. Стандарт описан в документе **EIP-721** (Ethereum Improvement Proposal), предложенном William Entriken, Dieter Shirley, Jacob Evans и Nastassia Sachs в январе 2018 года.

### Что такое невзаимозаменяемый токен?

**Non-Fungible** (невзаимозаменяемый) — значит, что каждый токен уникален и имеет собственную ценность. В отличие от **ERC-20 (fungible)**, где все токены одинаковы (как доллары), NFT — как билеты на концерт с конкретными местами: билет в первом ряду ≠ билет в последнем.

### Почему не подходит ERC-20?

ERC-20 оперирует балансами: «у Алисы 100 токенов, у Боба 50». Но для NFT нужно знать **какими именно токенами** владеет Алиса — токен №42 или токен №777. Каждый NFT идентифицируется парой `(адрес контракта, tokenId)`, которая **глобально уникальна** во всём блокчейне.

### Где используются ERC-721 токены?

- **Коллекционное искусство** — CryptoPunks, Bored Ape Yacht Club (BAYC), Azuki
- **Игровые предметы** — оружие, персонажи, земля в метавселенных (Axie Infinity, Decentraland)
- **Доменные имена** — ENS (Ethereum Name Service): `vitalik.eth` — это NFT
- **Proof-of-Attendance** — POAP: бесплатные NFT за участие в мероприятиях
- **Сертификаты** — Soulbound NFT: дипломы, сертификаты навыков (см. [[wiki/Proof-of-Skill]])
- **Недвижимость и real-world активы** — токенизация физических объектов

### ERC-721 vs ERC-20: ключевые отличия

| Характеристика | ERC-20 | ERC-721 |
|---------------|--------|---------|
| Тип токена | Взаимозаменяемый (fungible) | Уникальный (non-fungible) |
| Единица учёта | Баланс (`balanceOf`) | Владение конкретным ID (`ownerOf`) |
| Перевод | `transfer(кому, сколько)` | `transferFrom(от, кому, tokenId)` |
| Делимость | Да (через `decimals`) | Нет (каждый токен — единица) |
| Метаданные | Только name/symbol | `tokenURI` — JSON с картинкой и описанием |

---

## Уровень 3. Для разработчика (интерфейс и механика)

### Интерфейс ERC-721 (EIP-721)

Смарт-контракт считается ERC-721, если реализует интерфейс `IERC721`, интерфейс `IERC165` (`supportsInterface`), и опционально — расширения `IERC721Metadata` и `IERC721Enumerable`.

#### Обязательные методы

```solidity
// ===== Базовые методы IERC721 =====

// Количество NFT у конкретного адреса
function balanceOf(address _owner) external view returns (uint256)

// Владелец конкретного токена (кидает ошибку, если токен не существует)
function ownerOf(uint256 _tokenId) external view returns (address)

// Безопасный перевод с проверкой: контракт-получатель должен реализовать
// IERC721Receiver.onERC721Received, иначе транзакция ревёртится.
// Защищает от безвозвратной потери токенов при переводе на контракт.
function safeTransferFrom(address _from, address _to, uint256 _tokenId) external payable
function safeTransferFrom(address _from, address _to, uint256 _tokenId, bytes calldata _data) external payable

// «Опасный» перевод — НЕ проверяет, умеет ли получатель работать с NFT.
// Использовать ТОЛЬКО когда уверен, что _to — это EOA или проверенный контракт.
function transferFrom(address _from, address _to, uint256 _tokenId) external payable

// Одобрить адрес для управления одним конкретным токеном
function approve(address _approved, uint256 _tokenId) external payable

// Кто одобрен для управления конкретным токеном (или address(0), если никто)
function getApproved(uint256 _tokenId) external view returns (address)

// Одобрить/запретить оператора для ВСЕХ токенов владельца
function setApprovalForAll(address _operator, bool _approved) external

// Проверить, является ли адрес оператором для владельца
function isApprovedForAll(address _owner, address _operator) external view returns (bool)
```

#### Обязательные события

```solidity
// Эмитится при любом переводе (включая mint и burn)
event Transfer(address indexed _from, address indexed _to, uint256 indexed _tokenId)
// Особые случаи:
//   mint:  _from = address(0)
//   burn:  _to   = address(0)

// Эмитится при вызове approve() — одобрение для одного токена
event Approval(address indexed _owner, address indexed _approved, uint256 indexed _tokenId)

// Эмитится при вызове setApprovalForAll() — одобрение/отзыв оператора
event ApprovalForAll(address indexed _owner, address indexed _operator, bool _approved)
```

**Важное отличие от ERC-20**: все три параметра событий `Transfer` и `Approval` в ERC-721 — `indexed`, что позволяет фильтровать по любому из них. В ERC-20 `value` не был `indexed` (ограничение: до 3 indexed-параметров на событие).

#### Расширение IERC721Metadata (опциональное)

```solidity
// Название коллекции
function name() external view returns (string)   // Пример: "Bored Ape Yacht Club"

// Символ (тикер)
function symbol() external view returns (string)  // Пример: "BAYC"

// URI с метаданными конкретного токена (JSON)
function tokenURI(uint256 _tokenId) external view returns (string)
```

#### Расширение IERC721Enumerable (опциональное)

```solidity
// Общее количество токенов
function totalSupply() external view returns (uint256)

// Токен по порядковому индексу (для перебора ВСЕХ токенов)
function tokenByIndex(uint256 _index) external view returns (uint256)

// Токен владельца по индексу (для перебора токенов ОДНОГО владельца)
function tokenOfOwnerByIndex(address _owner, uint256 _index) external view returns (uint256)
```

### Как работает approve и transferFrom

Модель делегирования, похожая на ERC-20, но работающая на уровне отдельных токенов:

```
Алиса --approve(маркетплейс, tokenId=42)--> ERC-721 контракт
                                              |
Маркетплейс --transferFrom(Алиса, Боб, 42)--> ERC-721 контракт
```

**Два уровня делегирования в ERC-721:**

1. **`approve`** — одобрение для одного конкретного токена. Только один адрес может быть approved для заданного `tokenId` одновременно. При Transfer — approved **сбрасывается** в `address(0)`.
2. **`setApprovalForAll`** — одобрение оператора для **всех** токенов владельца сразу. Используется маркетплейсами (OpenSea, Blur) для листинга всей коллекции без approve на каждый токен.

### safeTransferFrom — защита от потерянных токенов

`safeTransferFrom` проверяет, что получатель **умеет** принимать NFT:

```solidity
// Интерфейс, который должен реализовать контракт-получатель
interface IERC721Receiver {
    function onERC721Received(
        address operator,
        address from,
        uint256 tokenId,
        bytes calldata data
    ) external returns (bytes4);
}
```

Если `_to` — смарт-контракт, `safeTransferFrom` вызывает на нём `onERC721Received` и проверяет, что возвращённый `bytes4` равен селектору `IERC721Receiver.onERC721Received.selector`. Если нет — транзакция ревёртится, токен остаётся у отправителя.

**`transferFrom`** (без «safe») этой проверки НЕ делает — если отправить токен на контракт без `onERC721Received`, токены будут **безвозвратно потеряны**.

### Метаданные: JSON schema

`tokenURI(uint256 tokenId)` возвращает URI, указывающий на JSON-файл с метаданными токена. Сам файл обычно хранится на:

- **IPFS** — `ipfs://Qm...` (децентрализованно, нельзя изменить)
- **Arweave** — перманентное хранение
- **Централизованный сервер** — `https://api.example.com/metadata/42` (можно изменить)
- **On-chain (Base64)** — JSON закодирован прямо в контракте (дорого, но неизменяемо)

#### Стандартная JSON-схема метаданных (из EIP-721)

```json
{
    "title": "Asset Metadata",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Название актива, который представляет NFT"
        },
        "description": {
            "type": "string",
            "description": "Описание актива"
        },
        "image": {
            "type": "string",
            "description": "URI, указывающий на изображение (mime type image/*). Рекомендуется ширина 320–1080px, соотношение сторон от 1.91:1 до 4:5."
        }
    }
}
```

#### Расширенная схема (OpenSea de-facto стандарт)

```json
{
    "name": "Thor's Hammer",
    "description": "Mjölnir, the legendary hammer of the Norse god of thunder.",
    "image": "https://game.example/item-id-8u5h2m.png",
    "external_url": "https://game.example/item/8u5h2m",
    "attributes": [
        {"trait_type": "Strength", "value": 20},
        {"trait_type": "Element", "value": "Lightning"},
        {"trait_type": "Rarity", "value": "Legendary"}
    ],
    "background_color": "000000",
    "animation_url": "https://game.example/item-id-8u5h2m.mp4"
}
```

Поля сверх `name/description/image` — это расширения, не входящие в EIP-721, но поддерживаемые маркетплейсами (OpenSea, Rarible):

- **`attributes`** — массив свойств с `trait_type` и `value` (могут быть строкой, числом или `boost_percentage`)
- **`external_url`** — ссылка на внешнюю страницу
- **`animation_url`** — видео, 3D-модель или интерактивный контент
- **`background_color`** — фоновый цвет в HEX без `#`

### Mint — создание токена

Mint (чеканка) — это создание нового NFT. В ERC-721 mint **не входит в стандартный интерфейс** — в спецификации нет функции `mint()`. Вместо этого стандарт определяет, что создание токена = событие `Transfer(address(0), to, tokenId)`.

#### Базовая реализация mint через OpenZeppelin

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC721URIStorage, ERC721} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract GameItem is ERC721URIStorage {
    uint256 private _nextTokenId;

    constructor() ERC721("GameItem", "ITM") {}

    function awardItem(address player, string memory tokenURI) public returns (uint256) {
        uint256 tokenId = _nextTokenId++;
        _mint(player, tokenId);
        _setTokenURI(tokenId, tokenURI);
        return tokenId;
    }
}
```

`_mint(address to, uint256 tokenId)` — внутренняя функция OpenZeppelin:
1. Проверяет, что `to != address(0)` и токен ещё не существует
2. Записывает владельца в mapping
3. Обновляет `balanceOf`
4. Эмитит `Transfer(address(0), to, tokenId)`

**ERC721URIStorage** — расширение OpenZeppelin, сохраняющее `tokenURI` для каждого токена в storage контракта. Альтернативно можно переопределить `tokenURI()` и вычислять URI динамически (например, через `baseURI + tokenId`).

---

## Уровень 4. Для продвинутого разработчика (реализация и нюансы)

### Минимальная реализация ERC-721 на Solidity

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SimpleNFT {
    string public name = "SimpleNFT";
    string public symbol = "SNFT";

    mapping(uint256 => address) private _owners;
    mapping(address => uint256) private _balances;
    mapping(uint256 => address) private _tokenApprovals;
    mapping(address => mapping(address => bool)) private _operatorApprovals;

> **Как читать четыре mapping'а ERC-721:** читай `_owners[tokenId] → address` как «чей это токен», `_balances[address] → count` как «сколько токенов у адреса», `_tokenApprovals[tokenId] → address` как «кому разрешено перевести этот конкретный токен», `_operatorApprovals[владелец][оператор] → bool` как «разрешено ли оператору управлять ВСЕМИ токенами владельца». Мнемоника: mapping'и ERC-721 — это четыре журнала: журнал владельцев, журнал балансов, журнал доверенностей на токен и журнал полных доверенностей.

    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
    event Approval(address indexed owner, address indexed approved, uint256 indexed tokenId);
    event ApprovalForAll(address indexed owner, address indexed operator, bool approved);

    function balanceOf(address owner) public view returns (uint256) {
        require(owner != address(0), "ERC721: zero address");
        return _balances[owner];
    }

    function ownerOf(uint256 tokenId) public view returns (address) {
        address owner = _owners[tokenId];
        require(owner != address(0), "ERC721: invalid token ID");
        return owner;
    }

    function _isApprovedOrOwner(address spender, uint256 tokenId) private view returns (bool) {
        address owner = ownerOf(tokenId);
        return (spender == owner ||
                getApproved(tokenId) == spender ||
                isApprovedForAll(owner, spender));
    }

> **Как читать `_isApprovedOrOwner` с тройным `||`:** читай как «разрешаю перевод, если вызывающий удовлетворяет ХОТЯ БЫ ОДНОМУ из трёх условий: (1) он и есть владелец токена, (2) ему выдали approve на этот конкретный токен, (3) ему выдали setApprovalForAll на ВСЕ токены владельца». Мнемоника: это шлюз с тремя дверьми — владелец проходит в первую, доверенный на токен во вторую, оператор всей коллекции в третью.

    function transferFrom(address from, address to, uint256 tokenId) public payable {
        require(_isApprovedOrOwner(msg.sender, tokenId), "ERC721: caller is not owner nor approved");
        require(ownerOf(tokenId) == from, "ERC721: transfer from incorrect owner");
        require(to != address(0), "ERC721: transfer to zero address");

        // Сброс approved при переводе
        _tokenApprovals[tokenId] = address(0);

        _balances[from] -= 1;
        _balances[to] += 1;
        _owners[tokenId] = to;

        emit Transfer(from, to, tokenId);
    }

    function approve(address to, uint256 tokenId) public payable {
        address owner = ownerOf(tokenId);
        require(to != owner, "ERC721: approval to current owner");
        require(msg.sender == owner || isApprovedForAll(owner, msg.sender),
            "ERC721: approve caller is not owner nor approved for all");

        _tokenApprovals[tokenId] = to;
        emit Approval(owner, to, tokenId);
    }

    function getApproved(uint256 tokenId) public view returns (address) {
        require(_owners[tokenId] != address(0), "ERC721: invalid token ID");
        return _tokenApprovals[tokenId];
    }

    function setApprovalForAll(address operator, bool approved) public {
        require(operator != msg.sender, "ERC721: approve to caller");
        _operatorApprovals[msg.sender][operator] = approved;
        emit ApprovalForAll(msg.sender, operator, approved);
    }

    function isApprovedForAll(address owner, address operator) public view returns (bool) {
        return _operatorApprovals[owner][operator];
    }

    // Внутренний mint — не входит в стандарт, но необходим
    function _mint(address to, uint256 tokenId) internal {
        require(to != address(0), "ERC721: mint to zero address");
        require(_owners[tokenId] == address(0), "ERC721: token already minted");

        _balances[to] += 1;
        _owners[tokenId] = to;

        emit Transfer(address(0), to, tokenId);
    }
}
```

### OpenZeppelin — промышленная реализация

В реальных проектах используют OpenZeppelin:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract MyNFT is ERC721URIStorage, Ownable {
    uint256 private _nextTokenId;
    uint256 public constant MAX_SUPPLY = 10000;
    uint256 public constant MINT_PRICE = 0.05 ether;

    constructor() ERC721("MyNFT", "MNFT") Ownable(msg.sender) {}

    function mint(address to, string memory uri) public payable returns (uint256) {
        require(msg.value >= MINT_PRICE, "Insufficient payment");
        require(_nextTokenId < MAX_SUPPLY, "Max supply reached");

        uint256 tokenId = _nextTokenId++;
        _mint(to, tokenId);
        _setTokenURI(tokenId, uri);
        return tokenId;
    }

    function withdraw() public onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
}
```

**Расширения OpenZeppelin для ERC-721:**

| Расширение | Назначение |
|-----------|-----------|
| `ERC721URIStorage` | Хранение `tokenURI` в storage (газозатратно, но гибко) |
| `ERC721Enumerable` | `totalSupply`, `tokenByIndex`, `tokenOfOwnerByIndex` |
| `ERC721Burnable` | `burn(tokenId)` — уничтожение токена |
| `ERC721Pausable` | Пауза всех переводов (экстренная остановка) |
| `ERC721Royalty` (ERC-2981) | Роялти: комиссия автору при перепродаже |
| `ERC721Consecutive` | Пакетный mint с последовательными ID |

### Soulbound-токены (non-transferable NFT)

**Soulbound-токен (SBT)** — это NFT, который **нельзя передать** другому адресу после mint. Концепция предложена Виталиком Бутериным в 2022 году для цифровой идентичности (дипломы, сертификаты, KYC, репутация).

#### Реализация Soulbound

**Способ 1. Блокировка transferFrom**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract SoulboundCertificate is ERC721URIStorage {
    uint256 private _nextTokenId;
    mapping(uint256 => bool) private _soulbound; // можно ли передавать?

    constructor() ERC721("Skill Certificate", "SKILL") {}

    function mint(address to, string memory uri, bool soulbound) public returns (uint256) {
        uint256 tokenId = _nextTokenId++;
        _mint(to, tokenId);
        _setTokenURI(tokenId, uri);
        _soulbound[tokenId] = soulbound;
        return tokenId;
    }

    // Блокируем перевод для soulbound-токенов
    function transferFrom(address from, address to, uint256 tokenId) public override {
        require(!_soulbound[tokenId], "Soulbound: token is non-transferable");
        super.transferFrom(from, to, tokenId);
    }

    function safeTransferFrom(address from, address to, uint256 tokenId, bytes memory data) public override {
        require(!_soulbound[tokenId], "Soulbound: token is non-transferable");
        super.safeTransferFrom(from, to, tokenId, data);
    }
}
```

**Способ 2. Полная блокировка (все токены контракта)**

```solidity
// Блокируем ВСЕ переводы — проще и надёжнее
function _update(address to, uint256 tokenId, address auth) internal override returns (address) {
    address from = _ownerOf(tokenId);
    // Разрешаем только mint (from = 0) и burn (to = 0)
    require(from == address(0) || to == address(0), "Soulbound: non-transferable");
    return super._update(to, tokenId, auth);
}
```

> **Как читать `require(from == address(0) || to == address(0))` в Soulbound:** читай как «транзакция разрешена только в двух случаях: либо токен рождается из ничего (from = 0x0, это mint), либо токен уходит в никуда (to = 0x0, это burn). Всё остальное — обычный перевод — запрещено». Мнемоника: `address(0)` — это «нулевой адрес», как `null` в JavaScript; mint = from=null, burn = to=null, а если ни то ни другое — ревёрт.

**Где используется Soulbound:**
- **UNI-дипломы и сертификаты** (см. [[wiki/Proof-of-Skill]])
- **Proof-of-Attendance** (POAP — их тоже нельзя передавать, если организатор так настроил)
- **KYC/identity** (верификация личности)
- **Голоса в governance** (голос привязан к личности, не продаётся)

### ERC-721A (Azuki) — gas-оптимизация пакетного минта

**ERC-721A** — улучшенная реализация ERC-721 от команды **Azuki** (Chiru Labs). Ключевое преимущество: **пакетный mint нескольких токенов стоит почти как mint одного**. Стандартный ERC-721 (OpenZeppelin) делает N × SSTORE при mint N токенов — это очень дорого.

#### Как работает оптимизация (lazy initialization)

ERC-721A использует механизм **отложенной инициализации**:

1. **При mint**: токены выпускаются последовательными ID. Контракт делает **всего 3 SSTORE** независимо от количества:
   - Инициализирует слот владельца только для **первого** токена в партии
   - Обновляет `balanceOf` получателя
   - Обновляет `_nextTokenId`
   - События `Transfer` эмитятся для каждого токена (но event дешевле SSTORE на порядок)

2. **При transfer**: инициализация слотов владельцев происходит **лениво**, в момент первого перевода токена. Это стоит дороже, чем обычный transfer, но эту цену платят при перепродаже, а не при mint.

**Идея**: газ на mint дороже (BASEFEE выше из-за ажиотажа), а transfer происходит позже, когда сеть спокойнее.

> **Как читать ERC-721A «lazy initialization»:** читай как «при чеканке не записываю владельца каждого токена по отдельности (это N×SSTORE = дорого), а записываю только первый токен партии и говорю "владелец у токенов #42–46 — Алиса, потом разберёмся"». Реальная запись владельца откладывается до первого transfer'а этого токена. Мнемоника: это как билеты на концерт — при покупке пачки записываешь только номер первого билета и что «билеты 42–46 купила Алиса», а номера мест уточняешь когда она начнёт их передавать.

#### Сравнение gas-расходов

| Операция | OpenZeppelin ERC-721 | ERC-721A |
|----------|---------------------|----------|
| Mint 5 токенов | 155 949 gas | **63 748 gas** (−59%) |
| Transfer 5 токенов | 226 655 gas | 334 450 gas (+47%) |
| Mint BASEFEE | 200 gwei | 200 gwei |
| Transfer BASEFEE | 40 gwei | 40 gwei |
| **Итого комиссия** | **0.0403 ETH** | **0.0261 ETH** (−35%) |

Даже при консервативной разнице в BASEFEE (200 vs 40), экономия на практике ещё выше, потому что массовые минты разгоняют BASEFEE экспоненциально (при заполнении gas limit блока).

#### Первый transfer vs повторные

| Операция | OpenZeppelin | ERC-721A |
|----------|-------------|----------|
| Первый transfer токена | 45 331 gas | 92 822 gas (дороже: 2 SSTORE + 5 SLOAD) |
| Повторный transfer | 45 331 gas | 44 499 gas (дешевле: слот уже инициализирован) |

Дополнительные затраты первого transfer:
- **2 extra SSTORE** — инициализация текущего и следующего слотов
- **5 extra SLOAD** — чтение предыдущих слотов и следующего слота

#### Использование ERC-721A

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

import "erc721a/contracts/ERC721A.sol";

contract Azuki is ERC721A {
    uint256 public constant MAX_SUPPLY = 10000;
    uint256 public constant MAX_PER_WALLET = 5;
    uint256 public constant MINT_PRICE = 0.05 ether;

    constructor() ERC721A("Azuki", "AZUKI") {}

    function mint(uint256 quantity) external payable {
        require(totalSupply() + quantity <= MAX_SUPPLY, "Max supply exceeded");
        require(_numberMinted(msg.sender) + quantity <= MAX_PER_WALLET, "Max per wallet");
        require(msg.value >= MINT_PRICE * quantity, "Insufficient payment");

        // _mint(address to, uint256 quantity) — а не tokenId!
        _mint(msg.sender, quantity);
    }

    function _baseURI() internal view virtual override returns (string memory) {
        return "https://api.azuki.com/metadata/";
    }
}
```

Ключевое отличие API: `_mint(address to, uint256 quantity)` вместо `_mint(address to, uint256 tokenId)`.

#### Важные нюансы ERC-721A

- **Токены должны быть последовательными** — transfer ломает последовательность, поэтому ERC-721A отслеживает «дырки» через слоты владельцев
- **balanceOf(address)** — остаётся O(1) через внутренний mapping балансов (команда отказалась от его удаления ради совместимости)
- **_numberMinted(address)** — дополнительная функция: сколько токенов адрес заминтил всего (включая проданные); используется для whitelist-проверок
- **_getAux / _setAux** — вспомогательные 64-битные слоты на адрес для кастомных данных (например, whitelist-биты) с минимальными затратами газа
- **Совместимость** — ERC-721A полностью совместим с EIP-721 (реализует `IERC721`, `IERC721Metadata`, `IERC721Enumerable`) и проходит все тесты стандарта
- **Расширения**: `ERC721ABurnable`, `ERC721AQueryable`, `ERC4907A` (аренда NFT)

#### Когда использовать ERC-721A, а когда стандартный ERC-721

| Сценарий | Выбор |
|----------|-------|
| Массовый mint (коллекции 1000+) | **ERC-721A** — экономия газа на mint |
| Одиночные минты / сертификаты | **Стандартный ERC-721** — проще, меньше байткода |
| Игровые предметы с частыми transfer | **Стандартный ERC-721** — дешевле повторные transfer |
| Коллекции с reveal-механикой | **ERC-721A** — базовая экономия + расширения |
| Soulbound (нет transfer) | **Стандартный ERC-721** — gas-оптимизация ERC-721A не даёт преимуществ без transfer |

### ERC-721 на практике: ethers.js / viem

```typescript
// ===== viem (рекомендуется) =====
import { createPublicClient, http } from 'viem';

const client = createPublicClient({ /* ... */ });

// Чтение владельца токена
const owner = await client.readContract({
    address: nftContractAddress,
    abi: erc721Abi,
    functionName: 'ownerOf',
    args: [42n],
});

// Чтение метаданных
const tokenURI = await client.readContract({
    address: nftContractAddress,
    abi: erc721Abi,
    functionName: 'tokenURI',
    args: [42n],
});

// Если URI — ipfs://..., преобразуем в HTTP
const httpUrl = tokenURI.replace('ipfs://', 'https://ipfs.io/ipfs/');
const metadata = await fetch(httpUrl).then(r => r.json());
console.log(metadata.name, metadata.image);

// Подписка на события Transfer в реальном времени
client.watchEvent({
    address: nftContractAddress,
    event: parseAbiItem('event Transfer(address indexed from, address indexed to, uint256 indexed tokenId)'),
    onLogs: (logs) => {
        for (const log of logs) {
            console.log(`${log.args.from} → ${log.args.to}: #${log.args.tokenId}`);
        }
    },
});
```

### Известные уязвимости и проблемы

#### 1. Потеря токенов через transferFrom на контракт

Если использовать `transferFrom` вместо `safeTransferFrom`, и получатель — контракт без `onERC721Received`, NFT теряется навсегда.

**Защита**: всегда использовать `safeTransferFrom`, если получатель может быть контрактом.

#### 2. Reentrancy в safeTransferFrom

`safeTransferFrom` делает внешний вызов в контракт получателя. Если контракт-получатель вызывает отправителя обратно до завершения перевода — возможна рекурсивная атака. OpenZeppelin защищает от этого, обновляя балансы ДО внешнего вызова (checks-effects-interactions).

#### 3. Неуникальные tokenURI

Если `tokenURI` отдаёт одинаковый URI для разных токенов — токены технически разные (разные ID), но выглядят одинаково. Это не баг, но может ввести пользователей в заблуждение.

#### 4. Централизованные метаданные

Если `tokenURI` указывает на централизованный сервер (https://...), владелец сервера может изменить метаданные в любой момент. **Решение**: IPFS, Arweave или on-chain Base64.

#### 5. Отсутствие supportsInterface

Контракт обязан реализовать `IERC165` с `supportsInterface`. Некоторые маркетплейсы и кошельки не распознают NFT без корректного `supportsInterface`, что приводит к ошибкам отображения.

---

## Связанное
- [[wiki/Proof-of-Skill]] — проект на Soulbound NFT


- [[wiki/ERC-20-стандарт-токенов]] — стандарт взаимозаменяемых токенов (отличия ERC-20 vs ERC-721)
- [[wiki/Solidity-основы]] — синтаксис Solidity, необходимый для написания ERC-721
- [[wiki/Главная]] — дорожная карта изучения web3, этап 2 (смарт-контракты)
- [[wiki/Proof-of-Skill]] — проект на ERC-721 Soulbound: децентрализованные сертификаты навыков
- [[wiki/Словарь-web3]] — термины: event, gas, ABI, storage, mapping, IPFS
- [[wiki/Блокчейн-как-это-работает]] — база по блокчейну: аккаунты, транзакции, gas
