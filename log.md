# Log — web3Crypto

Хронология всех операций над базой знаний.

---

## [2026-08-22] tutorial — Урок 11. ABI Encoding: calldata изнутри
- Создан `wiki/Frontend Web3/0_lesson-11-abi-encoding-calldata-iznutri.md`: Function Signature и Selector, ABI slots, static/dynamic types, Head/Offset/Tail, padding, ручное чтение calldata и примеры viem.
- Добавлены 7 Mermaid-схем, 2 справочные таблицы, 25 flashcards, 18 вопросов для собеседований, 9 практических заданий, алгоритм Calldata Decoder и связь с Web3 DevTools Hub.
- Обновлены `wiki/Словарь-web3.md` и `index.md`; урок 11 отмечен завершённым, счётчик страниц увеличен до 27.

## [2026-08-14] tutorial — Урок 8. Gas: стоимость выполнения транзакции
- Создана wiki/Frontend Web3/0_lesson-08-gas-stoimost-vypolneniya-transakcii.md: Gas, gasUsed, gasLimit, baseFee, priorityFee, maxFeePerGas, maxPriorityFeePerGas, effectiveGasPrice, gwei, outOfGas, gasEstimate, EIP-1559.
- Добавлены: 4 Mermaid-схемы (Gas lifecycle, EIP-1559 fee flow, Transaction execution → Gas Used → State Change, estimateGas flow), таблица «Термин → Определение → Где используется Frontend-разработчиком», >=20 flashcards, >=12 вопросов для собеседования, задачи на расчёт Transaction Fee, задачи на различение параметров, практическое задание по estimateGas в viem.
- Обновлён Словарь-web3.md — добавлены: Gas, Gas Used, Gas Limit, Gas Price, Base Fee, Priority Fee, Max Fee Per Gas, Max Priority Fee Per Gas, Effective Gas Price, Gwei, Out of Gas, Gas Estimation.
- Обновлён index.md — урок 8 отмечен завершённым (������✅), счётчик страниц 26.

## [2026-08-14] tutorial — Урок 7. EVM — Ethereum Virtual Machine
- Создана wiki/Frontend Web3/07. EVM — Ethereum Virtual Machine.md: EVM, bytecode, opcode, gas, stack, memory, storage, calldata, eth_call, view, pure, архитектура вызова.
- Добавлены: 4 Mermaid-схемы (Solidity→Compiler→Bytecode→EVM, Stack/Memory/Storage, Frontend→ABI→Calldata→Transaction→RPC→EVM, SLOAD→ADD→SSTORE), таблица «Concept → Что делает → Сохраняется ли состояние → Важность для Frontend», 20 flashcards, 12 вопросов для собеседования, практические задания (определение областей, чтение/запись, путь calldata, eth_call vs transaction), блок «Повторить на лавке» (10 тезисов), раздел «Связь с Web3 DevTools Hub».
- Обновлён Словарь-web3.md — добавлены: EVM, Bytecode, Opcode, Stack, Memory, Storage, Calldata, SLOAD, SSTORE, eth_call, view, pure.
- Обновлён index.md — урок 7 отмечен завершённым (��✅), счётчик страниц 25.

## [2026-08-11] tutorial — Урок 6. RPC: как Frontend разговаривает с Ethereum
- Создана wiki/0_lesson-06-rpc-frontend-ethereum.md: RPC vs Node vs Blockchain, HTTP/WebSocket, JSON-RPC 2.0, методы (eth_blockNumber, eth_getBalance, eth_getBlockByNumber, eth_getTransactionByHash, eth_getTransactionReceipt, eth_call, eth_sendRawTransaction), eth_call vs Transaction, RPC Provider, практическая классификация read/write
- Добавлены: 3 Mermaid-схемы, таблица «Метод → меняет состояние», 3 практических задания, 11 вопросов с собеседований, 10 ключевых тезисов, 22 flashcards, таблица терминов, блок «Повторить на лавке»
- Обновлён Словарь-web3.md — добавлены: RPC, JSON-RPC, RPC Provider, Endpoint, eth_call, Transaction Receipt, WebSocket RPC; уточнён Node
- Обновлён index.md — урок 6 отмечен завершённым (✅)

## [2026-08-11] tutorial — Урок 5. Mempool и ожидание транзакции
- Создана wiki/0_lesson-05-mempool-ozhidanie-transakcii.md: проверка транзакции нодой, выбор валидатора (EIP-1559, nonce-зависимости), Pending → Included/Confirmed/Dropped/Replaced, Speed Up, Cancel, пример зависимости по nonce
- Добавлены: Mermaid-схема жизненного цикла, таблица «Понятие → Frontend», 4 практические задачи, 12 вопросов с собеседований, 10 ключевых тезисов, 20 flashcards, таблица терминов
- Обновлён Словарь-web3.md — добавлены/уточнены: Mempool, Pending Transaction, Base Fee, Priority Fee, Max Fee Per Gas, Replacement Transaction, Speed Up, Cancel, Nonce
- Обновлён index.md — урок 5 отмечен завершённым (✅), счётчик страниц 24
- Обновлена ссылка «следующий урок» в 0_lesson-04

## [2026-07-23] update | Масштабное добавление «Как читать»-врезок (18 страниц, 52 врезки)
- Solidity: mapping, modifier, event indexed
- ERC-20: вложенный mapping, approve+transferFrom, decimals, gas-кеширование
- ERC-721: 4 mapping'а, _isApprovedOrOwner, Soulbound _update, ERC-721A lazy
- Блокчейн: sha256(), транзакция (wei, data), EIP-1559 gas
- DeFi: createConfig L2, Flashbots, healthFactor, x×y=k AMM
- Hardhat: getContractFactory, .connect(), task().setAction(), buildModule()
- OpenZeppelin: наследование is ERC20, keccak256-роли, deployProxy/UUPS, SafeERC20
- wagmi/RainbowKit: useReadContract, writeContract→waitForReceipt, getDefaultConfig
- Subgraph: dataSources YAML, @entity/@derivedFrom, Entity.save(), GraphQL-пагинация
- Паттерны транзакций: writeContract, waitForReceipt, baseError.walk, decodeErrorResult
- GitHub Commit Notary: tx { data: hash }, Proof of Skill: Soulbound mint, Escrow: createBounty→resolveBounty
- План трудоустройства: connect→sign→send, pending→receipt, вопросы собеседования: watchEvent, approve+transferFrom, useReadContracts, writeContractAsync

## [2026-07-19] tool — Hardhat-среда-разработки
- Исследована документация hardhat.org (Hardhat v2/v3)
- Создана wiki/Hardhat-среда-разработки.md — 4 уровня объяснения
- Покрыто: установка, инициализация, компиляция, Hardhat Network, деплой в Sepolia, тестирование (Chai + hardhat-chai-matchers), консоль, скрипты, Hardhat Ignition, система тасков, gas-оптимизация
- Полный разбор Counter.sol через Hardhat: от инициализации до тестов и деплоя
- Обновлён index.md — добавлена ссылка в раздел «Инструменты»

## [2026-07-13] concept — Solidity-основы
- Создан raw/Counter.sol — контракт-счётчик (состояние, события, модификатор, view-функции)
- Создана wiki/Страница Solidity-основы: типы данных, видимость, view/pure/payable, storage vs memory, глобальные переменные, модификаторы, события
- Обновлён index.md — добавлена ссылка в раздел «Концепты»
- Начало Этапа 2 по дорожной карте (Смарт-контракты)

## [2026-07-13] projects — три пет-проекта для портфолио
- Добавлены страницы проектов: GitHub Commit Notary, Proof of Skill, Open Source Sponsor Escrow
- Обновлён index.md — секция «Проекты» с перекрёстными ссылками
- Обновлён этап 5 в Главная.md — старые идеи заменены на три новых проекта с рекомендуемым порядком
- Проекты охватывают: криптографию + хеши, DID + NFT + IPFS, смарт-контракты + оракулы + escrow

## [2026-08-14] move — Перенос уроков 1-6 в папку Frontend Web3
- Перемещены файлы: 0_lesson-01-chto-takoe-web3.md через 0_lesson-06-rpc-frontend-ethereum.md из wiki/ в wiki/Frontend Web3/
- Обновлены ссылки в index.md: префикс wiki/Frontend Web3/ добавлен к урокам 1-6
- Количество страниц осталось 25

## [2026-08-14] rename — Переименование урока 7 в единый стиль
- Переименован файл: "07. EVM — Ethereum Virtual Machine.md" → "0_lesson-07-evm-ethereum-virtual-machine.md"
- Обновлена ссылка в index.md
- Сохранено количество страниц: 25
