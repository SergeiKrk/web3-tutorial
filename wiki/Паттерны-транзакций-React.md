---
title: "Паттерны работы с транзакциями в React"
date: 2026-07-19
tags: [web3, react, транзакции, wagmi]
category: tutorial
---

# Паттерны работы с транзакциями в React

**Практическое руководство по обработке транзакций в React-приложениях с wagmi/viem.** Все примеры — реальные боевые паттерны, которые пишут в продакшене. Минимум теории блокчейна, максимум кода.

> **Актуальность:** июль 2026, wagmi v3, viem v2.x. API проверен по официальной документации.

**Связанные страницы:** [[wiki/wagmi-RainbowKit-фронтенд]], [[wiki/web3-фронтендер-план-трудоустройства]]

---

## Жизненный цикл транзакции

Транзакция проходит 4 состояния. Ваш UI должен обрабатывать **каждое**:

```
 idle           pending             confirming           confirmed
  │                │                    │                    │
  │  пользователь   │  кошелёк           │  транзакция         │  N блоков
  │  нажал кнопку   │  попросил          │  в блоке, ждём      │  подтвердили
  │                │  подписать          │  квитанцию          │
  │                │                    │                    │
  ▼                ▼                    ▼                    ▼
┌──────┐  writeContract()  ┌─────────┐  майнинг  ┌───────────┐  confirmations  ┌────────────┐
│ idle │ ────────────────► │ pending │ ────────► │ confirming│ ──────────────► │ confirmed  │
└──────┘                   └─────────┘           └───────────┘                 └────────────┘
                                │                      │                           │
                                │ пользователь          │ revert /                  │ success
                                │ отклонил ────────────►│ out of gas ──────────────►│
                                ▼                      ▼                           ▼
                           ┌─────────┐           ┌───────────┐              ┌────────────┐
                           │ rejected│           │  failed   │              │  receipt   │
                           └─────────┘           └───────────┘              └────────────┘
```

**Ключевые хуки wagmi, соответствующие состояниям:**

| Состояние | Хук | Что даёт |
|-----------|-----|----------|
| `idle → pending` | `useWriteContract` / `useSendTransaction` | `writeContract()`, `isPending`, `data: hash` |
| `pending → confirming` | `useWaitForTransactionReceipt` | `isLoading`, `isSuccess` |
| `confirming → confirmed` | `useWaitForTransactionReceipt` с `confirmations` | Ждёт N блоков |
| Ошибка | `error` из хуков + `decodeErrorResult` | Расшифровка revert |

---

## useWriteContract — пишем в смарт-контракт

**Базовая механика:** `useWriteContract` возвращает мутацию TanStack Query. Вызываете `writeContract()` → кошелёк просит подписать → получаете `hash`.

```tsx
import { useWriteContract, useWaitForTransactionReceipt } from 'wagmi'
import { erc20Abi, parseEther } from 'viem'

function TransferToken() {
  const {
    data: hash,
    isPending,
    error,
    writeContract,
  } = useWriteContract()

  const {
    isLoading: isConfirming,
    isSuccess: isConfirmed,
  } = useWaitForTransactionReceipt({ hash })

  const handleTransfer = () => {
    writeContract({
      address: '0x6B175474E89094C44Da98b954EedeAC495271d0F', // DAI
      abi: erc20Abi,
      functionName: 'transfer',
      args: ['0xRecipient...', parseEther('10')], // 10 DAI
    })
  }

  return (
    <div>
      <button disabled={isPending} onClick={handleTransfer}>
        {isPending ? 'Подтвердите в кошельке...' : 'Отправить 10 DAI'}
      </button>

      {hash && <div>Tx: {hash.slice(0, 10)}...{hash.slice(-8)}</div>}
      {isConfirming && <div>⏳ Ожидание подтверждения...</div>}
      {isConfirmed && <div>✅ Транзакция подтверждена!</div>}
    </div>
  )
}
```

**Что важно знать о `useWriteContract` (wagmi v3):**

- Это **TanStack Query mutation**. Все поля: `data`, `isPending`, `isSuccess`, `isError`, `error`, `status`, `reset`.
- `mutate()` = `writeContract()` — вызываете для отправки.
- `mutateAsync()` = `writeContractAsync()` — возвращает Promise<`0x${string}`> (хеш).
- `data` содержит хеш транзакции (`0x${string}`) — **сразу** после подписи в кошельке, до майнинга.
- `isPending === true` пока кошелёк не подписал (или пользователь не отклонил).

> **Как читать writeContract({ address, abi, functionName, args }):** «отправь транзакцию в контракт: вот адрес, вот ABI-интерфейс, вот имя функции, вот аргументы — кошелёк попросит подпись, а в ответ ты получишь хеш». Мнемоника: *writeContract = запись в блокчейн, платно, не мгновенно, требует confirmations.*

> **Паттерн:** передаёте `hash` из `useWriteContract` в `useWaitForTransactionReceipt` — и получаете два независимых состояния: «подписывается» и «майнится».

---

## useSendTransaction — отправка нативного ETH

Для простых переводов ETH (не вызов контракта) — `useSendTransaction`:

```tsx
import { useSendTransaction, useWaitForTransactionReceipt } from 'wagmi'
import { parseEther } from 'viem'

function SendEth() {
  const {
    data: hash,
    isPending,
    sendTransaction,
  } = useSendTransaction()

  const { isLoading: isConfirming, isSuccess: isConfirmed } =
    useWaitForTransactionReceipt({ hash })

  const handleSend = () => {
    sendTransaction({
      to: '0xRecipientAddress...',
      value: parseEther('0.05'), // 0.05 ETH
    })
  }

  return (
    <button disabled={isPending} onClick={handleSend}>
      {isPending ? 'Подтвердите...' : 'Отправить 0.05 ETH'}
    </button>
  )
}
```

**Отличия от `useWriteContract`:**
- `useSendTransaction` — для transfer ETH, не требует ABI
- `useWriteContract` — для вызова функций контракта (transfer, mint, approve...)
- Оба возвращают одинаковую структуру (`{ data: hash, isPending, ... }`)

---

## useWaitForTransactionReceipt — ожидание квитанции

Самый важный хук для transaction flow. Ждёт, пока транзакция попадёт в блок, и возвращает **receipt** (статус, gas used, логи).

### Базовое использование

```tsx
const { data: hash, writeContract } = useWriteContract()

const {
  data: receipt,
  isLoading: isConfirming,
  isSuccess: isConfirmed,
  isError: isFailed,
  error: receiptError,
} = useWaitForTransactionReceipt({ hash })
```

**Возвращаемые поля:**

| Поле | Тип | Когда |
|------|-----|-------|
| `data` | `TransactionReceipt \| undefined` | Транзакция в блоке. Содержит `status`, `blockNumber`, `gasUsed`, `logs` |
| `isLoading` | `boolean` | Ожидание включения в блок |
| `isSuccess` | `boolean` | Транзакция подтверждена |
| `isError` | `boolean` | Транзакция revert / ошибка |
| `error` | `WaitForTransactionReceiptErrorType` | Детали ошибки |

> **Как читать useWaitForTransactionReceipt({ hash }):** «следи за хешем транзакции: пока она майнится — `isLoading: true`, когда блокчейн принял её навсегда — `isSuccess: true` и отдаёт квитанцию с `status`, `blockNumber`, `gasUsed`». Мнемоника: *подключи хеш — получи квитанцию; без хеша хук молчит.*

### Параметр `confirmations` — ждать N блоков

По умолчанию хук резолвится после **1 confirmation** (транзакция в блоке). Для безопасности ждите больше:

```tsx
const { isLoading, isSuccess } = useWaitForTransactionReceipt({
  hash,
  confirmations: 3, // ждём 3 блока после включения
})
```

**Когда сколько ждать:**
- 1 confirmation — достаточно для тестов и небольших сумм
- 3-5 confirmations — продакшен для средних сумм
- 12+ confirmations — крупные суммы / финализация на L1 (вероятность реорга ~0)

### Параметр `onReplaced` — детект замены транзакции

Если пользователь ускорил (speed up) или отменил транзакцию — хук сообщит:

```tsx
const { isLoading, isSuccess } = useWaitForTransactionReceipt({
  hash,
  onReplaced: (replacement) => {
    console.log('Tx заменена:', replacement.reason)
    // reason: 'replaced' | 'repriced' | 'cancelled'
    if (replacement.reason === 'cancelled') {
      // транзакция отменена пользователем
    }
  },
})
```

### Параметр `pollingInterval`

Частота опроса (мс). По умолчанию — из `config`. Для быстрых сетей можно уменьшить:

```tsx
useWaitForTransactionReceipt({
  hash,
  pollingInterval: 1_000, // опрос каждую секунду
})
```

---

## Обработка revert: decodeErrorResult

Когда смарт-контракт делает `revert`, вы получаете ошибку с закодированными данными. **decodeErrorResult** из viem расшифровывает причину.

### Паттерн: перехват и расшифровка

```tsx
import { type BaseError, useWriteContract } from 'wagmi'
import { decodeErrorResult } from 'viem'
import { contractAbi } from './abi'

function MintWithErrorHandling() {
  const { data: hash, isPending, error, writeContract } = useWriteContract()

  const getRevertReason = (err: Error | null): string => {
    if (!err) return 'Неизвестная ошибка'

    // User rejected — пользователь отклонил в кошельке
    if (err.name === 'UserRejectedRequestError') {
      return 'Вы отклонили транзакцию в кошельке'
    }

    // Пытаемся декодировать revert причину из контракта
    const baseError = err as BaseError
    const revertError = baseError.walk(
      (e) => (e as any)?.data?.data !== undefined
    )

    if (revertError) {
      try {
        const decoded = decodeErrorResult({
          abi: contractAbi,
          data: (revertError as any).data.data,
        })
        return `Контракт вернул ошибку: ${decoded.errorName} (${decoded.args})`
      } catch {
        // Не удалось декодировать — показываем сырое сообщение
      }
    }

    return baseError.shortMessage || err.message
  }

  return (
    <div>
      <button disabled={isPending} onClick={() => writeContract({ ... })}>
        Mint
      </button>
      {error && <div style={{ color: 'red' }}>❌ {getRevertReason(error)}</div>}
    </div>
  )
}
```

**Ключевой приём — `baseError.walk()`:**  
Ошибки в viem/wagmi — это цепочка `BaseError`. `walk()` идёт по цепочке и находит вложенную ошибку с нужными данными. В примере выше мы ищем ошибку, у которой есть `data.data` — это закодированный revert от контракта.

> **Как читать baseError.walk(e => условие):** «пройдись по цепочке вложенных ошибок и найди ту, которая удовлетворяет условию — например, содержит закодированный revert от контракта в `data.data`». Мнемоника: *walk = прогулка по матрёшке ошибок, ищешь самую глубокую с полезными данными.*

> **Как читать decodeErrorResult({ abi, data }):** «возьми ABI контракта и сырые байты ошибки — расшифруй, какое имя ошибки (например `InsufficientBalance`) и с какими аргументами контракт сделал revert». Мнемоника: *decodeErrorResult = переводчик с языка байтов revert-ошибки на человеческий «контракт сказал: недостаточно средств».*

### Типичные ошибки и их `.name`

| `error.name` | Значение | Действие |
|---|---|---|
| `UserRejectedRequestError` | Пользователь отклонил в кошельке | Показать «Отклонено», не пугать |
| `ContractFunctionRevertedError` | Контракт сделал revert | Декодировать `decodeErrorResult` |
| `EstimateGasExecutionError` | Не удалось оценить газ (скорее всего revert) | Показать причину до отправки |
| `InsufficientFundsError` | Не хватает ETH на газ | Показать «Недостаточно средств» |
| `TransactionExecutionError` | Ошибка при отправке | Показать `shortMessage` |

---

## Gas estimation: почему падает и как чинить

**Проблема:** `useWriteContract` внутри вызывает `estimateGas`, чтобы рассчитать лимит газа. `estimateGas` симулирует транзакцию — если симуляция делает revert, вы получаете ошибку **до** отправки в кошелёк.

### Причины падения estimateGas

1. **Контракт реально сделает revert** — неправильные аргументы, недостаточно баланса, не тот allowance
2. **Зависимость от состояния** — между вызовом estimateGas и реальной отправкой состояние изменилось (другой пользователь опередил)
3. **Сложная логика газа** — контракт с циклами/ветвлениями, газ зависит от входных данных
4. **Недостаточно средств** — на кошельке нет ETH для оплаты газа

### Решение 1: Ручная оценка газа с запасом

```tsx
import { useWriteContract } from 'wagmi'
import { usePublicClient } from 'wagmi'
import { erc20Abi } from 'viem'

function SafeTransfer() {
  const publicClient = usePublicClient()
  const { writeContract } = useWriteContract()

  const handleTransfer = async () => {
    if (!publicClient) return

    // 1. Пробуем оценить газ с запасом
    let gasLimit: bigint
    try {
      const estimated = await publicClient.estimateGas({
        account: '0xUserAddress...',
        to: '0xTokenAddress...',
        data: encodeFunctionData({
          abi: erc20Abi,
          functionName: 'transfer',
          args: ['0xRecipient...', parseEther('10')],
        }),
      })
      // Добавляем 20% запас
      gasLimit = (estimated * 120n) / 100n
    } catch {
      // Оценка не удалась — ставим щедрый дефолт
      gasLimit = 300_000n
    }

    // 2. Отправляем с явным gas limit
    writeContract({
      address: '0xTokenAddress...',
      abi: erc20Abi,
      functionName: 'transfer',
      args: ['0xRecipient...', parseEther('10')],
      gas: gasLimit, // ← форсируем лимит
    })
  }
}
```

### Решение 2: Предварительная проверка через `useSimulateContract`

wagmi v3 предоставляет `useSimulateContract` — выполняет сухую симуляцию **до** вызова кошелька:

```tsx
import { useSimulateContract, useWriteContract } from 'wagmi'
import { erc20Abi, parseEther } from 'viem'

function SafeTransferV2() {
  const { data: simulation } = useSimulateContract({
    address: '0xTokenAddress...',
    abi: erc20Abi,
    functionName: 'transfer',
    args: ['0xRecipient...', parseEther('10')],
    query: { enabled: true },
  })

  const { writeContract, isPending } = useWriteContract()

  const isSimulating = simulation === undefined
  const willFail = simulation?.error !== undefined

  return (
    <div>
      {isSimulating && <div>🔍 Проверяем транзакцию...</div>}
      {willFail && (
        <div style={{ color: 'red' }}>
          ❌ Транзакция не пройдёт: {simulation.error.message}
        </div>
      )}
      <button
        disabled={isPending || willFail || isSimulating}
        onClick={() => writeContract({
          address: '0xTokenAddress...',
          abi: erc20Abi,
          functionName: 'transfer',
          args: ['0xRecipient...', parseEther('10')],
        })}
      >
        Отправить
      </button>
    </div>
  )
}
```

> **Паттерн:** `useSimulateContract` → проверяем `error` → блокируем кнопку если revert → вызываем `writeContract` только если симуляция успешна.

### Решение 3: Надбавка газа для нетривиальных контрактов

```tsx
// Для контрактов с переменным потреблением газа (NFT mint, свопы)
const GAS_BUFFER_MULTIPLIER = 1.5 // 50% запас

writeContract({
  address: contractAddress,
  abi: contractAbi,
  functionName: 'mint',
  args: [quantity],
  gas: estimatedGas
    ? BigInt(Math.ceil(Number(estimatedGas) * GAS_BUFFER_MULTIPLIER))
    : 1_000_000n, // fallback для сложных операций
})
```

---

## Замена транзакции: speed up и cancel

В Ethereum транзакцию можно заменить, отправив **новую с тем же nonce** но более высоким газом.

### Speed up (ускорение)

Отправить ту же транзакцию, но с повышенной ценой газа:

```tsx
import { useWriteContract } from 'wagmi'

function SpeedUpButton({ oldHash }: { oldHash: `0x${string}` }) {
  const { writeContract } = useWriteContract()

  const speedUp = () => {
    writeContract({
      address: '0xContract...',
      abi: contractAbi,
      functionName: 'transfer',
      args: ['0xRecipient...', parseEther('10')],
      // Форсируем повышенный газ — кошелёк сам подставит правильный nonce
      maxFeePerGas: parseGwei('50'),  // было 20 → ставим 50
      maxPriorityFeePerGas: parseGwei('3'), // было 1 → ставим 3
    })
  }

  return <button onClick={speedUp}>⚡ Ускорить</button>
}
```

### Cancel (отмена)

Отправить транзакцию на свой же адрес с 0 ETH и тем же nonce:

```tsx
import { useSendTransaction } from 'wagmi'
import { useConnection } from 'wagmi'
import { parseGwei } from 'viem'

function CancelButton({ oldNonce }: { oldNonce: number }) {
  const { address } = useConnection()
  const { sendTransaction } = useSendTransaction()

  const cancel = () => {
    if (!address) return
    sendTransaction({
      to: address,        // отправляем себе
      value: 0n,          // 0 ETH
      nonce: oldNonce,    // тот же nonce
      maxFeePerGas: parseGwei('50'),   // повышенный газ
      maxPriorityFeePerGas: parseGwei('3'),
    })
  }

  return <button onClick={cancel}>❌ Отменить</button>
}
```

### Отслеживание замены через `onReplaced`

`useWaitForTransactionReceipt` сам обнаруживает замену:

```tsx
const { isLoading } = useWaitForTransactionReceipt({
  hash,
  onReplaced: ({ reason, transaction, transactionReceipt }) => {
    switch (reason) {
      case 'replaced':
        toast.success('Транзакция ускорена!')
        // Используйте новый hash из transaction.hash
        break
      case 'cancelled':
        toast.info('Транзакция отменена')
        break
    }
  },
})
```

---

## Toast-уведомления: полноценный хук

Собираем всё в один переиспользуемый хук, который показывает toast на каждом этапе:

```tsx
import { useState, useEffect, useCallback } from 'react'
import {
  useWriteContract,
  useWaitForTransactionReceipt,
  type BaseError,
} from 'wagmi'
import { decodeErrorResult } from 'viem'
import { toast } from 'react-hot-toast' // или sonner, или ваш toaster

type TxLifecycle = {
  status: 'idle' | 'pending' | 'confirming' | 'confirmed' | 'failed'
  hash?: `0x${string}`
  error?: string
  receipt?: { blockNumber: bigint; gasUsed: bigint }
}

export function useTransactionWithToast(abi: any) {
  const [lifecycle, setLifecycle] = useState<TxLifecycle>({ status: 'idle' })

  const {
    data: hash,
    isPending,
    error: writeError,
    writeContract,
  } = useWriteContract()

  const {
    isLoading: isConfirming,
    isSuccess,
    error: receiptError,
  } = useWaitForTransactionReceipt({ hash, confirmations: 2 })

  // === Эффекты для toast ===

  // pending: открываем toast при отправке
  useEffect(() => {
    if (isPending) {
      setLifecycle({ status: 'pending' })
      toast.loading('⏳ Подтвердите транзакцию в кошельке...', {
        id: 'tx-toast',
      })
    }
  }, [isPending])

  // hash получен: обновляем toast
  useEffect(() => {
    if (hash && !isConfirming && !isSuccess) {
      setLifecycle({ status: 'confirming', hash })
      toast.loading('⏳ Транзакция отправлена. Ожидаем подтверждения...', {
        id: 'tx-toast',
      })
    }
  }, [hash, isConfirming, isSuccess])

  // confirmed
  useEffect(() => {
    if (isSuccess) {
      setLifecycle({ status: 'confirmed', hash })
      toast.success('✅ Транзакция подтверждена!', { id: 'tx-toast' })
    }
  }, [isSuccess, hash])

  // ошибка на этапе отправки
  useEffect(() => {
    if (writeError) {
      const message = getReadableError(writeError)
      setLifecycle({ status: 'failed', error: message })
      toast.error(`❌ ${message}`, { id: 'tx-toast' })
    }
  }, [writeError])

  // ошибка на этапе подтверждения (revert)
  useEffect(() => {
    if (receiptError) {
      const message = getReadableError(receiptError)
      setLifecycle({ status: 'failed', error: message })
      toast.error(`❌ ${message}`, { id: 'tx-toast' })
    }
  }, [receiptError])

  // Cброс
  const reset = useCallback(() => {
    setLifecycle({ status: 'idle' })
    toast.dismiss('tx-toast')
  }, [])

  return {
    ...lifecycle,
    isPending,
    isConfirming,
    writeContract,
    reset,
  }
}

// Вспомогательная: человекопонятный текст ошибки
function getReadableError(err: Error): string {
  if (err.name === 'UserRejectedRequestError') {
    return 'Вы отклонили транзакцию'
  }
  const baseErr = err as BaseError
  if (baseErr.shortMessage?.includes('insufficient funds')) {
    return 'Недостаточно средств для газа'
  }
  return baseErr.shortMessage || err.message.slice(0, 100)
}
```

**Использование в компоненте:**

```tsx
function MyMintButton() {
  const { status, writeContract, isPending } = useTransactionWithToast(abi)

  return (
    <button
      disabled={status === 'pending' || status === 'confirming'}
      onClick={() =>
        writeContract({
          address: '0x...',
          abi,
          functionName: 'mint',
          args: [1n],
        })
      }
    >
      {status === 'idle' && 'Mint NFT'}
      {status === 'pending' && 'Подпишите...'}
      {status === 'confirming' && 'Майнинг...'}
      {status === 'confirmed' && '✅ Готово'}
      {status === 'failed' && 'Попробовать снова'}
    </button>
  )
}
```

---

## Transaction History: хранение и отображение

### Стратегия хранения

Транзакции уходят в блокчейн навсегда, но локально их нужно где-то хранить для истории пользователя. Варианты:

| Стратегия | Плюсы | Минусы |
|-----------|-------|--------|
| `localStorage` | Просто, переживает перезагрузку | Нет синхронизации между вкладками |
| React state + `localStorage` | Мгновенный UI + персистентность | Ручная синхронизация |
| Subgraph / The Graph | Полная история, индексация | Инфраструктура, задержка |
| Свой бэкенд + БД | Полный контроль | Нужен сервер |

### Реализация: localStorage + React Context

```tsx
// types.ts
type TxRecord = {
  hash: `0x${string}`
  chainId: number
  type: 'send' | 'contract'
  description: string       // "Transfer 10 DAI to 0x1234..."
  status: 'pending' | 'confirmed' | 'failed'
  timestamp: number
  blockNumber?: bigint
}

// TxHistoryContext.tsx
import { createContext, useContext, useState, useEffect, useCallback } from 'react'

const STORAGE_KEY = 'tx-history'

function loadHistory(): TxRecord[] {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

function saveHistory(records: TxRecord[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(records.slice(0, 100)))
}

const TxHistoryContext = createContext<{
  history: TxRecord[]
  addTx: (tx: TxRecord) => void
  updateTx: (hash: string, update: Partial<TxRecord>) => void
}>({ history: [], addTx: () => {}, updateTx: () => {} })

export function TxHistoryProvider({ children }: { children: React.ReactNode }) {
  const [history, setHistory] = useState<TxRecord[]>(loadHistory)

  useEffect(() => { saveHistory(history) }, [history])

  const addTx = useCallback((tx: TxRecord) => {
    setHistory((prev) => [tx, ...prev])
  }, [])

  const updateTx = useCallback((hash: string, update: Partial<TxRecord>) => {
    setHistory((prev) =>
      prev.map((tx) => (tx.hash === hash ? { ...tx, ...update } : tx))
    )
  }, [])

  return (
    <TxHistoryContext.Provider value={{ history, addTx, updateTx }}>
      {children}
    </TxHistoryContext.Provider>
  )
}

export const useTxHistory = () => useContext(TxHistoryContext)
```

**Интеграция с хуком транзакции:**

```tsx
function TransferWithHistory() {
  const { addTx, updateTx } = useTxHistory()
  const { writeContract, isPending } = useWriteContract()

  const { isLoading: isConfirming, isSuccess } =
    useWaitForTransactionReceipt({
      hash,
      confirmations: 1,
    })

  // При получении hash — добавляем в историю как pending
  useEffect(() => {
    if (hash) {
      addTx({
        hash,
        chainId: chainId!,
        type: 'contract',
        description: `Transfer ${amount} DAI to ${to.slice(0, 6)}...`,
        status: 'pending',
        timestamp: Date.now(),
      })
    }
  }, [hash])

  // При подтверждении — обновляем статус
  useEffect(() => {
    if (isSuccess && hash) {
      updateTx(hash, { status: 'confirmed' })
    }
  }, [isSuccess, hash])
}
```

### Компонент истории

```tsx
function TxHistoryList() {
  const { history } = useTxHistory()

  if (history.length === 0) {
    return <div style={{ color: '#888' }}>История транзакций пуста</div>
  }

  return (
    <div>
      <h3>История транзакций</h3>
      {history.map((tx) => (
        <div
          key={tx.hash}
          style={{
            padding: '12px',
            border: '1px solid #333',
            borderRadius: '8px',
            marginBottom: '8px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <strong>{tx.description}</strong>
            <TxStatusBadge status={tx.status} />
          </div>
          <div style={{ fontSize: '0.85em', color: '#888' }}>
            {tx.hash.slice(0, 10)}...{tx.hash.slice(-8)}
            {' · '}
            {new Date(tx.timestamp).toLocaleString()}
          </div>
          <a
            href={`https://etherscan.io/tx/${tx.hash}`}
            target="_blank"
            rel="noopener noreferrer"
            style={{ fontSize: '0.85em' }}
          >
            Etherscan ↗
          </a>
        </div>
      ))}
    </div>
  )
}

function TxStatusBadge({ status }: { status: TxRecord['status'] }) {
  const colors = {
    pending: { bg: '#332b00', text: '#ffd700' },
    confirmed: { bg: '#00331a', text: '#00ff88' },
    failed: { bg: '#330000', text: '#ff4444' },
  }
  const c = colors[status]
  return (
    <span
      style={{
        background: c.bg,
        color: c.text,
        padding: '2px 8px',
        borderRadius: '12px',
        fontSize: '0.8em',
      }}
    >
      {status === 'pending' && '⏳ Pending'}
      {status === 'confirmed' && '✅ Done'}
      {status === 'failed' && '❌ Failed'}
    </span>
  )
}
```

---

## Боевой компонент: всё вместе

Собираем все паттерны в один продакшен-компонент для transfer ERC-20:

```tsx
import { useState, useEffect } from 'react'
import {
  useWriteContract,
  useWaitForTransactionReceipt,
  useSimulateContract,
  useConnection,
  type BaseError,
} from 'wagmi'
import { erc20Abi, parseEther, decodeErrorResult, formatEther } from 'viem'
import { toast } from 'react-hot-toast'
import { useTxHistory } from './TxHistoryContext'

type TransferState =
  | { step: 'idle' }
  | { step: 'simulating' }
  | { step: 'ready'; gasEstimate: bigint }
  | { step: 'pending_sign' }
  | { step: 'mining'; hash: `0x${string}` }
  | { step: 'confirmed'; hash: `0x${string}` }
  | { step: 'error'; message: string }

export function TransferForm({
  tokenAddress,
  tokenDecimals,
}: {
  tokenAddress: `0x${string}`
  tokenDecimals: number
}) {
  const { address } = useConnection()
  const [to, setTo] = useState('')
  const [amount, setAmount] = useState('')
  const [state, setState] = useState<TransferState>({ step: 'idle' })
  const { addTx, updateTx } = useTxHistory()

  // Проверяем невалидный адрес
  const isValidAddress = /^0x[0-9a-fA-F]{40}$/.test(to)
  const isValidAmount = amount && !isNaN(Number(amount)) && Number(amount) > 0
  const canEstimate = isValidAddress && isValidAmount

  // === Симуляция ===
  const { data: simulation, isLoading: isSimulating } = useSimulateContract({
    address: tokenAddress,
    abi: erc20Abi,
    functionName: 'transfer',
    args: canEstimate
      ? [to as `0x${string}`, parseEther(amount)]
      : undefined,
    query: { enabled: canEstimate },
  })

  const willFail = simulation?.error !== undefined

  // === Отправка ===
  const {
    data: hash,
    isPending,
    error: writeError,
    writeContract,
  } = useWriteContract()

  // === Ожидание ===
  const {
    isLoading: isConfirming,
    isSuccess,
    error: receiptError,
  } = useWaitForTransactionReceipt({
    hash,
    confirmations: 2,
  })

  // === Эффекты ===
  useEffect(() => {
    if (isSimulating) setState({ step: 'simulating' })
    else if (simulation && !willFail) {
      setState({ step: 'ready', gasEstimate: simulation.gasEstimate })
    } else if (willFail) {
      setState({ step: 'error', message: getHumanError(simulation!.error!) })
    }
  }, [isSimulating, simulation, willFail])

  useEffect(() => {
    if (isPending) setState({ step: 'pending_sign' })
  }, [isPending])

  useEffect(() => {
    if (hash) {
      setState({ step: 'mining', hash })
      addTx({
        hash,
        chainId: 1,
        type: 'contract',
        description: `Transfer ${amount} tokens to ${to.slice(0, 6)}...`,
        status: 'pending',
        timestamp: Date.now(),
      })
      toast.loading('Транзакция в мемпуле...', { id: 'tx' })
    }
  }, [hash])

  useEffect(() => {
    if (isConfirming) {
      toast.loading(`Майнинг... (1/2 confirmations)`, { id: 'tx' })
    }
  }, [isConfirming])

  useEffect(() => {
    if (isSuccess && hash) {
      setState({ step: 'confirmed', hash })
      updateTx(hash, { status: 'confirmed' })
      toast.success('✅ Транзакция подтверждена!', { id: 'tx' })
    }
  }, [isSuccess, hash])

  useEffect(() => {
    if (writeError || receiptError) {
      const err = (writeError || receiptError)!
      setState({ step: 'error', message: getHumanError(err) })
      if (hash) updateTx(hash, { status: 'failed' })
      toast.error(getHumanError(err), { id: 'tx' })
    }
  }, [writeError, receiptError])

  // === Обработчик отправки ===
  const handleTransfer = () => {
    setState({ step: 'pending_sign' })
    writeContract({
      address: tokenAddress,
      abi: erc20Abi,
      functionName: 'transfer',
      args: [to as `0x${string}`, parseEther(amount)],
    })
  }

  return (
    <div style={{ maxWidth: 480, margin: '0 auto' }}>
      <h2>Отправить токены</h2>

      <input
        placeholder="Адрес получателя 0x..."
        value={to}
        onChange={(e) => setTo(e.target.value)}
        disabled={state.step !== 'idle' && state.step !== 'ready' && state.step !== 'error'}
        style={{ width: '100%', marginBottom: 8, padding: 8 }}
      />

      <input
        placeholder="Сумма"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        disabled={state.step !== 'idle' && state.step !== 'ready' && state.step !== 'error'}
        style={{ width: '100%', marginBottom: 8, padding: 8 }}
      />

      {/* Стейты кнопки */}
      {state.step === 'idle' && (
        <button disabled style={{ width: '100%', padding: 10 }}>
          Введите адрес и сумму
        </button>
      )}
      {state.step === 'simulating' && (
        <button disabled style={{ width: '100%', padding: 10 }}>
          🔍 Проверяем транзакцию...
        </button>
      )}
      {state.step === 'ready' && (
        <button onClick={handleTransfer} style={{ width: '100%', padding: 10 }}>
          Отправить ({formatEther(state.gasEstimate)} ETH gas)
        </button>
      )}
      {state.step === 'pending_sign' && (
        <button disabled style={{ width: '100%', padding: 10 }}>
          ✍️ Подтвердите в кошельке...
        </button>
      )}
      {state.step === 'mining' && (
        <button disabled style={{ width: '100%', padding: 10 }}>
          ⛏️ Майнинг... {state.hash.slice(0, 10)}...
        </button>
      )}
      {state.step === 'confirmed' && (
        <button
          onClick={() => setState({ step: 'idle' })}
          style={{ width: '100%', padding: 10, background: '#00aa55', color: '#fff' }}
        >
          ✅ Готово! Отправить ещё
        </button>
      )}

      {/* Ошибка */}
      {state.step === 'error' && (
        <div
          style={{
            marginTop: 12,
            padding: 12,
            background: '#330000',
            color: '#ff6666',
            borderRadius: 8,
          }}
        >
          ❌ {state.message}
          <button
            onClick={() => setState({ step: 'idle' })}
            style={{ marginLeft: 12 }}
          >
            Попробовать снова
          </button>
        </div>
      )}
    </div>
  )
}

// Человекопонятная ошибка
function getHumanError(err: Error): string {
  if (err.name === 'UserRejectedRequestError') return 'Вы отклонили транзакцию'
  const baseErr = err as BaseError
  if (baseErr.shortMessage?.includes('insufficient funds'))
    return 'Недостаточно средств'
  return baseErr.shortMessage || err.message.slice(0, 150)
}
```

---

## Шпаргалка: все хуки для транзакций

| Хук | Назначение | Ключевые поля |
|-----|-----------|---------------|
| `useWriteContract` | Вызов write-функции контракта | `writeContract()`, `data: hash`, `isPending` |
| `useSendTransaction` | Отправка ETH | `sendTransaction()`, `data: hash`, `isPending` |
| `useWaitForTransactionReceipt` | Ожидание квитанции | `isLoading`, `isSuccess`, `data: receipt`, `confirmations` |
| `useSimulateContract` | Сухая симуляция до отправки | `data: { result, gasEstimate, error }` |
| `useTransactionReceipt` | Получить receipt по hash | `data: receipt` |
| `useTransactionConfirmations` | Количество подтверждений | `data: number` |

---

## Чек-лист: что проверить перед продакшеном

- [ ] Все 4 состояния транзакции отображаются в UI (idle → pending → confirming → confirmed)
- [ ] Кнопка блокируется (`disabled`) на время pending и confirming
- [ ] Ошибка `UserRejectedRequestError` обрабатывается отдельно (не пугает пользователя)
- [ ] Revert причина декодируется через `decodeErrorResult`
- [ ] Gas limit устанавливается с запасом (≥20%)
- [ ] Используется `confirmations ≥ 2` для значимых транзакций
- [ ] Toast-уведомления на каждом этапе
- [ ] Хеш транзакции сохраняется в историю (localStorage минимум)
- [ ] Ссылка на Etherscan для каждой транзакции
- [ ] `onReplaced` обрабатывает speed up / cancel

---

## Дополнительные ресурсы

- **wagmi docs:** https://wagmi.sh/react/guides/write-to-contract
- **viem decodeErrorResult:** https://viem.sh/docs/contract/decodeErrorResult
- **viem estimateGas:** https://viem.sh/docs/actions/public/estimateGas
- **viem ошибки (BaseError):** https://viem.sh/docs/glossary/errors
- **Связанная wiki:** [[wiki/wagmi-RainbowKit-фронтенд]], [[wiki/Сравнение-ethers-viem-wagmi]]
