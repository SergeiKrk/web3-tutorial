---
title: "Урок 8. Gas: стоимость выполнения транзакции"
date: 2026-08-14
tags: [web3, gas, ethereum, evm, transaction-fee, eip-1559, base-fee, priority-fee, gwei, gas-estimate]
category: tutorial
---

# Урок 8. Gas: стоимость выполнения транзакции

## Главное определение

Gas — единица измерения вычислительной работы EVM.

Gas не является непосредственно деньгами.

Упрощённо:

Computational Work
        � ↓
       Gas
        � ↓
Gas Price
        � ↓
Transaction Fee

## Зачем нужен Gas

Gas создаёт экономическую стоимость вычислений и предотвращает злоупотребление вычислительными ресурсами сети.

Каждая операция EVM имеет стоимость Gas:

ADD
MUL
SUB
SLOAD
SSTORE
CALL
RETURN
...

## Gas Used

gasUsed — фактически использованное количество Gas при выполнении транзакции.

## Gas Limit

gasLimit — максимальное количество Gas, которое разрешено потратить на выполнение транзакции.

Пример:

gasLimit = 100000
gasUsed = 63000

Пользователь не платит за весь gasLimit. Комиссия рассчитывается исходя из фактически использованного Gas.

## Out of Gas

Если:

gasLimit < Gas Needed

то выполнение может завершиться:

Out of Gas

Транзакция при этом может быть включена в блок, но execution будет неуспешным.

Важно:

Included in block
�≠
Successful execution

## Gwei

1 ETH = 1,000,000,000 gwei

1 gwei = 10^-9 ETH

## Комиссия

Упрощённая формула:

Transaction Fee
=
Gas Used × Effective Gas Price

## EIP-1559

Современная модель Ethereum использует:

Base Fee
+
Priority Fee

Упрощённо:

Effective Gas Price
�≈
Base Fee + Priority Fee

при ограничениях, заданных пользователем.

## Base Fee

Базовая цена Gas сети.

Base Fee сжигается:

Base Fee → Burn

## Priority Fee

Доплата валидатору:

Priority Fee → Validator

## maxFeePerGas

Максимальная цена Gas, которую пользователь готов заплатить.

Если:

maxFeePerGas = 50 gwei

это не означает, что пользователь обязательно заплатит 50 gwei.

## maxPriorityFeePerGas

Максимальный размер tip валидатору.

## Термины

| Понятие | Значение |
|---|---|
| gasLimit | максимум Gas для выполнения |
| gasUsed | фактически использованный Gas |
| baseFee | базовая цена Gas |
| priorityFee | доплата валидатору |
| maxFeePerGas | максимальная цена Gas от пользователя |
| maxPriorityFeePerGas | максимальный tip |
| effectiveGasPrice | фактическая цена Gas |
| transaction fee | итоговая стоимость транзакции |

## Почему операции имеют разную стоимость

Разные операции EVM требуют разного количества вычислительных ресурсов.

Особенно важны операции изменения постоянного состояния:

SLOAD
SSTORE

SSTORE может быть дорогой операцией, потому что изменяет постоянное состояние Ethereum.

## Gas Estimate

Frontend может запросить оценку Gas.

Пример viem:

const gas = await publicClient.estimateGas({
  account,
  to,
  data,
  value,
})

Результат является оценкой, а не гарантией.

Состояние сети и контракта может измениться между оценкой и фактическим выполнением.

## Связь с eth_call

Симуляция выполнения может использоваться для оценки Газа:

Transaction
     � ↓
Simulation
     � ↓
Estimated Gas

## Полная цепочка

User
 � ↓
Frontend
 � ↓
Smart Contract Call
 � ↓
ABI Encoding
 � ↓
Calldata
 � ↓
Wallet
 � ↓
Signature
 � ↓
RPC
 � ↓
Node
 � ↓
Mempool
 � ↓
Validator
 � ↓
EVM
 � ↓
Opcodes
 � ↓
Gas Used
 � ↓
State Change
 � ↓
Block

Комиссия:

Gas Used
    ×
Effective Gas Price
    =
Transaction Fee

## Пример

Gas Used = 80000
Base Fee = 20 gwei
Priority Fee = 3 gwei

Тогда:

Effective Gas Price = 23 gwei

Transaction Fee:
80000 × 23 gwei
= 1,840,000 gwei
= 0.00184 ETH

Base Fee:

80000 × 20 gwei
= 0.0016 ETH

Priority Fee:

80000 × 3 gwei
= 0.00024 ETH

Итого:

0.0016 ETH → burn
0.00024 ETH → validator

## Mermaid-схемы

```mermaid
flowchart LR
    A[Computational Work] --> B[Gas]
    B --> C[Gas Price]
    C --> D[Transaction Fee]
```

```mermaid
flowchart LR
    A[User Transaction] --> B[Base Fee (burned)]
    A --> C[Priority Fee (to Validator)]
```

```mermaid
flowchart LR
    A[Transaction Execution] --> B[Opcodes Execution]
    B --> C[Gas Used Accumulation]
    C --> D[State Change (if successful)]
    D --> E[Block Inclusion]
```

```mermaid
flowchart LR
    A[Frontend Request] --> B[viem estimateGas]
    B --> C[Node Simulation]
    C --> D[Return Estimated Gas]
    D --> E[Frontend Uses Estimate]
```

## Таблица: Термин | Определение | Где используется Frontend-разработчиком

| Термин | Определение | Где используется Frontend-разработчиком |
|---|---|---|
| Gas | Единица измерения вычислительной работы EVM | Для понимания стоимости операций и планирования транзакций |
| Gas Used | Фактически использованное количество Gas при выполнении транзакции | При расчёте реальной комиссии и анализе логов |
| Gas Limit | Максимальное количество Gas, разрешённое на выполнение транзакции | При отправке транзакции, защита от чрезмерных расходов |
| Gas Price | Цена за единицу Gas (в gwei) | При ручной установке комиссии в legacy-транзакциях |
| Base Fee | Базовая цена Gas сети, сжигается | Для оценки минимальной комиссии в EIP-1559 |
| Priority Fee | Доплата валидатору (tip) | Для ускорения подтверждения транзакции |
| Max Fee Per Gas | Максимальная цена Gas, которую пользователь готов заплатить | При отправке транзакции с EIP-1559 (пользовательский лимит) |
| Max Priority Fee Per Gas | Максимальный tip, который пользователь готов заплатить | При отправке транзакции с EIP-1559 (пользовательский лимит tip) |
| Effective Gas Price | Фактическая цена Gas, использованная в транзакции (Base Fee + Priority Fee) | При расчёте реальной комиссии после выполнения |
| Transaction Fee | Итоговая стоимость транзакции в ETH (Gas Used × Effective Gas Price) | Для отображения пользователю стоимости операции |
| Gwei | Деноминация ETH (10^-9 ETH) | Для удобного указания комиссии и цен в интерфейсе |
| Out of Gas | Состояние, когда gasLimit меньше необходимого Gas | Для обработки ошибок и улучшения UX при неудачных транзакциях |
| Gas Estimation | Оценка необходимого Gas перед отправкой транзакции | Для предварительного расчёта комиссии и предотвращения Out of Gas |

## Flashcards (вопрос → ответ)

1. Что такое Gas? → Единица измерения вычислительной работы EVM.
2. Является ли Gas деньгами? → Нет, Gas — это единица измерения работы, а не валюта.
3. Какие три компонента формируют комиссию в EIP-1559? → Base Fee, Priority Fee, Effective Gas Price.
4. Что происходит с Base Fee после включения транзакции в блок? → Base Fee сжигается (burn).
5. Куда направляется Priority Fee? → Priority Fee переходит валидатору как tip.
6. Чем отличается gasLimit от gasUsed? → gasLimit — максимально допустимый Gas, gasUsed — фактически израсходованный.
7. Что такое Out of Gas? → Состояние, когда газ лимит меньше необходимого количества Газа для выполнения.
8. Может ли транзакция с Out of Gas быть включена в блок? → Да, транзакция может быть включена, но её выполнение неуспешно.
9. Сколько gwei в 1 ETH? → 1,000,000,000 gwei.
10. Сколько ETH в 1 gwei? → 0.000000001 ETH (10^-9 ETH).
11. Как рассчитывается комиссия за транзакцию? → Transaction Fee = Gas Used × Effective Gas Price.
12. Что такое effectiveGasPrice? → Фактическая цена за единицу Gas, обычно Base Fee + Priority Fee.
13. Какой метод viem используется для оценки Gas? → publicClient.estimateGas.
14. Что такое gasEstimation? → Оценка необходимого Gas перед отправкой транзакции.
15. Какие операции особенно дороги в Ethereum? → Операции изменения постоянного состояния, такие как SSTORE и SLOAD.
16. Почему SSTORE дорогая? → Потому что изменяет глобальное состояние блокчейна, требует значительных вычислительных ресурсов.
17. Какова цель Gas в сети Ethereum? → Создать экономическую стоимость вычислений и предотвратить спам и бесконечные циклы.
18. Что такое базовая комиссия (Base Fee) в EIP-1559? → Минимальная цена за Gas, определяемая сетью и сжигаемая.
19. Что такое приоритетная комиссия (Priority Fee) в EIP-1559? → Доплата валидатору для ускорения включения транзакции.
20. Можно ли гарантировать, что оценка Gas совпадёт с фактическим потреблением? → Нет, оценка — это приближение, реальное потребление может отличаться из-за изменения состояния.

## Вопросы для собеседования

1. Объясните, как Gas связан с вычислительной работой в EVM и почему он необходим.
2. Чем отличается legado-модель комиссии (Gas Price) от модели EIP-1559?
3. Как рассчитать комиссию транзакции, если известны Gas Used, Base Fee и Priority Fee?
4. Что происходит с Base Fee и Priority Fee после включения транзакции в блок?
5. Опишите разницу между gasLimit и gasUsed и почему пользователь не платит за неиспользованный лимит.
6. Что такое Out of Gas и как это влияет на статус транзакции?
7. Как Frontend может оценить необходимый Gas перед отправкой транзакции? Приведите пример кода на viem.
8. Почему операции SLOAD и SSTORE имеют высокую стоимость Gas?
9. Как влияет изменение состояния контракта между оценкой Gas и фактическим выполнением на точность оценки?
10. Какие параметры пользователь задаёт в EIP-1559 транзакции (maxFeePerGas, maxPriorityFeePerGas)?
11. Как проверить, что транзакция прошла успешно, используя transaction receipt?
12. Приведите пример расчёта комиссии: Gas Used = 50000, Base Fee = 15 gwei, Priority Fee = 2 gwei.

## Задачи на расчёт Transaction Fee

1. Дано: Gas Used = 72000, Base Fee = 25 gwei, Priority Fee = 4 gwei. Найдите комиссию в ETH.
2. Дано: Gas Used = 45000, Base Fee = 12 gwei, Priority Fee = 1 gwei. Найдите комиссию в ETH и укажите, сколько ETH сгорает, а сколько идёт валидатору.
3. Дано: Комиссия транзакции = 0.00216 ETH, Gas Used = 90000, Base Fee = 20 gwei. Найдите Priority Fee в gwei.

## Задачи на различение параметров

1. У пользователя настроены: maxFeePerGas = 60 gwei, maxPriorityFeePerGas = 8 gwei. Текущая Base Fee = 30 gwei. Какой Effective Gas Price будет использован, если сеть не перегружена?
2. gasLimit = 200000, gasUsed = 150000. Сколько Gas осталось неиспользованным и оплачивается ли оно?
3. Base Fee = 18 gwei, Priority Fee = 5 gwei, maxFeePerGas = 40 gwei, maxPriorityFeePerGas = 10 gwei. Пользователь отправил транзакцию. Будет ли транзакция отклонена из-за превышения лимитов?
4. gasUsed = 80000, gasLimit = 100000. Вычислите процент использования газа.

## Практическое задание по estimateGas в viem

Напишите функцию на JavaScript/TypeScript, используя viem, которая оценивает Gas для вызова функции `transfer` ERC-20 токена. Учтите параметры: account, tokenAddress, abi, amount. Верните оценку в виде числа Gas.

## Ссылки

- [[wiki/0_lesson-06-rpc-frontend-ethereum|06. RPC — взаимодействие Frontend с Ethereum]]
- [[wiki/Frontend Web3/0_lesson-07-evm-ethereum-virtual-machine|07. EVM — Ethereum Virtual Machine]]
- [[wiki/Mempool|Mempool]]
- [[wiki/EIP-1559|EIP-1559]]
- [[wiki/viem|viem]]
- [[wiki/Transaction|Transaction]]
- [[wiki/Calldata|Calldata]]

## Повторить на лавке

- Gas — единица измерения вычислительной работы EVM, не валюта.
- Комиссия = Gas Used × Effective Gas Price.
- Base Fee сжигается, Priority Fee идёт валидатору.
- gasLimit — максимум, gasUsed — фактически использовано.
- Out of Gas происходит, когда gasLimit < Gas Needed; транзакция может быть включена, но неуспешна.
- 1 ETH = 1 000 000 000 gwei.
- EIP-1559 делит комиссию на Base Fee + Priority Fee.
- Операции SLOAD и SSTORE дороги, потому что меняют постоянное состояние.
- Frontend может оценить Gas через eth_call или viem.estimateGas.
- Оценка Gas — приближение; реальное потребление может отличаться.

## Связь с Web3 DevTools Hub

На основе материала этого урока можно построить следующие инструменты:

- **Gas Calculator** — вычисляет комиссию в ETH на основе Gas Used, Base Fee и Priority Fee.
- **Gas Estimator** — использует eth_call или RPC-метод eth_estimateGas для предварительного расчёта необходимого Gas.
- **Transaction Fee Calculator** — интегрирует данные из mempool и текущей Base Fee для рекомендации оптимального maxFeePerGas.
- **EIP-1559 Fee Analyzer** — визуализирует распределение комиссии (burn vs validator) за выбранный период.
- **Gas Debugger** — трассирует opcode-исполнение в транзакции, показывая Gas стоимость каждой операции и выявляя узкие места.
